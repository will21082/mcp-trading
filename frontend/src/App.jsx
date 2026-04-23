import { useState, useEffect, useRef } from 'react'
import Header       from './components/Header.jsx'
import Controls     from './components/Controls.jsx'
import SignalTable  from './components/SignalTable.jsx'
import StatsPanel   from './components/StatsPanel.jsx'
import BacktestPanel from './components/BacktestPanel.jsx'
import { useScan }  from './hooks/useScan.js'

// ── trade setups helper ──────────────────────────────────────────────────────
function TradeTab({ signals }) {
  const longSetups = signals.filter(s => s.bbw < 0.05 && parseInt(s.bb_rating) >= 1 && s.direction === 'LONG' && s.confidence >= 5)
    .sort((a, b) => b.confidence - a.confidence)
  const shortSetups = signals.filter(s => s.bbw < 0.05 && parseInt(s.bb_rating) <= -1 && s.direction === 'SHORT' && s.confidence >= 5)
    .sort((a, b) => b.confidence - a.confidence)
  const setups = [...longSetups, ...shortSetups]

  function fmtP(p) {
    if (!p) return '—'
    return p >= 100 ? p.toFixed(2) : p >= 1 ? p.toFixed(4) : p.toFixed(6)
  }
  function rr(s) {
    if (!s.tp1 || !s.price || !s.stop_loss) return '—'
    if (s.direction === 'LONG')
      return ((s.tp1 - s.price) / (s.price - s.stop_loss)).toFixed(1) + 'R'
    return ((s.price - s.tp1) / (s.stop_loss - s.price)).toFixed(1) + 'R'
  }

  return (
    <>
      <div className="left-panel">
        <div className="panel-head">
          <span className="panel-title">Breakout Setups</span>
          <span className="panel-count">{longSetups.length} LONG · {shortSetups.length} SHORT</span>
        </div>
        <div className="tbl-scroll">
          <table>
            <thead>
              <tr>
                <th>Symbol</th><th>Dir</th><th>Confidence</th><th>Entry</th>
                <th>Stop Loss</th><th>TP1</th><th>TP2</th><th>R:R</th>
              </tr>
            </thead>
            <tbody>
              {setups.length === 0 ? (
                <tr><td colSpan={8}>
                  <div className="empty"><div className="empty-icon">◈</div><span>{signals.length === 0 ? 'Run scan first' : 'No setups match criteria'}</span></div>
                </td></tr>
              ) : setups.map((s, idx) => (
                <tr key={s.symbol + s.direction + idx}>
                  <td><span className="sym">{s.symbol?.replace(/USDT$/,'')}<span className="sym-q">/USDT</span></span></td>
                  <td><span className={`dir-badge ${s.direction === 'LONG' ? 'long' : 'short'}`}>{s.direction}</span></td>
                  <td>
                    <div className="conf-wrap">
                      {Array.from({length:10},(_,i)=><div key={i} className={`conf-dot ${i < s.confidence ? 'lit':''}`}/>)}
                      <span className="conf-num">{s.confidence}/10</span>
                    </div>
                  </td>
                  <td style={{ fontSize: 10, color: 'var(--tx-0)' }}>{fmtP(s.price)}</td>
                  <td style={{ fontSize: 10, color: 'var(--r2)' }}>{fmtP(s.stop_loss)}</td>
                  <td style={{ fontSize: 10, color: 'var(--g1)' }}>{fmtP(s.tp1)}</td>
                  <td style={{ fontSize: 10, color: 'var(--g2)' }}>{fmtP(s.tp2)}</td>
                  <td style={{ fontFamily: 'var(--fd)', fontSize: 11, fontWeight: 600, color: 'var(--cyan)' }}>{rr(s)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="right-panel">
        <div className="r-section">
          <div className="r-title">Strategy Info</div>
          <div style={{ fontSize: 10, color: 'var(--tx-2)', lineHeight: 1.8 }}>
            <div style={{ color: 'var(--purple)', fontFamily: 'var(--fd)', fontSize: 11, fontWeight: 600, letterSpacing: 2, marginBottom: 8 }}>BB SQUEEZE + BREAKOUT</div>
            Quét coin đang trong trạng thái squeeze (BBW &lt; 5%), BB Rating ≥ +1 (LONG) hoặc ≤ -1 (SHORT), confidence ≥ 5/10.
            Entry tại giá hiện tại, SL -3%, TP theo R:R 1.5/2.5/3.5.
          </div>
          <div className="strat-kpi">
            {[['WIN RATE','64%','var(--g2)'],['AVG R:R','2.5','var(--cyan)'],['MIN CONF','5/10','var(--amber)']].map(([l,v,c]) => (
              <div key={l} className="strat-kpi-card">
                <div className="skpi-lbl">{l}</div>
                <div className="skpi-val" style={{color:c}}>{v}</div>
              </div>
            ))}
          </div>
        </div>
        <div className="r-section">
          <div className="r-title">Exit Plan</div>
          {[
            ['TP1 (70%)', '+4.5% · đóng 70% vị thế'],
            ['TP2 (30%)', '+7.5% · đóng 30% còn lại'],
            ['Stop Loss', '-3% từ entry'],
            ['Max Hold',  '6h (15m/1h) · 48h (4h)'],
          ].map(([l,v]) => (
            <div key={l} className="perf-row">
              <span className="perf-lbl">{l}</span>
              <span style={{ fontSize: 10, color: 'var(--tx-1)' }}>{v}</span>
            </div>
          ))}
        </div>
      </div>
    </>
  )
}

// ── Toast ────────────────────────────────────────────────────────────────────
function useToast() {
  const [msg, setMsg]   = useState('')
  const [show, setShow] = useState(false)
  const timer = useRef(null)

  const toast = (m) => {
    setMsg(m); setShow(true)
    clearTimeout(timer.current)
    timer.current = setTimeout(() => setShow(false), 3200)
  }
  return [msg, show, toast]
}

// ── App ──────────────────────────────────────────────────────────────────────
export default function App() {
  const [tab,      setTab]      = useState('scan')
  const [exchange, setExchange] = useState('bybit')
  const [tf,       setTF]       = useState('15m')
  const [strategy, setStrategy] = useState('breakout')
  const [selected, setSelected] = useState(null)

  const { scanData, isScanning, error, backendOk, scan } = useScan()
  const [toastMsg, toastShow, showToast] = useToast()

  const signals = scanData?.signals ?? []

  async function handleScan() {
    const data = await scan({ exchanges: [exchange], timeframes: [tf, '1h', '4h'] })
    if (data) {
      if (data._from_cache) {
        showToast(data._notice || `Showing cached data (${data.total_signals} signals). Wait 30s before next scan.`)
      } else {
        showToast(`Scanned ${data.total_scanned} symbols · ${data.total_signals} signals found`)
      }
    }
  }

  useEffect(() => {
    if (error) showToast(`Error: ${error}`)
  }, [error])

  const tabBtns = [
    { id: 'scan',      icon: '⬡', label: 'SCAN' },
    { id: 'trade',     icon: '◈', label: 'TRADE SETUPS' },
    { id: 'backtest',  icon: '⟲', label: 'BACKTEST' },
  ]

  return (
    <>
      <Header backendOk={backendOk} />

      <nav className="nav">
        {tabBtns.map(t => (
          <button key={t.id} className={`nav-tab ${tab === t.id ? 'active' : ''}`} onClick={() => setTab(t.id)}>
            <span>{t.icon}</span> {t.label}
          </button>
        ))}
      </nav>

      <Controls
        exchange={exchange} timeframe={tf} strategy={strategy}
        onExch={setExchange} onTF={setTF} onStrat={setStrategy}
        onScan={handleScan}  isScanning={isScanning}
        showStrat={tab === 'trade'}
      />

      <div className="workspace">
        {backendOk === false && (
          <div className="backend-banner" style={{ gridColumn: '1/-1' }}>
            <div className="backend-title">⚠ BACKEND OFFLINE</div>
            <div className="backend-cmd">cd backend && pip install -r requirements.txt && uvicorn main:app --reload --port 8000</div>
            <div className="backend-hint">Frontend chạy trên port 5173 · Backend cần port 8000</div>
          </div>
        )}

        {tab === 'scan' && (
          <>
            <SignalTable
              signals={signals}
              selectedSymbol={selected?.symbol}
              onSelect={s => setSelected(s === selected ? null : s)}
              isLoading={isScanning}
            />
            <StatsPanel
              signals={signals}
              selectedSignal={selected}
              onCloseDetail={() => setSelected(null)}
            />
          </>
        )}

        {tab === 'trade' && <TradeTab signals={signals} />}

        {tab === 'backtest' && <BacktestPanel />}
      </div>

      {/* Footer */}
      <div className="footer">
        <div className="ft-item">EXCHANGE <span>{exchange.toUpperCase()}</span></div>
        <div className="ft-item">TF <span>{tf.toUpperCase()}</span></div>
        <div className="ft-item">SIGNALS <span>{signals.length}</span></div>
        {scanData?.scan_time && (
          <div className="ft-item">LAST SCAN <span>{new Date(scanData.scan_time).toLocaleTimeString()}</span></div>
        )}
        <div className="ft-item ft-right">
          BACKEND <span className="ft-live">{backendOk ? '●' : '○'}</span>
        </div>
      </div>

      {/* Toast */}
      <div className={`toast ${toastShow ? 'on' : ''}`}>{toastMsg}</div>
    </>
  )
}
