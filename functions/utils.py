import json
import random

# Load enhanced word list (fail loud if not available)
try:
    with open("words.json", "r", encoding="utf-8") as f:
        ENHANCED_WORDS = json.load(f)
        if not ENHANCED_WORDS:
            raise ValueError("words.json contains no words")
        print(f"✅ Loaded {len(ENHANCED_WORDS)} enhanced words")
except FileNotFoundError:
    print("⚠️ words.json not found, using fallback list")
    ENHANCED_WORDS = [{"word": "Fallback", "hints": ["No hints"]}]


def get_random_word() -> dict:
    """
    Select a random word from the enhanced word list.
    Returns enhanced word data dict with word, hints.
    """
    return random.choice(ENHANCED_WORDS)


def delete_discord_sessions_for_room(db, room_code: str) -> int:
    """
    Delete all discord user sessions associated with a specific room

    Parameters
    ----------
    db : firestore.Client
        Firestore database client
    room_code : str
        Room code to delete sessions for

    Returns
    -------
    int
        Number of sessions deleted
    """
    deleted_count = 0
    sessions_ref = db.collection("discord_user_sessions")

    try:
        sessions = sessions_ref.stream()
        for session in sessions:
            session_data = session.to_dict()
            current_room = session_data.get("current_room", "")

            if current_room.upper() == room_code.upper():
                session.reference.delete()
                deleted_count += 1
                print(
                    f"🗑️  Deleted discord session for user {session.id} (room {room_code})"
                )
    except Exception as e:
        print(f"⚠️  Error deleting discord sessions for room {room_code}: {e}")

    return deleted_count
