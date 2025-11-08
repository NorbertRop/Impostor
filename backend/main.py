from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from game import game_instance
from dictionary import dictionary


app = FastAPI(title="Impostor Game API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CreateGameRequest(BaseModel):
    player_names: list[str]


@app.get("/")
def root():
    """Health check endpoint."""
    return {"status": "ok", "game": "impostor"}


@app.post("/api/game/create")
def create_game(request: CreateGameRequest):
    """
    Create a new game with the specified players.
    
    Parameters
    ----------
    request : CreateGameRequest
        Contains list of player names
        
    Returns
    -------
    dict
        Game creation confirmation with total players
    """
    try:
        if len(request.player_names) < 3:
            raise HTTPException(
                status_code=400, 
                detail="Need at least 3 players"
            )
        
        word = dictionary.get_random_word()
        game_instance.create_game(request.player_names, word)
        
        return {
            "status": "created",
            "total_players": len(request.player_names)
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/game/player/{player_index}")
def get_player_info(player_index: int):
    """
    Get information for a specific player.
    
    Parameters
    ----------
    player_index : int
        Index of the player (0-based)
        
    Returns
    -------
    dict
        Player information including name and word/impostor status
    """
    try:
        return game_instance.get_player_info(player_index)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/game/reset")
def reset_game():
    """
    Reset the current game.
    
    Returns
    -------
    dict
        Reset confirmation
    """
    game_instance.reset()
    return {"status": "reset"}


@app.get("/api/game/status")
def game_status():
    """
    Get current game status.
    
    Returns
    -------
    dict
        Game status information
    """
    return {
        "is_active": game_instance.is_active,
        "total_players": len(game_instance.player_names) if game_instance.is_active else 0
    }

