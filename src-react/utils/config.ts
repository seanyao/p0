/**
 * 应用配置管理
 * 统一管理环境变量和应用配置
 */

import type { LocationParserConfig } from '../types/location'

// 环境变量类型检查
interface EnvVars {
  VITE_AMAP_API_KEY: string
  VITE_AMAP_SECURITY_KEY?: string
  VITE_APP_TITLE?: string
  VITE_APP_VERSION?: string
  NODE_ENV?: string
}

// 获取环境变量
function getEnvVar(key: keyof EnvVars, defaultValue?: string): string {
  const value = import.meta.env[key] || defaultValue
  if (!value && !defaultValue) {
    throw new Error(`Environment variable ${key} is required but not set`)
  }
  return value || defaultValue!
}

// 验证必需的环境变量
function validateEnvVars(): void {
  const requiredVars: (keyof EnvVars)[] = ['VITE_AMAP_API_KEY']
  
  for (const varName of requiredVars) {
    if (!import.meta.env[varName]) {
      throw new Error(`Required environment variable ${varName} is not set`)
    }
  }
}

// 高德地图配置
export const amapConfig = {
  apiKey: getEnvVar('VITE_AMAP_API_KEY'),
  securityKey: getEnvVar('VITE_AMAP_SECURITY_KEY', ''),
  baseUrl: 'https://restapi.amap.com/v3',
  jsApiUrl: 'https://webapi.amap.com/maps',
  version: '2.0'
}

// 地名解析器配置
export const locationParserConfig: LocationParserConfig = {
  apiKey: amapConfig.apiKey,
  baseUrl: `${amapConfig.baseUrl}/geocode/geo`,
  timeout: 5000, // 5秒超时
  retryCount: 3,
  validation: {
    minLength: 1,
    maxLength: 100,
    allowedChars: /^[\u4e00-\u9fa5a-zA-Z0-9\s\-_()（）]+$/,
    forbiddenWords: ['测试', 'test', '']
  },
  cache: {
    enabled: true,
    ttl: 30 * 60 * 1000, // 30分钟
    maxSize: 1000
  }
}

// 应用配置
export const appConfig = {
  title: getEnvVar('VITE_APP_TITLE', '旅游路线图生成器'),
  version: getEnvVar('VITE_APP_VERSION', '1.0.0'),
  isDevelopment: getEnvVar('NODE_ENV', 'development') === 'development',
  isProduction: getEnvVar('NODE_ENV', 'development') === 'production'
}

// 初始化配置
export function initializeConfig(): void {
  try {
    validateEnvVars()
    console.log('✅ Configuration initialized successfully')
    
    if (appConfig.isDevelopment) {
      console.log('🔧 Development mode enabled')
      console.log('📍 Amap API Key:', amapConfig.apiKey.substring(0, 8) + '...')
    }
  } catch (error) {
    console.error('❌ Configuration initialization failed:', error)
    throw error
  }
}

// 获取API请求头
export function getApiHeaders(): Record<string, string> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json'
  }
  
  // 如果有安全密钥，添加到请求头
  if (amapConfig.securityKey) {
    headers['X-Security-Key'] = amapConfig.securityKey
  }
  
  return headers
}

// 构建API URL
export function buildApiUrl(endpoint: string, params: Record<string, any>): string {
  const url = new URL(endpoint)
  
  // 添加API key
  params.key = amapConfig.apiKey
  
  // 添加其他参数
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      url.searchParams.append(key, String(value))
    }
  })
  
  return url.toString()
}

// 导出配置验证函数
export { validateEnvVars }