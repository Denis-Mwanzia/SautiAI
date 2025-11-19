import { useEffect, useState, useRef } from 'react'
import { MapContainer, TileLayer, Circle, CircleMarker, useMap } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import api from '../services/api'
import { MapPin, TrendingUp, MessageSquare } from 'lucide-react'

// Fix for default marker icons in Leaflet
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
})

// Kenya's approximate boundaries
const KENYA_BOUNDS = [
  [-4.7, 33.9], // Southwest corner
  [5.5, 41.9]   // Northeast corner
]

// Color palette for counties - distinct, vibrant colors
const COUNTY_COLORS = [
  '#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6',
  '#ec4899', '#06b6d4', '#f97316', '#84cc16', '#6366f1',
  '#14b8a6', '#f43f5e', '#a855f7', '#22c55e', '#eab308',
  '#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6',
  '#ec4899', '#06b6d4', '#f97316', '#84cc16', '#6366f1',
  '#14b8a6', '#f43f5e', '#a855f7', '#22c55e', '#eab308',
  '#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6',
  '#ec4899', '#06b6d4', '#f97316', '#84cc16', '#6366f1',
  '#14b8a6', '#f43f5e', '#a855f7', '#22c55e', '#eab308',
  '#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6',
  '#ec4899', '#06b6d4'
]

// Kenyan counties with approximate coordinates
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

// Get unique color for each county
const getCountyColor = (countyName) => {
  const countyList = Object.keys(KENYAN_COUNTIES)
  const index = countyList.indexOf(countyName)
  return COUNTY_COLORS[index % COUNTY_COLORS.length]
}

// Calculate distance between two lat/lng points (Haversine formula)
const calculateDistance = (lat1, lng1, lat2, lng2) => {
  const R = 6371 // Earth's radius in km
  const dLat = (lat2 - lat1) * Math.PI / 180
  const dLng = (lng2 - lng1) * Math.PI / 180
  const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
    Math.sin(dLng / 2) * Math.sin(dLng / 2)
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
  return R * c
}

function MapBounds({ bounds }) {
  const map = useMap()
  
  useEffect(() => {
    if (bounds) {
      map.setMaxBounds(bounds)
      map.fitBounds(bounds, { padding: [20, 20] })
    }
  }, [bounds, map])
  
  return null
}

// Map event handler component - tracks mouse position and finds closest county
function MapEventHandler({ onHover, onLeave, dataPoints }) {
  const hoverTimeoutRef = useRef(null)
  const map = useMap()
  
  useEffect(() => {
    if (!map) return
    
    const handleMouseMove = (e) => {
      if (!e.latlng || dataPoints.length === 0) return
      
      // Clear any existing timeout
      if (hoverTimeoutRef.current) {
        clearTimeout(hoverTimeoutRef.current)
      }
      
      // Find closest county to mouse position
      let closestCounty = null
      let minDistance = Infinity
      
      dataPoints.forEach(point => {
        const distance = calculateDistance(
          e.latlng.lat,
          e.latlng.lng,
          point.lat,
          point.lng
        )
        
        // Consider county within 80km radius
        if (distance < 80 && distance < minDistance) {
          minDistance = distance
          closestCounty = point
        }
      })
      
      if (closestCounty) {
        // Get mouse position in screen coordinates for tooltip
        const containerPoint = map.latLngToContainerPoint(e.latlng)
        const mapContainer = map.getContainer()
        const rect = mapContainer.getBoundingClientRect()
        
        onHover(closestCounty, {
          clientX: rect.left + containerPoint.x,
          clientY: rect.top + containerPoint.y
        })
      } else {
        // Small delay before hiding to prevent flickering
        hoverTimeoutRef.current = setTimeout(() => {
          onLeave()
        }, 150)
      }
    }
    
    const handleMouseOut = () => {
      if (hoverTimeoutRef.current) {
        clearTimeout(hoverTimeoutRef.current)
      }
      onLeave()
    }
    
    map.on('mousemove', handleMouseMove)
    map.on('mouseout', handleMouseOut)
    
    return () => {
      map.off('mousemove', handleMouseMove)
      map.off('mouseout', handleMouseOut)
      if (hoverTimeoutRef.current) {
        clearTimeout(hoverTimeoutRef.current)
      }
    }
  }, [map, dataPoints, onHover, onLeave])
  
  return null
}

// Floating tooltip component with smooth animations
function FloatingTooltip({ point, position }) {
  if (!point || !position) return null

  const { county, count, sentiment } = point
  const negative = sentiment.negative || 0
  const positive = sentiment.positive || 0
  const neutral = sentiment.neutral || 0

  return (
    <div
      className="fixed z-[1000] bg-white rounded-xl shadow-2xl border border-gray-200 p-4 min-w-[240px] pointer-events-none"
      style={{
        left: `${position.x}px`,
        top: `${position.y}px`,
        transform: 'translate(-50%, calc(-100% - 16px))',
        animation: 'fadeIn 0.2s ease-out'
      }}
    >
      {/* Tooltip arrow */}
      <div
        className="absolute bottom-0 left-1/2 transform -translate-x-1/2 translate-y-full"
        style={{
          width: 0,
          height: 0,
          borderLeft: '8px solid transparent',
          borderRight: '8px solid transparent',
          borderTop: '8px solid #e5e7eb'
        }}
      ></div>
      
      <div className="flex items-center gap-2 mb-3">
        <div
          className="w-4 h-4 rounded-full flex-shrink-0 shadow-sm"
          style={{ backgroundColor: point.color }}
        ></div>
        <h3 className="font-semibold text-gray-900 text-base">{county}</h3>
      </div>
      
      <div className="space-y-3">
        <div className="flex items-baseline gap-2">
          <span className="text-3xl font-bold text-gray-900">{count}</span>
          <span className="text-sm text-gray-500">feedback items</span>
        </div>

        {count > 0 && (
          <div className="pt-3 border-t border-gray-200 space-y-2">
            {positive > 0 && (
              <div className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-2">
                  <div className="w-2.5 h-2.5 rounded-full bg-green-500"></div>
                  <span className="text-gray-600">Positive</span>
                </div>
                <span className="font-semibold text-gray-900">{positive}</span>
              </div>
            )}
            {negative > 0 && (
              <div className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-2">
                  <div className="w-2.5 h-2.5 rounded-full bg-red-500"></div>
                  <span className="text-gray-600">Negative</span>
                </div>
                <span className="font-semibold text-gray-900">{negative}</span>
              </div>
            )}
            {neutral > 0 && (
              <div className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-2">
                  <div className="w-2.5 h-2.5 rounded-full bg-gray-400"></div>
                  <span className="text-gray-600">Neutral</span>
                </div>
                <span className="font-semibold text-gray-900">{neutral}</span>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default function CountyMap({ days = 7 }) {
  const [heatmapData, setHeatmapData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [hoveredCounty, setHoveredCounty] = useState(null)
  const [tooltipPosition, setTooltipPosition] = useState(null)

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

  const handleHover = (point, event) => {
    setHoveredCounty(point.county)
    if (event) {
      setTooltipPosition({ x: event.clientX, y: event.clientY })
    }
  }

  const handleLeave = () => {
    setHoveredCounty(null)
    setTooltipPosition(null)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96 bg-gray-50 rounded-lg border border-gray-200">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-2 border-gray-300 border-t-gray-900 mx-auto mb-2"></div>
          <p className="text-sm text-gray-600">Loading county data...</p>
        </div>
      </div>
    )
  }

  if (!heatmapData || Object.keys(heatmapData).length === 0) {
    return (
      <div className="flex items-center justify-center h-96 bg-gray-50 rounded-lg border border-gray-200">
        <div className="text-center">
          <MapPin className="h-12 w-12 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-600 font-medium">No county data available</p>
          <p className="text-sm text-gray-500 mt-1">Try adjusting the time period</p>
        </div>
      </div>
    )
  }

  // Create data points with unique colors
  const dataPoints = Object.entries(heatmapData)
    .map(([county, data]) => {
      const coords = KENYAN_COUNTIES[county]
      if (!coords) return null
      return {
        county,
        lat: coords.lat,
        lng: coords.lng,
        count: data.count || 0,
        sentiment: data.sentiment || {},
        color: getCountyColor(county)
      }
    })
    .filter(Boolean)

  // Sort by count for list view
  const sortedCounties = [...dataPoints].sort((a, b) => b.count - a.count)

  // Get hovered point data
  const hoveredPoint = hoveredCounty ? dataPoints.find(p => p.county === hoveredCounty) : null

  return (
    <div className="space-y-4 relative">
      {/* Floating Tooltip */}
      {hoveredPoint && tooltipPosition && (
        <FloatingTooltip point={hoveredPoint} position={tooltipPosition} />
      )}

      {/* Top Counties List */}
      {sortedCounties.length > 0 && (
        <div className="glass-card p-4">
          <div className="flex items-center gap-2 mb-4">
            <TrendingUp className="h-4 w-4 text-gray-600" />
            <h3 className="text-sm font-semibold text-gray-900">Top Counties</h3>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
            {sortedCounties.slice(0, 8).map((point) => (
              <div
                key={point.county}
                className="p-3 bg-gray-50 rounded-lg border border-gray-200 hover:border-gray-300 transition-colors"
              >
                <div className="flex items-center gap-2 mb-1">
                  <div
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: point.color }}
                  ></div>
                  <span className="text-xs font-medium text-gray-900 truncate">{point.county}</span>
                </div>
                <div className="flex items-baseline gap-1">
                  <span className="text-lg font-bold text-gray-900">{point.count}</span>
                  <span className="text-xs text-gray-500">items</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Map */}
      <div className="glass-card p-0 overflow-hidden relative">
        <div className="h-96 w-full">
          <MapContainer
            center={[-0.0236, 37.9062]}
            zoom={6}
            minZoom={6}
            maxZoom={10}
            style={{ height: '100%', width: '100%' }}
            scrollWheelZoom={true}
            maxBounds={KENYA_BOUNDS}
            maxBoundsViscosity={1.0}
          >
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            <MapBounds bounds={KENYA_BOUNDS} />
            <MapEventHandler
              onHover={handleHover}
              onLeave={handleLeave}
              dataPoints={dataPoints}
            />
            
            {/* County markers - subtle dots that highlight on hover */}
            {dataPoints.map((point) => {
              const isHovered = hoveredCounty === point.county
              
              return (
                <div key={point.county}>
                  {/* Outer glow circles - appear on hover with pulse animation */}
                  {isHovered && (
                    <>
                      <Circle
                        center={[point.lat, point.lng]}
                        radius={80000} // 80km radius - outer glow
                        pathOptions={{
                          fillColor: point.color,
                          color: point.color,
                          weight: 0,
                          opacity: 0.15,
                          fillOpacity: 0.08
                        }}
                        className="animate-pulse"
                      />
                      <Circle
                        center={[point.lat, point.lng]}
                        radius={60000} // 60km radius - middle glow
                        pathOptions={{
                          fillColor: point.color,
                          color: point.color,
                          weight: 0,
                          opacity: 0.25,
                          fillOpacity: 0.12
                        }}
                      />
                      <Circle
                        center={[point.lat, point.lng]}
                        radius={40000} // 40km radius - inner glow
                        pathOptions={{
                          fillColor: point.color,
                          color: point.color,
                          weight: 0,
                          opacity: 0.35,
                          fillOpacity: 0.15
                        }}
                      />
                    </>
                  )}
                  
                  {/* Main county marker - subtle dot, grows and brightens on hover */}
                  <CircleMarker
                    center={[point.lat, point.lng]}
                    radius={isHovered ? 16 : 6}
                    pathOptions={{
                      fillColor: point.color,
                      color: '#ffffff',
                      weight: isHovered ? 4 : 2,
                      opacity: 1,
                      fillOpacity: isHovered ? 0.95 : 0.5
                    }}
                    className="transition-all duration-300 ease-out"
                  />
                </div>
              )
            })}
          </MapContainer>
        </div>
      </div>

      {/* County Color Legend */}
      <div className="glass-card p-4">
        <div className="flex items-center gap-2 mb-3">
          <MessageSquare className="h-4 w-4 text-gray-600" />
          <h3 className="text-sm font-semibold text-gray-900">Counties</h3>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2 max-h-48 overflow-y-auto">
          {sortedCounties.map((point) => (
            <div
              key={point.county}
              className={`flex items-center gap-2 text-xs p-1.5 rounded transition-colors cursor-pointer ${
                hoveredCounty === point.county
                  ? 'bg-gray-100 border border-gray-300'
                  : 'hover:bg-gray-50'
              }`}
              onMouseEnter={() => {
                setHoveredCounty(point.county)
                // Set tooltip position to center of this element
                const rect = document.querySelector(`[data-county="${point.county}"]`)?.getBoundingClientRect()
                if (rect) {
                  setTooltipPosition({ x: rect.left + rect.width / 2, y: rect.top })
                }
              }}
              onMouseLeave={() => {
                if (hoveredCounty === point.county) {
                  setHoveredCounty(null)
                  setTooltipPosition(null)
                }
              }}
              data-county={point.county}
            >
              <div
                className="w-3 h-3 rounded-full flex-shrink-0"
                style={{ backgroundColor: point.color }}
              ></div>
              <span className="text-gray-700 truncate">{point.county}</span>
              <span className="text-gray-500 ml-auto">{point.count}</span>
            </div>
          ))}
        </div>
        <p className="text-xs text-gray-500 mt-3">
          Hover over counties on the map or in the list to see detailed statistics. Each county has a unique color.
        </p>
      </div>
    </div>
  )
}
