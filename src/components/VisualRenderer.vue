<template>
  <div class="visual-renderer">
    <div class="renderer-controls">
      <div class="control-group">
        <label>颜色方案:</label>
        <select v-model="selectedColorScheme" @change="updateStyle">
          <option value="default">默认</option>
          <option value="dark">深色</option>
          <option value="vibrant">鲜艳</option>
          <option value="pastel">柔和</option>
        </select>
      </div>
      
      <div class="control-group">
        <label>线条宽度:</label>
        <input 
          type="range" 
          v-model="lineWidth" 
          min="1" 
          max="10" 
          @input="updateStyle"
        />
        <span>{{ lineWidth }}px</span>
      </div>
      
      <div class="control-group">
        <label>字体大小:</label>
        <input 
          type="range" 
          v-model="fontSize" 
          min="10" 
          max="24" 
          @input="updateStyle"
        />
        <span>{{ fontSize }}px</span>
      </div>
      
      <div class="control-group">
        <button @click="toggleOptimization" :class="{ active: optimizationEnabled }">
          {{ optimizationEnabled ? '关闭优化' : '启用优化' }}
        </button>
        <button @click="clearRenderer">清空画布</button>
        <button @click="exportCanvas">导出图片</button>
      </div>
    </div>
    
    <div class="canvas-container">
      <canvas 
        ref="canvas" 
        :width="canvasWidth" 
        :height="canvasHeight"
        @mousedown="handleMouseDown"
        @mousemove="handleMouseMove"
        @mouseup="handleMouseUp"
        @wheel="handleWheel"
      ></canvas>
      
      <div v-if="showPerformanceInfo" class="performance-info">
        <h4>性能信息</h4>
        <div class="metric">
          <span>帧率:</span>
          <span>{{ performanceMetrics.frameRate?.toFixed(1) || 0 }} FPS</span>
        </div>
        <div class="metric">
          <span>渲染时间:</span>
          <span>{{ performanceMetrics.renderTime?.toFixed(2) || 0 }} ms</span>
        </div>
        <div class="metric">
          <span>内存使用:</span>
          <span>{{ performanceMetrics.memoryUsage?.toFixed(1) || 0 }} MB</span>
        </div>
        <div class="recommendations" v-if="recommendations.length > 0">
          <h5>优化建议:</h5>
          <ul>
            <li v-for="rec in recommendations" :key="rec">{{ rec }}</li>
          </ul>
        </div>
      </div>
    </div>
    
    <div class="status-bar">
      <span>画布尺寸: {{ canvasWidth }} × {{ canvasHeight }}</span>
      <span>缩放: {{ (zoomLevel * 100).toFixed(0) }}%</span>
      <span>元素数量: {{ elementCount }}</span>
      <button @click="showPerformanceInfo = !showPerformanceInfo">
        {{ showPerformanceInfo ? '隐藏' : '显示' }}性能信息
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { visualRenderer } from '../services/visualRenderer'
import { styleManager } from '../services/styleManager'
import { RouteData, StyleConfig } from '../types/visual'

// 响应式数据
const canvas = ref<HTMLCanvasElement>()
const selectedColorScheme = ref('default')
const lineWidth = ref(3)
const fontSize = ref(14)
const optimizationEnabled = ref(true)
const showPerformanceInfo = ref(false)
const canvasWidth = ref(800)
const canvasHeight = ref(600)
const zoomLevel = ref(1.0)
const elementCount = ref(0)

// 性能数据
const performanceMetrics = ref({
  frameRate: 0,
  renderTime: 0,
  memoryUsage: 0
})
const recommendations = ref<string[]>([])

// 交互状态
const isDragging = ref(false)
const lastMousePos = ref({ x: 0, y: 0 })
const panOffset = ref({ x: 0, y: 0 })

// 定时器
let performanceTimer: number | null = null

// 组件挂载
onMounted(async () => {
  await nextTick()
  if (canvas.value) {
    initRenderer()
    startPerformanceMonitoring()
    
    // 渲染示例数据
    renderSampleRoute()
  }
})

// 组件卸载
onUnmounted(() => {
  if (performanceTimer) {
    clearInterval(performanceTimer)
  }
})

// 初始化渲染器
function initRenderer() {
  if (!canvas.value) return
  
  try {
    visualRenderer.initCanvas(canvas.value)
    
    // 设置优化选项
    if (optimizationEnabled.value) {
      visualRenderer.setOptimizationOptions({
        enableLOD: true,
        maxPoints: 1000,
        simplificationTolerance: 2.0,
        enableCaching: true,
        batchSize: 50
      })
    }
  } catch (error) {
    console.error('Failed to initialize renderer:', error)
  }
}

// 更新样式
function updateStyle() {
  const style: StyleConfig = {
    colorScheme: selectedColorScheme.value as any,
    lineWidth: lineWidth.value,
    fontSize: fontSize.value
  }
  
  // 重新渲染
  renderSampleRoute()
}

// 切换优化
function toggleOptimization() {
  optimizationEnabled.value = !optimizationEnabled.value
  
  if (optimizationEnabled.value) {
    visualRenderer.autoOptimize()
  } else {
    visualRenderer.setOptimizationOptions({
      enableLOD: false,
      enableCaching: false
    })
  }
  
  renderSampleRoute()
}

// 清空渲染器
function clearRenderer() {
  visualRenderer.clearCanvas()
  visualRenderer.clearCache()
  elementCount.value = 0
}

// 导出画布
function exportCanvas() {
  if (!canvas.value) return
  
  const link = document.createElement('a')
  link.download = `route-map-${Date.now()}.png`
  link.href = canvas.value.toDataURL()
  link.click()
}

// 渲染示例路线
async function renderSampleRoute() {
  if (!canvas.value) return
  
  // 创建示例路线数据
  const sampleRoute: RouteData = {
    locations: [
      {
        name: '北京',
        coordinates: { lat: 39.9042, lng: 116.4074 },
        address: '北京市',
        type: 'city'
      },
      {
        name: '上海',
        coordinates: { lat: 31.2304, lng: 121.4737 },
        address: '上海市',
        type: 'city'
      },
      {
        name: '广州',
        coordinates: { lat: 23.1291, lng: 113.2644 },
        address: '广州市',
        type: 'city'
      }
    ],
    path: [
      { x: 1.164, y: 0.399 },
      { x: 1.200, y: 0.350 },
      { x: 1.247, y: 0.312 },
      { x: 1.136, y: 0.231 }
    ],
    bounds: {
      north: 40,
      south: 23,
      east: 122,
      west: 113
    }
  }
  
  const style: StyleConfig = {
    colorScheme: selectedColorScheme.value as any,
    lineWidth: lineWidth.value,
    fontSize: fontSize.value
  }
  
  try {
    await visualRenderer.renderRouteMap(sampleRoute, style)
    elementCount.value = sampleRoute.locations.length + sampleRoute.path.length
  } catch (error) {
    console.error('Failed to render route:', error)
  }
}

// 开始性能监控
function startPerformanceMonitoring() {
  performanceTimer = setInterval(() => {
    const metrics = visualRenderer.getPerformanceMetrics()
    if (metrics) {
      performanceMetrics.value = metrics
      recommendations.value = visualRenderer.getPerformanceRecommendations()
    }
  }, 1000) as any
}

// 鼠标事件处理
function handleMouseDown(event: MouseEvent) {
  isDragging.value = true
  lastMousePos.value = { x: event.clientX, y: event.clientY }
}

function handleMouseMove(event: MouseEvent) {
  if (!isDragging.value) return
  
  const deltaX = event.clientX - lastMousePos.value.x
  const deltaY = event.clientY - lastMousePos.value.y
  
  panOffset.value.x += deltaX
  panOffset.value.y += deltaY
  
  lastMousePos.value = { x: event.clientX, y: event.clientY }
  
  // 重新渲染
  renderSampleRoute()
}

function handleMouseUp() {
  isDragging.value = false
}

function handleWheel(event: WheelEvent) {
  event.preventDefault()
  
  const zoomFactor = event.deltaY > 0 ? 0.9 : 1.1
  zoomLevel.value = Math.max(0.1, Math.min(5.0, zoomLevel.value * zoomFactor))
  
  // 重新渲染
  renderSampleRoute()
}
</script>

<style scoped>
.visual-renderer {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f5f5f5;
}

.renderer-controls {
  display: flex;
  gap: 20px;
  padding: 16px;
  background: white;
  border-bottom: 1px solid #e0e0e0;
  flex-wrap: wrap;
}

.control-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.control-group label {
  font-weight: 500;
  color: #333;
}

.control-group select,
.control-group input[type="range"] {
  padding: 4px 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.control-group button {
  padding: 8px 16px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
  cursor: pointer;
  transition: all 0.2s;
}

.control-group button:hover {
  background: #f0f0f0;
}

.control-group button.active {
  background: #007bff;
  color: white;
  border-color: #007bff;
}

.canvas-container {
  flex: 1;
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #fafafa;
}

canvas {
  border: 1px solid #ddd;
  border-radius: 8px;
  background: white;
  cursor: grab;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

canvas:active {
  cursor: grabbing;
}

.performance-info {
  position: absolute;
  top: 16px;
  right: 16px;
  background: rgba(255, 255, 255, 0.95);
  padding: 16px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  min-width: 200px;
}

.performance-info h4 {
  margin: 0 0 12px 0;
  color: #333;
  font-size: 14px;
}

.metric {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 12px;
}

.recommendations {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #eee;
}

.recommendations h5 {
  margin: 0 0 8px 0;
  font-size: 12px;
  color: #666;
}

.recommendations ul {
  margin: 0;
  padding-left: 16px;
  font-size: 11px;
  color: #666;
}

.status-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 16px;
  background: #f8f9fa;
  border-top: 1px solid #e0e0e0;
  font-size: 12px;
  color: #666;
}

.status-bar button {
  padding: 4px 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
  cursor: pointer;
  font-size: 11px;
}

.status-bar button:hover {
  background: #f0f0f0;
}
</style>