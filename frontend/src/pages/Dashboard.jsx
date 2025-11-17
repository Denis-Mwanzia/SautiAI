import { useEffect, useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import api from '../services/api'
import { useToast } from '../contexts/ToastContext'
import { useAutoRefresh } from '../hooks/useAutoRefresh'
import { useRealtime } from '../hooks/useRealtime'
import { useApiCache } from '../hooks/useApiCache'
import { useRequestDeduplication } from '../hooks/useRequestDeduplication'
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import { TrendingUp, Users, AlertTriangle, MessageSquare, Activity, ArrowUpRight, ArrowDownRight, RefreshCw, Settings } from 'lucide-react'
import CountyMap from '../components/CountyMap'
import { StatCardSkeleton, ChartSkeleton } from '../components/LoadingSkeleton'
import OnboardingTour from '../components/OnboardingTour'

const COLORS = ['#0ea5e9', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899']
const SENTIMENT_COLORS = {
  positive: '#10b981',
  negative: '#ef4444',
  neutral: '#6b7280'
}

export default function Dashboard() {
  const { user } = useAuth()
  const toast = useToast()
  const { getCached, setCached } = useApiCache()
  const { dedupeRequest } = useRequestDeduplication()
  const [insights, setInsights] = useState(null)
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [sentimentTrends, setSentimentTrends] = useState(null)
  const [autoRefreshEnabled, setAutoRefreshEnabled] = useState(true)
  const [lastUpdatedAt, setLastUpdatedAt] = useState(null)

  const loadDashboardData = async (showToast = false, useCache = true) => {
    try {
      setRefreshing(true)
      
      // Check cache first
      const insightsCacheKey = 'dashboard-insights-7'
      const trendsCacheKey = 'dashboard-trends-30'
      
      let insightsData = useCache ? getCached(insightsCacheKey) : null
      let trendsData = useCache ? getCached(trendsCacheKey) : null
      
      // If cache is fresh, use it and skip API call
      if (insightsData && trendsData && useCache) {
        setInsights(insightsData)
        setSentimentTrends(trendsData)
        setLoading(false)
        setRefreshing(false)
        return
      }
      
      // Use request deduplication to prevent duplicate concurrent requests
      const [insightsRes, trendsRes] = await Promise.all([
        dedupeRequest('dashboard-insights-7', () => api.get('/dashboard/insights?days=7')),
        dedupeRequest('dashboard-trends-30', () => api.get('/dashboard/sentiment-trends?days=30')),
      ])

      insightsData = insightsRes.data.data
      trendsData = trendsRes.data.data
      
      // Cache the results
      setCached(insightsCacheKey, insightsData)
      setCached(trendsCacheKey, trendsData)

      setInsights(insightsData)
      setSentimentTrends(trendsData)
      
      if (showToast) {
        toast.success('Dashboard data refreshed')
      }
    } catch (error) {
      const errorMsg = error.response?.data?.detail || 'Failed to load dashboard data'
      toast.error(errorMsg)
      console.error('Error loading dashboard data:', error)
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  // Realtime updates: when a message arrives, reload lightweight
  const { connected, lastUpdateAt } = useRealtime(() => {
    // Reload without cache to reflect new data
    loadDashboardData(false, false)
    setLastUpdatedAt(new Date())
  })

  useEffect(() => {
    loadDashboardData()
  }, [])

  // Smart auto-refresh: longer interval when realtime is connected
  // Only refresh if cache is stale
  useAutoRefresh(
    () => loadDashboardData(false, true), // Use cache check
    autoRefreshEnabled ? (connected ? 60000 : 30000) : 0, // 60s if realtime, 30s if polling
    autoRefreshEnabled
  )

  // If realtime is connected, we can disable polling auto-refresh
  useEffect(() => {
    setAutoRefreshEnabled(!connected)
  }, [connected])

  if (loading) {
    return (
      <div className="space-y-6 animate-fade-in">
        <div className="flex items-center justify-between">
          <div>
            <div className="h-8 bg-gray-200 rounded w-64 mb-2 animate-pulse"></div>
            <div className="h-4 bg-gray-200 rounded w-96 animate-pulse"></div>
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[1, 2, 3, 4].map((i) => (
            <StatCardSkeleton key={i} />
          ))}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <ChartSkeleton />
          <ChartSkeleton />
        </div>
      </div>
    )
  }

  if (!insights) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center animate-fade-in">
          <div className="bg-white rounded-full p-4 w-20 h-20 mx-auto mb-4 flex items-center justify-center shadow-lg">
            <Activity className="h-10 w-10 text-gray-400" />
          </div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">No data available</h3>
          <p className="text-gray-600 mb-6">Unable to load dashboard insights</p>
          <button
            onClick={loadDashboardData}
            className="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
          >
            Retry
          </button>
        </div>
      </div>
    )
  }

  const sentimentData = Object.entries(insights.sentiment_distribution).map(([key, value]) => ({
    name: key.charAt(0).toUpperCase() + key.slice(1),
    value,
  }))

  const sectorData = Object.entries(insights.sector_distribution).map(([key, value]) => ({
    name: key.charAt(0).toUpperCase() + key.slice(1),
    value,
  }))

  const trendsData = sentimentTrends?.trends 
    ? Object.entries(sentimentTrends.trends).map(([date, data]) => ({
        date: date.length > 10 ? date.substring(5, 10) : date,
        positive: data.positive || 0,
        negative: data.negative || 0,
        neutral: data.neutral || 0,
      }))
    : []

  const totalAlerts = insights.recent_alerts?.filter((a) => !a.acknowledged).length || 0
  const positiveCount = insights.sentiment_distribution.positive || 0
  const negativeCount = insights.sentiment_distribution.negative || 0
  const sentimentChange = positiveCount > negativeCount ? 'up' : 'down'
  const deltas = insights.deltas || { total_feedback_pct: 0, positive_pct: 0, negative_pct: 0, neutral_pct: 0 }

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div className="animate-slide-up">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-primary-600 to-primary-800 bg-clip-text text-transparent">
          Dashboard
        </h1>
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mt-2 gap-2">
          <p className="text-gray-600 flex items-center gap-2">
            <span>Welcome back,</span>
            <span className="font-semibold text-gray-900">{user?.email?.split('@')[0]}</span>
          </p>
          <div className="flex items-center gap-3 text-sm">
            <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full border ${connected ? 'border-green-200 text-green-700 bg-green-50' : 'border-gray-200 text-gray-700 bg-gray-50'}`}>
              <span className={`w-2 h-2 rounded-full ${connected ? 'bg-green-500' : 'bg-gray-400'}`}></span>
              {connected ? 'Live' : 'Polling'}
            </span>
            {lastUpdatedAt && (
              <span className="text-gray-500">Last updated {new Date(lastUpdatedAt).toLocaleTimeString()}</span>
            )}
            <button
              onClick={() => loadDashboardData(true, false)}
              disabled={refreshing}
              className="inline-flex items-center gap-2 px-3 py-1.5 bg-white border border-gray-200 rounded-md text-gray-700 hover:bg-gray-50 disabled:opacity-50"
            >
              <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
              Refresh
            </button>
            <button
              onClick={() => setAutoRefreshEnabled((v) => !v)}
              className="text-gray-500 hover:text-gray-700"
            >
              <Settings className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Total Feedback Card */}
        <div className="bg-gradient-to-br from-white to-primary-50 rounded-xl shadow-lg p-6 border border-primary-100 card-hover animate-scale-in">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-primary-100 rounded-lg">
              <MessageSquare className="h-6 w-6 text-primary-600" />
            </div>
            <ArrowUpRight className="h-5 w-5 text-primary-400" />
          </div>
          <p className="text-sm font-medium text-gray-600 mb-1">Total Feedback</p>
          <p className="text-3xl font-bold text-gray-900">
            {insights.total_feedback.toLocaleString()}
          </p>
          <p className="text-xs text-gray-500 mt-2 flex items-center gap-2">
            <span>Last {7} days</span>
            <span className={`px-2 py-0.5 rounded-full ${deltas.total_feedback_pct >= 0 ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'}`}>
              {deltas.total_feedback_pct >= 0 ? '+' : ''}{deltas.total_feedback_pct}% vs prev
            </span>
          </p>
        </div>

        {/* Positive Sentiment Card */}
        <div className="bg-gradient-to-br from-white to-green-50 rounded-xl shadow-lg p-6 border border-green-100 card-hover animate-scale-in" style={{ animationDelay: '0.1s' }}>
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-green-100 rounded-lg">
              <TrendingUp className="h-6 w-6 text-green-600" />
            </div>
            {sentimentChange === 'up' ? (
              <ArrowUpRight className="h-5 w-5 text-green-500" />
            ) : (
              <ArrowDownRight className="h-5 w-5 text-red-500" />
            )}
          </div>
          <p className="text-sm font-medium text-gray-600 mb-1">Positive Sentiment</p>
          <p className="text-3xl font-bold text-green-600">
            {positiveCount}
          </p>
          <p className="text-xs text-gray-500 mt-2 flex items-center gap-2">
            <span>
              {insights.total_feedback > 0 
                ? `${((positiveCount / insights.total_feedback) * 100).toFixed(1)}% of total`
                : 'No data'}
            </span>
            <span className={`px-2 py-0.5 rounded-full ${deltas.positive_pct >= 0 ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'}`}>
              {deltas.positive_pct >= 0 ? '+' : ''}{deltas.positive_pct}% vs prev
            </span>
          </p>
        </div>

        {/* Active Alerts Card */}
        <div className="bg-gradient-to-br from-white to-red-50 rounded-xl shadow-lg p-6 border border-red-100 card-hover animate-scale-in" style={{ animationDelay: '0.2s' }}>
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-red-100 rounded-lg">
              <AlertTriangle className="h-6 w-6 text-red-600" />
            </div>
            {totalAlerts > 0 && (
              <span className="px-2 py-1 bg-red-500 text-white text-xs font-bold rounded-full">
                {totalAlerts}
              </span>
            )}
          </div>
          <p className="text-sm font-medium text-gray-600 mb-1">Active Alerts</p>
          <p className="text-3xl font-bold text-red-600">
            {totalAlerts}
          </p>
          <p className="text-xs text-gray-500 mt-2">Require attention</p>
        </div>

        {/* Top Sector Card */}
        <div className="bg-gradient-to-br from-white to-purple-50 rounded-xl shadow-lg p-6 border border-purple-100 card-hover animate-scale-in" style={{ animationDelay: '0.3s' }}>
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-purple-100 rounded-lg">
              <Users className="h-6 w-6 text-purple-600" />
            </div>
            <Activity className="h-5 w-5 text-purple-400" />
          </div>
          <p className="text-sm font-medium text-gray-600 mb-1">Top Sector</p>
          <p className="text-2xl font-bold text-gray-900">
            {sectorData[0]?.name || 'N/A'}
          </p>
          <p className="text-xs text-gray-500 mt-2">
            {sectorData[0]?.value || 0} feedback items
          </p>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Sentiment Distribution */}
        {sentimentData.some(d => d.value > 0) ? (
          <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100 animate-slide-up">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-gray-900">Sentiment Distribution</h2>
              <div className="flex gap-2">
                {sentimentData.map((entry, index) => (
                  <div key={index} className="flex items-center gap-1">
                    <div 
                      className="w-3 h-3 rounded-full" 
                      style={{ backgroundColor: SENTIMENT_COLORS[entry.name.toLowerCase()] || COLORS[index] }}
                    />
                    <span className="text-xs text-gray-600">{entry.name}</span>
                  </div>
                ))}
              </div>
            </div>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={sentimentData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={100}
                  innerRadius={40}
                  fill="#8884d8"
                  dataKey="value"
                  animationBegin={0}
                  animationDuration={800}
                >
                  {sentimentData.map((entry, index) => (
                    <Cell 
                      key={`cell-${index}`} 
                      fill={SENTIMENT_COLORS[entry.name.toLowerCase()] || COLORS[index]} 
                    />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'white', 
                    border: '1px solid #e5e7eb', 
                    borderRadius: '8px',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100 animate-slide-up">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Sentiment Distribution</h2>
            <div className="flex flex-col items-center justify-center h-[300px] text-gray-500">
              <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
                <Activity className="h-8 w-8 text-gray-400" />
              </div>
              <p className="text-center">No sentiment data available yet</p>
              <p className="text-sm text-gray-400 mt-1">Analyzing feedback...</p>
            </div>
          </div>
        )}

        {/* Sector Distribution */}
        {sectorData.length > 0 ? (
          <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100 animate-slide-up" style={{ animationDelay: '0.1s' }}>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-gray-900">Sector Distribution</h2>
              <span className="text-sm text-gray-500">{sectorData.length} sectors</span>
            </div>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={sectorData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
                <XAxis 
                  dataKey="name" 
                  tick={{ fill: '#6b7280', fontSize: 12 }}
                  axisLine={{ stroke: '#e5e7eb' }}
                />
                <YAxis 
                  tick={{ fill: '#6b7280', fontSize: 12 }}
                  axisLine={{ stroke: '#e5e7eb' }}
                />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'white', 
                    border: '1px solid #e5e7eb', 
                    borderRadius: '8px',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                  }}
                  cursor={{ fill: 'rgba(14, 165, 233, 0.1)' }}
                />
                <Bar 
                  dataKey="value" 
                  fill="#0ea5e9" 
                  radius={[8, 8, 0, 0]}
                  animationDuration={800}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100 animate-slide-up" style={{ animationDelay: '0.1s' }}>
            <h2 className="text-xl font-bold text-gray-900 mb-4">Sector Distribution</h2>
            <div className="flex flex-col items-center justify-center h-[300px] text-gray-500">
              <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
                <Activity className="h-8 w-8 text-gray-400" />
              </div>
              <p className="text-center">No sector data available yet</p>
              <p className="text-sm text-gray-400 mt-1">Analyzing feedback...</p>
            </div>
          </div>
        )}
      </div>

      {/* Sentiment Trends */}
      {trendsData.length > 0 ? (
        <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100 animate-slide-up">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-gray-900">Sentiment Trends (30 Days)</h2>
            <div className="flex gap-4 text-sm">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-green-500" />
                <span className="text-gray-600">Positive</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-red-500" />
                <span className="text-gray-600">Negative</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-gray-500" />
                <span className="text-gray-600">Neutral</span>
              </div>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={400}>
            <LineChart data={trendsData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
              <XAxis 
                dataKey="date" 
                tick={{ fill: '#6b7280', fontSize: 12 }}
                axisLine={{ stroke: '#e5e7eb' }}
              />
              <YAxis 
                tick={{ fill: '#6b7280', fontSize: 12 }}
                axisLine={{ stroke: '#e5e7eb' }}
              />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: 'white', 
                  border: '1px solid #e5e7eb', 
                  borderRadius: '8px',
                  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                }}
              />
              <Legend 
                wrapperStyle={{ paddingTop: '20px' }}
                iconType="line"
              />
              <Line 
                type="monotone" 
                dataKey="positive" 
                stroke="#10b981" 
                strokeWidth={3}
                dot={{ fill: '#10b981', r: 4 }}
                activeDot={{ r: 6 }}
                animationDuration={800}
              />
              <Line 
                type="monotone" 
                dataKey="negative" 
                stroke="#ef4444" 
                strokeWidth={3}
                dot={{ fill: '#ef4444', r: 4 }}
                activeDot={{ r: 6 }}
                animationDuration={800}
              />
              <Line 
                type="monotone" 
                dataKey="neutral" 
                stroke="#6b7280" 
                strokeWidth={3}
                dot={{ fill: '#6b7280', r: 4 }}
                activeDot={{ r: 6 }}
                animationDuration={800}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      ) : (
        <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100 animate-slide-up">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Sentiment Trends (30 Days)</h2>
          <div className="flex flex-col items-center justify-center h-[400px] text-gray-500">
            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
              <Activity className="h-8 w-8 text-gray-400" />
            </div>
            <p className="text-center">No trend data available yet</p>
          </div>
        </div>
      )}

      {/* Bottom Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Issues */}
        <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100 animate-slide-up">
          <h2 className="text-xl font-bold text-gray-900 mb-6">Top Issues</h2>
          {insights.top_issues && insights.top_issues.length > 0 ? (
            <div className="space-y-3">
              {insights.top_issues.slice(0, 5).map((issue, index) => (
                <div 
                  key={index} 
                  className="flex items-center justify-between p-4 bg-gradient-to-r from-gray-50 to-white rounded-lg border border-gray-100 hover:border-primary-200 hover:shadow-md transition-all duration-200 group"
                >
                  <div className="flex items-center gap-4">
                    <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-primary-100 text-primary-600 font-bold group-hover:bg-primary-200 transition-colors">
                      {index + 1}
                    </div>
                    <div>
                      <p className="font-semibold text-gray-900 capitalize">{issue.sector}</p>
                      <p className="text-sm text-gray-600">{issue.count} feedback items</p>
                    </div>
                  </div>
                  <div className="w-2 h-2 rounded-full bg-primary-500 opacity-0 group-hover:opacity-100 transition-opacity" />
                </div>
              ))}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-12 text-gray-500">
              <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
                <Activity className="h-8 w-8 text-gray-400" />
              </div>
              <p>No issues data available yet</p>
            </div>
          )}
        </div>

        {/* County Heatmap Map */}
        <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100 animate-slide-up" style={{ animationDelay: '0.1s' }}>
          <h2 className="text-xl font-bold text-gray-900 mb-6">County Heatmap</h2>
          <CountyMap days={7} />
        </div>
      </div>
    </div>
  )
}

