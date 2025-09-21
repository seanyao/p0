/**
 * 视觉渲染服务
 * 负责Canvas渲染和视觉效果处理
 */

import { 
  Point, 
  PathPoint, 
  RouteData, 
  LocationMarker, 
  RouteStyle, 
  DEFAULT_ROUTE_STYLE,
  VisualRenderer,
  StyleConfig,
  RenderOptions,
  COLOR_SCHEMES,
  DEFAULT_STYLE_CONFIG
} from '../types/visual'

import { 
  drawGradientPath, 
  drawSmoothPath, 
  drawCircleWithShadow, 
  drawTextLabel,
  calculateDistance,
  optimizeLabelPositions
} from '../utils/graphics'

import { 
  PerformanceOptimizer, 
  OptimizationOptions,
  PerformanceMetrics,
  performanceOptimizer 
} from '../utils/performance'

export class CanvasVisualRenderer implements VisualRenderer {
  private canvas: HTMLCanvasElement | null = null
  private ctx: CanvasRenderingContext2D | null = null
  private optimizer: PerformanceOptimizer
  private optimizationOptions: OptimizationOptions

  constructor() {
    this.optimizer = performanceOptimizer
    this.optimizationOptions = PerformanceOptimizer.DEFAULT_OPTIONS
  }

  /**
   * 初始化Canvas
   */
  initCanvas(canvas: HTMLCanvasElement): void {
    this.canvas = canvas
    this.ctx = canvas.getContext('2d')
    
    if (!this.ctx) {
      throw new Error('Failed to get 2D context')
    }

    // 设置高DPI支持
    const dpr = window.devicePixelRatio || 1
    const rect = canvas.getBoundingClientRect()
    
    canvas.width = rect.width * dpr
    canvas.height = rect.height * dpr
    
    this.ctx.scale(dpr, dpr)
    canvas.style.width = rect.width + 'px'
    canvas.style.height = rect.height + 'px'
  }

  /**
   * 渲染完整路线图
   */
  async renderRouteMap(routeData: RouteData, style: StyleConfig, options?: RenderOptions): Promise<HTMLCanvasElement> {
    if (!this.canvas || !this.ctx) {
      throw new Error('Canvas not initialized')
    }

    const startTime = performance.now()
    
    // 开始性能监控
    this.optimizer.startPerformanceMonitoring()
    
    // 清空画布
    this.clearCanvas()
    
    // 渲染底图
    this.renderBaseMap(routeData.bounds, this.canvas)
    
    // 性能优化：路径简化和LOD
    let optimizedPath = routeData.path
    if (this.optimizationOptions.enableLOD) {
      optimizedPath = this.optimizer.applyLOD(routeData.path, {
        width: this.canvas.width,
        height: this.canvas.height
      })
    }
    
    if (this.optimizationOptions.maxPoints && optimizedPath.length > this.optimizationOptions.maxPoints) {
      optimizedPath = this.optimizer.simplifyPath(
        optimizedPath, 
        this.optimizationOptions.simplificationTolerance
      )
    }
    
    // 渲染路线
    const colorScheme = COLOR_SCHEMES[style.colorScheme] || COLOR_SCHEMES['blue']
    this.renderRoute({ ...routeData, path: optimizedPath }, {
      pathColor: colorScheme.primary,
      pathWidth: style.lineWidth,
      fontSize: style.fontSize
    })
    
    // 记录性能指标
    this.optimizer.recordRenderTime(startTime)
    this.optimizer.recordFrame()

    return this.canvas
  }

  /**
   * 清空画布
   */
  clearCanvas(): void {
    if (!this.ctx || !this.canvas) return
    
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height)
  }

  /**
   * 渲染底图
   */
  private renderBaseMap(bounds: any, canvas: HTMLCanvasElement): void {
    if (!this.ctx) return
    
    // 渲染简单的网格背景
    this.ctx.strokeStyle = '#f0f0f0'
    this.ctx.lineWidth = 1
    
    const gridSize = 50
    for (let x = 0; x < canvas.width; x += gridSize) {
      this.ctx.beginPath()
      this.ctx.moveTo(x, 0)
      this.ctx.lineTo(x, canvas.height)
      this.ctx.stroke()
    }
    
    for (let y = 0; y < canvas.height; y += gridSize) {
      this.ctx.beginPath()
      this.ctx.moveTo(0, y)
      this.ctx.lineTo(canvas.width, y)
      this.ctx.stroke()
    }
  }

  /**
   * 渲染路线
   */
  private renderRoute(routeData: RouteData, style: any): void {
    if (!this.ctx || !routeData.path.length) return
    
    // 渲染路径
    this.renderRoutePath(routeData.path, {
      pathColor: style.pathColor,
      pathWidth: style.pathWidth,
      markerColor: '#ff4444',
      labelColor: '#333333'
    })
    
    // 渲染地点标记
    const locationMarkers: LocationMarker[] = routeData.locations.map(location => ({
      position: { x: location.coordinates.lng * 100, y: location.coordinates.lat * 100 },
      label: location.name,
      type: 'location' as const,
      style: {
        fillColor: '#ff4444',
        strokeColor: style.pathColor,
        radius: 8
      }
    }))
    
    this.renderLocationMarkers(locationMarkers, {
      pathColor: style.pathColor,
      pathWidth: style.pathWidth,
      markerColor: '#ff4444',
      labelColor: '#333333'
    })
  }

  /**
   * 渲染路线路径
   */
  private renderRoutePath(path: PathPoint[], style: RouteStyle): void {
    if (!this.ctx || path.length < 2) return
    
    // 转换坐标
    const points = path.map(p => ({ x: p.x * 100, y: p.y * 100 }))
    
    // 绘制平滑路径
    drawSmoothPath(this.ctx, points, {
      strokeStyle: style.pathColor,
      lineWidth: style.pathWidth,
      lineCap: 'round',
      lineJoin: 'round'
    })
  }

  /**
   * 渲染地点标记
   */
  private renderLocationMarkers(markers: LocationMarker[], style: RouteStyle): void {
    if (!this.ctx) return
    
    markers.forEach(marker => {
      // 绘制标记圆圈
      drawCircleWithShadow(this.ctx, marker.position, marker.style?.radius || 8, {
        fillStyle: marker.style?.fillColor || style.markerColor,
        strokeStyle: marker.style?.strokeColor || style.pathColor,
        shadowColor: 'rgba(0,0,0,0.3)',
        shadowBlur: 4,
        shadowOffsetX: 2,
        shadowOffsetY: 2
      })
      
      // 绘制标签
      if (marker.label) {
        drawTextLabel(this.ctx, marker.label, {
          x: marker.position.x,
          y: marker.position.y - 20
        }, {
          font: '12px Arial',
          fillStyle: style.labelColor,
          textAlign: 'center',
          backgroundColor: 'rgba(255,255,255,0.8)',
          padding: 4,
          borderRadius: 4
        })
      }
    })
  }

  /**
   * 设置优化选项
   */
  setOptimizationOptions(options: Partial<OptimizationOptions>): void {
    this.optimizationOptions = { ...this.optimizationOptions, ...options }
  }

  /**
   * 获取性能指标
   */
  getPerformanceMetrics(): PerformanceMetrics | null {
    if (!this.canvas) return null
    
    return this.optimizer.getPerformanceMetrics(
      this.canvas, 
      0 // 元素数量需要根据实际渲染内容计算
    )
  }

  /**
   * 自动优化配置
   */
  autoOptimize(): void {
    const metrics = this.getPerformanceMetrics()
    if (metrics) {
      const optimizedOptions = this.optimizer.getOptimizedOptions(metrics)
      this.setOptimizationOptions(optimizedOptions)
    }
  }

  /**
   * 清理缓存
   */
  clearCache(): void {
    this.optimizer.clearCache()
  }

  /**
   * 重置性能统计
   */
  resetPerformanceStats(): void {
    this.optimizer.resetStats()
  }

  /**
   * 获取性能建议
   */
  getPerformanceRecommendations(): string[] {
    const metrics = this.getPerformanceMetrics()
    if (!metrics) return []
    
    return this.optimizer.getPerformanceRecommendations(metrics)
  }
}

// 导出单例实例
export const visualRenderer = new CanvasVisualRenderer()