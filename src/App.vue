<template>
  <div id="app">
    <router-view v-if="$route.path !== '/'" />
    <div v-else>
      <header class="app-header">
        <div class="header-content">
          <div class="logo-section">
            <div class="logo">✈️</div>
            <div class="title-section">
              <h1 class="main-title">AI旅行路线图生成器</h1>
              <p class="subtitle">一键生成Instagram级艺术化旅行路线图</p>
            </div>
          </div>
          <div class="header-actions">
            <button class="style-btn">🎨 风格</button>
            <button class="share-btn">📤 分享</button>
          </div>
        </div>
      </header>

      <main class="app-main">
        <!-- 输入区域 -->
        <section class="input-section">
          <div class="input-container">
            <h2 class="section-title">✨ 描述你的旅行</h2>
            <p class="section-desc">用自然语言描述你的旅行计划，AI会为你生成艺术化路线图</p>
            
            <div class="input-examples">
              <span class="example-tag" @click="setExample('我想去日本看樱花，从东京到京都到大阪')">🌸 日本樱花之旅</span>
              <span class="example-tag" @click="setExample('欧洲文艺复兴艺术之旅，巴黎-佛罗伦萨-罗马')">🎨 欧洲艺术之旅</span>
              <span class="example-tag" @click="setExample('中国古都文化游，北京-西安-洛阳')">🏛️ 中国古都游</span>
            </div>
            
            <LocationParser 
              @location-parsed="handleLocationParsed" 
              @error="handleError"
              :placeholder="'例如：我想去日本看樱花，从东京到京都...'"
            />
          </div>
        </section>

        <!-- 结果展示区域 -->
        <section class="results-section" v-if="locations.length > 0 || isProcessing">
          <!-- AI处理状态 -->
          <div v-if="isProcessing" class="ai-processing">
            <div class="processing-animation">
              <div class="processing-dots">
                <span></span><span></span><span></span>
              </div>
              <p>🎨 AI正在为你创作艺术化路线图...</p>
            </div>
          </div>

          <!-- 艺术化路线图展示 -->
          <div v-else class="route-canvas-container">
            <div class="canvas-header">
              <h3>🗺️ 你的专属旅行路线图</h3>
              <div class="canvas-actions">
                <select class="style-selector">
                  <option value="watercolor">🎨 水彩风格</option>
                  <option value="minimalist">✨ 极简风格</option>
                  <option value="vintage">📸 复古风格</option>
                  <option value="modern">🌟 现代风格</option>
                </select>
                <button class="export-btn">💾 导出</button>
                <button class="share-instagram">📱 分享到Instagram</button>
              </div>
            </div>
            
            <!-- 路线图画布 -->
            <div class="route-canvas">
              <VisualRenderer 
                :locations="locations" 
                :routes="routes"
                :style="selectedStyle"
              />
            </div>
            
            <!-- 路线信息卡片 -->
            <div class="route-info-cards">
              <div v-for="(location, index) in locations" :key="index" class="location-card">
                <div class="card-number">{{ index + 1 }}</div>
                <div class="card-content">
                  <h4>{{ location.name }}</h4>
                  <p class="coordinates">{{ location.latitude.toFixed(4) }}, {{ location.longitude.toFixed(4) }}</p>
                  <p class="address">{{ location.formatted_address }}</p>
                </div>
                <div class="card-actions">
                  <button class="view-on-map">🗺️</button>
                  <button class="add-note">📝</button>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>
      
      <!-- 添加测试路由链接 -->
      <div class="test-link" style="text-align: center; margin: 20px;">
        <router-link to="/test-route" class="test-btn">
          🧪 查看真实路线测试案例
        </router-link>
      </div>

      <footer class="app-footer">
        <p>
          🤖 AI驱动 · 智能地名解析 · 精确坐标可视化 · 
          <span class="tech-stack">Vue3 + TypeScript + 高德API</span>
        </p>
      </footer>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import Header from '@/components/Header.vue'
import LocationInput from '@/components/LocationInput.vue'
import VisualRenderer from '@/components/VisualRenderer.vue'
import type { LocationInfo } from '@/types/location'

const router = useRouter()
const locations = ref<LocationInfo[]>([])

const handleLocationsParsed = (parsedLocations: LocationInfo[]) => {
  locations.value = parsedLocations
}

const handleExportComplete = () => {
  console.log('Export completed')
}
</script>

<style scoped>
/* 全局样式 */
#app {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* 头部样式 */
.app-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 2rem 1rem;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.logo {
  font-size: 3rem;
  filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3));
}

.main-title {
  margin: 0;
  font-size: 2.5rem;
  font-weight: 700;
  text-shadow: 0 2px 4px rgba(0,0,0,0.3);
}

.subtitle {
  margin: 0.5rem 0 0 0;
  font-size: 1.1rem;
  opacity: 0.9;
}

.header-actions {
  display: flex;
  gap: 1rem;
}

.style-btn, .share-btn {
  padding: 0.75rem 1.5rem;
  border: 2px solid rgba(255,255,255,0.3);
  background: rgba(255,255,255,0.1);
  color: white;
  border-radius: 25px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.style-btn:hover, .share-btn:hover {
  background: rgba(255,255,255,0.2);
  transform: translateY(-2px);
}

/* 主内容区域 */
.app-main {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem 1rem;
}

/* 输入区域 */
.input-section {
  background: white;
  border-radius: 20px;
  padding: 2rem;
  box-shadow: 0 10px 30px rgba(0,0,0,0.1);
  margin-bottom: 2rem;
}

.section-title {
  margin: 0 0 0.5rem 0;
  font-size: 1.8rem;
  font-weight: 700;
  color: #2d3748;
}

.section-desc {
  margin: 0 0 1.5rem 0;
  color: #718096;
  font-size: 1.1rem;
}

.input-examples {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.example-tag {
  padding: 0.5rem 1rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 20px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
  user-select: none;
}

.example-tag:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
}

/* 结果展示区域 */
.results-section {
  background: white;
  border-radius: 20px;
  padding: 2rem;
  box-shadow: 0 10px 30px rgba(0,0,0,0.1);
}

/* AI处理动画 */
.ai-processing {
  text-align: center;
  padding: 3rem 1rem;
}

.processing-dots {
  display: flex;
  justify-content: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.processing-dots span {
  width: 12px;
  height: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  animation: bounce 1.4s ease-in-out infinite both;
}

.processing-dots span:nth-child(1) { animation-delay: -0.32s; }
.processing-dots span:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

.ai-processing p {
  font-size: 1.2rem;
  color: #666;
  margin: 0;
}

/* 画布区域 */
.canvas-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #f7fafc;
}

.canvas-header h3 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 700;
  color: #2d3748;
}

.canvas-actions {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.style-selector {
  padding: 0.5rem 1rem;
  border: 2px solid #e2e8f0;
  border-radius: 10px;
  background: white;
  font-weight: 600;
  cursor: pointer;
}

.export-btn, .share-instagram {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.export-btn {
  background: #48bb78;
  color: white;
}

.share-instagram {
  background: linear-gradient(45deg, #f09433 0%,#e6683c 25%,#dc2743 50%,#cc2366 75%,#bc1888 100%);
  color: white;
}

.export-btn:hover, .share-instagram:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0,0,0,0.2);
}

/* 路线图画布 */
.route-canvas {
  background: #f8fafc;
  border-radius: 15px;
  min-height: 400px;
  margin-bottom: 2rem;
  border: 2px solid #e2e8f0;
}

/* 路线信息卡片 */
.route-info-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
}

.location-card {
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  border-radius: 15px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: all 0.3s ease;
}

.location-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(0,0,0,0.1);
}

.card-number {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 1.2rem;
}

.card-content {
  flex: 1;
}

.card-content h4 {
  margin: 0 0 0.25rem 0;
  font-size: 1.2rem;
  font-weight: 700;
  color: #2d3748;
}

.coordinates {
  margin: 0.25rem 0;
  font-family: 'Monaco', monospace;
  color: #4a5568;
  font-size: 0.9rem;
}

.address {
  margin: 0.25rem 0 0 0;
  color: #718096;
  font-size: 0.9rem;
}

.card-actions {
  display: flex;
  gap: 0.5rem;
}

.view-on-map, .add-note {
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 8px;
  background: #e2e8f0;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.view-on-map:hover, .add-note:hover {
  background: #cbd5e0;
  transform: scale(1.1);
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

/* 响应式设计 */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }
  
  .main-title {
    font-size: 2rem;
  }
  
  .canvas-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .canvas-actions {
    justify-content: center;
  }
  
  .input-examples {
    justify-content: center;
  }
  
  .route-info-cards {
    grid-template-columns: 1fr;
  }
}
</style>