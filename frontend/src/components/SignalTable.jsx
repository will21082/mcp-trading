import { useState } from 'react'

// ── helpers ──────────────────────────────────────────────────────────────────
const rClass  = r => r >= 0 ? `c${r}`  : `cm${Math.abs(r)}`
const bgClass = r => r >= 0 ? `bg${r}` : `bgm${Math.abs(r)}`

function ratingColor(r) {
  const m = { 3:'var(--g3)',2:'var(--g2)',1:'var(--g1)',0:'var(--n0)','-1':'var(--r1)','-2':'var(--r2)','-3':'var(--r3)' }
  return m[r] ?? 'var(--n0)'
}

function fmtPrice(p) {
  if (!p) return '—'
  if (p >= 10000)  return p.toLocaleString('en', {maximumFractionDigits: 0})
  if (p >= 100)    return p.toFixed(2)
  if (p >= 1)      return p.toFixed(4)
  if (p >= 0.0001) return p.toFixed(6)
  return p.toExponential(3)
}

function ConfDots({ n, max = 10 }) {
  return (
    <div className="conf-wrap">
      {Array.from({ length: max }, (_, i) => (
        <div key={i} className={`conf-dot ${i < n ? 'lit' : ''}`} />
      ))}
      <span className="conf-num">{n}/10</span>
    </div>
  )
}

function BBBar({ rating }) {
  const bw = Math.abs(rating) / 3 * 100
  const bl = rating >= 0 ? 50 : 50 - bw
  return (
    <div className="bb-wrap">
      <div className="bb-track">
        <div className="bb-track-mid" />
        <div className={`bb-fill ${bgClass(rating)}`} style={{ left: `${bl}%`, width: `${bw}%` }} />
      </div>
      <span className={`bb-num ${rClass(rating)}`}>{rating > 0 ? `+${rating}` : rating}</span>
    </div>
  )
}

// ── columns config ────────────────────────────────────────────────────────────
const COLS = [
  { key: 'symbol',     label: 'Symbol' },
  { key: 'direction',  label: 'Dir',      noSort: true },
  { key: 'price',      label: 'Price' },
  { key: 'bb_rating',  label: 'BB Rating' },
  { key: 'bbw',        label: 'BBW' },
  { key: 'rsi',        label: 'RSI' },
  { key: 'adx',        label: 'ADX' },
  { key: 'confidence', label: 'Score' },
  { key: 'warnings',   label: 'Warn',     noSort: true },
]

// ── component ─────────────────────────────────────────────────────────────────
export default function SignalTable({ signals = [], selectedSymbol, onSelect, isLoading }) {
  const [sortCol, setSortCol] = useState('bb_rating')
  const [sortDir, setSortDir] = useState(-1)
  const [dirFilter, setDirFilter] = useState('ALL')

  function handleSort(key) {
    if (key === sortCol) setSortDir(d => d * -1)
    else { setSortCol(key); setSortDir(key === 'bb_rating' ? -1 : 1) }
  }

  const filtered = dirFilter === 'ALL' ? signals
    : signals.filter(s => s.direction === dirFilter)

  const sorted = [...filtered].sort((a, b) => {
    const av = a[sortCol], bv = b[sortCol]
    if (av == null) return 1
    if (bv == null) return -1
    if (typeof av === 'string') return sortDir * av.localeCompare(bv)
    return sortDir * (av - bv)
  })

  const longCnt  = signals.filter(s => s.direction === 'LONG').length
  const shortCnt = signals.filter(s => s.direction === 'SHORT').length

  return (
    <div className="left-panel">
      <div className="panel-head">
        <span className="panel-title">Signal Results</span>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div className="dir-filter">
            <button className={`dir-btn ${dirFilter === 'ALL'   ? 'active-all'   : ''}`} onClick={() => setDirFilter('ALL')}>ALL {signals.length}</button>
            <button className={`dir-btn ${dirFilter === 'LONG'  ? 'active-long'  : ''}`} onClick={() => setDirFilter('LONG')}>LONG {longCnt}</button>
            <button className={`dir-btn ${dirFilter === 'SHORT' ? 'active-short' : ''}`} onClick={() => setDirFilter('SHORT')}>SHORT {shortCnt}</button>
          </div>
          <span className="panel-count">{sorted.length} shown</span>
        </div>
      </div>

      {isLoading && (
        <div className="load-mask">
          <div className="load-txt">Scanning market data...</div>
          <div className="load-bar"><div className="load-prog" /></div>
        </div>
      )}

      <div className="tbl-scroll">
        <table>
          <thead>
            <tr>
              {COLS.map(c => (
                <th key={c.key}
                    className={!c.noSort && sortCol === c.key ? (sortDir === 1 ? 'asc' : 'desc') : ''}
                    onClick={() => !c.noSort && handleSort(c.key)}>
                  {c.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {sorted.length === 0 ? (
              <tr><td colSpan={COLS.length}>
                <div className="empty">
                  <div className="empty-icon">◈</div>
                  <span>Run a scan to see signals</span>
                </div>
              </td></tr>
            ) : sorted.map(s => {
              const sym = s.symbol || ''
              const base = sym.replace(/USDT$|BTC$|ETH$/, '')
              const quote = sym.slice(base.length)
              const bbRating = parseInt(s.bb_rating ?? 0)
              const isSel = sym === selectedSymbol

              return (
                <tr key={sym + s.direction} className={isSel ? 'sel' : ''} onClick={() => onSelect(s)}>
                  <td><span className="sym"><span>{base}</span><span className="sym-q">/{quote}</span></span></td>
                  <td>
                    <span className={`dir-badge ${s.direction === 'LONG' ? 'dir-long' : 'dir-short'}`}>
                      {s.direction}
                    </span>
                  </td>
                  <td><span className="price">{fmtPrice(s.price)}</span></td>
                  <td><BBBar rating={bbRating} /></td>
                  <td>
                    <div className="bbw-cell">
                      <span style={{ color: 'var(--tx-1)', fontSize: 10 }}>{(s.bbw * 100).toFixed(2)}%</span>
                      {s.bbw < 0.03 && <span className="sqz-tag">SQZ</span>}
                    </div>
                  </td>
                  <td>
                    <span style={{ color: s.rsi > 70 ? 'var(--r1)' : s.rsi < 30 ? 'var(--cyan)' : 'var(--tx-1)', fontSize: 10 }}>
                      {s.rsi?.toFixed(1)}
                    </span>
                  </td>
                  <td>
                    <span style={{ color: s.adx > 25 ? 'var(--g1)' : 'var(--tx-2)', fontSize: 10 }}>
                      {s.adx?.toFixed(1)}
                    </span>
                  </td>
                  <td><ConfDots n={s.confidence ?? 0} /></td>
                  <td>
                    {s.warnings?.length
                      ? <span className="warn-icon" title={s.warnings.join(' | ')}>⚠</span>
                      : <span style={{ color: 'var(--tx-3)' }}>—</span>
                    }
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}
