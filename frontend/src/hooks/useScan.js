import { useState, useCallback, useEffect, useRef } from 'react'
import { api, WS_URL } from '../api'

export function useScan() {
  const [scanData,   setScanData]   = useState(null)
  const [isScanning, setIsScanning] = useState(false)
  const [error,      setError]      = useState(null)
  const [backendOk,  setBackendOk]  = useState(null)
  const [wsStatus,   setWsStatus]   = useState('disconnected')
  const wsRef = useRef(null)

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

  // WebSocket connection
  useEffect(() => {
    let ws = null
    let retryTimer = null

    function connect() {
      try {
        ws = new WebSocket(WS_URL)
        wsRef.current = ws

        ws.onopen = () => {
          setWsStatus('connected')
        }
        ws.onmessage = (e) => {
          try {
            const msg = JSON.parse(e.data)
            if (msg.type === 'scan_complete') {
              // Auto-refresh signals when scan completes from another source
              api.latestSignals().then(res => {
                if (res.success && res.data) setScanData(res.data)
              }).catch(() => {})
            }
          } catch {}
        }
        ws.onclose = () => {
          setWsStatus('disconnected')
          // Retry after 5s
          retryTimer = setTimeout(connect, 5000)
        }
        ws.onerror = () => {
          setWsStatus('error')
        }
      } catch {
        setWsStatus('error')
      }
    }

    connect()
    return () => {
      clearTimeout(retryTimer)
      if (ws) ws.close()
    }
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
      return null
    } finally {
      setIsScanning(false)
    }
  }, [])

  return { scanData, isScanning, error, backendOk, wsStatus, scan }
}

export function useMarketOverview() {
  const [overview, setOverview] = useState(null)
  const [loading,  setLoading]  = useState(false)

  const refresh = useCallback(async () => {
    setLoading(true)
    try {
      const data = await api.marketOverview()
      setOverview(data)
    } catch {}
    finally { setLoading(false) }
  }, [])

  useEffect(() => {
    refresh()
    const id = setInterval(refresh, 60000) // refresh every minute
    return () => clearInterval(id)
  }, [refresh])

  return { overview, loading, refresh }
}

export function useAlerts() {
  const [alerts,  setAlerts]  = useState([])
  const [loading, setLoading] = useState(false)

  const fetchAlerts = useCallback(async () => {
    try {
      const res = await api.getAlerts()
      setAlerts(res.alerts || [])
    } catch {}
  }, [])

  useEffect(() => { fetchAlerts() }, [fetchAlerts])

  const addAlert = useCallback(async (data) => {
    setLoading(true)
    try {
      await api.createAlert(data)
      await fetchAlerts()
    } catch {}
    finally { setLoading(false) }
  }, [fetchAlerts])

  const removeAlert = useCallback(async (id) => {
    try {
      await api.deleteAlert(id)
      setAlerts(prev => prev.filter(a => a.id !== id))
    } catch {}
  }, [])

  return { alerts, loading, addAlert, removeAlert, fetchAlerts }
}
