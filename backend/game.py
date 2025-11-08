import random
from typing import Optional


class Game:
    """Manages the state of a single Impostor game."""
    
    def __init__(self):
        self.player_names: list[str] = []
        self.word: str = ""
        self.impostor_index: int = -1
        self.is_active: bool = False
    
    def create_game(self, player_names: list[str], word: str) -> None:
        """
        Initialize a new game with players and a word.
        
        Parameters
        ----------
        player_names : list[str]
            List of player names
        word : str
            The word to be shown to non-impostor players
        """
        if len(player_names) < 3:
            raise ValueError("Need at least 3 players")
        
        self.player_names = player_names
        self.word = word
        self.impostor_index = random.randint(0, len(player_names) - 1)
        self.is_active = True
    
    def get_player_info(self, player_index: int) -> dict:
        """
        Get information for a specific player.
        
        Parameters
        ----------
        player_index : int
            Index of the player (0-based)
            
        Returns
        -------
        dict
            Player information including name, word/impostor status
        """
        if not self.is_active:
            raise ValueError("No active game")
        
        if player_index < 0 or player_index >= len(self.player_names):
            raise ValueError("Invalid player index")
        
        is_impostor = player_index == self.impostor_index
        
        return {
            "player_name": self.player_names[player_index],
            "is_impostor": is_impostor,
            "word": None if is_impostor else self.word,
            "player_index": player_index,
            "total_players": len(self.player_names)
        }
    
    def reset(self) -> None:
        """Reset the game state."""
        self.player_names = []
        self.word = ""
        self.impostor_index = -1
        self.is_active = False


game_instance = Game()

