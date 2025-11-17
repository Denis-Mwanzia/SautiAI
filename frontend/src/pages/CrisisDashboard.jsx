import { useEffect, useState, useCallback, useMemo } from 'react'
import api from '../services/api'
import { useToast } from '../contexts/ToastContext'
import { useAutoRefresh } from '../hooks/useAutoRefresh'
import { useApiCache } from '../hooks/useApiCache'
import { useRequestDeduplication } from '../hooks/useRequestDeduplication'
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import {
  AlertTriangle,
  TrendingUp,
  TrendingDown,
  Activity,
  Hash,
  Shield,
  Bell,
  RefreshCw,
  Zap,
  Target,
  BarChart3,
  Users,
  CheckCircle
} from 'lucide-react'
import { CardSkeleton } from '../components/LoadingSkeleton'

const COLORS = ['#ef4444', '#f59e0b', '#10b981', '#3b82f6', '#8b5cf6']

export default function CrisisDashboard() {
  const [dashboardData, setDashboardData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [selectedPolicy, setSelectedPolicy] = useState('')
  const [policyMonitoring, setPolicyMonitoring] = useState(null)
  const toast = useToast()
  const { getCached, setCached } = useApiCache()
  const { dedupeRequest } = useRequestDeduplication()

  const loadCrisisDashboard = useCallback(async (showToast = false, useCache = true) => {
    try {
      setRefreshing(true)
      
      // Performance: Check cache first
      const cacheKey = 'crisis-dashboard-7'
      const cached = useCache ? getCached(cacheKey) : null
      
      if (cached && useCache) {
        setDashboardData(cached)
        setLoading(false)
        setRefreshing(false)
        if (showToast) {
          toast.success('Crisis dashboard loaded from cache')
        }
        return
      }
      
      // Use request deduplication to prevent duplicate concurrent requests
      const response = await dedupeRequest('crisis-dashboard-7', () => api.get('/crisis/dashboard?days=7'))
      const data = response.data.data
      
      setDashboardData(data)
      setCached(cacheKey, data)
      
      if (showToast) {
        toast.success('Crisis dashboard refreshed')
      }
    } catch (error) {
      const errorMsg = error.response?.data?.detail || 'Failed to load crisis dashboard'
      toast.error(errorMsg)
      console.error('Error loading crisis dashboard:', error)
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }, [getCached, setCached, dedupeRequest, toast])

  const monitorPolicy = useCallback(async () => {
    try {
      if (!selectedPolicy.trim()) {
        toast.error('Please enter a policy name')
        return
      }
      
      // Generate keywords from policy name (generic approach)
      // Extract meaningful words, remove common stop words, and create variations
      const policyLower = selectedPolicy.toLowerCase()
      const stopWords = new Set(['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from'])
      const policyWords = policyLower
        .split(/\s+/)
        .filter(w => w.length > 2 && !stopWords.has(w))
        .map(w => w.replace(/[^a-z0-9]/g, ''))
        .filter(w => w.length > 0)
      
      // Create keyword variations: individual words, combined, and hashtag-style
      const keywords = [
        ...policyWords,
        policyWords.join(''),
        policyLower.replace(/\s+/g, ''),
        ...policyWords.map(w => `#${w}`)
      ].filter(k => k.length > 0).join(',')
      
      // Use request deduplication
      const response = await dedupeRequest(
        `policy-monitor-${selectedPolicy}`,
        () => api.post('/crisis/monitor-policy', null, {
          params: {
            policy_name: selectedPolicy,
            keywords: keywords,
            time_window_hours: 168
          }
        })
      )
      
      setPolicyMonitoring(response.data.data)
      toast.success(`Policy monitoring completed for ${selectedPolicy}`)
    } catch (error) {
      toast.error('Failed to monitor policy')
      console.error('Error monitoring policy:', error)
    }
  }, [selectedPolicy, dedupeRequest, toast])

  useEffect(() => {
    loadCrisisDashboard()
  }, [loadCrisisDashboard])

  // Auto-refresh every 5 minutes for crisis monitoring (with cache)
  useAutoRefresh(() => loadCrisisDashboard(false, true), 300000, true)

  // Performance: Memoize computed values BEFORE early return (React Hooks rules)
  const crisisSignals = useMemo(() => dashboardData?.crisis_signals || [], [dashboardData?.crisis_signals])
  const escalationPrediction = useMemo(() => dashboardData?.escalation_prediction || {}, [dashboardData?.escalation_prediction])
  const hashtagIntel = useMemo(() => dashboardData?.hashtag_intelligence || {}, [dashboardData?.hashtag_intelligence])
  const sentimentVelocity = useMemo(() => dashboardData?.sentiment_velocity || {}, [dashboardData?.sentiment_velocity])

  // Calculate risk level (memoized)
  const escalationProb = useMemo(() => escalationPrediction.escalation_probability || 0, [escalationPrediction.escalation_probability])
  const riskLevel = useMemo(() => {
    return escalationProb > 0.8 ? 'critical' : escalationProb > 0.6 ? 'high' : escalationProb > 0.4 ? 'moderate' : 'low'
  }, [escalationProb])

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="h-8 bg-gray-200 rounded w-64 mb-2 animate-pulse"></div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[1, 2, 3].map((i) => (
            <CardSkeleton key={i} />
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="animate-slide-up">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-red-600 to-orange-600 bg-clip-text text-transparent">
              Crisis Detection Dashboard
            </h1>
            <p className="text-gray-600 mt-2">
              Early warning system for detecting and monitoring policy-related crises and citizen sentiment
            </p>
          </div>
          <button
            onClick={() => loadCrisisDashboard(true)}
            disabled={refreshing}
            className="inline-flex items-center gap-2 px-4 py-2 bg-white border border-gray-200 rounded-lg text-gray-700 hover:bg-gray-50 disabled:opacity-50"
          >
            <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>
      </div>

      {/* Risk Level Banner */}
      <div className={`rounded-xl shadow-lg p-6 border-2 ${
        riskLevel === 'critical' ? 'bg-red-50 border-red-300' :
        riskLevel === 'high' ? 'bg-orange-50 border-orange-300' :
        riskLevel === 'moderate' ? 'bg-yellow-50 border-yellow-300' :
        'bg-green-50 border-green-300'
      }`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className={`p-4 rounded-lg ${
              riskLevel === 'critical' ? 'bg-red-100' :
              riskLevel === 'high' ? 'bg-orange-100' :
              riskLevel === 'moderate' ? 'bg-yellow-100' :
              'bg-green-100'
            }`}>
              <Shield className={`h-8 w-8 ${
                riskLevel === 'critical' ? 'text-red-600' :
                riskLevel === 'high' ? 'text-orange-600' :
                riskLevel === 'moderate' ? 'text-yellow-600' :
                'text-green-600'
              }`} />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-900">
                Current Risk Level: <span className="capitalize">{riskLevel}</span>
              </h2>
              <p className="text-gray-700 mt-1">
                Escalation Probability: {(escalationProb * 100).toFixed(0)}%
              </p>
              {escalationPrediction.recommendation && (
                <p className="text-sm font-semibold text-gray-800 mt-2">
                  {escalationPrediction.recommendation}
                </p>
              )}
            </div>
          </div>
          {escalationPrediction.risk_factors && escalationPrediction.risk_factors.length > 0 && (
            <div className="text-right">
              <p className="text-sm font-semibold text-gray-700 mb-2">Risk Factors:</p>
              <div className="space-y-1">
                {escalationPrediction.risk_factors.map((factor, idx) => (
                  <div key={idx} className="text-xs text-gray-600">• {factor}</div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Crisis Signals */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Active Crisis Signals */}
        <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-red-500" />
              Active Crisis Signals
            </h2>
            <span className="px-3 py-1 bg-red-100 text-red-700 rounded-full text-sm font-semibold">
              {crisisSignals.length} Active
            </span>
          </div>
          
          {crisisSignals.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <CheckCircle className="h-12 w-12 mx-auto mb-2 text-green-500" />
              <p>No active crisis signals detected</p>
            </div>
          ) : (
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {crisisSignals.map((signal, idx) => (
                <div
                  key={idx}
                  className={`p-4 rounded-lg border-l-4 ${
                    signal.severity === 'critical' ? 'bg-red-50 border-red-500' :
                    signal.severity === 'high' ? 'bg-orange-50 border-orange-500' :
                    'bg-yellow-50 border-yellow-500'
                  }`}
                >
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="font-semibold text-gray-900">{signal.title}</h3>
                    <span className={`px-2 py-1 rounded text-xs font-semibold capitalize ${
                      signal.severity === 'critical' ? 'bg-red-200 text-red-800' :
                      signal.severity === 'high' ? 'bg-orange-200 text-orange-800' :
                      'bg-yellow-200 text-yellow-800'
                    }`}>
                      {signal.severity}
                    </span>
                  </div>
                  <p className="text-sm text-gray-700 mb-2">{signal.description}</p>
                  {signal.recommendation && (
                    <div className="mt-2 p-2 bg-white rounded border border-gray-200">
                      <p className="text-xs font-semibold text-gray-800">Recommendation:</p>
                      <p className="text-xs text-gray-700">{signal.recommendation}</p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Sentiment Velocity */}
        <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100">
          <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2 mb-4">
            <TrendingDown className="h-5 w-5 text-red-500" />
            Sentiment Velocity
          </h2>
          
          {sentimentVelocity.velocity_score > 0 ? (
            <div className="space-y-4">
              <div className="text-center">
                <div className="text-4xl font-bold text-red-600 mb-2">
                  {sentimentVelocity.velocity_percent > 0 ? '+' : ''}{sentimentVelocity.velocity_percent?.toFixed(1)}%
                </div>
                <p className="text-sm text-gray-600">Sentiment Change Rate</p>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="p-3 bg-gray-50 rounded-lg">
                  <p className="text-xs text-gray-600 mb-1">Recent Negative</p>
                  <p className="text-lg font-bold text-gray-900">
                    {sentimentVelocity.recent_negative_pct?.toFixed(1)}%
                  </p>
                </div>
                <div className="p-3 bg-gray-50 rounded-lg">
                  <p className="text-xs text-gray-600 mb-1">Earlier Negative</p>
                  <p className="text-lg font-bold text-gray-900">
                    {sentimentVelocity.earlier_negative_pct?.toFixed(1)}%
                  </p>
                </div>
              </div>
              
              {sentimentVelocity.velocity_score > 0.5 && (
                <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                  <p className="text-sm font-semibold text-red-900">⚠️ Rapid Deterioration Detected</p>
                  <p className="text-xs text-red-700 mt-1">
                    Sentiment is deteriorating rapidly. Immediate attention recommended.
                  </p>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <Activity className="h-12 w-12 mx-auto mb-2 text-gray-400" />
              <p>Insufficient data for velocity analysis</p>
            </div>
          )}
        </div>
      </div>

      {/* Hashtag Intelligence */}
      <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100">
        <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2 mb-4">
          <Hash className="h-5 w-5 text-blue-500" />
          Hashtag Intelligence
        </h2>
        
        {hashtagIntel.trending_hashtags && hashtagIntel.trending_hashtags.length > 0 ? (
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {hashtagIntel.trending_hashtags.slice(0, 6).map((hashtag, idx) => (
                <div
                  key={idx}
                  className="p-4 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg border border-blue-200"
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-bold text-blue-900">{hashtag.hashtag}</span>
                    <span className="px-2 py-1 bg-blue-200 text-blue-800 rounded text-xs font-semibold">
                      {hashtag.count} mentions
                    </span>
                  </div>
                  <div className="text-xs text-gray-600">
                    Growth Score: {hashtag.growth_score}
                  </div>
                  {hashtag.sources && hashtag.sources.length > 0 && (
                    <div className="text-xs text-gray-500 mt-1">
                      Sources: {hashtag.sources.length}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            <Hash className="h-12 w-12 mx-auto mb-2 text-gray-400" />
            <p>No trending hashtags detected</p>
          </div>
        )}
      </div>

      {/* Policy Monitoring */}
      <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100">
        <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2 mb-4">
          <Target className="h-5 w-5 text-purple-500" />
          Policy Monitoring
        </h2>
        
        <div className="mb-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
          <p className="text-sm text-blue-800 mb-1">
            <strong>Monitor any policy or issue:</strong> Enter the name of any policy, bill, legislation, or public issue.
          </p>
          <p className="text-xs text-blue-700">
            Examples: "Finance Bill 2024", "Healthcare Act", "Education Policy", "Housing Reform", "Tax Amendment", "Water Rights"
          </p>
        </div>
        
        <div className="flex items-center gap-4 mb-4">
          <input
            type="text"
            value={selectedPolicy}
            onChange={(e) => setSelectedPolicy(e.target.value)}
            placeholder="Enter any policy, bill, or issue name"
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            onKeyPress={(e) => {
              if (e.key === 'Enter') {
                monitorPolicy()
              }
            }}
          />
          <button
            onClick={monitorPolicy}
            className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 flex items-center gap-2"
          >
            <Zap className="h-4 w-4" />
            Monitor Policy
          </button>
        </div>
        
        {policyMonitoring && (
          <div className={`p-4 rounded-lg border-2 ${
            policyMonitoring.status === 'critical' ? 'bg-red-50 border-red-300' :
            policyMonitoring.status === 'high_risk' ? 'bg-orange-50 border-orange-300' :
            policyMonitoring.status === 'moderate_risk' ? 'bg-yellow-50 border-yellow-300' :
            'bg-green-50 border-green-300'
          }`}>
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-bold text-lg text-gray-900">{policyMonitoring.policy}</h3>
              <span className={`px-3 py-1 rounded-full text-sm font-semibold capitalize ${
                policyMonitoring.status === 'critical' ? 'bg-red-200 text-red-800' :
                policyMonitoring.status === 'high_risk' ? 'bg-orange-200 text-orange-800' :
                policyMonitoring.status === 'moderate_risk' ? 'bg-yellow-200 text-yellow-800' :
                'bg-green-200 text-green-800'
              }`}>
                {policyMonitoring.status.replace('_', ' ')}
              </span>
            </div>
            
            <div className="grid grid-cols-3 gap-4 mb-3">
              <div className="p-3 bg-white rounded-lg">
                <p className="text-xs text-gray-600 mb-1">Total Mentions</p>
                <p className="text-2xl font-bold text-gray-900">{policyMonitoring.total_mentions}</p>
              </div>
              <div className="p-3 bg-white rounded-lg">
                <p className="text-xs text-gray-600 mb-1">Negative Sentiment</p>
                <p className="text-2xl font-bold text-red-600">
                  {policyMonitoring.negative_sentiment_pct?.toFixed(1)}%
                </p>
              </div>
              <div className="p-3 bg-white rounded-lg">
                <p className="text-xs text-gray-600 mb-1">Velocity Score</p>
                <p className="text-2xl font-bold text-orange-600">
                  {policyMonitoring.sentiment_velocity?.velocity_score?.toFixed(2) || 'N/A'}
                </p>
              </div>
            </div>
            
            {policyMonitoring.recommendation && (
              <div className="p-3 bg-white rounded-lg border border-gray-200">
                <p className="text-sm font-semibold text-gray-800 mb-1">Recommendation:</p>
                <p className="text-sm text-gray-700">{policyMonitoring.recommendation}</p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Escalation Prediction Details */}
      {escalationPrediction.escalation_probability > 0 && (
        <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100">
          <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2 mb-4">
            <BarChart3 className="h-5 w-5 text-orange-500" />
            Escalation Prediction Analysis
          </h2>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <span className="font-semibold text-gray-700">Escalation Probability</span>
              <div className="flex items-center gap-4">
                <div className="w-64 h-4 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className={`h-full ${
                      escalationProb > 0.8 ? 'bg-red-600' :
                      escalationProb > 0.6 ? 'bg-orange-500' :
                      escalationProb > 0.4 ? 'bg-yellow-500' :
                      'bg-green-500'
                    }`}
                    style={{ width: `${escalationProb * 100}%` }}
                  />
                </div>
                <span className="font-bold text-lg text-gray-900">
                  {(escalationProb * 100).toFixed(0)}%
                </span>
              </div>
            </div>
            
            {escalationPrediction.risk_factors && escalationPrediction.risk_factors.length > 0 && (
              <div>
                <p className="font-semibold text-gray-700 mb-2">Risk Factors Identified:</p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                  {escalationPrediction.risk_factors.map((factor, idx) => (
                    <div key={idx} className="flex items-center gap-2 p-2 bg-red-50 rounded">
                      <AlertTriangle className="h-4 w-4 text-red-600 flex-shrink-0" />
                      <span className="text-sm text-gray-700">{factor}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

