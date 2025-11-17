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

  // Redirect if already logged in
  useEffect(() => {
    if (!authLoading && user) {
      navigate('/', { replace: true })
    }
  }, [user, authLoading, navigate])

  // Password strength checker
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

  // Email validation
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

    // Validate email
    if (!validateEmail(email)) {
      setError('Please enter a valid email address')
      return
    }

    // Validate password strength for sign up
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
      // Better error messages
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
      // Navigation handled by auth state
    } catch (err) {
      const errorMsg = err?.message || 'Google sign-in failed'
      setError(errorMsg)
      toast.error('Failed to sign in with Google. Please use email & password.')
    } finally {
      setGoogleLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 via-white to-primary-100 p-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-2xl p-8 animate-scale-in border border-gray-100">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-primary-500 to-primary-700 rounded-2xl mb-4 shadow-lg">
            <span className="text-2xl font-bold text-white">SA</span>
          </div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-primary-600 to-primary-800 bg-clip-text text-transparent mb-2">
            Sauti AI
          </h1>
          <p className="text-gray-600 font-medium">Voice of the People</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <div className="bg-red-50 border-l-4 border-red-500 text-red-700 px-4 py-3 rounded-lg animate-slide-up flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 flex-shrink-0" />
              <span className="text-sm font-medium">{error}</span>
            </div>
          )}

          <div className="space-y-2">
            <label htmlFor="email" className="block text-sm font-semibold text-gray-700">
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
                className={`w-full px-4 py-3 border-2 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-200 outline-none ${
                  emailError ? 'border-red-300 focus:border-red-500 focus:ring-red-200' : 'border-gray-200'
                }`}
                placeholder="your@email.com"
                autoComplete="email"
              />
              {email && !emailError && (
                <CheckCircle2 className="absolute right-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-green-500" />
              )}
            </div>
            {emailError && (
              <p id="email-error" className="text-sm text-red-600 flex items-center gap-1" role="alert">
                <XCircle className="h-4 w-4" />
                {emailError}
              </p>
            )}
          </div>

          <div className="space-y-2">
            <label htmlFor="password" className="block text-sm font-semibold text-gray-700">
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
                className="w-full px-4 py-3 pr-12 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-200 outline-none"
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
                {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
              </button>
            </div>
            {isSignUp && password && (
              <div id="password-strength" className="space-y-2">
                <div className="flex items-center gap-2">
                  <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
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
            className="w-full bg-gradient-to-r from-primary-600 to-primary-700 text-white py-3 px-4 rounded-xl hover:from-primary-700 hover:to-primary-800 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 font-semibold"
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Processing...
              </span>
            ) : (
              isSignUp ? 'Create Account' : 'Sign In'
            )}
          </button>
        </form>

        {ENABLE_GOOGLE && (
          <>
            {/* Divider */}
            <div className="relative my-6">
              <div className="absolute inset-0 pass flex items-center">
                <div className="w-full border-t border-gray-300"></div>
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-white text-gray-500">Or continue with</span>
              </div>
            </div>

            {/* Google Sign In Button */}
            <button
              onClick={handleGoogleSignIn}
              disabled={googleLoading || loading}
              className="w-full flex items-center justify-center gap-3 px-4 py-3 border-2 border-gray-300 rounded-xl hover:border-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 bg-white text-gray-700 font-semibold shadow-sm hover:shadow-md"
              aria-label="Sign in with Google"
            >
              {googleLoading ? (
                <>
                  <div className="w-5 h-5 border-2 border-gray-400 border-t-transparent rounded-full animate-spin" />
                  <span>Connecting...</span>
                </>
              ) : (
                <>
                  {/* Google icon intentionally omitted when disabled */}
                  <span>Continue with Google</span>
                </>
              )}
            </button>
          </>
        )}

        <div className="mt-6 text-center">
          <button
            onClick={() => setIsSignUp(!isSignUp)}
            className="text-sm text-primary-600 hover:text-primary-700 font-medium transition-colors"
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

