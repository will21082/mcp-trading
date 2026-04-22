import React, { useState, useEffect } from 'react'
import axios from 'axios'
import Dashboard from './components/Dashboard'
import ScanButton from './components/ScanButton'
import ResultsTable from './components/ResultsTable'
import './App.css'

const API_BASE = 'http://localhost:5000/api'

function App() {
  const [scanData, setScanData] = useState(null)
  const [isScanning, setIsScanning] = useState(false)
  const [error, setError] = useState(null)
  const [config, setConfig] = useState(null)

  // Load configuration on mount
  useEffect(() => {
    loadConfig()
    loadLatestResults()
  }, [])

  const loadConfig = async () => {
    try {
      const response = await axios.get(`${API_BASE}/config`)
      setConfig(response.data)
    } catch (err) {
      console.error('Failed to load config:', err)
    }
  }

  const loadLatestResults = async () => {
    try {
      const response = await axios.get(`${API_BASE}/results/latest`)
      if (response.data.success) {
        setScanData(response.data.data)
      }
    } catch (err) {
      console.log('No previous results available')
    }
  }

  const handleScan = async () => {
    setIsScanning(true)
    setError(null)

    try {
      const response = await axios.post(`${API_BASE}/scan`)

      if (response.data.success) {
        setScanData(response.data.data)
      } else {
        setError(response.data.message)
      }
    } catch (err) {
      setError(err.response?.data?.message || err.message || 'Scan failed')
    } finally {
      setIsScanning(false)
    }
  }

  return (
    <div className="app">
      <header className="header">
        <div className="header-content">
          <h1 className="title">
            <span className="emoji">🚀</span>
            Crypto Trading Scanner
          </h1>
          <p className="subtitle">Bybit Breakout Strategy - 15m Timeframe</p>
        </div>
      </header>

      <main className="main-content">
        {/* Scan Control */}
        <section className="scan-section">
          <ScanButton
            isScanning={isScanning}
            onScan={handleScan}
          />
          {error && (
            <div className="error-message fade-in">
              <span className="emoji">⚠️</span>
              {error}
            </div>
          )}
        </section>

        {/* Dashboard Stats */}
        {scanData && (
          <Dashboard
            scanData={scanData}
            config={config}
          />
        )}

        {/* Results Table */}
        {scanData && scanData.signals && scanData.signals.length > 0 && (
          <ResultsTable signals={scanData.signals} />
        )}

        {/* No Results Message */}
        {scanData && scanData.signals && scanData.signals.length === 0 && (
          <div className="no-results fade-in">
            <span className="emoji large">💤</span>
            <h3>No Signals Found</h3>
            <p>This might be during a dead zone (01:00-08:00 UTC).</p>
            <p>Best scanning times:</p>
            <ul>
              <li>🌍 17:00 JST (08:00 UTC) - EU Open</li>
              <li>🇺🇸 21:00 JST (12:00 UTC) - US Open ⭐ BEST!</li>
              <li>🇺🇸 01:00 JST (16:00 UTC) - US Peak</li>
            </ul>
          </div>
        )}

        {/* Strategy Info */}
        {config && (
          <section className="strategy-info fade-in">
            <h3>📊 Strategy Configuration</h3>
            <div className="strategy-grid">
              <div className="strategy-item">
                <strong>Exchange:</strong> {config.exchange}
              </div>
              <div className="strategy-item">
                <strong>Timeframe:</strong> {config.timeframe}
              </div>
              <div className="strategy-item">
                <strong>TP1:</strong> {config.exit_strategy.tp1}
              </div>
              <div className="strategy-item">
                <strong>TP2:</strong> {config.exit_strategy.tp2}
              </div>
              <div className="strategy-item">
                <strong>Stop Loss:</strong> {config.exit_strategy.stop_loss}
              </div>
              <div className="strategy-item">
                <strong>Max Hold:</strong> {config.exit_strategy.max_hold}
              </div>
              <div className="strategy-item">
                <strong>Win Rate:</strong> {config.expected_win_rate}
              </div>
              <div className="strategy-item">
                <strong>Signals/Day:</strong> {config.expected_signals}
              </div>
            </div>

            <div className="schedule">
              <strong>🕐 Auto-Scan Schedule:</strong>
              <ul>
                {config.scan_schedule.map((time, idx) => (
                  <li key={idx}>{time}</li>
                ))}
              </ul>
            </div>
          </section>
        )}
      </main>

      <footer className="footer">
        <p>
          Crypto Trading System v2.0 - Optimized Exit Strategy (70% at TP1, 6h max)
        </p>
      </footer>
    </div>
  )
}

export default App
