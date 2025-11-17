import axios from 'axios'
import { supabase as supabaseClient } from '../contexts/AuthContext'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: `${API_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor for adding auth tokens
api.interceptors.request.use(
  async (config) => {
    // Add auth token from shared Supabase client if available
    try {
      if (supabaseClient) {
        const { data: { session } } = await supabaseClient.auth.getSession()
        if (session?.access_token) {
          config.headers.Authorization = `Bearer ${session.access_token}`
        }
      }
    } catch (error) {
      // Silently fail if Supabase not available
      console.debug('Could not add auth token:', error)
    }

    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized
      window.location.href = '/login'
    } else if (error.response?.status >= 500) {
      // Server errors - could show toast here if needed
      console.error('Server error:', error.response?.data)
    } else if (error.code === 'ERR_NETWORK' || error.message === 'Network Error') {
      // Network errors
      console.error('Network error:', error.message)
    }
    return Promise.reject(error)
  }
)

export default api

