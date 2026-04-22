function ratingColor(r) {
  const m = { 3:'var(--g3)',2:'var(--g2)',1:'var(--g1)',0:'var(--n0)','-1':'var(--r1)','-2':'var(--r2)','-3':'var(--r3)' }
  return m[r] ?? 'var(--n0)'
}
function rClass(r) { return r >= 0 ? `c${r}` : `cm${Math.abs(r)}` }

function fmtPrice(p) {
  if (!p) return '—'
  if (p >= 10000)  return p.toLocaleString('en', {maximumFractionDigits: 0})
  if (p >= 100)    return p.toFixed(2)
  if (p >= 1)      return p.toFixed(4)
  if (p >= 0.0001) return p.toFixed(6)
  return p.toExponential(3)
}

function DetailCard({ signal, onClose }) {
  const bbRating = parseInt(signal.bb_rating ?? 0)
  const sym = signal.symbol || ''
  const base = sym.replace(/USDT$|BTC$|ETH$/, '')

  return (
    <div className="detail-card">
      <div className="detail-hdr">
        <span className={`detail-sym ${rClass(bbRating)}`}>{base}/{sym.slice(base.length)}</span>
        <button className="detail-close" onClick={onClose}>✕ CLOSE</button>
      </div>

      <div className="ind-grid">
        {[
          ['Direction',   <span className={signal.direction === 'LONG' ? 'pos' : 'neg'}>{signal.direction}</span>],
          ['BB Rating',   <span className={rClass(bbRating)}>{bbRating > 0 ? `+${bbRating}` : bbRating}</span>],
          ['BBW',         `${(signal.bbw * 100).toFixed(2)}%`],
          ['Squeeze',     signal.bbw < 0.03 ? <span className="sqz-tag" style={{animation:'none'}}>YES</span> : <span style={{color:'var(--tx-3)'}}>NO</span>],
          ['RSI',         <span style={{color: signal.rsi > 70 ? 'var(--r1)' : signal.rsi < 30 ? 'var(--cyan)' : 'var(--tx-0)'}}>{signal.rsi?.toFixed(1)}</span>],
          ['ADX',         <span style={{color: signal.adx > 25 ? 'var(--g1)' : 'var(--tx-1)'}}>{signal.adx?.toFixed(1)}</span>],
          ['Confidence',  <span style={{color:'var(--amber)'}}>{signal.confidence}/10</span>],
          ['Quality',     <span style={{color:'var(--tx-0)'}}>{signal.quality}/15</span>],
        ].map(([l, v]) => (
          <div key={l} className="ind-row">
            <span className="ind-lbl">{l}</span>
            <span className="ind-val">{v}</span>
          </div>
        ))}
      </div>

      {signal.price && (
        <div className="entry-grid">
          {[
            ['Entry',    signal.price,     'var(--tx-0)'],
            ['Stop Loss',signal.stop_loss, 'var(--r2)'],
            ['TP1',      signal.tp1,       'var(--g1)'],
            ['TP2',      signal.tp2,       'var(--g2)'],
          ].map(([l, v, c]) => (
            <div key={l} className="entry-box">
              <div className="entry-lbl">{l}</div>
              <div className="entry-val" style={{ color: c }}>{fmtPrice(v)}</div>
            </div>
          ))}
        </div>
      )}

      {signal.reasons?.length > 0 && (
        <div className="reasons-list">
          {signal.reasons.slice(0, 4).map((r, i) => (
            <div key={i} className="reason-item">{r}</div>
          ))}
        </div>
      )}
    </div>
  )
}

export default function StatsPanel({ signals = [], selectedSignal, onCloseDetail }) {
  const bull  = signals.filter(s => parseInt(s.bb_rating) > 0).length
  const bear  = signals.filter(s => parseInt(s.bb_rating) < 0).length
  const neu   = signals.filter(s => parseInt(s.bb_rating) === 0).length
  const sqz   = signals.filter(s => s.bbw < 0.03).length

  const ratings = [3, 2, 1, 0, -1, -2, -3]
  const counts  = ratings.map(r => signals.filter(s => parseInt(s.bb_rating) === r).length)
  const maxC    = Math.max(...counts, 1)

  const topBull = [...signals]
    .filter(s => parseInt(s.bb_rating) >= 2 && s.direction === 'LONG')
    .sort((a, b) => b.confidence - a.confidence)
    .slice(0, 5)

  const topBear = [...signals]
    .filter(s => parseInt(s.bb_rating) <= -2 && s.direction === 'SHORT')
    .sort((a, b) => b.confidence - a.confidence)
    .slice(0, 4)

  return (
    <div className="right-panel">
      {/* Detail card */}
      {selectedSignal && (
        <DetailCard signal={selectedSignal} onClose={onCloseDetail} />
      )}

      {/* Overview */}
      <div className="r-section">
        <div className="r-title">Market Overview</div>
        <div className="stat-grid">
          <div className="stat-card sc-bull"><div className="stat-lbl">Bullish</div><div className="stat-val">{bull}</div></div>
          <div className="stat-card sc-bear"><div className="stat-lbl">Bearish</div><div className="stat-val">{bear}</div></div>
          <div className="stat-card sc-neu"> <div className="stat-lbl">Neutral</div><div className="stat-val">{neu}</div></div>
          <div className="stat-card sc-sqz"> <div className="stat-lbl">Squeezing</div><div className="stat-val">{sqz}</div></div>
        </div>
      </div>

      {/* Distribution */}
      {signals.length > 0 && (
        <div className="r-section">
          <div className="r-title">BB Rating Distribution</div>
          {ratings.map((r, i) => (
            <div key={r} className="dist-row">
              <span className={`dist-lbl ${rClass(r)}`}>{r > 0 ? `+${r}` : r}</span>
              <div className="dist-track">
                <div className="dist-fill" style={{ width: `${counts[i] / maxC * 100}%`, background: ratingColor(r) }} />
              </div>
              <span className="dist-cnt">{counts[i]}</span>
            </div>
          ))}
        </div>
      )}

      {/* Top LONG */}
      <div className="r-section">
        <div className="r-title">Top LONG Signals</div>
        {topBull.length > 0 ? (
          <div className="sig-list">
            {topBull.map(s => {
              const sym = s.symbol || ''
              const base = sym.replace(/USDT$|BTC$|ETH$/, '')
              const r = parseInt(s.bb_rating)
              return (
                <div key={sym} className="sig-item">
                  <div>
                    <div className="sig-sym">{base}/{sym.slice(base.length)}</div>
                    <div className="sig-meta">{s.bbw < 0.03 ? 'SQZ · ' : ''}BBW {(s.bbw*100).toFixed(2)}%</div>
                  </div>
                  <span className="sig-score" style={{ color: ratingColor(r) }}>+{r}</span>
                </div>
              )
            })}
          </div>
        ) : <div style={{ color: 'var(--tx-3)', fontSize: 10, letterSpacing: 1 }}>No LONG signals</div>}
      </div>

      {/* Top SHORT */}
      <div className="r-section">
        <div className="r-title">Top SHORT Signals</div>
        {topBear.length > 0 ? (
          <div className="sig-list">
            {topBear.map(s => {
              const sym = s.symbol || ''
              const base = sym.replace(/USDT$|BTC$|ETH$/, '')
              const r = parseInt(s.bb_rating)
              return (
                <div key={sym} className="sig-item">
                  <div>
                    <div className="sig-sym">{base}/{sym.slice(base.length)}</div>
                    <div className="sig-meta">BBW {(s.bbw*100).toFixed(2)}%</div>
                  </div>
                  <span className="sig-score" style={{ color: ratingColor(r) }}>{r}</span>
                </div>
              )
            })}
          </div>
        ) : <div style={{ color: 'var(--tx-3)', fontSize: 10, letterSpacing: 1 }}>No SHORT signals</div>}
      </div>
    </div>
  )
}
