import discord
import game_logic
from discord import app_commands
from loguru import logger

from bot.bot import bot
from bot.utils import format_player_list
from user_sessions import get_user_room, set_user_room


@bot.tree.command(name="impostor", description="Gra w Impostora")
@app_commands.describe(
    action="Akcja do wykonania", 
    code="Kod pokoju (opcjonalny - bot zapamięta twój ostatni pokój)"
)
@app_commands.choices(
    action=[
        app_commands.Choice(name="create - Stwórz nowy pokój", value="create"),
        app_commands.Choice(name="join - Dołącz do pokoju", value="join"),
        app_commands.Choice(name="start - Rozpocznij grę", value="start"),
        app_commands.Choice(name="status - Sprawdź status pokoju", value="status"),
        app_commands.Choice(name="reveal - Pokaż słowo ponownie", value="reveal"),
        app_commands.Choice(name="restart - Zrestartuj grę", value="restart"),
    ]
)
async def impostor_command(
    interaction: discord.Interaction,
    action: app_commands.Choice[str],
    code: str | None = None,
):
    await interaction.response.defer(ephemeral=(action.value in ["join", "reveal"]))

    user_id = str(interaction.user.id)
    username = interaction.user.display_name

    try:
        if action.value == "create":
            room_id = await game_logic.create_room(
                user_id,
                username,
                source="discord",
                channel_id=str(interaction.channel_id),
            )

            # Store this room as the user's current room
            await set_user_room(user_id, room_id)

            # Start listening for secrets in this room
            if hasattr(bot, "firestore_listener"):
                bot.firestore_listener.start_room_listener(room_id)
                logger.info(f"Started listener for room {room_id}")

            embed = discord.Embed(
                title="✅ Pokój utworzony!",
                description=f"Kod pokoju: **{room_id}**\n\n💡 Ten pokój został zapamiętany - nie musisz podawać kodu w kolejnych komendach!",
                color=discord.Color.green(),
            )
            embed.add_field(
                name="Jak dołączyć?",
                value=f"Discord: `/impostor join code:{room_id}`",
                inline=False,
            )
            embed.add_field(
                name="Rozpoczęcie gry",
                value=f"Gdy będzie minimum 3 graczy, użyj:\n`/impostor start` (lub `/impostor start code:{room_id}`)",
                inline=False,
            )
            embed.set_footer(text="Tylko host może rozpocząć grę")

            await interaction.followup.send(embed=embed)

        elif action.value == "join":
            if not code:
                await interaction.followup.send(
                    "❌ Musisz podać kod pokoju przy pierwszym dołączeniu!", ephemeral=True
                )
                return

            code = code.upper().strip()
            await game_logic.join_room(code, user_id, username, source="discord")

            # Store this room as the user's current room
            await set_user_room(user_id, code)

            # Start listening for secrets in this room (if not already)
            if hasattr(bot, "firestore_listener"):
                bot.firestore_listener.start_room_listener(code)
                logger.info(f"Started listener for room {code}")

            embed = discord.Embed(
                title="✅ Dołączono do pokoju!",
                description=f"Pokój: **{code}**\n\n💡 Ten pokój został zapamiętany - nie musisz podawać kodu w kolejnych komendach!",
                color=discord.Color.green(),
            )
            embed.add_field(
                name="Co dalej?",
                value="Czekaj aż host rozpocznie grę. Otrzymasz DM ze swoim słowem!",
                inline=False,
            )

            await interaction.followup.send(embed=embed, ephemeral=True)

        elif action.value == "start":
            if not code:
                code = await get_user_room(user_id)
                if not code:
                    await interaction.followup.send(
                        "❌ Nie znaleziono zapamiętanego pokoju! Podaj kod pokoju: `/impostor start code:KOD`",
                        ephemeral=True,
                    )
                    return
                logger.info(f"Using remembered room {code} for user {user_id}")
            else:
                code = code.upper().strip()

            # Verify host and player count, then trigger Cloud Function
            from firestore_client import get_db

            db = get_db()
            room_ref = db.collection("rooms").document(code)
            room_doc = room_ref.get()

            if not room_doc.exists:
                await interaction.followup.send(
                    f"❌ Pokój {code} nie istnieje!", ephemeral=True
                )
                return

            room_data = room_doc.to_dict()

            # Verify host
            if room_data.get("hostUid") != user_id:
                await interaction.followup.send(
                    "❌ Tylko host może rozpocząć grę!", ephemeral=True
                )
                return

            # Check player count
            players_ref = room_ref.collection("players")
            players_count = len(list(players_ref.stream()))

            if players_count < 2:
                await interaction.followup.send(
                    f"❌ Potrzeba minimum 3 graczy do rozpoczęcia gry! (obecnie: {players_count})",
                    ephemeral=True,
                )
                return

            # Trigger Cloud Function by updating status
            room_ref.update({"status": "started"})
            logger.info(
                f"Game started for room {code}, Cloud Function will handle secrets"
            )

            embed = discord.Embed(
                title="🎮 Gra rozpoczęta!",
                description=f"Pokój: **{code}**\n\nGracze Discord otrzymają DM ze swoim słowem!",
                color=discord.Color.blue(),
            )
            embed.add_field(
                name="Gracze", value=f"{players_count} graczy w grze", inline=True
            )
            embed.set_footer(
                text="DM-y będą wysłane za chwilę... Jeśli nie dostaniesz, użyj /impostor reveal"
            )

            await interaction.followup.send(embed=embed)

        elif action.value == "status":
            if not code:
                code = await get_user_room(user_id)
                if not code:
                    await interaction.followup.send(
                        "❌ Nie znaleziono zapamiętanego pokoju! Podaj kod pokoju: `/impostor status code:KOD`",
                        ephemeral=True,
                    )
                    return
                logger.info(f"Using remembered room {code} for user {user_id}")
            else:
                code = code.upper().strip()
            room_status = await game_logic.get_room_status(code)

            if not room_status:
                await interaction.followup.send(
                    f"❌ Pokój {code} nie istnieje!", ephemeral=True
                )
                return

            status_emoji = {
                "lobby": "⏳",
                "dealt": "🎮",
                "playing": "🎭",
                "ended": "🏁",
            }

            status_text = {
                "lobby": "Poczekalnia",
                "dealt": "Ujawnianie słów",
                "playing": "Gra w toku",
                "ended": "Zakończona",
            }

            embed = discord.Embed(
                title=f"Status pokoju {code}", color=discord.Color.blue()
            )
            embed.add_field(
                name="Status",
                value=f"{status_emoji.get(room_status['status'], '❓')} {status_text.get(room_status['status'], 'Nieznany')}",
                inline=True,
            )
            embed.add_field(
                name="Gracze",
                value=f"{len(room_status['players'])} graczy",
                inline=True,
            )
            embed.add_field(
                name="Dołączanie",
                value="🟢 Otwarte" if room_status.get("allowJoin") else "🔴 Zamknięte",
                inline=True,
            )
            embed.add_field(
                name="Lista graczy",
                value=format_player_list(room_status["players"]),
                inline=False,
            )

            await interaction.followup.send(embed=embed)

        elif action.value == "reveal":
            if not code:
                code = await get_user_room(user_id)
                if not code:
                    await interaction.followup.send(
                        "❌ Nie znaleziono zapamiętanego pokoju! Podaj kod pokoju: `/impostor reveal code:KOD`",
                        ephemeral=True,
                    )
                    return
                logger.info(f"Using remembered room {code} for user {user_id}")
            else:
                code = code.upper().strip()
            secret = await game_logic.get_player_secret(code, user_id)

            if not secret:
                await interaction.followup.send(
                    f"❌ Nie znaleziono twojej roli w pokoju {code}. Czy gra została rozpoczęta?",
                    ephemeral=True,
                )
                return

            # Mark player as having seen their word
            await game_logic.mark_player_seen(code, user_id)

            if secret["role"] == "impostor":
                embed = discord.Embed(
                    title="🎭 Jesteś IMPOSTOREM!",
                    description="Inni gracze widzą słowo. Ty musisz udawać, że je znasz!",
                    color=discord.Color.purple(),
                )
            else:
                embed = discord.Embed(
                    title="📝 Twoje słowo",
                    description=f"**{secret['word']}**",
                    color=discord.Color.green(),
                )

            embed.add_field(name="Pokój", value=f"`{code}`", inline=False)

            await interaction.followup.send(embed=embed, ephemeral=True)

        elif action.value == "restart":
            if not code:
                code = await get_user_room(user_id)
                if not code:
                    await interaction.followup.send(
                        "❌ Nie znaleziono zapamiętanego pokoju! Podaj kod pokoju: `/impostor restart code:KOD`",
                        ephemeral=True,
                    )
                    return
                logger.info(f"Using remembered room {code} for user {user_id}")
            else:
                code = code.upper().strip()

            try:
                await game_logic.restart_game(code, user_id)

                embed = discord.Embed(
                    title="🔄 Gra zrestartowana!",
                    description=f"Pokój: **{code}**\n\nNowa runda rozpoczyna się teraz!\nGracze Discord otrzymają DM z nowymi rolami.",
                    color=discord.Color.orange(),
                )
                embed.set_footer(
                    text="Wszyscy gracze pozostali w pokoju. Wybrano nowe słowo i impostora."
                )

                await interaction.followup.send(embed=embed)
            except ValueError as e:
                await interaction.followup.send(f"❌ {str(e)}", ephemeral=True)

    except ValueError as e:
        await interaction.followup.send(f"❌ {str(e)}", ephemeral=True)
    except Exception as e:
        logger.error(f"Error in command {action.value}: {e}")
        await interaction.followup.send(f"❌ Wystąpił błąd: {str(e)}", ephemeral=True)
