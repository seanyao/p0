# Spec 1.3 - 视觉渲染功能

## 基本信息
- **状态**: draft
- **优先级**: Must (核心功能)
- **预估时间**: 2小时
- **负责角色**: @CTO_Linus
- **Git分支**: feature/spec-1.3-visual-renderer（实施时创建）

## 功能描述
使用Canvas API将路线数据渲染为美观的旅游路线图，包括地图底图、路线样式、地点标注和整体视觉效果。

## 详细需求

### 地图底图渲染
- **地理轮廓**: 简洁的省份/城市边界线
- **背景色彩**: 淡雅的米白色/浅灰色背景
- **信息过滤**: 去除多余的地理标注和细节
- **比例协调**: 保持地图元素的视觉平衡

### 路线样式规范
- **线条粗细**: 默认6px，支持4-8px调节
- **颜色方案**: 5种预设渐变色彩
  - 🔵 经典蓝色渐变 (#4A90E2 → #357ABD)
  - 🟠 活力橙色渐变 (#FF8C42 → #FF6B35)
  - 🟢 自然绿色渐变 (#7ED321 → #5CB85C)
  - 🟣 优雅紫色渐变 (#9013FE → #7B68EE)
  - 🔴 热情红色渐变 (#FF4757 → #FF3838)
- **视觉效果**: 平滑曲线，带有轻微阴影
- **端点处理**: 圆形端点，与路线颜色一致

### 地点标注设计
- **标记点**: 圆形标记，直径14px，颜色与路线呼应
- **字体规范**: 
  - 中文字体: 苹方-简 / 思源黑体
  - 字号: 16px
  - 字重: Medium (500)
  - 颜色: 深灰色 #333333
- **标签背景**: 半透明白色背景，圆角矩形
- **位置优化**: 智能避让，确保清晰可读

### 整体布局规范
- **画布尺寸**: 
  - 方形: 1080x1080px (社交分享)
  - 横版: 1920x1080px (桌面壁纸)
- **边距控制**: 四周保持80px边距
- **水印标识**: 右下角添加小logo，透明度30%

## 技术实现

### 核心接口设计
```typescript
interface VisualRenderer {
  // 渲染完整路线图
  renderRouteMap(routeData: RouteData, style: StyleConfig): HTMLCanvasElement
  
  // 渲染地图底图
  renderBaseMap(bounds: MapBounds, canvas: HTMLCanvasElement): void
  
  // 渲染路线路径
  renderRoutePath(pathPoints: PathPoint[], style: PathStyle, canvas: HTMLCanvasElement): void
  
  // 渲染地点标注
  renderLocationMarkers(positions: LabelPosition[], style: MarkerStyle, canvas: HTMLCanvasElement): void
  
  // 添加装饰元素
  addDecorations(canvas: HTMLCanvasElement, config: DecorationConfig): void
}

interface StyleConfig {
  colorScheme: 'blue' | 'orange' | 'green' | 'purple' | 'red'
  lineWidth: number
  fontSize: number
  canvasSize: { width: number, height: number }
  showShadow: boolean
}

interface PathStyle {
  strokeStyle: string | CanvasGradient
  lineWidth: number
  lineCap: 'round' | 'square' | 'butt'
  shadowBlur: number
  shadowColor: string
}

interface MarkerStyle {
  fillStyle: string
  strokeStyle: string
  radius: number
  fontSize: number
  fontFamily: string
  textColor: string
}
```

### 渲染流程

#### 1. Canvas初始化
```typescript
function initializeCanvas(width: number, height: number): HTMLCanvasElement {
  const canvas = document.createElement('canvas')
  canvas.width = width
  canvas.height = height
  
  const ctx = canvas.getContext('2d')!
  ctx.imageSmoothingEnabled = true
  ctx.imageSmoothingQuality = 'high'
  
  return canvas
}
```

#### 2. 渐变色生成
```typescript
function createGradient(ctx: CanvasRenderingContext2D, start: Point, end: Point, colors: string[]): CanvasGradient {
  const gradient = ctx.createLinearGradient(start.x, start.y, end.x, end.y)
  
  colors.forEach((color, index) => {
    gradient.addColorStop(index / (colors.length - 1), color)
  })
  
  return gradient
}
```

#### 3. 路径绘制
```typescript
function drawSmoothPath(ctx: CanvasRenderingContext2D, points: PathPoint[], style: PathStyle): void {
  ctx.beginPath()
  ctx.moveTo(points[0].x, points[0].y)
  
  for (let i = 1; i < points.length - 2; i++) {
    const cp1 = points[i]
    const cp2 = points[i + 1]
    const end = points[i + 2]
    
    ctx.bezierCurveTo(cp1.x, cp1.y, cp2.x, cp2.y, end.x, end.y)
  }
  
  applyPathStyle(ctx, style)
  ctx.stroke()
}
```

#### 4. 文字渲染
```typescript
function drawLocationLabel(ctx: CanvasRenderingContext2D, text: string, position: Point, style: MarkerStyle): void {
  // 绘制背景
  const metrics = ctx.measureText(text)
  const padding = 8
  const bgWidth = metrics.width + padding * 2
  const bgHeight = style.fontSize + padding * 2
  
  ctx.fillStyle = 'rgba(255, 255, 255, 0.9)'
  ctx.fillRect(position.x - bgWidth/2, position.y - bgHeight/2, bgWidth, bgHeight)
  
  // 绘制文字
  ctx.fillStyle = style.textColor
  ctx.font = `${style.fontSize}px ${style.fontFamily}`
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  ctx.fillText(text, position.x, position.y)
}
```

## 验收标准

### 视觉质量验收
- [ ] 整体画面清晰，无锯齿和模糊
- [ ] 颜色搭配和谐，符合现代审美
- [ ] 路线平滑自然，视觉效果佳
- [ ] 文字清晰易读，对比度充足

### 功能完整性验收
- [ ] 支持所有预设的颜色方案
- [ ] 支持不同的画布尺寸输出
- [ ] 地点标注位置准确，不重叠
- [ ] 水印和装饰元素正确显示

### 性能验收
- [ ] 渲染时间 <3秒
- [ ] 支持高分辨率输出不卡顿
- [ ] 内存使用合理，无泄漏
- [ ] 多次渲染结果一致

## 测试用例

### 基础渲染测试
```
输入: 3个城市的路线数据 + 蓝色方案
期望: 生成蓝色渐变的美观路线图

输入: 相同数据 + 不同颜色方案
期望: 颜色正确切换，其他元素不变

输入: 8个城市的复杂路线
期望: 所有元素都能正确渲染，不重叠
```

### 边界情况测试
```
输入: 极小画布尺寸 (300x300)
期望: 元素按比例缩放，仍然清晰

输入: 超大画布尺寸 (4000x4000)
期望: 高分辨率输出，性能可接受

输入: 地名包含特殊字符
期望: 文字正确显示，不出现乱码
```

## 依赖关系

- **前置条件**: spec-1.2 路线生成功能完成
- **阻塞因素**: 无
- **后续任务**: spec-1.4 样式调整功能

## 风险评估

- **技术风险**: 中等，Canvas渲染需要处理各种边界情况
- **时间风险**: 中等，视觉效果调优可能需要多次迭代
- **资源风险**: 中等，高分辨率渲染消耗较多内存

## 性能优化

### 渲染优化
- **离屏渲染**: 使用离屏Canvas提高性能
- **分层渲染**: 底图和路线分层渲染，减少重绘
- **缓存机制**: 缓存常用的渐变和样式对象

### 内存优化
- **对象池**: 复用Canvas和Context对象
- **及时清理**: 渲染完成后及时释放临时资源
- **图像压缩**: 输出前进行适当的图像压缩

---

**实施计划**:
1. 搭建Canvas渲染框架 (30分钟)
2. 实现基础图形绘制功能 (45分钟)
3. 开发路线和标注渲染 (45分钟)
4. 实现颜色方案和样式系统 (30分钟)
5. 优化视觉效果和性能 (30分钟)