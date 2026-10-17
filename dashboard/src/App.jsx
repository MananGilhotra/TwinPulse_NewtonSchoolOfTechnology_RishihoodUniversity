import React, { useEffect, useState } from 'react'
import Overview from './components/Overview.jsx'
import Board from './components/Board.jsx'
import PatientView from './components/PatientView.jsx'
import SensorPriority from './components/SensorPriority.jsx'
import Evidence from './components/Evidence.jsx'
import About from './components/About.jsx'

const NAV = [
  { key: 'overview', label: 'Overview' },
  { key: 'board', label: 'Tonight Board' },
  { key: 'sensors', label: 'Sensor Priority' },
  { key: 'evidence', label: 'Evidence' },
  { key: 'about', label: 'Privacy & India' },
]

export default function App() {
  const [view, setView] = useState('overview')
  const [patientId, setPatientId] = useState(null)
  const [query, setQuery] = useState({})

  useEffect(() => {
    const onHash = () => {
      const [h, qs] = window.location.hash.slice(1).split('?')
      setQuery(Object.fromEntries(new URLSearchParams(qs || '')))
      if (h.startsWith('patient/')) {
        setPatientId(h.split('/')[1])
        setView('patient')
      } else setView(h || 'overview')
      window.scrollTo({ top: 0 })
    }
    onHash()
    window.addEventListener('hashchange', onHash)
    return () => window.removeEventListener('hashchange', onHash)
  }, [])

  const go = (v) => (window.location.hash = v)
  const active = view === 'patient' ? 'board' : view

  return (
    <div className="app">
      <header className="topbar">
        <div className="brand" onClick={() => go('overview')}>
          <svg className="logo" viewBox="0 0 32 32" aria-hidden="true">
            <circle cx="16" cy="16" r="14" fill="none" stroke="#a5b4fc" strokeWidth="2.5" />
            <path d="M16 2 A14 14 0 0 1 16 30 Z" fill="#a5b4fc" />
            <path d="M5 17h5l2-5 3 9 3-7 2 3h7" fill="none" stroke="#0f172a" strokeWidth="2" strokeLinejoin="round" />
          </svg>
          <div>
            <div className="brand-name">NightTwin</div>
            <div className="brand-tag">by Team TwinPulse · the twin lives the night first</div>
          </div>
        </div>
        <nav>
          {NAV.map((n) => (
            <button key={n.key} className={active === n.key ? 'active' : ''} onClick={() => go(n.key)}>
              {n.label}
            </button>
          ))}
        </nav>
        <div className="clinic">
          <div className="clinic-name">Paediatric Diabetes Clinic · District Hospital</div>
          <div className="synthetic-tag">Demo · all patients are synthetic</div>
        </div>
      </header>
      <main className={view === 'overview' ? 'wide' : ''}>
        {view === 'overview' && <Overview go={go} />}
        {view === 'board' && <Board onOpen={(id) => go(`patient/${id}`)} />}
        {view === 'patient' && patientId && <PatientView key={patientId} id={patientId} query={query} onBack={() => go('board')} />}
        {view === 'sensors' && <SensorPriority onOpen={(id) => go(`patient/${id}`)} />}
        {view === 'evidence' && <Evidence />}
        {view === 'about' && <About />}
      </main>
      <footer className="footer">
        NightTwin by Team TwinPulse · Newton School of Technology, Rishihood University · Happiest Health Digital Twin Challenge 2026 · Decision support for clinicians, not a medical device ·
        Models validated on open real-patient data (HUPA-UCM, T1D-UOM) · Apache-2.0
      </footer>
    </div>
  )
}
