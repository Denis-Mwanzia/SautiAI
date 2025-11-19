import { Link } from 'react-router-dom'
import { 
  LayoutDashboard, 
  Bell, 
  Search, 
  Settings, 
  MessageSquare,
  FileText,
  Shield,
  AlertTriangle,
  Github,
  Twitter,
  Mail
} from 'lucide-react'

export default function Footer() {
  const currentYear = new Date().getFullYear()

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

  return (
    <footer className="bg-white border-t border-gray-200 w-full relative overflow-hidden">
      <div className="px-4 md:px-6 lg:px-8 py-12 w-full">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-8">
          {/* Brand Section */}
          <div className="space-y-5">
            <div className="flex items-center gap-3 group cursor-pointer">
              <div className="relative w-14 h-14 bg-kenya-gradient rounded-2xl flex items-center justify-center shadow-kenya-lg ring-4 ring-white/50 group-hover:scale-110 group-hover:rotate-6 transition-all duration-500">
                <span className="text-white font-black text-2xl relative z-10 drop-shadow-lg">SA</span>
                <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-white/30 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
              </div>
              <div>
                <h3 className="text-2xl font-black kenya-gradient-text group-hover:scale-105 transition-transform duration-300">Sauti AI</h3>
                <p className="text-xs font-bold text-gray-600 uppercase tracking-widest mt-1">Voice of the People</p>
              </div>
            </div>
            <p className="text-sm text-gray-600 leading-relaxed font-medium">
              Empowering citizens through intelligent civic feedback analysis and government accountability tracking.
            </p>
            <div className="flex items-center gap-3 pt-2">
              <a 
                href="https://github.com" 
                target="_blank" 
                rel="noreferrer"
                className="relative p-3 bg-gradient-to-br from-gray-100 to-gray-50 rounded-xl hover:from-kenya-red-50 hover:to-kenya-red-100 hover:text-kenya-red-600 transition-all duration-300 group shadow-sm hover:shadow-md hover:scale-110 active:scale-95"
                aria-label="GitHub"
              >
                <Github className="h-5 w-5 group-hover:scale-110 group-hover:rotate-12 transition-transform duration-300" />
                <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-transparent via-white/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
              </a>
              <a 
                href="https://twitter.com" 
                target="_blank" 
                rel="noreferrer"
                className="relative p-3 bg-gradient-to-br from-gray-100 to-gray-50 rounded-xl hover:from-kenya-red-50 hover:to-kenya-red-100 hover:text-kenya-red-600 transition-all duration-300 group shadow-sm hover:shadow-md hover:scale-110 active:scale-95"
                aria-label="Twitter"
              >
                <Twitter className="h-5 w-5 group-hover:scale-110 group-hover:rotate-12 transition-transform duration-300" />
                <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-transparent via-white/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
              </a>
              <a 
                href="mailto:contact@sautiai.com" 
                className="relative p-3 bg-gradient-to-br from-gray-100 to-gray-50 rounded-xl hover:from-kenya-red-50 hover:to-kenya-red-100 hover:text-kenya-red-600 transition-all duration-300 group shadow-sm hover:shadow-md hover:scale-110 active:scale-95"
                aria-label="Email"
              >
                <Mail className="h-5 w-5 group-hover:scale-110 group-hover:rotate-12 transition-transform duration-300" />
                <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-transparent via-white/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
              </a>
            </div>
          </div>

          {/* Quick Links */}
          <div className="relative">
            <div className="absolute -left-4 top-0 bottom-0 w-1 bg-kenya-gradient rounded-full opacity-0 hover:opacity-100 transition-opacity duration-300"></div>
            <h4 className="text-sm font-black text-gray-900 uppercase tracking-wider mb-6 flex items-center gap-2">
              <span className="w-2 h-2 bg-kenya-red-500 rounded-full animate-pulse"></span>
              Quick Links
            </h4>
            <ul className="space-y-3">
              {navigation.slice(0, 4).map((item, index) => (
                <li key={item.name} style={{ animationDelay: `${index * 0.1}s` }}>
                  <Link
                    to={item.href}
                    className="group relative text-sm text-gray-600 hover:text-kenya-red-600 font-bold transition-all duration-300 flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gradient-to-r hover:from-kenya-red-50 hover:to-kenya-green-50 hover:shadow-sm hover:translate-x-2"
                  >
                    <div className="absolute left-0 top-0 bottom-0 w-1 bg-kenya-gradient rounded-r-full opacity-0 group-hover:opacity-100 transition-opacity"></div>
                    <item.icon className="h-4 w-4 group-hover:scale-125 group-hover:rotate-12 transition-all duration-300" />
                    <span className="relative z-10">{item.name}</span>
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* More Links */}
          <div className="relative">
            <div className="absolute -left-4 top-0 bottom-0 w-1 bg-kenya-gradient rounded-full opacity-0 hover:opacity-100 transition-opacity duration-300"></div>
            <h4 className="text-sm font-black text-gray-900 uppercase tracking-wider mb-6 flex items-center gap-2">
              <span className="w-2 h-2 bg-kenya-green-500 rounded-full animate-pulse"></span>
              More
            </h4>
            <ul className="space-y-3">
              {navigation.slice(4).map((item, index) => (
                <li key={item.name} style={{ animationDelay: `${index * 0.1}s` }}>
                  <Link
                    to={item.href}
                    className="group relative text-sm text-gray-600 hover:text-kenya-red-600 font-bold transition-all duration-300 flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gradient-to-r hover:from-kenya-red-50 hover:to-kenya-green-50 hover:shadow-sm hover:translate-x-2"
                  >
                    <div className="absolute left-0 top-0 bottom-0 w-1 bg-kenya-gradient rounded-r-full opacity-0 group-hover:opacity-100 transition-opacity"></div>
                    <item.icon className="h-4 w-4 group-hover:scale-125 group-hover:rotate-12 transition-all duration-300" />
                    <span className="relative z-10">{item.name}</span>
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Contact & Info */}
          <div className="relative">
            <div className="absolute -left-4 top-0 bottom-0 w-1 bg-kenya-gradient rounded-full opacity-0 hover:opacity-100 transition-opacity duration-300"></div>
            <h4 className="text-sm font-black text-gray-900 uppercase tracking-wider mb-6 flex items-center gap-2">
              <span className="w-2 h-2 bg-black rounded-full animate-pulse"></span>
              About
            </h4>
            <ul className="space-y-4 text-sm">
              <li className="font-black text-gray-900 text-base">Civic Intelligence Platform</li>
              <li className="text-sm text-gray-600 leading-relaxed font-medium">
                Built for transparency, accountability, and citizen engagement in Kenya.
              </li>
              <li className="pt-3">
                <a 
                  href="mailto:contact@sautiai.com" 
                  className="group inline-flex items-center gap-2 text-kenya-red-600 hover:text-kenya-red-700 font-bold transition-all duration-300 px-4 py-2 rounded-lg hover:bg-kenya-red-50 hover:shadow-sm"
                >
                  <Mail className="h-4 w-4 group-hover:scale-110 group-hover:rotate-12 transition-transform" />
                  <span>contact@sautiai.com</span>
                </a>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="pt-8 border-t border-gray-200">
          <div className="flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="flex items-center gap-3 text-sm">
              <span className="font-black text-gray-900">© {currentYear} Sauti AI.</span>
              <span className="hidden md:inline text-gray-500 font-medium">All rights reserved.</span>
            </div>
            <div className="flex items-center gap-4 text-xs">
              <a href="#" className="group font-bold text-gray-600 hover:text-kenya-red-600 transition-all duration-300 hover:scale-110 relative">
                Privacy Policy
                <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-kenya-red-600 group-hover:w-full transition-all duration-300"></span>
              </a>
              <span className="text-gray-300">•</span>
              <a href="#" className="group font-bold text-gray-600 hover:text-kenya-red-600 transition-all duration-300 hover:scale-110 relative">
                Terms of Service
                <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-kenya-red-600 group-hover:w-full transition-all duration-300"></span>
              </a>
              <span className="text-gray-300">•</span>
              <a href="#" className="group font-bold text-gray-600 hover:text-kenya-red-600 transition-all duration-300 hover:scale-110 relative">
                Documentation
                <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-kenya-red-600 group-hover:w-full transition-all duration-300"></span>
              </a>
            </div>
            {/* Kenya Flag Colors Indicator - Animated */}
            <div className="flex items-center gap-2 group cursor-pointer">
              <div className="h-2 w-10 bg-black rounded-full shadow-md group-hover:scale-110 transition-transform duration-300"></div>
              <div className="h-2 w-10 bg-kenya-red-500 rounded-full shadow-md group-hover:scale-110 transition-transform duration-300" style={{ animationDelay: '0.1s' }}></div>
              <div className="h-2 w-10 bg-kenya-green-500 rounded-full shadow-md group-hover:scale-110 transition-transform duration-300" style={{ animationDelay: '0.2s' }}></div>
            </div>
          </div>
        </div>
      </div>
    </footer>
  )
}

