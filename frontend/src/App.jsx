import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Setup from './components/Setup';
import Room from './components/Room';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Setup />} />
        <Route path="/r/:roomId" element={<Room />} />
      </Routes>
    </Router>
  );
}

export default App;
