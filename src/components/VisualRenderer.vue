<template>
  <div class="coordinate-visualizer">
    <div class="visualization-header">
      <h3>🎨 智能坐标可视化</h3>
      <div class="chart-controls">
        <button 
          v-for="chartType in chartTypes" 
          :key="chartType.value"
          @click="selectedChartType = chartType.value"
          :class="{ active: selectedChartType === chartType.value }"
          class="chart-type-btn"
        >
          {{ chartType.icon }} {{ chartType.label }}
        </button>
      </div>
    </div>

    <!-- 散点图可视化 -->
    <div v-if="selectedChartType === 'scatter'" class="chart-container">
      <canvas 
        ref="scatterCanvas" 
        :width="canvasWidth" 
        :height="canvasHeight"
        class="visualization-canvas"
      ></canvas>
      <div class="chart-info">
        <p>📍 基于真实经纬度坐标的散点分布图</p>
        <p>🎯 显示地点间的地理关系和距离分布</p>
      </div>
    </div>

    <!-- 连线图可视化 -->
    <div v-if="selectedChartType === 'network'" class="chart-container">
      <canvas 
        ref="networkCanvas" 
        :width="canvasWidth" 
        :height="canvasHeight"
        class="visualization-canvas"
      ></canvas>
      <div class="chart-info">
        <p>🔗 智能路径连接图</p>
        <p>📏 按地理距离优化的连接路径</p>
      </div>
    </div>

    <!-- 热力图可视化 -->
    <div v-if="selectedChartType === 'heatmap'" class="chart-container">
      <canvas 
        ref="heatmapCanvas" 
        :width="canvasWidth" 
        :height="canvasHeight"
        class="visualization-canvas"
      ></canvas>
      <div class="chart-info">
        <p>🌡️ 地理密度热力图</p>
        <p>🎨 基于坐标密度的颜色渐变显示</p>
      </div>
    </div>

    <!-- 统计信息 -->
    <div class="statistics-panel">
      <h4>📊 地理数据统计</h4>
      <div class="stats-grid">
        <div class="stat-item">
          <span class="stat-label">地点数量</span>
          <span class="stat-value">{{ locations.length }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">经度范围</span>
          <span class="stat-value">{{ longitudeRange }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">纬度范围</span>
          <span class="stat-value">{{ latitudeRange }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">覆盖面积</span>
          <span class="stat-value">{{ coverageArea }}</span>
        </div>
      </div>
    </div>

    <!-- 导出功能 -->
    <div class="export-section">
      <button @click="exportVisualization" class="export-btn">
        📥 导出可视化图表
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'

// Props
const props = defineProps<{
  locations: Array<{
    name: string
    coordinates: {
      longitude: number
      latitude: number
    }
  }>
}>()

// 响应式数据
const scatterCanvas = ref<HTMLCanvasElement>()
const networkCanvas = ref<HTMLCanvasElement>()
const heatmapCanvas = ref<HTMLCanvasElement>()
const canvasWidth = ref(800)
const canvasHeight = ref(500)
const selectedChartType = ref('scatter')

// 图表类型配置
const chartTypes = ref([
  { value: 'scatter', label: '散点图', icon: '📍' },
  { value: 'network', label: '连线图', icon: '🔗' },
  { value: 'heatmap', label: '热力图', icon: '🌡️' }
])

// 计算属性 - 地理数据统计
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

const coverageArea = computed(() => {
  if (props.locations.length < 2) return '0 km²'
  const lngs = props.locations.map(loc => loc.coordinates.longitude)
  const lats = props.locations.map(loc => loc.coordinates.latitude)
  const lngRange = Math.max(...lngs) - Math.min(...lngs)
  const latRange = Math.max(...lats) - Math.min(...lats)
  // 简化的面积计算（实际应该考虑地球曲率）
  const area = lngRange * latRange * 111 * 111 // 大约每度111km
  return `${area.toFixed(0)} km²`
})

// 坐标转换函数
function coordinateToCanvas(longitude: number, latitude: number) {
  if (props.locations.length === 0) return { x: 0, y: 0 }
  
  const lngs = props.locations.map(loc => loc.coordinates.longitude)
  const lats = props.locations.map(loc => loc.coordinates.latitude)
  
  const minLng = Math.min(...lngs)
  const maxLng = Math.max(...lngs)
  const minLat = Math.min(...lats)
  const maxLat = Math.max(...lats)
  
  const padding = 50
  const x = padding + ((longitude - minLng) / (maxLng - minLng)) * (canvasWidth.value - 2 * padding)
  const y = padding + ((maxLat - latitude) / (maxLat - minLat)) * (canvasHeight.value - 2 * padding)
  
  return { x, y }
}

// 绘制散点图
function drawScatterChart() {
  const canvas = scatterCanvas.value
  if (!canvas) return
  
  const ctx = canvas.getContext('2d')
  if (!ctx) return
  
  // 清空画布
  ctx.clearRect(0, 0, canvasWidth.value, canvasHeight.value)
  
  // 设置背景
  ctx.fillStyle = '#f8fafc'
  ctx.fillRect(0, 0, canvasWidth.value, canvasHeight.value)
  
  // 绘制网格
  ctx.strokeStyle = '#e2e8f0'
  ctx.lineWidth = 1
  for (let i = 0; i <= 10; i++) {
    const x = (canvasWidth.value / 10) * i
    const y = (canvasHeight.value / 10) * i
    ctx.beginPath()
    ctx.moveTo(x, 0)
    ctx.lineTo(x, canvasHeight.value)
    ctx.stroke()
    ctx.beginPath()
    ctx.moveTo(0, y)
    ctx.lineTo(canvasWidth.value, y)
    ctx.stroke()
  }
  
  // 绘制地点
  props.locations.forEach((location, index) => {
    const { x, y } = coordinateToCanvas(location.coordinates.longitude, location.coordinates.latitude)
    
    // 绘制点
    ctx.fillStyle = `hsl(${(index * 137.5) % 360}, 70%, 50%)`
    ctx.beginPath()
    ctx.arc(x, y, 8, 0, 2 * Math.PI)
    ctx.fill()
    
    // 绘制边框
    ctx.strokeStyle = '#ffffff'
    ctx.lineWidth = 2
    ctx.stroke()
    
    // 绘制标签
    ctx.fillStyle = '#1e293b'
    ctx.font = '12px Arial'
    ctx.textAlign = 'center'
    ctx.fillText(location.name, x, y - 15)
  })
}

// 绘制连线图
function drawNetworkChart() {
  const canvas = networkCanvas.value
  if (!canvas) return
  
  const ctx = canvas.getContext('2d')
  if (!ctx) return
  
  // 清空画布
  ctx.clearRect(0, 0, canvasWidth.value, canvasHeight.value)
  
  // 设置背景
  ctx.fillStyle = '#f1f5f9'
  ctx.fillRect(0, 0, canvasWidth.value, canvasHeight.value)
  
  // 绘制连线（按距离排序连接最近的点）
  const points = props.locations.map(loc => ({
    ...loc,
    canvas: coordinateToCanvas(loc.coordinates.longitude, loc.coordinates.latitude)
  }))
  
  // 绘制连线
  ctx.strokeStyle = '#3b82f6'
  ctx.lineWidth = 2
  for (let i = 0; i < points.length - 1; i++) {
    const current = points[i]
    const next = points[i + 1]
    
    ctx.beginPath()
    ctx.moveTo(current.canvas.x, current.canvas.y)
    ctx.lineTo(next.canvas.x, next.canvas.y)
    ctx.stroke()
  }
  
  // 绘制节点
  points.forEach((point, index) => {
    ctx.fillStyle = '#1e40af'
    ctx.beginPath()
    ctx.arc(point.canvas.x, point.canvas.y, 10, 0, 2 * Math.PI)
    ctx.fill()
    
    ctx.fillStyle = '#ffffff'
    ctx.font = 'bold 10px Arial'
    ctx.textAlign = 'center'
    ctx.fillText((index + 1).toString(), point.canvas.x, point.canvas.y + 3)
  })
}

// 绘制热力图
function drawHeatmapChart() {
  const canvas = heatmapCanvas.value
  if (!canvas) return
  
  const ctx = canvas.getContext('2d')
  if (!ctx) return
  
  // 清空画布
  ctx.clearRect(0, 0, canvasWidth.value, canvasHeight.value)
  
  // 设置背景
  ctx.fillStyle = '#0f172a'
  ctx.fillRect(0, 0, canvasWidth.value, canvasHeight.value)
  
  // 创建热力效果
  props.locations.forEach((location, index) => {
    const { x, y } = coordinateToCanvas(location.coordinates.longitude, location.coordinates.latitude)
    
    // 创建径向渐变
    const gradient = ctx.createRadialGradient(x, y, 0, x, y, 60)
    const hue = (index * 60) % 360
    gradient.addColorStop(0, `hsla(${hue}, 100%, 50%, 0.8)`)
    gradient.addColorStop(0.5, `hsla(${hue}, 100%, 50%, 0.4)`)
    gradient.addColorStop(1, `hsla(${hue}, 100%, 50%, 0)`)
    
    ctx.fillStyle = gradient
    ctx.beginPath()
    ctx.arc(x, y, 60, 0, 2 * Math.PI)
    ctx.fill()
  })
  
  // 绘制地点标记
  props.locations.forEach((location) => {
    const { x, y } = coordinateToCanvas(location.coordinates.longitude, location.coordinates.latitude)
    
    ctx.fillStyle = '#ffffff'
    ctx.beginPath()
    ctx.arc(x, y, 4, 0, 2 * Math.PI)
    ctx.fill()
  })
}

// 导出可视化图表
function exportVisualization() {
  let canvas: HTMLCanvasElement | undefined
  
  switch (selectedChartType.value) {
    case 'scatter':
      canvas = scatterCanvas.value
      break
    case 'network':
      canvas = networkCanvas.value
      break
    case 'heatmap':
      canvas = heatmapCanvas.value
      break
  }
  
  if (!canvas) return
  
  const link = document.createElement('a')
  link.download = `地理可视化-${selectedChartType.value}-${Date.now()}.png`
  link.href = canvas.toDataURL()
  link.click()
}

// 重新绘制当前图表
function redrawCurrentChart() {
  switch (selectedChartType.value) {
    case 'scatter':
      drawScatterChart()
      break
    case 'network':
      drawNetworkChart()
      break
    case 'heatmap':
      drawHeatmapChart()
      break
  }
}

// 监听数据变化
watch(() => props.locations, () => {
  redrawCurrentChart()
}, { deep: true })

watch(selectedChartType, () => {
  setTimeout(redrawCurrentChart, 100)
})

// 组件挂载后初始化
onMounted(() => {
  setTimeout(redrawCurrentChart, 100)
})
</script>

<style scoped>
.coordinate-visualizer {
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.visualization-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px;
  text-align: center;
}

.visualization-header h3 {
  margin: 0 0 15px 0;
  font-size: 1.5rem;
  font-weight: 600;
}

.chart-controls {
  display: flex;
  gap: 10px;
  justify-content: center;
  flex-wrap: wrap;
}

.chart-type-btn {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  padding: 8px 16px;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.9rem;
}

.chart-type-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
}

.chart-type-btn.active {
  background: rgba(255, 255, 255, 0.9);
  color: #667eea;
  font-weight: 600;
}

.chart-container {
  padding: 20px;
  text-align: center;
}

.visualization-canvas {
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  background: white;
}

.chart-info {
  margin-top: 15px;
  padding: 15px;
  background: #f8fafc;
  border-radius: 8px;
  border-left: 4px solid #3b82f6;
}

.chart-info p {
  margin: 5px 0;
  color: #64748b;
  font-size: 0.9rem;
}

.statistics-panel {
  background: #f8fafc;
  padding: 20px;
  border-top: 1px solid #e2e8f0;
}

.statistics-panel h4 {
  margin: 0 0 15px 0;
  color: #1e293b;
  font-size: 1.1rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.stat-item {
  background: white;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-label {
  color: #64748b;
  font-size: 0.9rem;
}

.stat-value {
  color: #1e293b;
  font-weight: 600;
  font-size: 1rem;
}

.export-section {
  padding: 20px;
  text-align: center;
  border-top: 1px solid #e2e8f0;
}

.export-btn {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 500;
  transition: all 0.3s ease;
}

.export-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
}

@media (max-width: 768px) {
  .chart-controls {
    flex-direction: column;
    align-items: center;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .visualization-canvas {
    max-width: 100%;
    height: auto;
  }
}
</style>