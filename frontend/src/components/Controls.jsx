const EXCHANGES  = ['bybit','binance','kucoin','okx','coinbase','gateio','huobi','all']
const TIMEFRAMES = ['5m','15m','1h','4h','1D','1W']
const STRATEGIES = ['breakout','squeeze','reversal']

export default function Controls({ exchange, timeframe, strategy, onExch, onTF, onStrat, onScan, isScanning, showStrat }) {
  return (
    <div className="controls">
      <span className="ctrl-lbl">Exchange</span>
      <div className="sel-wrap">
        <select value={exchange} onChange={e => onExch(e.target.value)}>
          {EXCHANGES.map(e => <option key={e} value={e}>{e.toUpperCase()}</option>)}
        </select>
        <span className="sel-arr">▼</span>
      </div>

      <div className="ctrl-sep" />

      <span className="ctrl-lbl">Timeframe</span>
      <div className="tf-group">
        {TIMEFRAMES.map(tf => (
          <button key={tf} className={`tf-btn ${timeframe === tf ? 'active' : ''}`} onClick={() => onTF(tf)}>
            {tf.toUpperCase()}
          </button>
        ))}
      </div>

      {showStrat && <>
        <div className="ctrl-sep" />
        <span className="ctrl-lbl">Strategy</span>
        <div className="strat-group">
          {STRATEGIES.map(s => (
            <button key={s} className={`strat-btn ${strategy === s ? 'active' : ''}`} onClick={() => onStrat(s)}>
              {s.toUpperCase()}
            </button>
          ))}
        </div>
      </>}

      <button className={`scan-btn ${isScanning ? 'running' : ''}`} onClick={onScan} disabled={isScanning}>
        {isScanning ? '● SCANNING' : '▶ SCAN'}
      </button>
    </div>
  )
}
