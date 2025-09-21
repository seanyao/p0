/**
 * 地名解析相关类型定义
 */

// 地名输入参数
export interface LocationInput {
  name: string
  timeout?: number
  useCache?: boolean
}

// 地理坐标
export interface Coordinates {
  longitude: number
  latitude: number
}

// 地名信息
export interface LocationInfo {
  name: string
  coordinates: Coordinates
  address?: string
  city?: string
  province?: string
  district?: string
  adcode?: string
  level?: string
}

// 解析结果
export interface ParseResult {
  success: boolean
  location?: LocationInfo
  error?: string
  suggestions?: string[]
  correctedInput?: string
}

// 批量解析结果
export interface BatchParseResult {
  summary: {
    total: number
    successful: number
    failed: number
  }
  results: ParseResult[]
}

// 自动完成建议
export interface AutoCompleteSuggestion {
  id: string
  name: string
  address?: string
  location?: Coordinates
}

// 历史记录项
export interface HistoryItem {
  id: string
  location: LocationInfo
  timestamp: number
}