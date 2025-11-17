import { useEffect, useRef, useCallback } from 'react'

/**
 * Custom hook for auto-refreshing data
 * @param {Function} fetchFunction - Function to call for refreshing data
 * @param {number} intervalMs - Refresh interval in milliseconds (default: 30000 = 30s)
 * @param {boolean} enabled - Whether auto-refresh is enabled (default: true)
 */
export function useAutoRefresh(fetchFunction, intervalMs = 30000, enabled = true) {
  const intervalRef = useRef(null)
  const isMountedRef = useRef(true)

  const refresh = useCallback(() => {
    if (isMountedRef.current && enabled) {
      fetchFunction()
    }
  }, [fetchFunction, enabled])

  useEffect(() => {
    isMountedRef.current = true

    if (enabled) {
      // Set up interval
      intervalRef.current = setInterval(refresh, intervalMs)

      // Cleanup on unmount
      return () => {
        isMountedRef.current = false
        if (intervalRef.current) {
          clearInterval(intervalRef.current)
        }
      }
    } else {
      // Clear interval if disabled
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }
  }, [refresh, intervalMs, enabled])

  return { refresh, isEnabled: enabled }
}

