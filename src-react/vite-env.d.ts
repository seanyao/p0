/// <reference types="vite/client" />

// 扩展 ImportMetaEnv 接口以包含我们的环境变量
interface ImportMetaEnv {
  readonly VITE_AMAP_API_KEY: string
  readonly VITE_AMAP_SECURITY_JS_CODE?: string
  readonly VITE_APP_TITLE: string
  readonly VITE_APP_ENV: 'development' | 'production' | 'test'
  readonly VITE_API_BASE_URL: string
  readonly VITE_ENABLE_CACHE: string
  readonly VITE_CACHE_DURATION: string
  readonly VITE_MAX_CONCURRENT_REQUESTS: string
  readonly VITE_REQUEST_TIMEOUT: string
}

// 扩展 ImportMeta 接口
interface ImportMeta {
  readonly env: ImportMetaEnv
}

// 声明全局变量
declare const __APP_VERSION__: string
declare const __BUILD_TIME__: string