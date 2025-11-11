import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ensureAnonAuth } from '../firebase';
import { subscribeRoom, subscribePlayers, subscribeMySecret } from '../api/room';
import Lobby from './Lobby';
import Reveal from './Reveal';
import './Room.css';

function Room() {
  const { roomId } = useParams();
  const navigate = useNavigate();
  const [room, setRoom] = useState(null);
  const [players, setPlayers] = useState([]);
  const [mySecret, setMySecret] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [myUid, setMyUid] = useState(null);

  useEffect(() => {
    let unsubRoom = null;
    let unsubPlayers = null;
    let unsubSecret = null;

    async function initialize() {
      try {
        const user = await ensureAnonAuth();
        setMyUid(user.uid);

        unsubRoom = subscribeRoom(roomId, (roomData) => {
          if (!roomData) {
            setError('Pokój nie istnieje');
            setLoading(false);
            return;
          }
          setRoom(roomData);
          setLoading(false);
        });

        unsubPlayers = subscribePlayers(roomId, (playersData) => {
          setPlayers(playersData);
        });

        unsubSecret = subscribeMySecret(roomId, user.uid, (secretData) => {
          setMySecret(secretData);
        });
      } catch (err) {
        console.error('Error initializing room:', err);
        setError('Błąd inicjalizacji: ' + err.message);
        setLoading(false);
      }
    }

    initialize();

    return () => {
      if (unsubRoom) unsubRoom();
      if (unsubPlayers) unsubPlayers();
      if (unsubSecret) unsubSecret();
    };
  }, [roomId]);

  const handleError = (message) => {
    setError(message);
    setTimeout(() => setError(''), 5000);
  };

  const handleLeaveRoom = () => {
    navigate('/');
  };

  if (loading) {
    return (
      <div className="room-loading">
        <h2>Ładowanie pokoju...</h2>
      </div>
    );
  }

  if (error && !room) {
    return (
      <div className="room-error">
        <h2>Błąd</h2>
        <p>{error}</p>
        <button onClick={handleLeaveRoom} className="back-button">
          Wróć do menu
        </button>
      </div>
    );
  }

  if (!room) {
    return null;
  }

  const isHost = room.hostUid === myUid;

  return (
    <div className="room-wrapper">
      {error && (
        <div className="error-banner">
          {error}
        </div>
      )}
      
      <div className="room-header">
        <button onClick={handleLeaveRoom} className="leave-button">
          ← Wyjdź
        </button>
      </div>

      {room.status === 'lobby' && (
        <Lobby
          roomId={roomId}
          room={room}
          players={players}
          isHost={isHost}
          onError={handleError}
        />
      )}

      {(room.status === 'dealt' || room.status === 'playing') && (
        <Reveal
          roomId={roomId}
          myUid={myUid}
          mySecret={mySecret}
          players={players}
          isHost={isHost}
          onError={handleError}
        />
      )}
    </div>
  );
}

export default Room;

