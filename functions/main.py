"""
Firebase Cloud Functions for Impostor Game

Functions:
- on_game_start: Triggered when room status changes to 'started'
- cleanup_old_rooms: Scheduled function to clean up old rooms (daily)
- manual_cleanup: HTTP endpoint for manual cleanup
"""

import random
from datetime import datetime, timedelta

from firebase_admin import firestore, initialize_app
from firebase_functions import firestore_fn, https_fn, options, scheduler_fn
from google.cloud.firestore_v1 import FieldFilter

initialize_app()

# Load word list
WORDS = []
try:
    with open("words.txt", "r", encoding="utf-8") as f:
        WORDS = [line.strip() for line in f if line.strip()]
        print(f"✅ Loaded {len(WORDS)} words from words.txt")
except FileNotFoundError:
    print("❌ Failed to load words.txt, using fallback")
    WORDS = ["kot", "pies", "dom", "drzewo", "słońce", "księżyc"]


def get_random_word() -> str:
    """Select a random word from the word list"""
    return random.choice(WORDS)


def select_impostor(player_ids: list[str]) -> str:
    """Select a random impostor from players"""
    return random.choice(player_ids)


@firestore_fn.on_document_updated(
    document="rooms/{room_id}", region=options.SupportedRegion.US_CENTRAL1
)
def on_game_start(event: firestore_fn.Event[firestore_fn.Change]) -> None:
    """
    Firestore trigger - automatically starts game when status changes to 'started'
    Assigns random word and selects impostor
    """
    before = event.data.before
    after = event.data.after
    room_id = event.params["room_id"]

    # Check if status changed to 'started'
    before_status = before.get("status") if before else None
    after_status = after.get("status") if after else None

    if before_status != "started" and after_status == "started":
        print(f"🎮 Game starting for room: {room_id}")

        try:
            db = firestore.client()
            room_ref = db.collection("rooms").document(room_id)

            # Get all players
            players_ref = room_ref.collection("players")
            players_docs = list(players_ref.stream())
            player_ids = [doc.id for doc in players_docs]
            players = {doc.id: doc.to_dict() for doc in players_docs}

            if len(player_ids) < 2:
                print("❌ Not enough players to start game")
                return

            # Select random word and impostor
            word = get_random_word()
            impostor_id = select_impostor(player_ids)

            print(f"📝 Selected word: {word}")
            print(f"🎭 Selected impostor: {impostor_id}")

            # Create secrets for each player
            batch = db.batch()
            secrets_ref = room_ref.collection("secrets")

            for player_id in player_ids:
                player = players[player_id]
                is_impostor = player_id == impostor_id

                secret_data = {
                    "name": player.get("name"),
                    "role": "impostor" if is_impostor else "player",
                    "word": None if is_impostor else word,
                    "discordId": player.get("discordId"),
                    "createdAt": firestore.SERVER_TIMESTAMP,
                }

                batch.set(secrets_ref.document(player_id), secret_data)

            # Update room with game info
            batch.update(
                room_ref,
                {
                    "word": word,
                    "impostorId": impostor_id,
                    "status": "dealt",
                    "startedAt": firestore.SERVER_TIMESTAMP,
                },
            )

            batch.commit()

            print(f"✅ Game started successfully for room {room_id}")

        except Exception as e:
            print(f"❌ Error starting game for room {room_id}: {e}")
            raise


@scheduler_fn.on_schedule(
    schedule="every 24 hours", region=options.SupportedRegion.US_CENTRAL1
)
def cleanup_old_rooms(event: scheduler_fn.ScheduledEvent) -> dict:
    """
    Scheduled function to clean up old rooms
    Runs every 24 hours and removes rooms older than 24 hours
    """
    db = firestore.client()
    cutoff_time = datetime.now() - timedelta(hours=24)

    print(f"🧹 Starting cleanup of rooms older than {cutoff_time.isoformat()}")

    try:
        rooms_query = db.collection("rooms").where(
            filter=FieldFilter("createdAt", "<", cutoff_time)
        )
        rooms_docs = list(rooms_query.stream())

        if not rooms_docs:
            print("✅ No old rooms to clean up")
            return {"success": True, "roomsDeleted": 0}

        deleted_count = 0

        for room_doc in rooms_docs:
            room_id = room_doc.id
            print(f"🗑️  Deleting room: {room_id}")

            # Delete subcollections
            players_ref = room_doc.reference.collection("players")
            for player_doc in players_ref.stream():
                player_doc.reference.delete()

            secrets_ref = room_doc.reference.collection("secrets")
            for secret_doc in secrets_ref.stream():
                secret_doc.reference.delete()

            # Delete room document
            room_doc.reference.delete()
            deleted_count += 1

        print(f"✅ Cleanup complete: {deleted_count} room(s) deleted")
        return {"success": True, "roomsDeleted": deleted_count}

    except Exception as e:
        print(f"❌ Cleanup error: {e}")
        raise


@https_fn.on_request(
    region=options.SupportedRegion.US_CENTRAL1,
    cors=options.CorsOptions(
        cors_origins="*",
        cors_methods=["GET", "POST"],
    ),
)
def manual_cleanup(req: https_fn.Request) -> https_fn.Response:
    """
    HTTP function for manual cleanup trigger
    Can be called directly for testing or manual cleanup
    """
    db = firestore.client()
    hours_param = req.args.get("hours", "24")

    try:
        hours = int(hours_param)
        if hours <= 0:
            return https_fn.Response(
                {"error": "Invalid hours parameter"},
                status=400,
                headers={"Content-Type": "application/json"},
            )
    except ValueError:
        return https_fn.Response(
            {"error": "Invalid hours parameter"},
            status=400,
            headers={"Content-Type": "application/json"},
        )

    cutoff_time = datetime.now() - timedelta(hours=hours)

    print(f"🧹 Manual cleanup: rooms older than {cutoff_time.isoformat()}")

    try:
        rooms_query = db.collection("rooms").where(
            filter=FieldFilter("createdAt", "<", cutoff_time)
        )
        rooms_docs = list(rooms_query.stream())

        if not rooms_docs:
            return https_fn.Response(
                {
                    "message": "No old rooms to clean up",
                    "roomsDeleted": 0,
                    "hoursThreshold": hours,
                },
                headers={"Content-Type": "application/json"},
            )

        deleted_count = 0

        for room_doc in rooms_docs:
            room_id = room_doc.id

            # Delete subcollections
            players_ref = room_doc.reference.collection("players")
            for player_doc in players_ref.stream():
                player_doc.reference.delete()

            secrets_ref = room_doc.reference.collection("secrets")
            for secret_doc in secrets_ref.stream():
                secret_doc.reference.delete()

            # Delete room document
            room_doc.reference.delete()
            deleted_count += 1

        return https_fn.Response(
            {
                "message": "Cleanup completed successfully",
                "roomsDeleted": deleted_count,
                "hoursThreshold": hours,
            },
            headers={"Content-Type": "application/json"},
        )

    except Exception as e:
        print(f"❌ Manual cleanup error: {e}")
        return https_fn.Response(
            {"error": str(e)}, status=500, headers={"Content-Type": "application/json"}
        )
