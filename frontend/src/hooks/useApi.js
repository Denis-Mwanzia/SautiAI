import { useState, useEffect, useCallback, useRef } from 'react'
import { useToast } from '../contexts/ToastContext'
import api from '../services/api'

/**
 * Custom hook for API calls with loading, error, and retry handling
 */
export function useApi(endpoint, options = {}) {
  const { immediate = true, method = 'GET', body = null, onSuccess, onError } = options
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(immediate)
  const [error, setError] = useState(null)
  const abortControllerRef = useRef(null)
  const toast = useToast()

  const execute = useCallback(async (retryCount = 0) => {
    // Cancel previous request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
    }

    // Create new abort controller
    abortControllerRef.current = new AbortController()

    setLoading(true)
    setError(null)

    try {
      let response
      const config = {
        signal: abortControllerRef.current.signal,
        ...options.config
      }

      switch (method.toUpperCase()) {
        case 'GET':
          response = await api.get(endpoint, config)
          break
        case 'POST':
          response = await api.post(endpoint, body, config)
          break
        case 'PUT':
          response = await api.put(endpoint, body, config)
          break
        case 'DELETE':
          response = await api.delete(endpoint, config)
          break
        default:
          response = await api.get(endpoint, config)
      }

      const result = response.data?.data || response.data
      setData(result)
      
      if (onSuccess) {
        onSuccess(result)
      }

      return result
    } catch (err) {
      // Don't set error if request was aborted
      if (err.name === 'AbortError' || err.code === 'ERR_CANCELED') {
        return
      }

      const errorMessage = err.response?.data?.detail || err.message || 'An error occurred'
      setError(errorMessage)

      // Auto-retry for network errors (max 2 retries)
      if (retryCount < 2 && (!err.response || err.response.status >= 500)) {
        await new Promise(resolve => setTimeout(resolve, 1000 * (retryCount + 1)))
        return execute(retryCount + 1)
      }

      if (onError) {
        onError(err)
      } else {
        toast.error(errorMessage)
      }

      throw err
    } finally {
      setLoading(false)
    }
  }, [endpoint, method, body, onSuccess, onError, toast, options.config])

  useEffect(() => {
    if (immediate) {
      execute()
    }

    // Cleanup: abort request on unmount
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort()
      }
    }
  }, [immediate, execute])

  const refetch = useCallback(() => {
    return execute()
  }, [execute])

  return { data, loading, error, refetch, execute }
}

