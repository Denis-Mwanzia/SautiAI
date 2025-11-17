import { useEffect, useState, useMemo, useCallback } from 'react'
import api from '../services/api'
import { useApiCache } from '../hooks/useApiCache'
import { useRequestDeduplication } from '../hooks/useRequestDeduplication'
import {
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
import { Shield, Clock, CheckCircle, XCircle, TrendingUp, Building2 } from 'lucide-react'

const COLORS = ['#10b981', '#f59e0b', '#ef4444', '#6b7280']

export default function Transparency() {
  const [metrics, setMetrics] = useState(null)
  const [agencies, setAgencies] = useState([])
  const [loading, setLoading] = useState(true)
  const [days, setDays] = useState(30)
  const { getCached, setCached } = useApiCache()
  const { dedupeRequest } = useRequestDeduplication()

  const loadTransparencyData = useCallback(async () => {
    try {
      setLoading(true)
      
      // Check cache
      const metricsCacheKey = `transparency-metrics-${days}`
      const agenciesCacheKey = `transparency-agencies-${days}`
      
      const cachedMetrics = getCached(metricsCacheKey)
      const cachedAgencies = getCached(agenciesCacheKey)
      
      if (cachedMetrics && cachedAgencies) {
        setMetrics(cachedMetrics)
        setAgencies(cachedAgencies)
        setLoading(false)
        return
      }
      
      // Parallel requests with deduplication
      const [metricsRes, agenciesRes] = await Promise.all([
        dedupeRequest(metricsCacheKey, () => api.get(`/transparency/metrics?days=${days}`)),
        dedupeRequest(agenciesCacheKey, () => api.get(`/transparency/agencies?days=${days}`))
      ])
      
      const metricsData = metricsRes?.data?.data
      const agenciesData = agenciesRes?.data?.data || []
      
      setMetrics(metricsData)
      setAgencies(agenciesData)
      
      // Cache results
      setCached(metricsCacheKey, metricsData)
      setCached(agenciesCacheKey, agenciesData)
    } catch (error) {
      console.error('Error loading transparency data:', error)
      // Set defaults on error to prevent crashes
      setMetrics({
        period_days: days,
        total_issues: 0,
        acknowledged_count: 0,
        resolved_count: 0,
        response_rate: 0,
        resolution_rate: 0,
        average_response_time_hours: 0,
        status_breakdown: { pending: 0, acknowledged: 0, resolved: 0, closed: 0 },
        agency_performance: [],
        total_responses: 0
      })
      setAgencies([])
    } finally {
      setLoading(false)
    }
  }, [days, getCached, setCached, dedupeRequest])

  useEffect(() => {
    loadTransparencyData()
  }, [loadTransparencyData])

  // Memoize computed data to avoid recalculation on every render
  // MUST be called before any conditional returns (React Hooks rules)
  const statusData = useMemo(() => {
    return metrics?.status_breakdown ? Object.entries(metrics.status_breakdown).map(([key, value]) => ({
      name: key.charAt(0).toUpperCase() + key.slice(1),
      value
    })) : []
  }, [metrics?.status_breakdown])

  const agencyData = useMemo(() => {
    return agencies.slice(0, 10).map(agency => ({
      name: agency.agency_name?.length > 20 ? agency.agency_name.substring(0, 20) + '...' : (agency.agency_name || ''),
      responseRate: agency.response_rate || 0,
      resolutionRate: agency.resolution_rate || 0
    }))
  }, [agencies])

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-4 border-primary-200 border-t-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600 animate-pulse">Loading transparency metrics...</p>
        </div>
      </div>
    )
  }

  if (!metrics) {
    return (
      <div className="bg-white rounded-2xl shadow-lg p-12 text-center">
        <Shield className="h-16 w-16 text-gray-400 mx-auto mb-4" />
        <h3 className="text-xl font-semibold text-gray-700 mb-2">No Transparency Data</h3>
        <p className="text-gray-600">Transparency metrics will appear here once government responses are recorded</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-primary-600 to-primary-800 bg-clip-text text-transparent">
            Transparency & Responsiveness
          </h1>
          <p className="text-gray-600 mt-1">Track government agency accountability and response metrics</p>
        </div>
        <select
          value={days}
          onChange={(e) => setDays(Number(e.target.value))}
          className="px-4 py-2 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none"
        >
          <option value={7}>Last 7 days</option>
          <option value={30}>Last 30 days</option>
          <option value={90}>Last 90 days</option>
        </select>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl p-6 text-white shadow-xl">
          <div className="flex items-center justify-between mb-4">
            <Shield className="h-8 w-8" />
            <span className="text-blue-200 text-sm">Total Issues</span>
          </div>
          <div className="text-3xl font-bold">{metrics.total_issues || 0}</div>
          <div className="text-blue-200 text-sm mt-2">Issues requiring response</div>
        </div>

        <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-2xl p-6 text-white shadow-xl">
          <div className="flex items-center justify-between mb-4">
            <CheckCircle className="h-8 w-8" />
            <span className="text-green-200 text-sm">Response Rate</span>
          </div>
          <div className="text-3xl font-bold">{metrics.response_rate || 0}%</div>
          <div className="text-green-200 text-sm mt-2">{metrics.acknowledged_count || 0} acknowledged</div>
        </div>

        <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-2xl p-6 text-white shadow-xl">
          <div className="flex items-center justify-between mb-4">
            <TrendingUp className="h-8 w-8" />
            <span className="text-purple-200 text-sm">Resolution Rate</span>
          </div>
          <div className="text-3xl font-bold">{metrics.resolution_rate || 0}%</div>
          <div className="text-purple-200 text-sm mt-2">{metrics.resolved_count || 0} resolved</div>
        </div>

        <div className="bg-gradient-to-br from-orange-500 to-orange-600 rounded-2xl p-6 text-white shadow-xl">
          <div className="flex items-center justify-between mb-4">
            <Clock className="h-8 w-8" />
            <span className="text-orange-200 text-sm">Avg Response Time</span>
          </div>
          <div className="text-3xl font-bold">{metrics.average_response_time_hours || 0}h</div>
          <div className="text-orange-200 text-sm mt-2">Hours to respond</div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Status Breakdown */}
        <div className="bg-white rounded-2xl shadow-lg p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Issue Status Breakdown</h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={statusData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {statusData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Agency Performance */}
        <div className="bg-white rounded-2xl shadow-lg p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Agency Response Rates</h2>
          {agencyData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={agencyData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="responseRate" fill="#0ea5e9" name="Response Rate %" />
                <Bar dataKey="resolutionRate" fill="#10b981" name="Resolution Rate %" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-[300px] text-gray-500">
              <div className="text-center">
                <Building2 className="h-12 w-12 mx-auto mb-2 text-gray-400" />
                <p>No agency data available</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Agency Performance Table */}
      {agencies.length > 0 && (
        <div className="bg-white rounded-2xl shadow-lg p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Agency Performance Details</h2>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Agency</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Sector</th>
                  <th className="text-right py-3 px-4 font-semibold text-gray-700">Total Issues</th>
                  <th className="text-right py-3 px-4 font-semibold text-gray-700">Response Rate</th>
                  <th className="text-right py-3 px-4 font-semibold text-gray-700">Resolution Rate</th>
                  <th className="text-right py-3 px-4 font-semibold text-gray-700">Avg Response Time</th>
                </tr>
              </thead>
              <tbody>
                {agencies.map((agency, idx) => (
                  <tr key={idx} className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                    <td className="py-3 px-4 font-medium text-gray-900">{agency.agency_name}</td>
                    <td className="py-3 px-4 text-gray-600">{agency.sector || 'All'}</td>
                    <td className="py-3 px-4 text-right text-gray-700">{agency.total_issues || 0}</td>
                    <td className="py-3 px-4 text-right">
                      <span className={`font-semibold ${(agency.response_rate || 0) >= 80 ? 'text-green-600' : (agency.response_rate || 0) >= 50 ? 'text-yellow-600' : 'text-red-600'}`}>
                        {agency.response_rate || 0}%
                      </span>
                    </td>
                    <td className="py-3 px-4 text-right">
                      <span className={`font-semibold ${(agency.resolution_rate || 0) >= 60 ? 'text-green-600' : (agency.resolution_rate || 0) >= 30 ? 'text-yellow-600' : 'text-red-600'}`}>
                        {agency.resolution_rate || 0}%
                      </span>
                    </td>
                    <td className="py-3 px-4 text-right text-gray-700">{agency.average_response_time_hours || 0}h</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Accountability Gaps */}
      <div className="bg-yellow-50 border-l-4 border-yellow-500 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-yellow-900 mb-2 flex items-center gap-2">
          <XCircle className="h-5 w-5" />
          Accountability Gaps
        </h3>
        <p className="text-yellow-800 text-sm">
          {metrics.response_rate < 50
            ? `Low response rate (${metrics.response_rate}%) indicates agencies need to improve acknowledgment of citizen concerns.`
            : metrics.resolution_rate < 30
            ? `Low resolution rate (${metrics.resolution_rate}%) indicates issues are being acknowledged but not resolved.`
            : metrics.average_response_time_hours > 72
            ? `High average response time (${metrics.average_response_time_hours}h) indicates delays in addressing citizen concerns.`
            : 'Agency responsiveness is within acceptable ranges. Continue monitoring for sustained performance.'}
        </p>
      </div>
    </div>
  )
}

