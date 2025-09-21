/**
 * 地名历史记录组合式函数
 */

import { ref, onMounted } from 'vue'
import type { LocationInfo, HistoryItem } from '../types/location'

export function useLocationHistory() {
  const history = ref<HistoryItem[]>([])
  const maxHistorySize = 20

  // 从localStorage加载历史记录
  const loadHistory = () => {
    try {
      const stored = localStorage.getItem('location-history')
      if (stored) {
        history.value = JSON.parse(stored)
      }
    } catch (error) {
      console.error('加载历史记录失败:', error)
      history.value = []
    }
  }

  // 保存历史记录到localStorage
  const saveHistory = () => {
    try {
      localStorage.setItem('location-history', JSON.stringify(history.value))
    } catch (error) {
      console.error('保存历史记录失败:', error)
    }
  }

  // 添加到历史记录
  const addToHistory = (location: LocationInfo) => {
    // 检查是否已存在
    const existingIndex = history.value.findIndex(
      item => item.location.name === location.name
    )

    if (existingIndex >= 0) {
      // 如果已存在，移到最前面
      const existing = history.value.splice(existingIndex, 1)[0]
      existing.timestamp = Date.now()
      history.value.unshift(existing)
    } else {
      // 添加新记录
      const historyItem: HistoryItem = {
        id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        location,
        timestamp: Date.now()
      }
      
      history.value.unshift(historyItem)
      
      // 限制历史记录数量
      if (history.value.length > maxHistorySize) {
        history.value = history.value.slice(0, maxHistorySize)
      }
    }

    saveHistory()
  }

  // 清空历史记录
  const clearHistory = () => {
    history.value = []
    saveHistory()
  }

  // 删除单个历史记录
  const removeFromHistory = (id: string) => {
    const index = history.value.findIndex(item => item.id === id)
    if (index >= 0) {
      history.value.splice(index, 1)
      saveHistory()
    }
  }

  // 组件挂载时加载历史记录
  onMounted(() => {
    loadHistory()
  })

  return {
    history,
    addToHistory,
    clearHistory,
    removeFromHistory
  }
}