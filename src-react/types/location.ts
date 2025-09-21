/**
 * 地名解析相关的类型定义
 */

// 坐标类型
export interface Coordinate {
  /** 经度 */
  lng: number
  /** 纬度 */
  lat: number
}

// 地名信息
export interface LocationInfo {
  /** 地名 */
  name: string
  /** 完整地址 */
  address: string
  /** 坐标 */
  coordinate: Coordinate
  /** 行政区划代码 */
  adcode?: string
  /** 城市名称 */
  city?: string
  /** 区县名称 */
  district?: string
  /** 省份名称 */
  province?: string
  /** 格式化地址 */
  formatted_address?: string
  /** 地点类型 */
  type?: string
  /** 置信度 */
  confidence?: number
}

// 地名解析输入参数
export interface LocationInput {
  /** 地名 */
  name: string
  /** 城市限制 */
  city?: string
  /** 超时时间(毫秒) */
  timeout?: number
  /** 是否使用缓存 */
  useCache?: boolean
}

// 地名解析结果
export interface LocationParseResult {
  /** 是否成功 */
  success: boolean
  /** 地名信息 */
  location?: LocationInfo
  /** 错误信息 */
  error?: string
  /** 是否来自缓存 */
  cached?: boolean
  /** 解析耗时(毫秒) */
  duration?: number
}

// 批量地名解析输入
export interface BatchLocationInput {
  queries: string[]      // 查询字符串数组
  options?: {
    maxConcurrent?: number  // 最大并发数
    timeout?: number        // 超时时间
    useCache?: boolean      // 是否使用缓存
  }
}

// 批量解析结果
export interface BatchLocationResult {
  /** 解析结果列表 */
  results: LocationParseResult[]
  /** 统计信息 */
  summary: {
    /** 总数 */
    total: number
    /** 成功数 */
    successful: number
    /** 失败数 */
    failed: number
    /** 缓存命中数 */
    cached: number
  }
  /** 总耗时(毫秒) */
  duration: number
}

// 地名解析错误
export interface LocationParseError {
  /** 错误代码 */
  code: string
  /** 错误信息 */
  message: string
  /** 原始错误 */
  originalError?: any
}

// 地名解析配置
export interface LocationParserConfig {
  /** API密钥 */
  apiKey: string
  /** 基础URL */
  baseUrl: string
  /** 安全密钥 */
  securityKey?: string
  /** 最大并发数 */
  maxConcurrent?: number
  /** 超时时间(毫秒) */
  timeout?: number
  /** 重试次数 */
  retryCount?: number
  /** 验证配置 */
  validation?: {
    minLength: number
    maxLength: number
    allowedChars: RegExp
    forbiddenWords: string[]
  }
  /** 缓存配置 */
  cache?: {
    enabled: boolean
    ttl: number
    maxSize: number
  }
}

// 高德地图API响应类型
export interface AmapGeocodeResponse {
  status: string
  info: string
  infocode: string
  count: string
  geocodes: AmapGeocode[]
}

export interface AmapGeocode {
  formatted_address: string
  country: string
  province: string
  citycode: string
  city: string
  district: string
  township: string[]
  neighborhood: {
    name: string[]
    type: string[]
  }
  building: {
    name: string[]
    type: string[]
  }
  adcode: string
  street: string[]
  number: string[]
  location: string
  level: string
}

// 缓存项结构
export interface CacheItem {
  data: LocationInfo
  timestamp: number
  ttl: number
}

// 解析器配置
export interface ParserConfig {
  apiKey: string
  baseUrl: string
  timeout: number
  maxRetries: number
  cacheEnabled: boolean
  cacheDuration: number
  maxConcurrent: number
}