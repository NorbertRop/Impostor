import discord
from discord import app_commands
from bot.bot import bot
from bot.utils import send_word_dm, format_player_list
import game_logic
from config import config

@bot.tree.command(name="impostor", description="Gra w Impostora")
@app_commands.describe(
    action="Akcja do wykonania",
    code="Kod pokoju (dla join/start/status/reveal)"
)
@app_commands.choices(action=[
    app_commands.Choice(name="create - Stwórz nowy pokój", value="create"),
    app_commands.Choice(name="join - Dołącz do pokoju", value="join"),
    app_commands.Choice(name="start - Rozpocznij grę", value="start"),
    app_commands.Choice(name="status - Sprawdź status pokoju", value="status"),
    app_commands.Choice(name="reveal - Pokaż słowo ponownie", value="reveal"),
])
async def impostor_command(
    interaction: discord.Interaction,
    action: app_commands.Choice[str],
    code: str = None
):
    await interaction.response.defer(ephemeral=(action.value in ['join', 'reveal']))
    
    user_id = str(interaction.user.id)
    username = interaction.user.display_name
    
    try:
        if action.value == "create":
            room_id = await game_logic.create_room(
                user_id,
                username,
                source='discord',
                channel_id=str(interaction.channel_id)
            )
            
            embed = discord.Embed(
                title="✅ Pokój utworzony!",
                description=f"Kod pokoju: **{room_id}**",
                color=discord.Color.green()
            )
            embed.add_field(
                name="Jak dołączyć?",
                value=(
                    f"Discord: `/impostor join code:{room_id}`\n"
                    f"Web: {config.WEB_BASE_URL}/r/{room_id}"
                ),
                inline=False
            )
            embed.add_field(
                name="Rozpoczęcie gry",
                value=f"Gdy będzie minimum 3 graczy, użyj:\n`/impostor start code:{room_id}`",
                inline=False
            )
            embed.set_footer(text="Tylko host może rozpocząć grę")
            
            await interaction.followup.send(embed=embed)
        
        elif action.value == "join":
            if not code:
                await interaction.followup.send("❌ Musisz podać kod pokoju!", ephemeral=True)
                return
            
            code = code.upper().strip()
            await game_logic.join_room(code, user_id, username, source='discord')
            
            embed = discord.Embed(
                title="✅ Dołączono do pokoju!",
                description=f"Pokój: **{code}**",
                color=discord.Color.green()
            )
            embed.add_field(
                name="Co dalej?",
                value="Czekaj aż host rozpocznie grę. Otrzymasz DM ze swoim słowem!",
                inline=False
            )
            embed.add_field(
                name="Link do pokoju",
                value=f"{config.WEB_BASE_URL}/r/{code}",
                inline=False
            )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
        
        elif action.value == "start":
            if not code:
                await interaction.followup.send("❌ Musisz podać kod pokoju!", ephemeral=True)
                return
            
            code = code.upper().strip()
            secrets = await game_logic.start_game(code, user_id)
            
            # Send DMs to all players
            success_count = 0
            failed_users = []
            
            for uid, secret in secrets.items():
                discord_id = secret.get('discord_id')
                if discord_id:
                    try:
                        user = await bot.fetch_user(int(discord_id))
                        success = await send_word_dm(user, code, secret, config.WEB_BASE_URL)
                        if success:
                            success_count += 1
                        else:
                            failed_users.append(secret['name'])
                    except Exception as e:
                        print(f"Failed to send DM to {discord_id}: {e}")
                        failed_users.append(secret['name'])
            
            embed = discord.Embed(
                title="🎮 Gra rozpoczęta!",
                description=f"Pokój: **{code}**",
                color=discord.Color.blue()
            )
            embed.add_field(
                name="Gracze",
                value=f"{len(secrets)} graczy otrzymało swoje role",
                inline=True
            )
            embed.add_field(
                name="DM wysłane",
                value=f"{success_count}/{len([s for s in secrets.values() if s.get('discord_id')])}",
                inline=True
            )
            
            if failed_users:
                embed.add_field(
                    name="⚠️ Nie udało się wysłać DM",
                    value="\n".join(failed_users) + "\n\n*Sprawdź ustawienia prywatności!*",
                    inline=False
                )
            
            embed.add_field(
                name="Link do gry",
                value=f"{config.WEB_BASE_URL}/r/{code}",
                inline=False
            )
            embed.set_footer(text="Jeśli nie dostałeś DM, użyj /impostor reveal")
            
            await interaction.followup.send(embed=embed)
        
        elif action.value == "status":
            if not code:
                await interaction.followup.send("❌ Musisz podać kod pokoju!", ephemeral=True)
                return
            
            code = code.upper().strip()
            room_status = await game_logic.get_room_status(code)
            
            if not room_status:
                await interaction.followup.send(f"❌ Pokój {code} nie istnieje!", ephemeral=True)
                return
            
            status_emoji = {
                'lobby': '⏳',
                'dealt': '🎮',
                'playing': '🎭',
                'ended': '🏁'
            }
            
            status_text = {
                'lobby': 'Poczekalnia',
                'dealt': 'Ujawnianie słów',
                'playing': 'Gra w toku',
                'ended': 'Zakończona'
            }
            
            embed = discord.Embed(
                title=f"Status pokoju {code}",
                color=discord.Color.blue()
            )
            embed.add_field(
                name="Status",
                value=f"{status_emoji.get(room_status['status'], '❓')} {status_text.get(room_status['status'], 'Nieznany')}",
                inline=True
            )
            embed.add_field(
                name="Gracze",
                value=f"{len(room_status['players'])} graczy",
                inline=True
            )
            embed.add_field(
                name="Dołączanie",
                value="🟢 Otwarte" if room_status.get('allowJoin') else "🔴 Zamknięte",
                inline=True
            )
            embed.add_field(
                name="Lista graczy",
                value=format_player_list(room_status['players']),
                inline=False
            )
            embed.add_field(
                name="Link",
                value=f"{config.WEB_BASE_URL}/r/{code}",
                inline=False
            )
            
            await interaction.followup.send(embed=embed)
        
        elif action.value == "reveal":
            if not code:
                await interaction.followup.send("❌ Musisz podać kod pokoju!", ephemeral=True)
                return
            
            code = code.upper().strip()
            secret = await game_logic.get_player_secret(code, user_id)
            
            if not secret:
                await interaction.followup.send(
                    f"❌ Nie znaleziono twojej roli w pokoju {code}. Czy gra została rozpoczęta?",
                    ephemeral=True
                )
                return
            
            if secret['role'] == 'impostor':
                embed = discord.Embed(
                    title="🎭 Jesteś IMPOSTOREM!",
                    description="Inni gracze widzą słowo. Ty musisz udawać, że je znasz!",
                    color=discord.Color.purple()
                )
            else:
                embed = discord.Embed(
                    title="📝 Twoje słowo",
                    description=f"**{secret['word']}**",
                    color=discord.Color.green()
                )
            
            embed.add_field(
                name="Pokój",
                value=f"`{code}`",
                inline=True
            )
            embed.add_field(
                name="Link",
                value=f"[Otwórz]({config.WEB_BASE_URL}/r/{code})",
                inline=True
            )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
    
    except ValueError as e:
        await interaction.followup.send(f"❌ {str(e)}", ephemeral=True)
    except Exception as e:
        print(f"Error in command {action.value}: {e}")
        await interaction.followup.send(
            f"❌ Wystąpił błąd: {str(e)}",
            ephemeral=True
        )

