async function req(path, opts) {
  const r = await fetch(path, opts)
  if (!r.ok) throw new Error(`${r.status} ${await r.text()}`)
  return r.json()
}

export const getBoard = () => req('/api/board')
export const getPatient = (id) => req(`/api/patients/${id}`)
export const getValidation = () => req('/api/validation')
export const postWhatIf = (id, body) =>
  req(`/api/patients/${id}/whatif`, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify(body),
  })

export const pct = (x, d = 0) => (x == null ? '–' : `${(x * 100).toFixed(d)}%`)
export const hhmm = (t) => t.slice(11, 16)
export const riskLevel = (p) => (p >= 0.4 ? 'high' : p >= 0.15 ? 'medium' : 'low')
export const REGIMEN = {
  nph_regular: 'NPH + Regular (human insulin)',
  premixed: 'Premixed 30/70',
  glargine_rapid: 'Glargine + rapid-acting',
}
