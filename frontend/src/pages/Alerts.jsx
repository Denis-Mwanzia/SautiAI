import { useEffect, useState, useMemo, useCallback } from 'react'
import api from '../services/api'
import { useToast } from '../contexts/ToastContext'
import { useAutoRefresh } from '../hooks/useAutoRefresh'
import { useApiCache } from '../hooks/useApiCache'
import { useRequestDeduplication } from '../hooks/useRequestDeduplication'
import { AlertTriangle, CheckCircle, Clock, RefreshCw, Plus, Trash2, ToggleLeft, ToggleRight } from 'lucide-react'
import { CardSkeleton } from '../components/LoadingSkeleton'

export default function Alerts() {
  const [alerts, setAlerts] = useState([])
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [rules, setRules] = useState([])
  const [ruleDraft, setRuleDraft] = useState({ name: '', enabled: true, sector: '', county: '', min_count: 10, notify_slack: false, notify_webhook: false })
  const toast = useToast()
  const { getCached, setCached } = useApiCache()
  const { dedupeRequest } = useRequestDeduplication()

  const loadAlerts = useCallback(async (showToast = false, useCache = true) => {
    try {
      setRefreshing(true)
      
      // Check cache first
      const cacheKey = 'alerts-list-50'
      const cached = useCache ? getCached(cacheKey) : null
      
      if (cached && useCache) {
        setAlerts(cached)
        setLoading(false)
        setRefreshing(false)
        return
      }
      
      // Use request deduplication
      const response = await dedupeRequest('alerts-list-50', () => api.get('/alerts?limit=50'))
      const alertsData = response.data.data || []
      
      setAlerts(alertsData)
      setCached(cacheKey, alertsData)
      
      if (showToast) {
        toast.success('Alerts refreshed')
      }
    } catch (error) {
      const errorMsg = error.response?.data?.detail || 'Failed to load alerts'
      toast.error(errorMsg)
      console.error('Error loading alerts:', error)
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }, [getCached, setCached, dedupeRequest, toast])

  const loadRules = useCallback(async () => {
    try {
      const cacheKey = 'alerts-rules'
      const cached = getCached(cacheKey)
      if (cached) {
        setRules(cached)
        return
      }
      
      const res = await dedupeRequest('alerts-rules', () => api.get('/rules'))
      const rulesData = res.data.data || []
      setRules(rulesData)
      setCached(cacheKey, rulesData)
    } catch (e) {
      console.error('Failed to load rules', e)
    }
  }, [getCached, setCached, dedupeRequest])

  useEffect(() => {
    loadAlerts()
    loadRules()
  }, [loadAlerts, loadRules])

  // Auto-refresh every 60 seconds (longer interval for alerts)
  useAutoRefresh(() => loadAlerts(false, true), 60000, true)

  // Memoize severity color function
  const getSeverityColor = useMemo(() => (severity) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-100 border-red-300 text-red-800'
      case 'high':
        return 'bg-orange-100 border-orange-300 text-orange-800'
      case 'medium':
        return 'bg-yellow-100 border-yellow-300 text-yellow-800'
      default:
        return 'bg-blue-100 border-blue-300 text-blue-800'
    }
  }, [])

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="h-8 bg-gray-200 rounded w-48 mb-2 animate-pulse"></div>
        <div className="space-y-4">
          {[1, 2, 3, 4].map((i) => (
            <CardSkeleton key={i} />
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="animate-slide-up">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-primary-600 to-primary-800 bg-clip-text text-transparent">
          Alerts
        </h1>
        <p className="text-gray-600 mt-2">Monitor system alerts and configure rule-based notifications</p>
      </div>

      {/* Rule Builder */}
      <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-orange-500" /> Alert Rules
          </h2>
          <button
            onClick={async () => {
              try {
                const payload = {
                  name: ruleDraft.name || 'New rule',
                  enabled: ruleDraft.enabled,
                  sector: ruleDraft.sector || null,
                  county: ruleDraft.county || null,
                  min_count: ruleDraft.min_count || null,
                  notify_slack: !!ruleDraft.notify_slack,
                  notify_webhook: !!ruleDraft.notify_webhook,
                }
                await api.post('/rules', payload)
                await loadRules()
                toast.success('Rule created')
                setRuleDraft({ name: '', enabled: true, sector: '', county: '', min_count: 10, notify_slack: false, notify_webhook: false })
              } catch (e) {
                toast.error('Failed to create rule')
              }
            }}
            className="inline-flex items-center gap-2 px-3 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
          >
            <Plus className="h-4 w-4" /> Add Rule
          </button>
        </div>
        <div className="grid md:grid-cols-5 gap-3 items-end">
          <div>
            <label className="text-sm text-gray-600">Name</label>
            <input className="w-full border rounded-md px-3 py-2" value={ruleDraft.name} onChange={e=>setRuleDraft({...ruleDraft, name:e.target.value})} />
          </div>
          <div>
            <label className="text-sm text-gray-600">Sector (optional)</label>
            <input className="w-full border rounded-md px-3 py-2" placeholder="health / education / ..." value={ruleDraft.sector} onChange={e=>setRuleDraft({...ruleDraft, sector:e.target.value})} />
          </div>
          <div>
            <label className="text-sm text-gray-600">County (optional)</label>
            <input className="w-full border rounded-md px-3 py-2" placeholder="Nairobi" value={ruleDraft.county} onChange={e=>setRuleDraft({...ruleDraft, county:e.target.value})} />
          </div>
          <div>
            <label className="text-sm text-gray-600">Min Count (24h)</label>
            <input type="number" className="w-full border rounded-md px-3 py-2" value={ruleDraft.min_count} onChange={e=>setRuleDraft({...ruleDraft, min_count: Number(e.target.value)})} />
          </div>
          <div className="flex items-center gap-4">
            <button
              type="button"
              onClick={()=>setRuleDraft({...ruleDraft, enabled: !ruleDraft.enabled})}
              className="flex items-center gap-2 text-sm text-gray-700"
            >
              {ruleDraft.enabled ? <><ToggleRight className="h-5 w-5 text-green-600"/> Enabled</> : <><ToggleLeft className="h-5 w-5 text-gray-400"/> Disabled</>}
            </button>
          </div>
        </div>

        {/* Existing rules */}
        <div className="mt-4 divide-y divide-gray-200">
          {rules.length === 0 ? (
            <p className="text-sm text-gray-500">No rules yet.</p>
          ) : (
            rules.map((r) => (
              <div key={r.id} className="py-3 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  {r.enabled ? <span className="text-green-600">●</span> : <span className="text-gray-400">●</span>}
                  <div>
                    <div className="font-medium text-gray-900">{r.name}</div>
                    <div className="text-xs text-gray-500">
                      {(r.sector ? `sector=${r.sector}` : '')} {r.county ? ` county=${r.county}` : ''} {r.min_count ? ` min≥${r.min_count}` : ''}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    className="p-2 rounded hover:bg-gray-100"
                    title="Toggle"
                    onClick={async ()=>{
                      try{
                        await api.patch(`/rules/${r.id}`, { ...r, enabled: !r.enabled })
                        await loadRules()
                      }catch{ toast.error('Failed to update rule') }
                    }}
                  >
                    {r.enabled ? <ToggleRight className="h-5 w-5 text-green-600"/> : <ToggleLeft className="h-5 w-5 text-gray-400"/>}
                  </button>
                  <button
                    className="p-2 rounded hover:bg-red-50 text-red-600"
                    title="Delete"
                    onClick={async ()=>{
                      try{ await api.delete(`/rules/${r.id}`); await loadRules(); } catch { toast.error('Failed to delete rule') }
                    }}
                  >
                    <Trash2 className="h-5 w-5"/>
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      <div className="space-y-4">
        {alerts.length === 0 ? (
          <div className="bg-white rounded-xl shadow-lg p-12 text-center border border-gray-100 animate-scale-in">
            <div className="inline-flex items-center justify-center w-20 h-20 bg-green-100 rounded-full mb-6">
              <CheckCircle className="h-10 w-10 text-green-600" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">All Clear!</h3>
            <p className="text-gray-600">No alerts at this time. The system is running smoothly.</p>
          </div>
        ) : (
          alerts.map((alert, index) => (
            <div
              key={alert.id}
              className={`bg-white rounded-xl shadow-lg border-l-4 p-6 animate-slide-up card-hover ${getSeverityColor(
                alert.severity
              )}`}
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-4 flex-1">
                  <div className={`p-3 rounded-lg ${
                    alert.severity === 'critical' ? 'bg-red-100' :
                    alert.severity === 'high' ? 'bg-orange-100' :
                    alert.severity === 'medium' ? 'bg-yellow-100' : 'bg-blue-100'
                  }`}>
                    <AlertTriangle className={`h-6 w-6 ${
                      alert.severity === 'critical' ? 'text-red-600' :
                      alert.severity === 'high' ? 'text-orange-600' :
                      alert.severity === 'medium' ? 'text-yellow-600' : 'text-blue-600'
                    }`} />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-start justify-between mb-2">
                      <h3 className="text-lg font-bold text-gray-900">{alert.title}</h3>
                      {alert.acknowledged && (
                        <div className="flex items-center gap-2 px-3 py-1 bg-green-100 text-green-700 rounded-full text-xs font-semibold">
                          <CheckCircle className="h-4 w-4" />
                          Acknowledged
                        </div>
                      )}
                    </div>
                    <p className="text-sm text-gray-700 mb-4 leading-relaxed">{alert.description}</p>
                    <div className="flex flex-wrap items-center gap-4 text-sm">
                      <span className="px-3 py-1 bg-white bg-opacity-70 rounded-lg font-semibold capitalize">
                        {alert.severity}
                      </span>
                      {alert.sector && (
                        <span className="px-3 py-1 bg-white bg-opacity-70 rounded-lg capitalize">
                          {alert.sector}
                        </span>
                      )}
                      <span className="flex items-center text-gray-600">
                        <Clock className="h-4 w-4 mr-1" />
                        {new Date(alert.created_at).toLocaleString()}
                      </span>
                    </div>
                    {alert.affected_counties && alert.affected_counties.length > 0 && (
                      <div className="mt-4 pt-4 border-t border-gray-200">
                        <p className="text-sm font-semibold text-gray-700 mb-2">Affected Counties:</p>
                        <div className="flex flex-wrap gap-2">
                          {alert.affected_counties.map((county, idx) => (
                            <span
                              key={idx}
                              className="px-3 py-1 bg-white bg-opacity-70 rounded-lg text-xs font-medium"
                            >
                              {county}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

