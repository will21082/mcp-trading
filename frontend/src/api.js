const BASE_URL = ''
const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const WS_URL   = `${protocol}//${window.location.host}/ws`

async function req(path, opts = {}) {
  const r = await fetch(BASE_URL + path, opts)
  if (!r.ok) {
    const body = await r.json().catch(() => ({}))
    throw new Error(body.detail || `HTTP ${r.status}`)
  }
  return r.json()
}

const get  = (path)        => req(path)
const post = (path, body)  => req(path, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(body),
})
const del  = (path)        => req(path, { method: 'DELETE' })

export const api = {
  health:        ()       => get('/api/health'),
  latestSignals: ()       => get('/api/signals/latest'),
  config:        ()       => get('/api/config'),
  marketOverview:()       => get('/api/market/overview'),
  getAlerts:     ()       => get('/api/alerts'),
  scan:          (body)   => post('/api/scan', body),
  backtest:      (body)   => post('/api/backtest', body),
  createAlert:   (body)   => post('/api/alerts', body),
  deleteAlert:   (id)     => del(`/api/alerts/${id}`),
}

export { WS_URL }
