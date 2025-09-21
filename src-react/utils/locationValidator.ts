/**
 * 地名输入验证工具
 * 提供各种地名输入的验证和处理功能
 */

import type { LocationParseError } from '../types/location'

// 常见地名模式
const LOCATION_PATTERNS = {
  // 中国城市名称
  chineseCity: /^[\u4e00-\u9fa5]{2,10}[市县区]?$/,
  // 省份名称
  province: /^[\u4e00-\u9fa5]{2,10}[省市区]$/,
  // 景点名称
  attraction: /^[\u4e00-\u9fa5a-zA-Z0-9\s]{2,20}$/,
  // 地址格式
  address: /^[\u4e00-\u9fa5a-zA-Z0-9\s\-_()（）]{5,100}$/
}

// 常见地名后缀
const LOCATION_SUFFIXES = [
  '市', '县', '区', '镇', '乡', '村', '街道', '路', '街', '巷',
  '省', '自治区', '特别行政区', '直辖市'
]

// 热门城市列表
const POPULAR_CITIES = [
  '北京', '上海', '广州', '深圳', '杭州', '南京', '苏州', '成都',
  '重庆', '武汉', '西安', '天津', '青岛', '大连', '厦门', '宁波',
  '无锡', '长沙', '郑州', '佛山', '福州', '哈尔滨', '济南', '昆明'
]

// 常见错误输入
const COMMON_TYPOS: Record<string, string> = {
  '北京市': '北京',
  '上海市': '上海',
  '广州市': '广州',
  '深圳市': '深圳',
  '杭州市': '杭州',
  '南京市': '南京',
  '苏州市': '苏州',
  '成都市': '成都'
}

/**
 * 基础输入验证
 */
export function validateBasicInput(input: string): LocationParseError | null {
  // 去除首尾空格
  const trimmed = input.trim()
  
  if (!trimmed) {
    return {
      code: 'EMPTY_INPUT',
      message: '请输入地名'
    }
  }

  if (trimmed.length < 2) {
    return {
      code: 'TOO_SHORT',
      message: '地名至少需要2个字符'
    }
  }

  if (trimmed.length > 50) {
    return {
      code: 'TOO_LONG',
      message: '地名不能超过50个字符'
    }
  }

  return null
}

/**
 * 检查是否包含特殊字符
 */
export function hasInvalidCharacters(input: string): boolean {
  // 允许中文、英文、数字、空格和常用标点
  const validChars = /^[\u4e00-\u9fa5a-zA-Z0-9\s\-_()（）·]+$/
  return !validChars.test(input)
}

/**
 * 检查是否为有效的地名格式
 */
export function isValidLocationFormat(input: string): boolean {
  const trimmed = input.trim()
  
  // 检查是否匹配任何地名模式
  return Object.values(LOCATION_PATTERNS).some(pattern => pattern.test(trimmed))
}

/**
 * 自动修正常见输入错误
 */
export function autoCorrectInput(input: string): string {
  let corrected = input.trim()
  
  // 修正常见错误
  for (const [typo, correct] of Object.entries(COMMON_TYPOS)) {
    if (corrected === typo) {
      corrected = correct
      break
    }
  }
  
  // 移除多余的后缀
  for (const suffix of LOCATION_SUFFIXES) {
    if (corrected.endsWith(suffix + suffix)) {
      corrected = corrected.slice(0, -suffix.length)
      break
    }
  }
  
  return corrected
}

/**
 * 提取地名关键词
 */
export function extractLocationKeywords(input: string): string[] {
  const keywords: string[] = []
  const trimmed = input.trim()
  
  // 按空格、逗号、顿号分割
  const parts = trimmed.split(/[\s,，、]+/).filter(part => part.length > 0)
  
  for (const part of parts) {
    const corrected = autoCorrectInput(part)
    if (corrected.length >= 2) {
      keywords.push(corrected)
    }
  }
  
  return keywords
}

/**
 * 检查是否为热门城市
 */
export function isPopularCity(input: string): boolean {
  const normalized = autoCorrectInput(input)
  return POPULAR_CITIES.includes(normalized)
}

/**
 * 生成输入建议
 */
export function generateInputSuggestions(input: string): string[] {
  const suggestions: string[] = []
  const normalized = input.toLowerCase().trim()
  
  if (normalized.length < 2) {
    return POPULAR_CITIES.slice(0, 8)
  }
  
  // 基于输入匹配热门城市
  for (const city of POPULAR_CITIES) {
    if (city.includes(normalized) || normalized.includes(city)) {
      suggestions.push(city)
    }
  }
  
  // 如果没有匹配，返回热门城市
  if (suggestions.length === 0) {
    return POPULAR_CITIES.slice(0, 5)
  }
  
  return suggestions.slice(0, 8)
}

/**
 * 验证批量输入
 */
export function validateBatchInput(input: string): {
  isValid: boolean
  locations: string[]
  errors: string[]
} {
  const locations: string[] = []
  const errors: string[] = []
  
  // 提取所有地名
  const keywords = extractLocationKeywords(input)
  
  if (keywords.length === 0) {
    errors.push('未找到有效的地名')
    return { isValid: false, locations, errors }
  }
  
  if (keywords.length > 20) {
    errors.push('一次最多只能输入20个地名')
    return { isValid: false, locations, errors }
  }
  
  // 验证每个地名
  for (const keyword of keywords) {
    const validation = validateBasicInput(keyword)
    if (validation) {
      errors.push(`"${keyword}": ${validation.message}`)
    } else if (hasInvalidCharacters(keyword)) {
      errors.push(`"${keyword}": 包含无效字符`)
    } else {
      locations.push(keyword)
    }
  }
  
  return {
    isValid: errors.length === 0,
    locations,
    errors
  }
}

/**
 * 格式化地名显示
 */
export function formatLocationDisplay(location: string): string {
  const corrected = autoCorrectInput(location)
  
  // 如果是热门城市，可以添加标识
  if (isPopularCity(corrected)) {
    return `🔥 ${corrected}`
  }
  
  return corrected
}

/**
 * 计算输入相似度
 */
export function calculateSimilarity(input1: string, input2: string): number {
  const s1 = input1.toLowerCase().trim()
  const s2 = input2.toLowerCase().trim()
  
  if (s1 === s2) return 1
  
  const maxLength = Math.max(s1.length, s2.length)
  if (maxLength === 0) return 1
  
  // 简单的编辑距离算法
  const distance = levenshteinDistance(s1, s2)
  return 1 - distance / maxLength
}

/**
 * 计算编辑距离
 */
function levenshteinDistance(str1: string, str2: string): number {
  const matrix: number[][] = []
  
  for (let i = 0; i <= str2.length; i++) {
    matrix[i] = [i]
  }
  
  for (let j = 0; j <= str1.length; j++) {
    matrix[0][j] = j
  }
  
  for (let i = 1; i <= str2.length; i++) {
    for (let j = 1; j <= str1.length; j++) {
      if (str2.charAt(i - 1) === str1.charAt(j - 1)) {
        matrix[i][j] = matrix[i - 1][j - 1]
      } else {
        matrix[i][j] = Math.min(
          matrix[i - 1][j - 1] + 1, // 替换
          matrix[i][j - 1] + 1,     // 插入
          matrix[i - 1][j] + 1      // 删除
        )
      }
    }
  }
  
  return matrix[str2.length][str1.length]
}

/**
 * 导出常用数据
 */
export {
  POPULAR_CITIES,
  LOCATION_PATTERNS,
  LOCATION_SUFFIXES
}