import game_logic
from fastapi import APIRouter, HTTPException

from api.models import CreateRoomRequest, JoinRoomRequest, StartGameRequest

router = APIRouter(prefix="/api", tags=["rooms"])


@router.post("/rooms/create")
async def create_room_endpoint(data: CreateRoomRequest):
    try:
        room_id = await game_logic.create_room(data.user_id, data.username, data.source)
        return {"room_id": room_id, "message": f"Room {room_id} created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rooms/{room_id}/join")
async def join_room_endpoint(room_id: str, data: JoinRoomRequest):
    try:
        await game_logic.join_room(room_id, data.user_id, data.username, data.source)
        return {"room_id": room_id, "message": f"Joined room {room_id} successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rooms/{room_id}")
async def get_room_endpoint(room_id: str):
    try:
        room_status = await game_logic.get_room_status(room_id)
        if room_status is None:
            raise HTTPException(status_code=404, detail="Room not found")
        return room_status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rooms/{room_id}/start")
async def start_game_endpoint(room_id: str, data: StartGameRequest):
    try:
        secrets = await game_logic.start_game(room_id, data.host_uid)
        return {
            "room_id": room_id,
            "message": "Game started successfully",
            "player_count": len(secrets),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rooms/{room_id}/secret/{user_id}")
async def get_secret_endpoint(room_id: str, user_id: str):
    try:
        secret = await game_logic.get_player_secret(room_id, user_id)
        if secret is None:
            raise HTTPException(status_code=404, detail="Secret not found")
        return secret
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/words/random")
async def get_random_word_endpoint():
    try:
        word = game_logic.get_random_word()
        return {"word": word}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
