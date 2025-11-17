import { useEffect, useState } from 'react'
import api from '../services/api'
import { useToast } from '../contexts/ToastContext'
import { Save, CheckCircle } from 'lucide-react'

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
    // TODO: Implement API key saving
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
      <div className="animate-slide-up">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-primary-600 to-primary-800 bg-clip-text text-transparent">
          Settings
        </h1>
        <p className="text-gray-600 mt-2">Manage API keys and agent schedules</p>
      </div>

      <div className="bg-white rounded-xl shadow-lg p-8 border border-gray-100 animate-slide-up">
        <div className="flex items-center gap-3 mb-6">
          <div className="p-2 bg-primary-100 rounded-lg">
            <Save className="h-6 w-6 text-primary-600" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900">API Keys</h2>
        </div>
        <div className="space-y-6">
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Twitter Bearer Token
            </label>
            <input
              type="password"
              value={apiKeys.twitter}
              onChange={(e) => setApiKeys({ ...apiKeys, twitter: e.target.value })}
              className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-200 outline-none"
              placeholder="Enter Twitter Bearer Token"
            />
            <p className="text-xs text-gray-500 mt-1">Optional - for Twitter data ingestion</p>
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Facebook Access Token
            </label>
            <input
              type="password"
              value={apiKeys.facebook}
              onChange={(e) => setApiKeys({ ...apiKeys, facebook: e.target.value })}
              className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-200 outline-none"
              placeholder="Enter Facebook Access Token"
            />
            <p className="text-xs text-gray-500 mt-1">Optional - for Facebook public pages</p>
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Vertex AI Project ID
            </label>
            <input
              type="text"
              value={apiKeys.vertexAI}
              onChange={(e) => setApiKeys({ ...apiKeys, vertexAI: e.target.value })}
              className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-200 outline-none"
              placeholder="Enter Vertex AI Project ID"
            />
            <p className="text-xs text-gray-500 mt-1">Required for AI analysis features</p>
          </div>

          <button
            onClick={handleSave}
            className="flex items-center justify-center gap-2 px-6 py-3 bg-gradient-to-r from-primary-600 to-primary-700 text-white rounded-xl hover:from-primary-700 hover:to-primary-800 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 font-semibold"
          >
            <Save className="h-5 w-5" />
            Save Changes
          </button>

          {saved && (
            <div className="flex items-center gap-2 px-4 py-3 bg-green-50 border border-green-200 text-green-700 rounded-xl animate-slide-up">
              <CheckCircle className="h-5 w-5" />
              <span className="font-medium">Settings saved successfully!</span>
            </div>
          )}
        </div>
      </div>

      {/* Alerts / Webhooks */}
      <div className="bg-white rounded-xl shadow-lg p-8 border border-gray-100 animate-slide-up" style={{ animationDelay: '0.05s' }}>
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Alerts & Notifications</h2>
        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">Slack Webhook URL</label>
            <input
              type="text"
              value={alertsCfg.SLACK_WEBHOOK_URL}
              onChange={(e)=>setAlertsCfg({...alertsCfg, SLACK_WEBHOOK_URL: e.target.value})}
              className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none"
              placeholder="https://hooks.slack.com/services/..."
            />
            <p className="text-xs text-gray-500 mt-1">Optional. Send rule-triggered or red-flag alerts to Slack.</p>
          </div>
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">Generic Webhook URL</label>
            <input
              type="text"
              value={alertsCfg.ALERT_WEBHOOK_URL}
              onChange={(e)=>setAlertsCfg({...alertsCfg, ALERT_WEBHOOK_URL: e.target.value})}
              className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none"
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
            className="inline-flex items-center gap-2 px-6 py-3 bg-primary-600 text-white rounded-xl hover:bg-primary-700"
          >
            <Save className="h-5 w-5"/> Save Alerts Config
          </button>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-lg p-8 border border-gray-100 animate-slide-up" style={{ animationDelay: '0.1s' }}>
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Agent Schedule</h2>
        <p className="text-gray-600 mb-4">Configure agent execution schedules</p>
        <div className="p-6 bg-gray-50 rounded-xl border-2 border-dashed border-gray-200">
          <p className="text-sm text-gray-500 text-center">Agent schedule configuration coming soon</p>
        </div>
      </div>
    </div>
  )
}

