import { useRef } from 'react'

const pendingRequests = new Map()

/**
 * Hook for deduplicating concurrent API requests
 * Prevents multiple identical requests from being made simultaneously
 */
export function useRequestDeduplication() {
  const dedupeRequest = async (key, requestFn) => {
    // If request is already pending, return the existing promise
    if (pendingRequests.has(key)) {
      return pendingRequests.get(key)
    }
    
    // Create new request promise
    const promise = requestFn()
      .then(result => {
        pendingRequests.delete(key)
        return result
      })
      .catch(error => {
        pendingRequests.delete(key)
        throw error
      })
    
    // Store promise for deduplication
    pendingRequests.set(key, promise)
    return promise
  }
  
  return { dedupeRequest }
}

