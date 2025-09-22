/**
 * 地名解析服务
 */

import axios from 'axios'
import type { ParseResult, BatchParseResult } from '../types/location'

// 创建axios实例
const api = axios.create({
  baseURL: '/api/v1',
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
      const response = await api.post('/parse', { input: name })
      const backendData = response.data
      
      // 转换后端数据格式为前端期望格式
      if (backendData.success && backendData.data?.coordinates?.length > 0) {
        const coord = backendData.data.coordinates[0]
        
        // 验证坐标数据
        const lng = parseFloat(coord.lng)
        const lat = parseFloat(coord.lat)
        
        if (isNaN(lng) || isNaN(lat)) {
          console.error('Invalid coordinates received from backend:', coord)
          return {
            success: false,
            error: '后端返回的坐标数据无效',
            suggestions: backendData.data.suggestions || []
          }
        }
        
        return {
          success: true,
          location: {
            name: coord.name || name,
            coordinates: {
              longitude: lng,
              latitude: lat
            },
            level: coord.level,
            address: coord.name
          },
          suggestions: backendData.data.suggestions || []
        }
      } else {
        return {
          success: false,
          error: backendData.message || '解析失败',
          suggestions: backendData.data?.suggestions || []
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
      const response = await api.post('/parse', { input })
      const backendData = response.data
      
      // 转换批量解析结果格式
      if (backendData.success && backendData.data?.coordinates) {
        const results: ParseResult[] = backendData.data.coordinates.map((coord: any, index: number) => {
          // 验证坐标数据
          const lng = parseFloat(coord.lng)
          const lat = parseFloat(coord.lat)
          
          if (isNaN(lng) || isNaN(lat)) {
            console.error(`Invalid coordinates for location ${index + 1}:`, coord)
            return {
              success: false,
              error: `位置${index + 1}的坐标数据无效`
            }
          }
          
          return {
            success: true,
            location: {
              name: coord.name || `位置${index + 1}`,
              coordinates: {
                longitude: lng,
                latitude: lat
              },
              level: coord.level,
              address: coord.name
            }
          }
        })
        
        const successfulResults = results.filter(r => r.success)
        const failedResults = results.filter(r => !r.success)
        
        return {
          summary: {
            total: results.length,
            successful: successfulResults.length,
            failed: failedResults.length
          },
          results
        }
      } else {
        return {
          summary: {
            total: 0,
            successful: 0,
            failed: 1
          },
          results: [{
            success: false,
            error: backendData.message || '批量解析失败'
          }]
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
        throw new Error(error.response?.data?.error || '服务不可用')
      }
      throw error
    }
  }
}