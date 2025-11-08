let words = [];

export async function loadDictionary() {
  if (words.length > 0) return;
  
  try {
    const response = await fetch('/words.txt');
    const text = await response.text();
    words = text.trim().split('\n').filter(w => w.length > 0);
  } catch (error) {
    console.error('Failed to load dictionary:', error);
    words = [
      'kot', 'pies', 'dom', 'drzewo', 'stół', 'krzesło', 'kwiat',
      'książka', 'komputer', 'telefon', 'samochód', 'rower', 'gitara',
      'pianino', 'obrazek', 'lampa', 'okno', 'drzwi', 'ściana', 'podłoga'
    ];
  }
}

export function getRandomWord() {
  if (words.length === 0) {
    return 'słowo';
  }
  return words[Math.floor(Math.random() * words.length)];
}

export function createGame(playerNames) {
  const word = getRandomWord();
  const impostorIndex = Math.floor(Math.random() * playerNames.length);
  
  return {
    playerNames,
    word,
    impostorIndex
  };
}

export function getPlayerInfo(game, playerIndex) {
  const isImpostor = playerIndex === game.impostorIndex;
  
  return {
    playerName: game.playerNames[playerIndex],
    isImpostor,
    word: isImpostor ? null : game.word,
    playerIndex,
    totalPlayers: game.playerNames.length
  };
}

