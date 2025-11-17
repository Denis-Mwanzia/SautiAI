import { createContext, useContext, useEffect, useState } from 'react'
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Missing Supabase environment variables')
}

const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: true
  }
})

// Export singleton for non-React modules (e.g., API interceptors)
export { supabase }

const AuthContext = createContext({})

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let mounted = true
    let initialSessionHandled = false

    // Listen for auth changes FIRST - this catches OAuth callbacks
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((event, session) => {
      if (!mounted) return

      // Debug log removed for production cleanliness

      // Always update user state
      setUser(session?.user ?? null)

      // Handle INITIAL_SESSION - this fires when Supabase loads/processes session
      if (event === 'INITIAL_SESSION') {
        initialSessionHandled = true
        setLoading(false)
        // Clean URL hash if present (OAuth callback)
        if (window.location.hash) {
          setTimeout(() => {
            window.history.replaceState(null, '', window.location.pathname)
          }, 100)
        }
        return
      }

      // Handle SIGNED_IN (OAuth or regular login)
      if (event === 'SIGNED_IN') {
        setLoading(false)
        // Clean URL hash after OAuth
        if (window.location.hash) {
          setTimeout(() => {
            window.history.replaceState(null, '', window.location.pathname)
          }, 100)
        }
        return
      }

      // Handle SIGNED_OUT
      if (event === 'SIGNED_OUT') {
        setLoading(false)
        return
      }
    })

    // Get initial session - this will trigger INITIAL_SESSION event
    supabase.auth.getSession().then(({ data: { session }, error }) => {
      if (!mounted) return
      
      if (error) {
        console.error('Error getting session:', error)
        if (!initialSessionHandled) {
          setLoading(false)
        }
        return
      }

      // If we got a session but INITIAL_SESSION hasn't fired yet, set it
      if (session && !initialSessionHandled) {
        setUser(session.user)
        setLoading(false)
      }
    })

    return () => {
      mounted = false
      subscription.unsubscribe()
    }
  }, [])

  const signIn = async (email, password) => {
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password,
    })
    if (error) throw error
    return data
  }

  const signUp = async (email, password) => {
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
    })
    if (error) throw error
    return data
  }

  const signOut = async () => {
    const { error } = await supabase.auth.signOut()
    if (error) throw error
  }

  const signInWithGoogle = async () => {
    const { data, error } = await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: {
        redirectTo: `${window.location.origin}/`,
      },
    })
    if (error) throw error
    return data
  }

  const value = {
    user,
    loading,
    signIn,
    signUp,
    signOut,
    signInWithGoogle,
    supabase,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
