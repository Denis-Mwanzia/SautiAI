import { useEffect, useState, useCallback } from 'react'
import api from '../services/api'
import { useToast } from '../contexts/ToastContext'
import { useApiCache } from '../hooks/useApiCache'
import { useRequestDeduplication } from '../hooks/useRequestDeduplication'
import { FileText, Download, Calendar, Globe, TrendingUp, AlertCircle } from 'lucide-react'

export default function Reports() {
  const [reports, setReports] = useState([])
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const toast = useToast()
  const { getCached, setCached } = useApiCache()
  const { dedupeRequest } = useRequestDeduplication()

  const loadReports = useCallback(async (useCache = true) => {
    try {
      setLoading(true)
      
      // Check cache
      const cacheKey = 'reports-pulse-20'
      const cached = useCache ? getCached(cacheKey) : null
      
      if (cached) {
        setReports(cached)
        setLoading(false)
        return
      }
      
      // Use request deduplication
      const response = await dedupeRequest(cacheKey, () => api.get('/reports/pulse?limit=20'))
      const reportsData = response?.data?.data || []
      
      setReports(reportsData)
      setCached(cacheKey, reportsData)
    } catch (error) {
      // Handle 404 gracefully (AI features disabled)
      if (error.response?.status === 404) {
        setReports([])
        // Don't show error toast for missing endpoint (AI disabled)
        console.info('Reports endpoint not available (AI features disabled)')
      } else {
        const errorMsg = error.response?.data?.detail || 'Failed to load reports'
        toast.error(errorMsg)
        console.error('Error loading reports:', error)
      }
    } finally {
      setLoading(false)
    }
  }, [getCached, setCached, dedupeRequest, toast])

  useEffect(() => {
    loadReports()
  }, [loadReports])

  const generateReport = async (period = 'weekly') => {
    setGenerating(true)
    try {
      await api.post(`/reports/pulse?period=${period}`)
      toast.success(`${period.charAt(0).toUpperCase() + period.slice(1)} report generated successfully`)
      // Reload reports after generation (clear cache)
      setTimeout(() => loadReports(false), 2000)
    } catch (error) {
      // Handle 503 (Service Unavailable) for AI disabled
      if (error.response?.status === 503) {
        toast.error('Report generation requires AI features. Please enable AI in the backend configuration.')
      } else {
        const errorMsg = error.response?.data?.detail || 'Failed to generate report'
        toast.error(errorMsg)
      }
      console.error('Error generating report:', error)
    } finally {
      setGenerating(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-4 border-primary-200 border-t-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600 animate-pulse">Loading reports...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-primary-600 to-primary-800 bg-clip-text text-transparent">
            Citizen Pulse Reports
          </h1>
          <p className="text-gray-600 mt-1">Actionable policy briefs and citizen intelligence summaries</p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={() => generateReport('daily')}
            disabled={generating}
            className="px-4 py-2 bg-primary-600 text-white rounded-xl hover:bg-primary-700 disabled:opacity-50 transition-all shadow-lg hover:shadow-xl"
          >
            {generating ? 'Generating...' : 'Generate Daily'}
          </button>
          <button
            onClick={() => generateReport('weekly')}
            disabled={generating}
            className="px-4 py-2 bg-gradient-to-r from-primary-600 to-primary-700 text-white rounded-xl hover:from-primary-700 hover:to-primary-800 disabled:opacity-50 transition-all shadow-lg hover:shadow-xl"
          >
            {generating ? 'Generating...' : 'Generate Weekly'}
          </button>
        </div>
      </div>

      {/* Reports List */}
      {reports.length === 0 ? (
        <div className="bg-white rounded-2xl shadow-lg p-12 text-center">
          <FileText className="h-16 w-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-700 mb-2">No Reports Yet</h3>
          <p className="text-gray-600 mb-6">Generate your first Citizen Pulse Report to get started</p>
          <button
            onClick={() => generateReport('weekly')}
            className="px-6 py-3 bg-gradient-to-r from-primary-600 to-primary-700 text-white rounded-xl hover:from-primary-700 hover:to-primary-800 transition-all shadow-lg hover:shadow-xl"
          >
            Generate Weekly Report
          </button>
        </div>
      ) : (
        <div className="grid gap-6">
          {reports.map((report) => (
            <div
              key={report.id}
              className="bg-white rounded-2xl shadow-lg p-6 border-l-4 border-primary-500 hover:shadow-xl transition-all card-hover"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="p-3 bg-primary-100 rounded-xl">
                    <FileText className="h-6 w-6 text-primary-600" />
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-gray-900">
                      {report.period?.charAt(0).toUpperCase() + report.period?.slice(1)} Citizen Pulse Report
                    </h3>
                    <div className="flex items-center gap-4 mt-1 text-sm text-gray-600">
                      <span className="flex items-center gap-1">
                        <Calendar className="h-4 w-4" />
                        {new Date(report.generated_at || report.created_at).toLocaleDateString()}
                      </span>
                      <span className="flex items-center gap-1">
                        <Globe className="h-4 w-4" />
                        {report.language === 'bilingual' ? 'English + Kiswahili' : report.language}
                      </span>
                    </div>
                  </div>
                </div>
                <a
                  href={`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/v1/reports/pulse/${report.id}/html`}
                  target="_blank"
                  rel="noreferrer"
                  className="px-4 py-2 bg-gray-100 text-gray-700 rounded-xl hover:bg-gray-200 transition-all flex items-center gap-2"
                >
                  <Download className="h-4 w-4" />
                  Open HTML
                </a>
              </div>

              {/* Report Summary */}
              <div className="grid grid-cols-3 gap-4 mb-4">
                <div className="bg-blue-50 rounded-xl p-4">
                  <div className="text-sm text-gray-600 mb-1">Total Feedback</div>
                  <div className="text-2xl font-bold text-blue-600">
                    {report.total_feedback || report.data?.total_feedback || 0}
                  </div>
                </div>
                <div className="bg-green-50 rounded-xl p-4">
                  <div className="text-sm text-gray-600 mb-1">Positive Sentiment</div>
                  <div className="text-2xl font-bold text-green-600">
                    {report.sentiment_breakdown?.positive || report.data?.sentiment_breakdown?.positive || 0}
                  </div>
                </div>
                <div className="bg-red-50 rounded-xl p-4">
                  <div className="text-sm text-gray-600 mb-1">Negative Concerns</div>
                  <div className="text-2xl font-bold text-red-600">
                    {report.sentiment_breakdown?.negative || report.data?.sentiment_breakdown?.negative || 0}
                  </div>
                </div>
              </div>

              {/* Top Issues */}
              {report.top_issues && report.top_issues.length > 0 && (
                <div className="mb-4">
                  <h4 className="font-semibold text-gray-700 mb-2 flex items-center gap-2">
                    <TrendingUp className="h-5 w-5 text-primary-600" />
                    Top Issues
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {report.top_issues.slice(0, 5).map((issue, idx) => (
                      <span
                        key={idx}
                        className="px-3 py-1 bg-primary-100 text-primary-700 rounded-lg text-sm font-medium"
                      >
                        {issue.sector || issue.name}: {issue.count} complaints
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Summary Preview */}
              {(report.summary_en || report.data?.summary_en) && (
                <div className="bg-gray-50 rounded-xl p-4 mb-4">
                  <h4 className="font-semibold text-gray-700 mb-2">Summary (English)</h4>
                  <p className="text-gray-600 text-sm line-clamp-3">
                    {report.summary_en || report.data?.summary_en || 'No summary available'}
                  </p>
                </div>
              )}

              {(report.summary_sw || report.data?.summary_sw) && (
                <div className="bg-gray-50 rounded-xl p-4">
                  <h4 className="font-semibold text-gray-700 mb-2">Muhtasari (Kiswahili)</h4>
                  <p className="text-gray-600 text-sm line-clamp-3">
                    {report.summary_sw || report.data?.summary_sw || 'Hakuna muhtasari'}
                  </p>
                </div>
              )}

              {/* Policy Recommendations */}
              {report.policy_recommendations && report.policy_recommendations.length > 0 && (
                <div className="mt-4 pt-4 border-t border-gray-200">
                  <h4 className="font-semibold text-gray-700 mb-2 flex items-center gap-2">
                    <AlertCircle className="h-5 w-5 text-primary-600" />
                    Policy Recommendations
                  </h4>
                  <ul className="space-y-2">
                    {report.policy_recommendations.slice(0, 3).map((rec, idx) => (
                      <li key={idx} className="text-sm text-gray-600 flex items-start gap-2">
                        <span className="text-primary-600 font-bold">{idx + 1}.</span>
                        <span>{rec.recommendation || rec.description || rec}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

