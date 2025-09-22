# Spec 1.6 - 用户界面功能

## 基本信息
- **状态**: draft
- **优先级**: Should (用户体验)
- **预估时间**: 2小时
- **负责角色**: @CPO_Jobs + @CTO_Linus
- **Git分支**: feature/spec-1.6-ui-interface（实施时创建）

## 功能描述
设计和实现完整的用户界面，提供直观友好的交互体验，整合所有功能模块，确保用户能够轻松完成从输入到导出的完整流程。

## 详细需求

### 整体布局设计

#### 主界面结构
```
┌─────────────────────────────────────────────┐
│  🗺️ 旅游路线图生成器                          │
│  ─────────────────────────────────────────  │
│                                             │
│  📍 输入你的旅行地点                          │
│  ┌─────────────────────────────────────────┐ │
│  │ 例如：北京 西安 成都 重庆                 │ │
│  └─────────────────────────────────────────┘ │
│              [🎨 生成路线图]                 │
│                                             │
│  ┌─────────────────────────────────────────┐ │
│  │                                         │ │
│  │           路线图预览区域                 │ │
│  │                                         │ │
│  │                                         │ │
│  └─────────────────────────────────────────┘ │
│                                             │
│  🎨 样式调整                                 │
│  颜色: 🔵🟠🟢🟣🔴  粗细: ─ ── ═  风格: 💼🌸📚  │
│                                             │
│        [💾 保存图片]    [📤 分享]           │
└─────────────────────────────────────────────┘
```

#### 响应式设计规范
- **桌面端** (>1200px): 
  - 固定宽度1200px，居中布局
  - 预览区域800x600px
  - 侧边样式调整面板
- **平板端** (768px-1200px):
  - 全宽布局，左右边距20px
  - 预览区域自适应
  - 样式调整面板折叠
- **手机端** (<768px):
  - 全屏布局
  - 垂直堆叠所有元素
  - 按钮加大便于触摸

### 交互流程设计

#### 核心用户流程
```
1. 页面加载 → 显示输入框和示例
2. 用户输入 → 实时验证和提示
3. 点击生成 → 显示加载状态
4. 生成完成 → 显示路线图和样式调整
5. 调整样式 → 实时预览更新
6. 导出分享 → 完成流程
```

#### 状态管理
- **初始状态**: 显示输入框和使用说明
- **输入状态**: 实时验证用户输入
- **生成状态**: 显示进度条和生成提示
- **预览状态**: 显示路线图和调整选项
- **导出状态**: 显示导出进度和结果

### 组件设计规范

#### 1. 输入组件 (LocationInput)
```typescript
interface LocationInputProps {
  placeholder: string
  onInputChange: (value: string) => void
  onGenerate: () => void
  isLoading: boolean
  error?: string
  suggestions?: string[]
}
```

**设计要求**:
- 大号输入框，易于输入
- 智能提示和自动补全
- 输入验证和错误提示
- 生成按钮状态管理

#### 2. 预览组件 (RoutePreview)
```typescript
interface RoutePreviewProps {
  routeData?: RouteData
  styleConfig: StyleConfig
  isLoading: boolean
  error?: string
}
```

**设计要求**:
- 居中显示路线图
- 加载状态动画
- 错误状态提示
- 支持缩放查看

#### 3. 样式调整组件 (StyleAdjuster)
```typescript
interface StyleAdjusterProps {
  currentStyle: StyleConfig
  onStyleChange: (config: StyleConfig) => void
  disabled: boolean
}
```

**设计要求**:
- 直观的选择界面
- 实时预览效果
- 重置功能
- 响应式布局

#### 4. 导出分享组件 (ExportShare)
```typescript
interface ExportShareProps {
  routeData?: RouteData
  onExport: (format: ExportFormat) => void
  onShare: (platform: SocialPlatform) => void
  isExporting: boolean
}
```

**设计要求**:
- 清晰的操作按钮
- 格式选择选项
- 分享平台图标
- 操作反馈提示

## 视觉设计规范

### 色彩系统
- **主色调**: #4A90E2 (品牌蓝)
- **辅助色**: #7ED321 (成功绿), #F5A623 (警告橙), #D0021B (错误红)
- **中性色**: #333333 (深灰), #666666 (中灰), #999999 (浅灰)
- **背景色**: #FFFFFF (纯白), #F8F9FA (浅灰背景)

### 字体规范
- **标题字体**: 24px, 粗体, #333333
- **正文字体**: 16px, 常规, #666666
- **按钮字体**: 16px, 中粗, #FFFFFF
- **提示字体**: 14px, 常规, #999999

### 间距系统
- **基础间距**: 8px的倍数 (8px, 16px, 24px, 32px)
- **组件间距**: 24px
- **内容边距**: 16px
- **按钮内边距**: 12px 24px

### 圆角和阴影
- **按钮圆角**: 6px
- **卡片圆角**: 8px
- **输入框圆角**: 4px
- **阴影**: 0 2px 8px rgba(0,0,0,0.1)

## 技术实现

### 组件架构
```vue
<!-- 主应用组件 -->
<template>
  <div class="app-container">
    <Header />
    <LocationInput 
      @generate="handleGenerate"
      :is-loading="appState === 'generating'"
    />
    <RoutePreview 
      :route-data="routeData"
      :style-config="styleConfig"
      :is-loading="appState === 'generating'"
    />
    <template v-if="routeData">
      <StyleAdjuster 
        :current-style="styleConfig"
        @style-change="handleStyleChange"
      />
      <ExportShare 
        :route-data="routeData"
        @export="handleExport"
        @share="handleShare"
      />
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import type { AppState, RouteData, StyleConfig } from '@/types'

const appState = ref<AppState>('input')
const routeData = ref<RouteData>()
const styleConfig = reactive<StyleConfig>(defaultStyle)

const handleGenerate = async (input: string) => {
  // 处理路线生成
}

const handleStyleChange = (newStyle: StyleConfig) => {
  Object.assign(styleConfig, newStyle)
}

const handleExport = (format: string) => {
  // 处理导出
}

const handleShare = (platform: string) => {
  // 处理分享
}
</script>
```

### 状态管理
```typescript
// 使用Pinia进行状态管理
import { defineStore } from 'pinia'

export const useAppStore = defineStore('app', {
  state: () => ({
    appState: 'input' as AppState,
    routeData: null as RouteData | null,
    styleConfig: { ...defaultStyle } as StyleConfig,
    error: null as string | null
  }),
  
  actions: {
    async generateRoute(input: string) {
      this.appState = 'generating'
      try {
        const result = await routeService.generate(input)
        this.routeData = result
        this.appState = 'preview'
      } catch (error) {
        this.error = error.message
        this.appState = 'input'
      }
    },
    
    updateStyle(config: StyleConfig) {
      this.styleConfig = { ...this.styleConfig, ...config }
    },
    
    async exportImage(format: ExportFormat) {
      this.appState = 'exporting'
      try {
        await exportService.export(this.routeData, format)
      } finally {
        this.appState = 'preview'
      }
    },
    
    async shareToSocial(platform: SocialPlatform) {
      await shareService.share(this.routeData, platform)
    }
  }
})

type AppState = 'input' | 'generating' | 'preview' | 'exporting'
```

### 响应式实现
```css
/* 桌面端 */
@media (min-width: 1200px) {
  .app-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 40px 20px;
  }
  
  .preview-area {
    width: 800px;
    height: 600px;
  }
}

/* 平板端 */
@media (min-width: 768px) and (max-width: 1199px) {
  .app-container {
    padding: 20px;
  }
  
  .preview-area {
    width: 100%;
    height: 400px;
  }
}

/* 手机端 */
@media (max-width: 767px) {
  .app-container {
    padding: 16px;
  }
  
  .preview-area {
    width: 100%;
    height: 300px;
  }
  
  .style-adjuster {
    flex-direction: column;
  }
  
  .export-buttons {
    flex-direction: column;
    gap: 12px;
  }
}
```

## 验收标准

### 功能完整性验收
- [ ] 所有组件正常渲染和交互
- [ ] 用户流程完整无阻断
- [ ] 状态切换正确，无异常状态
- [ ] 错误处理完善，用户体验友好

### 视觉设计验收
- [ ] 界面美观，符合设计规范
- [ ] 色彩搭配和谐，层次清晰
- [ ] 字体大小合适，易于阅读
- [ ] 间距布局合理，不拥挤

### 响应式验收
- [ ] 在不同设备上显示正常
- [ ] 触摸操作友好，按钮大小合适
- [ ] 内容自适应，无横向滚动
- [ ] 关键功能在小屏幕上可用

### 性能验收
- [ ] 页面加载时间 <3秒
- [ ] 交互响应时间 <200ms
- [ ] 动画流畅，无卡顿
- [ ] 内存使用合理

## 测试用例

### 基础交互测试
```
操作: 在输入框中输入地名
期望: 实时验证，显示提示信息

操作: 点击生成按钮
期望: 显示加载状态，按钮变为不可点击

操作: 生成完成后调整样式
期望: 预览区域实时更新
```

### 响应式测试
```
测试: 在不同屏幕尺寸下访问
期望: 布局自适应，功能完整

测试: 手机端触摸操作
期望: 按钮大小合适，操作流畅

测试: 平板端横竖屏切换
期望: 布局正确调整
```

### 异常情况测试
```
场景: 网络断开时生成路线图
期望: 显示网络错误，提供重试选项

场景: 输入无效地名
期望: 显示友好错误提示

场景: 浏览器不支持某些功能
期望: 降级处理，核心功能可用
```

## 依赖关系

- **前置条件**: 所有功能模块(spec-1.1到1.5, spec-1.7)完成
- **阻塞因素**: 无
- **后续任务**: 整体测试和优化

## 风险评估

- **技术风险**: 低，主要是UI开发
- **时间风险**: 中等，响应式适配需要时间
- **资源风险**: 低，不涉及复杂计算

---

**实施计划**:
1. 搭建基础组件架构 (30分钟)
2. 实现主要UI组件 (60分钟)
3. 开发响应式布局 (30分钟)
4. 集成所有功能模块 (30分钟)
5. 测试和优化用户体验 (30分钟)