import React, { useEffect, useState } from 'react'
import { getValidation } from '../api.js'

const STATS = [
  { big: '2.29 lakh', text: 'Indian children and teens with type 1 diabetes, the most of any country', src: 'IDF Diabetes Atlas 2021' },
  { big: '55%', text: 'of severe lows in type 1 diabetes happen during sleep', src: 'DCCT' },
  { big: '₹1.1 lakh+', text: 'a year for a CGM with alarms in India, out of reach for most families', src: 'Retail sensor prices, 2026' },
]

const STEPS = [
  {
    n: '1', title: 'Learn the child',
    text: 'A personal glucose–insulin model is fitted to each child from their own nights: insulin, meals, play, and CGM or finger-pricks, plus the health record (FHIR).',
  },
  {
    n: '2', title: 'Live tonight first',
    text: 'At 9 PM the twin simulates tonight 500 times. The doctor sees who is at risk, when, and why, then rehearses a fix on the twin before prescribing it.',
  },
  {
    n: '3', title: 'Guard the real night',
    text: 'For CGM users, a model trained on real patients warns about an hour before a low and calls the parent in their language.',
  },
]

export default function Overview({ go }) {
  const [v, setV] = useState(null)
  useEffect(() => { getValidation().then(setV).catch(() => {}) }, [])
  const ge = v?.extra?.guard_events?.unseen_patients?.['0.2']
  const sr = v?.extra?.sensor_ranking
  return (
    <div className="overview">
      <section className="hero">
        <div className="hero-text">
          <div className="eyebrow">Digital twin · Type 1 diabetes · India</div>
          <h1>Before a child sleeps, her twin lives the night first.</h1>
          <p>
            TwinPulse is a physiology-based digital twin for children with type 1 diabetes. It rehearses tonight on a
            virtual copy of the child, shows the doctor which nights are dangerous and what makes them safer, and guards
            the real night so a parent is woken <i>before</i> a low, not after.
          </p>
          <div className="hero-cta">
            <button className="btn primary big" onClick={() => go('board')}>Open tonight's board →</button>
            <button className="btn big" onClick={() => go('patient/TP-001')}>Meet Ananya's twin</button>
          </div>
        </div>
        <div className="hero-quote">
          <div className="quote-time">2:47 AM · Raichur</div>
          <p>"Every night for three years I set an alarm to prick her finger. I never know which night is the dangerous one."</p>
          <div className="muted small">Composite story of a parent's experience, for illustration</div>
        </div>
      </section>

      <section className="stats">
        {STATS.map((s) => (
          <div key={s.big} className="stat">
            <div className="stat-big">{s.big}</div>
            <div>{s.text}</div>
            <div className="muted small">{s.src}</div>
          </div>
        ))}
      </section>

      <section className="steps">
        {STEPS.map((s) => (
          <div key={s.n} className="step">
            <div className="step-n">{s.n}</div>
            <div className="step-title">{s.title}</div>
            <p>{s.text}</p>
          </div>
        ))}
      </section>

      <section className="proof">
        <div className="proof-title">Tested on real patients the model never saw</div>
        <div className="proof-grid">
          <div><span>{ge ? `${Math.round(ge.caught_15min_ahead * 100)}%` : '…'}</span>of {ge?.night_lows ?? ''} night-time lows warned at least 15 min ahead</div>
          <div><span>{ge ? `${Math.round(ge.median_warning_min)} min` : '…'}</span>median warning before the low</div>
          <div><span>{ge ? ge.false_alarms_per_night.toFixed(2) : '…'}</span>false alarms per night</div>
          <div><span>{sr ? `${Math.round((sr.top_third_later_rate / sr.bottom_third_later_rate) * 10) / 10}×` : '…'}</span>more night lows in children a one-week trial sensor flags as highest risk</div>
        </div>
        <button className="link" onClick={() => go('evidence')}>See all the evidence, including what didn't work →</button>
      </section>

      <section className="fusion">
        <div className="fusion-col">
          <div className="fusion-head">Static: health record</div>
          <ul><li>Age, weight, HbA1c, haemoglobin</li><li>Insulin regimen and daily dose</li><li>Past severe lows, hypo awareness</li><li>HLA genotype, islet autoantibodies</li><li>FHIR R4, ABDM-ready</li></ul>
        </div>
        <div className="fusion-mid plus">+</div>
        <div className="fusion-col">
          <div className="fusion-head">Dynamic: wearables</div>
          <ul><li>CGM every 5 min, or finger-pricks</li><li>Insulin doses and meals</li><li>Steps and heart rate from a band</li><li>Sleep window</li></ul>
        </div>
        <div className="fusion-mid">→ <b>Twin</b> →</div>
        <div className="fusion-col out">
          <div className="fusion-head">Output</div>
          <ul><li>Tonight's risk, time and depth of a low</li><li>Why: factor-by-factor explanation</li><li>Rehearsed plan the doctor approves</li><li>Real-time alert to the parent</li></ul>
        </div>
      </section>
    </div>
  )
}
