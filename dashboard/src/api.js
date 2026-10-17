import { whatif } from './twin.js'

// Static mode (GitHub Pages): read exported JSON and run the twin in the browser.
// Server mode (./run.sh): call the FastAPI service.
export const STATIC = import.meta.env.VITE_STATIC === '1'
const BASE = import.meta.env.BASE_URL

async function req(path, opts) {
  const r = await fetch(path, opts)
  if (!r.ok) throw new Error(`${r.status} ${await r.text()}`)
  return r.json()
}

const cache = {}
const getStatic = (file) => (cache[file] ||= req(`${BASE}data/${file}`))

export const getBoard = () => (STATIC ? getStatic('board.json') : req('/api/board'))
export const getPatient = (id) => (STATIC ? getStatic(`patients/${id}.json`) : req(`/api/patients/${id}`))
export const getValidation = () => (STATIC ? getStatic('validation.json') : req('/api/validation'))
export const postWhatIf = async (id, body) => {
  if (STATIC) {
    const p = await getPatient(id)
    await new Promise((r) => setTimeout(r, 0))
    // Same baseline as the rest of the page (computed by the Python twin); the plan is re-lived here.
    return { ...whatif(p.twin_input, body), baseline: p.tonight.risk }
  }
  return req(`/api/patients/${id}/whatif`, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify(body),
  })
}

export const pct = (x, d = 0) => (x == null ? '–' : `${(x * 100).toFixed(d)}%`)
export const hhmm = (t) => t.slice(11, 16)
export const riskLevel = (p) => (p >= 0.4 ? 'high' : p >= 0.15 ? 'medium' : 'low')
export const REGIMEN = {
  nph_regular: 'NPH + Regular (human insulin)',
  premixed: 'Premixed 30/70',
  glargine_rapid: 'Glargine + rapid-acting',
}
