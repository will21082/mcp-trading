import React from 'react'
import './ScanButton.css'

function ScanButton({ isScanning, onScan }) {
  return (
    <div className="scan-button-container">
      <button
        className={`scan-button ${isScanning ? 'scanning' : ''}`}
        onClick={onScan}
        disabled={isScanning}
      >
        {isScanning ? (
          <>
            <span className="spinner spin">⏳</span>
            Scanning Market...
          </>
        ) : (
          <>
            <span className="emoji">🔍</span>
            Scan Now
          </>
        )}
      </button>

      {isScanning && (
        <p className="scan-status pulse">
          Analyzing 84 coins on Bybit... This may take 30-60 seconds
        </p>
      )}
    </div>
  )
}

export default ScanButton
