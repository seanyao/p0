<template>
  <div class="location-parser" :class="className">
    <!-- 模式切换 -->
    <div v-if="showBatchMode" class="mode-switcher">
      <button 
        :class="{ active: mode === 'single' }"
        @click="mode = 'single'"
      >
        单个解析
      </button>
      <button 
        :class="{ active: mode === 'batch' }"
        @click="mode = 'batch'"
      >
        批量解析
      </button>
    </div>

    <!-- 单个地名解析 -->
    <div v-if="mode === 'single'" class="single-mode">
      <div class="input-container">
        <input
          v-model="input"
          type="text"
          :placeholder="placeholder"
          class="location-input"
          @keyup.enter="handleSingleParse"
          :disabled="isLoading"
        />
        <button 
          @click="handleSingleParse"
          :disabled="!input.trim() || isLoading"
          class="parse-button"
        >
          {{ isLoading ? '解析中...' : '解析' }}
        </button>
      </div>

      <!-- 自动完成建议 -->
      <div v-if="suggestions.length > 0" class="suggestions">
        <div 
          v-for="suggestion in suggestions" 
          :key="suggestion.id"
          class="suggestion-item"
          @click="selectSuggestion(suggestion)"
        >
          {{ suggestion.name }}
        </div>
      </div>

      <!-- 输入纠正提示 -->
      <div v-if="correctedInput && correctedInput !== input" class="correction-hint">
        建议输入: {{ correctedInput }}
        <button @click="input = correctedInput" class="apply-correction">
          应用
        </button>
      </div>
    </div>

    <!-- 批量地名解析 -->
    <div v-if="mode === 'batch'" class="batch-mode">
      <div class="batch-input-container">
        <textarea
          v-model="batchInput"
          placeholder="请输入多个地名，支持以下格式：&#10;1. 逗号分隔：北京,上海,广州&#10;2. 换行分隔：&#10;   北京&#10;   上海&#10;   广州&#10;3. 箭头连接：北京→上海→广州"
          class="batch-input"
          rows="6"
          :disabled="isLoading"
        ></textarea>
        <button 
          @click="handleBatchParse"
          :disabled="!batchInput.trim() || isLoading"
          class="parse-button batch-parse-button"
        >
          {{ isLoading ? '批量解析中...' : '批量解析' }}
        </button>
      </div>
    </div>

    <!-- 错误显示 -->
    <div v-if="error" class="error-message">
      <span>{{ error }}</span>
      <button @click="retry" class="retry-button">重试</button>
    </div>

    <!-- 单个解析结果 -->
    <LocationResult 
      v-if="result?.success && result.location" 
      :location="result.location" 
    />

    <!-- 批量解析结果 -->
    <BatchLocationResult 
      v-if="batchResult && batchResult.summary" 
      :result="batchResult" 
    />

    <!-- 历史记录 -->
    <LocationHistory
      v-if="showHistory && history.length > 0"
      :history="history"
      @clear-history="clearHistory"
      @select-location="handleHistorySelect"
    />
  </div>
</template>

<script setup lang="ts">
/**
 * 地名解析组件 - Vue 3版本
 */

import { ref, computed, watch } from 'vue'
import type { LocationInput } from '../types/location'
import { useLocationParser } from '../composables/useLocationParser'
import { useLocationAutoComplete } from '../composables/useLocationAutoComplete'
import { useLocationHistory } from '../composables/useLocationHistory'
import LocationResult from './LocationResult.vue'
import BatchLocationResult from './BatchLocationResult.vue'
import LocationHistory from './LocationHistory.vue'

// 组件属性
interface Props {
  placeholder?: string
  className?: string
  showHistory?: boolean
  showBatchMode?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: '请输入地名，如：北京市朝阳区',
  className: '',
  showHistory: true,
  showBatchMode: true
})

// 组件事件
const emit = defineEmits<{
  locationParsed: [result: any]
  error: [error: string]
}>()

// 响应式数据
const mode = ref<'single' | 'batch'>('single')
const batchInput = ref('')

// 使用组合式函数
const {
  isLoading,
  error,
  result,
  batchResult,
  parseLocation,
  parseBatch,
  retry
} = useLocationParser()

const {
  input,
  correctedInput,
  suggestions,
  selectSuggestion,
  clearInput
} = useLocationAutoComplete()

const { history, addToHistory, clearHistory } = useLocationHistory()

// 处理单个地名解析
const handleSingleParse = async () => {
  if (!input.value.trim()) return
  
  const locationInput: LocationInput = {
    name: correctedInput.value || input.value,
    timeout: 5000,
    useCache: true
  }
  
  await parseLocation(locationInput)
}

// 处理批量地名解析
const handleBatchParse = async () => {
  if (!batchInput.value.trim()) return
  
  await parseBatch(batchInput.value)
}

// 处理历史记录选择
const handleHistorySelect = (location: any) => {
  input.value = location.name
}

// 监听解析结果
watch(result, (newResult) => {
  if (newResult?.success && newResult.location) {
    addToHistory(newResult.location)
    emit('locationParsed', newResult)
  }
})

watch(batchResult, (newBatchResult) => {
  if (newBatchResult && newBatchResult.summary && newBatchResult.summary.successful > 0) {
    // 将成功解析的地名添加到历史记录
    newBatchResult.results.forEach((item: any) => {
      if (item.success && item.location) {
        addToHistory(item.location)
      }
    })
    emit('locationParsed', newBatchResult)
  }
})

// 监听错误
watch(error, (newError) => {
  if (newError) {
    emit('error', newError)
  }
})
</script>

<style scoped>
.location-parser {
  max-width: 800px;
  margin: 0 auto;
  padding: 1rem;
}

.mode-switcher {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  justify-content: center;
}

.mode-switcher button {
  padding: 0.5rem 1rem;
  border: 2px solid #667eea;
  background: white;
  color: #667eea;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
}

.mode-switcher button.active,
.mode-switcher button:hover {
  background: #667eea;
  color: white;
}

.input-container {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.location-input {
  flex: 1;
  padding: 0.75rem;
  border: 2px solid #e0e0e0;
  border-radius: 0.5rem;
  font-size: 1rem;
  transition: border-color 0.2s;
}

.location-input:focus {
  outline: none;
  border-color: #667eea;
}

.parse-button {
  padding: 0.75rem 1.5rem;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  font-size: 1rem;
  transition: background-color 0.2s;
}

.parse-button:hover:not(:disabled) {
  background: #5a6fd8;
}

.parse-button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.batch-input-container {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.batch-input {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #e0e0e0;
  border-radius: 0.5rem;
  font-size: 1rem;
  font-family: inherit;
  resize: vertical;
  transition: border-color 0.2s;
}

.batch-input:focus {
  outline: none;
  border-color: #667eea;
}

.batch-parse-button {
  align-self: flex-end;
}

.suggestions {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 0.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 1rem;
}

.suggestion-item {
  padding: 0.75rem;
  cursor: pointer;
  border-bottom: 1px solid #f0f0f0;
  transition: background-color 0.2s;
}

.suggestion-item:hover {
  background: #f8f9ff;
}

.suggestion-item:last-child {
  border-bottom: none;
}

.correction-hint {
  background: #fff3cd;
  border: 1px solid #ffeaa7;
  border-radius: 0.5rem;
  padding: 0.75rem;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.apply-correction {
  padding: 0.25rem 0.5rem;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
  font-size: 0.875rem;
}

.error-message {
  background: #f8d7da;
  border: 1px solid #f5c6cb;
  border-radius: 0.5rem;
  padding: 0.75rem;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: #721c24;
}

.retry-button {
  padding: 0.25rem 0.5rem;
  background: #dc3545;
  color: white;
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
  font-size: 0.875rem;
}
</style>