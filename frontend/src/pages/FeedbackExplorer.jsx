import { useEffect, useState, useMemo, useCallback } from 'react'
import api from '../services/api'
import { useDebounce } from '../hooks/useDebounce'
import { useApiCache } from '../hooks/useApiCache'
import { useRequestDeduplication } from '../hooks/useRequestDeduplication'
import { Search, Filter, Clock, Save, Bookmark, X } from 'lucide-react'

export default function FeedbackExplorer() {
  const [feedback, setFeedback] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [filterSector, setFilterSector] = useState('')
  const [filterCounty, setFilterCounty] = useState('')
  const [savedViews, setSavedViews] = useState([])
  const { getCached, setCached } = useApiCache()
  const { dedupeRequest } = useRequestDeduplication()
  
  const debouncedSearchQuery = useDebounce(searchQuery, 500)

  useEffect(() => {
    try {
      const raw = localStorage.getItem('sauti_saved_views')
      if (raw) setSavedViews(JSON.parse(raw))
    } catch {}
    loadFeedback()
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (!debouncedSearchQuery && !filterSector && !filterCounty) {
      return
    }
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
      
      const response = await dedupeRequest(cacheKey, () => api.get(`/search/feedback?${params.toString()}`))
      const feedbackData = response?.data?.data || []
      
      setFeedback(feedbackData)
      setCached(cacheKey, feedbackData)
    } catch (error) {
      console.error('Error loading feedback:', error)
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
          <div className="animate-spin rounded-full h-12 w-12 border-3 border-gray-200 border-t-gray-900 mx-auto mb-4"></div>
          <p className="text-gray-600 text-sm">Loading feedback...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold text-gray-900 mb-2">Feedback</h1>
        <p className="text-gray-600 text-sm">Search and explore citizen feedback data</p>
      </div>

      {/* Search and Filters */}
      <div className="glass-card p-6">
        <div className="flex flex-col md:flex-row items-stretch md:items-center gap-3">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search feedback by keywords..."
              className="w-full pl-10 pr-10 py-2.5 border border-gray-200 rounded-lg focus:ring-2 focus:ring-gray-900/20 focus:border-gray-900 transition-all duration-200 outline-none bg-white text-sm"
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery('')}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 p-1 rounded hover:bg-gray-100 transition-colors"
              >
                <X className="h-3.5 w-3.5 text-gray-400" />
              </button>
            )}
          </div>
          <div className="relative md:w-48">
            <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <select
              value={filterSector}
              onChange={(e) => setFilterSector(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 border border-gray-200 rounded-lg focus:ring-2 focus:ring-gray-900/20 focus:border-gray-900 transition-all duration-200 outline-none appearance-none bg-white text-sm"
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
          <div className="relative md:w-48">
            <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              value={filterCounty}
              onChange={(e) => setFilterCounty(e.target.value)}
              placeholder="County (e.g., Nairobi)"
              className="w-full pl-10 pr-4 py-2.5 border border-gray-200 rounded-lg focus:ring-2 focus:ring-gray-900/20 focus:border-gray-900 transition-all duration-200 outline-none bg-white text-sm"
            />
          </div>
          <button
            onClick={() => loadFeedback()}
            className="inline-flex items-center gap-2 px-4 py-2.5 bg-gray-900 text-white rounded-lg hover:bg-gray-800 transition-all duration-200 text-sm font-medium shadow-sm hover:shadow"
          >
            <Search className="h-4 w-4" />
            Search
          </button>
          <button
            onClick={() => {
              const view = { q: searchQuery, sector: filterSector, county: filterCounty, savedAt: Date.now() }
              const next = [view, ...savedViews].slice(0, 10)
              setSavedViews(next)
              localStorage.setItem('sauti_saved_views', JSON.stringify(next))
            }}
            className="p-2.5 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            title="Save current view"
          >
            <Save className="h-4 w-4 text-gray-600" />
          </button>
        </div>
        {(filteredFeedback.length > 0 || savedViews.length > 0) && (
          <p className="text-xs text-gray-500 mt-4">
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
                }}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-gray-50 border border-gray-200 rounded-lg text-xs hover:bg-gray-100 transition-colors"
                title={new Date(v.savedAt).toLocaleString()}
              >
                <Bookmark className="h-3.5 w-3.5 text-gray-500" />
                {v.q || 'All'} {v.sector ? `• ${v.sector}` : ''} {v.county ? `• ${v.county}` : ''}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Feedback List */}
      <div className="space-y-3">
        {filteredFeedback.length === 0 ? (
          <div className="glass-card p-12 text-center">
            <div className="relative mb-6 inline-block">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-gray-100 rounded-full border-2 border-gray-200">
                <Search className="h-8 w-8 text-gray-400" />
              </div>
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">No Feedback Found</h3>
            <p className="text-gray-600 text-sm mb-6 max-w-md mx-auto">
              {searchQuery || filterSector 
                ? 'Try adjusting your search or filter criteria to find what you\'re looking for.'
                : 'No feedback available at this time. Check back later or try different filters.'}
            </p>
            {(searchQuery || filterSector) && (
              <button
                onClick={() => {
                  setSearchQuery('')
                  setFilterSector('')
                  setFilterCounty('')
                }}
                className="inline-flex items-center gap-2 px-4 py-2 bg-white border border-gray-200 text-gray-700 rounded-lg hover:bg-gray-50 transition-all duration-200 text-sm font-medium shadow-sm hover:shadow"
              >
                Clear Filters
              </button>
            )}
          </div>
        ) : (
          filteredFeedback.map((item, index) => (
            <div 
              key={item.id} 
              className="glass-card p-5"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                  <span className="px-2.5 py-1 bg-gray-100 text-gray-700 rounded-md text-xs font-medium">
                    {item.source}
                  </span>
                  <span className="text-xs text-gray-500 flex items-center gap-1">
                    <Clock className="h-3.5 w-3.5" />
                    {new Date(item.created_at).toLocaleString()}
                  </span>
                </div>
              </div>
              <p className="text-gray-900 leading-relaxed mb-3">{item.text}</p>
              {(item.location || item.sector) && (
                <div className="flex items-center gap-4 text-xs text-gray-600 pt-3 border-t border-gray-200">
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
