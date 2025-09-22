/**
 * 地名解析服务
 */

import axios from 'axios'
import type { ParseResult, BatchParseResult } from '../types/location'

// 创建axios实例
const api = axios.create({
  baseURL: '/api/v1/ai',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    console.log('发送请求:', config.method?.toUpperCase(), config.url)
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    console.log('收到响应:', response.status, response.data)
    return response
  },
  (error) => {
    console.error('请求错误:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

export const locationService = {
  // 解析单个地名
  async parseLocation(name: string): Promise<ParseResult> {
    try {
      const response = await api.post('/generate-route', { user_input: name })
      const backendData = response.data
      
      // 转换后端数据格式为前端期望格式
      if (backendData.success && backendData.locations?.length > 0) {
        const location = backendData.locations[0]
        
        // 验证坐标数据
        const lng = parseFloat(location.coordinates[0])
        const lat = parseFloat(location.coordinates[1])
        
        if (isNaN(lng) || isNaN(lat)) {
          console.error('Invalid coordinates received from backend:', location)
          return {
            success: false,
            error: '后端返回的坐标数据无效',
            suggestions: []
          }
        }
        
        return {
          success: true,
          location: {
            name: location.name || name,
            coordinates: {
              longitude: lng,
              latitude: lat
            },
            level: location.type,
            address: location.display_name
          },
          suggestions: []
        }
      } else {
        return {
          success: false,
          error: backendData.message || '解析失败',
          suggestions: []
        }
      }
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(error.response?.data?.error || '网络请求失败')
      }
      throw error
    }
  },

  // 批量解析地名
  async parseBatch(input: string): Promise<BatchParseResult> {
    try {
      const response = await api.post('/generate-route', { user_input: input })
      const backendData = response.data
      
      // 转换批量解析结果格式
      if (backendData.success && backendData.locations) {
        const results: ParseResult[] = backendData.locations.map((location: any, index: number) => {
          const lng = parseFloat(location.coordinates[0])
          const lat = parseFloat(location.coordinates[1])
          
          if (isNaN(lng) || isNaN(lat)) {
            return {
              success: false,
              error: `第${index + 1}个地点坐标无效`,
              suggestions: []
            }
          }
          
          return {
            success: true,
            location: {
              name: location.name,
              coordinates: {
                longitude: lng,
                latitude: lat
              },
              level: location.type,
              address: location.display_name
            },
            suggestions: []
          }
        })
        
        const successful = results.filter(r => r.success).length
        const failed = results.length - successful
        
        return {
          summary: {
            total: results.length,
            successful,
            failed
          },
          results
        }
      } else {
        return {
          summary: {
            total: 0,
            successful: 0,
            failed: 0
          },
          results: []
        }
      }
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(error.response?.data?.error || '网络请求失败')
      }
      throw error
    }
  },

  // 健康检查
  async healthCheck() {
    try {
      const response = await api.get('/health')
      return response.data
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(error.response?.data?.error || '健康检查失败')
      }
      throw error
    }
  }
}