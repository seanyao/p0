/**
 * 视觉渲染相关类型定义
 */

import { LocationInfo, Coordinates } from './location'

// 基础几何类型
export interface Point {
  x: number
  y: number
}

export interface MapBounds {
  north: number
  south: number
  east: number
  west: number
}

// 路线数据
export interface RouteData {
  locations: LocationInfo[]
  path: PathPoint[]
  bounds: MapBounds
  totalDistance?: number
}

// 地点标记
export interface LocationMarker {
  position: Point
  label: string
  type?: 'start' | 'end' | 'waypoint'
  location?: LocationInfo
}

// 路线样式
export interface RouteStyle {
  pathColor: string
  pathWidth: number
  markerColor: string
  markerSize: number
  fontSize: number
  fontFamily: string
  labelTextColor: string
  labelBackgroundColor: string
  labelBorderColor: string
}

// 路径点
export interface PathPoint extends Point {
  location?: LocationInfo
  isWaypoint?: boolean
}

// 样式配置
export interface StyleConfig {
  colorScheme: 'blue' | 'orange' | 'green' | 'purple' | 'red'
  lineWidth: number
  fontSize: number
  canvasSize: { width: number; height: number }
  showShadow: boolean
  shadowIntensity?: number
}

// 路径样式
export interface PathStyle {
  strokeStyle: string | CanvasGradient
  lineWidth: number
  lineCap: 'round' | 'square' | 'butt'
  shadowBlur: number
  shadowColor: string
}

// 标记样式
export interface MarkerStyle {
  fillStyle: string
  strokeStyle: string
  radius: number
  fontSize: number
  fontFamily: string
  textColor: string
}

// 标签位置
export interface LabelPosition extends Point {
  text: string
  location: LocationInfo
}

// 装饰配置
export interface DecorationConfig {
  showWatermark: boolean
  watermarkText?: string
  watermarkOpacity?: number
  showGrid?: boolean
  gridColor?: string
}

// 颜色方案定义
export interface ColorScheme {
  name: string
  primary: string
  secondary: string
  gradient: string[]
  text: string
  background: string
}

// 渲染选项
export interface RenderOptions {
  quality: 'low' | 'medium' | 'high'
  antialiasing: boolean
  retina: boolean
}

// 视觉渲染器接口
export interface VisualRenderer {
  // 渲染完整路线图
  renderRouteMap(routeData: RouteData, style: StyleConfig, options?: RenderOptions): Promise<HTMLCanvasElement>
  
  // 渲染地图底图
  renderBaseMap(bounds: MapBounds, canvas: HTMLCanvasElement): void
  
  // 渲染路线路径
  renderRoutePath(pathPoints: PathPoint[], style: PathStyle, canvas: HTMLCanvasElement): void
  
  // 渲染地点标注
  renderLocationMarkers(positions: LabelPosition[], style: MarkerStyle, canvas: HTMLCanvasElement): void
  
  // 添加装饰元素
  addDecorations(canvas: HTMLCanvasElement, config: DecorationConfig): void
}

// 预设样式方案
export const COLOR_SCHEMES: Record<string, ColorScheme> = {
  blue: {
    name: '经典蓝色',
    primary: '#4A90E2',
    secondary: '#357ABD',
    gradient: ['#4A90E2', '#357ABD'],
    text: '#333333',
    background: '#F8F9FA'
  },
  orange: {
    name: '活力橙色',
    primary: '#FF8C42',
    secondary: '#FF6B35',
    gradient: ['#FF8C42', '#FF6B35'],
    text: '#333333',
    background: '#FFF8F5'
  },
  green: {
    name: '自然绿色',
    primary: '#7ED321',
    secondary: '#5CB85C',
    gradient: ['#7ED321', '#5CB85C'],
    text: '#333333',
    background: '#F8FFF8'
  },
  purple: {
    name: '优雅紫色',
    primary: '#9013FE',
    secondary: '#7B68EE',
    gradient: ['#9013FE', '#7B68EE'],
    text: '#333333',
    background: '#FAF8FF'
  },
  red: {
    name: '热情红色',
    primary: '#FF4757',
    secondary: '#FF3838',
    gradient: ['#FF4757', '#FF3838'],
    text: '#333333',
    background: '#FFF8F8'
  }
}

// 默认样式配置}

// 默认路线样式
export const DEFAULT_ROUTE_STYLE: RouteStyle = {
  pathColor: '#4A90E2',
  pathWidth: 6,
  markerColor: '#FF8C42',
  markerSize: 12,
  fontSize: 14,
  fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
  labelTextColor: '#333333',
  labelBackgroundColor: '#FFFFFF',
  labelBorderColor: '#E0E0E0'
}

export const DEFAULT_STYLE_CONFIG: StyleConfig = {
  colorScheme: 'blue',
  lineWidth: 6,
  fontSize: 16,
  canvasSize: { width: 1080, height: 1080 },
  showShadow: true,
  shadowIntensity: 0.3
}