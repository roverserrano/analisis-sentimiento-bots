import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import Navbar from './components/Navbar'
import BulkAnalysis from './pages/BulkAnalysis'
import SingleAnalysis from './pages/SingleAnalysis'

function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <main className="app-main">
        <Routes>
          <Route path="/" element={<SingleAnalysis />} />
          <Route path="/bulk" element={<BulkAnalysis />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </BrowserRouter>
  )
}

export default App

