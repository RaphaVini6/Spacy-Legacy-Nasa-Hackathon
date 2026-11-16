import { Suspense, lazy } from 'react'
import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { PreferencesProvider } from './context/Preferences'
import Layout from './components/layout/Layout'
import { Loader } from './components/ui'
import Home from './pages/Home'
import { lazyPage } from './utils/reload'

// other pages load on demand
const Exhibits = lazy(lazyPage(() => import('./pages/Exhibits')))
const ProbeDetail = lazy(lazyPage(() => import('./pages/ProbeDetail')))
const Missions = lazy(lazyPage(() => import('./pages/Missions')))
const Simulator = lazy(lazyPage(() => import('./pages/Simulator')))
const Learn = lazy(lazyPage(() => import('./pages/Learn')))
const NotFound = lazy(lazyPage(() => import('./pages/NotFound')))

const page = (Page) => (
  <Suspense fallback={<Loader />}>
    <Page />
  </Suspense>
)

export default function App() {
  return (
    <PreferencesProvider>
      <BrowserRouter basename={import.meta.env.BASE_URL.replace(/\/$/, '') || '/'}>
        <Routes>
          <Route element={<Layout />}>
            <Route path="/" element={<Home />} />
            <Route path="/exhibits" element={page(Exhibits)} />
            <Route path="/exhibits/:id" element={page(ProbeDetail)} />
            <Route path="/missions" element={page(Missions)} />
            <Route path="/simulator" element={page(Simulator)} />
            <Route path="/learn" element={page(Learn)} />
            <Route path="*" element={page(NotFound)} />
          </Route>
        </Routes>
      </BrowserRouter>
    </PreferencesProvider>
  )
}
