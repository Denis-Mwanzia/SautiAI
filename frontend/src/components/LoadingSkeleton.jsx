export function StatCardSkeleton() {
  return (
    <div className="bg-white rounded-2xl shadow-lg p-6 animate-pulse">
      <div className="flex items-center justify-between mb-4">
        <div className="h-4 bg-gray-200 rounded w-24"></div>
        <div className="h-8 w-8 bg-gray-200 rounded"></div>
      </div>
      <div className="h-8 bg-gray-200 rounded w-32 mb-2"></div>
      <div className="h-4 bg-gray-200 rounded w-20"></div>
    </div>
  )
}

export function ChartSkeleton() {
  return (
    <div className="bg-white rounded-2xl shadow-lg p-6 animate-pulse">
      <div className="h-6 bg-gray-200 rounded w-48 mb-6"></div>
      <div className="h-64 bg-gray-100 rounded"></div>
    </div>
  )
}

export function TableSkeleton({ rows = 5 }) {
  return (
    <div className="bg-white rounded-2xl shadow-lg p-6 animate-pulse">
      <div className="h-6 bg-gray-200 rounded w-32 mb-6"></div>
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
    <div className="bg-white rounded-2xl shadow-lg p-6 animate-pulse">
      <div className="h-6 bg-gray-200 rounded w-3/4 mb-4"></div>
      <div className="h-4 bg-gray-200 rounded w-full mb-2"></div>
      <div className="h-4 bg-gray-200 rounded w-5/6"></div>
    </div>
  )
}

