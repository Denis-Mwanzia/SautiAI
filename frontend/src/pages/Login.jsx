import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { useToast } from '../contexts/ToastContext'
import { AlertTriangle, CheckCircle2, XCircle, Eye, EyeOff } from 'lucide-react'

const ENABLE_GOOGLE = import.meta.env.VITE_ENABLE_GOOGLE_AUTH === 'true'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [isSignUp, setIsSignUp] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [emailError, setEmailError] = useState('')
  const { user, loading: authLoading, signIn, signUp, signInWithGoogle } = useAuth()
  const toast = useToast()
  const navigate = useNavigate()
  const [googleLoading, setGoogleLoading] = useState(false)

  useEffect(() => {
    if (!authLoading && user) {
      navigate('/', { replace: true })
    }
  }, [user, authLoading, navigate])

  const getPasswordStrength = (pwd) => {
    if (!pwd) return { strength: 0, label: '', color: '' }
    let strength = 0
    if (pwd.length >= 8) strength++
    if (pwd.length >= 12) strength++
    if (/[a-z]/.test(pwd) && /[A-Z]/.test(pwd)) strength++
    if (/\d/.test(pwd)) strength++
    if (/[^a-zA-Z\d]/.test(pwd)) strength++
    
    const levels = [
      { label: 'Very Weak', color: 'bg-red-500' },
      { label: 'Weak', color: 'bg-orange-500' },
      { label: 'Fair', color: 'bg-yellow-500' },
      { label: 'Good', color: 'bg-blue-500' },
      { label: 'Strong', color: 'bg-green-500' },
      { label: 'Very Strong', color: 'bg-green-600' }
    ]
    return { strength, ...levels[Math.min(strength, 5)] }
  }

  const passwordStrength = isSignUp ? getPasswordStrength(password) : null

  const validateEmail = (email) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!email) {
      setEmailError('')
      return false
    }
    if (!emailRegex.test(email)) {
      setEmailError('Please enter a valid email address')
      return false
    }
    setEmailError('')
    return true
  }

  const handleEmailChange = (e) => {
    const value = e.target.value
    setEmail(value)
    if (value) validateEmail(value)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setEmailError('')

    if (!validateEmail(email)) {
      setError('Please enter a valid email address')
      return
    }

    if (isSignUp && passwordStrength.strength < 2) {
      setError('Password is too weak. Please use at least 8 characters with a mix of letters and numbers.')
      return
    }

    setLoading(true)

    try {
      if (isSignUp) {
        await signUp(email, password)
        toast.success('Account created successfully! Please check your email for verification.')
      } else {
        await signIn(email, password)
      }
      navigate('/')
    } catch (err) {
      const errorMsg = err.message || 'Authentication failed'
      if (errorMsg.includes('Invalid login credentials')) {
        setError('Invalid email or password. Please check your credentials and try again.')
      } else if (errorMsg.includes('User already registered')) {
        setError('An account with this email already exists. Please sign in instead.')
        setIsSignUp(false)
      } else if (errorMsg.includes('Email not confirmed')) {
        setError('Please verify your email address before signing in. Check your inbox for the verification link.')
      } else if (errorMsg.includes('Password')) {
        setError('Password does not meet requirements. Please use at least 8 characters.')
      } else {
        setError(errorMsg)
      }
    } finally {
      setLoading(false)
    }
  }

  const handleGoogleSignIn = async () => {
    if (!ENABLE_GOOGLE) {
      setError('Google sign-in is disabled for this environment')
      return
    }
    setError('')
    setGoogleLoading(true)
    try {
      await signInWithGoogle?.()
    } catch (err) {
      const errorMsg = err?.message || 'Google sign-in failed'
      setError(errorMsg)
      toast.error('Failed to sign in with Google. Please use email & password.')
    } finally {
      setGoogleLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-50 via-white to-gray-50 p-4">
      <div className="max-w-md w-full glass-card p-8 relative">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gray-900 rounded-xl mb-4">
            <span className="text-2xl font-bold text-white">SA</span>
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Sauti AI
          </h1>
          <p className="text-gray-600 text-sm mb-1">Voice of the People</p>
          <p className="text-gray-500 text-xs">Civic Intelligence Platform</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 flex-shrink-0" />
              <span className="text-sm font-medium">{error}</span>
            </div>
          )}

          <div className="space-y-1.5">
            <label htmlFor="email" className="block text-sm font-medium text-gray-700">
              Email Address
            </label>
            <div className="relative">
              <input
                id="email"
                type="email"
                value={email}
                onChange={handleEmailChange}
                onBlur={() => validateEmail(email)}
                required
                aria-invalid={emailError ? 'true' : 'false'}
                aria-describedby={emailError ? 'email-error' : undefined}
                className={`w-full px-4 py-2.5 border rounded-lg focus:ring-2 focus:ring-gray-900/20 focus:border-gray-900 transition-all duration-200 outline-none bg-white text-sm ${
                  emailError ? 'border-red-300 focus:border-red-500' : 'border-gray-200'
                }`}
                placeholder="your@email.com"
                autoComplete="email"
              />
              {email && !emailError && (
                <CheckCircle2 className="absolute right-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-green-500" />
              )}
            </div>
            {emailError && (
              <p id="email-error" className="text-xs text-red-600 flex items-center gap-1" role="alert">
                <XCircle className="h-3 w-3" />
                {emailError}
              </p>
            )}
          </div>

          <div className="space-y-1.5">
            <label htmlFor="password" className="block text-sm font-medium text-gray-700">
              Password
              {isSignUp && (
                <span className="text-xs font-normal text-gray-500 ml-2">
                  (min. 8 characters)
                </span>
              )}
            </label>
            <div className="relative">
              <input
                id="password"
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full px-4 py-2.5 pr-12 border border-gray-200 rounded-lg focus:ring-2 focus:ring-gray-900/20 focus:border-gray-900 transition-all duration-200 outline-none bg-white text-sm"
                placeholder="••••••••"
                autoComplete={isSignUp ? 'new-password' : 'current-password'}
                aria-describedby={isSignUp ? 'password-strength' : undefined}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700 focus:outline-none"
                aria-label={showPassword ? 'Hide password' : 'Show password'}
              >
                {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            </div>
            {isSignUp && password && (
              <div id="password-strength" className="space-y-2">
                <div className="flex items-center gap-2">
                  <div className="flex-1 h-1.5 bg-gray-200 rounded-full overflow-hidden">
                    <div
                      className={`h-full transition-all duration-300 ${passwordStrength.color}`}
                      style={{ width: `${(passwordStrength.strength / 5) * 100}%` }}
                    />
                  </div>
                  <span className={`text-xs font-medium ${passwordStrength.strength >= 3 ? 'text-green-600' : passwordStrength.strength >= 2 ? 'text-yellow-600' : 'text-red-600'}`}>
                    {passwordStrength.label}
                  </span>
                </div>
                <div className="grid grid-cols-2 gap-2 text-xs text-gray-600">
                  <div className={`flex items-center gap-1 ${password.length >= 8 ? 'text-green-600' : ''}`}>
                    {password.length >= 8 ? <CheckCircle2 className="h-3 w-3" /> : <XCircle className="h-3 w-3" />}
                    At least 8 characters
                  </div>
                  <div className={`flex items-center gap-1 ${/[a-z]/.test(password) && /[A-Z]/.test(password) ? 'text-green-600' : ''}`}>
                    {/[a-z]/.test(password) && /[A-Z]/.test(password) ? <CheckCircle2 className="h-3 w-3" /> : <XCircle className="h-3 w-3" />}
                    Upper & lowercase
                  </div>
                  <div className={`flex items-center gap-1 ${/\d/.test(password) ? 'text-green-600' : ''}`}>
                    {/\d/.test(password) ? <CheckCircle2 className="h-3 w-3" /> : <XCircle className="h-3 w-3" />}
                    Contains number
                  </div>
                  <div className={`flex items-center gap-1 ${/[^a-zA-Z\d]/.test(password) ? 'text-green-600' : ''}`}>
                    {/[^a-zA-Z\d]/.test(password) ? <CheckCircle2 className="h-3 w-3" /> : <XCircle className="h-3 w-3" />}
                    Special character
                  </div>
                </div>
              </div>
            )}
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 px-4 bg-gray-900 text-white rounded-lg hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-gray-900/20 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 text-sm font-medium shadow-sm hover:shadow"
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Processing...
              </span>
            ) : (
              isSignUp ? 'Create Account' : 'Sign In'
            )}
          </button>
        </form>

        {ENABLE_GOOGLE && (
          <>
            <div className="relative my-6">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-200"></div>
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-white text-gray-500 text-xs">Or continue with</span>
              </div>
            </div>

            <button
              onClick={handleGoogleSignIn}
              disabled={googleLoading || loading}
              className="w-full flex items-center justify-center gap-2 px-4 py-2.5 border border-gray-200 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-900/20 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 bg-white text-gray-700 text-sm font-medium shadow-sm hover:shadow"
              aria-label="Sign in with Google"
            >
              {googleLoading ? (
                <>
                  <div className="w-4 h-4 border-2 border-gray-400 border-t-transparent rounded-full animate-spin" />
                  <span>Connecting...</span>
                </>
              ) : (
                <span>Continue with Google</span>
              )}
            </button>
          </>
        )}

        <div className="mt-6 text-center pt-6 border-t border-gray-200">
          <button
            onClick={() => setIsSignUp(!isSignUp)}
            className="text-sm text-gray-600 hover:text-gray-900 font-medium transition-colors"
          >
            {isSignUp
              ? 'Already have an account? Sign in'
              : "Don't have an account? Sign up"}
          </button>
        </div>
      </div>
    </div>
  )
}
