import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  
  // 路径解析
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src-vue'),
      '@components': resolve(__dirname, 'src-vue/components'),
      '@services': resolve(__dirname, 'src-vue/services'),
      '@utils': resolve(__dirname, 'src-vue/utils'),
      '@types': resolve(__dirname, 'src-vue/types'),
      '@composables': resolve(__dirname, 'src-vue/composables'),
      '@views': resolve(__dirname, 'src-vue/views'),
    },
  },
  
  // 开发服务器配置
  server: {
    port: 3001,
    host: true,
    open: true,
    cors: true,
    proxy: {
      // 代理后端API请求
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
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
    outDir: 'dist-vue',
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
          vue: ['vue', 'vue-router', 'pinia'],
          vendor: ['axios', '@vueuse/core'],
        },
      },
    },
    chunkSizeWarningLimit: 1000,
  },
  
  // 环境变量前缀
  envPrefix: 'VITE_',
  
  // CSS配置
  css: {
    devSourcemap: true,
  },
  
  // 依赖优化
  optimizeDeps: {
    include: ['vue', 'vue-router', 'pinia', 'axios'],
    exclude: [],
  },
  
  // 预览配置
  preview: {
    port: 4174,
    host: true,
    cors: true,
  },
  
  // 定义全局常量
  define: {
    __APP_VERSION__: JSON.stringify('1.0.0'),
    __BUILD_TIME__: JSON.stringify(new Date().toISOString()),
  },
})