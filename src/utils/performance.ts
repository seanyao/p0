/**
 * 性能优化工具
 * 提供Canvas渲染性能优化和监控功能
 */

import { Point, PathPoint } from '../types/visual'

export interface PerformanceMetrics {
  renderTime: number
  frameRate: number
  memoryUsage?: number
  canvasSize: { width: number; height: number }
  elementCount: number
}

export interface OptimizationOptions {
  enableLOD: boolean          // 启用细节层次优化
  maxPoints: number           // 最大点数限制
  simplificationTolerance: number  // 路径简化容差
  enableCaching: boolean      // 启用缓存
  batchSize: number          // 批处理大小
}

export class PerformanceOptimizer {
  private renderCache: Map<string, ImageData> = new Map()
  private lastFrameTime: number = 0
  private frameCount: number = 0
  private fpsHistory: number[] = []
  private renderTimes: number[] = []

  /**
   * 默认优化选项
   */
  static readonly DEFAULT_OPTIONS: OptimizationOptions = {
    enableLOD: true,
    maxPoints: 1000,
    simplificationTolerance: 2.0,
    enableCaching: true,
    batchSize: 50
  }

  /**
   * 路径简化 - Douglas-Peucker算法
   */
  simplifyPath(points: PathPoint[], tolerance: number = 2.0): PathPoint[] {
    if (points.length <= 2) return points

    return this.douglasPeucker(points, tolerance)
  }

  /**
   * Douglas-Peucker路径简化算法
   */
  private douglasPeucker(points: PathPoint[], tolerance: number): PathPoint[] {
    if (points.length <= 2) return points

    let maxDistance = 0
    let maxIndex = 0
    const end = points.length - 1

    // 找到距离起点和终点连线最远的点
    for (let i = 1; i < end; i++) {
      const distance = this.pointToLineDistance(points[i], points[0], points[end])
      if (distance > maxDistance) {
        maxDistance = distance
        maxIndex = i
      }
    }

    // 如果最大距离大于容差，递归简化
    if (maxDistance > tolerance) {
      const leftPart = this.douglasPeucker(points.slice(0, maxIndex + 1), tolerance)
      const rightPart = this.douglasPeucker(points.slice(maxIndex), tolerance)
      
      // 合并结果，去除重复点
      return [...leftPart.slice(0, -1), ...rightPart]
    }

    // 否则返回起点和终点
    return [points[0], points[end]]
  }

  /**
   * 计算点到直线的距离
   */
  private pointToLineDistance(point: Point, lineStart: Point, lineEnd: Point): number {
    const A = point.x - lineStart.x
    const B = point.y - lineStart.y
    const C = lineEnd.x - lineStart.x
    const D = lineEnd.y - lineStart.y

    const dot = A * C + B * D
    const lenSq = C * C + D * D
    
    if (lenSq === 0) return Math.sqrt(A * A + B * B)
    
    let param = dot / lenSq
    
    let xx: number, yy: number
    
    if (param < 0) {
      xx = lineStart.x
      yy = lineStart.y
    } else if (param > 1) {
      xx = lineEnd.x
      yy = lineEnd.y
    } else {
      xx = lineStart.x + param * C
      yy = lineStart.y + param * D
    }
    
    const dx = point.x - xx
    const dy = point.y - yy
    return Math.sqrt(dx * dx + dy * dy)
  }

  /**
   * 细节层次优化 (Level of Detail)
   */
  applyLOD(points: PathPoint[], canvasSize: { width: number; height: number }): PathPoint[] {
    const totalPixels = canvasSize.width * canvasSize.height
    const complexity = points.length
    
    // 根据画布大小和复杂度动态调整简化程度
    let tolerance = 1.0
    
    if (totalPixels < 500000) { // 小画布
      tolerance = complexity > 200 ? 3.0 : 1.5
    } else if (totalPixels < 2000000) { // 中等画布
      tolerance = complexity > 500 ? 2.5 : 1.0
    } else { // 大画布
      tolerance = complexity > 1000 ? 2.0 : 0.5
    }
    
    return this.simplifyPath(points, tolerance)
  }

  /**
   * 批量渲染优化
   */
  batchRender<T>(
    items: T[],
    renderFunction: (batch: T[]) => void,
    batchSize: number = 50
  ): void {
    for (let i = 0; i < items.length; i += batchSize) {
      const batch = items.slice(i, i + batchSize)
      renderFunction(batch)
      
      // 在批次之间让出控制权，避免阻塞UI
      if (i + batchSize < items.length) {
        setTimeout(() => {}, 0)
      }
    }
  }

  /**
   * Canvas缓存管理
   */
  cacheCanvas(key: string, canvas: HTMLCanvasElement): void {
    const ctx = canvas.getContext('2d')
    if (ctx) {
      const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height)
      this.renderCache.set(key, imageData)
    }
  }

  /**
   * 从缓存恢复Canvas
   */
  restoreFromCache(key: string, canvas: HTMLCanvasElement): boolean {
    const imageData = this.renderCache.get(key)
    if (imageData) {
      const ctx = canvas.getContext('2d')
      if (ctx) {
        ctx.putImageData(imageData, 0, 0)
        return true
      }
    }
    return false
  }

  /**
   * 清理缓存
   */
  clearCache(key?: string): void {
    if (key) {
      this.renderCache.delete(key)
    } else {
      this.renderCache.clear()
    }
  }

  /**
   * 开始性能监控
   */
  startPerformanceMonitoring(): void {
    this.lastFrameTime = performance.now()
    this.frameCount = 0
    this.fpsHistory = []
    this.renderTimes = []
  }

  /**
   * 记录帧渲染
   */
  recordFrame(): void {
    const currentTime = performance.now()
    const deltaTime = currentTime - this.lastFrameTime
    
    if (deltaTime > 0) {
      const fps = 1000 / deltaTime
      this.fpsHistory.push(fps)
      
      // 保持历史记录在合理范围内
      if (this.fpsHistory.length > 60) {
        this.fpsHistory.shift()
      }
    }
    
    this.lastFrameTime = currentTime
    this.frameCount++
  }

  /**
   * 记录渲染时间
   */
  recordRenderTime(startTime: number): void {
    const renderTime = performance.now() - startTime
    this.renderTimes.push(renderTime)
    
    // 保持历史记录在合理范围内
    if (this.renderTimes.length > 100) {
      this.renderTimes.shift()
    }
  }

  /**
   * 获取性能指标
   */
  getPerformanceMetrics(canvas: HTMLCanvasElement, elementCount: number): PerformanceMetrics {
    const avgFps = this.fpsHistory.length > 0 
      ? this.fpsHistory.reduce((a, b) => a + b, 0) / this.fpsHistory.length 
      : 0
    
    const avgRenderTime = this.renderTimes.length > 0
      ? this.renderTimes.reduce((a, b) => a + b, 0) / this.renderTimes.length
      : 0

    return {
      renderTime: avgRenderTime,
      frameRate: avgFps,
      memoryUsage: this.getMemoryUsage(),
      canvasSize: { width: canvas.width, height: canvas.height },
      elementCount
    }
  }

  /**
   * 获取内存使用情况
   */
  private getMemoryUsage(): number | undefined {
    if ('memory' in performance) {
      return (performance as any).memory.usedJSHeapSize / 1024 / 1024 // MB
    }
    return undefined
  }

  /**
   * 性能建议
   */
  getPerformanceRecommendations(metrics: PerformanceMetrics): string[] {
    const recommendations: string[] = []
    
    if (metrics.frameRate < 30) {
      recommendations.push('帧率较低，建议减少渲染元素数量或启用LOD优化')
    }
    
    if (metrics.renderTime > 16) {
      recommendations.push('渲染时间过长，建议使用批量渲染或缓存优化')
    }
    
    if (metrics.elementCount > 1000) {
      recommendations.push('元素数量过多，建议启用路径简化')
    }
    
    if (metrics.memoryUsage && metrics.memoryUsage > 100) {
      recommendations.push('内存使用较高，建议清理缓存或减少数据量')
    }
    
    const canvasPixels = metrics.canvasSize.width * metrics.canvasSize.height
    if (canvasPixels > 4000000) { // 2000x2000
      recommendations.push('Canvas尺寸较大，建议考虑分块渲染')
    }
    
    return recommendations
  }

  /**
   * 自动优化配置
   */
  getOptimizedOptions(metrics: PerformanceMetrics): OptimizationOptions {
    const options = { ...PerformanceOptimizer.DEFAULT_OPTIONS }
    
    // 根据性能指标调整优化选项
    if (metrics.frameRate < 30 || metrics.renderTime > 16) {
      options.enableLOD = true
      options.maxPoints = Math.min(500, options.maxPoints)
      options.simplificationTolerance = Math.max(3.0, options.simplificationTolerance)
      options.batchSize = Math.min(25, options.batchSize)
    }
    
    if (metrics.elementCount > 1000) {
      options.maxPoints = Math.min(300, options.maxPoints)
      options.simplificationTolerance = 4.0
    }
    
    if (metrics.memoryUsage && metrics.memoryUsage > 100) {
      options.enableCaching = false // 禁用缓存以节省内存
    }
    
    return options
  }

  /**
   * 视口裁剪优化
   */
  cullOutsideViewport(
    points: PathPoint[], 
    viewport: { x: number; y: number; width: number; height: number },
    margin: number = 50
  ): PathPoint[] {
    const bounds = {
      left: viewport.x - margin,
      right: viewport.x + viewport.width + margin,
      top: viewport.y - margin,
      bottom: viewport.y + viewport.height + margin
    }
    
    return points.filter(point => 
      point.x >= bounds.left && 
      point.x <= bounds.right && 
      point.y >= bounds.top && 
      point.y <= bounds.bottom
    )
  }

  /**
   * 重置性能统计
   */
  resetStats(): void {
    this.frameCount = 0
    this.fpsHistory = []
    this.renderTimes = []
    this.lastFrameTime = performance.now()
  }
}

/**
 * 渲染性能装饰器
 */
export function measurePerformance(optimizer: PerformanceOptimizer) {
  return function (target: any, propertyName: string, descriptor: PropertyDescriptor) {
    const method = descriptor.value
    
    descriptor.value = function (...args: any[]) {
      const startTime = performance.now()
      const result = method.apply(this, args)
      optimizer.recordRenderTime(startTime)
      optimizer.recordFrame()
      return result
    }
  }
}

// 导出单例实例
export const performanceOptimizer = new PerformanceOptimizer()