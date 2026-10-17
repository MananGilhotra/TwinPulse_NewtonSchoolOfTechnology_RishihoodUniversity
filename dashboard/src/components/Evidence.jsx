import React, { useEffect, useState } from 'react'
import { getValidation } from '../api.js'

const f2 = (x) => (x == null ? '–' : x.toFixed(2))
const f1 = (x) => (x == null ? '–' : x.toFixed(1))

function GuardEvents({ ge }) {
  const [thr, setThr] = useState('0.2')
  const rows = [['Unseen patients (Spain, 5 groups)', ge.unseen_patients[thr]], ['External test (UK, other devices)', ge.external[thr]]]
  return (
    <div className="card highlight">
      <div className="card-title">Night guard, counted the way a parent would count it
        <span className="seg">
          {['0.15', '0.2', '0.3'].map((t) => (
            <button key={t} className={thr === t ? 'on' : ''} onClick={() => setThr(t)}>
              {t === '0.15' ? 'More sensitive' : t === '0.2' ? 'Balanced (default)' : 'Fewer alarms'}
            </button>
          ))}
        </span>
      </div>
      <div className="event-grid">
        {rows.map(([label, r]) => (
          <div key={label} className="event-col">
            <div className="muted">{label} · {r.night_lows} night-time lows over {r.nights} nights</div>
            <div className="event-kpis">
              <div><span>{Math.round(r.caught_15min_ahead * 100)}%</span>of lows warned ≥15 min ahead</div>
              <div><span>{Math.round(r.median_warning_min)} min</span>median warning</div>
              <div><span>{r.false_alarms_per_night.toFixed(2)}</span>false alarms per night</div>
            </div>
          </div>
        ))}
      </div>
      <p className="muted small">A night-time low = glucose below 70 mg/dL for 15+ minutes starting between 22:00 and 06:00, after at least 30 minutes in range.
        A false alarm = an alert episode at night with no low in the next 2 hours. Risk is smoothed over 15 minutes.</p>
    </div>
  )
}

export default function Evidence() {
  const [v, setV] = useState(null)
  useEffect(() => { getValidation().then(setV) }, [])
  if (!v) return <div className="loading">Loading evidence…</div>
  const rt = v.realtime
  const n = v.night
  const fc = rt.forecast
  return (
    <div>
      <div className="page-head">
        <div>
          <h1>Evidence</h1>
          <p className="muted">
            Every number here comes from <b>real people with type 1 diabetes</b>: HUPA-UCM (25 people, Spain, FreeStyle Libre 2 + Fitbit)
            for development, with patients split into 5 groups so each score is on people the model never saw, and T1D-UOM
            (UK, different devices) as an external test. The demo children are synthetic and are never used for scoring.
          </p>
        </div>
      </div>

      {v.extra && <GuardEvents ge={v.extra.guard_events} />}

      <div className="card">
        <div className="card-title">1 · Night guard: warning before a low (CGM users)</div>
        <table className="ev">
          <thead><tr><th>Predicts</th><th>Unseen patients (AUROC)</th><th>External UK data (AUROC)</th><th>Glucose-only model</th></tr></thead>
          <tbody>
            <tr><td>Low within 60 min, at night (22:00–06:00)</td><td><b>{f2(rt.low_next60.night_22_06_full_twin.auroc)}</b></td><td>{f2(rt.low_next60.external_night_22_06.auroc)}</td><td>{f2(rt.low_next60.night_22_06_glucose_only.auroc)}</td></tr>
            <tr><td>Low within 2 h, at night</td><td><b>{f2(rt.low_next120.night_22_06_full_twin.auroc)}</b></td><td>{f2(rt.low_next120.external_night_22_06.auroc)}</td><td>{f2(rt.low_next120.night_22_06_glucose_only.auroc)}</td></tr>
            <tr><td>Low within 2 h, any time of day</td><td>{f2(rt.low_next120.all_day_full_twin.auroc)}</td><td>{f2(rt.low_next120.external_all_day.auroc)}</td><td>{f2(rt.low_next120.all_day_glucose_only.auroc)}</td></tr>
          </tbody>
        </table>
        <p className="muted small">AUROC 0.5 = coin toss, 1.0 = perfect. Insulin, meal, step and heart-rate data add only about 0.01 over glucose alone on these datasets; we report that honestly.</p>
      </div>

      <div className="card">
        <div className="card-title">2 · Glucose forecast error (RMSE, mg/dL; lower is better)</div>
        <table className="ev">
          <thead><tr><th>Horizon</th><th>Assume no change</th><th>Extend the trend</th><th>NightTwin</th><th>Clarke grid zones A+B</th></tr></thead>
          <tbody>
            {['30min', '60min', '120min'].map((h) => (
              <tr key={h}><td>{h.replace('min', ' min')}</td><td>{f1(fc[h].persistence.rmse)}</td><td>{f1(fc[h].linear_trend.rmse)}</td>
                <td><b>{f1(fc[h].full_twin.rmse)}</b></td><td>{((fc[h].full_twin.clarke.A + fc[h].full_twin.clarke.B) * 100).toFixed(1)}%</td></tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="card">
        <div className="card-title">3 · What we could not do: predict the whole night from bedtime alone</div>
        <table className="ev">
          <thead><tr><th>Bedtime (23:00) prediction of a low between 00:00 and 06:00</th><th>Unseen patients</th><th>External</th></tr></thead>
          <tbody>
            <tr><td>Rule: lower bedtime glucose = higher risk</td><td>{f2(n.cv.rule_bedtime_bg.auroc)}</td><td>{f2(n.external.rule_bedtime_bg.auroc)}</td></tr>
            <tr><td>ML: CGM + insulin + meals + wearables + history</td><td>{f2(n.cv.full_twin.auroc)}</td><td>{f2(n.external.full_twin.auroc)}</td></tr>
            <tr><td>ML: finger-pricks + band only (no CGM)</td><td>{f2(n.cv.fingerstick_band.auroc)}</td><td>{f2(n.external.fingerstick_band.auroc)}</td></tr>
            {v.extra?.twin_bedtime?.['HUPA-UCM'] && (
              <tr><td>Physiology twin, refitted on each patient's previous nights</td><td>{f2(v.extra.twin_bedtime['HUPA-UCM'].twin_auroc)}</td><td>{f2(v.extra.twin_bedtime['T1D-UOM']?.twin_auroc)}</td></tr>
            )}
          </tbody>
        </table>
        <p className="muted small">
          Night-to-night variation in the same child is large, so bedtime-only risk is close to chance on {n.n_nights} real nights.
          That's why NightTwin uses the bedtime rehearsal to <i>compare plans</i> (what changes the risk) rather than to promise a night is safe,
          and relies on the in-night guard for warnings. What does work without nightly CGM: a child's first week on a trial sensor ranks which
          children will have the most night lows later (Spearman 0.63, 29 real patients), so scarce sensors can go to those who need them most.
        </p>
      </div>
    </div>
  )
}
