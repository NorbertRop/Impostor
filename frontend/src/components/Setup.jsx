import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ensureAnonAuth } from '../firebase';
import { createRoom, joinRoom } from '../api/room';
import { loadDictionary } from '../utils/game';
import './Setup.css';

function Setup() {
  const navigate = useNavigate();
  const [playerName, setPlayerName] = useState('');
  const [roomCode, setRoomCode] = useState('');
  const [mode, setMode] = useState('menu');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);

  useEffect(() => {
    loadDictionary().then(() => setLoading(false));
  }, []);

  const handleCreateRoom = async () => {
    if (!playerName.trim()) {
      setError('Podaj swoje imię');
      return;
    }

    setProcessing(true);
    setError('');
    
    try {
      await ensureAnonAuth();
      const roomId = await createRoom(playerName.trim());
      navigate(`/r/${roomId}`);
    } catch (err) {
      console.error('Error creating room:', err);
      setError('Nie udało się utworzyć pokoju: ' + err.message);
      setProcessing(false);
    }
  };

  const handleJoinRoom = async () => {
    if (!playerName.trim()) {
      setError('Podaj swoje imię');
      return;
    }

    if (!roomCode.trim()) {
      setError('Podaj kod pokoju');
      return;
    }

    setProcessing(true);
    setError('');
    
    try {
      await ensureAnonAuth();
      const normalizedCode = roomCode.trim().toUpperCase();
      await joinRoom(normalizedCode, playerName.trim());
      navigate(`/r/${normalizedCode}`);
    } catch (err) {
      console.error('Error joining room:', err);
      setError('Nie udało się dołączyć: ' + err.message);
      setProcessing(false);
    }
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
        {mode === 'menu' && (
          <div className="menu-mode">
            <p className="description">
              Gra towarzyska, w której jeden gracz jest impostorem i nie zna słowa.
              Odkryj, kto nim jest!
            </p>
            
            <div className="name-input-group">
              <label htmlFor="playerName">Twoje imię:</label>
              <input
                type="text"
                id="playerName"
                value={playerName}
                onChange={(e) => setPlayerName(e.target.value)}
                placeholder="Wpisz swoje imię"
                maxLength={20}
              />
            </div>

            {error && <div className="error">{error}</div>}

            <div className="button-group">
              <button
                className="primary-button"
                onClick={() => playerName.trim() ? setMode('create') : setError('Podaj swoje imię')}
                disabled={processing}
              >
                Stwórz pokój
              </button>
              
              <button
                className="secondary-button"
                onClick={() => playerName.trim() ? setMode('join') : setError('Podaj swoje imię')}
                disabled={processing}
              >
                Dołącz do pokoju
              </button>
            </div>
          </div>
        )}

        {mode === 'create' && (
          <div className="create-mode">
            <p className="mode-description">
              Utworzysz pokój i zostaniesz hostem. Inni gracze będą mogli dołączyć używając kodu pokoju.
            </p>
            
            <div className="player-info">
              <strong>Twoje imię:</strong> {playerName}
            </div>

            {error && <div className="error">{error}</div>}

            <div className="button-group">
              <button
                className="primary-button"
                onClick={handleCreateRoom}
                disabled={processing}
              >
                {processing ? 'Tworzenie...' : 'Utwórz pokój'}
              </button>
              
              <button
                className="back-button"
                onClick={() => {
                  setMode('menu');
                  setError('');
                }}
                disabled={processing}
              >
                Wróć
              </button>
            </div>
          </div>
        )}

        {mode === 'join' && (
          <div className="join-mode">
            <p className="mode-description">
              Wpisz kod pokoju, który otrzymałeś od hosta.
            </p>
            
            <div className="player-info">
              <strong>Twoje imię:</strong> {playerName}
            </div>

            <div className="code-input-group">
              <label htmlFor="roomCode">Kod pokoju:</label>
              <input
                type="text"
                id="roomCode"
                value={roomCode}
                onChange={(e) => setRoomCode(e.target.value.toUpperCase())}
                placeholder="np. ABC123"
                maxLength={6}
                style={{ textTransform: 'uppercase' }}
              />
            </div>

            {error && <div className="error">{error}</div>}

            <div className="button-group">
              <button
                className="primary-button"
                onClick={handleJoinRoom}
                disabled={processing}
              >
                {processing ? 'Dołączanie...' : 'Dołącz'}
              </button>
              
              <button
                className="back-button"
                onClick={() => {
                  setMode('menu');
                  setRoomCode('');
                  setError('');
                }}
                disabled={processing}
              >
                Wróć
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default Setup;
