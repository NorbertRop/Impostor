import discord
import game_logic
from discord import app_commands
from discord.ui import Button, View
from firestore_client import get_db
from loguru import logger
from user_sessions import get_user_room, set_user_room

from bot.bot import bot
from bot.utils import format_player_list


class GameControlView(View):
    """Unified view with all game control buttons"""

    def __init__(self, room_id: str):
        super().__init__(timeout=None)
        self.room_id = room_id

        # Join button
        join_button = Button(
            label="Dołącz",
            style=discord.ButtonStyle.green,
            emoji="🎮",
            custom_id=f"join:{room_id}",
        )
        join_button.callback = self.join_callback
        self.add_item(join_button)

        # Start button
        start_button = Button(
            label="Start",
            style=discord.ButtonStyle.blurple,
            emoji="▶️",
            custom_id=f"start:{room_id}",
        )
        start_button.callback = self.start_callback
        self.add_item(start_button)

        # Restart button
        restart_button = Button(
            label="Restart",
            style=discord.ButtonStyle.blurple,
            emoji="🔄",
            custom_id=f"restart:{room_id}",
        )
        restart_button.callback = self.restart_callback
        self.add_item(restart_button)

        # Status button
        status_button = Button(
            label="Status",
            style=discord.ButtonStyle.gray,
            emoji="📊",
            custom_id=f"status:{room_id}",
        )
        status_button.callback = self.status_callback
        self.add_item(status_button)

    async def join_callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        user_id = str(interaction.user.id)
        username = interaction.user.display_name

        try:
            await game_logic.join_room(
                self.room_id, user_id, username, source="discord"
            )

            await set_user_room(user_id, self.room_id)

            bot.firestore_listener.start_room_listener(self.room_id)
            logger.info(
                f"User {username} ({user_id}) joined room {self.room_id} via button"
            )

            embed = discord.Embed(
                title="✅ Dołączono do pokoju!",
                description=f"Pokój: **{self.room_id}**",
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
            logger.error(f"Error joining game via button: {e}")
            await interaction.followup.send(
                f"❌ Wystąpił błąd: {str(e)}", ephemeral=True
            )

    async def start_callback(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)

        try:
            db = get_db()
            room_ref = db.collection("rooms").document(self.room_id)
            room_doc = room_ref.get()

            if not room_doc.exists:
                await interaction.response.send_message(
                    f"❌ Pokój {self.room_id} nie istnieje!", ephemeral=True
                )
                return

            room_data = room_doc.to_dict()

            if room_data.get("hostUid") != user_id:
                await interaction.response.send_message(
                    "❌ Tylko host może rozpocząć grę!", ephemeral=True
                )
                return

            players_ref = room_ref.collection("players")
            players_count = len(list(players_ref.stream()))

            if players_count < 2:
                await interaction.response.send_message(
                    f"❌ Potrzeba minimum 3 graczy do rozpoczęcia gry! (obecnie: {players_count})",
                    ephemeral=True,
                )
                return

            room_ref.update({"status": "started"})
            logger.info(f"Game started for room {self.room_id} via button by {user_id}")

            await interaction.response.defer()

        except ValueError as e:
            await interaction.response.send_message(f"❌ {str(e)}", ephemeral=True)
        except Exception as e:
            logger.error(f"Error starting game via button: {e}")
            await interaction.response.send_message(
                f"❌ Wystąpił błąd: {str(e)}", ephemeral=True
            )

    async def restart_callback(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)

        try:
            await game_logic.restart_game(self.room_id, user_id)

            logger.info(f"User {user_id} restarted room {self.room_id} via button")

            await interaction.response.defer()

        except ValueError as e:
            await interaction.response.send_message(f"❌ {str(e)}", ephemeral=True)
        except Exception as e:
            logger.error(f"Error restarting game via button: {e}")
            await interaction.response.send_message(
                f"❌ Wystąpił błąd: {str(e)}", ephemeral=True
            )

    async def status_callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        try:
            room_status = await game_logic.get_room_status(self.room_id)

            if not room_status:
                await interaction.followup.send(
                    f"❌ Pokój {self.room_id} nie istnieje!", ephemeral=True
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
                title=f"Status pokoju {self.room_id}", color=discord.Color.blue()
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

            await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception as e:
            logger.error(f"Error fetching status via button: {e}")
            await interaction.followup.send(
                f"❌ Wystąpił błąd: {str(e)}", ephemeral=True
            )


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
            description=f"Kod pokoju: **{room_id}**",
            color=discord.Color.green(),
        )
        embed.add_field(
            name="Sterowanie",
            value="🎮 **Dołącz** - wejdź do gry\n▶️ **Start** - rozpocznij (host, min. 3 graczy)\n🔄 **Restart** - nowa runda (host)\n📊 **Status** - sprawdź stan gry",
            inline=False,
        )
        embed.set_footer(text="Tylko host może rozpocząć i zrestartować grę")

        view = GameControlView(room_id)
        await interaction.followup.send(embed=embed, view=view)

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

    except ValueError as e:
        await interaction.followup.send(f"❌ {str(e)}", ephemeral=True)
    except Exception as e:
        logger.error(f"Error in restart command: {e}")
        await interaction.followup.send(f"❌ Wystąpił błąd: {str(e)}", ephemeral=True)
