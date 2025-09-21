/**
 * 旅游路线图工具 - 应用入口
 */

import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import { initializeConfig } from './utils/config'

// 初始化配置
try {
  initializeConfig()
  console.log('✅ 配置初始化成功')
} catch (error) {
  console.error('❌ 配置初始化失败:', error)
}

// 渲染应用
ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)