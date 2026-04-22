import React, { useState } from 'react'
import './ResultsTable.css'

function ResultsTable({ signals }) {
  const [filter, setFilter] = useState('ALL') // ALL, LONG, SHORT

  const filteredSignals = signals.filter(signal => {
    if (filter === 'ALL') return true
    return signal.direction === filter
  })

  const getQualityBadge = (score) => {
    if (score >= 12) return { class: 'exceptional', label: '⭐⭐⭐' }
    if (score >= 9) return { class: 'excellent', label: '⭐⭐' }
    if (score >= 8) return { class: 'good', label: '⭐' }
    return { class: 'skip', label: '❌' }
  }

  const formatPrice = (price) => {
    return price.toFixed(price < 1 ? 6 : 2)
  }

  return (
    <section className="results-section fade-in">
      <div className="results-header">
        <h2>📈 Trading Signals</h2>

        <div className="filter-buttons">
          <button
            className={filter === 'ALL' ? 'active' : ''}
            onClick={() => setFilter('ALL')}
          >
            All ({signals.length})
          </button>
          <button
            className={filter === 'LONG' ? 'active long' : ''}
            onClick={() => setFilter('LONG')}
          >
            🟢 LONG ({signals.filter(s => s.direction === 'LONG').length})
          </button>
          <button
            className={filter === 'SHORT' ? 'active short' : ''}
            onClick={() => setFilter('SHORT')}
          >
            🔴 SHORT ({signals.filter(s => s.direction === 'SHORT').length})
          </button>
        </div>
      </div>

      <div className="table-container">
        <table className="results-table">
          <thead>
            <tr>
              <th>#</th>
              <th>Symbol</th>
              <th>Direction</th>
              <th>Entry</th>
              <th>TP1 (70%)</th>
              <th>TP2 (30%)</th>
              <th>Stop Loss</th>
              <th>R:R</th>
              <th>Quality</th>
            </tr>
          </thead>
          <tbody>
            {filteredSignals.map((signal, idx) => {
              const badge = getQualityBadge(signal.quality_score)
              return (
                <tr key={idx} className={`signal-row ${signal.direction.toLowerCase()}`}>
                  <td className="rank">{signal.rank}</td>
                  <td className="symbol">{signal.symbol}</td>
                  <td className={`direction ${signal.direction.toLowerCase()}`}>
                    <span className="direction-badge">
                      {signal.direction === 'LONG' ? '🟢' : '🔴'} {signal.direction}
                    </span>
                  </td>
                  <td className="price">${formatPrice(signal.entry)}</td>
                  <td className="price tp1">${formatPrice(signal.tp1)}</td>
                  <td className="price tp2">${formatPrice(signal.tp2)}</td>
                  <td className="price sl">${formatPrice(signal.stop_loss)}</td>
                  <td className="rr">1:{signal.risk_reward}</td>
                  <td className="quality">
                    <span className={`quality-badge ${badge.class}`}>
                      {signal.quality_score}/15 {badge.label}
                    </span>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>

      <div className="exit-strategy-reminder">
        <h4>⚡ Exit Strategy Reminder:</h4>
        <ul>
          <li><strong>Hour 3-4:</strong> Close 70% at TP1, move SL to breakeven (0%)</li>
          <li><strong>Hour 4-6:</strong> Close remaining 30% at TP2</li>
          <li><strong>Hour 6+:</strong> FORCE CLOSE ALL (prevent reversal!)</li>
        </ul>
      </div>
    </section>
  )
}

export default ResultsTable
