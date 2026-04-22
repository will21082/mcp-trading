import { useState, useRef, useEffect } from 'react'
import { api } from '../api'

function drawEquity(canvas, curve) {
  if (!canvas || !curve?.length) return
  const W = canvas.parentElement?.clientWidth || 280
  canvas.width  = W
  canvas.height = 70
  const ctx = canvas.getContext('2d')
  const H = 70, pad = 4
  ctx.clearRect(0, 0, W, H)

  const mn = Math.min(...curve), mx = Math.max(...curve)
  const tx = i => pad + (i / (curve.length - 1)) * (W - pad * 2)
  const ty = v => H - pad - ((v - mn) / (mx - mn || 1)) * (H - pad * 2)

  const grad = ctx.createLinearGradient(0, 0, 0, H)
  grad.addColorStop(0, 'rgba(0,217,124,.25)')
  grad.addColorStop(1, 'rgba(0,217,124,0)')

  ctx.beginPath()
  ctx.moveTo(tx(0), ty(curve[0]))
  curve.forEach((v, i) => i > 0 && ctx.lineTo(tx(i), ty(v)))
  ctx.lineTo(tx(curve.length - 1), H)
  ctx.lineTo(tx(0), H)
  ctx.closePath()
  ctx.fillStyle = grad; ctx.fill()

  ctx.beginPath()
  ctx.moveTo(tx(0), ty(curve[0]))
  curve.forEach((v, i) => i > 0 && ctx.lineTo(tx(i), ty(v)))
  ctx.strokeStyle = '#00d97c'; ctx.lineWidth = 1.5; ctx.stroke()
}

export default function BacktestPanel() {
  const [days,    setDays]    = useState(30)
  const [capital, setCapital] = useState(10000)
  const [risk,    setRisk]    = useState(1.0)
  const [minConf, setMinConf] = useState(6)
  const [result,  setResult]  = useState(null)
  const [running, setRunning] = useState(false)
  const canvasRef = useRef(null)

  useEffect(() => {
    if (result?.equity_curve) drawEquity(canvasRef.current, result.equity_curve)
  }, [result])

  async function run() {
    setRunning(true)
    try {
      const r = await api.backtest({ days, capital, risk_pct: risk, min_confidence: minConf })
      setResult(r)
    } catch (e) {
      console.error(e)
    } finally {
      setRunning(false)
    }
  }

  return (
    <>
      {/* Left: trade history */}
      <div className="left-panel">
        <div className="panel-head">
          <span className="panel-title">Trade History</span>
          <span className="panel-count">{result ? `${result.n_trades} trades · ${result.days}d` : '—'}</span>
        </div>
        <div className="bt-history-area">
          {!result ? (
            <div className="empty">
              <div className="empty-icon">⟲</div>
              <span>Configure and run backtest</span>
            </div>
          ) : (
            <>
              <div className="bt-htitle">Recent 25 Trades</div>
              <table>
                <thead>
                  <tr>
                    <th>Days Ago</th>
                    <th>Symbol</th>
                    <th>Direction</th>
                    <th>PnL %</th>
                    <th>Result</th>
                  </tr>
                </thead>
                <tbody>
                  {result.trades.map((t, i) => (
                    <tr key={i}>
                      <td style={{ color: 'var(--tx-2)', fontSize: 10 }}>{t.days_ago}d</td>
                      <td><span className="sym" style={{ fontSize: 10 }}>{t.symbol}</span></td>
                      <td>
                        <span className={`dir-badge ${t.direction === 'LONG' ? 'dir-long' : 'dir-short'}`}>
                          {t.direction}
                        </span>
                      </td>
                      <td style={{ color: t.result === 'WIN' ? 'var(--g2)' : 'var(--r2)', fontWeight: 500, fontSize: 10 }}>
                        {t.pnl_pct > 0 ? '+' : ''}{t.pnl_pct}%
                      </td>
                      <td>
                        <span style={{
                          fontFamily: 'var(--fd)', fontSize: 8, letterSpacing: 1,
                          padding: '1px 5px', border: `1px solid ${t.result === 'WIN' ? 'var(--g2)' : 'var(--r2)'}`,
                          color: t.result === 'WIN' ? 'var(--g2)' : 'var(--r2)',
                        }}>{t.result}</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </>
          )}
        </div>
      </div>

      {/* Right: config + results */}
      <div className="right-panel">
        <div className="r-section">
          <div className="r-title">Configuration</div>
          <div className="bt-form">
            <div className="bt-row"><span className="bt-lbl">Days</span><input type="number" value={days}    min="7"   max="365" onChange={e => setDays(+e.target.value)}    /></div>
            <div className="bt-row"><span className="bt-lbl">Capital</span><input type="number" value={capital} step="1000" onChange={e => setCapital(+e.target.value)} /><span className="bt-unit">USDT</span></div>
            <div className="bt-row"><span className="bt-lbl">Risk %</span><input type="number" value={risk}    min="0.5" max="5"   step="0.5" onChange={e => setRisk(+e.target.value)}    /></div>
            <div className="bt-row"><span className="bt-lbl">Min Conf</span><input type="number" value={minConf} min="4"   max="10" onChange={e => setMinConf(+e.target.value)} /></div>
            <button className={`bt-run-btn ${running ? 'running' : ''}`} onClick={run} disabled={running}>
              {running ? '● RUNNING...' : '▶ RUN BACKTEST'}
            </button>
          </div>
        </div>

        {result && (
          <div className="r-section">
            <div className="r-title">Performance</div>
            {[
              ['Total Return',   `+${result.total_return_pct}%`,         result.total_return_pct >= 0 ? 'var(--g2)' : 'var(--r2)'],
              ['Win Rate',       `${result.win_rate_pct}%`,               'var(--g1)'],
              ['Max Drawdown',   `${result.max_drawdown_pct}%`,           'var(--r2)'],
              ['Sharpe Ratio',   result.sharpe,                           'var(--cyan)'],
              ['Profit Factor',  result.profit_factor,                    'var(--tx-0)'],
              ['Total Trades',   result.n_trades,                         'var(--tx-0)'],
              ['Final Equity',   `$${result.final_equity.toLocaleString('en',{maximumFractionDigits:0})}`, 'var(--amber)'],
            ].map(([l, v, c]) => (
              <div key={l} className="perf-row">
                <span className="perf-lbl">{l}</span>
                <span className="perf-val" style={{ color: c }}>{v}</span>
              </div>
            ))}
            <div className="equity-lbl">EQUITY CURVE</div>
            <canvas ref={canvasRef} className="equity-canvas" />
          </div>
        )}
      </div>
    </>
  )
}
