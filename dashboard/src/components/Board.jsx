import React, { useEffect, useState } from 'react'
import { getBoard, pct, riskLevel, REGIMEN } from '../api.js'

export default function Board({ onOpen }) {
  const [data, setData] = useState(null)
  const [err, setErr] = useState(null)
  useEffect(() => {
    getBoard().then(setData).catch((e) => setErr(String(e)))
  }, [])
  if (err) return <div className="card error">Could not reach the twin API: {err}</div>
  if (!data) return <div className="loading">The twins are rehearsing tonight for every child…</div>

  const high = data.patients.filter((p) => riskLevel(p.p_low) === 'high')
  const med = data.patients.filter((p) => riskLevel(p.p_low) === 'medium')
  return (
    <div>
      <div className="page-head">
        <div>
          <h1>Tonight Board</h1>
          <p className="muted">
            9:00 PM, {new Date(data.tonight).toDateString()}. Each child's twin has lived tonight 500 times.
            Children at the top need a call before bed.
          </p>
        </div>
        <div className="kpis">
          <div className="kpi danger"><span>{high.length}</span>high-risk nights</div>
          <div className="kpi warn"><span>{med.length}</span>to watch</div>
          <div className="kpi"><span>{data.patients.length}</span>children enrolled</div>
        </div>
      </div>
      <div className="card">
        <table className="board">
          <thead>
            <tr>
              <th>Child</th>
              <th>Tonight's risk of a low</th>
              <th>Likely time</th>
              <th>Last glucose</th>
              <th>Monitoring</th>
              <th>Insulin</th>
              <th>Night lows, last 14 days</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {data.patients.map((p) => (
              <tr key={p.id} onClick={() => onOpen(p.id)} className={p.hero ? 'hero' : ''}>
                <td>
                  <div className="child">{p.name}, {p.age}</div>
                  <div className="muted small">{p.town} · {p.language}</div>
                </td>
                <td>
                  <div className={`risk-pill ${riskLevel(p.p_low)}`}>{pct(p.p_low)}</div>
                  <div className="riskbar"><div style={{ width: pct(p.p_low) }} className={riskLevel(p.p_low)} /></div>
                </td>
                <td>{p.p_low >= 0.05 ? p.onset || '–' : '–'}</td>
                <td>{p.last_bg ? `${Math.round(p.last_bg)} mg/dL` : '–'}</td>
                <td><span className={`badge ${p.mode}`}>{p.mode === 'cgm' ? 'CGM' : 'Finger-prick'}</span></td>
                <td className="small">{REGIMEN[p.regimen]}</td>
                <td>{pct(p.night_tbr_14d, 1)} of night time</td>
                <td><button className="link">Open twin →</button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="muted small">
        Risk = share of the twin's 500 simulated nights that fall below 70 mg/dL for 15+ minutes between 00:00 and 06:00.
        Bedtime risk is a planning aid, not a diagnosis: on real patients, bedtime-only prediction is weak (see Evidence).
        The in-night guard for CGM users is where TwinPulse is strongest.
      </p>
    </div>
  )
}
