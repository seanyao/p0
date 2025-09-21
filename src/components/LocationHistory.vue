<template>
  <div class="location-history">
    <div class="history-header">
      <h3>历史记录</h3>
      <button @click="$emit('clear-history')" class="clear-button">
        清空历史
      </button>
    </div>
    
    <div class="history-list">
      <div 
        v-for="item in history" 
        :key="item.id"
        class="history-item"
        @click="$emit('select-location', item.location)"
      >
        <div class="location-info">
          <div class="location-name">{{ item.location.name }}</div>
          <div class="location-address">{{ item.location.address || '无详细地址' }}</div>
          <div class="timestamp">{{ formatTimestamp(item.timestamp) }}</div>
        </div>
        <div class="coordinates">
          {{ item.location.coordinates.longitude }}, {{ item.location.coordinates.latitude }}
        </div>
        <button 
          @click.stop="removeItem(item.id)"
          class="remove-button"
          title="删除此记录"
        >
          ×
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 地名历史记录组件
 */

import type { HistoryItem, LocationInfo } from '../types/location'

interface Props {
  history: HistoryItem[]
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'clear-history': []
  'select-location': [location: LocationInfo]
  'remove-item': [id: string]
}>()

// 格式化时间戳
const formatTimestamp = (timestamp: number): string => {
  const date = new Date(timestamp)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / (1000 * 60))
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

  if (diffMins < 1) {
    return '刚刚'
  } else if (diffMins < 60) {
    return `${diffMins}分钟前`
  } else if (diffHours < 24) {
    return `${diffHours}小时前`
  } else if (diffDays < 7) {
    return `${diffDays}天前`
  } else {
    return date.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }
}

// 删除单个记录
const removeItem = (id: string) => {
  emit('remove-item', id)
}
</script>

<style scoped>
.location-history {
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e0e0e0;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.history-header h3 {
  margin: 0;
  color: #333;
  font-size: 1.1rem;
}

.clear-button {
  padding: 0.5rem 1rem;
  background: #dc3545;
  color: white;
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
  font-size: 0.875rem;
  transition: background-color 0.2s;
}

.clear-button:hover {
  background: #c82333;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  max-height: 400px;
  overflow-y: auto;
}

.history-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}

.history-item:hover {
  background: #f8f9ff;
  border-color: #667eea;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.location-info {
  flex: 1;
  min-width: 0;
}

.location-name {
  font-weight: 500;
  color: #333;
  margin-bottom: 0.25rem;
}

.location-address {
  font-size: 0.875rem;
  color: #666;
  margin-bottom: 0.25rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.timestamp {
  font-size: 0.75rem;
  color: #999;
}

.coordinates {
  font-family: monospace;
  font-size: 0.875rem;
  color: #555;
  background: #f5f5f5;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  white-space: nowrap;
}

.remove-button {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  width: 1.5rem;
  height: 1.5rem;
  background: #dc3545;
  color: white;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  font-size: 1rem;
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s;
}

.history-item:hover .remove-button {
  opacity: 1;
}

.remove-button:hover {
  background: #c82333;
}

/* 滚动条样式 */
.history-list::-webkit-scrollbar {
  width: 6px;
}

.history-list::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.history-list::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.history-list::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>