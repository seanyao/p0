<template>
  <div class="batch-result">
    <h3>批量解析结果</h3>
    
    <!-- 统计信息 -->
    <div class="summary">
      <div class="summary-item">
        <span class="label">总数:</span>
        <span class="value">{{ result.summary.total }}</span>
      </div>
      <div class="summary-item success">
        <span class="label">成功:</span>
        <span class="value">{{ result.summary.successful }}</span>
      </div>
      <div class="summary-item failed">
        <span class="label">失败:</span>
        <span class="value">{{ result.summary.failed }}</span>
      </div>
    </div>

    <!-- 解析结果列表 -->
    <div class="results-list">
      <div 
        v-for="(item, index) in result.results" 
        :key="index"
        class="result-item"
        :class="{ success: item.success, failed: !item.success }"
      >
        <div v-if="item.success && item.location" class="success-result">
          <div class="location-name">{{ item.location.name }}</div>
          <div class="location-details">
            <span class="coordinates">
              {{ item.location.coordinates.longitude }}, {{ item.location.coordinates.latitude }}
            </span>
            <span v-if="item.location.address" class="address">
              {{ item.location.address }}
            </span>
          </div>
          <div class="actions">
            <button @click="copyCoordinates(item.location)" class="copy-btn">
              复制坐标
            </button>
            <button @click="openInMap(item.location)" class="map-btn">
              查看地图
            </button>
          </div>
        </div>
        
        <div v-else class="failed-result">
          <div class="error-info">
            <span class="error-icon">❌</span>
            <span class="error-message">{{ item.error || '解析失败' }}</span>
          </div>
          <div v-if="item.suggestions && item.suggestions.length > 0" class="suggestions">
            <span class="suggestions-label">建议:</span>
            <span class="suggestions-list">{{ item.suggestions.join(', ') }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 批量操作 -->
    <div class="batch-actions">
      <button @click="copyAllCoordinates" class="batch-copy-btn">
        复制所有坐标
      </button>
      <button @click="exportResults" class="export-btn">
        导出结果
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 批量地名解析结果组件
 */

import type { BatchParseResult, LocationInfo } from '../types/location'

interface Props {
  result: BatchParseResult
}

const props = defineProps<Props>()

// 复制单个坐标
const copyCoordinates = async (location: LocationInfo) => {
  const coordinates = `${location.coordinates.longitude},${location.coordinates.latitude}`
  
  try {
    await navigator.clipboard.writeText(coordinates)
    alert(`${location.name} 的坐标已复制`)
  } catch (error) {
    console.error('复制失败:', error)
  }
}

// 在地图中查看
const openInMap = (location: LocationInfo) => {
  const { longitude, latitude } = location.coordinates
  const url = `https://uri.amap.com/marker?position=${longitude},${latitude}&name=${encodeURIComponent(location.name)}`
  window.open(url, '_blank')
}

// 复制所有坐标
const copyAllCoordinates = async () => {
  const successfulResults = props.result.results.filter(item => item.success && item.location)
  const coordinates = successfulResults.map(item => 
    `${item.location!.name}: ${item.location!.coordinates.longitude},${item.location!.coordinates.latitude}`
  ).join('\n')
  
  try {
    await navigator.clipboard.writeText(coordinates)
    alert(`已复制 ${successfulResults.length} 个地名的坐标`)
  } catch (error) {
    console.error('复制失败:', error)
  }
}

// 导出结果
const exportResults = () => {
  const data = props.result.results.map(item => {
    if (item.success && item.location) {
      return {
        name: item.location.name,
        longitude: item.location.coordinates.longitude,
        latitude: item.location.coordinates.latitude,
        address: item.location.address || '',
        status: 'success'
      }
    } else {
      return {
        error: item.error || '解析失败',
        suggestions: item.suggestions?.join(', ') || '',
        status: 'failed'
      }
    }
  })

  const csv = [
    'Name,Longitude,Latitude,Address,Status,Error,Suggestions',
    ...data.map(row => {
      if (row.status === 'success') {
        return `"${row.name}",${row.longitude},${row.latitude},"${row.address}",${row.status},,`
      } else {
        return `,,,,${row.status},"${row.error}","${row.suggestions}"`
      }
    })
  ].join('\n')

  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = `location_results_${new Date().toISOString().split('T')[0]}.csv`
  link.click()
}
</script>

<style scoped>
.batch-result {
  margin-top: 1.5rem;
}

.batch-result h3 {
  margin: 0 0 1rem 0;
  color: #333;
  font-size: 1.25rem;
}

.summary {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 0.5rem;
}

.summary-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
}

.summary-item .label {
  font-size: 0.875rem;
  color: #666;
}

.summary-item .value {
  font-size: 1.5rem;
  font-weight: bold;
  color: #333;
}

.summary-item.success .value {
  color: #28a745;
}

.summary-item.failed .value {
  color: #dc3545;
}

.results-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.result-item {
  padding: 1rem;
  border-radius: 0.5rem;
  border: 1px solid #e0e0e0;
}

.result-item.success {
  background: #f8fff9;
  border-color: #28a745;
}

.result-item.failed {
  background: #fff5f5;
  border-color: #dc3545;
}

.success-result .location-name {
  font-weight: bold;
  color: #333;
  margin-bottom: 0.5rem;
}

.location-details {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  margin-bottom: 0.75rem;
  font-size: 0.9rem;
  color: #666;
}

.coordinates {
  font-family: monospace;
}

.actions {
  display: flex;
  gap: 0.5rem;
}

.copy-btn,
.map-btn {
  padding: 0.25rem 0.75rem;
  border: 1px solid #667eea;
  background: white;
  color: #667eea;
  border-radius: 0.25rem;
  cursor: pointer;
  font-size: 0.8rem;
  transition: all 0.2s;
}

.copy-btn:hover,
.map-btn:hover {
  background: #667eea;
  color: white;
}

.map-btn {
  border-color: #28a745;
  color: #28a745;
}

.map-btn:hover {
  background: #28a745;
}

.failed-result .error-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.error-message {
  color: #dc3545;
  font-weight: 500;
}

.suggestions {
  font-size: 0.9rem;
  color: #666;
}

.suggestions-label {
  font-weight: 500;
}

.batch-actions {
  display: flex;
  gap: 0.5rem;
  justify-content: center;
  padding-top: 1rem;
  border-top: 1px solid #e0e0e0;
}

.batch-copy-btn,
.export-btn {
  padding: 0.75rem 1.5rem;
  border: 1px solid #667eea;
  background: white;
  color: #667eea;
  border-radius: 0.5rem;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.batch-copy-btn:hover,
.export-btn:hover {
  background: #667eea;
  color: white;
}

.export-btn {
  border-color: #28a745;
  color: #28a745;
}

.export-btn:hover {
  background: #28a745;
}
</style>