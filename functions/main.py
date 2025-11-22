"""
Firebase Cloud Functions for Impostor Game

Functions are split into modules:
- room.py: Room creation and joining
- game.py: Game logic (start, restart, hints)
- cleanup.py: Scheduled cleanup tasks
- triggers.py: Firestore triggers
"""

from firebase_admin import initialize_app

# Initialize Firebase Admin once
initialize_app()

# Import functions to export them
from cleanup import (
    cleanup_anonymous_users,
    cleanup_discord_sessions,
    cleanup_old_rooms,
    manual_cleanup,
    manual_user_cleanup,
)
from game import get_next_hint, restart_game, start_game
from room import create_room, join_room
