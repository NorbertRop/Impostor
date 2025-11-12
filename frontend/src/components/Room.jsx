import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ensureAnonAuth } from '../firebase';
import { subscribeRoom, subscribePlayers, subscribeMySecret } from '../api/room';
import Lobby from './Lobby';
import Reveal from './Reveal';

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
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-gray-200 border-t-blue-500 rounded-full animate-spin mb-3 mx-auto"></div>
          <h2 className="text-xl font-semibold text-gray-700">Ładowanie pokoju...</h2>
        </div>
      </div>
    );
  }

  if (error && !room) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-xl shadow-lg p-6 max-w-md w-full text-center">
          <h2 className="text-2xl font-bold text-red-600 mb-3">Błąd</h2>
          <p className="text-gray-700 mb-4 text-sm">{error}</p>
          <button 
            onClick={handleLeaveRoom} 
            className="px-5 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            Wróć do menu
          </button>
        </div>
      </div>
    );
  }

  if (!room) {
    return null;
  }

  const isHost = room.hostUid === myUid;

  return (
    <div className="min-h-screen bg-gray-50">
      {error && (
        <div className="fixed top-0 left-0 right-0 bg-red-100 border-b-2 border-red-400 px-3 py-2 text-red-700 text-center z-50 text-sm">
          {error}
        </div>
      )}
      
      <div className="container mx-auto px-3 py-2">
        <button 
          onClick={handleLeaveRoom} 
          className="mb-2 px-3 py-1.5 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium inline-flex items-center text-sm"
        >
          <span className="mr-1">←</span> Wyjdź
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

      {room.status === 'started' && (
        <div className="flex items-center justify-center min-h-[50vh]">
          <div className="text-center">
            <div className="w-16 h-16 border-4 border-gray-200 border-t-green-500 rounded-full animate-spin mb-4 mx-auto"></div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Rozpoczynanie gry...</h2>
            <p className="text-base text-gray-600">Losowanie ról i słów...</p>
          </div>
        </div>
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

