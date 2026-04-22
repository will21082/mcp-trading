import { useState, useEffect } from 'react'

export default function Header({ backendOk }) {
  const [time, setTime] = useState('')

  useEffect(() => {
    const tick = () => {
      const d = new Date()
      setTime(d.toUTCString().split(' ')[4] + ' UTC')
    }
    tick()
    const id = setInterval(tick, 1000)
    return () => clearInterval(id)
  }, [])

  return (
    <header className="header">
      <div className="logo-wrap">
        <div className="logo-hex">◈</div>
        <div>
          <div className="logo-text">MCP TRADING</div>
          <div className="logo-sub">TERMINAL v2.0</div>
        </div>
      </div>

      <div className="hdr-center">
        <div className="hdr-stat">
          <div className={`hdr-dot ${backendOk ? 'live' : backendOk === false ? 'dead' : 'cyan'}`} />
          <span>{backendOk === null ? 'CONNECTING...' : backendOk ? 'BACKEND ONLINE' : 'BACKEND OFFLINE'}</span>
        </div>
        <div className="hdr-stat">
          <div className="hdr-dot cyan" />
          <span>TRADINGVIEW · BB SQUEEZE STRATEGY</span>
        </div>
      </div>

      <div className="clock">{time}</div>
    </header>
  )
}
