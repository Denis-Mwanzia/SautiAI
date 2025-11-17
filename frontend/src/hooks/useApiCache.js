import { useState, useCallback, useRef } from 'react'

const CACHE_DURATION = 5 * 60 * 1000 // 5 minutes

const cache = new Map()

export function useApiCache() {
  const getCached = useCallback((key) => {
    const cached = cache.get(key)
    if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
      return cached.data
    }
    cache.delete(key)
    return null
  }, [])

  const setCached = useCallback((key, data) => {
    cache.set(key, {
      data,
      timestamp: Date.now()
    })
  }, [])

  const clearCache = useCallback((key) => {
    if (key) {
      cache.delete(key)
    } else {
      cache.clear()
    }
  }, [])

  return { getCached, setCached, clearCache }
}

