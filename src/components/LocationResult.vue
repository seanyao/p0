<template>
  <div class="location-result">
    <h3>解析结果</h3>
    <div class="result-card">
      <div class="location-info">
        <h4>{{ location.name }}</h4>
        <p v-if="location.address" class="address">{{ location.address }}</p>
        <div class="coordinates">
          <span>经度: {{ location.coordinates.longitude }}</span>
          <span>纬度: {{ location.coordinates.latitude }}</span>
        </div>
        <div v-if="location.city || location.province" class="administrative">
          <span v-if="location.province">{{ location.province }}</span>
          <span v-if="location.city">{{ location.city }}</span>
          <span v-if="location.district">{{ location.district }}</span>
        </div>
      </div>
      <div class="actions">
        <button @click="copyCoordinates" class="copy-button">
          复制坐标
        </button>
        <button @click="openInMap" class="map-button">
          在地图中查看
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 单个地名解析结果组件
 */

import type { LocationInfo } from '../types/location'

interface Props {
  location: LocationInfo
}

const props = defineProps<Props>()

// 复制坐标
const copyCoordinates = async () => {
  const coordinates = `${props.location.coordinates.longitude},${props.location.coordinates.latitude}`
  
  try {
    await navigator.clipboard.writeText(coordinates)
    alert('坐标已复制到剪贴板')
  } catch (error) {
    console.error('复制失败:', error)
    // 降级方案
    const textArea = document.createElement('textarea')
    textArea.value = coordinates
    document.body.appendChild(textArea)
    textArea.select()
    document.execCommand('copy')
    document.body.removeChild(textArea)
    alert('坐标已复制到剪贴板')
  }
}

// 在地图中查看
const openInMap = () => {
  const { longitude, latitude } = props.location.coordinates
  const url = `https://uri.amap.com/marker?position=${longitude},${latitude}&name=${encodeURIComponent(props.location.name)}`
  window.open(url, '_blank')
}
</script>

<style scoped>
.location-result {
  margin-top: 1.5rem;
}

.location-result h3 {
  margin: 0 0 1rem 0;
  color: #333;
  font-size: 1.25rem;
}

.result-card {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 0.5rem;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.location-info h4 {
  margin: 0 0 0.5rem 0;
  color: #333;
  font-size: 1.1rem;
}

.address {
  color: #666;
  margin: 0 0 1rem 0;
  font-size: 0.9rem;
}

.coordinates {
  display: flex;
  gap: 1rem;
  margin-bottom: 0.5rem;
  font-family: monospace;
  font-size: 0.9rem;
  color: #555;
}

.administrative {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  font-size: 0.9rem;
  color: #666;
}

.administrative span {
  background: #f0f0f0;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
}

.actions {
  display: flex;
  gap: 0.5rem;
}

.copy-button,
.map-button {
  padding: 0.5rem 1rem;
  border: 1px solid #667eea;
  background: white;
  color: #667eea;
  border-radius: 0.25rem;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.copy-button:hover,
.map-button:hover {
  background: #667eea;
  color: white;
}

.map-button {
  border-color: #28a745;
  color: #28a745;
}

.map-button:hover {
  background: #28a745;
  color: white;
}
</style>