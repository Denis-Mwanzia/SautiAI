import { useEffect, useState } from 'react'
import api from '../services/api'
import { useToast } from '../contexts/ToastContext'
import { Save, CheckCircle, Bell, Settings as SettingsIcon } from 'lucide-react'

export default function Settings() {
  const [apiKeys, setApiKeys] = useState({
    twitter: '',
    facebook: '',
    vertexAI: '',
  })
  const [saved, setSaved] = useState(false)
  const [alertsCfg, setAlertsCfg] = useState({ SLACK_WEBHOOK_URL: '', ALERT_WEBHOOK_URL: '' })
  const toast = useToast()

  const handleSave = () => {
    setSaved(true)
    toast.success('Settings saved successfully')
    setTimeout(() => setSaved(false), 3000)
  }

  useEffect(() => {
    const load = async () => {
      try {
        const res = await api.get('/config/alerts')
        setAlertsCfg({
          SLACK_WEBHOOK_URL: res.data?.data?.SLACK_WEBHOOK_URL || '',
          ALERT_WEBHOOK_URL: res.data?.data?.ALERT_WEBHOOK_URL || ''
        })
      } catch {}
    }
    load()
  }, [])

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold text-gray-900 mb-2">Settings</h1>
        <p className="text-gray-600 text-sm">Manage API keys, alerts, and agent schedules</p>
      </div>

      {/* API Keys */}
      <div className="glass-card p-6">
        <div className="flex items-center gap-3 mb-6">
          <div className="p-2.5 bg-gray-900 rounded-lg">
            <Save className="h-5 w-5 text-white" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-gray-900">API Keys</h2>
            <p className="text-xs text-gray-600 mt-0.5">Configure external service integrations</p>
          </div>
        </div>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1.5">
              Twitter Bearer Token
            </label>
            <input
              type="password"
              value={apiKeys.twitter}
              onChange={(e) => setApiKeys({ ...apiKeys, twitter: e.target.value })}
              className="w-full px-4 py-2.5 border border-gray-200 rounded-lg focus:ring-2 focus:ring-gray-900/20 focus:border-gray-900 transition-all duration-200 outline-none bg-white text-sm"
              placeholder="Enter Twitter Bearer Token"
            />
            <p className="text-xs text-gray-500 mt-1">Optional - for Twitter data ingestion</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1.5">
              Facebook Access Token
            </label>
            <input
              type="password"
              value={apiKeys.facebook}
              onChange={(e) => setApiKeys({ ...apiKeys, facebook: e.target.value })}
              className="w-full px-4 py-2.5 border border-gray-200 rounded-lg focus:ring-2 focus:ring-gray-900/20 focus:border-gray-900 transition-all duration-200 outline-none bg-white text-sm"
              placeholder="Enter Facebook Access Token"
            />
            <p className="text-xs text-gray-500 mt-1">Optional - for Facebook public pages</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1.5">
              Vertex AI Project ID
            </label>
            <input
              type="text"
              value={apiKeys.vertexAI}
              onChange={(e) => setApiKeys({ ...apiKeys, vertexAI: e.target.value })}
              className="w-full px-4 py-2.5 border border-gray-200 rounded-lg focus:ring-2 focus:ring-gray-900/20 focus:border-gray-900 transition-all duration-200 outline-none bg-white text-sm"
              placeholder="Enter Vertex AI Project ID"
            />
            <p className="text-xs text-gray-500 mt-1">Required for AI analysis features</p>
          </div>

          <button
            onClick={handleSave}
            className="inline-flex items-center gap-2 px-4 py-2.5 bg-gray-900 text-white rounded-lg hover:bg-gray-800 transition-all duration-200 text-sm font-medium shadow-sm hover:shadow"
          >
            <Save className="h-4 w-4" />
            Save Changes
          </button>

          {saved && (
            <div className="flex items-center gap-2 px-4 py-3 bg-green-50 border border-green-200 text-green-700 rounded-lg">
              <CheckCircle className="h-5 w-5" />
              <span className="text-sm font-medium">Settings saved successfully!</span>
            </div>
          )}
        </div>
      </div>

      {/* Alerts / Webhooks */}
      <div className="glass-card p-6">
        <div className="flex items-center gap-3 mb-6">
          <div className="p-2.5 bg-gray-900 rounded-lg">
            <Bell className="h-5 w-5 text-white" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Alerts & Notifications</h2>
            <p className="text-xs text-gray-600 mt-0.5">Configure webhook endpoints for alerts</p>
          </div>
        </div>
        <div className="grid md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1.5">Slack Webhook URL</label>
            <input
              type="text"
              value={alertsCfg.SLACK_WEBHOOK_URL}
              onChange={(e)=>setAlertsCfg({...alertsCfg, SLACK_WEBHOOK_URL: e.target.value})}
              className="w-full px-4 py-2.5 border border-gray-200 rounded-lg focus:ring-2 focus:ring-gray-900/20 focus:border-gray-900 transition-all duration-200 outline-none bg-white text-sm"
              placeholder="https://hooks.slack.com/services/..."
            />
            <p className="text-xs text-gray-500 mt-1">Optional. Send rule-triggered or red-flag alerts to Slack.</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1.5">Generic Webhook URL</label>
            <input
              type="text"
              value={alertsCfg.ALERT_WEBHOOK_URL}
              onChange={(e)=>setAlertsCfg({...alertsCfg, ALERT_WEBHOOK_URL: e.target.value})}
              className="w-full px-4 py-2.5 border border-gray-200 rounded-lg focus:ring-2 focus:ring-gray-900/20 focus:border-gray-900 transition-all duration-200 outline-none bg-white text-sm"
              placeholder="https://example.com/webhook"
            />
            <p className="text-xs text-gray-500 mt-1">Optional. Receives full alert payloads (JSON).</p>
          </div>
        </div>
        <div className="mt-4">
          <button
            onClick={async ()=>{
              try {
                await api.post('/config/alerts', alertsCfg)
                toast.success('Alert configuration saved')
              } catch (e) {
                toast.error('Failed to save alert configuration')
              }
            }}
            className="inline-flex items-center gap-2 px-4 py-2.5 bg-gray-900 text-white rounded-lg hover:bg-gray-800 transition-all duration-200 text-sm font-medium shadow-sm hover:shadow"
          >
            <Save className="h-4 w-4"/> Save Alerts Config
          </button>
        </div>
      </div>

      {/* Agent Schedule */}
      <div className="glass-card p-6">
        <div className="mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-1">Agent Schedule</h2>
          <p className="text-sm text-gray-600">Configure agent execution schedules</p>
        </div>
        <div className="p-8 bg-gray-50 rounded-lg border border-gray-200 text-center">
          <div className="inline-flex items-center justify-center w-12 h-12 bg-gray-100 rounded-full mb-4">
            <SettingsIcon className="h-6 w-6 text-gray-400" />
          </div>
          <p className="text-sm text-gray-500">Agent schedule configuration coming soon</p>
        </div>
      </div>
    </div>
  )
}
