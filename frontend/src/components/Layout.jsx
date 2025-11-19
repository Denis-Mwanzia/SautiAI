import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import ConnectionStatus from './ConnectionStatus'
import Footer from './Footer'
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
    <div className="bg-gradient-to-br from-gray-50 via-white to-gray-50 flex flex-col min-h-screen overflow-x-hidden">
      {/* Skip to main content - Accessibility */}
      <a href="#main-content" className="skip-to-main">
        Skip to main content
      </a>
      
      {/* Mobile Header */}
      <div className="lg:hidden fixed top-0 left-0 right-0 bg-white shadow-md z-30 flex items-center justify-between p-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-kenya-gradient rounded-xl flex items-center justify-center shadow-lg ring-2 ring-white/20">
            <span className="text-white font-bold text-lg">SA</span>
          </div>
          <span className="text-xl font-bold bg-kenya-gradient bg-clip-text text-transparent">
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
      
      {/* Sidebar - Fixed on left */}
      <aside className="hidden lg:flex fixed top-0 bottom-0 left-0 w-64 bg-white border-r border-gray-200 flex-col z-20 overflow-hidden">
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center gap-3 h-20 px-6 border-b border-gray-200">
            <div className="w-10 h-10 bg-gray-900 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-lg">SA</span>
            </div>
            <div>
              <h1 className="text-lg font-bold text-gray-900">Sauti AI</h1>
              <p className="text-xs text-gray-600">Voice of the People</p>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
            {navigation.map((item) => {
              const Icon = item.icon
              const isActive = location.pathname === item.href
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  aria-current={isActive ? 'page' : undefined}
                  className={`group flex items-center gap-3 px-3 py-2.5 text-sm font-medium rounded-lg transition-all duration-200 ${
                    isActive
                      ? 'bg-gray-900 text-white'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  <Icon className={`h-5 w-5 flex-shrink-0 ${isActive ? 'text-white' : 'text-gray-600'}`} />
                  <span>{item.name}</span>
                </Link>
              )
            })}
          </nav>

          {/* Sign Out */}
          <div className="p-4 border-t border-gray-200">
            <button
              onClick={handleSignOut}
              className="flex items-center justify-center gap-2 w-full px-3 py-2.5 text-sm font-medium text-gray-700 rounded-lg hover:bg-gray-100 transition-all duration-200"
            >
              <LogOut className="h-5 w-5" />
              <span>Sign Out</span>
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content Area with Footer - Positioned next to sidebar */}
      <div className="lg:pl-64 pt-16 lg:pt-0 flex flex-col min-h-screen w-full">
        <main id="main-content" className="flex-1 px-4 md:px-6 lg:px-8 max-w-7xl mx-auto w-full py-8" role="main">{children}</main>
        
        {/* Footer - Below both sidebar and content, spans from sidebar edge to viewport edge */}
        <footer className="w-full relative z-30 mt-auto">
          <Footer />
        </footer>
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
                <div className="w-10 h-10 bg-kenya-gradient rounded-xl flex items-center justify-center shadow-lg ring-2 ring-white/20">
                  <span className="text-white font-bold text-lg">SA</span>
                </div>
                <span className="text-xl font-bold bg-kenya-gradient bg-clip-text text-transparent">
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
          <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
            {navigation.map((item) => {
              const Icon = item.icon
              const isActive = location.pathname === item.href
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  onClick={() => setMobileMenuOpen(false)}
                  className={`flex items-center gap-3 px-3 py-2.5 text-sm font-medium rounded-lg transition-all duration-200 ${
                    isActive
                      ? 'bg-gray-900 text-white'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  <Icon className={`h-5 w-5 flex-shrink-0 ${isActive ? 'text-white' : 'text-gray-600'}`} />
                  {item.name}
                </Link>
              )
            })}
          </nav>

          {/* Sign Out */}
          <div className="p-4 border-t border-gray-200">
            <button
              onClick={handleSignOut}
              className="flex items-center gap-2 w-full px-3 py-2.5 text-sm font-medium text-gray-700 rounded-lg hover:bg-gray-100 transition-all duration-200"
            >
              <LogOut className="h-5 w-5" />
              <span>Sign Out</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

