import { BrowserRouter, Route, Routes } from 'react-router-dom'
import ProbeList from './pages/ProbeList'
import ProbeDetail from './pages/ProbeDetail'

export default function App() {
  return (
    <BrowserRouter>
      <main className="container">
        <Routes>
          <Route path="/" element={<ProbeList />} />
          <Route path="/probes/:id" element={<ProbeDetail />} />
        </Routes>
      </main>
    </BrowserRouter>
  )
}
