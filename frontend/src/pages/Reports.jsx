import { useEffect, useState, useCallback } from 'react'
import api from '../services/api'
import { useToast } from '../contexts/ToastContext'
import { useApiCache } from '../hooks/useApiCache'
import { useRequestDeduplication } from '../hooks/useRequestDeduplication'
import { FileText, Download, Calendar, Globe, TrendingUp, AlertCircle, Sparkles, RefreshCw } from 'lucide-react'

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
      
      const cacheKey = 'reports-pulse-20'
      const cached = useCache ? getCached(cacheKey) : null
      
      if (cached) {
        setReports(cached)
        setLoading(false)
        return
      }
      
      const response = await dedupeRequest(cacheKey, () => api.get('/reports/pulse?limit=20'))
      const reportsData = response?.data?.data || []
      
      setReports(reportsData)
      setCached(cacheKey, reportsData)
    } catch (error) {
      if (error.response?.status === 404) {
        setReports([])
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
      setTimeout(() => loadReports(false), 2000)
    } catch (error) {
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
          <div className="animate-spin rounded-full h-12 w-12 border-3 border-gray-200 border-t-gray-900 mx-auto mb-4"></div>
          <p className="text-gray-600 text-sm">Loading reports...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
        <div>
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Reports</h1>
          <p className="text-gray-600 text-sm">Actionable policy briefs and citizen intelligence summaries</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => generateReport('daily')}
            disabled={generating}
            className="inline-flex items-center gap-2 px-4 py-2 bg-white border border-gray-200 text-gray-700 rounded-lg hover:bg-gray-50 disabled:opacity-50 transition-all duration-200 text-sm font-medium shadow-sm hover:shadow"
          >
            {generating ? 'Generating...' : 'Daily'}
          </button>
          <button
            onClick={() => generateReport('weekly')}
            disabled={generating}
            className="inline-flex items-center gap-2 px-4 py-2 bg-gray-900 text-white rounded-lg hover:bg-gray-800 disabled:opacity-50 transition-all duration-200 text-sm font-medium shadow-sm hover:shadow"
          >
            {generating ? 'Generating...' : 'Weekly'}
          </button>
          <button
            onClick={() => loadReports(false)}
            disabled={loading}
            className="inline-flex items-center gap-2 px-4 py-2 bg-white border border-gray-200 text-gray-700 rounded-lg hover:bg-gray-50 disabled:opacity-50 transition-all duration-200 text-sm font-medium shadow-sm hover:shadow"
          >
            <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Reports List */}
      {reports.length === 0 ? (
        <div className="glass-card p-12 text-center">
          <div className="relative mb-6 inline-block">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-gray-100 rounded-full border-2 border-gray-200">
              <FileText className="h-8 w-8 text-gray-400" />
            </div>
          </div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">No Reports Yet</h3>
          <p className="text-gray-600 text-sm mb-8 max-w-md mx-auto">Generate your first Citizen Pulse Report to get started</p>
          <button
            onClick={() => generateReport('weekly')}
            disabled={generating}
            className="inline-flex items-center gap-2 px-6 py-3 bg-gray-900 text-white rounded-lg hover:bg-gray-800 disabled:opacity-50 transition-all duration-200 text-sm font-medium shadow-sm hover:shadow"
          >
            <FileText className="h-4 w-4" />
            Generate Weekly Report
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {reports.map((report) => (
            <div
              key={report.id}
              className="glass-card p-6"
            >
              <div className="flex items-start justify-between mb-6">
                <div className="flex items-center gap-4">
                  <div className="p-3 bg-gray-100 rounded-lg">
                    <FileText className="h-5 w-5 text-gray-700" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-1">
                      {report.period?.charAt(0).toUpperCase() + report.period?.slice(1)} Citizen Pulse Report
                    </h3>
                    <div className="flex items-center gap-4 text-xs text-gray-600">
                      <span className="flex items-center gap-1.5">
                        <Calendar className="h-3.5 w-3.5" />
                        {new Date(report.generated_at || report.created_at).toLocaleDateString()}
                      </span>
                      <span className="flex items-center gap-1.5">
                        <Globe className="h-3.5 w-3.5" />
                        {report.language === 'bilingual' ? 'English + Kiswahili' : report.language}
                      </span>
                    </div>
                  </div>
                </div>
                <a
                  href={`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/v1/reports/pulse/${report.id}/html`}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-2 px-4 py-2 bg-white border border-gray-200 text-gray-700 rounded-lg hover:bg-gray-50 transition-all duration-200 text-sm font-medium shadow-sm hover:shadow"
                >
                  <Download className="h-4 w-4" />
                  Open HTML
                </a>
              </div>

              {/* Report Summary Stats */}
              <div className="grid grid-cols-3 gap-4 mb-6">
                <div className="bg-blue-50 rounded-lg p-4 border border-blue-100">
                  <div className="text-xs text-gray-600 mb-1 font-medium">Total Feedback</div>
                  <div className="text-2xl font-semibold text-blue-600">
                    {report.total_feedback || report.data?.total_feedback || 0}
                  </div>
                </div>
                <div className="bg-green-50 rounded-lg p-4 border border-green-100">
                  <div className="text-xs text-gray-600 mb-1 font-medium">Positive Sentiment</div>
                  <div className="text-2xl font-semibold text-green-600">
                    {report.sentiment_breakdown?.positive || report.data?.sentiment_breakdown?.positive || 0}
                  </div>
                </div>
                <div className="bg-red-50 rounded-lg p-4 border border-red-100">
                  <div className="text-xs text-gray-600 mb-1 font-medium">Negative Concerns</div>
                  <div className="text-2xl font-semibold text-red-600">
                    {report.sentiment_breakdown?.negative || report.data?.sentiment_breakdown?.negative || 0}
                  </div>
                </div>
              </div>

              {/* Top Issues */}
              {report.top_issues && report.top_issues.length > 0 && (
                <div className="mb-6">
                  <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2 text-sm">
                    <TrendingUp className="h-4 w-4 text-gray-700" />
                    Top Issues
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {report.top_issues.slice(0, 5).map((issue, idx) => (
                      <span
                        key={idx}
                        className="px-3 py-1.5 bg-gray-100 text-gray-700 rounded-lg text-xs font-medium border border-gray-200"
                      >
                        {issue.sector || issue.name}: {issue.count} complaints
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Summary Preview */}
              {(report.summary_en || report.data?.summary_en) && (
                <div className="bg-gray-50 rounded-lg p-4 mb-4 border border-gray-200">
                  <h4 className="font-semibold text-gray-900 mb-2 text-sm">Summary (English)</h4>
                  <p className="text-gray-600 text-sm line-clamp-3 leading-relaxed">
                    {report.summary_en || report.data?.summary_en || 'No summary available'}
                  </p>
                </div>
              )}

              {(report.summary_sw || report.data?.summary_sw) && (
                <div className="bg-gray-50 rounded-lg p-4 mb-4 border border-gray-200">
                  <h4 className="font-semibold text-gray-900 mb-2 text-sm">Muhtasari (Kiswahili)</h4>
                  <p className="text-gray-600 text-sm line-clamp-3 leading-relaxed">
                    {report.summary_sw || report.data?.summary_sw || 'Hakuna muhtasari'}
                  </p>
                </div>
              )}

              {/* Policy Recommendations */}
              {report.policy_recommendations && report.policy_recommendations.length > 0 && (
                <div className="pt-4 border-t border-gray-200">
                  <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2 text-sm">
                    <AlertCircle className="h-4 w-4 text-gray-700" />
                    Policy Recommendations
                  </h4>
                  <ul className="space-y-2">
                    {report.policy_recommendations.slice(0, 3).map((rec, idx) => (
                      <li key={idx} className="text-sm text-gray-700 flex items-start gap-2">
                        <span className="text-gray-900 font-semibold mt-0.5">{idx + 1}.</span>
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
