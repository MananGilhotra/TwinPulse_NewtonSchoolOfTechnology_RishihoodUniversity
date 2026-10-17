import React, { useEffect, useState } from 'react'
import Overview from './components/Overview.jsx'
import Board from './components/Board.jsx'
import PatientView from './components/PatientView.jsx'
import SensorPriority from './components/SensorPriority.jsx'
import Evidence from './components/Evidence.jsx'
import About from './components/About.jsx'
import Logo from './components/Logo.jsx'
import Icon from './components/Icon.jsx'

const NAV = [
  { key: 'overview', label: 'Overview', icon: 'home' },
  { key: 'board', label: 'Tonight Board', icon: 'moon' },
  { key: 'sensors', label: 'Sensor Priority', icon: 'sensor' },
  { key: 'evidence', label: 'Evidence', icon: 'chart' },
  { key: 'about', label: 'Privacy & India', icon: 'shield' },
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
        <div className="topbar-inner">
          <a className="brand" href="#overview" aria-label="NightTwin home">
            <Logo size={38} />
            <span className="wordmark">
              <span className="wm-name">Night<b>Twin</b></span>
              <span className="wm-by">by Team TwinPulse</span>
            </span>
          </a>
          <nav className="nav" aria-label="Main">
            {NAV.map((n) => (
              <button key={n.key} className={active === n.key ? 'active' : ''} onClick={() => go(n.key)}
                aria-current={active === n.key ? 'page' : undefined}>
                <Icon name={n.icon} size={15} />
                <span>{n.label}</span>
              </button>
            ))}
          </nav>
          <div className="top-right">
            <span className="pill-night"><Icon name="moon" size={13} /> Tonight · 17 Oct · 21:00</span>
            <span className="pill-demo" title="All patients shown are synthetic">Synthetic demo</span>
          </div>
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
        <div className="footer-inner">
          <div className="footer-brand"><Logo size={22} /> <b>NightTwin</b> by Team TwinPulse · Newton School of Technology, Rishihood University</div>
          <div className="muted">Happiest Health Digital Twin Challenge 2026 · Decision support for clinicians, not a medical device · Validated on open real-patient data (HUPA-UCM, T1D-UOM) · Apache-2.0</div>
        </div>
      </footer>
    </div>
  )
}
