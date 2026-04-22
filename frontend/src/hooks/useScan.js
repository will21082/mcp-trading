import { useState, useCallback, useEffect } from 'react'
import { api } from '../api'

export function useScan() {
  const [scanData,   setScanData]   = useState(null)
  const [isScanning, setIsScanning] = useState(false)
  const [error,      setError]      = useState(null)
  const [backendOk,  setBackendOk]  = useState(null)   // null=unknown, true, false

  // Check backend + load cached data on mount
  useEffect(() => {
    api.health()
      .then(() => {
        setBackendOk(true)
        return api.latestSignals()
      })
      .then(res => { if (res.success && res.data) setScanData(res.data) })
      .catch(() => setBackendOk(false))
  }, [])

  const scan = useCallback(async ({ exchanges, timeframes, minConfidence = 5 }) => {
    setIsScanning(true)
    setError(null)
    try {
      const data = await api.scan({ exchanges, timeframes, min_confidence: minConfidence })
      setScanData(data)
      return data
    } catch (e) {
      setError(e.message)
    } finally {
      setIsScanning(false)
    }
  }, [])

  return { scanData, isScanning, error, backendOk, scan }
}
