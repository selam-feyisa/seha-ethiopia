import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import HomePage from './pages/HomePage';
import SymptomChecker from './pages/SymptomChecker';
import DocumentReader from './pages/DocumentReader';
import PrescriptionScanner from './pages/PrescriptionScanner';
import AskSeha from './pages/AskSeha';

function App() {
  return (
    <Router>
      {/* Navigation Bar */}
      <nav className="bg-green-700 text-white px-6 py-4 flex gap-6">
        <Link to="/" className="font-bold text-lg">SEHA 🏥</Link>
        <Link to="/symptoms">Symptom Checker</Link>
        <Link to="/documents">Document Reader</Link>
        <Link to="/prescription">Prescription Scanner</Link>
        <Link to="/ask">Ask SEHA</Link>
      </nav>

      {/* Pages */}
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/symptoms" element={<SymptomChecker />} />
        <Route path="/documents" element={<DocumentReader />} />
        <Route path="/prescription" element={<PrescriptionScanner />} />
        <Route path="/ask" element={<AskSeha />} />
      </Routes>
    </Router>
  );
}

export default App;