const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export async function getRandomWord() {
  try {
    const response = await fetch(`${API_URL}/api/words/random`);
    if (!response.ok) {
      throw new Error('Failed to fetch random word');
    }
    const data = await response.json();
    return data.word;
  } catch (error) {
    console.error('Failed to get random word from API:', error);
    // Fallback to a default word if API fails
    const fallbackWords = [
      'kot', 'pies', 'dom', 'drzewo', 'stół', 'krzesło', 'kwiat',
      'książka', 'komputer', 'telefon', 'samochód', 'rower', 'gitara',
      'pianino', 'obrazek', 'lampa', 'okno', 'drzwi', 'ściana', 'podłoga'
    ];
    return fallbackWords[Math.floor(Math.random() * fallbackWords.length)];
  }
}
