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

const COLORS = ['#009639', '#DE2910', '#000000', '#f59e0b']

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
      
      const [metricsRes, agenciesRes] = await Promise.all([
        dedupeRequest(metricsCacheKey, () => api.get(`/transparency/metrics?days=${days}`)),
        dedupeRequest(agenciesCacheKey, () => api.get(`/transparency/agencies?days=${days}`))
      ])
      
      const metricsData = metricsRes?.data?.data
      const agenciesData = agenciesRes?.data?.data || []
      
      setMetrics(metricsData)
      setAgencies(agenciesData)
      
      setCached(metricsCacheKey, metricsData)
      setCached(agenciesCacheKey, agenciesData)
    } catch (error) {
      console.error('Error loading transparency data:', error)
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
          <div className="animate-spin rounded-full h-12 w-12 border-3 border-gray-200 border-t-gray-900 mx-auto mb-4"></div>
          <p className="text-gray-600 text-sm">Loading transparency metrics...</p>
        </div>
      </div>
    )
  }

  if (!metrics) {
    return (
      <div className="glass-card p-12 text-center">
        <Shield className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-xl font-semibold text-gray-900 mb-2">No Transparency Data</h3>
        <p className="text-gray-600 text-sm">Transparency metrics will appear here once government responses are recorded</p>
      </div>
    )
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
        <div>
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Transparency</h1>
          <p className="text-gray-600 text-sm">Track government agency accountability and response metrics</p>
        </div>
        <select
          value={days}
          onChange={(e) => setDays(Number(e.target.value))}
          className="px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-gray-900/20 focus:border-gray-900 outline-none bg-white text-sm font-medium shadow-sm hover:shadow transition-all duration-200"
        >
          <option value={7}>Last 7 days</option>
          <option value={30}>Last 30 days</option>
          <option value={90}>Last 90 days</option>
        </select>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="stat-card p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="stat-card-icon">
              <Shield className="h-5 w-5 text-gray-700" />
            </div>
          </div>
          <p className="stat-card-label mb-2">Total Issues</p>
          <p className="stat-card-value mb-2">{metrics.total_issues || 0}</p>
          <div className="text-xs text-gray-600">Issues requiring response</div>
        </div>

        <div className="stat-card p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="stat-card-icon" style={{ background: 'linear-gradient(135deg, rgba(0, 150, 57, 0.1) 0%, rgba(0, 150, 57, 0.05) 100%)' }}>
              <CheckCircle className="h-5 w-5 text-kenya-green-600" />
            </div>
          </div>
          <p className="stat-card-label mb-2">Response Rate</p>
          <p className="stat-card-value mb-2" style={{ color: '#009639' }}>{metrics.response_rate || 0}%</p>
          <div className="text-xs text-gray-600">{metrics.acknowledged_count || 0} acknowledged</div>
        </div>

        <div className="stat-card p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="stat-card-icon" style={{ background: 'linear-gradient(135deg, rgba(222, 41, 16, 0.1) 0%, rgba(222, 41, 16, 0.05) 100%)' }}>
              <TrendingUp className="h-5 w-5 text-kenya-red-600" />
            </div>
          </div>
          <p className="stat-card-label mb-2">Resolution Rate</p>
          <p className="stat-card-value mb-2" style={{ color: '#DE2910' }}>{metrics.resolution_rate || 0}%</p>
          <div className="text-xs text-gray-600">{metrics.resolved_count || 0} resolved</div>
        </div>

        <div className="stat-card p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="stat-card-icon">
              <Clock className="h-5 w-5 text-gray-700" />
            </div>
          </div>
          <p className="stat-card-label mb-2">Avg Response Time</p>
          <p className="stat-card-value mb-2">{metrics.average_response_time_hours || 0}h</p>
          <div className="text-xs text-gray-600">Hours to respond</div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Status Breakdown */}
        <div className="glass-card p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-6">Issue Status Breakdown</h2>
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie
                data={statusData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={90}
                innerRadius={35}
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
        <div className="glass-card p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-6">Agency Response Rates</h2>
          {agencyData.length > 0 ? (
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={agencyData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
                <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Legend wrapperStyle={{ fontSize: '12px' }} />
                <Bar dataKey="responseRate" fill="#0ea5e9" name="Response Rate %" radius={[6, 6, 0, 0]} />
                <Bar dataKey="resolutionRate" fill="#10b981" name="Resolution Rate %" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-[280px] text-gray-500">
              <div className="text-center">
                <Building2 className="h-10 w-10 mx-auto mb-2 text-gray-300" />
                <p className="text-sm">No agency data available</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Agency Performance Table */}
      {agencies.length > 0 && (
        <div className="glass-card p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-6">Agency Performance Details</h2>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 font-semibold text-gray-700 text-sm">Agency</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-700 text-sm">Sector</th>
                  <th className="text-right py-3 px-4 font-semibold text-gray-700 text-sm">Total Issues</th>
                  <th className="text-right py-3 px-4 font-semibold text-gray-700 text-sm">Response Rate</th>
                  <th className="text-right py-3 px-4 font-semibold text-gray-700 text-sm">Resolution Rate</th>
                  <th className="text-right py-3 px-4 font-semibold text-gray-700 text-sm">Avg Response Time</th>
                </tr>
              </thead>
              <tbody>
                {agencies.map((agency, idx) => (
                  <tr key={idx} className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                    <td className="py-3 px-4 font-medium text-gray-900 text-sm">{agency.agency_name}</td>
                    <td className="py-3 px-4 text-gray-600 text-sm">{agency.sector || 'All'}</td>
                    <td className="py-3 px-4 text-right text-gray-700 text-sm">{agency.total_issues || 0}</td>
                    <td className="py-3 px-4 text-right">
                      <span className={`font-semibold text-sm ${(agency.response_rate || 0) >= 80 ? 'text-green-600' : (agency.response_rate || 0) >= 50 ? 'text-yellow-600' : 'text-red-600'}`}>
                        {agency.response_rate || 0}%
                      </span>
                    </td>
                    <td className="py-3 px-4 text-right">
                      <span className={`font-semibold text-sm ${(agency.resolution_rate || 0) >= 60 ? 'text-green-600' : (agency.resolution_rate || 0) >= 30 ? 'text-yellow-600' : 'text-red-600'}`}>
                        {agency.resolution_rate || 0}%
                      </span>
                    </td>
                    <td className="py-3 px-4 text-right text-gray-700 text-sm">{agency.average_response_time_hours || 0}h</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Accountability Gaps */}
      <div className="bg-yellow-50 border-l-4 border-yellow-500 rounded-lg p-4">
        <h3 className="text-base font-semibold text-yellow-900 mb-2 flex items-center gap-2">
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
