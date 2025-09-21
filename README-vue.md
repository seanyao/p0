# 旅游路线图工具 - Vue 3 + TypeScript版本

一个极简美观的旅游路线图生成工具，基于Vue 3 + TypeScript + Vite构建。

## ✨ 特性

- 🎯 **智能地名解析** - 支持中文地名、别名和多种输入格式
- 📍 **精确定位** - 基于高德地图API的高精度地理编码
- 🔄 **批量处理** - 支持批量解析多个地名
- 📱 **响应式设计** - 完美适配桌面和移动设备
- 💾 **历史记录** - 自动保存解析历史，便于重复使用
- 🚀 **现代技术栈** - Vue 3 + TypeScript + Vite + Pinia

## 🛠️ 技术栈

### 前端
- **Vue 3** - 渐进式JavaScript框架
- **TypeScript** - 类型安全的JavaScript超集
- **Vite** - 下一代前端构建工具
- **Pinia** - Vue的状态管理库
- **Vue Router** - Vue.js官方路由
- **Axios** - HTTP客户端
- **VueUse** - Vue组合式API工具集

### 后端
- **FastAPI** - 现代、快速的Python Web框架
- **Pydantic** - 数据验证和设置管理
- **Uvicorn** - ASGI服务器
- **高德地图API** - 地理编码服务

## 🚀 快速开始

### 环境要求

- Node.js >= 16.0.0
- Python >= 3.8
- npm >= 8.0.0

### 安装依赖

```bash
# 安装Vue前端依赖
npm install

# 安装Python后端依赖
cd backend
pip install -r requirements.txt
```

### 配置API密钥

1. 复制环境变量文件：
```bash
cp .env.example .env
```

2. 在`.env`文件中配置高德地图API密钥：
```env
VITE_AMAP_API_KEY=your_amap_api_key_here
VITE_AMAP_SECURITY_KEY=your_security_key_here
```

3. 在`backend/config.json`中配置后端API密钥：
```json
{
  "amap": {
    "api_key": "your_amap_api_key_here",
    "security_key": "your_security_key_here"
  }
}
```

### 启动服务

1. 启动后端服务：
```bash
cd backend
python main.py
```

2. 启动Vue前端服务：
```bash
# 使用Vue版本配置
npm run dev -- --config vite-vue.config.ts
```

3. 访问应用：
- 前端：http://localhost:3001
- 后端API：http://localhost:8000
- API文档：http://localhost:8000/docs

## 📁 项目结构

```
src-vue/                    # Vue源码目录
├── components/             # Vue组件
│   ├── LocationParser.vue  # 地名解析主组件
│   ├── LocationResult.vue  # 单个解析结果组件
│   ├── BatchLocationResult.vue # 批量解析结果组件
│   └── LocationHistory.vue # 历史记录组件
├── composables/            # 组合式函数
│   ├── useLocationParser.ts # 地名解析逻辑
│   ├── useLocationAutoComplete.ts # 自动完成逻辑
│   └── useLocationHistory.ts # 历史记录逻辑
├── services/               # 服务层
│   └── locationService.ts  # 地名解析API服务
├── types/                  # 类型定义
│   └── location.ts         # 地名相关类型
├── views/                  # 页面视图
│   └── Home.vue           # 首页
├── App.vue                # 根组件
├── main.ts                # 应用入口
└── style.css              # 全局样式

backend/                   # Python后端
├── app/                   # 应用代码
├── tests/                 # 测试代码
├── config.json           # 配置文件
├── main.py               # 应用入口
└── requirements.txt      # Python依赖
```

## 🎯 功能特性

### 地名解析
- 支持中文地名输入
- 智能别名识别（如：帝都→北京）
- 多种分隔符支持（逗号、分号、箭头等）
- 输入纠错和建议

### 批量处理
- 支持多种输入格式
- 并发解析提升性能
- 详细的解析统计
- 结果导出功能

### 用户体验
- 响应式设计
- 实时输入提示
- 历史记录管理
- 一键复制坐标
- 地图链接跳转

## 🧪 测试

### 运行测试
```bash
# 后端集成测试
cd backend
python -m pytest tests/ -v

# 前端单元测试（如果配置）
npm run test
```

### 测试覆盖
- API接口测试
- 地名解析功能测试
- 错误处理测试
- 性能测试

## 📦 构建部署

### 构建生产版本
```bash
# 构建Vue前端
npm run build -- --config vite-vue.config.ts

# 构建产物在 dist-vue/ 目录
```

### 部署建议
- 前端：可部署到Nginx、Apache或CDN
- 后端：可部署到Docker、云服务器或Serverless平台
- 数据库：建议使用Redis缓存提升性能

## 🤝 贡献指南

1. Fork本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 📄 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- [Vue.js](https://vuejs.org/) - 渐进式JavaScript框架
- [高德地图](https://lbs.amap.com/) - 地理信息服务
- [FastAPI](https://fastapi.tiangolo.com/) - 现代Python Web框架
- [Vite](https://vitejs.dev/) - 下一代前端构建工具