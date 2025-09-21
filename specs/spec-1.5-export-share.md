# Spec 1.5 - 导出分享功能

## 基本信息
- **状态**: draft
- **优先级**: Must (核心功能)
- **预估时间**: 1.5小时
- **负责角色**: @CTO_Linus
- **Git分支**: feature/spec-1.5-export-share（实施时创建）

## 功能描述
提供高质量的图片导出和便捷的社交分享功能，支持多种尺寸格式和主流社交平台分享。

## 详细需求

### 导出格式支持

#### 图片格式
- **主要格式**: PNG (无损压缩，支持透明背景)
- **备用格式**: JPEG (文件更小，适合网络传输)
- **质量控制**: PNG无损，JPEG质量90%

#### 尺寸规格
- **方形格式**: 1080x1080px
  - 适用平台: Instagram、微信朋友圈
  - 文件大小: <2MB
- **横版格式**: 1920x1080px  
  - 适用平台: 微博、电脑壁纸
  - 文件大小: <3MB
- **自定义尺寸**: 支持用户自定义宽高比

#### 质量标准
- **分辨率**: 高清输出，适合打印和高分屏显示
- **色彩**: sRGB色彩空间，确保跨设备一致性
- **压缩**: 智能压缩，平衡文件大小和质量

### 分享功能

#### 本地保存
- **一键保存**: 直接保存到设备相册/下载文件夹
- **文件命名**: 自动生成有意义的文件名
  - 格式: `旅游路线图_北京-上海-广州_20240115.png`
- **保存反馈**: 保存成功后显示确认提示

#### 社交平台分享
- **微信分享**: 
  - 好友分享: 直接发送图片
  - 朋友圈分享: 带文案模板
- **微博分享**: 
  - 自动添加话题标签 #旅游路线图#
  - 提供文案模板
- **QQ空间分享**: 
  - 图片+文字描述
- **通用分享**: 
  - 系统原生分享菜单
  - 支持更多平台

#### 链接分享
- **分享链接**: 生成临时分享链接
- **预览页面**: 链接包含路线图预览
- **有效期**: 链接7天有效
- **访问统计**: 记录分享链接的访问次数

## 技术实现

### 核心接口设计
```typescript
interface ExportShare {
  // 导出图片
  exportImage(format: ExportFormat): Promise<ExportResult>
  
  // 保存到本地
  saveToLocal(imageBlob: Blob, filename: string): Promise<boolean>
  
  // 社交平台分享
  shareToSocial(platform: SocialPlatform, content: ShareContent): Promise<boolean>
  
  // 生成分享链接
  generateShareLink(routeData: RouteData): Promise<string>
}

interface ExportFormat {
  type: 'png' | 'jpeg'
  size: { width: number, height: number }
  quality?: number // 仅JPEG格式
  backgroundColor?: string
}

interface ExportResult {
  success: boolean
  blob?: Blob
  dataUrl?: string
  error?: string
  fileSize: number
}

interface ShareContent {
  image: Blob
  text: string
  hashtags?: string[]
  url?: string
}

type SocialPlatform = 'wechat' | 'weibo' | 'qq' | 'system'
```

### 导出实现

#### 1. Canvas转图片
```typescript
async function exportCanvasToImage(canvas: HTMLCanvasElement, format: ExportFormat): Promise<ExportResult> {
  try {
    // 创建高分辨率Canvas
    const exportCanvas = createHighResCanvas(canvas, format.size)
    
    // 转换为Blob
    const blob = await new Promise<Blob>((resolve, reject) => {
      exportCanvas.toBlob((blob) => {
        if (blob) resolve(blob)
        else reject(new Error('导出失败'))
      }, `image/${format.type}`, format.quality)
    })
    
    // 生成DataURL用于预览
    const dataUrl = exportCanvas.toDataURL(`image/${format.type}`, format.quality)
    
    return {
      success: true,
      blob,
      dataUrl,
      fileSize: blob.size
    }
  } catch (error) {
    return {
      success: false,
      error: error.message,
      fileSize: 0
    }
  }
}
```

#### 2. 高分辨率渲染
```typescript
function createHighResCanvas(sourceCanvas: HTMLCanvasElement, targetSize: Size): HTMLCanvasElement {
  const scale = Math.min(
    targetSize.width / sourceCanvas.width,
    targetSize.height / sourceCanvas.height
  )
  
  const exportCanvas = document.createElement('canvas')
  exportCanvas.width = targetSize.width
  exportCanvas.height = targetSize.height
  
  const ctx = exportCanvas.getContext('2d')!
  ctx.imageSmoothingEnabled = true
  ctx.imageSmoothingQuality = 'high'
  
  // 居中绘制
  const offsetX = (targetSize.width - sourceCanvas.width * scale) / 2
  const offsetY = (targetSize.height - sourceCanvas.height * scale) / 2
  
  ctx.drawImage(sourceCanvas, offsetX, offsetY, sourceCanvas.width * scale, sourceCanvas.height * scale)
  
  return exportCanvas
}
```

#### 3. 文件保存
```typescript
async function saveImageToLocal(blob: Blob, filename: string): Promise<boolean> {
  try {
    if ('showSaveFilePicker' in window) {
      // 现代浏览器：使用File System Access API
      const fileHandle = await window.showSaveFilePicker({
        suggestedName: filename,
        types: [{
          description: 'PNG图片',
          accept: { 'image/png': ['.png'] }
        }]
      })
      
      const writable = await fileHandle.createWritable()
      await writable.write(blob)
      await writable.close()
    } else {
      // 兼容性方案：使用下载链接
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = filename
      a.click()
      URL.revokeObjectURL(url)
    }
    
    return true
  } catch (error) {
    console.error('保存失败:', error)
    return false
  }
}
```

### 分享实现

#### 1. 社交平台分享
```typescript
async function shareToSocial(platform: SocialPlatform, content: ShareContent): Promise<boolean> {
  switch (platform) {
    case 'wechat':
      return shareToWechat(content)
    case 'weibo':
      return shareToWeibo(content)
    case 'system':
      return shareViaSystem(content)
    default:
      throw new Error(`不支持的平台: ${platform}`)
  }
}

async function shareViaSystem(content: ShareContent): Promise<boolean> {
  if ('share' in navigator) {
    try {
      await navigator.share({
        title: '我的旅游路线图',
        text: content.text,
        files: [new File([content.image], 'route-map.png', { type: 'image/png' })]
      })
      return true
    } catch (error) {
      return false
    }
  }
  return false
}
```

#### 2. 分享链接生成
```typescript
async function generateShareLink(routeData: RouteData): Promise<string> {
  // 上传路线图到临时存储
  const imageBlob = await exportRouteImage(routeData)
  const uploadResult = await uploadToTempStorage(imageBlob)
  
  // 生成分享页面
  const shareId = generateUniqueId()
  const shareData = {
    id: shareId,
    imageUrl: uploadResult.url,
    routeData: routeData,
    createdAt: Date.now(),
    expiresAt: Date.now() + 7 * 24 * 60 * 60 * 1000 // 7天后过期
  }
  
  await saveShareData(shareData)
  
  return `${window.location.origin}/share/${shareId}`
}
```

## 验收标准

### 功能完整性验收
- [ ] 支持PNG和JPEG两种格式导出
- [ ] 支持方形和横版两种尺寸
- [ ] 本地保存功能正常工作
- [ ] 主流社交平台分享功能正常

### 质量标准验收
- [ ] 导出图片清晰，无失真
- [ ] 文件大小控制在规定范围内
- [ ] 颜色在不同设备上显示一致
- [ ] 分享链接能正常访问和预览

### 用户体验验收
- [ ] 导出过程有进度提示
- [ ] 保存成功有明确反馈
- [ ] 分享操作简单直观
- [ ] 错误情况有友好提示

## 测试用例

### 基础功能测试
```
操作: 点击"保存图片"按钮
期望: 图片成功保存到本地，显示成功提示

操作: 选择微信分享
期望: 调起微信分享界面，图片正确传递

操作: 生成分享链接
期望: 生成有效链接，点击能正常预览
```

### 格式和质量测试
```
测试: 导出1080x1080 PNG格式
期望: 文件大小<2MB，图片清晰

测试: 导出1920x1080 JPEG格式  
期望: 文件大小<3MB，质量良好

测试: 在不同设备上查看导出图片
期望: 颜色和清晰度一致
```

### 异常情况测试
```
场景: 网络断开时生成分享链接
期望: 显示网络错误提示

场景: 存储空间不足时保存图片
期望: 显示存储空间不足提示

场景: 不支持的浏览器使用分享功能
期望: 降级到下载功能
```

## 依赖关系

- **前置条件**: spec-1.3 视觉渲染功能完成
- **阻塞因素**: 需要临时存储服务支持
- **后续任务**: 无

## 风险评估

- **技术风险**: 中等，不同浏览器的兼容性问题
- **时间风险**: 低，功能相对标准化
- **资源风险**: 中等，需要临时存储服务

## 性能优化

### 导出性能优化
- **异步处理**: 导出过程不阻塞UI
- **进度反馈**: 显示导出进度条
- **内存管理**: 及时释放大图片占用的内存

### 分享体验优化
- **预加载**: 预先准备分享内容
- **缓存机制**: 缓存已生成的分享链接
- **降级方案**: 不支持的功能提供替代方案

---

**实施计划**:
1. 实现Canvas到图片的导出功能 (30分钟)
2. 开发本地保存和下载功能 (30分钟)
3. 实现社交平台分享接口 (30分钟)
4. 开发分享链接生成功能 (20分钟)
5. 测试和兼容性优化 (20分钟)