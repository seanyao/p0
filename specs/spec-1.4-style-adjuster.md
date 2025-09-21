# Spec 1.4 - 样式调整功能

## 基本信息
- **状态**: draft
- **优先级**: Should (用户体验)
- **预估时间**: 1.5小时
- **负责角色**: @CTO_Linus
- **Git分支**: feature/spec-1.4-style-adjuster（实施时创建）

## 功能描述
提供用户友好的样式调整界面，允许用户实时预览和调整路线图的视觉样式，包括颜色、粗细、字体等选项。

## 详细需求

### 样式调整选项

#### 路线样式
- **颜色方案**: 5种预设配色，点击切换
  - 🔵 经典蓝色渐变
  - 🟠 活力橙色渐变  
  - 🟢 自然绿色渐变
  - 🟣 优雅紫色渐变
  - 🔴 热情红色渐变
- **线条粗细**: 3个档位选择
  - 细线: 4px
  - 中等: 6px (默认)
  - 粗线: 8px
- **线条样式**: 2种类型
  - 实线 (默认)
  - 虚线

#### 文字样式
- **字体大小**: 3个档位
  - 小号: 14px
  - 中号: 16px (默认)
  - 大号: 18px
- **字体颜色**: 2种选择
  - 跟随路线色彩
  - 固定深灰色 #333333 (默认)

#### 整体风格
- **🏢 商务风格**: 深色调，简洁线条，适合商务场景
- **🌸 休闲风格**: 暖色调，圆润元素，适合休闲旅游
- **📚 文艺风格**: 复古色调，手绘感觉，适合文艺青年

### 交互设计

#### 控制面板布局
```
┌─────────────────────────────────────────────┐
│  🎨 样式调整                                 │
│  ─────────────────────────────────────────  │
│                                             │
│  颜色方案                                    │
│  🔵 🟠 🟢 🟣 🔴                            │
│                                             │
│  线条粗细                                    │
│  ○ 细  ● 中  ○ 粗                          │
│                                             │
│  整体风格                                    │
│  💼 商务  🌸 休闲  📚 文艺                   │
│                                             │
│  ┌─────────────┐  ┌─────────────┐          │
│  │  重置默认    │  │  应用样式    │          │
│  └─────────────┘  └─────────────┘          │
└─────────────────────────────────────────────┘
```

#### 实时预览
- **即时反馈**: 点击样式选项立即在预览区域生效
- **预览质量**: 使用与最终输出相同的渲染质量
- **加载状态**: 样式切换时显示加载指示器
- **错误处理**: 渲染失败时显示友好提示

## 技术实现

### 核心接口设计
```typescript
interface StyleAdjuster {
  // 应用样式配置
  applyStyle(config: StyleConfig): Promise<void>
  
  // 重置为默认样式
  resetToDefault(): void
  
  // 获取当前样式配置
  getCurrentStyle(): StyleConfig
  
  // 预设样式方案
  getPresetStyles(): PresetStyle[]
}

interface StyleConfig {
  // 路线样式
  colorScheme: ColorScheme
  lineWidth: LineWidth
  lineStyle: 'solid' | 'dashed'
  
  // 文字样式
  fontSize: FontSize
  fontColor: 'auto' | 'fixed'
  
  // 整体风格
  theme: 'business' | 'casual' | 'artistic'
  
  // 高级选项
  showShadow: boolean
  shadowIntensity: number
}

type ColorScheme = 'blue' | 'orange' | 'green' | 'purple' | 'red'
type LineWidth = 'thin' | 'medium' | 'thick'
type FontSize = 'small' | 'medium' | 'large'

interface PresetStyle {
  name: string
  description: string
  config: StyleConfig
  preview: string // 预览图URL
}
```

### 样式系统架构

#### 1. 样式配置管理
```typescript
class StyleManager {
  private currentConfig: StyleConfig
  private defaultConfig: StyleConfig
  private presets: Map<string, PresetStyle>
  
  constructor() {
    this.defaultConfig = this.getDefaultConfig()
    this.currentConfig = { ...this.defaultConfig }
    this.initializePresets()
  }
  
  updateConfig(updates: Partial<StyleConfig>): void {
    this.currentConfig = { ...this.currentConfig, ...updates }
    this.notifyChange()
  }
  
  private notifyChange(): void {
    // 触发重新渲染
    this.onConfigChange?.(this.currentConfig)
  }
}
```

#### 2. 预设样式定义
```typescript
const PRESET_STYLES: PresetStyle[] = [
  {
    name: '商务风格',
    description: '深色调，简洁专业',
    config: {
      colorScheme: 'blue',
      lineWidth: 'medium',
      lineStyle: 'solid',
      fontSize: 'medium',
      fontColor: 'fixed',
      theme: 'business',
      showShadow: false,
      shadowIntensity: 0
    }
  },
  {
    name: '休闲风格', 
    description: '暖色调，轻松愉快',
    config: {
      colorScheme: 'orange',
      lineWidth: 'thick',
      lineStyle: 'solid',
      fontSize: 'large',
      fontColor: 'auto',
      theme: 'casual',
      showShadow: true,
      shadowIntensity: 0.3
    }
  }
  // ... 更多预设
]
```

#### 3. 实时预览实现
```typescript
class StylePreview {
  private canvas: HTMLCanvasElement
  private renderer: VisualRenderer
  private routeData: RouteData
  
  async updatePreview(config: StyleConfig): Promise<void> {
    try {
      // 显示加载状态
      this.showLoading()
      
      // 应用新样式并重新渲染
      const styledCanvas = await this.renderer.renderRouteMap(this.routeData, config)
      
      // 更新预览显示
      this.updateCanvas(styledCanvas)
      
      // 隐藏加载状态
      this.hideLoading()
    } catch (error) {
      this.showError('样式应用失败，请重试')
    }
  }
}
```

## 验收标准

### 功能完整性验收
- [ ] 所有样式选项都能正常工作
- [ ] 实时预览功能正常，无明显延迟
- [ ] 重置功能能恢复到默认状态
- [ ] 预设样式方案能正确应用

### 用户体验验收
- [ ] 界面布局清晰，操作直观
- [ ] 样式切换响应时间 <500ms
- [ ] 加载状态有明确反馈
- [ ] 错误情况有友好提示

### 视觉效果验收
- [ ] 不同样式方案视觉差异明显
- [ ] 预设风格符合描述和预期
- [ ] 样式组合搭配和谐美观
- [ ] 在不同设备上显示一致

## 测试用例

### 基础功能测试
```
操作: 点击蓝色方案
期望: 路线图立即变为蓝色渐变

操作: 调整线条粗细为"粗"
期望: 路线变粗，其他元素不变

操作: 切换到商务风格
期望: 整体样式变为商务风格配置
```

### 组合功能测试
```
操作: 先选择橙色方案，再选择文艺风格
期望: 两个设置都生效，样式正确组合

操作: 多次快速切换颜色方案
期望: 每次切换都能正确响应，无卡顿

操作: 应用样式后点击重置
期望: 恢复到初始默认状态
```

### 异常情况测试
```
场景: 网络较慢时切换样式
期望: 显示加载状态，完成后正确更新

场景: 渲染过程中发生错误
期望: 显示错误提示，不影响其他功能

场景: 连续快速点击样式选项
期望: 防抖处理，最终状态正确
```

## 依赖关系

- **前置条件**: spec-1.3 视觉渲染功能完成
- **阻塞因素**: 无
- **后续任务**: spec-1.6 用户界面功能

## 风险评估

- **技术风险**: 低，主要是UI交互逻辑
- **时间风险**: 低，功能相对简单
- **资源风险**: 低，不涉及大量计算

## 性能优化

### 响应性优化
- **防抖处理**: 避免频繁的样式切换导致性能问题
- **缓存机制**: 缓存已渲染的样式结果
- **异步渲染**: 使用Web Worker进行后台渲染

### 用户体验优化
- **预加载**: 预加载常用样式的预览图
- **渐进增强**: 基础功能优先，高级特效可选
- **响应式设计**: 适配不同屏幕尺寸的设备

---

**实施计划**:
1. 设计样式配置数据结构 (20分钟)
2. 实现样式管理和应用逻辑 (40分钟)
3. 开发用户界面和交互 (30分钟)
4. 实现实时预览功能 (30分钟)
5. 测试和优化用户体验 (20分钟)