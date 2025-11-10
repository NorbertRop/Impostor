import { useState, useEffect } from 'react';
import { markSeen } from '../api/room';
import './Reveal.css';

function Reveal({ roomId, myUid, mySecret, players, onError }) {
  const [revealed, setRevealed] = useState(false);
  const [marking, setMarking] = useState(false);

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

  if (!mySecret) {
    return (
      <div className="reveal-container">
        <div className="loading-message">
          <p>Ładowanie...</p>
        </div>
      </div>
    );
  }

  if (myPlayer?.seen) {
    return (
      <div className="reveal-container">
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

