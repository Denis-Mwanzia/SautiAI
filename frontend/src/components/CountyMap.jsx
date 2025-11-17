import { useEffect, useState, useRef } from 'react'
import { MapContainer, TileLayer, CircleMarker, Popup, useMap, Circle } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import api from '../services/api'
import { AlertTriangle, Layers, Filter, Zap, BarChart3, TrendingUp, TrendingDown, Activity, MapPin, X, Search, Sparkles, Gauge, PieChart as PieChartIcon, ArrowUp, ArrowDown, Minus, Target, Users, MessageSquare } from 'lucide-react'
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts'

// Fix for default marker icons in Leaflet
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
})

// Kenya's approximate boundaries (to restrict map view)
const KENYA_BOUNDS = [
  [-4.7, 33.9], // Southwest corner
  [5.5, 41.9]   // Northeast corner
]

// Kenyan counties with approximate coordinates (all 47 counties)
const KENYAN_COUNTIES = {
  "Nairobi": { lat: -1.2921, lng: 36.8219 },
  "Mombasa": { lat: -4.0435, lng: 39.6682 },
  "Kisumu": { lat: -0.0917, lng: 34.7680 },
  "Nakuru": { lat: -0.3031, lng: 36.0800 },
  "Eldoret": { lat: 0.5143, lng: 35.2698 },
  "Thika": { lat: -1.0333, lng: 37.0694 },
  "Malindi": { lat: -3.2175, lng: 40.1169 },
  "Kitale": { lat: 1.0167, lng: 35.0000 },
  "Garissa": { lat: -0.4569, lng: 39.6583 },
  "Kakamega": { lat: 0.2827, lng: 34.7519 },
  "Kisii": { lat: -0.6773, lng: 34.7796 },
  "Meru": { lat: 0.0463, lng: 37.6559 },
  "Nyeri": { lat: -0.4197, lng: 36.9475 },
  "Machakos": { lat: -1.5167, lng: 37.2667 },
  "Uasin Gishu": { lat: 0.5143, lng: 35.2698 },
  "Kiambu": { lat: -1.0333, lng: 36.8333 },
  "Narok": { lat: -1.0833, lng: 35.8667 },
  "Turkana": { lat: 3.1167, lng: 35.6000 },
  "Mandera": { lat: 3.9333, lng: 41.8667 },
  "Wajir": { lat: 1.7500, lng: 40.0667 },
  "Marsabit": { lat: 2.3333, lng: 37.9833 },
  "Isiolo": { lat: 0.3500, lng: 37.5833 },
  "Laikipia": { lat: 0.0333, lng: 36.3667 },
  "Nyandarua": { lat: -0.3000, lng: 36.4167 },
  "Murang'a": { lat: -0.7167, lng: 37.1500 },
  "Kirinyaga": { lat: -0.5000, lng: 37.2833 },
  "Embu": { lat: -0.5333, lng: 37.4500 },
  "Tharaka-Nithi": { lat: -0.3000, lng: 37.6500 },
  "Kitui": { lat: -1.3667, lng: 38.0167 },
  "Makueni": { lat: -1.8000, lng: 37.6167 },
  "Nyamira": { lat: -0.5667, lng: 34.9333 },
  "Bomet": { lat: -0.7833, lng: 35.3333 },
  "Kericho": { lat: -0.3667, lng: 35.2833 },
  "Baringo": { lat: 0.4667, lng: 35.9667 },
  "Elgeyo-Marakwet": { lat: 0.5167, lng: 35.2833 },
  "Nandi": { lat: 0.1833, lng: 35.0000 },
  "Vihiga": { lat: 0.0833, lng: 34.7167 },
  "Busia": { lat: 0.4667, lng: 34.1167 },
  "Siaya": { lat: 0.0667, lng: 34.2833 },
  "Homa Bay": { lat: -0.5333, lng: 34.4500 },
  "Migori": { lat: -1.0667, lng: 34.4667 },
  "Taita-Taveta": { lat: -3.4000, lng: 38.3667 },
  "Kwale": { lat: -4.1833, lng: 39.4500 },
  "Kilifi": { lat: -3.6333, lng: 39.8500 },
  "Tana River": { lat: -1.5167, lng: 40.0167 },
  "Lamu": { lat: -2.2667, lng: 40.9000 },
  "Samburu": { lat: 1.1000, lng: 36.6833 },
  "West Pokot": { lat: 1.5167, lng: 35.1167 },
  "Trans Nzoia": { lat: 1.0167, lng: 35.0000 }
}

function MapBounds({ bounds }) {
  const map = useMap()
  
  useEffect(() => {
    if (bounds) {
      // Restrict map to Kenya's boundaries
      map.setMaxBounds(bounds)
      map.fitBounds(bounds, { padding: [20, 20] })
    }
  }, [bounds, map])
  
  return null
}

export default function CountyMap({ days = 7 }) {
  const [heatmapData, setHeatmapData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [viewMode, setViewMode] = useState('heat') // 'heat', 'choropleth', 'clusters', 'pulse'
  const [severityFilter, setSeverityFilter] = useState('all')
  const [showAnimation, setShowAnimation] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCounty, setSelectedCounty] = useState(null)
  const [hoveredCounty, setHoveredCounty] = useState(null)
  const animationFrameRef = useRef(null)

  useEffect(() => {
    loadHeatmapData()
  }, [days])

  const loadHeatmapData = async () => {
    try {
      const response = await api.get(`/dashboard/county-heatmap?days=${days}`)
      setHeatmapData(response.data.data)
    } catch (error) {
      console.error('Error loading heatmap data:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96 bg-gray-100 rounded-lg">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (!heatmapData || Object.keys(heatmapData).length === 0) {
    return (
      <div className="flex items-center justify-center h-96 bg-gray-100 rounded-lg">
        <p className="text-gray-600">No county data available</p>
      </div>
    )
  }

  // Calculate max count for color scaling
  const maxCount = Math.max(...Object.values(heatmapData).map(d => d.count || 0), 1)
  const minCount = Math.min(...Object.values(heatmapData).map(d => d.count || 0).filter(c => c > 0), 1)

  // Enhanced color scheme based on issue severity
  const getColor = (count, sentiment) => {
    if (!count || count === 0) return '#9ca3af' // gray for no data
    
    const ratio = count / maxCount
    const negativeRatio = sentiment?.negative ? sentiment.negative / count : 0
    
    // High count + high negative sentiment = critical (dark red)
    if (ratio > 0.6 && negativeRatio > 0.5) return '#dc2626' // dark red
    // High count = high priority (red)
    if (ratio > 0.6) return '#ef4444' // red
    // Medium count + negative sentiment = warning (orange-red)
    if (ratio > 0.3 && negativeRatio > 0.4) return '#f97316' // orange-red
    // Medium count = medium priority (orange)
    if (ratio > 0.3) return '#f59e0b' // orange
    // Low count but negative = caution (yellow)
    if (negativeRatio > 0.4) return '#eab308' // yellow
    // Low count = low priority (green)
    return '#10b981' // green
  }

  // Enhanced radius calculation with better scaling
  const getRadius = (count) => {
    if (!count || count === 0) return 6
    // Logarithmic scaling for better visualization
    const logScale = Math.log10(count + 1) / Math.log10(maxCount + 1)
    return Math.max(10, Math.min(40, 10 + logScale * 30))
  }

  // Get severity level for display
  const getSeverity = (count, sentiment) => {
    if (!count || count === 0) return 'No Data'
    const ratio = count / maxCount
    const negativeRatio = sentiment?.negative ? sentiment.negative / count : 0
    
    if (ratio > 0.6 && negativeRatio > 0.5) return 'Critical'
    if (ratio > 0.6) return 'High'
    if (ratio > 0.3 && negativeRatio > 0.4) return 'Warning'
    if (ratio > 0.3) return 'Medium'
    if (negativeRatio > 0.4) return 'Caution'
    return 'Low'
  }

  // Filter counties based on severity and search query
  const filteredData = Object.entries(heatmapData).filter(([county, data]) => {
    // Search filter
    if (searchQuery && !county.toLowerCase().includes(searchQuery.toLowerCase())) {
      return false
    }
    // Severity filter
    if (severityFilter === 'all') return true
    const severity = getSeverity(data.count || 0, data.sentiment || {})
    return severity.toLowerCase() === severityFilter.toLowerCase()
  })

  // Create heat intensity data points for gradient visualization
  const createHeatPoints = () => {
    return filteredData.map(([county, data]) => {
      const coords = KENYAN_COUNTIES[county]
      if (!coords) return null
      const count = data.count || 0
      const intensity = count / maxCount
      return {
        lat: coords.lat,
        lng: coords.lng,
        intensity: intensity,
        count: count,
        county: county,
        data: data
      }
    }).filter(Boolean)
  }

  const heatPoints = createHeatPoints()

  // Enhanced popup with creative visualizations
  const renderPopup = (county, data) => {
    const count = data.count || 0
    const sentiment = data.sentiment || {}
    const severity = getSeverity(count, sentiment)
    const negativePercent = sentiment.negative ? (sentiment.negative / count * 100).toFixed(0) : 0
    const positivePercent = sentiment.positive ? (sentiment.positive / count * 100).toFixed(0) : 0
    const neutralPercent = sentiment.neutral ? (sentiment.neutral / count * 100).toFixed(0) : 0
    
    // Calculate trend (mock for now - could be real data)
    const trend = count > maxCount * 0.7 ? 'up' : count > maxCount * 0.3 ? 'stable' : 'down'
    const trendPercent = Math.abs((count / maxCount) * 100 - 50)
    
    // Sentiment data for pie chart
    const sentimentChartData = [
      { name: 'Positive', value: sentiment.positive || 0, color: '#10b981' },
      { name: 'Negative', value: sentiment.negative || 0, color: '#ef4444' },
      { name: 'Neutral', value: sentiment.neutral || 0, color: '#6b7280' }
    ].filter(item => item.value > 0)
    
    const severityColors = {
      'Critical': { dot: 'bg-red-500', text: 'text-red-600', bg: 'bg-red-50', border: 'border-red-200', gradient: 'from-red-500 to-red-600' },
      'High': { dot: 'bg-orange-500', text: 'text-orange-600', bg: 'bg-orange-50', border: 'border-orange-200', gradient: 'from-orange-500 to-orange-600' },
      'Warning': { dot: 'bg-yellow-500', text: 'text-yellow-600', bg: 'bg-yellow-50', border: 'border-yellow-200', gradient: 'from-yellow-500 to-yellow-600' },
      'Medium': { dot: 'bg-blue-500', text: 'text-blue-600', bg: 'bg-blue-50', border: 'border-blue-200', gradient: 'from-blue-500 to-blue-600' },
      'Low': { dot: 'bg-green-500', text: 'text-green-600', bg: 'bg-green-50', border: 'border-green-200', gradient: 'from-green-500 to-green-600' },
      'No Data': { dot: 'bg-gray-400', text: 'text-gray-600', bg: 'bg-gray-50', border: 'border-gray-200', gradient: 'from-gray-400 to-gray-500' }
    }
    
    const colors = severityColors[severity] || severityColors['No Data']
    
    return (
      <div className="min-w-[300px] max-w-[320px] bg-white rounded-xl shadow-2xl border-2 border-gray-200 animate-scale-in overflow-hidden">
        {/* Enhanced header with gradient */}
        <div className={`px-4 py-3 bg-gradient-to-r ${colors.gradient} text-white`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <MapPin className="h-4 w-4" />
              <h3 className="font-bold text-lg">{county}</h3>
            </div>
            <div className="flex items-center gap-1.5 px-2.5 py-1 bg-white/20 backdrop-blur-sm rounded-full">
              <div className={`w-2 h-2 rounded-full ${colors.dot}`}></div>
              <span className="text-xs font-semibold">{severity}</span>
            </div>
          </div>
        </div>
        
        {/* Main content */}
        <div className="p-4 space-y-4">
          {/* Hero stat with trend indicator */}
          <div className="text-center py-3 bg-gradient-to-br from-gray-50 to-white rounded-lg border border-gray-100">
            <div className="flex items-center justify-center gap-2 mb-1">
              <MessageSquare className="h-4 w-4 text-gray-500" />
              <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">Total Feedback</p>
            </div>
            <div className="flex items-center justify-center gap-2">
              <p className="text-4xl font-bold text-gray-900">{count}</p>
              {trend === 'up' && <ArrowUp className="h-5 w-5 text-red-500" />}
              {trend === 'down' && <ArrowDown className="h-5 w-5 text-green-500" />}
              {trend === 'stable' && <Minus className="h-5 w-5 text-gray-400" />}
            </div>
            <div className="mt-2 flex items-center justify-center gap-1 text-xs text-gray-500">
              <Activity className="h-3 w-3" />
              <span>Last {days} days</span>
            </div>
          </div>
          
          {/* Sentiment pie chart */}
          {sentimentChartData.length > 0 && (
            <div className="space-y-3 pt-2 border-t border-gray-100">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <PieChartIcon className="h-4 w-4 text-gray-600" />
                  <h4 className="text-sm font-semibold text-gray-900">Sentiment Breakdown</h4>
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-3">
                {/* Mini pie chart */}
                <div className="h-24">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={sentimentChartData}
                        cx="50%"
                        cy="50%"
                        innerRadius={20}
                        outerRadius={35}
                        dataKey="value"
                      >
                        {sentimentChartData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                
                {/* Sentiment stats */}
                <div className="space-y-2 flex flex-col justify-center">
                  {sentiment.positive > 0 && (
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded-full bg-green-500"></div>
                      <div className="flex-1">
                        <div className="flex items-center justify-between text-xs">
                          <span className="text-gray-600">Positive</span>
                          <span className="font-bold text-gray-900">{sentiment.positive}</span>
                        </div>
                        <div className="w-full h-1 bg-gray-100 rounded-full mt-0.5">
                          <div 
                            className="h-full bg-green-500 rounded-full transition-all"
                            style={{ width: `${positivePercent}%` }}
                          />
                        </div>
                      </div>
                    </div>
                  )}
                  
                  {sentiment.negative > 0 && (
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded-full bg-red-500"></div>
                      <div className="flex-1">
                        <div className="flex items-center justify-between text-xs">
                          <span className="text-gray-600">Negative</span>
                          <span className="font-bold text-gray-900">{sentiment.negative}</span>
                        </div>
                        <div className="w-full h-1 bg-gray-100 rounded-full mt-0.5">
                          <div 
                            className="h-full bg-red-500 rounded-full transition-all"
                            style={{ width: `${negativePercent}%` }}
                          />
                        </div>
                      </div>
                    </div>
                  )}
                  
                  {sentiment.neutral > 0 && (
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded-full bg-gray-400"></div>
                      <div className="flex-1">
                        <div className="flex items-center justify-between text-xs">
                          <span className="text-gray-600">Neutral</span>
                          <span className="font-bold text-gray-900">{sentiment.neutral}</span>
                        </div>
                        <div className="w-full h-1 bg-gray-100 rounded-full mt-0.5">
                          <div 
                            className="h-full bg-gray-400 rounded-full transition-all"
                            style={{ width: `${neutralPercent}%` }}
                          />
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
              
              {/* Alert for high negative sentiment */}
              {sentiment.negative > 0 && negativePercent > 50 && (
                <div className="mt-3 p-2.5 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2">
                  <AlertTriangle className="h-4 w-4 text-red-600 flex-shrink-0" />
                  <div className="flex-1">
                    <p className="text-xs font-semibold text-red-900">High Negative Sentiment</p>
                    <p className="text-xs text-red-700">{negativePercent}% of feedback is negative - requires attention</p>
                  </div>
                </div>
              )}
            </div>
          )}
          
          {/* Priority gauge */}
          <div className="pt-2 border-t border-gray-100">
            <div className="flex items-center justify-between text-xs">
              <div className="flex items-center gap-2">
                <Gauge className="h-4 w-4 text-gray-600" />
                <span className="text-gray-600 font-medium">Priority Level</span>
              </div>
              <div className={`px-2 py-1 rounded-full ${colors.bg} ${colors.border} border`}>
                <span className={`text-xs font-semibold ${colors.text}`}>{severity}</span>
              </div>
            </div>
            <div className="mt-2 w-full h-2 bg-gray-100 rounded-full overflow-hidden">
              <div 
                className={`h-full bg-gradient-to-r ${colors.gradient} rounded-full transition-all`}
                style={{ width: `${Math.min((count / maxCount) * 100, 100)}%` }}
              />
            </div>
          </div>
        </div>
      </div>
    )
  }

  // Sort counties by count for legend
  const sortedCounties = Object.entries(heatmapData)
    .map(([county, data]) => ({ county, ...data }))
    .sort((a, b) => (b.count || 0) - (a.count || 0))
    .slice(0, 5) // Top 5 for legend

          return (
            <div className="w-full rounded-lg overflow-hidden border border-gray-200 relative mobile-scroll">
              {/* Search Bar */}
              <div className="absolute top-4 left-4 z-[1000] bg-white rounded-lg shadow-lg p-2 border border-gray-200 max-w-xs">
                <div className="flex items-center gap-2">
                  <Search className="h-4 w-4 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Search county..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="flex-1 text-sm px-2 py-1 border-0 focus:outline-none focus:ring-0"
                  />
                  {searchQuery && (
                    <button
                      onClick={() => setSearchQuery('')}
                      className="p-1 hover:bg-gray-100 rounded"
                    >
                      <X className="h-3 w-3 text-gray-400" />
                    </button>
                  )}
                </div>
                {searchQuery && filteredData.length > 0 && (
                  <div className="mt-1 text-xs text-gray-500">
                    {filteredData.length} county{filteredData.length !== 1 ? 'ies' : ''} found
                  </div>
                )}
              </div>

              {/* Controls */}
              <div className="absolute top-4 right-4 z-[1000] flex flex-col gap-2 touch-manipulation">
        {/* View Mode Toggle */}
        <div className="bg-white rounded-lg shadow-lg p-2 border border-gray-200 flex gap-1">
          <button
            onClick={() => setViewMode('heat')}
            className={`p-2 rounded transition-all ${
              viewMode === 'heat' 
                ? 'bg-primary-600 text-white shadow-md' 
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
            title="Heat Map View"
          >
            <Zap className="h-4 w-4" />
          </button>
          <button
            onClick={() => setViewMode('choropleth')}
            className={`p-2 rounded transition-all ${
              viewMode === 'choropleth' 
                ? 'bg-primary-600 text-white shadow-md' 
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
            title="Choropleth View"
          >
            <Layers className="h-4 w-4" />
          </button>
          <button
            onClick={() => setViewMode('clusters')}
            className={`p-2 rounded transition-all ${
              viewMode === 'clusters' 
                ? 'bg-primary-600 text-white shadow-md' 
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
            title="Cluster View"
          >
            <BarChart3 className="h-4 w-4" />
          </button>
          <button
            onClick={() => setViewMode('pulse')}
            className={`p-2 rounded transition-all ${
              viewMode === 'pulse' 
                ? 'bg-primary-600 text-white shadow-md' 
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
            title="Pulse/Ripple View"
          >
            <Sparkles className="h-4 w-4" />
          </button>
        </div>

        {/* Severity Filter */}
        <div className="bg-white rounded-lg shadow-lg p-2 border border-gray-200">
          <div className="flex items-center gap-2 mb-2">
            <Filter className="h-4 w-4 text-gray-600" />
            <span className="text-xs font-semibold text-gray-700">Filter</span>
          </div>
          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="w-full text-xs px-2 py-1 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="all">All Severities</option>
            <option value="critical">Critical Only</option>
            <option value="high">High & Critical</option>
            <option value="medium">Medium & Above</option>
            <option value="low">All Issues</option>
          </select>
        </div>

        {/* Animation Toggle */}
        <button
          onClick={() => setShowAnimation(!showAnimation)}
          className={`p-2 rounded-lg shadow-lg border border-gray-200 transition-all ${
            showAnimation 
              ? 'bg-primary-600 text-white' 
              : 'bg-white text-gray-700 hover:bg-gray-50'
          }`}
          title={showAnimation ? "Disable Animation" : "Enable Animation"}
        >
          <div className={`w-4 h-4 rounded-full ${showAnimation ? 'bg-white animate-pulse' : 'bg-gray-400'}`} />
        </button>
      </div>

              {/* Map Container */}
              <div className="h-96 w-full touch-manipulation" style={{ touchAction: 'pan-x pan-y pinch-zoom' }}>
                <MapContainer
          center={[-0.0236, 37.9062]} // Center of Kenya
          zoom={6}
          minZoom={6}
          maxZoom={10}
          style={{ height: '100%', width: '100%' }}
          scrollWheelZoom={true}
          maxBounds={KENYA_BOUNDS}
          maxBoundsViscosity={1.0} // Prevent panning outside Kenya
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          <MapBounds bounds={KENYA_BOUNDS} />
          
          {/* Heat Map View - Gradient circles with intensity */}
          {viewMode === 'heat' && heatPoints.map((point) => {
            const severity = getSeverity(point.count, point.data.sentiment || {})
            const color = getColor(point.count, point.data.sentiment || {})
            const baseRadius = getRadius(point.count)
            
            return (
              <div key={point.county}>
                {/* Outer glow circle for heat effect */}
                {showAnimation && point.intensity > 0.5 && (
                  <Circle
                    center={[point.lat, point.lng]}
                    radius={baseRadius * 3}
                    pathOptions={{
                      fillColor: color,
                      color: 'transparent',
                      fillOpacity: 0.1,
                      weight: 0
                    }}
                  />
                )}
                
                {/* Main marker circle */}
                <CircleMarker
                  center={[point.lat, point.lng]}
                  radius={baseRadius}
                  pathOptions={{
                    fillColor: color,
                    color: '#ffffff',
                    weight: showAnimation && severity === 'Critical' ? 4 : 3,
                    opacity: 1,
                    fillOpacity: 0.8
                  }}
                  className={showAnimation && severity === 'Critical' ? 'animate-pulse' : ''}
                >
                  {/* Inner intensity circle */}
                  <Circle
                    center={[point.lat, point.lng]}
                    radius={baseRadius * 0.6}
                    pathOptions={{
                      fillColor: '#ffffff',
                      color: 'transparent',
                      fillOpacity: 0.3,
                      weight: 0
                    }}
                  />
                  <Popup 
                    className="custom-popup" 
                    maxWidth={320}
                    closeButton={true}
                    autoPan={true}
                    autoPanPadding={[10, 10]}
                  >
                    {renderPopup(point.county, point.data)}
                  </Popup>
                </CircleMarker>
              </div>
            )
          })}

          {/* Choropleth View - Larger filled circles representing county areas */}
          {viewMode === 'choropleth' && heatPoints.map((point) => {
            const severity = getSeverity(point.count, point.data.sentiment || {})
            const color = getColor(point.count, point.data.sentiment || {})
            const radius = getRadius(point.count) * 2.5 // Larger for choropleth effect
            
            return (
              <div key={point.county}>
                {/* Base circle with gradient effect */}
                <Circle
                  center={[point.lat, point.lng]}
                  radius={radius * 1000} // Convert to meters for larger area
                  pathOptions={{
                    fillColor: color,
                    color: '#ffffff',
                    weight: 2,
                    opacity: 0.9,
                    fillOpacity: 0.4
                  }}
                />
                {/* Center marker */}
                <CircleMarker
                  center={[point.lat, point.lng]}
                  radius={12}
                  pathOptions={{
                    fillColor: color,
                    color: '#ffffff',
                    weight: 3,
                    opacity: 1,
                    fillOpacity: 0.9
                  }}
                >
                  <Popup 
                    className="custom-popup" 
                    maxWidth={320}
                    closeButton={true}
                    autoPan={true}
                    autoPanPadding={[10, 10]}
                  >
                    {renderPopup(point.county, point.data)}
                  </Popup>
                </CircleMarker>
              </div>
            )
          })}

          {/* Cluster View - Grouped visualization with count badges */}
          {viewMode === 'clusters' && heatPoints.map((point) => {
            const severity = getSeverity(point.count, point.data.sentiment || {})
            const color = getColor(point.count, point.data.sentiment || {})
            const radius = getRadius(point.count)
            
            return (
              <div key={point.county}>
                {/* Cluster circle */}
                <CircleMarker
                  center={[point.lat, point.lng]}
                  radius={Math.max(radius, 15)}
                  pathOptions={{
                    fillColor: color,
                    color: '#ffffff',
                    weight: 4,
                    opacity: 1,
                    fillOpacity: 0.7
                  }}
                >
                  {/* Count badge circle */}
                  <CircleMarker
                    center={[point.lat, point.lng]}
                    radius={8}
                    pathOptions={{
                      fillColor: '#ffffff',
                      color: color,
                      weight: 2,
                      opacity: 1,
                      fillOpacity: 1
                    }}
                  />
                  <Popup 
                    className="custom-popup" 
                    maxWidth={320}
                    closeButton={true}
                    autoPan={true}
                    autoPanPadding={[10, 10]}
                  >
                    {renderPopup(point.county, point.data)}
                  </Popup>
                </CircleMarker>
              </div>
            )
          })}

          {/* Pulse/Ripple View - Animated ripple effects for high-priority areas */}
          {viewMode === 'pulse' && heatPoints.map((point) => {
            const severity = getSeverity(point.count, point.data.sentiment || {})
            const color = getColor(point.count, point.data.sentiment || {})
            const baseRadius = getRadius(point.count)
            const isHighPriority = severity === 'Critical' || severity === 'High'
            
            return (
              <div key={point.county}>
                {/* Animated ripple circles for high-priority areas */}
                {showAnimation && isHighPriority && (
                  <>
                    <Circle
                      center={[point.lat, point.lng]}
                      radius={baseRadius * 4}
                      pathOptions={{
                        fillColor: color,
                        color: color,
                        weight: 2,
                        opacity: 0.2,
                        fillOpacity: 0.1
                      }}
                      className="animate-pulse"
                    />
                    <Circle
                      center={[point.lat, point.lng]}
                      radius={baseRadius * 6}
                      pathOptions={{
                        fillColor: color,
                        color: color,
                        weight: 1,
                        opacity: 0.1,
                        fillOpacity: 0.05
                      }}
                      className="animate-pulse"
                      style={{ animationDelay: '0.5s' }}
                    />
                  </>
                )}
                
                {/* Main marker with enhanced styling */}
                <CircleMarker
                  center={[point.lat, point.lng]}
                  radius={baseRadius}
                  pathOptions={{
                    fillColor: color,
                    color: '#ffffff',
                    weight: isHighPriority ? 5 : 3,
                    opacity: 1,
                    fillOpacity: 0.85
                  }}
                  className={showAnimation && isHighPriority ? 'animate-pulse' : ''}
                >
                  {/* Inner glow circle */}
                  <Circle
                    center={[point.lat, point.lng]}
                    radius={baseRadius * 0.5}
                    pathOptions={{
                      fillColor: '#ffffff',
                      color: 'transparent',
                      fillOpacity: 0.4,
                      weight: 0
                    }}
                  />
                  
                  {/* Outer ring for emphasis */}
                  {isHighPriority && (
                    <Circle
                      center={[point.lat, point.lng]}
                      radius={baseRadius * 1.3}
                      pathOptions={{
                        fillColor: 'transparent',
                        color: color,
                        weight: 2,
                        opacity: 0.6,
                        fillOpacity: 0,
                        dashArray: '5, 5'
                      }}
                    />
                  )}
                  
                  <Popup 
                    className="custom-popup" 
                    maxWidth={320}
                    closeButton={true}
                    autoPan={true}
                    autoPanPadding={[10, 10]}
                  >
                    {renderPopup(point.county, point.data)}
                  </Popup>
                </CircleMarker>
              </div>
            )
          })}
        </MapContainer>
      </div>
    </div>
  )
}

