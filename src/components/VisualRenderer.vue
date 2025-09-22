<template>
  <div class="artistic-route-renderer">
    <!-- 艺术风格选择器 -->
    <div class="style-selector-panel" v-if="showStyleSelector">
      <h4>🎨 选择艺术风格</h4>
      <div class="style-options">
        <div 
          v-for="styleOption in styleOptions" 
          :key="styleOption.value"
          @click="selectedStyle = styleOption.value"
          :class="{ active: selectedStyle === styleOption.value }"
          class="style-option"
        >
          <div class="style-preview" :style="styleOption.preview"></div>
          <span class="style-name">{{ styleOption.icon }} {{ styleOption.name }}</span>
        </div>
      </div>
    </div>

    <!-- 艺术化路线图画布 -->
    <div class="route-canvas-container">
      <canvas 
        ref="routeCanvas" 
        :width="canvasWidth" 
        :height="canvasHeight"
        class="artistic-canvas"
      ></canvas>
      
      <!-- 画布覆盖层 - 用于添加艺术效果 -->
      <div class="canvas-overlay" :class="`style-${selectedStyle}`">
        <div class="artistic-elements">
          <!-- 动态粒子效果 -->
          <div v-if="selectedStyle === 'watercolor'" class="watercolor-particles"></div>
          <!-- 几何图形 -->
          <div v-if="selectedStyle === 'minimalist'" class="geometric-shapes"></div>
          <!-- 复古纹理 -->
          <div v-if="selectedStyle === 'vintage'" class="vintage-texture"></div>
        </div>
      </div>
    </div>

    <!-- 路线信息面板 -->
    <div class="route-info-panel" v-if="locations.length > 0">
      <h4>✈️ 旅行路线</h4>
      <div class="route-timeline">
        <div 
          v-for="(location, index) in locations" 
          :key="index"
          class="timeline-item"
          :class="{ active: index === activeLocationIndex }"
          @mouseenter="highlightLocation(index)"
          @mouseleave="clearHighlight()"
        >
          <div class="timeline-marker">{{ index + 1 }}</div>
          <div class="timeline-content">
            <h5>{{ location.name }}</h5>
            <p class="location-description">{{ getLocationDescription(location) }}</p>
            <div class="travel-info" v-if="index < locations.length - 1">
              <span class="distance">{{ getDistanceToNext(index) }}</span>
              <span class="duration">{{ getDurationToNext(index) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import type { LocationInfo } from '../types/location'

// Props
const props = defineProps<{
  locations: LocationInfo[]
}>()

// 响应式数据
const routeCanvas = ref<HTMLCanvasElement>()
const canvasWidth = ref(800)
const canvasHeight = ref(600)
const selectedStyle = ref('watercolor')
const showStyleSelector = ref(true)
const activeLocationIndex = ref(-1)

// 艺术风格选项
const styleOptions = ref([
  {
    value: 'watercolor',
    name: '水彩风格',
    icon: '🎨',
    preview: {
      background: 'linear-gradient(45deg, #ff9a9e 0%, #fecfef 50%, #fecfef 100%)',
      borderRadius: '8px'
    }
  },
  {
    value: 'minimalist',
    name: '极简风格',
    icon: '⚪',
    preview: {
      background: 'linear-gradient(45deg, #667eea 0%, #764ba2 100%)',
      borderRadius: '8px'
    }
  },
  {
    value: 'vintage',
    name: '复古风格',
    icon: '📸',
    preview: {
      background: 'linear-gradient(45deg, #f093fb 0%, #f5576c 100%)',
      borderRadius: '8px'
    }
  },
  {
    value: 'neon',
    name: '霓虹风格',
    icon: '✨',
    preview: {
      background: 'linear-gradient(45deg, #4facfe 0%, #00f2fe 100%)',
      borderRadius: '8px'
    }
  }
])

// 计算属性
const longitudeRange = computed(() => {
  if (props.locations.length === 0) return '0°'
  const lngs = props.locations.map(loc => loc.coordinates.longitude)
  const min = Math.min(...lngs)
  const max = Math.max(...lngs)
  return `${min.toFixed(3)}° ~ ${max.toFixed(3)}°`
})

const latitudeRange = computed(() => {
  if (props.locations.length === 0) return '0°'
  const lats = props.locations.map(loc => loc.coordinates.latitude)
  const min = Math.min(...lats)
  const max = Math.max(...lats)
  return `${min.toFixed(3)}° ~ ${max.toFixed(3)}°`
})

// 方法
function highlightLocation(index: number) {
  activeLocationIndex.value = index
  // 在画布上高亮显示对应位置
  drawArtisticRoute()
}

function clearHighlight() {
  activeLocationIndex.value = -1
  drawArtisticRoute()
}

function getLocationDescription(location: LocationInfo): string {
  return `经度: ${location.coordinates.longitude.toFixed(4)}, 纬度: ${location.coordinates.latitude.toFixed(4)}`
}

function getDistanceToNext(index: number): string {
  if (index >= props.locations.length - 1) return ''
  const current = props.locations[index]
  const next = props.locations[index + 1]
  
  // 简化的距离计算
  const lat1 = current.coordinates.latitude * Math.PI / 180
  const lat2 = next.coordinates.latitude * Math.PI / 180
  const deltaLat = (next.coordinates.latitude - current.coordinates.latitude) * Math.PI / 180
  const deltaLng = (next.coordinates.longitude - current.coordinates.longitude) * Math.PI / 180
  
  const a = Math.sin(deltaLat/2) * Math.sin(deltaLat/2) +
          Math.cos(lat1) * Math.cos(lat2) *
          Math.sin(deltaLng/2) * Math.sin(deltaLng/2)
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a))
  const distance = 6371 * c // 地球半径
  
  return `${distance.toFixed(0)} km`
}

function getDurationToNext(index: number): string {
  if (index >= props.locations.length - 1) return ''
  const distance = parseFloat(getDistanceToNext(index))
  const hours = Math.ceil(distance / 500) // 假设平均速度500km/h
  return `${hours}h`
}

// 坐标转换函数
function coordinateToCanvas(longitude: number, latitude: number) {
  if (props.locations.length === 0) return { x: 0, y: 0 }
  
  const lngs = props.locations.map(loc => loc.coordinates.longitude)
  const lats = props.locations.map(loc => loc.coordinates.latitude)
  
  const minLng = Math.min(...lngs)
  const maxLng = Math.max(...lngs)
  const minLat = Math.min(...lats)
  const maxLat = Math.max(...lats)
  
  const padding = 80
  const x = padding + ((longitude - minLng) / (maxLng - minLng || 1)) * (canvasWidth.value - 2 * padding)
  const y = padding + ((maxLat - latitude) / (maxLat - minLat || 1)) * (canvasHeight.value - 2 * padding)
  
  return { x, y }
}

// 艺术化路线绘制
function drawArtisticRoute() {
  const canvas = routeCanvas.value
  if (!canvas) return
  
  const ctx = canvas.getContext('2d')
  if (!ctx) return
  
  // 清空画布
  ctx.clearRect(0, 0, canvasWidth.value, canvasHeight.value)
  
  if (props.locations.length === 0) return
  
  // 根据选择的风格设置绘制参数
  const styleConfig = getStyleConfig(selectedStyle.value)
  
  // 绘制背景
  drawBackground(ctx, styleConfig)
  
  // 绘制路线连线
  if (props.locations.length > 1) {
    drawRoutePath(ctx, styleConfig)
  }
  
  // 绘制地点标记
  drawLocationMarkers(ctx, styleConfig)
}

function getStyleConfig(style: string) {
  const configs: Record<string, any> = {
    watercolor: {
      backgroundColor: '#f8fafc',
      pathColor: '#3b82f6',
      markerColors: ['#ef4444', '#f59e0b', '#10b981', '#8b5cf6', '#f97316'],
      pathWidth: 3,
      markerSize: 12,
      shadowBlur: 8
    },
    minimalist: {
      backgroundColor: '#ffffff',
      pathColor: '#374151',
      markerColors: ['#111827'],
      pathWidth: 2,
      markerSize: 8,
      shadowBlur: 0
    },
    vintage: {
      backgroundColor: '#fef7ed',
      pathColor: '#92400e',
      markerColors: ['#dc2626', '#d97706', '#059669', '#7c3aed'],
      pathWidth: 4,
      markerSize: 14,
      shadowBlur: 6
    },
    neon: {
      backgroundColor: '#0f172a',
      pathColor: '#06b6d4',
      markerColors: ['#f59e0b', '#ef4444', '#10b981', '#8b5cf6'],
      pathWidth: 3,
      markerSize: 12,
      shadowBlur: 10
    }
  }
  return configs[style] || configs.watercolor
}

function drawBackground(ctx: CanvasRenderingContext2D, config: any) {
  ctx.fillStyle = config.backgroundColor
  ctx.fillRect(0, 0, canvasWidth.value, canvasHeight.value)
}

function drawRoutePath(ctx: CanvasRenderingContext2D, config: any) {
  ctx.strokeStyle = config.pathColor
  ctx.lineWidth = config.pathWidth
  ctx.lineCap = 'round'
  ctx.lineJoin = 'round'
  
  if (config.shadowBlur > 0) {
    ctx.shadowColor = config.pathColor
    ctx.shadowBlur = config.shadowBlur
  }
  
  ctx.beginPath()
  props.locations.forEach((location, index) => {
    const { x, y } = coordinateToCanvas(location.coordinates.longitude, location.coordinates.latitude)
    if (index === 0) {
      ctx.moveTo(x, y)
    } else {
      ctx.lineTo(x, y)
    }
  })
  ctx.stroke()
  
  // 重置阴影
  ctx.shadowBlur = 0
}

function drawLocationMarkers(ctx: CanvasRenderingContext2D, config: any) {
  props.locations.forEach((location, index) => {
    const { x, y } = coordinateToCanvas(location.coordinates.longitude, location.coordinates.latitude)
    const isActive = index === activeLocationIndex.value
    const markerSize = isActive ? config.markerSize * 1.5 : config.markerSize
    
    // 绘制标记点
    ctx.fillStyle = config.markerColors[index % config.markerColors.length]
    ctx.beginPath()
    ctx.arc(x, y, markerSize, 0, 2 * Math.PI)
    ctx.fill()
    
    // 绘制边框
    ctx.strokeStyle = '#ffffff'
    ctx.lineWidth = 2
    ctx.stroke()
    
    // 绘制序号
    ctx.fillStyle = '#ffffff'
    ctx.font = `bold ${markerSize}px Arial`
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    ctx.fillText((index + 1).toString(), x, y)
    
    // 绘制地点名称
    ctx.fillStyle = selectedStyle.value === 'neon' ? '#ffffff' : '#1e293b'
    ctx.font = '14px Arial'
    ctx.textAlign = 'center'
    ctx.textBaseline = 'top'
    ctx.fillText(location.name, x, y + markerSize + 8)
  })
}

// 导出PNG图片
function exportToPNG() {
  const canvas = routeCanvas.value
  if (!canvas) return
  
  // 创建一个新的canvas用于导出，确保高质量
  const exportCanvas = document.createElement('canvas')
  const exportCtx = exportCanvas.getContext('2d')
  if (!exportCtx) return
  
  // 设置高分辨率
  const scale = 2
  exportCanvas.width = canvasWidth.value * scale
  exportCanvas.height = canvasHeight.value * scale
  exportCtx.scale(scale, scale)
  
  // 重新绘制到导出canvas
  drawArtisticRouteToCanvas(exportCtx, canvasWidth.value, canvasHeight.value)
  
  // 创建下载链接
  const link = document.createElement('a')
  const timestamp = new Date().toISOString().slice(0, 10)
  link.download = `艺术化旅行路线图-${selectedStyle.value}-${timestamp}.png`
  link.href = exportCanvas.toDataURL('image/png', 1.0)
  link.click()
}

// 绘制到指定canvas的通用函数
function drawArtisticRouteToCanvas(ctx: CanvasRenderingContext2D, width: number, height: number) {
  // 清空画布
  ctx.clearRect(0, 0, width, height)
  
  if (props.locations.length === 0) return
  
  // 根据选择的风格设置绘制参数
  const styleConfig = getStyleConfig(selectedStyle.value)
  
  // 绘制背景
  ctx.fillStyle = styleConfig.backgroundColor
  ctx.fillRect(0, 0, width, height)
  
  // 绘制路线连线
  if (props.locations.length > 1) {
    drawRoutePathToCanvas(ctx, styleConfig, width, height)
  }
  
  // 绘制地点标记
  drawLocationMarkersToCanvas(ctx, styleConfig, width, height)
  
  // 添加标题和日期信息
  drawTitleAndInfo(ctx, styleConfig, width, height)
}

function drawRoutePathToCanvas(ctx: CanvasRenderingContext2D, config: any, width: number, height: number) {
  ctx.strokeStyle = config.pathColor
  ctx.lineWidth = config.pathWidth
  ctx.lineCap = 'round'
  ctx.lineJoin = 'round'
  
  if (config.shadowBlur > 0) {
    ctx.shadowColor = config.pathColor
    ctx.shadowBlur = config.shadowBlur
  }
  
  ctx.beginPath()
  props.locations.forEach((location, index) => {
    const { x, y } = coordinateToCanvasForExport(location.coordinates.longitude, location.coordinates.latitude, width, height)
    if (index === 0) {
      ctx.moveTo(x, y)
    } else {
      ctx.lineTo(x, y)
    }
  })
  ctx.stroke()
  
  // 重置阴影
  ctx.shadowBlur = 0
}

function drawLocationMarkersToCanvas(ctx: CanvasRenderingContext2D, config: any, width: number, height: number) {
  props.locations.forEach((location, index) => {
    const { x, y } = coordinateToCanvasForExport(location.coordinates.longitude, location.coordinates.latitude, width, height)
    const markerSize = config.markerSize
    
    // 绘制标记点
    ctx.fillStyle = config.markerColors[index % config.markerColors.length]
    ctx.beginPath()
    ctx.arc(x, y, markerSize, 0, 2 * Math.PI)
    ctx.fill()
    
    // 绘制边框
    ctx.strokeStyle = '#ffffff'
    ctx.lineWidth = 2
    ctx.stroke()
    
    // 绘制序号
    ctx.fillStyle = '#ffffff'
    ctx.font = `bold ${markerSize}px Arial`
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    ctx.fillText((index + 1).toString(), x, y)
    
    // 绘制地点名称
    ctx.fillStyle = selectedStyle.value === 'neon' ? '#ffffff' : '#1e293b'
    ctx.font = '14px Arial'
    ctx.textAlign = 'center'
    ctx.textBaseline = 'top'
    ctx.fillText(location.name, x, y + markerSize + 8)
  })
}

function drawTitleAndInfo(ctx: CanvasRenderingContext2D, config: any, width: number, height: number) {
  // 绘制标题
  ctx.fillStyle = selectedStyle.value === 'neon' ? '#ffffff' : '#1e293b'
  ctx.font = 'bold 24px Arial'
  ctx.textAlign = 'center'
  ctx.fillText('🎨 艺术化旅行路线图', width / 2, 40)
  
  // 绘制副标题
  ctx.font = '16px Arial'
  ctx.fillText(`${props.locations.length}个目的地 · ${selectedStyle.value === 'watercolor' ? '水彩风格' : selectedStyle.value === 'minimalist' ? '极简风格' : selectedStyle.value === 'vintage' ? '复古风格' : '霓虹风格'}`, width / 2, 65)
  
  // 绘制生成时间
  ctx.font = '12px Arial'
  ctx.fillStyle = '#64748b'
  const now = new Date().toLocaleString('zh-CN')
  ctx.fillText(`生成时间: ${now}`, width / 2, height - 20)
}

// 导出专用的坐标转换函数
function coordinateToCanvasForExport(longitude: number, latitude: number, width: number, height: number) {
  if (props.locations.length === 0) return { x: 0, y: 0 }
  
  const lngs = props.locations.map(loc => loc.coordinates.longitude)
  const lats = props.locations.map(loc => loc.coordinates.latitude)
  
  const minLng = Math.min(...lngs)
  const maxLng = Math.max(...lngs)
  const minLat = Math.min(...lats)
  const maxLat = Math.max(...lats)
  
  const padding = 100 // 导出时使用更大的边距
  const x = padding + ((longitude - minLng) / (maxLng - minLng || 1)) * (width - 2 * padding)
  const y = padding + ((maxLat - latitude) / (maxLat - minLat || 1)) * (height - 2 * padding)
  
  return { x, y }
}

// 监听数据变化
watch(() => props.locations, () => {
  drawArtisticRoute()
}, { deep: true })

watch(selectedStyle, () => {
  drawArtisticRoute()
})

// 组件挂载后初始化
onMounted(() => {
  drawArtisticRoute()
})

// 暴露导出函数给父组件
defineExpose({
  exportToPNG
})
</script>

<style scoped>
.artistic-route-renderer {
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  position: relative;
}

.style-selector-panel {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 24px;
  text-align: center;
}

.style-selector-panel h4 {
  margin: 0 0 20px 0;
  font-size: 1.4rem;
  font-weight: 600;
}

.style-options {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 16px;
  max-width: 600px;
  margin: 0 auto;
}

.style-option {
  background: rgba(255, 255, 255, 0.1);
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: center;
}

.style-option:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-4px);
}

.style-option.active {
  background: rgba(255, 255, 255, 0.9);
  color: #667eea;
  border-color: rgba(255, 255, 255, 0.8);
  transform: translateY(-4px);
}

.style-preview {
  width: 40px;
  height: 40px;
  margin: 0 auto 12px;
  border-radius: 8px;
}

.style-name {
  font-size: 0.9rem;
  font-weight: 500;
}

.route-canvas-container {
  position: relative;
  padding: 24px;
  text-align: center;
}

.artistic-canvas {
  border: 3px solid #e2e8f0;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  background: white;
  max-width: 100%;
  height: auto;
}

.canvas-overlay {
  position: absolute;
  top: 24px;
  left: 24px;
  right: 24px;
  bottom: 24px;
  pointer-events: none;
  border-radius: 12px;
  overflow: hidden;
}

.artistic-elements {
  width: 100%;
  height: 100%;
  position: relative;
}

.watercolor-particles {
  position: absolute;
  width: 100%;
  height: 100%;
  background: radial-gradient(circle at 20% 30%, rgba(255, 154, 158, 0.1) 0%, transparent 50%),
              radial-gradient(circle at 80% 70%, rgba(254, 207, 239, 0.1) 0%, transparent 50%);
  animation: float 6s ease-in-out infinite;
}

.geometric-shapes::before {
  content: '';
  position: absolute;
  top: 10%;
  right: 10%;
  width: 60px;
  height: 60px;
  border: 2px solid rgba(102, 126, 234, 0.2);
  border-radius: 50%;
  animation: rotate 20s linear infinite;
}

.vintage-texture {
  position: absolute;
  width: 100%;
  height: 100%;
  background-image: 
    radial-gradient(circle at 25% 25%, rgba(146, 64, 14, 0.05) 0%, transparent 50%),
    radial-gradient(circle at 75% 75%, rgba(217, 119, 6, 0.05) 0%, transparent 50%);
  filter: sepia(20%);
}

.route-info-panel {
  background: #f8fafc;
  padding: 24px;
  border-top: 1px solid #e2e8f0;
}

.route-info-panel h4 {
  margin: 0 0 20px 0;
  color: #1e293b;
  font-size: 1.2rem;
  font-weight: 600;
}

.route-timeline {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.timeline-item {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 16px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  cursor: pointer;
}

.timeline-item:hover {
  transform: translateX(8px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.timeline-item.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  transform: translateX(8px);
}

.timeline-marker {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  background: #3b82f6;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.9rem;
}

.timeline-item.active .timeline-marker {
  background: rgba(255, 255, 255, 0.2);
}

.timeline-content {
  flex: 1;
}

.timeline-content h5 {
  margin: 0 0 8px 0;
  font-size: 1.1rem;
  font-weight: 600;
}

.location-description {
  margin: 0 0 12px 0;
  color: #64748b;
  font-size: 0.9rem;
  line-height: 1.4;
}

.timeline-item.active .location-description {
  color: rgba(255, 255, 255, 0.8);
}

.travel-info {
  display: flex;
  gap: 16px;
  font-size: 0.85rem;
}

.distance, .duration {
  padding: 4px 8px;
  background: #e2e8f0;
  border-radius: 6px;
  color: #475569;
  font-weight: 500;
}

.timeline-item.active .distance,
.timeline-item.active .duration {
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

@keyframes float {
  0%, 100% { transform: translateY(0px) rotate(0deg); }
  50% { transform: translateY(-10px) rotate(2deg); }
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@media (max-width: 768px) {
  .style-options {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .route-canvas-container {
    padding: 16px;
  }
  
  .timeline-item {
    flex-direction: column;
    text-align: center;
  }
  
  .timeline-item:hover,
  .timeline-item.active {
    transform: none;
  }
}
</style>