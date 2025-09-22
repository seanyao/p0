<template>
  <div id="app">
    <header class="app-header">
      <h1>🤖 AI地理可视化工具</h1>
      <p>输入地名，AI智能生成精美的地理坐标图表</p>
    </header>

    <main class="app-main">
      <!-- 简化的输入区域 -->
      <div class="input-section">
        <LocationParser
          :placeholder="'输入地名，如：北京、上海、深圳、广州'"
          :show-history="false"
          :show-batch-mode="true"
          @location-parsed="handleLocationParsed"
          @error="handleError"
        />
      </div>

      <!-- AI处理状态 -->
      <div v-if="isProcessing" class="ai-processing">
        <div class="processing-animation">🤖</div>
        <p>AI正在智能解析地理坐标...</p>
      </div>

      <!-- 可视化输出区域 -->
      <div v-if="locations.length > 0 && !isProcessing" class="output-section">
        <h2>📊 AI生成的地理坐标可视化</h2>
        
        <!-- 坐标数据展示 -->
        <div class="coordinates-display">
          <h3>解析的坐标数据</h3>
          <div class="coordinate-grid">
            <div 
              v-for="(location, index) in locations" 
              :key="index"
              class="coordinate-item"
            >
              <div class="location-name">{{ location.name }}</div>
              <div class="coordinates">
                <span class="coord-label">经度:</span> {{ parseFloat(location.longitude).toFixed(6) }}°
                <br>
                <span class="coord-label">纬度:</span> {{ parseFloat(location.latitude).toFixed(6) }}°
              </div>
            </div>
          </div>
        </div>

        <!-- 可视化图表 -->
        <VisualRenderer 
          :locations="locations"
          :routes="routes"
        />
      </div>
    </main>

    <footer class="app-footer">
      <p>
        🤖 AI驱动 · 智能地名解析 · 精确坐标可视化 · 
        <span class="tech-stack">Vue3 + TypeScript + 高德API</span>
      </p>
    </footer>
  </div>
</template>

<script setup lang="ts">
/**
 * AI地理可视化工具 - 主应用组件
 */

import { ref } from 'vue'
import LocationParser from './components/LocationParser.vue'
import VisualRenderer from './components/VisualRenderer.vue'

// 响应式数据
const locations = ref<any[]>([])
const routes = ref<any[]>([])
const isProcessing = ref(false)

const handleLocationParsed = (result: any) => {
  console.log('AI地名解析结果:', result)
  
  // 显示AI处理状态
  isProcessing.value = true
  
  // 模拟AI处理时间
  setTimeout(() => {
    // 如果是单个地点解析结果
    if (result.success && result.location) {
      const location = {
        name: result.location.name,
        longitude: result.location.coordinates.longitude,
        latitude: result.location.coordinates.latitude,
        formatted_address: result.location.address
      }
      locations.value.push(location)
    }
    
    // 如果是批量解析结果
    if (result.summary && result.results) {
      const successfulResults = result.results.filter((item: any) => item.success && item.location)
      successfulResults.forEach((item: any) => {
        const location = {
          name: item.location.name,
          longitude: item.location.coordinates.longitude,
          latitude: item.location.coordinates.latitude,
          formatted_address: item.location.address
        }
        locations.value.push(location)
      })
    }
    
    // 生成路线（如果有多个地点）
    if (locations.value.length > 1) {
      generateRoutes()
    }
    
    // 完成AI处理
    isProcessing.value = false
  }, 1500) // 1.5秒的AI处理动画
}

const handleError = (error: string) => {
  console.error('AI解析错误:', error)
  isProcessing.value = false
}

const generateRoutes = () => {
  // 智能路线生成：连接相邻的地点
  const newRoutes = []
  for (let i = 0; i < locations.value.length - 1; i++) {
    newRoutes.push({
      from: locations.value[i],
      to: locations.value[i + 1],
      id: `route-${i}`
    })
  }
  routes.value = newRoutes
}
</script>

<style scoped>
.app-header {
  text-align: center;
  padding: 3rem 1rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  margin-bottom: 2rem;
}

.app-header h1 {
  margin: 0 0 0.5rem 0;
  font-size: 2.8rem;
  font-weight: 700;
  text-shadow: 0 2px 4px rgba(0,0,0,0.3);
}

.app-header p {
  margin: 0;
  font-size: 1.2rem;
  opacity: 0.9;
}

.app-main {
  max-width: 1000px;
  margin: 0 auto;
  padding: 0 1rem;
}

.input-section {
  margin-bottom: 2rem;
}

.ai-processing {
  text-align: center;
  padding: 3rem 1rem;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  border-radius: 12px;
  color: white;
  margin: 2rem 0;
}

.processing-animation {
  font-size: 4rem;
  animation: bounce 1s infinite;
  margin-bottom: 1rem;
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-10px);
  }
  60% {
    transform: translateY(-5px);
  }
}

.ai-processing p {
  font-size: 1.3rem;
  margin: 0;
  font-weight: 500;
}

.output-section {
  margin-top: 3rem;
}

.output-section h2 {
  color: #333;
  font-size: 2rem;
  margin-bottom: 2rem;
  text-align: center;
}

.coordinates-display {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 2rem;
  margin-bottom: 2rem;
}

.coordinates-display h3 {
  color: #495057;
  margin-bottom: 1.5rem;
  font-size: 1.4rem;
}

.coordinate-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1rem;
}

.coordinate-item {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  border-left: 4px solid #667eea;
}

.location-name {
  font-size: 1.2rem;
  font-weight: 600;
  color: #333;
  margin-bottom: 0.8rem;
}

.coordinates {
  font-family: 'Monaco', 'Menlo', monospace;
  font-size: 0.95rem;
  color: #666;
  line-height: 1.6;
}

.coord-label {
  font-weight: 600;
  color: #495057;
}

.app-footer {
  text-align: center;
  padding: 2rem 1rem;
  margin-top: 4rem;
  border-top: 1px solid #e0e0e0;
  color: #666;
}

.tech-stack {
  color: #667eea;
  font-weight: 500;
}
</style>