/**
 * 样式管理服务
 * 负责管理颜色方案、样式配置和主题切换
 */

import { 
  StyleConfig, 
  ColorScheme, 
  RouteStyle,
  COLOR_SCHEMES, 
  DEFAULT_STYLE_CONFIG,
  DEFAULT_ROUTE_STYLE
} from '../types/visual'

export interface ThemePreset {
  id: string
  name: string
  description: string
  styleConfig: StyleConfig
  routeStyle: RouteStyle
  preview?: string
}

export class StyleManager {
  private currentTheme: string = 'blue'
  private customStyles: Map<string, Partial<StyleConfig>> = new Map()
  private themeChangeListeners: Array<(theme: string) => void> = []

  /**
   * 获取当前主题
   */
  getCurrentTheme(): string {
    return this.currentTheme
  }

  /**
   * 设置当前主题
   */
  setCurrentTheme(themeId: string): void {
    if (COLOR_SCHEMES[themeId]) {
      this.currentTheme = themeId
      this.notifyThemeChange(themeId)
    } else {
      console.warn(`Theme '${themeId}' not found`)
    }
  }

  /**
   * 获取颜色方案
   */
  getColorScheme(themeId?: string): ColorScheme {
    const id = themeId || this.currentTheme
    return COLOR_SCHEMES[id] || COLOR_SCHEMES.blue
  }

  /**
   * 获取所有可用的颜色方案
   */
  getAllColorSchemes(): Record<string, ColorScheme> {
    return COLOR_SCHEMES
  }

  /**
   * 创建基于主题的样式配置
   */
  createStyleConfig(themeId?: string, overrides?: Partial<StyleConfig>): StyleConfig {
    const theme = themeId || this.currentTheme
    const baseConfig = { ...DEFAULT_STYLE_CONFIG }
    const customStyle = this.customStyles.get(theme)
    
    return {
      ...baseConfig,
      colorScheme: theme as any,
      ...customStyle,
      ...overrides
    }
  }

  /**
   * 创建基于主题的路线样式
   */
  createRouteStyle(themeId?: string, overrides?: Partial<RouteStyle>): RouteStyle {
    const colorScheme = this.getColorScheme(themeId)
    
    return {
      ...DEFAULT_ROUTE_STYLE,
      pathColor: colorScheme.primary,
      markerColor: colorScheme.secondary,
      labelTextColor: colorScheme.text,
      labelBackgroundColor: colorScheme.background,
      ...overrides
    }
  }

  /**
   * 保存自定义样式
   */
  saveCustomStyle(themeId: string, style: Partial<StyleConfig>): void {
    this.customStyles.set(themeId, style)
    
    // 如果是当前主题，立即应用
    if (themeId === this.currentTheme) {
      this.notifyThemeChange(themeId)
    }
  }

  /**
   * 获取自定义样式
   */
  getCustomStyle(themeId: string): Partial<StyleConfig> | undefined {
    return this.customStyles.get(themeId)
  }

  /**
   * 删除自定义样式
   */
  removeCustomStyle(themeId: string): void {
    this.customStyles.delete(themeId)
  }

  /**
   * 获取预设主题列表
   */
  getThemePresets(): ThemePreset[] {
    return Object.entries(COLOR_SCHEMES).map(([id, scheme]) => ({
      id,
      name: scheme.name,
      description: `使用${scheme.name}作为主色调的经典配色方案`,
      styleConfig: this.createStyleConfig(id),
      routeStyle: this.createRouteStyle(id),
      preview: scheme.primary
    }))
  }

  /**
   * 创建自定义主题预设
   */
  createCustomThemePreset(
    id: string,
    name: string,
    description: string,
    colorScheme: ColorScheme,
    styleOverrides?: Partial<StyleConfig>
  ): ThemePreset {
    // 临时添加到颜色方案中
    const tempSchemes = { ...COLOR_SCHEMES, [id]: colorScheme }
    
    const styleConfig = {
      ...DEFAULT_STYLE_CONFIG,
      colorScheme: id as any,
      ...styleOverrides
    }
    
    const routeStyle = {
      ...DEFAULT_ROUTE_STYLE,
      pathColor: colorScheme.primary,
      markerColor: colorScheme.secondary,
      labelTextColor: colorScheme.text,
      labelBackgroundColor: colorScheme.background
    }

    return {
      id,
      name,
      description,
      styleConfig,
      routeStyle,
      preview: colorScheme.primary
    }
  }

  /**
   * 根据场景推荐主题
   */
  recommendThemeForScenario(scenario: 'travel' | 'business' | 'nature' | 'urban' | 'classic'): string {
    const recommendations = {
      travel: 'orange',    // 活力橙色适合旅游
      business: 'blue',    // 经典蓝色适合商务
      nature: 'green',     // 自然绿色适合户外
      urban: 'purple',     // 优雅紫色适合都市
      classic: 'blue'      // 经典蓝色作为默认
    }
    
    return recommendations[scenario] || 'blue'
  }

  /**
   * 生成渐变色
   */
  generateGradientColors(baseColor: string, steps: number = 5): string[] {
    // 简单的渐变生成算法
    const colors: string[] = []
    const baseRgb = this.hexToRgb(baseColor)
    
    if (!baseRgb) return [baseColor]
    
    for (let i = 0; i < steps; i++) {
      const factor = i / (steps - 1)
      const r = Math.round(baseRgb.r + (255 - baseRgb.r) * factor * 0.3)
      const g = Math.round(baseRgb.g + (255 - baseRgb.g) * factor * 0.3)
      const b = Math.round(baseRgb.b + (255 - baseRgb.b) * factor * 0.3)
      
      colors.push(this.rgbToHex(r, g, b))
    }
    
    return colors
  }

  /**
   * 获取对比色
   */
  getContrastColor(backgroundColor: string): string {
    const rgb = this.hexToRgb(backgroundColor)
    if (!rgb) return '#000000'
    
    // 计算亮度
    const brightness = (rgb.r * 299 + rgb.g * 587 + rgb.b * 114) / 1000
    
    // 根据亮度返回黑色或白色
    return brightness > 128 ? '#000000' : '#FFFFFF'
  }

  /**
   * 添加主题变化监听器
   */
  addThemeChangeListener(listener: (theme: string) => void): void {
    this.themeChangeListeners.push(listener)
  }

  /**
   * 移除主题变化监听器
   */
  removeThemeChangeListener(listener: (theme: string) => void): void {
    const index = this.themeChangeListeners.indexOf(listener)
    if (index > -1) {
      this.themeChangeListeners.splice(index, 1)
    }
  }

  /**
   * 通知主题变化
   */
  private notifyThemeChange(theme: string): void {
    this.themeChangeListeners.forEach(listener => {
      try {
        listener(theme)
      } catch (error) {
        console.error('Theme change listener error:', error)
      }
    })
  }

  /**
   * 十六进制转RGB
   */
  private hexToRgb(hex: string): { r: number; g: number; b: number } | null {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex)
    return result ? {
      r: parseInt(result[1], 16),
      g: parseInt(result[2], 16),
      b: parseInt(result[3], 16)
    } : null
  }

  /**
   * RGB转十六进制
   */
  private rgbToHex(r: number, g: number, b: number): string {
    return "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1)
  }

  /**
   * 导出样式配置
   */
  exportStyleConfig(): string {
    return JSON.stringify({
      currentTheme: this.currentTheme,
      customStyles: Object.fromEntries(this.customStyles)
    }, null, 2)
  }

  /**
   * 导入样式配置
   */
  importStyleConfig(configJson: string): boolean {
    try {
      const config = JSON.parse(configJson)
      
      if (config.currentTheme) {
        this.currentTheme = config.currentTheme
      }
      
      if (config.customStyles) {
        this.customStyles = new Map(Object.entries(config.customStyles))
      }
      
      this.notifyThemeChange(this.currentTheme)
      return true
    } catch (error) {
      console.error('Failed to import style config:', error)
      return false
    }
  }

  /**
   * 重置为默认样式
   */
  resetToDefault(): void {
    this.currentTheme = 'blue'
    this.customStyles.clear()
    this.notifyThemeChange(this.currentTheme)
  }
}

// 导出单例实例
export const styleManager = new StyleManager()