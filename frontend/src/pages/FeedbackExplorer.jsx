import { useEffect, useState, useMemo, useCallback } from 'react'
import api from '../services/api'
import { useDebounce } from '../hooks/useDebounce'
import { useApiCache } from '../hooks/useApiCache'
import { useRequestDeduplication } from '../hooks/useRequestDeduplication'
import { Search, Filter, Clock, Save, Bookmark } from 'lucide-react'

export default function FeedbackExplorer() {
  const [feedback, setFeedback] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [filterSector, setFilterSector] = useState('')
  const [filterCounty, setFilterCounty] = useState('')
  const [savedViews, setSavedViews] = useState([])
  const { getCached, setCached } = useApiCache()
  const { dedupeRequest } = useRequestDeduplication()
  
  // Debounce search query to avoid excessive API calls
  const debouncedSearchQuery = useDebounce(searchQuery, 500)

  useEffect(() => {
    // Load saved views
    try {
      const raw = localStorage.getItem('sauti_saved_views')
      if (raw) setSavedViews(JSON.parse(raw))
    } catch {}
    // Initial load
    loadFeedback()
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  // Reload when debounced search or filters change
  useEffect(() => {
    // Skip initial render (handled above)
    if (!debouncedSearchQuery && !filterSector && !filterCounty) {
      return
    }
    // Wait for debounce to settle
    if (debouncedSearchQuery !== searchQuery && searchQuery !== '') {
      return
    }
    loadFeedback()
  }, [debouncedSearchQuery, filterSector, filterCounty]) // eslint-disable-line react-hooks/exhaustive-deps

  const loadFeedback = useCallback(async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams()
      const query = debouncedSearchQuery || searchQuery
      if (query) params.append('q', query)
      if (filterSector) params.append('sector', filterSector)
      if (filterCounty) params.append('county', filterCounty)
      params.append('limit', '50')
      
      const cacheKey = `feedback-search-${params.toString()}`
      const cached = getCached(cacheKey)
      
      if (cached) {
        setFeedback(cached)
        setLoading(false)
        return
      }
      
      // Use request deduplication
      const response = await dedupeRequest(cacheKey, () => api.get(`/search/feedback?${params.toString()}`))
      const feedbackData = response?.data?.data || []
      
      setFeedback(feedbackData)
      setCached(cacheKey, feedbackData)
    } catch (error) {
      console.error('Error loading feedback:', error)
      // Set empty array on error to prevent crashes
      setFeedback([])
    } finally {
      setLoading(false)
    }
  }, [debouncedSearchQuery, searchQuery, filterSector, filterCounty, getCached, setCached, dedupeRequest])

  const filteredFeedback = feedback

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-4 border-primary-200 border-t-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600 animate-pulse">Loading feedback...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="animate-slide-up">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-primary-600 to-primary-800 bg-clip-text text-transparent">
          Feedback Explorer
        </h1>
        <p className="text-gray-600 mt-2">Search and explore citizen feedback</p>
      </div>

      {/* Search and Filters */}
      <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100 animate-slide-up">
        <div className="flex flex-col md:flex-row items-stretch md:items-center gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search feedback by keywords..."
              className="w-full pl-12 pr-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-200 outline-none"
            />
          </div>
          <div className="relative md:w-64">
            <Filter className="absolute left-4 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <select
                    value={filterSector}
                    onChange={(e) => setFilterSector(e.target.value)}
                    className="w-full pl-12 pr-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-200 outline-none appearance-none bg-white"
                  >
                    <option value="">All Sectors</option>
                    <option value="health">Health</option>
                    <option value="education">Education</option>
                    <option value="governance">Governance</option>
                    <option value="transport">Transport</option>
                    <option value="infrastructure">Infrastructure</option>
                    <option value="security">Security</option>
                  </select>
          </div>
          <div className="relative md:w-64">
            <Filter className="absolute left-4 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              value={filterCounty}
              onChange={(e) => setFilterCounty(e.target.value)}
              placeholder="County (e.g., Nairobi)"
              className="w-full pl-12 pr-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-200 outline-none"
            />
          </div>
          <button
            onClick={() => loadFeedback()}
            className="px-4 py-3 bg-primary-600 text-white rounded-xl hover:bg-primary-700 transition-all"
          >
            Search
          </button>
          <button
            onClick={() => {
              const view = { q: searchQuery, sector: filterSector, county: filterCounty, savedAt: Date.now() }
              const next = [view, ...savedViews].slice(0, 10)
              setSavedViews(next)
              localStorage.setItem('sauti_saved_views', JSON.stringify(next))
            }}
            className="px-3 py-3 bg-white border border-gray-200 rounded-xl hover:bg-gray-50"
            title="Save current view"
          >
            <Save className="h-5 w-5 text-gray-600" />
          </button>
        </div>
        {(filteredFeedback.length > 0 || savedViews.length > 0) && (
          <p className="text-sm text-gray-500 mt-4">
            Showing {filteredFeedback.length} of {feedback.length} feedback items
          </p>
        )}
        {savedViews.length > 0 && (
          <div className="mt-4 flex flex-wrap gap-2">
            {savedViews.map((v, i) => (
              <button
                key={i}
                onClick={() => {
                  setSearchQuery(v.q || '')
                  setFilterSector(v.sector || '')
                  setFilterCounty(v.county || '')
                  // loadFeedback will be triggered by useEffect
                }}
                className="inline-flex items-center gap-2 px-3 py-1.5 bg-gray-50 border border-gray-200 rounded-full text-sm hover:bg-gray-100"
                title={new Date(v.savedAt).toLocaleString()}
              >
                <Bookmark className="h-4 w-4 text-gray-500" />
                {v.q || 'All'} {v.sector ? `• ${v.sector}` : ''} {v.county ? `• ${v.county}` : ''}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Feedback List */}
      <div className="space-y-4">
        {filteredFeedback.length === 0 ? (
          <div className="bg-white rounded-xl shadow-lg p-12 text-center border border-gray-100 animate-scale-in">
            <div className="inline-flex items-center justify-center w-20 h-20 bg-gray-100 rounded-full mb-6">
              <Search className="h-10 w-10 text-gray-400" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">No feedback found</h3>
            <p className="text-gray-600">
              {searchQuery || filterSector 
                ? 'Try adjusting your search or filter criteria'
                : 'No feedback available at this time'}
            </p>
          </div>
        ) : (
          filteredFeedback.map((item, index) => (
            <div 
              key={item.id} 
              className="bg-white rounded-xl shadow-lg p-6 border border-gray-100 card-hover animate-slide-up"
              style={{ animationDelay: `${index * 0.05}s` }}
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="px-3 py-1 bg-primary-100 text-primary-700 rounded-lg text-xs font-semibold uppercase">
                    {item.source}
                  </div>
                  <span className="text-xs text-gray-500 flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    {new Date(item.created_at).toLocaleString()}
                  </span>
                </div>
              </div>
              <p className="text-gray-900 leading-relaxed line-clamp-4">{item.text}</p>
              {(item.location || item.sector) && (
                <div className="mt-3 text-xs text-gray-500 flex gap-3">
                  {item.location && <span>County: {item.location}</span>}
                  {item.sector && <span>Sector: {item.sector}</span>}
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  )
}

