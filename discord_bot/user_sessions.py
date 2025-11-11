from firestore_client import get_db
from loguru import logger


async def set_user_room(user_id: str, room_code: str):
    """
    Store the current room for a Discord user
    
    Parameters
    ----------
    user_id : str
        Discord user ID
    room_code : str
        Room code to remember
    """
    try:
        db = get_db()
        db.collection("discord_user_sessions").document(user_id).set({
            "current_room": room_code.upper()
        })
        logger.info(f"Stored room {room_code} for user {user_id}")
    except Exception as e:
        logger.error(f"Failed to store user room: {e}")


async def get_user_room(user_id: str) -> str | None:
    """
    Get the current room for a Discord user
    
    Parameters
    ----------
    user_id : str
        Discord user ID
        
    Returns
    -------
    str | None
        Room code if found, None otherwise
    """
    try:
        db = get_db()
        doc = db.collection("discord_user_sessions").document(user_id).get()
        if doc.exists:
            data = doc.to_dict()
            room_code = data.get("current_room")
            logger.info(f"Retrieved room {room_code} for user {user_id}")
            return room_code
        return None
    except Exception as e:
        logger.error(f"Failed to get user room: {e}")
        return None


async def clear_user_room(user_id: str):
    """
    Clear the current room for a Discord user
    
    Parameters
    ----------
    user_id : str
        Discord user ID
    """
    try:
        db = get_db()
        db.collection("discord_user_sessions").document(user_id).delete()
        logger.info(f"Cleared room for user {user_id}")
    except Exception as e:
        logger.error(f"Failed to clear user room: {e}")

