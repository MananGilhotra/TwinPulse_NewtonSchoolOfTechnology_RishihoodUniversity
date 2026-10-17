import React, { useEffect, useState } from 'react'
import { getBoard, getValidation, pct } from '../api.js'

export default function SensorPriority({ onOpen }) {
  const [board, setBoard] = useState(null)
  const [v, setV] = useState(null)
  const [sensors, setSensors] = useState(2)
  useEffect(() => { getBoard().then(setBoard); getValidation().then(setV) }, [])
  if (!board) return <div className="loading">Ranking children…</div>
  const finger = board.patients.filter((p) => p.mode === 'fingerstick').sort((a, b) => b.night_tbr_14d - a.night_tbr_14d)
  const sr = v?.extra?.sensor_ranking
  return (
    <div>
      <div className="page-head">
        <div>
          <h1>Sensor Priority</h1>
          <p className="muted">
            A state programme has a few CGMs to give out. Each finger-prick child wore one 14-day trial sensor; the twin ranks
            who will have the most night lows, so continuous protection reaches the children who need it most.
          </p>
        </div>
        <div className="kpis">
          <label className="kpi sel">CGMs available
            <select value={sensors} onChange={(e) => setSensors(Number(e.target.value))}>
              {[1, 2, 3, 4].map((n) => <option key={n} value={n}>{n}</option>)}
            </select>
          </label>
        </div>
      </div>
      <div className="grid">
        <div className="card">
          <table className="board">
            <thead><tr><th>#</th><th>Child</th><th>Night time below 70 (trial sensor)</th><th>Tonight's twin risk</th><th>Insulin</th><th>Decision</th></tr></thead>
            <tbody>
              {finger.map((p, i) => (
                <tr key={p.id} onClick={() => onOpen(p.id)}>
                  <td>{i + 1}</td>
                  <td><div className="child">{p.name}, {p.age}</div><div className="muted small">{p.town}</div></td>
                  <td>
                    <b>{pct(p.night_tbr_14d, 1)}</b>
                    <div className="riskbar"><div className="high" style={{ width: `${Math.min(100, p.night_tbr_14d * 600)}%` }} /></div>
                  </td>
                  <td>{pct(p.p_low)}</td>
                  <td className="small">{p.regimen === 'premixed' ? 'Premixed 30/70' : 'NPH + Regular'}</td>
                  <td>{i < sensors ? <span className="badge give">Give CGM</span> : <span className="badge">Finger-prick + twin rehearsal</span>}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="col-side">
          <div className="card">
            <div className="card-title">Why this works (real patients)</div>
            {sr ? (
              <>
                <p>Among <b>{sr.patients}</b> real people with T1D, time below range in the first week ranked who would have the most night lows later
                  (Spearman <b>{sr.spearman_week1_tbr_vs_later.toFixed(2)}</b>).</p>
                <div className="compare">
                  <div><span className="danger-text">{pct(sr.top_third_later_rate)}</span>of later nights had a low in the top third</div>
                  <div><span className="good-text">{pct(sr.bottom_third_later_rate)}</span>in the bottom third</div>
                </div>
              </>
            ) : '…'}
            <p className="muted small">One ₹4–5k trial sensor per child, instead of ₹1.1 lakh a year for everyone, points scarce CGMs to the highest-risk children.</p>
          </div>
        </div>
      </div>
    </div>
  )
}
