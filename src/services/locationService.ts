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
      return response.data
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
      return response.data
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