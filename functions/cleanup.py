import json
from datetime import datetime, timedelta

from firebase_admin import auth, firestore
from firebase_functions import https_fn, options, scheduler_fn
from google.cloud.firestore_v1 import FieldFilter
from utils import delete_discord_sessions_for_room


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
        sessions_deleted = 0

        for room_doc in rooms_docs:
            room_id = room_doc.id
            room_data = room_doc.to_dict()
            room_code = room_data.get("code", "")
            print(f"🗑️  Deleting room: {room_id} (code: {room_code})")

            # Delete discord sessions for this room
            if room_code:
                sessions_deleted += delete_discord_sessions_for_room(db, room_code)

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

        print(
            f"✅ Cleanup complete: {deleted_count} room(s) deleted, {sessions_deleted} discord session(s) deleted"
        )
        return {
            "success": True,
            "roomsDeleted": deleted_count,
            "sessionsDeleted": sessions_deleted,
        }

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
                json.dumps({"error": "Invalid hours parameter"}),
                status=400,
                headers={"Content-Type": "application/json"},
            )
    except ValueError:
        return https_fn.Response(
            json.dumps({"error": "Invalid hours parameter"}),
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
                json.dumps(
                    {
                        "message": "No old rooms to clean up",
                        "roomsDeleted": 0,
                        "sessionsDeleted": 0,
                        "hoursThreshold": hours,
                    }
                ),
                headers={"Content-Type": "application/json"},
            )

        deleted_count = 0
        sessions_deleted = 0

        for room_doc in rooms_docs:
            room_data = room_doc.to_dict()
            room_code = room_data.get("code", "")

            # Delete discord sessions for this room
            if room_code:
                sessions_deleted += delete_discord_sessions_for_room(db, room_code)

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
            json.dumps(
                {
                    "message": "Cleanup completed successfully",
                    "roomsDeleted": deleted_count,
                    "sessionsDeleted": sessions_deleted,
                    "hoursThreshold": hours,
                }
            ),
            headers={"Content-Type": "application/json"},
        )

    except Exception as e:
        print(f"❌ Manual cleanup error: {e}")
        return https_fn.Response(
            json.dumps({"error": str(e)}),
            status=500,
            headers={"Content-Type": "application/json"},
        )


@scheduler_fn.on_schedule(
    schedule="every 24 hours", region=options.SupportedRegion.US_CENTRAL1
)
def cleanup_anonymous_users(event: scheduler_fn.ScheduledEvent) -> dict:
    """
    Scheduled function to clean up old anonymous users
    Runs every 24 hours and removes anonymous users who haven't signed in for 30 days
    """
    cutoff_time = datetime.now() - timedelta(days=30)
    cutoff_timestamp = int(cutoff_time.timestamp() * 1000)

    print(
        f"🧹 Starting cleanup of anonymous users older than {cutoff_time.isoformat()}"
    )

    try:
        deleted_count = 0
        page = auth.list_users()

        while page:
            for user in page.users:
                # Check if user is anonymous
                is_anonymous = any(
                    provider.provider_id == "anonymous"
                    for provider in user.provider_data
                )

                # For anonymous users, provider_data is empty
                if not user.provider_data or is_anonymous:
                    # Check last sign-in time
                    last_signin_timestamp = user.user_metadata.last_sign_in_timestamp

                    if (
                        last_signin_timestamp
                        and last_signin_timestamp < cutoff_timestamp
                    ):
                        try:
                            auth.delete_user(user.uid)
                            deleted_count += 1
                            print(f"🗑️  Deleted anonymous user: {user.uid}")
                        except Exception as delete_error:
                            print(
                                f"⚠️  Failed to delete user {user.uid}: {delete_error}"
                            )

            # Get next page
            page = page.get_next_page()

        print(f"✅ User cleanup complete: {deleted_count} anonymous user(s) deleted")
        return {"success": True, "usersDeleted": deleted_count}

    except Exception as e:
        print(f"❌ User cleanup error: {e}")
        raise


@https_fn.on_request(
    region=options.SupportedRegion.US_CENTRAL1,
    cors=options.CorsOptions(
        cors_origins="*",
        cors_methods=["GET", "POST"],
    ),
)
def manual_user_cleanup(req: https_fn.Request) -> https_fn.Response:
    """
    HTTP function for manual anonymous user cleanup trigger
    Can be called directly for testing or manual cleanup
    Query params:
    - days: Number of days of inactivity before deletion (default: 30)
    """
    days_param = req.args.get("days", "30")

    try:
        days = int(days_param)
        if days <= 0:
            return https_fn.Response(
                json.dumps({"error": "Invalid days parameter"}),
                status=400,
                headers={"Content-Type": "application/json"},
            )
    except ValueError:
        return https_fn.Response(
            json.dumps({"error": "Invalid days parameter"}),
            status=400,
            headers={"Content-Type": "application/json"},
        )

    cutoff_time = datetime.now() - timedelta(days=days)
    cutoff_timestamp = int(cutoff_time.timestamp() * 1000)

    print(
        f"🧹 Manual user cleanup: anonymous users older than {cutoff_time.isoformat()}"
    )

    try:
        deleted_count = 0
        page = auth.list_users()

        while page:
            for user in page.users:
                # Check if user is anonymous
                is_anonymous = any(
                    provider.provider_id == "anonymous"
                    for provider in user.provider_data
                )

                # For anonymous users, provider_data is empty
                if not user.provider_data or is_anonymous:
                    # Check last sign-in time
                    last_signin_timestamp = user.user_metadata.last_sign_in_timestamp

                    if (
                        last_signin_timestamp
                        and last_signin_timestamp < cutoff_timestamp
                    ):
                        try:
                            auth.delete_user(user.uid)
                            deleted_count += 1
                        except Exception as delete_error:
                            print(
                                f"⚠️  Failed to delete user {user.uid}: {delete_error}"
                            )

            # Get next page
            page = page.get_next_page()

        return https_fn.Response(
            json.dumps(
                {
                    "message": "User cleanup completed successfully",
                    "usersDeleted": deleted_count,
                    "daysThreshold": days,
                }
            ),
            headers={"Content-Type": "application/json"},
        )

    except Exception as e:
        print(f"❌ Manual user cleanup error: {e}")
        return https_fn.Response(
            json.dumps({"error": str(e)}),
            status=500,
            headers={"Content-Type": "application/json"},
        )


@scheduler_fn.on_schedule(
    schedule="every 24 hours", region=options.SupportedRegion.US_CENTRAL1
)
def cleanup_discord_sessions(event: scheduler_fn.ScheduledEvent) -> dict:
    """
    Scheduled function to clean up orphaned discord user sessions
    Runs every 24 hours and removes sessions for rooms that no longer exist
    """
    db = firestore.client()

    print("🧹 Starting cleanup of orphaned discord user sessions")

    try:
        # Get all active room codes
        rooms = db.collection("rooms").stream()
        active_room_codes = set()
        for room in rooms:
            room_data = room.to_dict()
            if "code" in room_data:
                active_room_codes.add(room_data["code"].upper())

        print(f"📋 Found {len(active_room_codes)} active rooms")

        # Get all discord sessions
        sessions = db.collection("discord_user_sessions").stream()
        deleted_count = 0

        for session in sessions:
            session_data = session.to_dict()
            current_room = session_data.get("current_room", "").upper()

            # Delete if room doesn't exist
            if current_room and current_room not in active_room_codes:
                session.reference.delete()
                deleted_count += 1
                print(
                    f"🗑️  Deleted session for user {session.id} (room {current_room} no longer exists)"
                )

        print(
            f"✅ Discord session cleanup complete: {deleted_count} orphaned session(s) deleted"
        )
        return {"success": True, "sessionsDeleted": deleted_count}

    except Exception as e:
        print(f"❌ Discord session cleanup error: {e}")
        raise
