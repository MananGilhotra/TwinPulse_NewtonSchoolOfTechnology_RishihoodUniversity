// Browser port of twinpulse/twin.py: the same glucose–insulin model, so the live demo can
// re-live the night for any plan without a server. Python remains the reference implementation.

const P2 = 0.02, TAU_I = 55.0, KABS = 0.03, TAU_E = 240.0, STEP_NORM = 500.0
const LOWER = [1e-4, 1e-3, 70.0, 1.0, 1e-5]
const UPPER = [2.0, 0.05, 300.0, 15.0, 0.02]

function rng(seed) {
  let a = seed >>> 0
  const uni = () => {
    a |= 0; a = (a + 0x6d2b79f5) | 0
    let t = Math.imul(a ^ (a >>> 15), 1 | a)
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
  const normal = () => {
    let u = 0, v = 0
    while (u === 0) u = uni()
    while (v === 0) v = uni()
    return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v)
  }
  return { uni, normal }
}

function simulateOne(p, ib, tauL, inp, gObs, nudgeUntil, gain, noise) {
  const [si, sg, gb, cf, ex] = p
  const T = inp.bolus.length
  const out = new Float64Array(T)
  let G = gb
  for (let t = 0; t < T; t++) if (gObs[t] != null) { G = gObs[t]; break }
  let X = 0, S1 = ib * TAU_I, S2 = ib * TAU_I, L1 = 0, L2 = 0, Q1 = 0, Q2 = 0, E = 0
  for (let t = 0; t < T; t++) {
    S1 += inp.bolus[t] + inp.basal[t]
    L1 += inp.inj[t]
    Q1 += inp.carbs[t]
    for (let k = 0; k < 5; k++) {
      const ia = S2 / TAU_I + L2 / tauL
      const dS1 = -S1 / TAU_I, dS2 = (S1 - S2) / TAU_I
      const dL1 = -L1 / tauL, dL2 = (L1 - L2) / tauL
      const dQ1 = -KABS * Q1, dQ2 = KABS * (Q1 - Q2)
      const ra = cf * KABS * Q2
      const dX = -P2 * X + P2 * si * (ia - ib)
      const a = Math.min(inp.steps[t] / STEP_NORM, 1.5)
      const dE = (a - E) / TAU_E
      const dG = -(sg + X) * G + sg * gb + ra - ex * E * G
      S1 += dS1; S2 += dS2; L1 += dL1; L2 += dL2; Q1 += dQ1; Q2 += dQ2; X += dX; E += dE; G += dG
    }
    if (t < nudgeUntil && gObs[t] != null) G = G + gain * (gObs[t] - G)
    else G += noise[t]
    G = Math.min(Math.max(G, 20), 500)
    out[t] = G
  }
  return out
}

export function runNight(ti, overrides = {}, n = 500, seed = 1) {
  const r = rng(seed)
  const inp = {
    bolus: overrides.bolus || ti.bolus, basal: overrides.basal || ti.basal, inj: overrides.inj || ti.inj,
    carbs: overrides.carbs || ti.carbs, steps: overrides.steps || ti.steps,
  }
  const T = ti.bolus.length
  const trajs = []
  for (let s = 0; s < n; s++) {
    const p = ti.params.map((v) => v * Math.exp(r.normal() * 0.15))
    p[2] = ti.params[2] + r.normal() * 12
    for (let j = 0; j < 5; j++) p[j] = Math.min(Math.max(p[j], LOWER[j]), UPPER[j])
    const noise = new Float64Array(T)
    for (let t = 0; t < T; t++) noise[t] = r.normal() * ti.noise_sd
    trajs.push(simulateOne(p, ti.ib, ti.tau_l, inp, ti.glucose, ti.nudge_until, 0.6, noise))
  }
  return trajs
}

function times(ti) {
  const start = new Date(ti.start + ':00')
  return ti.bolus.map((_, i) => new Date(start.getTime() + i * 5 * 60000))
}

const pad = (x) => String(x).padStart(2, '0')
const iso = (d) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`

function quantile(sorted, q) {
  const pos = (sorted.length - 1) * q
  const lo = Math.floor(pos), hi = Math.ceil(pos)
  return sorted[lo] + (sorted[hi] - sorted[lo]) * (pos - lo)
}

export function nightRisk(ti, trajs, thr = 70) {
  const ts = times(ti)
  const cutoff = ts[ti.nudge_until - 1].getTime()
  const idx = ts.map((d, i) => i).filter((i) => ts[i].getHours() < 6 && ts[i].getTime() > cutoff)
  let lows = 0, lowsL2 = 0
  const onsets = [], mins = []
  for (const g of trajs) {
    let run = 0, run2 = 0, hit = -1, hit2 = false, mn = Infinity
    for (const i of idx) {
      mn = Math.min(mn, g[i])
      run = g[i] < thr ? run + 1 : 0
      run2 = g[i] < 54 ? run2 + 1 : 0
      if (run >= 3 && hit < 0) hit = i
      if (run2 >= 3) hit2 = true
    }
    if (hit >= 0) { lows++; onsets.push(idx[idx.indexOf(hit) - 2]) }
    if (hit2) lowsL2++
    mins.push(mn)
  }
  onsets.sort((a, b) => a - b)
  mins.sort((a, b) => a - b)
  const i0 = ti.nudge_until - 24
  const band = []
  for (let i = i0; i < ts.length; i++) {
    const col = trajs.map((g) => g[i]).sort((a, b) => a - b)
    band.push({ t: iso(ts[i]), p5: quantile(col, 0.05), p25: quantile(col, 0.25), p50: quantile(col, 0.5), p75: quantile(col, 0.75), p95: quantile(col, 0.95) })
  }
  const med = onsets.length ? ts[onsets[Math.floor(onsets.length / 2)]] : null
  return {
    risk: {
      p_low: lows / trajs.length, p_low_l2: lowsL2 / trajs.length,
      median_onset: med ? `${pad(med.getHours())}:${pad(med.getMinutes())}` : null,
      p10_min: quantile(mins, 0.1), median_min: quantile(mins, 0.5),
    },
    band,
  }
}

export function whatifOverrides(ti, { snack_g = 0, dinner_rapid_pct = 0, long_acting_pct = 0, long_acting_shift_min = 0, skip_play = false }) {
  const nu = ti.nudge_until
  const ov = {}
  if (snack_g) { const c = ti.carbs.slice(); c[nu - 6] += snack_g; ov.carbs = c }
  const e0 = nu - 36
  if (dinner_rapid_pct) { const b = ti.bolus.slice(); for (let i = e0; i < nu; i++) b[i] *= 1 + dinner_rapid_pct / 100; ov.bolus = b }
  if (long_acting_pct || long_acting_shift_min) {
    const inj = ti.inj.slice()
    const idx = []
    for (let i = e0 - 12; i < nu; i++) if (inj[i]) idx.push(i)
    for (const i of idx) {
      const dose = inj[i] * (1 + long_acting_pct / 100)
      inj[i] = 0
      const j = Math.min(i + Math.floor(long_acting_shift_min / 5), inj.length - 1)
      inj[j] += dose
    }
    ov.inj = inj
  }
  if (skip_play) { const s = ti.steps.slice(); for (let i = nu - 72; i < nu - 54; i++) s[i] = Math.min(s[i], 60); ov.steps = s }
  return ov
}

export function whatif(ti, plan) {
  const base = nightRisk(ti, runNight(ti))
  const res = nightRisk(ti, runNight(ti, whatifOverrides(ti, plan)))
  return { risk: res.risk, band: res.band, baseline: base.risk }
}
