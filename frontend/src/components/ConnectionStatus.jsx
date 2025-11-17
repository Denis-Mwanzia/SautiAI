import { useState, useEffect } from 'react'
import { Wifi, WifiOff, Activity } from 'lucide-react'
import { useToast } from '../contexts/ToastContext'

export default function ConnectionStatus() {
  const [isOnline, setIsOnline] = useState(navigator.onLine)
  const [wsConnected, setWsConnected] = useState(false)
  const toast = useToast()

  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true)
      toast.success('Connection restored')
    }

    const handleOffline = () => {
      setIsOnline(false)
      toast.error('Connection lost. Please check your internet.')
    }

    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)

    // Check WebSocket connection (if implemented)
    // For now, simulate based on API health
    const checkConnection = async () => {
      try {
        const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/health`)
        setWsConnected(response.ok)
      } catch {
        setWsConnected(false)
      }
    }

    const interval = setInterval(checkConnection, 30000) // Check every 30s
    checkConnection()

    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
      clearInterval(interval)
    }
  }, [toast])

  if (isOnline && wsConnected) return null // Don't show if everything is fine

  return (
    <div
      className="fixed bottom-4 right-4 z-50 bg-white rounded-lg shadow-lg border-2 p-3 flex items-center gap-2 animate-slide-up"
      role="status"
      aria-live="polite"
    >
      {!isOnline ? (
        <>
          <WifiOff className="h-5 w-5 text-red-500" />
          <span className="text-sm font-medium text-gray-700">Offline</span>
        </>
      ) : !wsConnected ? (
        <>
          <Activity className="h-5 w-5 text-yellow-500 animate-pulse" />
          <span className="text-sm font-medium text-gray-700">Connecting...</span>
        </>
      ) : null}
    </div>
  )
}

