import { useState, useEffect } from 'react';
import { restartGame, getNextHint } from '../api/room';

function Reveal({ roomId, myUid, mySecret, players, isHost, onError, room }) {
  const [showRestartConfirm, setShowRestartConfirm] = useState(false);
  const [restarting, setRestarting] = useState(false);
  const [revealedHints, setRevealedHints] = useState([]);
  const [loadingHint, setLoadingHint] = useState(false);

  // Restore revealed hints from database when secret loads
  useEffect(() => {
    if (mySecret?.revealedHints && Array.isArray(mySecret.revealedHints)) {
      setRevealedHints(mySecret.revealedHints);
    }
  }, [mySecret?.revealedHints]);

  const handleRestartGame = async () => {
    setRestarting(true);
    try {
      await restartGame(roomId);
      setShowRestartConfirm(false);
    } catch (error) {
      console.error('Error restarting game:', error);
      onError('Nie udało się zrestartować gry: ' + error.message);
      setRestarting(false);
    }
  };

  if (!mySecret) {
    return (
      <div className="max-w-2xl mx-auto p-4 min-h-[300px] flex items-center justify-center">
        <div className="flex flex-col items-center text-center">
          <div className="w-12 h-12 border-4 border-gray-200 border-t-blue-500 rounded-full animate-spin mb-4"></div>
          <p className="text-base text-gray-700">Ładowanie twojej roli...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto p-3 sm:p-4">
      {showRestartConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-60 backdrop-blur-sm flex items-center justify-center p-4 z-50" onClick={() => setShowRestartConfirm(false)}>
          <div className="bg-white rounded-xl p-6 max-w-md w-full shadow-2xl border-2 border-gray-200" onClick={(e) => e.stopPropagation()}>
            <div className="text-center mb-3">
              <span className="text-4xl">🔄</span>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-3 text-center">Zrestartować grę?</h2>
            <p className="text-gray-600 mb-2 text-center text-sm">Nowa runda rozpocznie się natychmiast z nowymi słowami i nowym impostorem.</p>
            <p className="text-gray-600 mb-4 text-center font-medium text-sm">✅ Wszyscy gracze pozostaną w pokoju.</p>
            <div className="flex gap-2">
              <button 
                onClick={handleRestartGame} 
                disabled={restarting}
                className="flex-1 px-4 py-3 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-lg font-bold hover:from-green-600 hover:to-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all text-sm"
              >
                {restarting ? '⏳ Restartowanie...' : '✅ Tak, restartuj'}
              </button>
              <button 
                onClick={() => setShowRestartConfirm(false)} 
                className="flex-1 px-4 py-3 bg-gray-200 text-gray-800 rounded-lg font-bold hover:bg-gray-300 disabled:opacity-50 transition-all text-sm"
                disabled={restarting}
              >
                ❌ Anuluj
              </button>
            </div>
          </div>
        </div>
      )}
      <div className="w-full">
          {mySecret.role === 'impostor' ? (
            <div className="bg-gradient-to-br from-purple-100 to-pink-100 border-3 border-purple-500 rounded-xl p-4 mb-4 shadow-xl">
              <div className="text-center mb-3">
                <span className="text-4xl">🎭</span>
              </div>
              <h2 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-700 to-pink-700 mb-3 text-center">
                Jesteś IMPOSTOREM!
              </h2>
              <p className="text-sm text-gray-700 leading-relaxed text-center mb-3">
                Inni gracze widzą słowo, a Ty musisz udawać, że je znasz.
                Spróbuj odkryć, co to za słowo, obserwując innych graczy! 🕵️
              </p>
                {(room?.totalHints) ? (
                <div className="mt-3 bg-white/80 backdrop-blur-sm border-2 border-purple-300 rounded-lg p-3">
                  <h3 className="text-sm font-bold text-purple-700 mb-2 flex items-center gap-2">
                    💡 Podpowiedzi:
                  </h3>
                  
                  {revealedHints.length > 0 && (
                    <ul className="space-y-1 mb-3">
                      {revealedHints.map((hint, index) => (
                        <li key={index} className="text-xs text-gray-700 flex items-start gap-2 animate-fadeIn">
                          <span className="text-purple-500 font-bold">•</span>
                          <span>{hint}</span>
                        </li>
                      ))}
                    </ul>
                  )}
                  
                  
                  {room.totalHints && revealedHints.length < room.totalHints && (
                    <button
                      onClick={async () => {
                        setLoadingHint(true);
                        try {
                          await getNextHint(roomId);
                        } catch (err) {
                          console.error('Error getting hint:', err);
                          onError('Nie udało się pobrać podpowiedzi: ' + err.message);
                        } finally {
                          setLoadingHint(false);
                        }
                      }}
                      disabled={loadingHint}
                      className="w-full py-2 bg-purple-100 hover:bg-purple-200 text-purple-700 text-xs font-bold rounded transition-colors border border-purple-200 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {loadingHint ? '⏳ Ładowanie...' : `➕ Pokaż kolejną podpowiedź (${room.totalHints - revealedHints.length})`} 
                    </button>
                  )}
                </div>
              ) : null}
            </div>
          ) : (
            <div className="bg-gradient-to-br from-green-100 to-emerald-100 border-3 border-green-500 rounded-xl p-4 mb-4 text-center shadow-xl">
              <div className="mb-3">
                <span className="text-4xl">✅</span>
              </div>
              <h2 className="text-lg font-bold text-green-700 mb-3">Twoje słowo:</h2>
              <div className="text-3xl font-bold my-4 py-4 px-4 bg-white border-3 border-green-400 rounded-lg text-transparent bg-clip-text bg-gradient-to-r from-green-700 to-emerald-700 shadow-lg">
                {mySecret.word}
              </div>
              <p className="text-sm text-gray-700 mt-3 font-medium">
                🤫 Zapamiętaj to słowo i nie pokazuj go innym!
              </p>
            </div>
          )}

          {mySecret.role !== 'impostor' && (
            <div className="bg-purple-50 border border-purple-200 rounded-xl p-3 mb-3 flex items-center justify-center gap-2 animate-fadeIn">
              <span className="text-xl">💡</span>
              <span className="text-purple-900 font-medium">
                Impostor użył podpowiedzi: <span className="font-bold text-lg">{room?.impostorHintsUsed ?? 0}</span>
              </span>
            </div>
          )}

          {room?.speakingOrder && (
            <div className="bg-white border-2 border-indigo-200 rounded-xl p-4 mb-3 shadow-xl">
              <h3 className="text-lg font-bold text-gray-900 mb-3 flex items-center gap-2">
                🎤 Kolejność wypowiedzi
              </h3>
              <ol className="space-y-2">
                {room.speakingOrder.map((playerId, index) => {
                  const player = players.find(p => p.uid === playerId);
                  const isMe = playerId === myUid;
                  return (
                    <li 
                      key={playerId} 
                      className={`flex items-center px-3 py-2 rounded-lg text-sm font-semibold transition-all ${
                        isMe 
                          ? 'bg-gradient-to-r from-yellow-100 to-orange-100 border-2 border-yellow-400 shadow-lg text-gray-900' 
                          : 'bg-gradient-to-r from-gray-50 to-gray-100 border-2 border-gray-200 text-gray-700'
                      }`}
                    >
                      <span className="font-bold text-indigo-600 mr-2 w-6">{index + 1}.</span>
                      <span className="flex-1">{player?.name || 'Nieznany gracz'}</span>
                      {isMe && <span className="ml-2 px-2 py-0.5 bg-orange-500 text-white rounded text-xs font-bold">Ty</span>}
                    </li>
                  );
                })}
              </ol>
            </div>
          )}

          {isHost && (
            <div className="flex justify-center">
              <button 
                onClick={() => setShowRestartConfirm(true)} 
                className="px-6 py-3 bg-gradient-to-r from-orange-500 to-red-500 text-white rounded-lg font-bold hover:from-orange-600 hover:to-red-600 transition-all shadow-xl"
              >
                🔄 Restartuj grę
              </button>
            </div>
          )}
        </div>
    </div>
  );
}

export default Reveal;

