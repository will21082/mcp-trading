const BASE = ''   // proxied via vite to http://localhost:8000

async function req(path, opts = {}) {
  const r = await fetch(BASE + path, opts)
  if (!r.ok) {
    const body = await r.json().catch(() => ({}))
    throw new Error(body.detail || `HTTP ${r.status}`)
  }
  return r.json()
}

const post = (path, body) => req(path, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(body),
})

export const api = {
  health:        ()      => req('/api/health'),
  latestSignals: ()      => req('/api/signals/latest'),
  config:        ()      => req('/api/config'),
  scan:          (body)  => post('/api/scan', body),
  backtest:      (body)  => post('/api/backtest', body),
}
