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
  
  // 绘制主要内容
  drawBackground(ctx, styleConfig)
  drawRoutePath(ctx, styleConfig)
  drawLocationMarkers(ctx, styleConfig)
  
  // 添加图例和信息面板 - 模仿参考图片的信息展示
  const drawLegend = () => {
    const legendX = 20
    const legendY = canvasHeight.value - 150
    const legendWidth = 200
    const legendHeight = 120
    
    // 图例背景
    ctx.fillStyle = 'rgba(255, 255, 255, 0.95)'
    ctx.strokeStyle = '#2E86C1'
    ctx.lineWidth = 2
    ctx.beginPath()
    ctx.roundRect(legendX, legendY, legendWidth, legendHeight, 10)
    ctx.fill()
    ctx.stroke()
    
    // 图例标题
    ctx.fillStyle = '#2E86C1'
    ctx.font = 'bold 16px Arial'
    ctx.textAlign = 'left'
    ctx.fillText('图例', legendX + 15, legendY + 25)
    
    // 路线说明
    let itemY = legendY + 45
    
    // 起点标识
    ctx.fillStyle = '#E74C3C'
    ctx.beginPath()
    ctx.arc(legendX + 25, itemY, 8, 0, 2 * Math.PI)
    ctx.fill()
    ctx.fillStyle = '#FFFFFF'
    ctx.font = 'bold 12px Arial'
    ctx.textAlign = 'center'
    ctx.fillText('A', legendX + 25, itemY + 3)
    
    ctx.fillStyle = '#333333'
    ctx.font = '12px Arial'
    ctx.textAlign = 'left'
    ctx.fillText('起点', legendX + 45, itemY + 4)
    
    // 终点标识
    itemY += 20
    ctx.fillStyle = '#27AE60'
    ctx.beginPath()
    ctx.arc(legendX + 25, itemY, 8, 0, 2 * Math.PI)
    ctx.fill()
    ctx.fillStyle = '#FFFFFF'
    ctx.font = 'bold 12px Arial'
    ctx.textAlign = 'center'
    ctx.fillText('B', legendX + 25, itemY + 3)
    
    ctx.fillStyle = '#333333'
    ctx.font = '12px Arial'
    ctx.textAlign = 'left'
    ctx.fillText('终点', legendX + 45, itemY + 4)
    
    // 路线标识
    itemY += 20
    ctx.strokeStyle = '#2E86C1'
    ctx.lineWidth = 4
    ctx.beginPath()
    ctx.moveTo(legendX + 15, itemY)
    ctx.lineTo(legendX + 35, itemY)
    ctx.stroke()
    
    ctx.fillStyle = '#333333'
    ctx.font = '12px Arial'
    ctx.textAlign = 'left'
    ctx.fillText('旅游路线', legendX + 45, itemY + 4)
  }
  
  // 添加统计信息面板
  const drawStatsPanel = () => {
    const panelX = canvasWidth.value - 220
    const panelY = canvasHeight.value - 120
    const panelWidth = 200
    const panelHeight = 100
    
    // 统计面板背景
    ctx.fillStyle = 'rgba(255, 255, 255, 0.95)'
    ctx.strokeStyle = '#2E86C1'
    ctx.lineWidth = 2
    ctx.beginPath()
    ctx.roundRect(panelX, panelY, panelWidth, panelHeight, 10)
    ctx.fill()
    ctx.stroke()
    
    // 统计标题
    ctx.fillStyle = '#2E86C1'
    ctx.font = 'bold 16px Arial'
    ctx.textAlign = 'left'
    ctx.fillText('路线统计', panelX + 15, panelY + 25)
    
    // 统计信息
    ctx.fillStyle = '#333333'
    ctx.font = '12px Arial'
    ctx.fillText(`总站点: ${props.locations.length}`, panelX + 15, panelY + 45)
    
    // 计算总距离（简化计算）
    let totalDistance = 0
    for (let i = 0; i < props.locations.length - 1; i++) {
      const start = coordinateToCanvas(props.locations[i].coordinates.longitude, props.locations[i].coordinates.latitude)
      const end = coordinateToCanvas(props.locations[i + 1].coordinates.longitude, props.locations[i + 1].coordinates.latitude)
      totalDistance += Math.sqrt(Math.pow(end.x - start.x, 2) + Math.pow(end.y - start.y, 2)) * 0.1
    }
    
    ctx.fillText(`预估距离: ${totalDistance.toFixed(0)}km`, panelX + 15, panelY + 65)
    ctx.fillText(`生成时间: ${new Date().toLocaleDateString()}`, panelX + 15, panelY + 85)
  }
  
  // 绘制图例和统计面板
  drawLegend()
  drawStatsPanel()
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
  // 绘制专业地图背景 - 模仿参考图片的浅色地理背景
  const gradient = ctx.createLinearGradient(0, 0, canvasWidth.value, canvasHeight.value)
  gradient.addColorStop(0, '#F8F9FA')    // 浅灰白色
  gradient.addColorStop(0.5, '#E9ECEF')  // 中性灰色
  gradient.addColorStop(1, '#DEE2E6')    // 稍深灰色
  
  ctx.fillStyle = gradient
  ctx.fillRect(0, 0, canvasWidth.value, canvasHeight.value)
  
  // 添加地理网格线 - 模仿专业地图的网格效果
  ctx.strokeStyle = 'rgba(108, 117, 125, 0.1)'
  ctx.lineWidth = 1
  ctx.setLineDash([5, 5])
  
  const gridSize = 50
  
  // 绘制垂直网格线
  for (let x = 0; x < canvasWidth.value; x += gridSize) {
    ctx.beginPath()
    ctx.moveTo(x, 0)
    ctx.lineTo(x, canvasHeight.value)
    ctx.stroke()
  }
  
  // 绘制水平网格线
  for (let y = 0; y < canvasHeight.value; y += gridSize) {
    ctx.beginPath()
    ctx.moveTo(0, y)
    ctx.lineTo(canvasWidth.value, y)
    ctx.stroke()
  }
  
  // 重置线条样式
  ctx.setLineDash([])
  
  // 添加标题区域背景
  const titleHeight = 80
  const titleGradient = ctx.createLinearGradient(0, 0, 0, titleHeight)
  titleGradient.addColorStop(0, 'rgba(46, 134, 193, 0.9)')
  titleGradient.addColorStop(1, 'rgba(46, 134, 193, 0.7)')
  
  ctx.fillStyle = titleGradient
  ctx.fillRect(0, 0, canvasWidth.value, titleHeight)
  
  // 绘制标题
  ctx.fillStyle = '#FFFFFF'
  ctx.font = 'bold 24px Arial'
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  ctx.fillText('旅游路线图', canvasWidth.value / 2, titleHeight / 2)
  
  // 添加指北针
  const compassSize = 40
  const compassX = canvasWidth.value - compassSize - 20
  const compassY = titleHeight + 30
  
  // 指北针背景圆
  ctx.fillStyle = 'rgba(255, 255, 255, 0.9)'
  ctx.strokeStyle = '#2E86C1'
  ctx.lineWidth = 2
  ctx.beginPath()
  ctx.arc(compassX, compassY, compassSize / 2, 0, 2 * Math.PI)
  ctx.fill()
  ctx.stroke()
  
  // 指北针箭头
  ctx.fillStyle = '#E74C3C'
  ctx.beginPath()
  ctx.moveTo(compassX, compassY - compassSize / 2 + 5)
  ctx.lineTo(compassX - 8, compassY + 5)
  ctx.lineTo(compassX + 8, compassY + 5)
  ctx.closePath()
  ctx.fill()
  
  // 指北针文字
  ctx.fillStyle = '#2E86C1'
  ctx.font = 'bold 12px Arial'
  ctx.textAlign = 'center'
  ctx.fillText('N', compassX, compassY - compassSize / 2 - 10)
}

function drawRoutePath(ctx: CanvasRenderingContext2D, config: any) {
  // 绘制路线 - 模仿参考图片的蓝色专业风格
  if (props.locations.length < 2) return
  
  // 主路线 - 使用蓝色粗线条
  ctx.strokeStyle = '#2E86C1'  // 专业蓝色
  ctx.lineWidth = 6
  ctx.lineCap = 'round'
  ctx.lineJoin = 'round'
  
  // 绘制路线阴影效果
  ctx.shadowColor = 'rgba(46, 134, 193, 0.3)'
  ctx.shadowBlur = 8
  ctx.shadowOffsetX = 2
  ctx.shadowOffsetY = 2
  
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
  
  // 清除阴影
  ctx.shadowColor = 'transparent'
  ctx.shadowBlur = 0
  ctx.shadowOffsetX = 0
  ctx.shadowOffsetY = 0
  
  // 绘制路线段标识
  for (let i = 0; i < props.locations.length - 1; i++) {
    const start = coordinateToCanvas(props.locations[i].coordinates.longitude, props.locations[i].coordinates.latitude)
    const end = coordinateToCanvas(props.locations[i + 1].coordinates.longitude, props.locations[i + 1].coordinates.latitude)
    const midX = (start.x + end.x) / 2
    const midY = (start.y + end.y) / 2
    
    // 计算距离（简化计算）
    const distance = Math.sqrt(Math.pow(end.x - start.x, 2) + Math.pow(end.y - start.y, 2)) * 0.1
    
    // 绘制距离标签背景
    ctx.fillStyle = 'rgba(255, 255, 255, 0.9)'
    ctx.strokeStyle = '#2E86C1'
    ctx.lineWidth = 1
    const text = `${distance.toFixed(0)}km`
    const textWidth = ctx.measureText(text).width
    const padding = 8
    
    ctx.fillRect(midX - textWidth/2 - padding, midY - 12, textWidth + padding*2, 20)
    ctx.strokeRect(midX - textWidth/2 - padding, midY - 12, textWidth + padding*2, 20)
    
    // 绘制距离文字
    ctx.fillStyle = '#2E86C1'
    ctx.font = 'bold 12px Arial'
    ctx.textAlign = 'center'
    ctx.fillText(text, midX, midY + 3)
  }
}

function drawLocationMarkers(ctx: CanvasRenderingContext2D, config: any) {
  props.locations.forEach((location, index) => {
    const { x, y } = coordinateToCanvas(location.coordinates.longitude, location.coordinates.latitude)
    const isActive = index === activeLocationIndex.value
    
    // 绘制地点标记 - 模仿参考图片的专业样式
    const isStart = index === 0
    const isEnd = index === props.locations.length - 1
    
    // 标记圆圈
    ctx.fillStyle = isStart ? '#E74C3C' : isEnd ? '#27AE60' : '#2E86C1'  // 起点红色，终点绿色，中间蓝色
    ctx.strokeStyle = '#FFFFFF'
    ctx.lineWidth = 3
    
    // 绘制外圈阴影
    ctx.shadowColor = 'rgba(0, 0, 0, 0.3)'
    ctx.shadowBlur = 6
    ctx.shadowOffsetX = 2
    ctx.shadowOffsetY = 2
    
    ctx.beginPath()
    ctx.arc(x, y, 12, 0, 2 * Math.PI)
    ctx.fill()
    ctx.stroke()
    
    // 清除阴影
    ctx.shadowColor = 'transparent'
    ctx.shadowBlur = 0
    ctx.shadowOffsetX = 0
    ctx.shadowOffsetY = 0
    
    // 绘制标记字母
    ctx.fillStyle = '#FFFFFF'
    ctx.font = 'bold 14px Arial'
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    const label = isStart ? 'A' : isEnd ? 'B' : String.fromCharCode(65 + index)
    ctx.fillText(label, x, y)
    
    // 绘制地点名称标签 - 专业样式
    const labelY = y - 25
    const labelText = location.name
    ctx.font = 'bold 13px Arial'
    const textWidth = ctx.measureText(labelText).width
    const padding = 10
    
    // 标签背景
    ctx.fillStyle = 'rgba(255, 255, 255, 0.95)'
    ctx.strokeStyle = isStart ? '#E74C3C' : isEnd ? '#27AE60' : '#2E86C1'
    ctx.lineWidth = 2
    
    const rectX = x - textWidth/2 - padding
    const rectY = labelY - 10
    const rectWidth = textWidth + padding * 2
    const rectHeight = 20
    
    // 绘制圆角矩形背景
    ctx.beginPath()
    ctx.roundRect(rectX, rectY, rectWidth, rectHeight, 8)
    ctx.fill()
    ctx.stroke()
    
    // 绘制地点名称
    ctx.fillStyle = isStart ? '#E74C3C' : isEnd ? '#27AE60' : '#2E86C1'
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    ctx.fillText(labelText, x, labelY)
    
    // 绘制连接线
    ctx.strokeStyle = isStart ? '#E74C3C' : isEnd ? '#27AE60' : '#2E86C1'
    ctx.lineWidth = 2
    ctx.beginPath()
    ctx.moveTo(x, y + 12)
    ctx.lineTo(x, labelY + 10)
    ctx.stroke()
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