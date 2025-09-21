/**
 * 地名解析组合式函数
 */

import { ref, reactive } from 'vue'
import type { LocationInput, ParseResult, BatchParseResult } from '../types/location'
import { locationService } from '../services/locationService'

export function useLocationParser() {
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const result = ref<ParseResult | null>(null)
  const batchResult = ref<BatchParseResult | null>(null)

  // 解析单个地名
  const parseLocation = async (input: LocationInput) => {
    isLoading.value = true
    error.value = null
    result.value = null

    try {
      const response = await locationService.parseLocation(input.name)
      result.value = response
    } catch (err) {
      error.value = err instanceof Error ? err.message : '解析失败'
    } finally {
      isLoading.value = false
    }
  }

  // 批量解析地名
  const parseBatch = async (input: string) => {
    isLoading.value = true
    error.value = null
    batchResult.value = null

    try {
      const response = await locationService.parseBatch(input)
      batchResult.value = response
    } catch (err) {
      error.value = err instanceof Error ? err.message : '批量解析失败'
    } finally {
      isLoading.value = false
    }
  }

  // 重试
  const retry = () => {
    error.value = null
  }

  return {
    isLoading,
    error,
    result,
    batchResult,
    parseLocation,
    parseBatch,
    retry
  }
}