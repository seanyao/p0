const { defineConfig } = require('@vue/cli-service')

module.exports = defineConfig({
  transpileDependencies: true,
  
  // 开发服务器配置
  devServer: {
    port: 3000,
    host: '0.0.0.0',
    open: true,
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
        pathRewrite: {
          '^/api/amap': ''
        },
        secure: true,
      },
    },
  },
  
  // 构建配置
  configureWebpack: {
    resolve: {
      alias: {
        '@': require('path').resolve(__dirname, 'src'),
        '@components': require('path').resolve(__dirname, 'src/components'),
        '@services': require('path').resolve(__dirname, 'src/services'),
        '@utils': require('path').resolve(__dirname, 'src/utils'),
        '@types': require('path').resolve(__dirname, 'src/types'),
        '@hooks': require('path').resolve(__dirname, 'src/composables'),
      },
    },
  },
  
  // CSS配置
  css: {
    sourceMap: true,
  },
  
  // 生产环境配置
  productionSourceMap: true,
})