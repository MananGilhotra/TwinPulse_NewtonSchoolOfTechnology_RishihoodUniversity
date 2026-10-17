import Icon from './Icon.jsx'
import React, { useEffect, useMemo, useRef, useState } from 'react'
import { getPatient, postWhatIf, pct, riskLevel, REGIMEN } from '../api.js'
import { FanChart, GuardChart, HourBars, Timeline } from './charts.jsx'
import FamilyMessage from './FamilyMessage.jsx'

const NO_PLAN = { snack_g: 0, dinner_rapid_pct: 0, long_acting_pct: 0, long_acting_shift_min: 0, skip_play: false }

function fhirValue(bundle, id) {
  const e = bundle.entry.find((x) => x.resource.id?.endsWith(id))
  if (!e) return null
  const r = e.resource
  if (!r.valueQuantity) return r.valueString
  const { value, unit } = r.valueQuantity
  return `${value} ${value === 1 && unit.endsWith('s') ? unit.slice(0, -1) : unit}`
}

function EhrCard({ meta, fhir }) {
  const hb = parseFloat(fhirValue(fhir, '718-7'))
  const rows = [
    ['HbA1c', fhirValue(fhir, '4548-4')],
    ['Haemoglobin', fhirValue(fhir, '718-7'), hb < 11.5 ? 'Anaemia: HbA1c may read falsely high. Trust CGM/time-in-range for dosing.' : null],
    ['Weight', fhirValue(fhir, '29463-7')],
    ['Daily insulin', fhirValue(fhir, 'tdd')],
    ['Severe lows (12 m)', fhirValue(fhir, 'severe-hypo-12m')],
    ['Hypo awareness', fhirValue(fhir, 'hypo-awareness')],
    ['HLA genotype', fhirValue(fhir, 'hla')],
    ['Autoantibodies', fhirValue(fhir, 'autoantibodies')],
    ['Test strips', fhirValue(fhir, 'strips')],
  ]
  return (
    <div className="card">
      <div className="card-title"><Icon name="file" /> Health record <span className="muted small">FHIR R4 · ABDM-ready</span></div>
      <div className="ehr">
        {rows.map(([k, v, flag]) => (
          <div key={k} className="ehr-row">
            <span className="muted">{k}</span>
            <span>{v}</span>
            {flag && <div className="flag">{flag}</div>}
          </div>
        ))}
      </div>
      <div className="consent">✓ Parental consent on file. Data processed by the clinic for the child's health services (DPDP Act 2023, s.9 and Rules Sch. IV).</div>
    </div>
  )
}

function Why({ items, base }) {
  return (
    <div className="card">
      <div className="card-title"><Icon name="alert" /> Why tonight is risky</div>
      <p className="muted small">The twin removes one thing at a time and re-lives the night. The bigger the bar, the more that factor drives tonight's risk.</p>
      {items.map((x) => (
        <div key={x.factor} className="why-row">
          <div>{x.factor}</div>
          {x.contribution != null ? (
            <div className="why-bar">
              <div style={{ width: `${Math.max(0, (x.contribution / Math.max(base, 0.01)) * 100)}%` }} />
              <span>{x.contribution > 0 ? `+${Math.round(x.contribution * 100)} pts` : 'little effect'}</span>
            </div>
          ) : <div className="muted small">starting point for tonight</div>}
        </div>
      ))}
    </div>
  )
}

function Rehearse({ meta, plan, setPlan, result, busy }) {
  const nph = meta.insulin_type === 'nph'
  const set = (k) => (e) => setPlan({ ...plan, [k]: e.target.type === 'checkbox' ? e.target.checked : Number(e.target.value) })
  return (
    <div className="card rehearse">
      <div className="card-title"><Icon name="spark" /> Rehearse a plan on the twin</div>
      <div className="presets">
        <span className="muted small">Quick plans:</span>
        <button className="chip" onClick={() => setPlan({ ...plan, snack_g: 15 })}>Bedtime snack</button>
        {nph && <button className="chip" onClick={() => setPlan({ ...plan, snack_g: 15, long_acting_shift_min: 90 })}>Snack + NPH at bedtime</button>}
        <button className="chip" onClick={() => setPlan({ ...plan, dinner_rapid_pct: -20 })}>Sports day: dinner dose −20%</button>
        <button className="chip" onClick={() => setPlan({ snack_g: 0, dinner_rapid_pct: 0, long_acting_pct: 0, long_acting_shift_min: 0, skip_play: false })}>Reset</button>
      </div>
      <div className="controls">
        <label>Bedtime snack (22:30)
          <select value={plan.snack_g} onChange={set('snack_g')}>
            <option value={0}>None</option>
            <option value={15}>15 g: glass of milk + 2 biscuits</option>
            <option value={30}>30 g: milk + banana</option>
          </select>
        </label>
        <label>Dinner {nph ? 'Regular' : 'rapid-acting'} insulin: {plan.dinner_rapid_pct}%
          <input type="range" min={-40} max={0} step={10} value={plan.dinner_rapid_pct} onChange={set('dinner_rapid_pct')} />
        </label>
        <label>{nph ? 'Evening NPH' : 'Bedtime glargine'} dose: {plan.long_acting_pct}%
          <input type="range" min={-40} max={0} step={10} value={plan.long_acting_pct} onChange={set('long_acting_pct')} />
        </label>
        <label>Move {nph ? 'evening NPH' : 'glargine'} later: {plan.long_acting_shift_min} min
          <input type="range" min={0} max={120} step={30} value={plan.long_acting_shift_min} onChange={set('long_acting_shift_min')} />
          {nph && <span className="hint">Moving NPH from dinner to bedtime shifts its peak past 3 AM: a standard fix for night lows on human insulin.</span>}
        </label>
        <label className="check"><input type="checkbox" checked={plan.skip_play} onChange={set('skip_play')} /> No evening play today</label>
      </div>
      {result && (
        <div className={`result ${riskLevel(result.risk.p_low)}`}>
          {busy ? 'Re-living the night…' : (
            <>Risk of a low tonight: <b>{pct(result.baseline.p_low)}</b> → <b>{pct(result.risk.p_low)}</b>
              {result.risk.p_low_l2 > 0.01 && <> · serious lows (&lt;54): {pct(result.risk.p_low_l2)}</>}</>
          )}
        </div>
      )}
    </div>
  )
}

function Guard({ guard, meta }) {
  const [i, setI] = useState(guard.available ? guard.series.length - 1 : 0)
  const timer = useRef(null)
  const play = () => {
    clearInterval(timer.current)
    setI(0)
    timer.current = setInterval(() => setI((x) => {
      if (x >= guard.series.length - 1) { clearInterval(timer.current); return x }
      return x + 1
    }), 40)
  }
  useEffect(() => () => clearInterval(timer.current), [])
  if (!guard.available) {
    return (
      <div className="card">
        <div className="card-title"><Icon name="pulse" /> Night guard (real time)</div>
        <p className="muted">{guard.reason} The bedtime rehearsal above still applies. If the twin's risk is high, the family gets a reminder to check at the predicted time.</p>
      </div>
    )
  }
  const now = guard.series[i]
  const alertIdx = guard.first_alert ? guard.series.findIndex((s) => s.t.endsWith(guard.first_alert)) : -1
  const alerted = alertIdx >= 0 && i >= alertIdx
  return (
    <div className="card">
      <div className="card-title"><Icon name="pulse" /> Night guard: replay of tonight
        <button className="btn small" onClick={play}><Icon name="play" size={12} /> Replay night</button>
      </div>
      <GuardChart series={guard.series} upTo={i} threshold={guard.threshold} alertAt={guard.first_alert} onsetAt={guard.low_onset} />
      <div className="guard-foot">
        <div><span className="muted">Now</span> {now.t.slice(11, 16)} · CGM {Math.round(now.cgm)} mg/dL · risk of a low within 2 h <b>{pct(now.p120)}</b></div>
        {guard.lead_min != null && <div className="lead">Alert at {guard.first_alert} · low began {guard.low_onset} · <b>{guard.lead_min} min warning</b></div>}
      </div>
      {alerted && <FamilyMessage meta={meta} kind="night" />}
    </div>
  )
}

// Shareable demo states, e.g. #patient/TP-001?snack=15&shift=90&approve=1
function planFromQuery(q) {
  return {
    snack_g: Number(q.snack || 0), dinner_rapid_pct: Number(q.dinner || 0), long_acting_pct: Number(q.long || 0),
    long_acting_shift_min: Number(q.shift || 0), skip_play: q.noplay === '1',
  }
}

export default function PatientView({ id, onBack, query = {} }) {
  const [p, setP] = useState(null)
  const [plan, setPlan] = useState(() => planFromQuery(query))
  const [result, setResult] = useState(null)
  const [busy, setBusy] = useState(false)
  const [sent, setSent] = useState(query.approve === '1')

  useEffect(() => { getPatient(id).then(setP) }, [id])
  useEffect(() => {
    if (!p) return
    const changed = JSON.stringify(plan) !== JSON.stringify(NO_PLAN)
    if (!changed) { setResult(null); return }
    setBusy(true)
    const t = setTimeout(() => postWhatIf(id, plan).then((r) => { setResult(r); setBusy(false) }), 250)
    return () => clearTimeout(t)
  }, [plan, p, id])

  if (!p) return <div className="loading">Loading twin…</div>
  const { meta, tonight } = p
  const r = tonight.risk
  const wk = p.weekly
  return (
    <div>
      <button className="link back" onClick={onBack}>← Tonight Board</button>
      <div className="patient-head">
        <div>
          <div className="who big-who"><span className={`avatar lg ${riskLevel(r.p_low)}`}>{meta.name[0]}</span>
          <div><h1>{meta.name}, {meta.age} <span className="synthetic">synthetic</span></h1>
          <div className="muted">{meta.town} · {meta.language} · Parent: {meta.parent} · {REGIMEN[meta.regimen]} · {meta.insulin_source}</div>
          <div className="tags"><span className={`badge ${meta.mode}`}>{meta.mode === 'cgm' ? 'CGM' : 'Finger-prick'}</span>
            {meta.hypo_unaware && <span className="badge warnb">Impaired hypo awareness</span>}
            <span className="badge">{meta.phone}</span></div></div></div>
        </div>
        <div className={`headline ${riskLevel(r.p_low)}`}>
          <div className="big">{pct(r.p_low)}</div>
          <div>of {meta.name}'s 500 rehearsed nights go low{r.p_low >= 0.05 && r.median_onset ? <>, most often around <b>{r.median_onset}</b></> : ''}</div>
        </div>
      </div>

      <div className="grid">
        <div className="col-main">
          <div className="card">
            <div className="card-title"><Icon name="moon" /> Tonight, rehearsed 500 times <span className="muted small">physiology twin · fitted on {meta.name}'s last 13 nights</span></div>
            <FanChart band={tonight.band} alt={result?.band} />
            <div className="legend"><span className="sw band" /> spread of simulated nights {result && <><span className="sw alt" /> with the plan</>}</div>
          </div>
          <Rehearse meta={meta} plan={plan} setPlan={setPlan} result={result} busy={busy} />
          {result && (
            <div className="card approve">
              <button className="btn primary" onClick={() => setSent(true)}><Icon name="check" size={15} /> Approve plan and send to family</button>
              <span className="muted small">Only the doctor changes treatment. The family sees the approved action in {meta.language}.</span>
              {sent && <FamilyMessage meta={meta} kind="plan" plan={plan} />}
            </div>
          )}
          <Guard guard={p.guard} meta={meta} />
          <div className="card">
            <div className="card-title"><Icon name="chart" /> Last 36 hours <span className="muted small">{meta.mode === 'cgm' ? 'CGM' : 'finger-prick readings only'} · meals ▲ · insulin ◆ · steps</span></div>
            <Timeline series={p.series} mode={meta.mode} />
          </div>
        </div>
        <div className="col-side">
          <Why items={tonight.explain} base={r.p_low} />
          <EhrCard meta={meta} fhir={p.fhir} />
          <div className="card">
            <div className="card-title"><Icon name="chart" /> Last 14 days <span className="muted small">{wk.source}</span></div>
            <div className="tir">
              <div className="tir-bar">
                <div className="tbr" style={{ width: pct(wk.tbr70) }} />
                <div className="in" style={{ width: pct(wk.tir) }} />
                <div className="tar" style={{ width: pct(wk.tar180) }} />
              </div>
              <div className="tir-legend">
                <span><b>{pct(wk.tir)}</b> in range <span className="muted">(target &gt;70%)</span></span>
                <span><b>{pct(wk.tbr70, 1)}</b> below 70 <span className="muted">(&lt;4%)</span></span>
                <span><b>{pct(wk.tbr54, 1)}</b> below 54 <span className="muted">(&lt;1%)</span></span>
                <span>GMI {wk.gmi}% · CV {pct(wk.cv)}</span>
              </div>
            </div>
            <div className="muted small">Time below 70 by hour of day</div>
            <HourBars rows={wk.lows_by_hour} />
          </div>
          <div className="card">
            <div className="card-title"><Icon name="pulse" /> Twin parameters</div>
            <div className="ehr">
              <div className="ehr-row"><span className="muted">Insulin sensitivity</span><span>{tonight.twin.si.toFixed(3)}</span></div>
              <div className="ehr-row"><span className="muted">Glucose settle point</span><span>{Math.round(tonight.twin.gb)} mg/dL</span></div>
              <div className="ehr-row"><span className="muted">Rise per gram carb</span><span>{tonight.twin.cf.toFixed(1)} mg/dL</span></div>
              <div className="ehr-row"><span className="muted">Exercise effect</span><span>{(tonight.twin.ex * 1000).toFixed(1)} ×10⁻³</span></div>
              <div className="ehr-row"><span className="muted">Fit error (past nights)</span><span>{Math.round(tonight.twin.fit_rmse)} mg/dL</span></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
