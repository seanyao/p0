# Spec 1.3 - 智能风格定制系统

## 基本信息
- **状态**: draft
- **优先级**: Must (核心功能)
- **预估时间**: 3小时
- **负责角色**: @CPO_Jobs + @CTO_Linus
- **Git分支**: feature/spec-1.3-style-customization（实施时创建）

## 🎨 功能描述
基于AI的智能风格定制系统，让用户通过简单的交互就能创造出个性化的艺术风格，同时提供专业级的细节调整选项。

## 🧠 AI风格推荐

### 1. 智能风格匹配
```typescript
interface StyleRecommendationEngine {
  // 基于旅行类型推荐风格
  recommendByTravelType(travelType: TravelType): Promise<StyleRecommendation[]>
  
  // 基于情感分析推荐风格
  recommendByMood(userInput: string): Promise<StyleRecommendation[]>
  
  // 基于用户历史偏好推荐
  recommendByHistory(userProfile: UserProfile): Promise<StyleRecommendation[]>
  
  // 基于时间和季节推荐
  recommendBySeason(timeframe: TimeFrame, location: Location): Promise<StyleRecommendation[]>
}

interface StyleRecommendation {
  style: ArtisticStyle
  confidence: number        // 推荐置信度 0-1
  reason: string           // 推荐理由
  preview: PreviewImage    // 预览图
  tags: string[]          // 风格标签
  mood: EmotionalMood     // 情感基调
}
```

### 2. 情感色彩分析
```typescript
class EmotionalColorAnalyzer {
  async analyzeUserMood(input: string): Promise<EmotionalProfile> {
    const emotions = await this.extractEmotions(input)
    const colors = this.mapEmotionsToColors(emotions)
    
    return {
      primary_emotion: emotions.dominant,
      color_palette: colors,
      energy_level: emotions.energy,
      warmth_preference: emotions.warmth
    }
  }
  
  private mapEmotionsToColors(emotions: EmotionAnalysis): ColorPalette {
    const colorMap = {
      excitement: ['#FF6B35', '#F7931E', '#FFD23F'],
      peace: ['#87CEEB', '#B0E0E6', '#E0F6FF'],
      romance: ['#FF69B4', '#FFB6C1', '#FFC0CB'],
      adventure: ['#FF4500', '#FF6347', '#FFA500'],
      nostalgia: ['#DEB887', '#F5DEB3', '#FFEFD5'],
      mystery: ['#4B0082', '#663399', '#8A2BE2']
    }
    
    return colorMap[emotions.dominant] || colorMap.peace
  }
}
```

## 🎭 风格定制界面

### 1. 直观的风格选择器
```vue
<template>
  <div class="style-customization">
    <!-- AI推荐区域 -->
    <div class="ai-recommendations">
      <h3>🤖 AI为你推荐</h3>
      <div class="recommendation-grid">
        <StyleCard 
          v-for="rec in aiRecommendations"
          :key="rec.style.id"
          :recommendation="rec"
          @select="selectStyle"
          class="recommended-style"
        >
          <div class="recommendation-reason">
            <Icon name="sparkles" />
            {{ rec.reason }}
          </div>
        </StyleCard>
      </div>
    </div>
    
    <!-- 风格画廊 -->
    <div class="style-gallery">
      <h3>🎨 风格画廊</h3>
      <div class="style-categories">
        <CategoryTab 
          v-for="category in styleCategories"
          :key="category.name"
          :category="category"
          :active="activeCategory === category.name"
          @click="setActiveCategory"
        />
      </div>
      
      <div class="style-grid">
        <StylePreview
          v-for="style in filteredStyles"
          :key="style.id"
          :style="style"
          :selected="selectedStyle?.id === style.id"
          @select="selectStyle"
          @preview="showPreview"
        />
      </div>
    </div>
    
    <!-- 实时预览 -->
    <div class="live-preview">
      <h3>👀 实时预览</h3>
      <div class="preview-container">
        <canvas 
          ref="previewCanvas"
          class="preview-canvas"
          @click="showFullPreview"
        />
        <div class="preview-controls">
          <button @click="regeneratePreview" class="regenerate-btn">
            <Icon name="refresh" /> 重新生成
          </button>
          <button @click="saveStyle" class="save-btn">
            <Icon name="heart" /> 保存风格
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
```

### 2. 高级定制面板
```vue
<template>
  <div class="advanced-customization">
    <!-- 色彩调整 -->
    <div class="color-section">
      <h4>🌈 色彩调整</h4>
      <ColorPalettePicker 
        v-model="customStyle.colorPalette"
        :suggestions="colorSuggestions"
        @change="updatePreview"
      />
      
      <div class="color-controls">
        <SliderControl
          label="饱和度"
          v-model="customStyle.saturation"
          :min="0" :max="2" :step="0.1"
          @input="updatePreview"
        />
        <SliderControl
          label="对比度"
          v-model="customStyle.contrast"
          :min="0" :max="2" :step="0.1"
          @input="updatePreview"
        />
        <SliderControl
          label="色温"
          v-model="customStyle.temperature"
          :min="-100" :max="100" :step="5"
          @input="updatePreview"
        />
      </div>
    </div>
    
    <!-- 纹理效果 -->
    <div class="texture-section">
      <h4>🖌️ 纹理效果</h4>
      <TextureSelector
        v-model="customStyle.texture"
        :options="textureOptions"
        @change="updatePreview"
      />
      
      <SliderControl
        label="纹理强度"
        v-model="customStyle.textureIntensity"
        :min="0" :max="1" :step="0.05"
        @input="updatePreview"
      />
    </div>
    
    <!-- 光影效果 -->
    <div class="lighting-section">
      <h4>💡 光影效果</h4>
      <div class="lighting-controls">
        <DirectionPicker
          label="光源方向"
          v-model="customStyle.lightDirection"
          @change="updatePreview"
        />
        <SliderControl
          label="光照强度"
          v-model="customStyle.lightIntensity"
          :min="0" :max="2" :step="0.1"
          @input="updatePreview"
        />
        <SliderControl
          label="阴影深度"
          v-model="customStyle.shadowDepth"
          :min="0" :max="1" :step="0.05"
          @input="updatePreview"
        />
      </div>
    </div>
  </div>
</template>
```

## 🎨 风格系统架构

### 1. 风格数据结构
```typescript
interface CustomStyle {
  id: string
  name: string
  category: StyleCategory
  
  // 基础风格
  baseStyle: ArtisticStyle
  
  // 色彩配置
  colorPalette: ColorPalette
  saturation: number
  contrast: number
  temperature: number
  
  // 纹理配置
  texture: TextureType
  textureIntensity: number
  brushStyle: BrushStyle
  
  // 光影配置
  lightDirection: Vector3
  lightIntensity: number
  shadowDepth: number
  ambientLight: number
  
  // 特效配置
  effects: VisualEffect[]
  animation: AnimationConfig
  
  // 元数据
  tags: string[]
  mood: EmotionalMood
  popularity: number
  created_at: Date
  user_id?: string
}

interface ColorPalette {
  primary: string[]      // 主色调 3-5个颜色
  secondary: string[]    // 辅助色 2-3个颜色
  accent: string        // 强调色
  background: string    // 背景色
  text: string         // 文字色
}
```

### 2. 风格渲染引擎
```typescript
class StyleRenderEngine {
  async applyCustomStyle(
    baseImage: HTMLCanvasElement,
    style: CustomStyle
  ): Promise<HTMLCanvasElement> {
    
    // 1. 应用基础艺术风格
    let styledImage = await this.applyBaseStyle(baseImage, style.baseStyle)
    
    // 2. 调整色彩
    styledImage = this.adjustColors(styledImage, {
      palette: style.colorPalette,
      saturation: style.saturation,
      contrast: style.contrast,
      temperature: style.temperature
    })
    
    // 3. 应用纹理
    styledImage = await this.applyTexture(styledImage, {
      type: style.texture,
      intensity: style.textureIntensity,
      brush: style.brushStyle
    })
    
    // 4. 添加光影效果
    styledImage = this.applyLighting(styledImage, {
      direction: style.lightDirection,
      intensity: style.lightIntensity,
      shadowDepth: style.shadowDepth,
      ambient: style.ambientLight
    })
    
    // 5. 应用特效
    for (const effect of style.effects) {
      styledImage = await this.applyEffect(styledImage, effect)
    }
    
    return styledImage
  }
  
  private adjustColors(
    image: HTMLCanvasElement, 
    colorConfig: ColorConfig
  ): HTMLCanvasElement {
    const canvas = document.createElement('canvas')
    const ctx = canvas.getContext('2d')!
    
    canvas.width = image.width
    canvas.height = image.height
    ctx.drawImage(image, 0, 0)
    
    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height)
    const data = imageData.data
    
    // 应用色彩映射
    for (let i = 0; i < data.length; i += 4) {
      const [r, g, b] = [data[i], data[i + 1], data[i + 2]]
      
      // 色彩重映射
      const mappedColor = this.mapToColorPalette([r, g, b], colorConfig.palette)
      
      // 调整饱和度和对比度
      const adjusted = this.adjustSaturationContrast(
        mappedColor, 
        colorConfig.saturation, 
        colorConfig.contrast
      )
      
      // 调整色温
      const final = this.adjustTemperature(adjusted, colorConfig.temperature)
      
      data[i] = final[0]
      data[i + 1] = final[1] 
      data[i + 2] = final[2]
    }
    
    ctx.putImageData(imageData, 0, 0)
    return canvas
  }
}
```

## 🎯 智能预设系统

### 1. 场景化预设
```typescript
interface ScenePreset {
  name: string
  description: string
  icon: string
  style: CustomStyle
  suitableFor: TravelType[]
  mood: EmotionalMood
  examples: PreviewImage[]
}

const SCENE_PRESETS: ScenePreset[] = [
  {
    name: '日系小清新',
    description: '温柔的色调，如春日暖阳般治愈',
    icon: '🌸',
    style: {
      baseStyle: ArtisticStyle.WATERCOLOR,
      colorPalette: {
        primary: ['#FFE4E1', '#FFF8DC', '#F0F8FF'],
        secondary: ['#FFB6C1', '#DDA0DD'],
        accent: '#FF69B4',
        background: '#FFFAF0',
        text: '#696969'
      },
      saturation: 0.8,
      contrast: 0.9,
      temperature: 10
    },
    suitableFor: ['romantic', 'cultural', 'nature'],
    mood: 'peaceful'
  },
  
  {
    name: '赛博朋克',
    description: '未来感十足的霓虹色彩，科技与艺术的碰撞',
    icon: '🌃',
    style: {
      baseStyle: ArtisticStyle.NEON,
      colorPalette: {
        primary: ['#00FFFF', '#FF00FF', '#FFFF00'],
        secondary: ['#8A2BE2', '#00CED1'],
        accent: '#FF1493',
        background: '#000000',
        text: '#FFFFFF'
      },
      saturation: 1.5,
      contrast: 1.3,
      temperature: -20
    },
    suitableFor: ['urban', 'adventure'],
    mood: 'energetic'
  }
]
```

### 2. 用户风格学习
```typescript
class StyleLearningEngine {
  private userPreferences: Map<string, UserStyleProfile> = new Map()
  
  async learnFromUserBehavior(
    userId: string, 
    interaction: StyleInteraction
  ): Promise<void> {
    const profile = this.getUserProfile(userId)
    
    // 更新用户偏好
    profile.updatePreferences(interaction)
    
    // 分析风格趋势
    const trends = this.analyzeStyleTrends(profile.history)
    
    // 生成个性化推荐
    const recommendations = await this.generatePersonalizedStyles(trends)
    
    // 缓存推荐结果
    await this.cacheRecommendations(userId, recommendations)
  }
  
  private analyzeStyleTrends(history: StyleInteraction[]): StyleTrends {
    const colorPreferences = this.extractColorPreferences(history)
    const texturePreferences = this.extractTexturePreferences(history)
    const moodPreferences = this.extractMoodPreferences(history)
    
    return {
      favoriteColors: colorPreferences,
      preferredTextures: texturePreferences,
      emotionalTendency: moodPreferences,
      complexity: this.calculateComplexityPreference(history)
    }
  }
}
```

## 📱 移动端优化

### 1. 触控友好的界面
```vue
<template>
  <div class="mobile-style-editor">
    <!-- 手势控制的色彩选择器 -->
    <div class="color-wheel-container">
      <ColorWheel
        v-model="selectedColor"
        @pan="handleColorPan"
        @pinch="handleColorZoom"
        class="touch-color-wheel"
      />
    </div>
    
    <!-- 滑动式风格预览 -->
    <div class="style-carousel">
      <Swiper
        :slides-per-view="1.2"
        :space-between="20"
        :centered-slides="true"
        @slide-change="onStyleChange"
      >
        <SwiperSlide 
          v-for="style in styles"
          :key="style.id"
          class="style-slide"
        >
          <StylePreviewCard :style="style" />
        </SwiperSlide>
      </Swiper>
    </div>
    
    <!-- 快速调整控件 -->
    <div class="quick-controls">
      <TouchSlider
        label="氛围"
        v-model="mood"
        :options="moodOptions"
        @change="updateMood"
      />
      <TouchSlider
        label="色彩"
        v-model="colorIntensity"
        :min="0" :max="2"
        @change="updateColorIntensity"
      />
    </div>
  </div>
</template>
```

### 2. 性能优化
```typescript
class MobileStyleOptimizer {
  // 降低移动端渲染复杂度
  async optimizeForMobile(style: CustomStyle): Promise<CustomStyle> {
    return {
      ...style,
      // 减少纹理复杂度
      textureIntensity: Math.min(style.textureIntensity, 0.7),
      
      // 简化特效
      effects: style.effects.filter(effect => 
        effect.performance_cost < PerformanceCost.HIGH
      ),
      
      // 优化色彩数量
      colorPalette: this.simplifyColorPalette(style.colorPalette)
    }
  }
  
  // 渐进式加载
  async loadStyleProgressively(
    styleId: string,
    onProgress: (progress: number) => void
  ): Promise<CustomStyle> {
    // 先加载基础配置
    onProgress(0.3)
    const baseConfig = await this.loadBaseConfig(styleId)
    
    // 再加载纹理资源
    onProgress(0.6)
    const textures = await this.loadTextures(baseConfig.texture)
    
    // 最后加载特效
    onProgress(1.0)
    const effects = await this.loadEffects(baseConfig.effects)
    
    return { ...baseConfig, textures, effects }
  }
}
```

## ✅ 验收标准

### 用户体验
- [ ] 风格选择直观易用，3步内完成定制
- [ ] 实时预览响应速度 <2秒
- [ ] AI推荐准确率 >75%
- [ ] 移动端操作流畅自然

### 功能完整性
- [ ] 支持8种以上基础艺术风格
- [ ] 提供20+个场景化预设
- [ ] 色彩、纹理、光影全面可调
- [ ] 用户自定义风格可保存和分享

### 技术性能
- [ ] 风格应用时间 <5秒
- [ ] 内存使用 <200MB
- [ ] 支持离线风格预览
- [ ] 兼容主流移动设备

## 🔗 依赖关系

- **前置条件**: 
  - 艺术渲染引擎完成
  - 用户认证系统
  - 风格素材库准备
- **阻塞因素**: 
  - AI风格推荐算法调优
  - 移动端性能优化
- **后续任务**: 
  - 社区风格分享功能
  - 风格市场和付费风格

---

**🎨 设计理念**: "让每个人都能成为艺术家，用简单的交互创造独特的视觉风格"