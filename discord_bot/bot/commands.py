import discord
import game_logic
from discord import app_commands
from loguru import logger
from user_sessions import get_user_room, set_user_room
 from firestore_client import get_db

from bot.bot import bot
from bot.utils import format_player_list


@bot.tree.command(name="create", description="Stwórz nowy pokój do gry w Impostora")
async def create_command(interaction: discord.Interaction):
    await interaction.response.defer()

    user_id = str(interaction.user.id)
    username = interaction.user.display_name

    try:
        room_id = await game_logic.create_room(
            user_id,
            username,
            source="discord",
            channel_id=str(interaction.channel_id),
        )

        await set_user_room(user_id, room_id)

        bot.firestore_listener.start_room_listener(room_id)
        logger.info(f"Started listener for room {room_id}")

        embed = discord.Embed(
            title="✅ Pokój utworzony!",
            description=f"Kod pokoju: **{room_id}**\n\n💡",
            color=discord.Color.green(),
        )
        embed.add_field(
            name="Jak dołączyć?",
            value=f"Discord: `/join code:{room_id}`",
            inline=False,
        )
        embed.add_field(
            name="Rozpoczęcie gry",
            value="Gdy będzie minimum 3 graczy, użyj:\n`/start`",
            inline=False,
        )
        embed.set_footer(text="Tylko host może rozpocząć grę")

        await interaction.followup.send(embed=embed)

    except Exception as e:
        logger.error(f"Error in create command: {e}")
        await interaction.followup.send(f"❌ Wystąpił błąd: {str(e)}", ephemeral=True)


@bot.tree.command(name="join", description="Dołącz do pokoju")
@app_commands.describe(code="Kod pokoju")
async def join_command(interaction: discord.Interaction, code: str):
    await interaction.response.defer(ephemeral=True)

    user_id = str(interaction.user.id)
    username = interaction.user.display_name

    try:
        code = code.upper().strip()
        await game_logic.join_room(code, user_id, username, source="discord")

        await set_user_room(user_id, code)

        bot.firestore_listener.start_room_listener(code)
        logger.info(f"Started listener for room {code}")

        embed = discord.Embed(
            title="✅ Dołączono do pokoju!",
            description=f"Pokój: **{code}**\n\n💡",
            color=discord.Color.green(),
        )
        embed.add_field(
            name="Co dalej?",
            value="Czekaj aż host rozpocznie grę. Otrzymasz DM ze swoim słowem!",
            inline=False,
        )

        await interaction.followup.send(embed=embed, ephemeral=True)

    except ValueError as e:
        await interaction.followup.send(f"❌ {str(e)}", ephemeral=True)
    except Exception as e:
        logger.error(f"Error in join command: {e}")
        await interaction.followup.send(f"❌ Wystąpił błąd: {str(e)}", ephemeral=True)


@bot.tree.command(name="start", description="Rozpocznij grę (tylko host)")
@app_commands.describe(code="Kod pokoju (opcjonalny - użyje zapamiętanego)")
async def start_command(interaction: discord.Interaction, code: str | None = None):
    await interaction.response.defer()

    user_id = str(interaction.user.id)

    try:
        if not code:
            code = await get_user_room(user_id)
            if not code:
                await interaction.followup.send(
                    "❌ Nie znaleziono zapamiętanego pokoju! Podaj kod: `/start code:CODE`",
                    ephemeral=True,
                )
                return
            logger.info(f"Using remembered room {code} for user {user_id}")
        else:
            code = code.upper().strip()

        db = get_db()
        room_ref = db.collection("rooms").document(code)
        room_doc = room_ref.get()

        if not room_doc.exists:
            await interaction.followup.send(
                f"❌ Pokój {code} nie istnieje!", ephemeral=True
            )
            return

        room_data = room_doc.to_dict()

        if room_data.get("hostUid") != user_id:
            await interaction.followup.send(
                "❌ Tylko host może rozpocząć grę!", ephemeral=True
            )
            return

        players_ref = room_ref.collection("players")
        players_count = len(list(players_ref.stream()))

        if players_count < 2:
            await interaction.followup.send(
                f"❌ Potrzeba minimum 3 graczy do rozpoczęcia gry! (obecnie: {players_count})",
                ephemeral=True,
            )
            return

        room_ref.update({"status": "started"})
        logger.info(f"Game started for room {code}, Cloud Function will handle secrets")

        embed = discord.Embed(
            title="🎮 Gra rozpoczęta!",
            description=f"Pokój: **{code}**\n\nGracze Discord otrzymają DM ze swoim słowem!",
            color=discord.Color.blue(),
        )
        embed.add_field(
            name="Gracze", value=f"{players_count} graczy w grze", inline=True
        )
        embed.set_footer(
            text="DM-y będą wysłane za chwilę... Jeśli nie dostaniesz, użyj /reveal"
        )

        await interaction.followup.send(embed=embed)

    except ValueError as e:
        await interaction.followup.send(f"❌ {str(e)}", ephemeral=True)
    except Exception as e:
        logger.error(f"Error in start command: {e}")
        await interaction.followup.send(f"❌ Wystąpił błąd: {str(e)}", ephemeral=True)


@bot.tree.command(name="status", description="Sprawdź status pokoju")
@app_commands.describe(code="Kod pokoju (opcjonalny - użyje zapamiętanego)")
async def status_command(interaction: discord.Interaction, code: str | None = None):
    await interaction.response.defer()

    user_id = str(interaction.user.id)

    try:
        if not code:
            code = await get_user_room(user_id)
            if not code:
                await interaction.followup.send(
                    "❌ Nie znaleziono zapamiętanego pokoju! Podaj kod: `/status code:KOD`",
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

        embed = discord.Embed(title=f"Status pokoju {code}", color=discord.Color.blue())
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

    except Exception as e:
        logger.error(f"Error in status command: {e}")
        await interaction.followup.send(f"❌ Wystąpił błąd: {str(e)}", ephemeral=True)


@bot.tree.command(name="reveal", description="Pokaż swoje słowo/rolę ponownie")
@app_commands.describe(code="Kod pokoju (opcjonalny - użyje zapamiętanego)")
async def reveal_command(interaction: discord.Interaction, code: str | None = None):
    await interaction.response.defer(ephemeral=True)

    user_id = str(interaction.user.id)

    try:
        if not code:
            code = await get_user_room(user_id)
            if not code:
                await interaction.followup.send(
                    "❌ Nie znaleziono zapamiętanego pokoju! Podaj kod: `/reveal code:KOD`",
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

    except Exception as e:
        logger.error(f"Error in reveal command: {e}")
        await interaction.followup.send(f"❌ Wystąpił błąd: {str(e)}", ephemeral=True)


@bot.tree.command(name="restart", description="Zrestartuj grę (tylko host)")
@app_commands.describe(code="Kod pokoju (opcjonalny - użyje zapamiętanego)")
async def restart_command(interaction: discord.Interaction, code: str | None = None):
    await interaction.response.defer()

    user_id = str(interaction.user.id)

    try:
        if not code:
            code = await get_user_room(user_id)
            if not code:
                await interaction.followup.send(
                    "❌ Nie znaleziono zapamiętanego pokoju! Podaj kod: `/restart code:KOD`",
                    ephemeral=True,
                )
                return
            logger.info(f"Using remembered room {code} for user {user_id}")
        else:
            code = code.upper().strip()

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
    except Exception as e:
        logger.error(f"Error in restart command: {e}")
        await interaction.followup.send(f"❌ Wystąpił błąd: {str(e)}", ephemeral=True)
