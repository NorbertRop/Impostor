import discord
from loguru import logger


async def send_word_dm(user: discord.User, room_id: str, secret: dict):
    try:
        if secret["role"] == "impostor":
            embed = discord.Embed(
                title="🎭 Jesteś IMPOSTOREM!",
                description=(
                    "Inni gracze widzą słowo. Ty musisz udawać, że je znasz!\n"
                    "Spróbuj odkryć, co to za słowo, obserwując innych graczy."
                ),
                color=discord.Color.purple(),
            )

            # Add hints if available
            hints = secret.get("hints", [])
            if hints:
                hints_text = "\n".join([f"• {hint}" for hint in hints])
                embed.add_field(name="💡 Podpowiedzi", value=hints_text, inline=False)
        else:
            embed = discord.Embed(
                title="📝 Twoje słowo",
                description=f"**{secret['word']}**",
                color=discord.Color.green(),
            )
            embed.add_field(
                name="Pamiętaj!",
                value="Zapamiętaj to słowo i nie pokazuj go innym!",
                inline=False,
            )

        embed.add_field(name="Kod pokoju", value=f"`{room_id}`", inline=False)
        embed.set_footer(
            text="Możesz użyć /impostor reveal aby zobaczyć swoje słowo ponownie"
        )

        await user.send(embed=embed)
        return True
    except discord.Forbidden:
        return False
    except Exception as e:
        logger.error(f"Error sending DM to {user.name}: {e}")
        return False


def format_player_list(players: list) -> str:
    if not players:
        return "Brak graczy"

    lines = []
    for i, player in enumerate(players, 1):
        status = "👑 Host" if player.get("isHost") else "🎮 Gracz"
        source = "🌐 Web" if player.get("source") == "web" else "💬 Discord"
        seen = "✅" if player.get("seen") else "⏳"
        lines.append(f"{i}. {player['name']} {status} {source} {seen}")

    return "\n".join(lines)
