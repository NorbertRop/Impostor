import { useState, useEffect } from 'react';
import { loadDictionary, createGame } from '../utils/game';
import './Setup.css';

function Setup({ onGameStart }) {
  const [numPlayers, setNumPlayers] = useState(4);
  const [playerNames, setPlayerNames] = useState(['Patrycja', 'Bebol', 'David', 'Dajmond']);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDictionary().then(() => setLoading(false));
  }, []);

  const handleNumPlayersChange = (e) => {
    const num = parseInt(e.target.value);
    if (num >= 3 && num <= 20) {
      setNumPlayers(num);
      const newNames = Array(num).fill('').map((_, i) => 
        playerNames[i] || ''
      );
      setPlayerNames(newNames);
    }
  };

  const handlePlayerNameChange = (index, value) => {
    const newNames = [...playerNames];
    newNames[index] = value;
    setPlayerNames(newNames);
  };

  const handleStartGame = () => {
    const filledNames = playerNames.filter(name => name.trim() !== '');
    
    if (filledNames.length < 3) {
      setError('Musisz podać przynajmniej 3 graczy');
      return;
    }
    
    if (filledNames.length !== playerNames.length) {
      setError('Wszystkie pola muszą być wypełnione');
      return;
    }

    const game = createGame(filledNames);
    onGameStart(game);
  };

  if (loading) {
    return (
      <div className="setup-container">
        <h1>Ładowanie słownika...</h1>
      </div>
    );
  }

  return (
    <div className="setup-container">
      <h1>Gra w Impostora</h1>
      
      <div className="setup-form">
        <div className="form-group">
          <label htmlFor="numPlayers">Liczba graczy:</label>
          <input
            type="number"
            id="numPlayers"
            min="3"
            max="20"
            value={numPlayers}
            onChange={handleNumPlayersChange}
          />
        </div>

        <div className="players-list">
          <h3>Imiona graczy:</h3>
          {playerNames.map((name, index) => (
            <div key={index} className="player-input-group">
              <label htmlFor={`player-${index}`}>Gracz {index + 1}:</label>
              <input
                type="text"
                id={`player-${index}`}
                value={name}
                onChange={(e) => handlePlayerNameChange(index, e.target.value)}
                placeholder={`Imię gracza ${index + 1}`}
              />
            </div>
          ))}
        </div>

        {error && <div className="error">{error}</div>}

        <button className="start-button" onClick={handleStartGame}>
          Rozpocznij Grę
        </button>
      </div>
    </div>
  );
}

export default Setup;
