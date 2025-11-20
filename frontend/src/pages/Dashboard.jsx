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
import { TrendingUp, Users, AlertTriangle, MessageSquare, Activity, ArrowUpRight, ArrowDownRight, RefreshCw, Settings, Clock, Sparkles } from 'lucide-react'
import CountyMap from '../components/CountyMap'
import { StatCardSkeleton, ChartSkeleton } from '../components/LoadingSkeleton'
import OnboardingTour from '../components/OnboardingTour'

const SENTIMENT_COLORS = {
  positive: '#009639',
  negative: '#DE2910',
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
      
      const insightsCacheKey = 'dashboard-insights-7'
      const trendsCacheKey = 'dashboard-trends-30'
      
      let insightsData = useCache ? getCached(insightsCacheKey) : null
      let trendsData = useCache ? getCached(trendsCacheKey) : null
      
      if (insightsData && trendsData && useCache) {
        setInsights(insightsData)
        setSentimentTrends(trendsData)
        setLoading(false)
        setRefreshing(false)
        return
      }
      
      const [insightsRes, trendsRes] = await Promise.all([
        dedupeRequest('dashboard-insights-7', () => api.get('/dashboard/insights', { params: { days: 7 } })),
        dedupeRequest('dashboard-trends-30', () => api.get('/dashboard/sentiment-trends', { params: { days: 30 } })),
      ])

      insightsData = insightsRes.data?.data || null
      trendsData = trendsRes.data?.data || null
      
      setCached(insightsCacheKey, insightsData)
      setCached(trendsCacheKey, trendsData)

      setInsights(insightsData)
      setSentimentTrends(trendsData)
      
      if (showToast) {
        toast.success('Dashboard data refreshed')
      }
    } catch (error) {
      const errorMsg = error.response?.data?.detail || 'Failed to load dashboard data'
      // Only show toast if explicitly requested
      if (showToast) {
        toast.error(errorMsg)
      }
      console.error('Error loading dashboard data:', error)
      // Set null data on error to show appropriate UI
      setInsights(null)
      setSentimentTrends(null)
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  const { connected, lastUpdateAt } = useRealtime(() => {
    loadDashboardData(false, false)
    setLastUpdatedAt(new Date())
  })

  useEffect(() => {
    loadDashboardData()
  }, [])

  useAutoRefresh(
    () => loadDashboardData(false, true),
    autoRefreshEnabled ? (connected ? 60000 : 30000) : 0,
    autoRefreshEnabled
  )

  useEffect(() => {
    setAutoRefreshEnabled(!connected)
  }, [connected])

  if (loading) {
    return (
      <div className="space-y-8 animate-fade-in">
        <div className="h-12 bg-gray-200 rounded-lg w-64 mb-4 animate-pulse"></div>
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
        <div className="text-center animate-fade-in max-w-md">
          <div className="relative mb-6">
            <div className="bg-gradient-to-br from-gray-50 to-gray-100 rounded-full p-6 w-20 h-20 mx-auto flex items-center justify-center shadow-lg border border-gray-200">
              <Activity className="h-10 w-10 text-gray-400" />
            </div>
          </div>
          <h3 className="text-2xl font-bold text-gray-900 mb-3">No Data Available</h3>
          <p className="text-gray-600 mb-8">
            We couldn't load your dashboard insights. This might be a temporary issue.
          </p>
          <button
            onClick={loadDashboardData}
            className="inline-flex items-center gap-2 px-6 py-3 bg-gray-900 text-white rounded-lg font-semibold shadow-md hover:shadow-lg transition-all duration-200 hover:bg-gray-800"
          >
            <RefreshCw className="h-4 w-4" />
            Try Again
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
      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <h1 className="text-4xl font-bold text-gray-900">Dashboard</h1>
            <div className={`px-2.5 py-1 rounded-md text-xs font-semibold flex items-center gap-1.5 ${
              connected 
                ? 'bg-green-50 text-green-700 border border-green-200' 
                : 'bg-gray-100 text-gray-600 border border-gray-200'
            }`}>
              <span className={`w-1.5 h-1.5 rounded-full ${connected ? 'bg-green-500' : 'bg-gray-400'}`}></span>
              {connected ? 'Live' : 'Polling'}
            </div>
          </div>
          <p className="text-gray-600 text-sm">Welcome back, {user?.email?.split('@')[0] || 'User'}</p>
        </div>
        <div className="flex items-center gap-2">
          {lastUpdatedAt && (
            <div className="flex items-center gap-2 px-3 py-1.5 bg-gray-50 rounded-lg border border-gray-200 text-xs text-gray-600">
              <Clock className="h-3.5 w-3.5" />
              <span>Updated {new Date(lastUpdatedAt).toLocaleTimeString()}</span>
            </div>
          )}
          <button
            onClick={() => loadDashboardData(true, false)}
            disabled={refreshing}
            className="inline-flex items-center gap-2 px-4 py-2 bg-white border border-gray-200 rounded-lg text-gray-700 hover:bg-gray-50 disabled:opacity-50 transition-all duration-200 text-sm font-medium shadow-sm hover:shadow"
          >
            <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
            Refresh
          </button>
          <button
            onClick={() => setAutoRefreshEnabled((v) => !v)}
            className={`p-2 rounded-lg transition-all duration-200 ${
              autoRefreshEnabled 
                ? 'bg-gray-900 text-white' 
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
            title={autoRefreshEnabled ? 'Disable auto-refresh' : 'Enable auto-refresh'}
          >
            <Settings className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Feedback */}
        <div className="stat-card p-6 group cursor-pointer">
          <div className="flex items-center justify-between mb-4">
            <div className="stat-card-icon">
              <MessageSquare className="h-5 w-5 text-kenya-red-600" />
            </div>
            <ArrowUpRight className="h-4 w-4 text-gray-400 group-hover:text-kenya-red-600 transition-colors" />
          </div>
          <p className="stat-card-label mb-2">Total Feedback</p>
          <p className="stat-card-value mb-3">
            {insights.total_feedback.toLocaleString()}
          </p>
          <div className="flex items-center gap-2 text-xs text-gray-600">
            <span>Last 7 days</span>
            <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
              deltas.total_feedback_pct >= 0 
                ? 'bg-green-50 text-green-700' 
                : 'bg-red-50 text-red-700'
            }`}>
              {deltas.total_feedback_pct >= 0 ? '↑' : '↓'} {Math.abs(deltas.total_feedback_pct)}%
            </span>
          </div>
        </div>

        {/* Positive Sentiment */}
        <div className="stat-card p-6 group cursor-pointer">
          <div className="flex items-center justify-between mb-4">
            <div className="stat-card-icon" style={{ background: 'linear-gradient(135deg, rgba(0, 150, 57, 0.1) 0%, rgba(0, 150, 57, 0.05) 100%)' }}>
              <TrendingUp className="h-5 w-5 text-kenya-green-600" />
            </div>
            {sentimentChange === 'up' ? (
              <ArrowUpRight className="h-4 w-4 text-gray-400 group-hover:text-kenya-green-600 transition-colors" />
            ) : (
              <ArrowDownRight className="h-4 w-4 text-gray-400 group-hover:text-red-600 transition-colors" />
            )}
          </div>
          <p className="stat-card-label mb-2">Positive Sentiment</p>
          <p className="stat-card-value mb-3" style={{ color: '#009639' }}>
            {positiveCount}
          </p>
          <div className="flex items-center gap-2 text-xs text-gray-600">
            <span>{insights.total_feedback > 0 ? `${((positiveCount / insights.total_feedback) * 100).toFixed(1)}% of total` : 'No data'}</span>
            <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${deltas.positive_pct >= 0 ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'}`}>
              {deltas.positive_pct >= 0 ? '↑' : '↓'} {Math.abs(deltas.positive_pct)}%
            </span>
          </div>
        </div>

        {/* Active Alerts */}
        <div className="stat-card p-6 group cursor-pointer">
          <div className="flex items-center justify-between mb-4">
            <div className="stat-card-icon">
              <AlertTriangle className="h-5 w-5 text-kenya-red-600" />
            </div>
            {totalAlerts > 0 && (
              <span className="px-2 py-1 bg-red-100 text-red-700 text-xs font-semibold rounded-full">
                {totalAlerts}
              </span>
            )}
          </div>
          <p className="stat-card-label mb-2">Active Alerts</p>
          <p className="stat-card-value mb-3" style={{ color: '#DE2910' }}>
            {totalAlerts}
          </p>
          <div className="text-xs text-gray-600">Require attention</div>
        </div>

        {/* Top Sector */}
        <div className="stat-card p-6 group cursor-pointer">
          <div className="flex items-center justify-between mb-4">
            <div className="stat-card-icon" style={{ background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(139, 92, 246, 0.05) 100%)' }}>
              <Users className="h-5 w-5 text-purple-600" />
            </div>
            <Sparkles className="h-4 w-4 text-gray-400 group-hover:text-purple-600 transition-colors" />
          </div>
          <p className="stat-card-label mb-2">Top Sector</p>
          <p className="stat-card-value mb-3 text-2xl">
            {sectorData[0]?.name ? sectorData[0].name.charAt(0).toUpperCase() + sectorData[0].name.slice(1) : 'N/A'}
          </p>
          <div className="text-xs text-gray-600">
            {sectorData[0]?.value || 0} feedback items
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Sentiment Distribution */}
        {sentimentData.some(d => d.value > 0) ? (
          <div className="glass-card p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg font-semibold text-gray-900">Sentiment Distribution</h2>
              <div className="flex gap-3">
                {sentimentData.map((entry, index) => (
                  <div key={index} className="flex items-center gap-1.5">
                    <div 
                      className="w-2 h-2 rounded-full" 
                      style={{ backgroundColor: SENTIMENT_COLORS[entry.name.toLowerCase()] || '#6b7280' }}
                    />
                    <span className="text-xs text-gray-600">{entry.name}</span>
                  </div>
                ))}
              </div>
            </div>
            <ResponsiveContainer width="100%" height={280}>
              <PieChart>
                <Pie
                  data={sentimentData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={90}
                  innerRadius={35}
                  fill="#8884d8"
                  dataKey="value"
                  animationBegin={0}
                  animationDuration={600}
                >
                  {sentimentData.map((entry, index) => (
                    <Cell 
                      key={`cell-${index}`} 
                      fill={SENTIMENT_COLORS[entry.name.toLowerCase()] || '#6b7280'} 
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
          <div className="glass-card p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-6">Sentiment Distribution</h2>
            <div className="flex flex-col items-center justify-center h-[280px] text-gray-500">
              <Activity className="h-12 w-12 mb-3 text-gray-300" />
              <p className="text-sm">No sentiment data available yet</p>
            </div>
          </div>
        )}

        {/* Sector Distribution */}
        {sectorData.length > 0 ? (
          <div className="glass-card p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg font-semibold text-gray-900">Sector Distribution</h2>
              <span className="text-xs text-gray-600 font-medium">{sectorData.length} sectors</span>
            </div>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={sectorData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
                <XAxis 
                  dataKey="name" 
                  tick={{ fill: '#6b7280', fontSize: 11 }}
                  axisLine={{ stroke: '#e5e7eb' }}
                />
                <YAxis 
                  tick={{ fill: '#6b7280', fontSize: 11 }}
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
                  radius={[6, 6, 0, 0]}
                  animationDuration={600}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <div className="glass-card p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-6">Sector Distribution</h2>
            <div className="flex flex-col items-center justify-center h-[280px] text-gray-500">
              <Activity className="h-12 w-12 mb-3 text-gray-300" />
              <p className="text-sm">No sector data available yet</p>
            </div>
          </div>
        )}
      </div>

      {/* Sentiment Trends */}
      {trendsData.length > 0 ? (
        <div className="glass-card p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold text-gray-900">Sentiment Trends (30 Days)</h2>
            <div className="flex gap-4 text-xs">
              <div className="flex items-center gap-1.5">
                <div className="w-2 h-2 rounded-full bg-green-500" />
                <span className="text-gray-600">Positive</span>
              </div>
              <div className="flex items-center gap-1.5">
                <div className="w-2 h-2 rounded-full bg-red-500" />
                <span className="text-gray-600">Negative</span>
              </div>
              <div className="flex items-center gap-1.5">
                <div className="w-2 h-2 rounded-full bg-gray-500" />
                <span className="text-gray-600">Neutral</span>
              </div>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={350}>
            <LineChart data={trendsData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
              <XAxis 
                dataKey="date" 
                tick={{ fill: '#6b7280', fontSize: 11 }}
                axisLine={{ stroke: '#e5e7eb' }}
              />
              <YAxis 
                tick={{ fill: '#6b7280', fontSize: 11 }}
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
                wrapperStyle={{ paddingTop: '20px', fontSize: '12px' }}
                iconType="line"
              />
              <Line 
                type="monotone" 
                dataKey="positive" 
                stroke="#10b981" 
                strokeWidth={2}
                dot={{ fill: '#10b981', r: 3 }}
                activeDot={{ r: 5 }}
                animationDuration={600}
              />
              <Line 
                type="monotone" 
                dataKey="negative" 
                stroke="#ef4444" 
                strokeWidth={2}
                dot={{ fill: '#ef4444', r: 3 }}
                activeDot={{ r: 5 }}
                animationDuration={600}
              />
              <Line 
                type="monotone" 
                dataKey="neutral" 
                stroke="#6b7280" 
                strokeWidth={2}
                dot={{ fill: '#6b7280', r: 3 }}
                activeDot={{ r: 5 }}
                animationDuration={600}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      ) : (
        <div className="glass-card p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-6">Sentiment Trends (30 Days)</h2>
          <div className="flex flex-col items-center justify-center h-[350px] text-gray-500">
            <Activity className="h-12 w-12 mb-3 text-gray-300" />
            <p className="text-sm">No trend data available yet</p>
          </div>
        </div>
      )}

      {/* Bottom Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Issues */}
        <div className="glass-card p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-6">Top Issues</h2>
          {insights.top_issues && insights.top_issues.length > 0 ? (
            <div className="space-y-3">
              {insights.top_issues.slice(0, 5).map((issue, index) => (
                <div 
                  key={index} 
                  className="group flex items-center justify-between p-4 rounded-lg bg-gray-50 border border-gray-200 hover:border-gray-300 hover:bg-gray-100 transition-all duration-200"
                >
                  <div className="flex items-center gap-4">
                    <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-gray-900 text-white font-semibold text-sm">
                      {index + 1}
                    </div>
                    <div>
                      <p className="font-semibold text-gray-900 capitalize">{issue.sector}</p>
                      <p className="text-xs text-gray-600">{issue.count} feedback items</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-12 text-gray-500">
              <Activity className="h-10 w-10 mb-3 text-gray-300" />
              <p className="text-sm">No issues data available yet</p>
            </div>
          )}
        </div>

        {/* County Heatmap */}
        <div className="glass-card p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-6">County Heatmap</h2>
          <CountyMap days={7} />
        </div>
      </div>

      <OnboardingTour />
    </div>
  )
}
