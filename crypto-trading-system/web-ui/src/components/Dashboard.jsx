import React from 'react'
import './Dashboard.css'

function Dashboard({ scanData }) {
  if (!scanData) return null

  const successRate = scanData.coins_scanned > 0
    ? Math.round((scanData.total_signals / scanData.coins_scanned) * 100)
    : 0

  return (
    <section className="dashboard fade-in">
      <div className="stat-card">
        <div className="stat-icon">🕐</div>
        <div className="stat-content">
          <div className="stat-label">Last Scan</div>
          <div className="stat-value">{scanData.scan_time}</div>
        </div>
      </div>

      <div className="stat-card">
        <div className="stat-icon">🪙</div>
        <div className="stat-content">
          <div className="stat-label">Coins Scanned</div>
          <div className="stat-value">{scanData.coins_scanned}</div>
        </div>
      </div>

      <div className="stat-card success">
        <div className="stat-icon">🟢</div>
        <div className="stat-content">
          <div className="stat-label">LONG Signals</div>
          <div className="stat-value">{scanData.long_count}</div>
        </div>
      </div>

      <div className="stat-card danger">
        <div className="stat-icon">🔴</div>
        <div className="stat-content">
          <div className="stat-label">SHORT Signals</div>
          <div className="stat-value">{scanData.short_count}</div>
        </div>
      </div>

      <div className="stat-card highlight">
        <div className="stat-icon">🎯</div>
        <div className="stat-content">
          <div className="stat-label">Total Signals</div>
          <div className="stat-value">{scanData.total_signals}</div>
        </div>
      </div>

      <div className="stat-card">
        <div className="stat-icon">📊</div>
        <div className="stat-content">
          <div className="stat-label">Success Rate</div>
          <div className="stat-value">{successRate}%</div>
        </div>
      </div>
    </section>
  )
}

export default Dashboard
