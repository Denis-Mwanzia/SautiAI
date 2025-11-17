import { useEffect, useRef, useState } from 'react'

export function useRealtime(onUpdate) {
  const [connected, setConnected] = useState(false)
  const [lastUpdateAt, setLastUpdateAt] = useState(null)
  const wsRef = useRef(null)
  const reconnectTimeoutRef = useRef(null)
  const reconnectAttemptsRef = useRef(0)
  const maxReconnectAttempts = 3 // Limit retry attempts
  const isIntentionallyClosedRef = useRef(false)

  useEffect(() => {
    const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
    const wsUrl = apiUrl.replace('http', 'ws') + '/api/v1/realtime/stream'

    const connect = () => {
      // Don't reconnect if we've exceeded max attempts or intentionally closed
      if (reconnectAttemptsRef.current >= maxReconnectAttempts || isIntentionallyClosedRef.current) {
        return
      }

      // Don't create new connection if one already exists and is connecting/connected
      if (wsRef.current && (wsRef.current.readyState === WebSocket.CONNECTING || wsRef.current.readyState === WebSocket.OPEN)) {
        return
      }

      try {
        // Clean up any existing connection
        if (wsRef.current) {
          try {
            wsRef.current.onopen = null
            wsRef.current.onclose = null
            wsRef.current.onerror = null
            wsRef.current.onmessage = null
            if (wsRef.current.pingInterval) {
              clearInterval(wsRef.current.pingInterval)
            }
            wsRef.current.close()
          } catch {}
        }

        wsRef.current = new WebSocket(wsUrl)

        wsRef.current.onopen = () => {
          setConnected(true)
          reconnectAttemptsRef.current = 0 // Reset on successful connection
          // Keepalive ping every 25s
          wsRef.current.pingInterval = setInterval(() => {
            try {
              if (wsRef.current?.readyState === WebSocket.OPEN) {
                wsRef.current.send('ping')
              }
            } catch {}
          }, 25000)
        }

        wsRef.current.onmessage = (event) => {
          try {
            const payload = JSON.parse(event.data)
            if (payload?.type === 'update') {
              setLastUpdateAt(new Date())
              onUpdate?.(payload)
            }
          } catch {
            // ignore non-json messages
          }
        }

        wsRef.current.onclose = (event) => {
          setConnected(false)
          if (wsRef.current?.pingInterval) {
            clearInterval(wsRef.current.pingInterval)
            wsRef.current.pingInterval = null
          }
          
          // Only reconnect if not intentionally closed and haven't exceeded max attempts
          if (!isIntentionallyClosedRef.current && reconnectAttemptsRef.current < maxReconnectAttempts) {
            reconnectAttemptsRef.current++
            // Exponential backoff: 5s, 10s, 20s
            const delay = Math.min(5000 * Math.pow(2, reconnectAttemptsRef.current - 1), 20000)
            reconnectTimeoutRef.current = setTimeout(connect, delay)
          }
        }

        wsRef.current.onerror = (error) => {
          // Silently handle errors - they'll be handled by onclose
          // Don't log to avoid console spam
        }
      } catch (err) {
        // Only retry if we haven't exceeded max attempts
        if (reconnectAttemptsRef.current < maxReconnectAttempts) {
          reconnectAttemptsRef.current++
          const delay = Math.min(5000 * Math.pow(2, reconnectAttemptsRef.current - 1), 20000)
          reconnectTimeoutRef.current = setTimeout(connect, delay)
        }
      }
    }

    // Initial connection attempt
    connect()

    return () => {
      isIntentionallyClosedRef.current = true
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
      }
      if (wsRef.current) {
        if (wsRef.current.pingInterval) {
          clearInterval(wsRef.current.pingInterval)
        }
        try {
          wsRef.current.onopen = null
          wsRef.current.onclose = null
          wsRef.current.onerror = null
          wsRef.current.onmessage = null
          wsRef.current.close()
        } catch {}
      }
    }
  }, [onUpdate])

  return { connected, lastUpdateAt }
}
