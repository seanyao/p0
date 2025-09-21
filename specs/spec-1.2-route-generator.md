# Spec 1.2 - 路线生成功能

## 基本信息
- **状态**: draft
- **优先级**: Must (核心功能)
- **预估时间**: 2小时
- **负责角色**: @CTO_Linus
- **Git分支**: feature/spec-1.2-route-generator（实施时创建）

## 功能描述
基于地理坐标自动生成美观的旅游路线图，包括地图视角调整、路线连接算法和布局优化。

## 详细需求

### 路线生成算法
- **连接顺序**: 严格按照用户输入的地名顺序连接
- **路径类型**: 直线连接（不考虑实际交通路线）
- **曲线平滑**: 使用贝塞尔曲线实现平滑连接效果
- **避免重叠**: 智能调整路径避免与地名标签重叠

### 地图视角优化
- **自动缩放**: 确保所有地点都在可视范围内
- **边距控制**: 保持适当的边距，避免地点贴边显示
- **中心定位**: 自动计算最佳地图中心点
- **比例协调**: 保持地图比例的视觉协调性

### 布局算法
- **标签定位**: 智能计算地名标签的最佳位置
- **避让算法**: 防止标签之间相互遮挡
- **视觉平衡**: 保持整体布局的视觉平衡
- **响应式适配**: 适配不同尺寸的输出格式

## 技术实现

### 核心接口设计
```typescript
interface RouteGenerator {
  // 生成路线数据
  generateRoute(coordinates: Coordinate[]): Promise<RouteData>
  
  // 优化布局
  optimizeLayout(route: RouteData): RouteData
  
  // 计算地图边界
  calculateBounds(coordinates: Coordinate[]): MapBounds
  
  // 生成路径点
  generatePathPoints(coordinates: Coordinate[]): PathPoint[]
}

interface RouteData {
  coordinates: Coordinate[]      // 地点坐标
  pathPoints: PathPoint[]       // 路径点数据
  bounds: MapBounds            // 地图边界
  center: Coordinate           // 地图中心
  zoom: number                // 缩放级别
  labelPositions: LabelPosition[] // 标签位置
}

interface PathPoint {
  lng: number
  lat: number
  type: 'start' | 'end' | 'control' // 路径点类型
  index: number                     // 在路径中的索引
}

interface LabelPosition {
  coordinate: Coordinate
  position: 'top' | 'bottom' | 'left' | 'right'
  offset: { x: number, y: number }
}
```

### 算法实现

#### 1. 边界计算算法
```typescript
function calculateBounds(coordinates: Coordinate[]): MapBounds {
  const lngs = coordinates.map(c => c.lng)
  const lats = coordinates.map(c => c.lat)
  
  const minLng = Math.min(...lngs)
  const maxLng = Math.max(...lngs)
  const minLat = Math.min(...lats)
  const maxLat = Math.max(...lats)
  
  // 添加10%的边距
  const lngPadding = (maxLng - minLng) * 0.1
  const latPadding = (maxLat - minLat) * 0.1
  
  return {
    southwest: { lng: minLng - lngPadding, lat: minLat - latPadding },
    northeast: { lng: maxLng + lngPadding, lat: maxLat + latPadding }
  }
}
```

#### 2. 贝塞尔曲线生成
```typescript
function generateSmoothPath(start: Coordinate, end: Coordinate): PathPoint[] {
  const controlPoint1 = calculateControlPoint(start, end, 0.3)
  const controlPoint2 = calculateControlPoint(start, end, 0.7)
  
  return generateBezierPoints(start, controlPoint1, controlPoint2, end, 20)
}
```

#### 3. 标签避让算法
```typescript
function optimizeLabelPositions(coordinates: Coordinate[]): LabelPosition[] {
  const positions: LabelPosition[] = []
  const occupiedAreas: Rectangle[] = []
  
  for (const coord of coordinates) {
    const bestPosition = findBestLabelPosition(coord, occupiedAreas)
    positions.push(bestPosition)
    occupiedAreas.push(getLabelBounds(bestPosition))
  }
  
  return positions
}
```

## 验收标准

### 功能验收
- [ ] 路线按输入顺序正确连接
- [ ] 所有地点都在可视范围内
- [ ] 路径平滑美观，无锯齿效果
- [ ] 地名标签不重叠，位置合理

### 视觉验收
- [ ] 整体布局协调美观
- [ ] 地图比例适中，不过于拥挤或稀疏
- [ ] 路径曲线自然流畅
- [ ] 标签字体清晰易读

### 性能验收
- [ ] 路线生成时间 <5秒
- [ ] 支持最多8个地点的路线生成
- [ ] 算法稳定，不会出现异常结果
- [ ] 内存使用合理，无内存泄漏

## 测试用例

### 基础功能测试
```
输入: 北京(116.4074, 39.9042) → 上海(121.4737, 31.2304)
期望: 生成平滑连接的两点路线

输入: 3个相近城市坐标
期望: 地图缩放合适，标签不重叠

输入: 8个分布较远的城市坐标  
期望: 所有城市都在可视范围内
```

### 边界情况测试
```
输入: 2个坐标完全相同
期望: 提示错误或合并处理

输入: 坐标跨度极大（如北京到三亚）
期望: 地图能正确显示全部范围

输入: 坐标呈一条直线分布
期望: 标签能智能避让，不重叠
```

## 依赖关系

- **前置条件**: spec-1.1 地名解析功能完成
- **阻塞因素**: 无
- **后续任务**: spec-1.3 视觉渲染功能

## 风险评估

- **技术风险**: 中等，贝塞尔曲线和避让算法需要调试
- **时间风险**: 中等，算法优化可能需要多次迭代
- **资源风险**: 低，主要是计算资源消耗

## 性能优化

### 计算优化
- **缓存机制**: 相同坐标组合的计算结果缓存
- **算法优化**: 使用高效的几何计算库
- **并行处理**: 路径生成和标签定位并行计算

### 内存优化
- **对象复用**: 复用临时计算对象
- **及时释放**: 及时释放不需要的中间结果
- **数据结构**: 使用高效的数据结构存储路径点

---

**实施计划**:
1. 实现基础路线连接算法 (45分钟)
2. 开发地图边界和缩放计算 (30分钟)
3. 实现贝塞尔曲线平滑算法 (30分钟)
4. 开发标签避让算法 (45分钟)
5. 测试和优化 (30分钟)