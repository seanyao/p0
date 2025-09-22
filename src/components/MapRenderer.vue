<template>
  <div class="map-renderer">
    <div class="renderer-header">
      <h3>🗺️ 路线可视化</h3>
      <div class="controls">
        <button @click="clearAll" class="btn-clear">清空</button>
        <button @click="exportRoute" class="btn-export">导出路线</button>
      </div>
    </div>

    <div class="map-container" ref="mapContainer">
      <!-- 地图容器 -->
      <div id="map-container" class="amap-container"></div>
      
      <!-- 地点列表 -->
      <div class="locations-panel">
        <h4>📍 地点列表 ({{ locations.length }})</h4>
        <div class="location-list">
          <div 
            v-for="(location, index) in locations" 
            :key="index"
            class="location-item"
            :class="{ active: selectedLocation === index }"
            @click="selectLocation(index)"
          >
            <div class="location-info">
              <span class="location-index">{{ index + 1 }}</span>
              <div class="location-details">
                <div class="location-name">{{ location.name || location.formatted_address }}</div>
                <div class="location-coords">
                  {{ location.longitude?.toFixed(6) }}, {{ location.latitude?.toFixed(6) }}
                </div>
              </div>
            </div>
            <button @click.stop="removeLocation(index)" class="btn-remove">×</button>
          </div>
        </div>
      </div>

      <!-- 路线信息 -->
      <div class="routes-panel" v-if="routes.length > 0">
        <h4>🛣️ 路线信息</h4>
        <div class="route-list">
          <div v-for="(route, index) in routes" :key="route.id" class="route-item">
            <span class="route-index">{{ index + 1 }}</span>
            <span class="route-info">
              {{ route.from.name || route.from.formatted_address }} 
              → 
              {{ route.to.name || route.to.formatted_address }}
            </span>
          </div>
        </div>
        <div class="route-stats">
          <p>总路线段数: {{ routes.length }}</p>
          <p>总地点数: {{ locations.length }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, nextTick } from 'vue'
import '../types/amap.d.ts'

// Props
const props = defineProps<{
  locations: any[]
  routes: any[]
}>()

// Emits
const emit = defineEmits<{
  'location-removed': [index: number]
  'locations-cleared': []
}>()

// 响应式数据
const mapContainer = ref<HTMLElement>()
const selectedLocation = ref<number>(-1)
const map = ref<any>(null)
const markers = ref<any[]>([])
const polylines = ref<any[]>([])

// 选择地点
const selectLocation = (index: number) => {
  selectedLocation.value = index
  
  // 验证地点坐标
  const location = props.locations[index]
  if (!location) return
  
  const lng = parseFloat(location.longitude)
  const lat = parseFloat(location.latitude)
  
  if (isNaN(lng) || isNaN(lat)) {
    console.warn('选中地点坐标无效:', location)
    return
  }
  
  // 移动地图中心到选中地点
  if (map.value) {
    try {
      map.value.setCenter([lng, lat])
      map.value.setZoom(15)
    } catch (error) {
      console.error('移动地图中心失败:', error)
    }
  }
}

// 移除地点
const removeLocation = (index: number) => {
  emit('location-removed', index)
}

// 清空所有
const clearAll = () => {
  emit('locations-cleared')
}

// 导出路线
const exportRoute = () => {
  const routeData = {
    locations: props.locations,
    routes: props.routes,
    exportTime: new Date().toISOString()
  }
  
  const blob = new Blob([JSON.stringify(routeData, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `route-${Date.now()}.json`
  a.click()
  URL.revokeObjectURL(url)
}

// 初始化地图
const initMap = () => {
  if (!window.AMap) {
    console.error('高德地图API未加载')
    return
  }
  
  try {
    map.value = new window.AMap.Map('map-container', {
      zoom: 10,
      center: [116.397428, 39.90923], // 北京
      mapStyle: 'amap://styles/normal'
    })
    
    console.log('地图初始化成功')
  } catch (error) {
    console.error('地图初始化失败:', error)
  }
}

// 更新地图标记
const updateMarkers = () => {
  if (!map.value) return

  // 清除现有标记
  markers.value.forEach(marker => marker.setMap(null))
  markers.value = []

  // 添加新标记
  props.locations.forEach((location, index) => {
    // 验证坐标数据
    const lng = parseFloat(location.longitude)
    const lat = parseFloat(location.latitude)
    
    if (isNaN(lng) || isNaN(lat)) {
      console.warn(`地点 ${index + 1} 坐标无效:`, location)
      return
    }
    
    console.log(`创建标记 ${index + 1}:`, { lng, lat, name: location.name })
    
    try {
      // 首先尝试创建带offset的标记
      const marker = new window.AMap.Marker({
        position: [lng, lat],
        title: location.name || location.formatted_address,
        label: {
          content: `${index + 1}`,
          offset: new window.AMap.Pixel(-5, -5)
        }
      })
      
      marker.setMap(map.value)
      markers.value.push(marker)
      console.log(`标记 ${index + 1} 创建成功`)
    } catch (error) {
      console.error(`创建标记失败 (地点 ${index + 1}):`, error, location)
      // 尝试不使用offset创建标记
      try {
        const fallbackMarker = new window.AMap.Marker({
          position: [lng, lat],
          title: location.name || location.formatted_address,
          label: {
            content: `${index + 1}`
          }
        })
        
        fallbackMarker.setMap(map.value)
        markers.value.push(fallbackMarker)
        console.log(`使用备用方案创建标记成功 (地点 ${index + 1})`)
      } catch (fallbackError) {
        console.error(`备用标记创建也失败 (地点 ${index + 1}):`, fallbackError)
      }
    }
  })

  // 自适应视野
  const validLocations = props.locations.filter(location => {
    const lng = parseFloat(location.longitude)
    const lat = parseFloat(location.latitude)
    return !isNaN(lng) && !isNaN(lat)
  })
  
  if (validLocations.length > 0) {
    try {
      const bounds = new window.AMap.Bounds()
      validLocations.forEach(location => {
        bounds.extend([parseFloat(location.longitude), parseFloat(location.latitude)])
      })
      map.value.setBounds(bounds)
      console.log(`设置地图边界成功，包含 ${validLocations.length} 个有效地点`)
    } catch (error) {
      console.error('设置地图边界失败:', error)
    }
  }
}

// 更新路线
const updateRoutes = () => {
  if (!map.value) return

  // 清除现有路线
  polylines.value.forEach(polyline => polyline.setMap(null))
  polylines.value = []

  // 添加新路线
  props.routes.forEach((route, index) => {
    // 验证路线数据
    const fromLng = parseFloat(route.from?.longitude)
    const fromLat = parseFloat(route.from?.latitude)
    const toLng = parseFloat(route.to?.longitude)
    const toLat = parseFloat(route.to?.latitude)
    
    if (isNaN(fromLng) || isNaN(fromLat) || isNaN(toLng) || isNaN(toLat)) {
      console.warn(`路线 ${index + 1} 坐标无效:`, route)
      return
    }
    
    try {
      const polyline = new window.AMap.Polyline({
        path: [
          [fromLng, fromLat],
          [toLng, toLat]
        ],
        strokeColor: '#3366FF',
        strokeWeight: 3,
        strokeOpacity: 0.8
      })
      
      polyline.setMap(map.value)
      polylines.value.push(polyline)
    } catch (error) {
      console.error(`创建路线失败 (路线 ${index + 1}):`, error, route)
    }
  })
}

// 监听数据变化
watch(() => props.locations, () => {
  nextTick(() => {
    updateMarkers()
  })
}, { deep: true })

watch(() => props.routes, () => {
  nextTick(() => {
    updateRoutes()
  })
}, { deep: true })

// 组件挂载
onMounted(() => {
  // 等待高德地图API加载完成
  const checkAMapLoaded = () => {
    if (window.AMap) {
      console.log('高德地图API已加载')
      initMap()
      nextTick(() => {
        updateMarkers()
        updateRoutes()
      })
    } else {
      console.log('等待高德地图API加载...')
      setTimeout(checkAMapLoaded, 100)
    }
  }
  
  checkAMapLoaded()
})
</script>

<style scoped>
.map-renderer {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.renderer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  background: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
}

.renderer-header h3 {
  margin: 0;
  color: #333;
  font-size: 1.2rem;
}

.controls {
  display: flex;
  gap: 0.5rem;
}

.btn-clear, .btn-export {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.2s;
}

.btn-clear {
  background: #dc3545;
  color: white;
}

.btn-clear:hover {
  background: #c82333;
}

.btn-export {
  background: #28a745;
  color: white;
}

.btn-export:hover {
  background: #218838;
}

.map-container {
  display: grid;
  grid-template-columns: 1fr 300px;
  height: 500px;
}

.amap-container {
  width: 100%;
  height: 100%;
}

.locations-panel, .routes-panel {
  padding: 1rem;
  background: #f8f9fa;
  border-left: 1px solid #e9ecef;
  overflow-y: auto;
}

.locations-panel h4, .routes-panel h4 {
  margin: 0 0 1rem 0;
  color: #333;
  font-size: 1rem;
}

.location-list, .route-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.location-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid #e9ecef;
}

.location-item:hover {
  background: #e3f2fd;
  border-color: #2196f3;
}

.location-item.active {
  background: #e3f2fd;
  border-color: #2196f3;
}

.location-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 1;
}

.location-index {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  background: #2196f3;
  color: white;
  border-radius: 50%;
  font-size: 0.8rem;
  font-weight: bold;
}

.location-details {
  flex: 1;
}

.location-name {
  font-weight: 500;
  color: #333;
  margin-bottom: 0.25rem;
}

.location-coords {
  font-size: 0.8rem;
  color: #666;
  font-family: monospace;
}

.btn-remove {
  width: 24px;
  height: 24px;
  border: none;
  background: #dc3545;
  color: white;
  border-radius: 50%;
  cursor: pointer;
  font-size: 1rem;
  line-height: 1;
  transition: background-color 0.2s;
}

.btn-remove:hover {
  background: #c82333;
}

.route-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  background: white;
  border-radius: 4px;
  border: 1px solid #e9ecef;
}

.route-index {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  background: #28a745;
  color: white;
  border-radius: 50%;
  font-size: 0.7rem;
  font-weight: bold;
}

.route-info {
  font-size: 0.9rem;
  color: #333;
}

.route-stats {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #e9ecef;
}

.route-stats p {
  margin: 0.25rem 0;
  font-size: 0.9rem;
  color: #666;
}

@media (max-width: 768px) {
  .map-container {
    grid-template-columns: 1fr;
    grid-template-rows: 300px 1fr;
    height: auto;
  }
  
  .locations-panel, .routes-panel {
    border-left: none;
    border-top: 1px solid #e9ecef;
  }
}
</style>