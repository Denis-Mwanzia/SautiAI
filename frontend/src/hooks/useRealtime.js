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
            // Only close if not already closed or closing
            if (wsRef.current.readyState !== WebSocket.CLOSED && wsRef.current.readyState !== WebSocket.CLOSING) {
            wsRef.current.onopen = null
            wsRef.current.onclose = null
            wsRef.current.onerror = null
            wsRef.current.onmessage = null
            if (wsRef.current.pingInterval) {
              clearInterval(wsRef.current.pingInterval)
            }
            wsRef.current.close()
            }
          } catch {}
          wsRef.current = null
        }

        // Don't create new connection if intentionally closed
        if (isIntentionallyClosedRef.current) {
          return
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
          
          // Don't reconnect if intentionally closed or in cleanup
          if (isIntentionallyClosedRef.current) {
            return
          }
          
          // Only reconnect if not intentionally closed and haven't exceeded max attempts
          if (reconnectAttemptsRef.current < maxReconnectAttempts) {
            reconnectAttemptsRef.current++
            // Exponential backoff: 5s, 10s, 20s
            const delay = Math.min(5000 * Math.pow(2, reconnectAttemptsRef.current - 1), 20000)
            reconnectTimeoutRef.current = setTimeout(() => {
              // Double-check we're not intentionally closed before reconnecting
              if (!isIntentionallyClosedRef.current) {
                connect()
              }
            }, delay)
          }
        }

        wsRef.current.onerror = (error) => {
          // Silently handle errors - they'll be handled by onclose
          // Don't log to avoid console spam, especially in React StrictMode
          // where double mounting causes expected connection closures
        }
      } catch (err) {
        // Only retry if we haven't exceeded max attempts and not intentionally closed
        if (!isIntentionallyClosedRef.current && reconnectAttemptsRef.current < maxReconnectAttempts) {
          reconnectAttemptsRef.current++
          const delay = Math.min(5000 * Math.pow(2, reconnectAttemptsRef.current - 1), 20000)
          reconnectTimeoutRef.current = setTimeout(() => {
            if (!isIntentionallyClosedRef.current) {
              connect()
            }
          }, delay)
      }
    }
    }

    // Initial connection attempt
    connect()

    return () => {
      isIntentionallyClosedRef.current = true
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
        reconnectTimeoutRef.current = null
      }
      if (wsRef.current) {
        if (wsRef.current.pingInterval) {
          clearInterval(wsRef.current.pingInterval)
          wsRef.current.pingInterval = null
        }
        try {
          // Remove event handlers first to prevent reconnection attempts
          wsRef.current.onopen = null
          wsRef.current.onclose = null
          wsRef.current.onerror = null
          wsRef.current.onmessage = null
          // Only close if not already closed or closing
          if (wsRef.current.readyState !== WebSocket.CLOSED && wsRef.current.readyState !== WebSocket.CLOSING) {
          wsRef.current.close()
          }
        } catch {}
        wsRef.current = null
      }
    }
  }, [onUpdate])

  return { connected, lastUpdateAt }
}
