import { useEffect, useState, useMemo, useCallback } from 'react'
import api from '../services/api'
import { useToast } from '../contexts/ToastContext'
import { useAutoRefresh } from '../hooks/useAutoRefresh'
import { useApiCache } from '../hooks/useApiCache'
import { useRequestDeduplication } from '../hooks/useRequestDeduplication'
import { AlertTriangle, CheckCircle, Clock, RefreshCw, Plus, Trash2, ToggleLeft, ToggleRight, Bell } from 'lucide-react'
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
      
      const cacheKey = 'alerts-list-50'
      const cached = useCache ? getCached(cacheKey) : null
      
      if (cached && useCache) {
        setAlerts(cached)
        setLoading(false)
        setRefreshing(false)
        return
      }
      
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

  useAutoRefresh(() => loadAlerts(false, true), 60000, true)

  const getSeverityColor = useMemo(() => (severity) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-50 border-red-300 text-red-800'
      case 'high':
        return 'bg-orange-50 border-orange-300 text-orange-800'
      case 'medium':
        return 'bg-yellow-50 border-yellow-300 text-yellow-800'
      default:
        return 'bg-blue-50 border-blue-300 text-blue-800'
    }
  }, [])

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="h-10 bg-gray-200 rounded-lg w-48 mb-4 animate-pulse"></div>
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
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
        <div>
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Alerts</h1>
          <p className="text-gray-600 text-sm">Monitor system alerts and configure rule-based notifications</p>
        </div>
        <button
          onClick={() => loadAlerts(true, false)}
          disabled={refreshing}
          className="inline-flex items-center gap-2 px-4 py-2 bg-white border border-gray-200 rounded-lg text-gray-700 hover:bg-gray-50 disabled:opacity-50 transition-all duration-200 text-sm font-medium shadow-sm hover:shadow"
        >
          <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {/* Rule Builder */}
      <div className="glass-card p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-gray-900 rounded-lg">
              <Bell className="h-5 w-5 text-white" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-gray-900">Alert Rules</h2>
              <p className="text-xs text-gray-600 mt-0.5">Create and manage notification rules</p>
            </div>
          </div>
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
            className="inline-flex items-center gap-2 px-4 py-2 bg-gray-900 text-white rounded-lg hover:bg-gray-800 transition-all duration-200 text-sm font-medium shadow-sm hover:shadow"
          >
            <Plus className="h-4 w-4" /> Add Rule
          </button>
        </div>
        <div className="grid md:grid-cols-5 gap-3 items-end">
          <div>
            <label className="text-xs text-gray-600 mb-1.5 block font-medium">Name</label>
            <input 
              className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-gray-900/20 focus:border-gray-900 transition-all duration-200 outline-none bg-white" 
              value={ruleDraft.name} 
              onChange={e=>setRuleDraft({...ruleDraft, name:e.target.value})} 
            />
          </div>
          <div>
            <label className="text-xs text-gray-600 mb-1.5 block font-medium">Sector (optional)</label>
            <input 
              className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-gray-900/20 focus:border-gray-900 transition-all duration-200 outline-none bg-white" 
              placeholder="health / education / ..." 
              value={ruleDraft.sector} 
              onChange={e=>setRuleDraft({...ruleDraft, sector:e.target.value})} 
            />
          </div>
          <div>
            <label className="text-xs text-gray-600 mb-1.5 block font-medium">County (optional)</label>
            <input 
              className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-gray-900/20 focus:border-gray-900 transition-all duration-200 outline-none bg-white" 
              placeholder="Nairobi" 
              value={ruleDraft.county} 
              onChange={e=>setRuleDraft({...ruleDraft, county:e.target.value})} 
            />
          </div>
          <div>
            <label className="text-xs text-gray-600 mb-1.5 block font-medium">Min Count (24h)</label>
            <input 
              type="number" 
              className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-gray-900/20 focus:border-gray-900 transition-all duration-200 outline-none bg-white" 
              value={ruleDraft.min_count} 
              onChange={e=>setRuleDraft({...ruleDraft, min_count: Number(e.target.value)})} 
            />
          </div>
          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={()=>setRuleDraft({...ruleDraft, enabled: !ruleDraft.enabled})}
              className="flex items-center gap-2 text-sm text-gray-700 hover:text-gray-900 transition-colors"
            >
              {ruleDraft.enabled ? <><ToggleRight className="h-5 w-5 text-green-600"/> Enabled</> : <><ToggleLeft className="h-5 w-5 text-gray-400"/> Disabled</>}
            </button>
          </div>
        </div>

        {/* Existing rules */}
        <div className="mt-6 space-y-2">
          {rules.length === 0 ? (
            <p className="text-sm text-gray-500 py-4">No rules yet.</p>
          ) : (
            rules.map((r) => (
              <div key={r.id} className="py-3 px-4 flex items-center justify-between bg-gray-50 rounded-lg border border-gray-200 hover:bg-gray-100 transition-colors">
                <div className="flex items-center gap-3">
                  {r.enabled ? <span className="text-green-600 text-lg">●</span> : <span className="text-gray-400 text-lg">●</span>}
                  <div>
                    <div className="font-medium text-gray-900 text-sm">{r.name}</div>
                    <div className="text-xs text-gray-500">
                      {(r.sector ? `sector=${r.sector}` : '')} {r.county ? ` county=${r.county}` : ''} {r.min_count ? ` min≥${r.min_count}` : ''}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    className="p-2 rounded-lg hover:bg-gray-200 transition-colors"
                    title="Toggle"
                    onClick={async ()=>{
                      try{
                        await api.patch(`/rules/${r.id}`, { ...r, enabled: !r.enabled })
                        await loadRules()
                      }catch{ toast.error('Failed to update rule') }
                    }}
                  >
                    {r.enabled ? <ToggleRight className="h-4 w-4 text-green-600"/> : <ToggleLeft className="h-4 w-4 text-gray-400"/>}
                  </button>
                  <button
                    className="p-2 rounded-lg hover:bg-red-50 text-red-600 transition-colors"
                    title="Delete"
                    onClick={async ()=>{
                      try{ await api.delete(`/rules/${r.id}`); await loadRules(); } catch { toast.error('Failed to delete rule') }
                    }}
                  >
                    <Trash2 className="h-4 w-4"/>
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Alerts List */}
      <div className="space-y-3">
        {alerts.length === 0 ? (
          <div className="glass-card p-12 text-center">
            <div className="relative mb-4 inline-block">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-green-50 rounded-full border-2 border-green-200">
                <CheckCircle className="h-8 w-8 text-green-600" />
              </div>
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">All Clear!</h3>
            <p className="text-gray-600 text-sm max-w-md mx-auto">No alerts at this time. The system is running smoothly.</p>
          </div>
        ) : (
          alerts.map((alert, index) => (
            <div
              key={alert.id}
              className={`glass-card p-5 border-l-4 ${getSeverityColor(alert.severity)}`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start gap-4 flex-1">
                  <div className={`p-2.5 rounded-lg ${
                    alert.severity === 'critical' ? 'bg-red-100' :
                    alert.severity === 'high' ? 'bg-orange-100' :
                    alert.severity === 'medium' ? 'bg-yellow-100' : 'bg-blue-100'
                  }`}>
                    <AlertTriangle className={`h-5 w-5 ${
                      alert.severity === 'critical' ? 'text-red-600' :
                      alert.severity === 'high' ? 'text-orange-600' :
                      alert.severity === 'medium' ? 'text-yellow-600' : 'text-blue-600'
                    }`} />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-start justify-between mb-2">
                      <h3 className="text-base font-semibold text-gray-900">{alert.title}</h3>
                      {alert.acknowledged && (
                        <div className="flex items-center gap-1.5 px-2.5 py-1 bg-green-100 text-green-700 rounded-full text-xs font-semibold">
                          <CheckCircle className="h-3.5 w-3.5" />
                          Acknowledged
                        </div>
                      )}
                    </div>
                    <p className="text-sm text-gray-700 mb-3 leading-relaxed">{alert.description}</p>
                    <div className="flex flex-wrap items-center gap-3 text-xs">
                      <span className="px-2.5 py-1 bg-white bg-opacity-70 rounded-md font-semibold capitalize">
                        {alert.severity}
                      </span>
                      {alert.sector && (
                        <span className="px-2.5 py-1 bg-white bg-opacity-70 rounded-md capitalize">
                          {alert.sector}
                        </span>
                      )}
                      <span className="flex items-center text-gray-600">
                        <Clock className="h-3.5 w-3.5 mr-1" />
                        {new Date(alert.created_at).toLocaleString()}
                      </span>
                    </div>
                    {alert.affected_counties && alert.affected_counties.length > 0 && (
                      <div className="mt-3 pt-3 border-t border-gray-200">
                        <p className="text-xs font-semibold text-gray-700 mb-2">Affected Counties:</p>
                        <div className="flex flex-wrap gap-2">
                          {alert.affected_counties.map((county, idx) => (
                            <span
                              key={idx}
                              className="px-2.5 py-1 bg-white bg-opacity-70 rounded-md text-xs font-medium"
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
