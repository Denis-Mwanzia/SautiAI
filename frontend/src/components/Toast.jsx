import { useEffect } from 'react'
import { CheckCircle, XCircle, AlertCircle, Info, X } from 'lucide-react'

const TOAST_TYPES = {
  success: { icon: CheckCircle, color: 'bg-green-500', textColor: 'text-green-800', bgColor: 'bg-green-50', borderColor: 'border-green-200' },
  error: { icon: XCircle, color: 'bg-red-500', textColor: 'text-red-800', bgColor: 'bg-red-50', borderColor: 'border-red-200' },
  warning: { icon: AlertCircle, color: 'bg-yellow-500', textColor: 'text-yellow-800', bgColor: 'bg-yellow-50', borderColor: 'border-yellow-200' },
  info: { icon: Info, color: 'bg-blue-500', textColor: 'text-blue-800', bgColor: 'bg-blue-50', borderColor: 'border-blue-200' }
}

function Toast({ toast, onClose }) {
  const { type = 'info', message, duration = 5000 } = toast
  const config = TOAST_TYPES[type] || TOAST_TYPES.info
  const Icon = config.icon

  useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(() => onClose(), duration)
      return () => clearTimeout(timer)
    }
  }, [duration, onClose])

  return (
    <div className={`${config.bgColor} border ${config.borderColor} rounded-lg shadow-lg p-4 mb-3 flex items-start gap-3 min-w-[300px] max-w-md`}>
      <Icon className={`h-5 w-5 ${config.textColor} flex-shrink-0 mt-0.5`} />
      <div className="flex-1">
        <p className={`text-sm font-medium ${config.textColor}`}>{message}</p>
      </div>
      <button
        onClick={onClose}
        className={`${config.textColor} hover:opacity-70 transition-opacity flex-shrink-0`}
        aria-label="Close toast"
      >
        <X className="h-4 w-4" />
      </button>
    </div>
  )
}

export default Toast
