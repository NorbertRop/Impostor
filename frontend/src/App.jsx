import { useState } from 'react';
import Setup from './components/Setup';
import PlayerView from './components/PlayerView';
import './App.css';

function App() {
  const [game, setGame] = useState(null);

  const handleGameStart = (newGame) => {
    setGame(newGame);
  };

  const handleReset = () => {
    setGame(null);
  };

  return (
    <div className="app">
      {!game ? (
        <Setup onGameStart={handleGameStart} />
      ) : (
        <PlayerView game={game} onReset={handleReset} />
      )}
    </div>
  );
}

export default App;
