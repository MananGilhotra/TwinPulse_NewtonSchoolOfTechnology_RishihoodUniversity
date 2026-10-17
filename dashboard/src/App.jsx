import React, { useEffect, useState } from 'react'
import Board from './components/Board.jsx'
import PatientView from './components/PatientView.jsx'
import Evidence from './components/Evidence.jsx'
import About from './components/About.jsx'

const NAV = [
  { key: 'board', label: 'Tonight Board' },
  { key: 'evidence', label: 'Evidence' },
  { key: 'about', label: 'Privacy & India' },
]

export default function App() {
  const [view, setView] = useState('board')
  const [patientId, setPatientId] = useState(null)

  useEffect(() => {
    const onHash = () => {
      const h = window.location.hash.slice(1)
      if (h.startsWith('patient/')) {
        setPatientId(h.split('/')[1])
        setView('patient')
      } else if (h) setView(h)
      else setView('board')
    }
    onHash()
    window.addEventListener('hashchange', onHash)
    return () => window.removeEventListener('hashchange', onHash)
  }, [])

  const go = (v) => (window.location.hash = v)

  return (
    <div className="app">
      <header className="topbar">
        <div className="brand" onClick={() => go('board')}>
          <span className="logo">◐</span>
          <div>
            <div className="brand-name">TwinPulse</div>
            <div className="brand-tag">The twin lives the night first</div>
          </div>
        </div>
        <nav>
          {NAV.map((n) => (
            <button key={n.key} className={view === n.key ? 'active' : ''} onClick={() => go(n.key)}>
              {n.label}
            </button>
          ))}
        </nav>
        <div className="clinic">
          <div className="clinic-name">Paediatric Diabetes Clinic · District Hospital</div>
          <div className="synthetic-tag">Demo · all patients are synthetic</div>
        </div>
      </header>
      <main>
        {view === 'board' && <Board onOpen={(id) => go(`patient/${id}`)} />}
        {view === 'patient' && patientId && <PatientView key={patientId} id={patientId} onBack={() => go('board')} />}
        {view === 'evidence' && <Evidence />}
        {view === 'about' && <About />}
      </main>
    </div>
  )
}
