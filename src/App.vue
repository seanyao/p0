<template>
  <div id="app">
    <header class="app-header">
      <h1>🗺️ 旅游路线图工具</h1>
      <p>智能地名解析，轻松规划旅游路线</p>
    </header>

    <main class="app-main">
      <LocationParser
        :placeholder="'请输入地名，如：北京市朝阳区、上海外滩、西湖'"
        :show-history="true"
        :show-batch-mode="true"
        @location-parsed="handleLocationParsed"
        @error="handleError"
      />
    </main>

    <footer class="app-footer">
      <p>
        基于高德地图API · 支持单个和批量地名解析 · 
        <a 
          href="https://lbs.amap.com/api/javascript-api-v2/guide/abc/jscode" 
          target="_blank" 
          rel="noopener noreferrer"
        >
          API文档
        </a>
      </p>
    </footer>
  </div>
</template>

<script setup lang="ts">
/**
 * 旅游路线图工具 - 主应用组件
 */

import LocationParser from './components/LocationParser.vue'

const handleLocationParsed = (result: any) => {
  console.log('地名解析结果:', result)
}

const handleError = (error: string) => {
  console.error('解析错误:', error)
}
</script>

<style scoped>
.app-header {
  text-align: center;
  padding: 2rem 1rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  margin-bottom: 2rem;
}

.app-header h1 {
  margin: 0 0 0.5rem 0;
  font-size: 2.5rem;
  font-weight: 600;
}

.app-header p {
  margin: 0;
  font-size: 1.1rem;
  opacity: 0.9;
}

.app-main {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

.app-footer {
  text-align: center;
  padding: 2rem 1rem;
  margin-top: 3rem;
  border-top: 1px solid #e0e0e0;
  color: #666;
}

.app-footer a {
  color: #667eea;
  text-decoration: none;
}

.app-footer a:hover {
  text-decoration: underline;
}
</style>