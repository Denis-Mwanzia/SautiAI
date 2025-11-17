import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import ConnectionStatus from './ConnectionStatus'
import { 
  LayoutDashboard, 
  Bell, 
  Search, 
  Settings, 
  LogOut,
  Menu,
  X,
  MessageSquare,
  FileText,
  Shield,
  AlertTriangle
} from 'lucide-react'
import { useState } from 'react'

export default function Layout({ children }) {
  const { signOut } = useAuth()
  const location = useLocation()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  const navigation = [
    { name: 'Dashboard', href: '/', icon: LayoutDashboard },
    { name: 'Crisis Detection', href: '/crisis', icon: AlertTriangle },
    { name: 'Alerts', href: '/alerts', icon: Bell },
    { name: 'Feedback', href: '/feedback', icon: Search },
    { name: 'Chat', href: '/chat', icon: MessageSquare },
    { name: 'Reports', href: '/reports', icon: FileText },
    { name: 'Transparency', href: '/transparency', icon: Shield },
    { name: 'Settings', href: '/settings', icon: Settings },
  ]

  const handleSignOut = async () => {
    try {
      await signOut()
    } catch (error) {
      console.error('Error signing out:', error)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Skip to main content - Accessibility */}
      <a href="#main-content" className="skip-to-main">
        Skip to main content
      </a>
      
      {/* Mobile Header */}
      <div className="lg:hidden fixed top-0 left-0 right-0 bg-white shadow-md z-30 flex items-center justify-between p-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-700 rounded-xl flex items-center justify-center shadow-lg">
            <span className="text-white font-bold text-lg">SA</span>
          </div>
          <span className="text-xl font-bold bg-gradient-to-r from-primary-600 to-primary-800 bg-clip-text text-transparent">
            Sauti AI
          </span>
        </div>
        <button
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="p-2 rounded-lg hover:bg-gray-100"
          aria-label="Toggle menu"
        >
          {mobileMenuOpen ? (
            <X className="h-6 w-6 text-gray-600" />
          ) : (
            <Menu className="h-6 w-6 text-gray-600" />
          )}
        </button>
      </div>
      
      {/* Sidebar */}
      <div className="hidden lg:flex fixed inset-y-0 left-0 w-64 bg-white border-r border-gray-200 shadow-lg flex-col">
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center justify-between h-20 px-6 border-b border-gray-200 bg-gradient-to-r from-primary-50 to-white">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-700 rounded-xl flex items-center justify-center shadow-md">
                <span className="text-white font-bold text-lg">SA</span>
              </div>
              <h1 className="text-xl font-bold bg-gradient-to-r from-primary-600 to-primary-800 bg-clip-text text-transparent">
                Sauti AI
              </h1>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-6 space-y-2 overflow-y-auto">
            {navigation.map((item) => {
              const Icon = item.icon
              const isActive = location.pathname === item.href
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  aria-current={isActive ? 'page' : undefined}
                  className={`flex items-center px-4 py-3 text-sm font-semibold rounded-xl transition-all duration-200 group ${
                    isActive
                      ? 'bg-gradient-to-r from-primary-500 to-primary-600 text-white shadow-lg shadow-primary-200'
                      : 'text-gray-700 hover:bg-gray-100 hover:text-primary-600'
                  }`}
                >
                  <Icon className={`mr-3 h-5 w-5 transition-transform group-hover:scale-110 ${isActive ? 'text-white' : ''}`} />
                  {item.name}
                </Link>
              )
            })}
          </nav>

          {/* Sign Out */}
          <div className="p-4 border-t border-gray-200 bg-gray-50">
            <button
              onClick={handleSignOut}
              className="flex items-center w-full px-4 py-3 text-sm font-semibold text-gray-700 rounded-xl hover:bg-red-50 hover:text-red-600 transition-all duration-200 group"
            >
              <LogOut className="mr-3 h-5 w-5 transition-transform group-hover:scale-110" />
              Sign Out
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="lg:pl-64 pt-16 lg:pt-0">
        <main id="main-content" className="p-4 md:p-8 max-w-7xl mx-auto" role="main">{children}</main>
      </div>

      {/* Connection Status Indicator */}
      <ConnectionStatus />
      
      {/* Mobile Menu Overlay */}
      {mobileMenuOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={() => setMobileMenuOpen(false)}
        />
      )}
      
      {/* Mobile Sidebar */}
      <div
        className={`fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-xl transform transition-transform duration-300 ease-in-out lg:hidden ${
          mobileMenuOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="p-6 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-700 rounded-xl flex items-center justify-center shadow-lg">
                  <span className="text-white font-bold text-lg">SA</span>
                </div>
                <span className="text-xl font-bold bg-gradient-to-r from-primary-600 to-primary-800 bg-clip-text text-transparent">
                  Sauti AI
                </span>
              </div>
              <button
                onClick={() => setMobileMenuOpen(false)}
                className="lg:hidden p-2 rounded-lg hover:bg-gray-100"
              >
                <X className="h-6 w-6 text-gray-600" />
              </button>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-6 space-y-2 overflow-y-auto">
            {navigation.map((item) => {
              const Icon = item.icon
              const isActive = location.pathname === item.href
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  onClick={() => setMobileMenuOpen(false)}
                  className={`flex items-center px-4 py-3 text-sm font-semibold rounded-xl transition-all duration-200 group ${
                    isActive
                      ? 'bg-gradient-to-r from-primary-500 to-primary-600 text-white shadow-lg shadow-primary-200'
                      : 'text-gray-700 hover:bg-gray-100 hover:text-primary-600'
                  }`}
                >
                  <Icon className={`mr-3 h-5 w-5 transition-transform group-hover:scale-110 ${isActive ? 'text-white' : ''}`} />
                  {item.name}
                </Link>
              )
            })}
          </nav>

          {/* Sign Out */}
          <div className="p-4 border-t border-gray-200 bg-gray-50">
            <button
              onClick={handleSignOut}
              className="flex items-center w-full px-4 py-3 text-sm font-semibold text-gray-700 rounded-xl hover:bg-red-50 hover:text-red-600 transition-all duration-200 group"
            >
              <LogOut className="mr-3 h-5 w-5 transition-transform group-hover:scale-110" />
              Sign Out
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

