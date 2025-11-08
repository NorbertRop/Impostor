import random
from pathlib import Path


class PolishDictionary:
    """Handles Polish dictionary loading and random word selection."""
    
    def __init__(self):
        self.words: list[str] = []
        self._load_dictionary()
    
    def _load_dictionary(self) -> None:
        """Load Polish words from the dictionary file."""
        dict_path = Path(__file__).parent / "data" / "polish_words.txt"
        
        if not dict_path.exists():
            self.words = [
                "kot", "pies", "dom", "drzewo", "stół", "krzesło", "kwiat",
                "książka", "komputer", "telefon", "samochód", "rower", "gitara",
                "pianino", "obrazek", "lampa", "okno", "drzwi", "ściana", "podłoga"
            ]
            return
        
        with open(dict_path, "r", encoding="utf-8") as f:
            self.words = [
                line.strip() 
                for line in f 
                if line.strip() and len(line.strip()) >= 3
            ]
    
    def get_random_word(self) -> str:
        """
        Get a random word from the dictionary.
        
        Returns
        -------
        str
            A random Polish word
        """
        if not self.words:
            return "słowo"
        return random.choice(self.words)


dictionary = PolishDictionary()

