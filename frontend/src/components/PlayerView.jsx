import { useState } from 'react';
import { getPlayerInfo } from '../utils/game';

function PlayerView({ game, onReset }) {
  const [currentPlayerIndex, setCurrentPlayerIndex] = useState(0);
  const [playerInfo, setPlayerInfo] = useState(null);
  const [showInfo, setShowInfo] = useState(false);

  const handleShowWord = () => {
    const info = getPlayerInfo(game, currentPlayerIndex);
    setPlayerInfo(info);
    setShowInfo(true);
  };

  const handleNextPlayer = () => {
    setShowInfo(false);
    setPlayerInfo(null);
    if (currentPlayerIndex < game.playerNames.length - 1) {
      setCurrentPlayerIndex(currentPlayerIndex + 1);
    } else {
      setCurrentPlayerIndex(game.playerNames.length);
    }
  };

  if (currentPlayerIndex >= game.playerNames.length) {
    return (
      <div className="max-w-2xl mx-auto p-8 min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Wszyscy gracze zobaczyli swoje słowa!</h1>
          <p className="text-lg text-gray-600 mb-8">Teraz możecie rozpocząć grę.</p>
          <button 
            className="px-8 py-4 bg-blue-600 text-white text-xl font-semibold rounded-lg hover:bg-blue-700 transition-colors" 
            onClick={onReset}
          >
            Nowa Gra
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto p-8 min-h-screen flex items-center justify-center">
      <div className="w-full text-center">
        <h2 className="text-2xl font-semibold text-gray-600 mb-2">Tura gracza:</h2>
        <h1 className="text-5xl font-bold text-gray-900 mb-8">{game.playerNames[currentPlayerIndex]}</h1>

        {!showInfo ? (
          <div>
            <p className="text-lg text-gray-600 mb-6">
              Upewnij się, że tylko {game.playerNames[currentPlayerIndex]} widzi ekran
            </p>
            <button 
              className="px-8 py-4 bg-blue-600 text-white text-xl font-semibold rounded-lg hover:bg-blue-700 transition-colors shadow-lg" 
              onClick={handleShowWord}
            >
              Pokaż moje słowo
            </button>
          </div>
        ) : (
          <div>
            {playerInfo?.isImpostor ? (
              <div className="bg-gray-50 border-2 border-purple-400 rounded-lg p-8 mb-6">
                <h2 className="text-3xl font-bold text-purple-700 mb-4">Jesteś IMPOSTOREM!</h2>
                <p className="text-lg text-gray-600">
                  Inni gracze widzą słowo, a Ty musisz udawać, że je znasz.
                </p>
              </div>
            ) : (
              <div className="bg-gray-50 border-2 border-green-400 rounded-lg p-8 mb-6">
                <h2 className="text-2xl font-semibold text-green-600 mb-4">Twoje słowo:</h2>
                <div className="text-5xl font-bold text-green-800 py-6">{playerInfo?.word}</div>
              </div>
            )}

            <button 
              className="px-8 py-4 bg-green-600 text-white text-xl font-semibold rounded-lg hover:bg-green-700 transition-colors shadow-lg" 
              onClick={handleNextPlayer}
            >
              Następny Gracz
            </button>
          </div>
        )}

        <div className="mt-8 text-gray-500 text-lg">
          Gracz {currentPlayerIndex + 1} z {game.playerNames.length}
        </div>
      </div>
    </div>
  );
}

export default PlayerView;
