import { useState, useEffect } from 'react';
import { markSeen, restartGame } from '../api/room';
import './Reveal.css';

function Reveal({ roomId, myUid, mySecret, players, isHost, onError }) {
  const [revealed, setRevealed] = useState(false);
  const [marking, setMarking] = useState(false);
  const [showRestartConfirm, setShowRestartConfirm] = useState(false);
  const [restarting, setRestarting] = useState(false);

  const myPlayer = players.find(p => p.uid === myUid);
  const seenCount = players.filter(p => p.seen).length;
  const totalCount = players.length;

  const handleReveal = () => {
    setRevealed(true);
  };

  const handleMarkSeen = async () => {
    setMarking(true);
    try {
      await markSeen(roomId, myUid, true);
    } catch (error) {
      console.error('Error marking seen:', error);
      onError('Nie udało się zapisać');
      setMarking(false);
    }
  };

  useEffect(() => {
    if (myPlayer?.seen) {
      setRevealed(true);
    }
  }, [myPlayer?.seen]);

  const handleRestartGame = async () => {
    setRestarting(true);
    try {
      await restartGame(roomId);
      setRevealed(false);
      setShowRestartConfirm(false);
    } catch (error) {
      console.error('Error restarting game:', error);
      onError('Nie udało się zrestartować gry: ' + error.message);
      setRestarting(false);
    }
  };

  if (!mySecret) {
    return (
      <div className="reveal-container">
        <div className="loading-message">
          <div className="spinner"></div>
          <p>Ładowanie twojej roli...</p>
        </div>
      </div>
    );
  }

  if (myPlayer?.seen) {
    return (
      <div className="reveal-container">
        {showRestartConfirm && (
          <div className="modal-overlay" onClick={() => setShowRestartConfirm(false)}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
              <h2>Zrestartować grę?</h2>
              <p>Nowa runda rozpocznie się natychmiast z nowymi słowami i nowym impostorem.</p>
              <p>Wszyscy gracze pozostaną w pokoju.</p>
              <div className="modal-buttons">
                <button 
                  onClick={handleRestartGame} 
                  disabled={restarting}
                  className="confirm-button"
                >
                  {restarting ? 'Restartowanie...' : 'Tak, restartuj'}
                </button>
                <button 
                  onClick={() => setShowRestartConfirm(false)} 
                  className="cancel-button"
                  disabled={restarting}
                >
                  Anuluj
                </button>
              </div>
            </div>
          </div>
        )}
        <div className="waiting-section">
          <h1>Gotowy!</h1>
          <p className="waiting-text">
            Czekaj na innych graczy...
          </p>
          <div className="progress-info">
            <p>Graczy gotowych: {seenCount} / {totalCount}</p>
          </div>
          {mySecret.role === 'impostor' ? (
            <div className="reminder impostor-reminder">
              <p>Pamiętaj: Jesteś IMPOSTOREM!</p>
            </div>
          ) : (
            <div className="reminder civilian-reminder">
              <p>Twoje słowo: <strong>{mySecret.word}</strong></p>
            </div>
          )}
          {isHost && (
            <button 
              onClick={() => setShowRestartConfirm(true)} 
              className="restart-button"
            >
              Restartuj grę
            </button>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="reveal-container">
      {!revealed ? (
        <div className="pre-reveal">
          <h1>Twoja kolej!</h1>
          <p className="instruction">
            Upewnij się, że tylko Ty widzisz ekran
          </p>
          <button onClick={handleReveal} className="reveal-button">
            Pokaż moją rolę
          </button>
        </div>
      ) : (
        <div className="post-reveal">
          {mySecret.role === 'impostor' ? (
            <div className="impostor-message">
              <h2 className="impostor-title">Jesteś IMPOSTOREM!</h2>
              <p className="impostor-description">
                Inni gracze widzą słowo, a Ty musisz udawać, że je znasz.
                Spróbuj odkryć, co to za słowo, obserwując innych graczy!
              </p>
            </div>
          ) : (
            <div className="word-message">
              <h2>Twoje słowo:</h2>
              <div className="word">{mySecret.word}</div>
              <p className="civilian-description">
                Zapamiętaj to słowo i nie pokazuj go innym!
              </p>
            </div>
          )}
          <button
            onClick={handleMarkSeen}
            disabled={marking}
            className="confirm-button"
          >
            {marking ? 'Zapisywanie...' : 'Zapamiętałem/am'}
          </button>
        </div>
      )}
    </div>
  );
}

export default Reveal;

