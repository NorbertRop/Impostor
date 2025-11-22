import discord
from firestore_client import get_db
from loguru import logger


class HintsView(discord.ui.View):
    def __init__(self, hints: list[str], room_id: str, user_id: str):
        super().__init__(timeout=None)
        self.hints = hints
        self.room_id = room_id
        self.user_id = user_id
        self.current_index = 1
        self.update_button()

    def update_button(self):
        self.clear_items()
        if self.current_index < len(self.hints):
            remaining = len(self.hints) - self.current_index
            button = discord.ui.Button(
                label=f"Pokaż kolejną podpowiedź ({remaining})",
                style=discord.ButtonStyle.primary,
                custom_id="show_hint",
            )
            button.callback = self.show_next_hint
            self.add_item(button)

    async def show_next_hint(self, interaction: discord.Interaction):
        self.current_index += 1
        self.update_button()

        # Update hints used in Firestore
        try:
            from bot.firestore_client import update_document

            # We need room_id and user_id to update the secret
            # These are not directly available in the view, so we need to pass them
            if hasattr(self, "room_id") and hasattr(self, "user_id"):
                await update_document(
                    f"rooms/{self.room_id}/secrets/{self.user_id}",
                    {"hintsUsed": self.current_index},
                )
        except Exception as e:
            logger.error(f"Error updating hints used: {e}")

        # Reconstruct embed with more hints
        embed = interaction.message.embeds[0]
        # Find the hints field and update it
        for i, field in enumerate(embed.fields):
            if field.name == "💡 Podpowiedzi":
                visible_hints = self.hints[: self.current_index]
                hints_text = "\n".join([f"• {hint}" for hint in visible_hints])
                embed.set_field_at(
                    i, name="💡 Podpowiedzi", value=hints_text, inline=False
                )
                break

        await interaction.response.edit_message(embed=embed, view=self)


async def send_word_dm(
    user: discord.User,
    room_id: str,
    secret: dict,
    room_data: dict | None = None,
    all_players: dict | None = None,
    hints: list[str] | None = None,
):
    try:
        view = None
        if secret["role"] == "impostor":
            embed = discord.Embed(
                title="🎭 Jesteś IMPOSTOREM!",
                description=(
                    "Inni gracze widzą słowo. Ty musisz udawać, że je znasz!\n"
                    "Spróbuj odkryć, co to za słowo, obserwując innych graczy."
                ),
                color=discord.Color.purple(),
            )

            # Add hints if provided (from hint_data collection)
            if hints:
                # Show only first hint initially
                visible_hints = hints[:1]
                hints_text = "\n".join([f"• {hint}" for hint in visible_hints])
                embed.add_field(name="💡 Podpowiedzi", value=hints_text, inline=False)

                if len(hints) > 1:
                    view = HintsView(hints, room_id, str(user.id))
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

        # Add speaking order if available
        if room_data and all_players and room_data.get("speakingOrder"):
            speaking_order = room_data["speakingOrder"]
            discord_user_id = secret.get("discordId")

            order_lines = []
            position = 1
            for player_id in speaking_order:
                player = all_players.get(player_id, {})
                player_name = player.get("name", "Nieznany gracz") or "Nieznany gracz"

                # Skip players with missing or invalid data
                if not player or not player_name.strip():
                    continue

                # Check if this is the current user
                if player_id == discord_user_id:
                    order_lines.append(f"**{position}.** {player_name} **(TY)**")
                else:
                    order_lines.append(f"{position}. {player_name}")

                position += 1

            order_text = "\n".join(order_lines)
            embed.add_field(
                name="🎤 Kolejność wypowiedzi", value=order_text, inline=False
            )

        embed.add_field(name="Kod pokoju", value=f"`{room_id}`", inline=False)
        embed.set_footer(
            text="Możesz użyć /impostor reveal aby zobaczyć swoje słowo ponownie"
        )

        await user.send(embed=embed, view=view)
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
        lines.append(f"{i}. {player['name']} {status} {source}")

    return "\n".join(lines)
