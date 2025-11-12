import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ensureAnonAuth } from '../firebase';
import { createRoom, joinRoom } from '../api/room';

const PLAYER_NAME_KEY = 'impostor_player_name';

function Setup() {
  const navigate = useNavigate();
  const [playerName, setPlayerName] = useState('');
  const [roomCode, setRoomCode] = useState('');
  const [mode, setMode] = useState('menu');
  const [error, setError] = useState('');
  const [processing, setProcessing] = useState(false);

  useEffect(() => {
    const savedName = localStorage.getItem(PLAYER_NAME_KEY);
    if (savedName) {
      setPlayerName(savedName);
    }
  }, []);

  const handleCreateRoom = async () => {
    if (!playerName.trim()) {
      setError('Podaj swoje imię');
      return;
    }

    setProcessing(true);
    setError('');
    
    try {
      const trimmedName = playerName.trim();
      localStorage.setItem(PLAYER_NAME_KEY, trimmedName);
      await ensureAnonAuth();
      const roomId = await createRoom(trimmedName);
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
      const trimmedName = playerName.trim();
      localStorage.setItem(PLAYER_NAME_KEY, trimmedName);
      await ensureAnonAuth();
      const normalizedCode = roomCode.trim().toUpperCase();
      await joinRoom(normalizedCode, trimmedName);
      navigate(`/r/${normalizedCode}`);
    } catch (err) {
      console.error('Error joining room:', err);
      setError('Nie udało się dołączyć: ' + err.message);
      setProcessing(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 flex items-center justify-center p-3">
      <div className="max-w-md w-full">
        <div className="text-center mb-4">
          <div className="inline-block bg-white/10 backdrop-blur-sm px-4 py-2 rounded-full mb-2">
            <span className="text-4xl">🎭</span>
          </div>
          <h1 className="text-3xl font-bold text-white mb-1 drop-shadow-lg">Gra w Impostora</h1>
          <p className="text-white/90 text-sm">Odkryj kto kłamie!</p>
        </div>
        
        <div className="bg-white/95 backdrop-blur-md rounded-2xl shadow-2xl p-4 sm:p-6 border border-white/20">
          {mode === 'menu' && (
            <div>
              <p className="text-gray-600 text-center mb-4 leading-relaxed text-sm">
                Gra towarzyska, w której jeden gracz jest <strong className="text-purple-600">impostorem</strong> i nie zna słowa. Odkryj, kto nim jest! 🕵️
              </p>
              
              <div className="mb-4">
                <label htmlFor="playerName" className="block text-sm font-semibold text-gray-700 mb-1">
                  Twoje imię
                </label>
                <input
                  type="text"
                  id="playerName"
                  value={playerName}
                  onChange={(e) => setPlayerName(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleCreateRoom()}
                  placeholder="Wpisz swoje imię"
                  maxLength={20}
                  className="w-full px-3 py-2 border-2 border-gray-200 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none transition-all"
                />
              </div>

              {error && (
                <div className="mb-3 p-3 bg-red-50 border-l-4 border-red-500 rounded-lg text-red-700 text-xs flex items-start gap-2">
                  <span className="text-sm">⚠️</span>
                  <span>{error}</span>
                </div>
              )}

              <div className="space-y-2">
                <button
                  className="w-full px-4 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 text-white font-bold rounded-lg hover:from-purple-700 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg"
                  onClick={handleCreateRoom}
                  disabled={processing}
                >
                  {processing ? '⏳ Tworzenie...' : '✨ Stwórz pokój'}
                </button>
                
                <button
                  className="w-full px-4 py-3 bg-white border-2 border-gray-300 text-gray-800 font-bold rounded-lg hover:bg-gray-50 hover:border-gray-400 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                  onClick={() => playerName.trim() ? setMode('join') : setError('Podaj swoje imię')}
                  disabled={processing}
                >
                  🚪 Dołącz do pokoju
                </button>
              </div>
            </div>
          )}

          {mode === 'join' && (
            <div>
              <p className="text-gray-600 text-center mb-3 text-sm">
                Wpisz kod pokoju, który otrzymałeś od hosta. 🎫
              </p>
              
              <div className="bg-gradient-to-r from-purple-50 to-indigo-50 border-2 border-purple-200 rounded-lg p-3 mb-4">
                <span className="text-gray-600 text-xs font-medium">Twoje imię:</span>
                <div className="text-gray-900 font-bold">{playerName}</div>
              </div>

              <div className="mb-4">
                <label htmlFor="roomCode" className="block text-sm font-semibold text-gray-700 mb-1">
                  Kod pokoju
                </label>
                <input
                  type="text"
                  id="roomCode"
                  value={roomCode}
                  onChange={(e) => setRoomCode(e.target.value.toUpperCase())}
                  onKeyDown={(e) => e.key === 'Enter' && handleJoinRoom()}
                  placeholder="ABC123"
                  maxLength={6}
                  className="w-full px-3 py-2 border-2 border-gray-200 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 outline-none transition-all uppercase text-center text-xl font-mono tracking-widest font-bold"
                />
              </div>

              {error && (
                <div className="mb-3 p-3 bg-red-50 border-l-4 border-red-500 rounded-lg text-red-700 text-xs flex items-start gap-2">
                  <span className="text-sm">⚠️</span>
                  <span>{error}</span>
                </div>
              )}

              <div className="space-y-2">
                <button
                  className="w-full px-4 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 text-white font-bold rounded-lg hover:from-purple-700 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg"
                  onClick={handleJoinRoom}
                  disabled={processing}
                >
                  {processing ? '⏳ Dołączanie...' : '🚀 Dołącz'}
                </button>
                
                <button
                  className="w-full px-4 py-2 bg-white border-2 border-gray-300 text-gray-800 font-semibold rounded-lg hover:bg-gray-50 hover:border-gray-400 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                  onClick={() => {
                    setMode('menu');
                    setRoomCode('');
                    setError('');
                  }}
                  disabled={processing}
                >
                  ← Wróć
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Setup;
