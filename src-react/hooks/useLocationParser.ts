/**
 * 地名解析 React Hook
 * 提供地名解析功能的React集成
 */

import { useState, useCallback, useEffect, useRef } from 'react'
import type {
  LocationInput,
  LocationParseResult,
  BatchLocationResult,
  LocationInfo
} from '../types/location'
import { parseLocation, parseBatchLocations, clearLocationCache } from '../services/locationParser'
import { validateBatchInput, generateInputSuggestions, autoCorrectInput } from '../utils/locationValidator'

// Hook 状态类型
interface UseLocationParserState {
  isLoading: boolean
  error: string | null
  result: LocationParseResult | null
  batchResult: BatchLocationResult | null
  suggestions: string[]
}

// Hook 返回类型
interface UseLocationParserReturn extends UseLocationParserState {
  // 单个地名解析
  parseLocation: (input: LocationInput) => Promise<void>
  
  // 批量地名解析
  parseBatch: (input: string) => Promise<void>
  
  // 获取输入建议
  getSuggestions: (input: string) => void
  
  // 清除结果
  clearResults: () => void
  
  // 清除缓存
  clearCache: () => void
  
  // 重试解析
  retry: () => Promise<void>
}

/**
 * 地名解析 Hook
 */
export function useLocationParser(): UseLocationParserReturn {
  const [state, setState] = useState<UseLocationParserState>({
    isLoading: false,
    error: null,
    result: null,
    batchResult: null,
    suggestions: []
  })
  
  // 保存最后一次的输入，用于重试
  const lastInputRef = useRef<LocationInput | string | null>(null)
  const lastInputTypeRef = useRef<'single' | 'batch' | null>(null)
  
  // 防抖定时器
  const debounceTimerRef = useRef<NodeJS.Timeout | undefined>(undefined)
  
  /**
   * 更新状态的辅助函数
   */
  const updateState = useCallback((updates: Partial<UseLocationParserState>) => {
    setState(prev => ({ ...prev, ...updates }))
  }, [])
  
  /**
   * 单个地名解析
   */
  const handleParseLocation = useCallback(async (input: LocationInput) => {
    try {
      updateState({ isLoading: true, error: null })
      lastInputRef.current = input
      lastInputTypeRef.current = 'single'
      
      const result = await parseLocation(input)
      
      if (result.success) {
        updateState({ 
          result, 
          isLoading: false,
          error: null 
        })
      } else {
        updateState({ 
          result, 
          isLoading: false,
          error: result.error || '解析失败' 
        })
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '未知错误'
      updateState({ 
        isLoading: false, 
        error: errorMessage,
        result: null 
      })
    }
  }, [updateState])
  
  /**
   * 批量地名解析
   */
  const handleParseBatch = useCallback(async (input: string) => {
    try {
      updateState({ isLoading: true, error: null })
      lastInputRef.current = input
      lastInputTypeRef.current = 'batch'
      
      // 验证批量输入
      const validation = validateBatchInput(input)
      if (!validation.isValid) {
        updateState({
          isLoading: false,
          error: validation.errors.join('; ')
        })
        return
      }
      
      // 执行批量解析
      const locations = validation.locations
      
      const batchResult = await parseBatchLocations(locations)
      
      updateState({
        batchResult,
        isLoading: false,
        error: batchResult.summary.failed > 0 ? '部分地名解析失败' : null
      })
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : '批量解析失败'
      updateState({
        isLoading: false,
        error: errorMessage,
        batchResult: null
      })
    }
  }, [updateState])
  
  /**
   * 获取输入建议
   */
  const handleGetSuggestions = useCallback((input: string) => {
    // 清除之前的防抖定时器
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current)
    }
    
    // 设置新的防抖定时器
    debounceTimerRef.current = setTimeout(() => {
      const suggestions = generateInputSuggestions(input)
      updateState({ suggestions })
    }, 300) // 300ms 防抖
  }, [updateState])
  
  /**
   * 清除结果
   */
  const clearResults = useCallback(() => {
    setState({
      isLoading: false,
      error: null,
      result: null,
      batchResult: null,
      suggestions: []
    })
    lastInputRef.current = null
    lastInputTypeRef.current = null
  }, [])
  
  /**
   * 清除缓存
   */
  const handleClearCache = useCallback(() => {
    clearLocationCache()
  }, [])
  
  /**
   * 重试解析
   */
  const retry = useCallback(async () => {
    const lastInput = lastInputRef.current
    const lastType = lastInputTypeRef.current
    
    if (!lastInput || !lastType) {
      updateState({ error: '没有可重试的操作' })
      return
    }
    
    if (lastType === 'single') {
      await handleParseLocation(lastInput as LocationInput)
    } else if (lastType === 'batch') {
      await handleParseBatch(lastInput as string)
    }
  }, [handleParseLocation, handleParseBatch, updateState])
  
  // 清理防抖定时器
  useEffect(() => {
    return () => {
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current)
      }
    }
  }, [])
  
  return {
    ...state,
    parseLocation: handleParseLocation,
    parseBatch: handleParseBatch,
    getSuggestions: handleGetSuggestions,
    clearResults,
    clearCache: handleClearCache,
    retry
  }
}

/**
 * 地名输入建议 Hook
 */
export function useLocationSuggestions(input: string, delay: number = 300) {
  const [suggestions, setSuggestions] = useState<string[]>([])
  const [isLoading, setIsLoading] = useState(false)
  
  useEffect(() => {
    if (!input.trim()) {
      setSuggestions([])
      return
    }
    
    setIsLoading(true)
    
    const timer = setTimeout(() => {
      const newSuggestions = generateInputSuggestions(input)
      setSuggestions(newSuggestions)
      setIsLoading(false)
    }, delay)
    
    return () => {
      clearTimeout(timer)
      setIsLoading(false)
    }
  }, [input, delay])
  
  return { suggestions, isLoading }
}

/**
 * 地名自动完成 Hook
 */
export function useLocationAutoComplete() {
  const [input, setInput] = useState('')
  const [correctedInput, setCorrectedInput] = useState('')
  const { suggestions, isLoading } = useLocationSuggestions(input)
  
  // 自动修正输入
  useEffect(() => {
    if (input) {
      const corrected = autoCorrectInput(input)
      setCorrectedInput(corrected)
    } else {
      setCorrectedInput('')
    }
  }, [input])
  
  const selectSuggestion = useCallback((suggestion: string) => {
    setInput(suggestion)
    setCorrectedInput(suggestion)
  }, [])
  
  const clearInput = useCallback(() => {
    setInput('')
    setCorrectedInput('')
  }, [])
  
  return {
    input,
    setInput,
    correctedInput,
    suggestions,
    isLoading,
    selectSuggestion,
    clearInput
  }
}

/**
 * 地名解析历史记录 Hook
 */
export function useLocationHistory(maxSize: number = 10) {
  const [history, setHistory] = useState<LocationInfo[]>([])
  
  const addToHistory = useCallback((location: LocationInfo) => {
    setHistory(prev => {
      // 避免重复
      const filtered = prev.filter(item => 
        item.coordinate.lng !== location.coordinate.lng ||
        item.coordinate.lat !== location.coordinate.lat
      )
      
      // 添加到开头，限制数量
      return [location, ...filtered].slice(0, maxSize)
    })
  }, [maxSize])
  
  const clearHistory = useCallback(() => {
    setHistory([])
  }, [])
  
  const removeFromHistory = useCallback((index: number) => {
    setHistory(prev => prev.filter((_, i) => i !== index))
  }, [])
  
  return {
    history,
    addToHistory,
    clearHistory,
    removeFromHistory
  }
}