<template>
  <div class="test-route-page">
    <div class="header">
      <h1>🎨 艺术化路线图测试</h1>
      <p>真实旅游路线案例：天津-内蒙古-北京-济南-上海</p>
    </div>
    
    <div class="route-info">
      <h3>📅 行程安排</h3>
      <div class="timeline">
        <div v-for="(item, index) in routeData" :key="index" class="timeline-item">
          <div class="date">{{ item.date }}</div>
          <div class="location">{{ item.location }}</div>
        </div>
      </div>
    </div>
    
    <div class="controls">
      <button @click="generateRoute" class="generate-btn" :disabled="loading">
        {{ loading ? '生成中...' : '🎨 生成艺术路线图' }}
      </button>
      <button @click="exportPNG" class="export-btn" :disabled="!locations.length">
        📸 导出PNG图片
      </button>
    </div>
    
    <div v-if="locations.length" class="renderer-container">
      <VisualRenderer 
        ref="rendererRef"
        :locations="locations" 
        :show-export="false"
      />
    </div>
    
    <div v-if="error" class="error-message">
      ❌ {{ error }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import VisualRenderer from '@/components/VisualRenderer.vue'
import type { LocationInfo } from '@/types/location'

// 真实旅游路线数据
const routeData = [
  { date: '2025.9.27', location: '天津' },
  { date: '2025.9.28', location: '赤峰' },
  { date: '2025.9.29', location: '巴林右旗' },
  { date: '2025.9.30', location: '巴彦查干苏木' },
  { date: '2025.10.1', location: '经棚镇' },
  { date: '2025.10.2', location: '多伦县' },
  { date: '2025.10.3', location: '多伦县' },
  { date: '2025.10.4', location: '狮子沟乡' },
  { date: '2025.10.5', location: '北京' },
  { date: '2025.10.6', location: '北京' },
  { date: '2025.10.7', location: '济南' },
  { date: '2025.10.8', location: '上海' }
]

const locations = ref<LocationInfo[]>([])
const loading = ref(false)
const error = ref('')
const rendererRef = ref()

// 模拟地理编码服务
const geocodeLocation = async (locationName: string): Promise<LocationInfo | null> => {
  // 预设的坐标数据（实际应用中应该调用地理编码API）
  const coordinates: Record<string, [number, number]> = {
    '天津': [117.2008, 39.0842],
    '赤峰': [118.8869, 42.2574],
    '巴林右旗': [118.6644, 43.5342],
    '巴彦查干苏木': [116.8500, 43.2000],
    '经棚镇': [116.6447, 43.3497],
    '多伦县': [116.4775, 42.2033],
    '狮子沟乡': [116.2000, 41.8000],
    '北京': [116.4074, 39.9042],
    '济南': [117.0009, 36.6758],
    '上海': [121.4737, 31.2304]
  }
  
  const coords = coordinates[locationName]
  if (!coords) {
    return null
  }
  
  return {
    name: locationName,
    coordinates: {
      longitude: coords[0],
      latitude: coords[1]
    },
    address: locationName
  }
}

// 生成路线
const generateRoute = async () => {
  loading.value = true
  error.value = ''
  locations.value = []
  
  try {
    const locationPromises = routeData.map(item => geocodeLocation(item.location))
    const results = await Promise.all(locationPromises)
    
    const validLocations = results.filter(loc => loc !== null) as LocationInfo[]
    
    if (validLocations.length === 0) {
      throw new Error('无法解析任何地点坐标')
    }
    
    locations.value = validLocations
    
    // 等待渲染完成
    await new Promise(resolve => setTimeout(resolve, 1000))
    
  } catch (err) {
    error.value = err instanceof Error ? err.message : '生成路线时发生错误'
  } finally {
    loading.value = false
  }
}

// 导出PNG
const exportPNG = async () => {
  if (!rendererRef.value) {
    error.value = '渲染器未准备就绪'
    return
  }
  
  try {
    await rendererRef.value.exportToPNG()
  } catch (err) {
    error.value = err instanceof Error ? err.message : '导出PNG时发生错误'
  }
}

// 自动生成路线
generateRoute()
</script>

<style scoped>
.test-route-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.header {
  text-align: center;
  margin-bottom: 30px;
}

.header h1 {
  color: #2c3e50;
  margin-bottom: 10px;
  font-size: 2.5em;
}

.header p {
  color: #7f8c8d;
  font-size: 1.2em;
}

.route-info {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 30px;
}

.route-info h3 {
  color: #2c3e50;
  margin-bottom: 15px;
}

.timeline {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.timeline-item {
  background: white;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border-left: 4px solid #3498db;
}

.date {
  font-weight: bold;
  color: #3498db;
  font-size: 0.9em;
  margin-bottom: 5px;
}

.location {
  color: #2c3e50;
  font-size: 1.1em;
}

.controls {
  display: flex;
  gap: 15px;
  justify-content: center;
  margin-bottom: 30px;
}

.generate-btn, .export-btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 1.1em;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.generate-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.generate-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
}

.export-btn {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
}

.export-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(245, 87, 108, 0.4);
}

.generate-btn:disabled, .export-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.renderer-container {
  margin-top: 30px;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.error-message {
  background: #fee;
  color: #c33;
  padding: 15px;
  border-radius: 8px;
  margin-top: 20px;
  text-align: center;
  border: 1px solid #fcc;
}
</style>