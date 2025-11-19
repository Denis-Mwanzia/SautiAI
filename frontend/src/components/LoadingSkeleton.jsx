export function StatCardSkeleton() {
  return (
    <div className="stat-card p-6 relative overflow-hidden">
      <div className="flex items-center justify-between mb-4">
        <div className="h-10 w-10 bg-gray-200 rounded-lg animate-pulse"></div>
        <div className="h-6 w-6 bg-gray-200 rounded animate-pulse"></div>
      </div>
      <div className="h-3 bg-gray-200 rounded w-20 mb-2 animate-pulse"></div>
      <div className="h-8 bg-gray-200 rounded w-24 mb-2 animate-pulse"></div>
      <div className="h-3 bg-gray-200 rounded w-16 animate-pulse"></div>
    </div>
  )
}

export function ChartSkeleton() {
  return (
    <div className="glass-card p-6 relative overflow-hidden">
      <div className="h-6 bg-gray-200 rounded w-40 mb-6 animate-pulse"></div>
      <div className="h-64 bg-gray-100 rounded-lg animate-pulse relative">
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-12 h-12 border-3 border-gray-200 border-t-gray-900 rounded-full animate-spin"></div>
        </div>
      </div>
    </div>
  )
}

export function TableSkeleton({ rows = 5 }) {
  return (
    <div className="glass-card p-6 animate-pulse">
      <div className="h-5 bg-gray-200 rounded w-32 mb-6"></div>
      <div className="space-y-3">
        {Array.from({ length: rows }).map((_, i) => (
          <div key={i} className="flex gap-4">
            <div className="h-4 bg-gray-200 rounded flex-1"></div>
            <div className="h-4 bg-gray-200 rounded w-24"></div>
            <div className="h-4 bg-gray-200 rounded w-24"></div>
          </div>
        ))}
      </div>
    </div>
  )
}

export function CardSkeleton() {
  return (
    <div className="glass-card p-6 relative overflow-hidden animate-pulse">
      <div className="h-5 bg-gray-200 rounded w-3/4 mb-4"></div>
      <div className="h-4 bg-gray-200 rounded w-full mb-2"></div>
      <div className="h-4 bg-gray-200 rounded w-5/6"></div>
    </div>
  )
}
