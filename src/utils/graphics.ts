/**
 * 图形绘制工具函数
 * 提供高级的Canvas绘制功能
 */

import { Point, PathPoint } from '../types/visual'

/**
 * 创建线性渐变
 */
export function createLinearGradient(
  ctx: CanvasRenderingContext2D,
  start: Point,
  end: Point,
  colors: string[]
): CanvasGradient {
  const gradient = ctx.createLinearGradient(start.x, start.y, end.x, end.y)
  
  colors.forEach((color, index) => {
    gradient.addColorStop(index / (colors.length - 1), color)
  })
  
  return gradient
}

/**
 * 创建径向渐变
 */
export function createRadialGradient(
  ctx: CanvasRenderingContext2D,
  center: Point,
  innerRadius: number,
  outerRadius: number,
  colors: string[]
): CanvasGradient {
  const gradient = ctx.createRadialGradient(
    center.x, center.y, innerRadius,
    center.x, center.y, outerRadius
  )
  
  colors.forEach((color, index) => {
    gradient.addColorStop(index / (colors.length - 1), color)
  })
  
  return gradient
}

/**
 * 绘制平滑曲线路径
 * 使用贝塞尔曲线连接所有点
 */
export function drawSmoothPath(
  ctx: CanvasRenderingContext2D,
  points: PathPoint[],
  tension: number = 0.3
): void {
  if (points.length < 2) return

  ctx.beginPath()
  ctx.moveTo(points[0].x, points[0].y)

  if (points.length === 2) {
    // 只有两个点，直接连线
    ctx.lineTo(points[1].x, points[1].y)
  } else {
    // 多个点，使用平滑曲线
    for (let i = 0; i < points.length - 1; i++) {
      const current = points[i]
      const next = points[i + 1]
      
      if (i === 0) {
        // 第一段，使用二次贝塞尔曲线
        const cp = {
          x: current.x + (next.x - current.x) * tension,
          y: current.y + (next.y - current.y) * tension
        }
        ctx.quadraticCurveTo(cp.x, cp.y, next.x, next.y)
      } else {
        // 中间段，使用三次贝塞尔曲线
        const prev = points[i - 1]
        const cp1 = {
          x: current.x + (next.x - prev.x) * tension * 0.5,
          y: current.y + (next.y - prev.y) * tension * 0.5
        }
        const cp2 = {
          x: next.x - (points[Math.min(i + 2, points.length - 1)].x - current.x) * tension * 0.5,
          y: next.y - (points[Math.min(i + 2, points.length - 1)].y - current.y) * tension * 0.5
        }
        ctx.bezierCurveTo(cp1.x, cp1.y, cp2.x, cp2.y, next.x, next.y)
      }
    }
  }
}

/**
 * 绘制带阴影的圆形
 */
export function drawCircleWithShadow(
  ctx: CanvasRenderingContext2D,
  center: Point,
  radius: number,
  fillStyle: string | CanvasGradient,
  strokeStyle?: string,
  shadowBlur: number = 4,
  shadowColor: string = 'rgba(0, 0, 0, 0.2)'
): void {
  ctx.save()
  
  // 设置阴影
  ctx.shadowBlur = shadowBlur
  ctx.shadowColor = shadowColor
  ctx.shadowOffsetX = 2
  ctx.shadowOffsetY = 2
  
  // 绘制圆形
  ctx.beginPath()
  ctx.arc(center.x, center.y, radius, 0, Math.PI * 2)
  ctx.fillStyle = fillStyle
  ctx.fill()
  
  if (strokeStyle) {
    ctx.shadowBlur = 0 // 边框不需要阴影
    ctx.strokeStyle = strokeStyle
    ctx.lineWidth = 2
    ctx.stroke()
  }
  
  ctx.restore()
}

/**
 * 绘制带背景的文字标签
 */
export function drawTextLabel(
  ctx: CanvasRenderingContext2D,
  text: string,
  position: Point,
  options: {
    fontSize: number
    fontFamily: string
    textColor: string
    backgroundColor: string
    borderColor?: string
    padding: number
    borderRadius?: number
  }
): void {
  const { fontSize, fontFamily, textColor, backgroundColor, borderColor, padding, borderRadius = 4 } = options
  
  ctx.save()
  
  // 设置字体
  ctx.font = `500 ${fontSize}px ${fontFamily}`
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  
  // 测量文字尺寸
  const metrics = ctx.measureText(text)
  const textWidth = metrics.width
  const textHeight = fontSize
  
  const bgWidth = textWidth + padding * 2
  const bgHeight = textHeight + padding * 2
  
  const bgX = position.x - bgWidth / 2
  const bgY = position.y - bgHeight / 2
  
  // 绘制圆角矩形背景
  if (borderRadius > 0) {
    drawRoundedRect(ctx, bgX, bgY, bgWidth, bgHeight, borderRadius)
  } else {
    ctx.rect(bgX, bgY, bgWidth, bgHeight)
  }
  
  ctx.fillStyle = backgroundColor
  ctx.fill()
  
  // 绘制边框
  if (borderColor) {
    ctx.strokeStyle = borderColor
    ctx.lineWidth = 1
    ctx.stroke()
  }
  
  // 绘制文字
  ctx.fillStyle = textColor
  ctx.fillText(text, position.x, position.y)
  
  ctx.restore()
}

/**
 * 绘制圆角矩形路径
 */
export function drawRoundedRect(
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  width: number,
  height: number,
  radius: number
): void {
  ctx.beginPath()
  ctx.moveTo(x + radius, y)
  ctx.lineTo(x + width - radius, y)
  ctx.quadraticCurveTo(x + width, y, x + width, y + radius)
  ctx.lineTo(x + width, y + height - radius)
  ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height)
  ctx.lineTo(x + radius, y + height)
  ctx.quadraticCurveTo(x, y + height, x, y + height - radius)
  ctx.lineTo(x, y + radius)
  ctx.quadraticCurveTo(x, y, x + radius, y)
  ctx.closePath()
}

/**
 * 计算两点之间的距离
 */
export function calculateDistance(point1: Point, point2: Point): number {
  const dx = point2.x - point1.x
  const dy = point2.y - point1.y
  return Math.sqrt(dx * dx + dy * dy)
}

/**
 * 计算点到线段的距离
 */
export function pointToLineDistance(point: Point, lineStart: Point, lineEnd: Point): number {
  const A = point.x - lineStart.x
  const B = point.y - lineStart.y
  const C = lineEnd.x - lineStart.x
  const D = lineEnd.y - lineStart.y

  const dot = A * C + B * D
  const lenSq = C * C + D * D
  
  if (lenSq === 0) return calculateDistance(point, lineStart)
  
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
 * 智能标签位置计算
 * 避免标签重叠
 */
export function calculateOptimalLabelPositions(
  points: PathPoint[],
  labelHeight: number = 30,
  minDistance: number = 50
): Point[] {
  const positions: Point[] = []
  
  points.forEach((point, index) => {
    let bestY = point.y - labelHeight
    let attempts = 0
    const maxAttempts = 10
    
    // 检查是否与已有标签重叠
    while (attempts < maxAttempts) {
      let hasOverlap = false
      
      for (const existingPos of positions) {
        const distance = calculateDistance({ x: point.x, y: bestY }, existingPos)
        if (distance < minDistance) {
          hasOverlap = true
          break
        }
      }
      
      if (!hasOverlap) break
      
      // 尝试不同的位置
      bestY = attempts % 2 === 0 
        ? point.y - labelHeight - (attempts + 1) * 10
        : point.y + labelHeight + attempts * 10
      
      attempts++
    }
    
    positions.push({ x: point.x, y: bestY })
  })
  
  return positions
}

/**
 * 应用高质量渲染设置
 */
export function applyHighQualitySettings(ctx: CanvasRenderingContext2D): void {
  ctx.imageSmoothingEnabled = true
  ctx.imageSmoothingQuality = 'high'
  ctx.lineCap = 'round'
  ctx.lineJoin = 'round'
}

/**
 * 重置Canvas上下文设置
 */
export function resetCanvasContext(ctx: CanvasRenderingContext2D): void {
  ctx.shadowBlur = 0
  ctx.shadowOffsetX = 0
  ctx.shadowOffsetY = 0
  ctx.globalAlpha = 1
  ctx.setLineDash([])
}