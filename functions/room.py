import json
import random
import string

from firebase_admin import auth, firestore
from firebase_functions import https_fn, options


@https_fn.on_request(
    region=options.SupportedRegion.US_CENTRAL1,
    cors=options.CorsOptions(
        cors_origins="*",
        cors_methods=["POST"],
    ),
)
def create_room(req: https_fn.Request) -> https_fn.Response:
    """
    Creates a new game room.
    """
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
        player_name = data.get("playerName")
        source = data.get("source")

        if not player_name:
            return https_fn.Response(
                json.dumps({"error": "Missing playerName"}), status=400
            )

        db = firestore.client()

        # Generate a 6-character room code and use it as the document ID
        room_code = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))

        # Create room doc with the code as the ID
        room_ref = db.collection("rooms").document(room_code)

        room_data = {
            "code": room_code,
            "hostId": uid,
            "status": "lobby",
            "createdAt": firestore.SERVER_TIMESTAMP,
            "impostorHintsUsed": 0,
        }

        batch = db.batch()
        batch.set(room_ref, room_data)

        # Add host as player
        player_ref = room_ref.collection("players").document(uid)
        player_data = {
            "name": player_name,
            "joinedAt": firestore.SERVER_TIMESTAMP,
            "isHost": True,
            "source": source,
        }
        batch.set(player_ref, player_data)

        batch.commit()

        return https_fn.Response(
            json.dumps({"roomId": room_code}),
            headers={"Content-Type": "application/json"},
        )

    except Exception as e:
        print(f"❌ Error creating room: {e}")
        return https_fn.Response(json.dumps({"error": str(e)}), status=500)


@https_fn.on_request(
    region=options.SupportedRegion.US_CENTRAL1,
    cors=options.CorsOptions(
        cors_origins="*",
        cors_methods=["POST"],
    ),
)
def join_room(req: https_fn.Request) -> https_fn.Response:
    """
    Joins an existing room.
    """
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
        player_name = data.get("playerName")
        source = data.get("source")

        if not room_id or not player_name:
            return https_fn.Response(
                json.dumps({"error": "Missing roomId or playerName"}), status=400
            )

        db = firestore.client()
        room_ref = db.collection("rooms").document(room_id)
        room_doc = room_ref.get()

        if not room_doc.exists:
            return https_fn.Response(
                json.dumps({"error": "Room not found"}), status=404
            )

        room_data = room_doc.to_dict()

        player_ref = room_ref.collection("players").document(uid)
        player_data = {
            "name": player_name,
            "joinedAt": firestore.SERVER_TIMESTAMP,
            "isHost": False,
            "source": source,
        }

        # Check if re-joining host
        if room_data.get("hostId") == uid:
            player_data["isHost"] = True

        player_ref.set(player_data, merge=True)

        # Handle late joiner logic if game is in progress
        status = room_data.get("status")
        if status in ["started"]:
            word = room_data.get("word")
            if word:
                secret_data = {
                    "role": "player",
                    "word": word,
                    "createdAt": firestore.SERVER_TIMESTAMP,
                }
                room_ref.collection("secrets").document(uid).set(secret_data)

                # Update speaking order
                speaking_order = room_data.get("speakingOrder", [])
                if uid not in speaking_order:
                    speaking_order.append(uid)
                    room_ref.update({"speakingOrder": speaking_order})

        return https_fn.Response(
            json.dumps({"success": True, "roomId": room_id}),
            headers={"Content-Type": "application/json"},
        )

    except Exception as e:
        print(f"❌ Error joining room: {e}")
        return https_fn.Response(json.dumps({"error": str(e)}), status=500)
