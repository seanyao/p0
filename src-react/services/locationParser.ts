/**
 * 地名解析服务
 * 基于高德地图API实现地名到坐标的转换
 */

import type {
  LocationInput,
  LocationInfo,
  LocationParseResult,
  LocationParseError,
  BatchLocationResult,
  AmapGeocodeResponse,
  AmapGeocode,
  Coordinate
} from '../types/location'
import { locationParserConfig, buildApiUrl, getApiHeaders } from '../utils/config'

// 缓存管理
class LocationCache {
  private cache = new Map<string, { data: LocationInfo[], timestamp: number }>()
  private readonly ttl: number
  private readonly maxSize: number

  constructor(ttl: number, maxSize: number) {
    this.ttl = ttl
    this.maxSize = maxSize
  }

  get(key: string): LocationInfo[] | null {
    const item = this.cache.get(key)
    if (!item) return null

    // 检查是否过期
    if (Date.now() - item.timestamp > this.ttl) {
      this.cache.delete(key)
      return null
    }

    return item.data
  }

  set(key: string, data: LocationInfo[]): void {
    // 如果缓存已满，删除最旧的条目
    if (this.cache.size >= this.maxSize) {
      const firstKey = this.cache.keys().next().value
      if (firstKey) {
        this.cache.delete(firstKey)
      }
    }

    this.cache.set(key, {
      data,
      timestamp: Date.now()
    })
  }

  clear(): void {
    this.cache.clear()
  }

  size(): number {
    return this.cache.size
  }
}

// 创建缓存实例
const cache = new LocationCache(
  locationParserConfig.cache?.ttl || 30 * 60 * 1000,
  locationParserConfig.cache?.maxSize || 1000
)

/**
 * 验证地名输入
 */
function validateLocationInput(query: string): LocationParseError | null {
  const validation = locationParserConfig.validation

  if (!validation) {
    return null
  }

  // 检查长度
  if (query.length < validation.minLength) {
    return {
      code: 'INVALID_LENGTH',
      message: `地名长度不能少于${validation.minLength}个字符`
    }
  }

  if (query.length > validation.maxLength) {
    return {
      code: 'INVALID_LENGTH',
      message: `地名长度不能超过${validation.maxLength}个字符`
    }
  }

  // 检查字符
  if (!validation.allowedChars.test(query)) {
    return {
      code: 'INVALID_CHARS',
      message: '地名包含不支持的字符，请使用中文、英文、数字或常用符号'
    }
  }

  // 检查禁用词汇
  for (const word of validation.forbiddenWords) {
    if (word && query.includes(word)) {
      return {
        code: 'FORBIDDEN_WORD',
        message: `地名包含禁用词汇: ${word}`
      }
    }
  }

  return null
}

/**
 * 解析坐标字符串
 */
function parseCoordinate(locationStr: string): Coordinate {
  const [lng, lat] = locationStr.split(',').map(Number)
  return { lng, lat }
}

/**
 * 转换高德API响应为标准格式
 */
function transformAmapResponse(geocode: AmapGeocode): LocationInfo {
  return {
    name: geocode.formatted_address,
    address: geocode.formatted_address,
    coordinate: parseCoordinate(geocode.location),
    adcode: geocode.adcode,
    city: geocode.city,
    district: geocode.district,
    province: geocode.province,
    formatted_address: geocode.formatted_address,
    type: geocode.level
  }
}

/**
 * 发送API请求
 */
async function sendApiRequest(url: string): Promise<AmapGeocodeResponse> {
  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), locationParserConfig.timeout || 5000)

  try {
    const response = await fetch(url, {
      method: 'GET',
      headers: getApiHeaders(),
      signal: controller.signal
    })

    clearTimeout(timeoutId)

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }

    const data = await response.json()

    // 检查高德API响应状态
    if (data.status !== '1') {
      throw new Error(`API Error: ${data.info} (${data.infocode})`)
    }

    return data
  } catch (error) {
    clearTimeout(timeoutId)
    throw error
  }
}

/**
 * 带重试的请求
 */
async function requestWithRetry(url: string, retryCount: number = locationParserConfig.retryCount || 3): Promise<AmapGeocodeResponse> {
  let lastError: Error

  for (let i = 0; i <= retryCount; i++) {
    try {
      return await sendApiRequest(url)
    } catch (error) {
      lastError = error as Error
      
      // 如果不是最后一次尝试，等待后重试
      if (i < retryCount) {
        await new Promise(resolve => setTimeout(resolve, Math.pow(2, i) * 1000))
      }
    }
  }

  throw lastError!
}

/**
 * 解析单个地名
 */
export async function parseLocation(input: LocationInput): Promise<LocationParseResult> {
  const startTime = Date.now()
  
  try {
    // 验证输入
    const validationError = validateLocationInput(input.name)
    if (validationError) {
      return {
        success: false,
        error: validationError.message,
        duration: Date.now() - startTime
      }
    }

    // 检查缓存
    const cacheKey = `${input.name}:${input.city || ''}`
    if (locationParserConfig.cache?.enabled) {
      const cachedResult = cache.get(cacheKey)
      if (cachedResult && cachedResult.length > 0) {
        return {
          success: true,
          location: cachedResult[0],
          cached: true,
          duration: Date.now() - startTime
        }
      }
    }

    // 构建API URL
    const params: Record<string, any> = {
      key: locationParserConfig.apiKey,
      address: input.name,
      output: 'json'
    }

    if (input.city) {
      params.city = input.city
    }

    const url = buildApiUrl('geocode/geo', params)

    // 发送请求
    const response = await requestWithRetry(url)

    if (!response.geocodes || response.geocodes.length === 0) {
      return {
        success: false,
        error: '未找到匹配的地名',
        duration: Date.now() - startTime
      }
    }

    // 转换结果
    const locations = response.geocodes.map(transformAmapResponse)
    
    // 缓存结果
    if (locationParserConfig.cache?.enabled) {
      cache.set(cacheKey, locations)
    }

    return {
      success: true,
      location: locations[0],
      cached: false,
      duration: Date.now() - startTime
    }

  } catch (error) {
    return {
      success: false,
      error: `解析失败: ${error instanceof Error ? error.message : String(error)}`,
      duration: Date.now() - startTime
    }
  }
}

/**
 * 批量解析地名
 */
export async function parseBatchLocations(locations: string[]): Promise<BatchLocationResult> {
  const startTime = Date.now()
  const results: LocationParseResult[] = []
  
  try {
    // 并发解析
    const promises = locations.map(name => 
      parseLocation({ name })
    )
    
    const batchResults = await Promise.all(promises)
    results.push(...batchResults)

    // 统计结果
    const summary = {
      total: results.length,
      successful: results.filter(r => r.success).length,
      failed: results.filter(r => !r.success).length,
      cached: results.filter(r => r.cached).length
    }

    return {
      results,
      summary,
      duration: Date.now() - startTime
    }

  } catch (error) {
    return {
      results,
      summary: {
        total: locations.length,
        successful: 0,
        failed: locations.length,
        cached: 0
      },
      duration: Date.now() - startTime
    }
  }
}

/**
 * 清空缓存
 */
export function clearLocationCache(): void {
  cache.clear()
}

/**
 * 获取缓存统计
 */
export function getCacheStats(): { size: number; maxSize: number; ttl: number } {
  return {
    size: cache.size(),
    maxSize: locationParserConfig.cache?.maxSize || 1000,
    ttl: locationParserConfig.cache?.ttl || 30 * 60 * 1000
  }
}

/**
 * 预加载常用地名
 */
export async function preloadCommonLocations(locations: string[]): Promise<void> {
  const promises = locations.map(name => parseLocation({ name }))
  await Promise.allSettled(promises)
}