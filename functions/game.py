import json
import random

from firebase_admin import auth, firestore
from firebase_functions import https_fn, options
from utils import get_random_word


def _start_new_game(room_id: str, is_restart: bool = False) -> None:
    """
    Internal helper to start or restart a game.
    """
    print(f"🎮 Game {'restarting' if is_restart else 'starting'} for room: {room_id}")

    try:
        db = firestore.client()
        room_ref = db.collection("rooms").document(room_id)
        room_doc = room_ref.get()

        if not room_doc.exists:
            raise ValueError(f"Room {room_id} not found")

        # Get all players
        players_ref = room_ref.collection("players")
        players_docs = list(players_ref.stream())
        player_ids = [doc.id for doc in players_docs]

        if len(player_ids) < 2:
            print("❌ Not enough players to start game")
            raise ValueError("Not enough players to start game")

        # Select random word and impostor
        word_data = get_random_word()
        word = word_data["word"]
        hints = word_data.get("hints", [])

        impostor_id = random.choice(player_ids)

        # Generate random speaking order
        speaking_order = player_ids.copy()
        random.shuffle(speaking_order)

        print(f"📝 Selected word: {word}")
        print(f"🎭 Selected impostor: {impostor_id}")
        print(f"🎤 Speaking order: {speaking_order}")
        if hints:
            print(f"💡 Impostor hints: {hints}")

        # Delete old secrets if this is a restart
        secrets_ref = room_ref.collection("secrets")
        old_secrets = list(secrets_ref.stream())

        if old_secrets:
            print(f"🗑️  Deleting {len(old_secrets)} old secrets")
            for secret_doc in old_secrets:
                secret_doc.reference.delete()

        # Create secrets for each player
        batch = db.batch()

        for player_id in player_ids:
            is_impostor = player_id == impostor_id

            if is_impostor:
                secret_data = {
                    "role": "impostor",
                    "revealedHints": [],  # Populated as hints are requested
                    "createdAt": firestore.SERVER_TIMESTAMP,
                }

                # Store hints in server-only collection (not readable by clients)
                if hints:
                    hint_data_ref = room_ref.collection("hint_data").document(player_id)
                    batch.set(
                        hint_data_ref,
                        {"hints": hints, "createdAt": firestore.SERVER_TIMESTAMP},
                    )
            else:
                secret_data = {
                    "role": "player",
                    "word": word,
                    "createdAt": firestore.SERVER_TIMESTAMP,
                }

            batch.set(secrets_ref.document(player_id), secret_data)

        # Update room with game info
        room_update = {
            "word": word,
            "impostorId": impostor_id,
            "speakingOrder": speaking_order,
            "status": "started",
            "startedAt": firestore.SERVER_TIMESTAMP,
            "impostorHintsUsed": 0,
            "totalHints": len(hints),
        }

        batch.update(room_ref, room_update)

        batch.commit()

        print(f"✅ Game started successfully for room {room_id}")

    except Exception as e:
        print(f"❌ Error starting game for room {room_id}: {e}")
        raise


def _handle_game_control(req: https_fn.Request, action: str) -> https_fn.Response:
    # Verify auth
    if not req.headers.get("Authorization"):
        return https_fn.Response(json.dumps({"error": "Unauthorized"}), status=401)

    try:
        id_token = req.headers.get("Authorization").split("Bearer ")[1]
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token["uid"]
    except Exception:
        return https_fn.Response(
            json.dumps({"error": "Invalid authentication"}), status=401
        )

    try:
        data = req.get_json()
        room_id = data.get("roomId")

        if not room_id:
            return https_fn.Response(
                json.dumps({"error": "Missing roomId"}), status=400
            )

        db = firestore.client()
        room_ref = db.collection("rooms").document(room_id)
        room_doc = room_ref.get()

        if not room_doc.exists:
            return https_fn.Response(
                json.dumps({"error": "Room not found"}), status=404
            )

        room_data = room_doc.to_dict()

        if room_data.get("hostId") != uid:
            return https_fn.Response(
                json.dumps({"error": "Only host can start/restart game"}), status=403
            )

        is_restart = action == "restart"
        _start_new_game(room_id, is_restart)

        return https_fn.Response(
            json.dumps({"success": True}), headers={"Content-Type": "application/json"}
        )

    except Exception as e:
        print(f"❌ Error {action}ing game: {e}")
        return https_fn.Response(json.dumps({"error": str(e)}), status=500)


@https_fn.on_request(
    region=options.SupportedRegion.US_CENTRAL1,
    cors=options.CorsOptions(
        cors_origins="*",
        cors_methods=["POST"],
    ),
)
def start_game(req: https_fn.Request) -> https_fn.Response:
    """
    Starts the game. Only host can call.
    """
    return _handle_game_control(req, "start")


@https_fn.on_request(
    region=options.SupportedRegion.US_CENTRAL1,
    cors=options.CorsOptions(
        cors_origins="*",
        cors_methods=["POST"],
    ),
)
def restart_game(req: https_fn.Request) -> https_fn.Response:
    """
    Restarts the game. Only host can call.
    """
    return _handle_game_control(req, "restart")


@https_fn.on_request(
    region=options.SupportedRegion.US_CENTRAL1,
    cors=options.CorsOptions(
        cors_origins="*",
        cors_methods=["GET", "POST"],
    ),
)
def get_next_hint(req: https_fn.Request) -> https_fn.Response:
    """
    HTTP function to get the next hint for an impostor.
    Validates the user is the impostor and atomically increments hintsUsed.

    Query params:
    - roomId: Room ID

    Returns:
    - JSON with next hint or error
    """
    # Verify authentication
    if not req.headers.get("Authorization"):
        return https_fn.Response(
            json.dumps({"error": "Unauthorized"}),
            status=401,
            headers={"Content-Type": "application/json"},
        )

    # Extract Firebase ID token
    try:
        id_token = req.headers.get("Authorization").split("Bearer ")[1]
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token["uid"]
    except Exception as e:
        print(f"❌ Auth error: {e}")
        return https_fn.Response(
            json.dumps({"error": "Invalid authentication"}),
            status=401,
            headers={"Content-Type": "application/json"},
        )

    # Get room ID from request body
    try:
        data = req.get_json()
        room_id = data.get("roomId")
    except Exception:
        room_id = None

    if not room_id:
        return https_fn.Response(
            json.dumps({"error": "Missing roomId parameter"}),
            status=400,
            headers={"Content-Type": "application/json"},
        )

    try:
        db = firestore.client()
        room_ref = db.collection("rooms").document(room_id)

        # Get user's secret
        secret_ref = room_ref.collection("secrets").document(uid)
        secret_doc = secret_ref.get()

        if not secret_doc.exists:
            return https_fn.Response(
                json.dumps({"error": "Secret not found"}),
                status=404,
                headers={"Content-Type": "application/json"},
            )

        secret_data = secret_doc.to_dict()

        # Verify user is impostor
        if secret_data.get("role") != "impostor":
            return https_fn.Response(
                json.dumps({"error": "Not an impostor"}),
                status=403,
                headers={"Content-Type": "application/json"},
            )

        # Get hint data from server-only collection
        hint_data_ref = room_ref.collection("hint_data").document(uid)
        hint_data_doc = hint_data_ref.get()

        if not hint_data_doc.exists:
            return https_fn.Response(
                json.dumps({"error": "No hints available"}),
                status=404,
                headers={"Content-Type": "application/json"},
            )

        hint_data = hint_data_doc.to_dict()
        hints = hint_data.get("hints", [])

        if not hints:
            return https_fn.Response(
                json.dumps({"error": "No hints configured"}),
                status=404,
                headers={"Content-Type": "application/json"},
            )

        # Get current hints used count
        room_data = room_ref.get().to_dict()
        hints_used = room_data.get("impostorHintsUsed")

        # Check if all hints already revealed
        if hints_used >= len(hints):
            return https_fn.Response(
                json.dumps({"error": "All hints already revealed"}),
                status=400,
                headers={"Content-Type": "application/json"},
            )

        # Get next hint (0-indexed)
        next_hint = hints[hints_used]

        # Build array of revealed hints (including the new one)
        revealed_hints = hints[: hints_used + 1]

        # Atomically increment hintsUsed and save revealed hints
        new_hints_used = hints_used + 1

        batch = db.batch()
        batch.update(
            secret_ref,
            {
                "hintsUsed": new_hints_used,
                "revealedHints": revealed_hints,
            },
        )
        batch.update(room_ref, {"impostorHintsUsed": new_hints_used})

        batch.commit()

        print(
            f"💡 Served hint {new_hints_used}/{len(hints)} to {uid} in room {room_id}"
        )

        return https_fn.Response(
            json.dumps(
                {
                    "hint": next_hint,
                    "hintsUsed": new_hints_used,
                    "totalHints": len(hints),
                }
            ),
            headers={"Content-Type": "application/json"},
        )

    except Exception as e:
        print(f"❌ Error getting next hint: {e}")
        return https_fn.Response(
            json.dumps({"error": str(e)}),
            status=500,
            headers={"Content-Type": "application/json"},
        )
