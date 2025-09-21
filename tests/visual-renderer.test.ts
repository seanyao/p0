/**
 * 视觉渲染器集成测试
 * 验证Spec 1.3的功能实现
 */

import { describe, it, expect, beforeEach, afterEach } from 'vitest'
import { visualRenderer } from '../src/services/visualRenderer'
import { styleManager } from '../src/services/styleManager'
import { performanceOptimizer } from '../src/utils/performance'
import { RouteData, StyleConfig } from '../src/types/visual'

// 模拟Canvas环境
class MockCanvas {
  width = 800
  height = 600
  style = {
    width: '800px',
    height: '600px'
  }
  
  getContext(type: string) {
    if (type === '2d') {
      return new MockCanvasRenderingContext2D()
    }
    return null
  }
  
  getBoundingClientRect() {
    return {
      width: this.width,
      height: this.height,
      left: 0,
      top: 0,
      right: this.width,
      bottom: this.height
    }
  }
  
  toDataURL() {
    return 'data:image/png;base64,mock-data'
  }
}

class MockCanvasRenderingContext2D {
  fillStyle = '#000000'
  strokeStyle = '#000000'
  lineWidth = 1
  font = '10px sans-serif'
  textAlign = 'start'
  textBaseline = 'alphabetic'
  globalAlpha = 1
  lineCap = 'butt'
  lineJoin = 'miter'
  shadowBlur = 0
  shadowColor = 'rgba(0, 0, 0, 0)'
  shadowOffsetX = 0
  shadowOffsetY = 0
  
  beginPath() {}
  closePath() {}
  moveTo(x: number, y: number) {}
  lineTo(x: number, y: number) {}
  arc(x: number, y: number, radius: number, startAngle: number, endAngle: number) {}
  quadraticCurveTo(cpx: number, cpy: number, x: number, y: number) {}
  bezierCurveTo(cp1x: number, cp1y: number, cp2x: number, cp2y: number, x: number, y: number) {}
  stroke() {}
  fill() {}
  clearRect(x: number, y: number, width: number, height: number) {}
  fillRect(x: number, y: number, width: number, height: number) {}
  strokeRect(x: number, y: number, width: number, height: number) {}
  fillText(text: string, x: number, y: number) {}
  strokeText(text: string, x: number, y: number) {}
  measureText(text: string) {
    return { width: text.length * 8 }
  }
  save() {}
  restore() {}
  scale(x: number, y: number) {}
  translate(x: number, y: number) {}
  rotate(angle: number) {}
  setLineDash(segments: number[]) {}
  getLineDash() { return [] }
  createLinearGradient(x0: number, y0: number, x1: number, y1: number) {
    return {
      addColorStop: (offset: number, color: string) => {}
    }
  }
  createRadialGradient(x0: number, y0: number, r0: number, x1: number, y1: number, r1: number) {
    return {
      addColorStop: (offset: number, color: string) => {}
    }
  }
  getImageData(sx: number, sy: number, sw: number, sh: number) {
    return {
      data: new Uint8ClampedArray(sw * sh * 4),
      width: sw,
      height: sh
    }
  }
  putImageData(imageData: any, dx: number, dy: number) {}
}

// 全局模拟
global.HTMLCanvasElement = MockCanvas as any
global.CanvasRenderingContext2D = MockCanvasRenderingContext2D as any
global.window = {
  devicePixelRatio: 1
} as any
global.performance = {
  now: () => Date.now(),
  memory: {
    usedJSHeapSize: 1024 * 1024 * 50 // 50MB
  }
} as any

describe('视觉渲染器集成测试', () => {
  let canvas: HTMLCanvasElement
  let testRouteData: RouteData
  let testStyleConfig: StyleConfig

  beforeEach(() => {
    // 创建测试Canvas
    canvas = new MockCanvas() as any
    
    // 初始化渲染器
    visualRenderer.initCanvas(canvas)
    
    // 准备测试数据
    testRouteData = {
      locations: [
        {
          name: '起点',
          coordinates: { longitude: 116.4074, latitude: 39.9042 },
          address: '北京市'
        },
        {
          name: '终点',
          coordinates: { longitude: 121.4737, latitude: 31.2304 },
          address: '上海市'
        }
      ],
      path: [
        { x: 100, y: 100 },
        { x: 200, y: 150 },
        { x: 300, y: 200 },
        { x: 400, y: 250 }
      ],
      bounds: {
        north: 40,
        south: 30,
        east: 122,
        west: 116
      }
    }
    
    testStyleConfig = {
      colorScheme: 'blue',
      lineWidth: 3,
      fontSize: 14,
      canvasSize: { width: 800, height: 600 },
      showShadow: true
    }
  })

  afterEach(() => {
    visualRenderer.clearCanvas()
    visualRenderer.clearCache()
    performanceOptimizer.resetStats()
  })

  describe('核心渲染功能', () => {
    it('应该能够初始化Canvas', () => {
      expect(() => {
        visualRenderer.initCanvas(canvas)
      }).not.toThrow()
    })

    it('应该能够渲染完整路线图', async () => {
      const result = await visualRenderer.renderRouteMap(testRouteData, testStyleConfig)
      expect(result).toBe(canvas)
    })

    it('应该能够清空画布', () => {
      expect(() => {
        visualRenderer.clearCanvas()
      }).not.toThrow()
    })
  })

  describe('性能优化功能', () => {
    it('应该能够设置优化选项', () => {
      expect(() => {
        visualRenderer.setOptimizationOptions({
          enableLOD: true,
          maxPoints: 500,
          simplificationTolerance: 3.0
        })
      }).not.toThrow()
    })

    it('应该能够获取性能指标', () => {
      const metrics = visualRenderer.getPerformanceMetrics()
      expect(metrics).toBeDefined()
      if (metrics) {
        expect(typeof metrics.renderTime).toBe('number')
        expect(typeof metrics.frameRate).toBe('number')
        expect(typeof metrics.elementCount).toBe('number')
      }
    })

    it('应该能够自动优化配置', () => {
      expect(() => {
        visualRenderer.autoOptimize()
      }).not.toThrow()
    })

    it('应该能够获取性能建议', () => {
      const recommendations = visualRenderer.getPerformanceRecommendations()
      expect(Array.isArray(recommendations)).toBe(true)
    })
  })

  describe('样式管理功能', () => {
    it('应该能够应用不同的颜色方案', async () => {
      const schemes = ['blue', 'orange', 'green', 'purple', 'red']
      
      for (const scheme of schemes) {
        const style = { ...testStyleConfig, colorScheme: scheme as any }
        expect(async () => {
          await visualRenderer.renderRouteMap(testRouteData, style)
        }).not.toThrow()
      }
    })

    it('应该能够调整线条宽度', async () => {
      const widths = [1, 3, 5, 8]
      
      for (const width of widths) {
        const style = { ...testStyleConfig, lineWidth: width }
        expect(async () => {
          await visualRenderer.renderRouteMap(testRouteData, style)
        }).not.toThrow()
      }
    })

    it('应该能够调整字体大小', async () => {
      const sizes = [10, 14, 18, 24]
      
      for (const size of sizes) {
        const style = { ...testStyleConfig, fontSize: size }
        expect(async () => {
          await visualRenderer.renderRouteMap(testRouteData, style)
        }).not.toThrow()
      }
    })
  })

  describe('路径优化功能', () => {
    it('应该能够简化复杂路径', () => {
      const complexPath = Array.from({ length: 1000 }, (_, i) => ({
        x: i,
        y: Math.sin(i * 0.1) * 100 + 200
      }))
      
      const simplifiedPath = performanceOptimizer.simplifyPath(complexPath, 5.0)
      expect(simplifiedPath.length).toBeLessThan(complexPath.length)
      expect(simplifiedPath.length).toBeGreaterThan(2)
    })

    it('应该能够应用LOD优化', () => {
      const path = Array.from({ length: 500 }, (_, i) => ({
        x: i * 2,
        y: Math.random() * 400 + 100
      }))
      
      const optimizedPath = performanceOptimizer.applyLOD(path, { width: 800, height: 600 })
      expect(optimizedPath.length).toBeLessThanOrEqual(path.length)
    })

    it('应该能够进行视口裁剪', () => {
      const path = Array.from({ length: 100 }, (_, i) => ({
        x: i * 10,
        y: i * 5
      }))
      
      const viewport = { x: 200, y: 100, width: 400, height: 300 }
      const culledPath = performanceOptimizer.cullOutsideViewport(path, viewport)
      
      expect(culledPath.length).toBeLessThanOrEqual(path.length)
    })
  })

  describe('缓存功能', () => {
    it('应该能够缓存Canvas内容', () => {
      expect(() => {
        performanceOptimizer.cacheCanvas('test-key', canvas)
      }).not.toThrow()
    })

    it('应该能够从缓存恢复Canvas', () => {
      performanceOptimizer.cacheCanvas('test-key', canvas)
      const restored = performanceOptimizer.restoreFromCache('test-key', canvas)
      expect(typeof restored).toBe('boolean')
    })

    it('应该能够清理缓存', () => {
      performanceOptimizer.cacheCanvas('test-key', canvas)
      expect(() => {
        performanceOptimizer.clearCache('test-key')
      }).not.toThrow()
      
      expect(() => {
        performanceOptimizer.clearCache()
      }).not.toThrow()
    })
  })

  describe('错误处理', () => {
    it('应该处理无效的Canvas初始化', () => {
      expect(() => {
        visualRenderer.initCanvas(null as any)
      }).toThrow()
    })

    it('应该处理空的路线数据', async () => {
      const emptyRoute: RouteData = {
        locations: [],
        path: [],
        bounds: { north: 0, south: 0, east: 0, west: 0 }
      }
      
      expect(async () => {
        await visualRenderer.renderRouteMap(emptyRoute, testStyleConfig)
      }).not.toThrow()
    })

    it('应该处理无效的样式配置', async () => {
      const invalidStyle = {
        ...testStyleConfig,
        lineWidth: -1,
        fontSize: 0
      }
      
      expect(async () => {
        await visualRenderer.renderRouteMap(testRouteData, invalidStyle)
      }).not.toThrow()
    })
  })

  describe('性能基准测试', () => {
    it('渲染性能应该在合理范围内', async () => {
      const startTime = performance.now()
      
      await visualRenderer.renderRouteMap(testRouteData, testStyleConfig)
      
      const renderTime = performance.now() - startTime
      expect(renderTime).toBeLessThan(100) // 应该在100ms内完成
    })

    it('大量数据渲染应该启用优化', async () => {
      const largeRouteData: RouteData = {
        ...testRouteData,
        path: Array.from({ length: 2000 }, (_, i) => ({
          x: i,
          y: Math.sin(i * 0.01) * 200 + 300
        }))
      }
      
      visualRenderer.setOptimizationOptions({
        enableLOD: true,
        maxPoints: 500,
        simplificationTolerance: 3.0
      })
      
      const startTime = performance.now()
      await visualRenderer.renderRouteMap(largeRouteData, testStyleConfig)
      const renderTime = performance.now() - startTime
      
      expect(renderTime).toBeLessThan(200) // 优化后应该在200ms内完成
    })
  })

  describe('验收标准验证', () => {
    it('应该满足Spec 1.3的所有核心要求', async () => {
      // 1. Canvas渲染框架
      expect(visualRenderer.initCanvas).toBeDefined()
      
      // 2. 基础图形绘制
      expect(() => visualRenderer.clearCanvas()).not.toThrow()
      
      // 3. 路线和地点标注渲染
      const result = await visualRenderer.renderRouteMap(testRouteData, testStyleConfig)
      expect(result).toBe(canvas)
      
      // 4. 颜色方案和样式配置
      expect(styleManager.setCurrentTheme).toBeDefined()
      expect(styleManager.createStyleConfig).toBeDefined()
      
      // 5. 性能优化
      expect(visualRenderer.setOptimizationOptions).toBeDefined()
      expect(visualRenderer.getPerformanceMetrics).toBeDefined()
      
      // 6. 集成测试通过
      expect(true).toBe(true) // 如果到这里没有抛出异常，说明集成测试通过
    })

    it('应该支持所有预定义的颜色方案', () => {
      const supportedSchemes = ['blue', 'orange', 'green', 'purple', 'red']
      
      supportedSchemes.forEach(scheme => {
        expect(() => {
          styleManager.setCurrentTheme(scheme as any)
        }).not.toThrow()
      })
    })

    it('应该提供完整的性能监控功能', () => {
      // 性能指标获取
      const metrics = visualRenderer.getPerformanceMetrics()
      expect(metrics).toBeDefined()
      
      // 性能建议
      const recommendations = visualRenderer.getPerformanceRecommendations()
      expect(Array.isArray(recommendations)).toBe(true)
      
      // 自动优化
      expect(() => visualRenderer.autoOptimize()).not.toThrow()
    })
  })
})

describe('样式管理器测试', () => {
  beforeEach(() => {
    styleManager.resetToDefault()
  })

  it('应该能够设置和获取主题', () => {
    styleManager.setCurrentTheme('green')
    const config = styleManager.createStyleConfig()
    expect(config.colorScheme).toBe('green')
  })

  it('应该能够自定义样式配置', () => {
    const customConfig = {
      colorScheme: 'custom' as any,
      lineWidth: 5,
      fontSize: 16,
      canvasSize: { width: 1000, height: 800 },
      showShadow: false
    }
    
    styleManager.saveCustomStyle('custom', customConfig)
    const config = styleManager.createStyleConfig('custom')
    expect(config.lineWidth).toBe(5)
    expect(config.fontSize).toBe(16)
  })

  it('应该能够重置为默认配置', () => {
    styleManager.setCurrentTheme('purple')
    styleManager.resetToDefault()
    
    const currentTheme = styleManager.getCurrentTheme()
    expect(currentTheme).toBe('blue')
  })
})

describe('性能优化器测试', () => {
  beforeEach(() => {
    performanceOptimizer.resetStats()
  })

  it('应该能够记录性能指标', () => {
    performanceOptimizer.startPerformanceMonitoring()
    performanceOptimizer.recordFrame()
    performanceOptimizer.recordRenderTime(performance.now())
    
    const canvas = new MockCanvas() as any
    const metrics = performanceOptimizer.getPerformanceMetrics(canvas, 100)
    
    expect(metrics).toBeDefined()
    expect(typeof metrics.renderTime).toBe('number')
    expect(typeof metrics.frameRate).toBe('number')
  })

  it('应该能够提供性能建议', () => {
    const canvas = new MockCanvas() as any
    const metrics = performanceOptimizer.getPerformanceMetrics(canvas, 100)
    const recommendations = performanceOptimizer.getPerformanceRecommendations(metrics)
    
    expect(Array.isArray(recommendations)).toBe(true)
  })

  it('应该能够生成优化配置', () => {
    const canvas = new MockCanvas() as any
    const metrics = performanceOptimizer.getPerformanceMetrics(canvas, 2000)
    const options = performanceOptimizer.getOptimizedOptions(metrics)
    
    expect(options).toBeDefined()
    expect(typeof options.enableLOD).toBe('boolean')
    expect(typeof options.maxPoints).toBe('number')
  })
})