import { useState } from 'react';
import { getPlayerInfo } from '../utils/game';
import './PlayerView.css';

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
      <div className="player-view-container">
        <div className="game-ready">
          <h1>Wszyscy gracze zobaczyli swoje słowa!</h1>
          <p>Teraz możecie rozpocząć grę.</p>
          <div className="button-group">
            <button className="action-button" onClick={onReset}>
              Nowa Gra
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="player-view-container">
      <div className="player-turn">
        <h2>Tura gracza:</h2>
        <h1 className="player-name">{game.playerNames[currentPlayerIndex]}</h1>

        {!showInfo ? (
          <div className="instruction">
            <p>Upewnij się, że tylko {game.playerNames[currentPlayerIndex]} widzi ekran</p>
            <button className="action-button" onClick={handleShowWord}>
              Pokaż moje słowo
            </button>
          </div>
        ) : (
          <div className="word-display">
            {playerInfo?.isImpostor ? (
              <div className="impostor-message">
                <h2 className="impostor-title">Jesteś IMPOSTOREM!</h2>
                <p className="impostor-description">
                  Inni gracze widzą słowo, a Ty musisz udawać, że je znasz.
                </p>
              </div>
            ) : (
              <div className="word-message">
                <h2>Twoje słowo:</h2>
                <div className="word">{playerInfo?.word}</div>
              </div>
            )}

            <button className="action-button next-button" onClick={handleNextPlayer}>
              Następny Gracz
            </button>
          </div>
        )}

        <div className="progress">
          Gracz {currentPlayerIndex + 1} z {game.playerNames.length}
        </div>
      </div>
    </div>
  );
}

export default PlayerView;
