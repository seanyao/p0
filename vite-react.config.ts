import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  
  // 路径解析
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
      '@components': resolve(__dirname, 'src/components'),
      '@services': resolve(__dirname, 'src/services'),
      '@utils': resolve(__dirname, 'src/utils'),
      '@types': resolve(__dirname, 'src/types'),
      '@hooks': resolve(__dirname, 'src/hooks'),
    },
  },
  
  // 开发服务器配置
  server: {
    port: 3000,
    host: true,
    open: true,
    cors: true,
    proxy: {
      // 代理高德地图API请求，避免CORS问题
      '/api/amap': {
        target: 'https://restapi.amap.com',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/amap/, ''),
        secure: true,
      },
    },
  },
  
  // 构建配置
  build: {
    outDir: 'dist',
    sourcemap: true,
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true,
      },
    },
    rollupOptions: {
      output: {
        manualChunks: {
          // 将React相关库分离到单独的chunk
          react: ['react', 'react-dom'],
        },
      },
    },
    // 设置chunk大小警告限制
    chunkSizeWarningLimit: 1000,
  },
  
  // 环境变量配置
  envPrefix: 'VITE_',
  
  // CSS配置
  css: {
    devSourcemap: true,
  },
  
  // 优化配置
  optimizeDeps: {
    include: ['react', 'react-dom'],
    exclude: [],
  },
  
  // 预览服务器配置
  preview: {
    port: 4173,
    host: true,
    cors: true,
  },
  
  // 全局常量定义
  define: {
    __APP_VERSION__: JSON.stringify('1.0.0'),
    __BUILD_TIME__: JSON.stringify(new Date().toISOString()),
  },
})