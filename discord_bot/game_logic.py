import random
import string
from datetime import datetime

from firestore_client import get_db
from google.cloud.firestore_v1 import SERVER_TIMESTAMP
from loguru import logger


def generate_room_id():
    chars = string.ascii_uppercase + string.digits
    chars = chars.replace("0", "").replace("O", "").replace("1", "").replace("I")
    return "".join(random.choice(chars) for _ in range(6))


def load_word_list():
    import os

    # Try multiple paths
    possible_paths = [
        "words.txt",  # Same directory
        "/app/words.txt",  # Docker/Render deployment
        os.path.join(os.path.dirname(__file__), "words.txt"),  # Relative to this file
    ]

    for path in possible_paths:
        try:
            with open(path, "r", encoding="utf-8") as f:
                words = [line.strip() for line in f if line.strip()]
                if words:
                    logger.success(f"Loaded {len(words)} words from {path}")
                    return words
        except FileNotFoundError:
            continue

    # Fallback words if file not found
    logger.warning("Using fallback word list")
    return [
        "kot",
        "pies",
        "dom",
        "drzewo",
        "stół",
        "krzesło",
        "kwiat",
        "książka",
        "komputer",
        "telefon",
        "samochód",
        "rower",
        "gitara",
        "pianino",
        "obrazek",
        "lampa",
        "okno",
        "drzwi",
        "ściana",
        "podłoga",
    ]


WORDS = load_word_list()


def get_random_word():
    return random.choice(WORDS)


async def create_room(
    user_id: str, username: str, source: str = "discord", channel_id: str | None = None
):
    db = get_db()
    room_id = generate_room_id()

    # Check if room already exists
    room_ref = db.collection("rooms").document(room_id)
    room_doc = room_ref.get()

    # Regenerate if exists (unlikely but possible)
    while room_doc.exists:
        room_id = generate_room_id()
        room_ref = db.collection("rooms").document(room_id)
        room_doc = room_ref.get()

    # Create room document
    room_data = {
        "hostUid": user_id,
        "hostSource": source,
        "status": "lobby",
        "createdAt": SERVER_TIMESTAMP,
        "allowJoin": True,
    }

    if channel_id:
        room_data["discordChannelId"] = channel_id

    room_ref.set(room_data)

    # Create host player document
    player_ref = room_ref.collection("players").document(user_id)
    player_data = {
        "name": username,
        "isHost": True,
        "joinedAt": SERVER_TIMESTAMP,
        "seen": False,
        "present": True,
        "source": source,
    }

    if source == "discord":
        player_data["discordId"] = user_id

    player_ref.set(player_data)

    return room_id


async def join_room(room_id: str, user_id: str, username: str, source: str = "discord"):
    db = get_db()
    room_ref = db.collection("rooms").document(room_id)
    room_doc = room_ref.get()

    if not room_doc.exists:
        raise ValueError(f"Room {room_id} does not exist")

    room_data = room_doc.to_dict()

    if not room_data.get("allowJoin", True):
        raise ValueError("Room is not accepting new players")

    if room_data.get("status") != "lobby":
        raise ValueError("Game has already started")

    # Add player
    player_ref = room_ref.collection("players").document(user_id)
    player_data = {
        "name": username,
        "isHost": False,
        "joinedAt": SERVER_TIMESTAMP,
        "seen": False,
        "present": True,
        "source": source,
    }

    if source == "discord":
        player_data["discordId"] = user_id

    player_ref.set(player_data)

    return room_id


async def get_room_status(room_id: str):
    db = get_db()
    room_ref = db.collection("rooms").document(room_id)
    room_doc = room_ref.get()

    if not room_doc.exists:
        return None

    room_data = room_doc.to_dict()

    # Get players
    players_ref = room_ref.collection("players")
    players_docs = players_ref.stream()

    players = []
    for doc in players_docs:
        player_data = doc.to_dict()
        player_data["uid"] = doc.id
        players.append(player_data)

    return {
        "room_id": room_id,
        "status": room_data.get("status"),
        "hostUid": room_data.get("hostUid"),
        "hostSource": room_data.get("hostSource"),
        "allowJoin": room_data.get("allowJoin"),
        "players": players,
    }


async def start_game(room_id: str, host_uid: str):
    db = get_db()
    room_ref = db.collection("rooms").document(room_id)
    room_doc = room_ref.get()

    if not room_doc.exists:
        raise ValueError(f"Room {room_id} does not exist")

    room_data = room_doc.to_dict()

    # Verify host
    if room_data.get("hostUid") != host_uid:
        raise ValueError("Only the host can start the game")

    # Get players
    players_ref = room_ref.collection("players")
    players_docs = list(players_ref.stream())

    if len(players_docs) < 2:
        raise ValueError("Need at least 3 players to start")

    # Pick word and impostor
    word = get_random_word()
    impostor_index = random.randint(0, len(players_docs) - 1)

    # Write secrets
    for i, player_doc in enumerate(players_docs):
        is_impostor = i == impostor_index
        secret_ref = room_ref.collection("secrets").document(player_doc.id)
        secret_ref.set(
            {
                "role": "impostor" if is_impostor else "civilian",
                "word": None if is_impostor else word,
            }
        )

    # Update room status
    room_ref.update({"status": "dealt"})

    # Return player secrets for DM distribution
    secrets = {}
    for i, player_doc in enumerate(players_docs):
        is_impostor = i == impostor_index
        player_data = player_doc.to_dict()
        secrets[player_doc.id] = {
            "name": player_data.get("name"),
            "discordId": player_data.get("discordId"),
            "role": "impostor" if is_impostor else "civilian",
            "word": None if is_impostor else word,
        }

    return secrets


async def get_player_secret(room_id: str, user_id: str):
    db = get_db()
    secret_ref = (
        db.collection("rooms").document(room_id).collection("secrets").document(user_id)
    )
    secret_doc = secret_ref.get()

    if not secret_doc.exists:
        return None

    return secret_doc.to_dict()


async def mark_player_seen(room_id: str, user_id: str):
    db = get_db()
    player_ref = (
        db.collection("rooms").document(room_id).collection("players").document(user_id)
    )
    player_doc = player_ref.get()

    if player_doc.exists:
        player_ref.update({"seen": True})
        logger.info(f"Marked player {user_id} as seen in room {room_id}")


async def restart_game(room_id: str, host_uid: str):
    db = get_db()
    room_ref = db.collection("rooms").document(room_id)
    room_doc = room_ref.get()

    if not room_doc.exists:
        raise ValueError(f"Room {room_id} does not exist")

    room_data = room_doc.to_dict()

    if room_data.get("hostUid") != host_uid:
        raise ValueError("Only the host can restart the game")

    players_ref = room_ref.collection("players")
    players_docs = list(players_ref.stream())

    if len(players_docs) < 2:
        raise ValueError("Need at least 3 players to restart")

    secrets_ref = room_ref.collection("secrets")
    secrets_docs = list(secrets_ref.stream())

    for player_doc in players_docs:
        player_ref = room_ref.collection("players").document(player_doc.id)
        player_ref.update({"seen": False})

    for secret_doc in secrets_docs:
        secret_doc.reference.delete()

    room_ref.update({"status": "started"})

    logger.info(f"Game restarted for room {room_id} by host {host_uid}")
