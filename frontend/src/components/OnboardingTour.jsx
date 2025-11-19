import { useState, useEffect } from 'react'
import { X, ArrowRight, ArrowLeft, CheckCircle } from 'lucide-react'

const TOUR_STEPS = [
  {
    id: 'dashboard',
    title: 'Welcome to Sauti AI!',
    content: 'This is your dashboard where you can see real-time citizen feedback, sentiment trends, and county-level insights.',
    target: '[data-tour="dashboard"]',
    position: 'bottom'
  },
  {
    id: 'stats',
    title: 'Key Metrics',
    content: 'Monitor total feedback, sentiment distribution, active alerts, and top sectors at a glance.',
    target: '[data-tour="stats"]',
    position: 'bottom'
  },
  {
    id: 'heatmap',
    title: 'County Heatmap',
    content: 'Visualize issues across all 47 Kenyan counties. Click markers to see detailed information. Switch between Heat, Choropleth, and Cluster views.',
    target: '[data-tour="heatmap"]',
    position: 'top'
  },
  {
    id: 'navigation',
    title: 'Navigation',
    content: 'Access Alerts, Feedback Explorer, AI Chat, Reports, Transparency metrics, and Settings from the sidebar.',
    target: '[data-tour="navigation"]',
    position: 'right'
  }
]

export default function OnboardingTour({ onComplete }) {
  const [currentStep, setCurrentStep] = useState(0)
  const [isVisible, setIsVisible] = useState(false)

  useEffect(() => {
    // Check if user has seen the tour
    const hasSeenTour = localStorage.getItem('sauti-ai-tour-completed')
    if (!hasSeenTour) {
      // Wait for page to load
      setTimeout(() => setIsVisible(true), 1000)
    }
  }, [])

  const handleNext = () => {
    if (currentStep < TOUR_STEPS.length - 1) {
      setCurrentStep(currentStep + 1)
    } else {
      handleComplete()
    }
  }

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1)
    }
  }

  const handleComplete = () => {
    localStorage.setItem('sauti-ai-tour-completed', 'true')
    setIsVisible(false)
    if (onComplete) onComplete()
  }

  const handleSkip = () => {
    handleComplete()
  }

  if (!isVisible) return null

  const step = TOUR_STEPS[currentStep]
  const targetElement = document.querySelector(step.target)

  if (!targetElement) {
    // If target not found, skip to next step
    if (currentStep < TOUR_STEPS.length - 1) {
      setTimeout(() => setCurrentStep(currentStep + 1), 100)
    } else {
      handleComplete()
    }
    return null
  }

  const rect = targetElement.getBoundingClientRect()
  const position = step.position || 'bottom'
  
  let top = 0
  let left = 0
  let arrowClass = ''

  switch (position) {
    case 'bottom':
      top = rect.bottom + 20
      left = rect.left + rect.width / 2
      arrowClass = 'top-0 left-1/2 transform -translate-x-1/2 -translate-y-full'
      break
    case 'top':
      top = rect.top - 20
      left = rect.left + rect.width / 2
      arrowClass = 'bottom-0 left-1/2 transform -translate-x-1/2 translate-y-full'
      break
    case 'right':
      top = rect.top + rect.height / 2
      left = rect.right + 20
      arrowClass = 'left-0 top-1/2 transform -translate-x-full -translate-y-1/2'
      break
    case 'left':
      top = rect.top + rect.height / 2
      left = rect.left - 20
      arrowClass = 'right-0 top-1/2 transform translate-x-full -translate-y-1/2'
      break
  }

  return (
    <>
      {/* Overlay */}
      <div
        className="fixed inset-0 bg-black bg-opacity-50 z-[9998]"
        onClick={handleSkip}
        aria-hidden="true"
      />
      
      {/* Highlight */}
      <div
        className="fixed z-[9999] border-4 border-kenya-red-500 rounded-lg pointer-events-none animate-pulse"
        style={{
          top: rect.top - 4,
          left: rect.left - 4,
          width: rect.width + 8,
          height: rect.height + 8,
          boxShadow: '0 0 0 9999px rgba(0, 0, 0, 0.5)'
        }}
      />

      {/* Tooltip */}
      <div
        className="fixed z-[10000] bg-white rounded-lg shadow-2xl p-6 max-w-sm animate-scale-in"
        style={{
          top: position === 'bottom' ? `${top}px` : position === 'top' ? 'auto' : `${top}px`,
          bottom: position === 'top' ? `${window.innerHeight - rect.top + 20}px` : 'auto',
          left: position === 'left' || position === 'right' ? 'auto' : `${left}px`,
          right: position === 'right' ? `${window.innerWidth - rect.right - 20}px` : 'auto',
          transform: position === 'bottom' || position === 'top' ? 'translateX(-50%)' : 'translateY(-50%)'
        }}
        role="dialog"
        aria-labelledby="tour-title"
        aria-describedby="tour-content"
      >
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <h3 id="tour-title" className="text-lg font-bold text-gray-900 mb-2">
              {step.title}
            </h3>
            <p id="tour-content" className="text-sm text-gray-600">
              {step.content}
            </p>
          </div>
          <button
            onClick={handleSkip}
            className="ml-4 text-gray-400 hover:text-gray-600 focus:outline-none"
            aria-label="Skip tour"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="flex items-center justify-between mt-6">
          <div className="flex items-center gap-2">
            {TOUR_STEPS.map((_, idx) => (
              <div
                key={idx}
                className={`h-2 rounded-full transition-all ${
                  idx === currentStep
                    ? 'bg-kenya-red-500 w-8'
                    : idx < currentStep
                    ? 'bg-kenya-green-500 w-2'
                    : 'bg-gray-300 w-2'
                }`}
                aria-hidden="true"
              />
            ))}
          </div>

          <div className="flex items-center gap-2">
            {currentStep > 0 && (
              <button
                onClick={handlePrevious}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-kenya-red-500"
              >
                <ArrowLeft className="h-4 w-4 inline mr-1" />
                Previous
              </button>
            )}
            <button
              onClick={handleNext}
              className="px-4 py-2 text-sm font-medium text-white bg-kenya-gradient rounded-lg hover:opacity-90 focus:outline-none focus:ring-2 focus:ring-kenya-red-500 flex items-center gap-1"
            >
              {currentStep === TOUR_STEPS.length - 1 ? (
                <>
                  Complete
                  <CheckCircle className="h-4 w-4" />
                </>
              ) : (
                <>
                  Next
                  <ArrowRight className="h-4 w-4" />
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </>
  )
}

