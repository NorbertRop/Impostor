import { useState } from 'react';
import { startGame, toggleAllowJoin } from '../api/room';

function Lobby({ roomId, room, players, isHost, onError }) {
  const [starting, setStarting] = useState(false);
  const [toggling, setToggling] = useState(false);

  const handleStartGame = async () => {
    if (players.length < 2) {
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
    <div className="max-w-2xl mx-auto p-3 sm:p-4">
      <div className="text-center mb-4">
        <div className="inline-block mb-2">
          <span className="text-4xl">⏳</span>
        </div>
        <h1 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-pink-600 mb-1">Poczekalnia</h1>
        <p className="text-gray-600 text-sm">Czekamy na pozostałych graczy...</p>
      </div>
      
      <div className="bg-gradient-to-br from-purple-50 to-indigo-50 rounded-xl shadow-xl p-4 mb-4 border-2 border-purple-200">
        <div className="text-center">
          <h2 className="text-xs font-semibold text-purple-700 mb-2 uppercase tracking-wide">Kod pokoju</h2>
          <div className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-indigo-600 mb-3 tracking-widest font-mono">{roomId}</div>
          <div className="flex gap-2 justify-center flex-wrap">
            <button 
              onClick={handleCopyRoomCode} 
              className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-all font-semibold shadow-lg text-sm"
            >
              📋 Kopiuj kod
            </button>
            <button 
              onClick={handleCopyLink} 
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-all font-semibold shadow-lg text-sm"
            >
              🔗 Kopiuj link
            </button>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-xl p-4 mb-4 border-2 border-gray-100">
        <h3 className="text-xl font-bold text-gray-900 mb-3 flex items-center gap-2">
          <span>👥</span>
          Gracze <span className="text-purple-600">({players.length})</span>
        </h3>
        <div className="space-y-2">
          {players.map((player, index) => (
            <div 
              key={player.uid} 
              className="flex items-center justify-between px-3 py-2 bg-gradient-to-r from-gray-50 to-gray-100 rounded-lg border-2 border-gray-200 hover:border-purple-300 transition-all"
            >
              <div className="flex items-center gap-2">
                <span className="text-lg font-bold text-purple-600 w-6">#{index + 1}</span>
                <span className="text-gray-900 font-semibold">{player.name}</span>
              </div>
              {player.isHost && (
                <span className="px-2 py-1 bg-gradient-to-r from-yellow-400 to-orange-400 text-white rounded-md font-bold text-xs shadow-md">
                  👑 Host
                </span>
              )}
            </div>
          ))}
        </div>
      </div>

      {isHost && (
        <div className="space-y-2">
          <button
            onClick={handleStartGame}
            disabled={players.length < 2 || starting}
            className="w-full px-4 py-3 bg-gradient-to-r from-green-500 to-emerald-600 text-white font-bold rounded-lg hover:from-green-600 hover:to-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-xl"
          >
            {starting ? '⏳ Rozpoczynanie...' : '🎮 Rozpocznij grę'}
          </button>
          
          <button
            onClick={handleToggleJoin}
            disabled={toggling}
            className="w-full px-4 py-2 bg-white border-2 border-gray-300 text-gray-800 font-semibold rounded-lg hover:bg-gray-50 hover:border-gray-400 disabled:opacity-50 transition-all text-sm"
          >
            {room.allowJoin ? '🔒 Zablokuj dołączanie' : '🔓 Odblokuj dołączanie'}
          </button>
          
          {players.length < 2 && (
            <div className="mt-3 p-3 bg-amber-50 border-l-4 border-amber-500 rounded-lg">
              <p className="text-amber-800 font-semibold flex items-center gap-2 text-sm">
                <span>⚠️</span>
                Potrzebujesz przynajmniej 3 graczy
              </p>
            </div>
          )}
        </div>
      )}

      {!isHost && (
        <div className="text-center py-6 bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl border-2 border-blue-200">
          <div className="mb-3">
            <span className="text-3xl">⏰</span>
          </div>
          <p className="text-base text-gray-700 font-medium">Czekaj na rozpoczęcie gry przez hosta...</p>
        </div>
      )}
    </div>
  );
}

export default Lobby;

