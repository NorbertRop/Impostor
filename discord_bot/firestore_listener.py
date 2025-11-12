"""
Firestore listener for Discord bot
Listens for game state changes and sends DMs to Discord players
"""

import asyncio

import discord
from bot.utils import send_word_dm
from firestore_client import get_db
from loguru import logger


class FirestoreListener:
    """Listens to Firestore changes and triggers Discord actions"""

    def __init__(self, bot: discord.Client):
        self.bot = bot
        self.db = get_db()
        self.active_listeners = {}

    def start_room_listener(self, room_id: str):
        """Start listening to a specific room for secret changes"""
        if room_id in self.active_listeners:
            logger.debug(f"Already listening to room {room_id}")
            return

        secrets_ref = (
            self.db.collection("rooms").document(room_id).collection("secrets")
        )

        def on_snapshot(col_snapshot, changes, read_time):
            """Handle Firestore snapshot changes"""
            for change in changes:
                if change.type.name == "ADDED":
                    secret_doc = change.document
                    secret_data = secret_doc.to_dict()

                    # Check if this player has a Discord ID
                    discord_id = secret_data.get("discordId")
                    if discord_id:
                        # Schedule DM sending in the bot's event loop
                        # Use asyncio.run_coroutine_threadsafe since Firestore callbacks
                        # run in a separate thread
                        asyncio.run_coroutine_threadsafe(
                            self._send_discord_dm(room_id, discord_id, secret_data),
                            self.bot.loop,
                        )
                        logger.info(
                            f"Scheduled DM for discord_id={discord_id} in room {room_id}"
                        )

        # Start watching the collection
        watch = secrets_ref.on_snapshot(on_snapshot)
        self.active_listeners[room_id] = watch
        logger.info(f"Started listening to room {room_id} for secret changes")

    def stop_room_listener(self, room_id: str):
        """Stop listening to a specific room"""
        if room_id in self.active_listeners:
            self.active_listeners[room_id].unsubscribe()
            del self.active_listeners[room_id]
            logger.info(f"Stopped listening to room {room_id}")

    async def _send_discord_dm(self, room_id: str, discord_id: str, secret: dict):
        """Send DM to a Discord user with their role and word"""
        try:
            user_id = int(discord_id)
            user = await self.bot.fetch_user(user_id)

            if user:
                # Fetch room data and all players for speaking order
                room_ref = self.db.collection("rooms").document(room_id)
                room_doc = room_ref.get()
                room_data = room_doc.to_dict() if room_doc.exists else None

                # Fetch all players
                players_ref = room_ref.collection("players")
                players_docs = list(players_ref.stream())
                all_players = {doc.id: doc.to_dict() for doc in players_docs}

                success = await send_word_dm(
                    user, room_id, secret, room_data, all_players
                )
                if success:
                    # Mark player as having seen their word
                    player_ref = (
                        self.db.collection("rooms")
                        .document(room_id)
                        .collection("players")
                        .document(discord_id)
                    )
                    player_ref.update({"seen": True})
                    logger.success(
                        f"Sent DM to Discord user {user.name} for room {room_id} and marked as seen"
                    )
                else:
                    logger.warning(
                        f"Failed to send DM to Discord user {user.name} for room {room_id}"
                    )
            else:
                logger.error(f"Could not find Discord user with ID {discord_id}")

        except Exception as e:
            logger.error(f"Error sending Discord DM: {e}")

    def cleanup(self):
        """Stop all listeners"""
        for room_id in list(self.active_listeners.keys()):
            self.stop_room_listener(room_id)
