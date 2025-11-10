import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Setup from './components/Setup';
import Room from './components/Room';
import './App.css';

function App() {
  return (
    <Router>
    <div className="app">
        <Routes>
          <Route path="/" element={<Setup />} />
          <Route path="/r/:roomId" element={<Room />} />
        </Routes>
    </div>
    </Router>
  );
}

export default App;
