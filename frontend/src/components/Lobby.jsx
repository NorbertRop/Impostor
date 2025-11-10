import { useState } from 'react';
import { startGame, toggleAllowJoin } from '../api/room';
import './Lobby.css';

function Lobby({ roomId, room, players, isHost, onError }) {
  const [starting, setStarting] = useState(false);
  const [toggling, setToggling] = useState(false);

  const handleStartGame = async () => {
    if (players.length < 3) {
      onError('Potrzebujesz przynajmniej 3 graczy');
      return;
    }
    
    setStarting(true);
    try {
      await startGame(roomId);
    } catch (error) {
      console.error('Error starting game:', error);
      onError('Nie udało się rozpocząć gry: ' + error.message);
      setStarting(false);
    }
  };

  const handleToggleJoin = async () => {
    setToggling(true);
    try {
      await toggleAllowJoin(roomId, !room.allowJoin);
    } catch (error) {
      console.error('Error toggling join:', error);
      onError('Nie udało się zmienić ustawień');
    } finally {
      setToggling(false);
    }
  };

  const handleCopyRoomCode = () => {
    navigator.clipboard.writeText(roomId);
  };

  const handleCopyLink = () => {
    const link = `${window.location.origin}/r/${roomId}`;
    navigator.clipboard.writeText(link);
  };

  return (
    <div className="lobby-container">
      <h1>Poczekalnia</h1>
      
      <div className="room-info">
        <div className="room-code-section">
          <h2>Kod pokoju:</h2>
          <div className="room-code">{roomId}</div>
          <div className="share-buttons">
            <button onClick={handleCopyRoomCode} className="copy-button">
              Kopiuj kod
            </button>
            <button onClick={handleCopyLink} className="copy-button">
              Kopiuj link
            </button>
          </div>
        </div>
      </div>

      <div className="players-section">
        <h3>Gracze ({players.length}):</h3>
        <div className="players-list">
          {players.map((player) => (
            <div key={player.uid} className="player-item">
              <span className="player-name">
                {player.name}
                {player.isHost && <span className="host-badge"> (Host)</span>}
              </span>
            </div>
          ))}
        </div>
      </div>

      {isHost && (
        <div className="host-controls">
          <button
            onClick={handleStartGame}
            disabled={players.length < 3 || starting}
            className="start-button"
          >
            {starting ? 'Rozpoczynanie...' : 'Rozpocznij grę'}
          </button>
          
          <button
            onClick={handleToggleJoin}
            disabled={toggling}
            className="toggle-button"
          >
            {room.allowJoin ? 'Zablokuj dołączanie' : 'Odblokuj dołączanie'}
          </button>
          
          {players.length < 3 && (
            <p className="warning">Potrzebujesz przynajmniej 3 graczy</p>
          )}
        </div>
      )}

      {!isHost && (
        <div className="waiting-message">
          <p>Czekaj na rozpoczęcie gry przez hosta...</p>
        </div>
      )}
    </div>
  );
}

export default Lobby;

