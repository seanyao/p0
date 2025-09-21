# 🗺️ 旅游路线图生成工具

一个基于 Vue 3 + TypeScript 的极简美观旅游路线图生成工具，让旅行规划变得简单而有趣。

## ✨ 产品特色

- **极简设计**: 一个输入框，一键生成，无需复杂操作
- **美观优先**: 精心设计的视觉效果，让路线图赏心悦目
- **智能解析**: 自动识别地名，智能规划最优路线
- **样式丰富**: 多种颜色、线条样式，个性化定制
- **便捷分享**: 一键导出高清图片，轻松分享旅行计划

## 🛠️ 技术栈

- **前端框架**: Vue 3 + TypeScript
- **构建工具**: Vite
- **状态管理**: Pinia
- **路由管理**: Vue Router
- **样式方案**: CSS3 + 响应式设计
- **后端服务**: Python FastAPI

## 🚀 快速开始

### 环境要求
- Node.js >= 16.0.0
- npm >= 8.0.0
- Python >= 3.8

### 安装依赖
```bash
npm install
```

### 启动开发服务器
```bash
npm run dev
```

### 构建生产版本
```bash
npm run build
```

## 📁 项目结构

```
travel-route-map/
├── specs/                    # 项目规范文档
│   ├── README.md            # 规范说明
│   ├── spec-1.0-project-overview.md
│   ├── spec-1.1-location-parser.md
│   ├── spec-1.2-route-generator.md
│   ├── spec-1.3-visual-renderer.md
│   ├── spec-1.4-style-adjuster.md
│   ├── spec-1.5-export-share.md
│   ├── spec-1.6-ui-interface.md
│   └── spec-2.0-future-features.md
├── src/                     # 源代码目录
├── public/                  # 静态资源
├── package.json            # 项目配置
└── README.md               # 项目说明
```

## 🛠️ 开发规范

本项目采用 **specs workflow** 开发流程，所有功能开发都基于详细的规范文档。

### 分支命名规范
- `feature/spec-x.x-功能名称` - 功能开发分支
- `bugfix/issue-描述` - 问题修复分支
- `hotfix/紧急修复描述` - 紧急修复分支

### 提交信息规范
```
feat: 新功能
fix: 修复问题
docs: 文档更新
style: 代码格式调整
refactor: 代码重构
test: 测试相关
chore: 构建工具或辅助工具的变动
```

## 📋 开发计划

### V1.0 核心功能 (MVP)
- [x] 项目规范和架构设计
- [ ] 地名解析功能 (spec-1.1)
- [ ] 路线生成算法 (spec-1.2)
- [ ] 视觉渲染引擎 (spec-1.3)
- [ ] 样式调整系统 (spec-1.4)
- [ ] 导出分享功能 (spec-1.5)
- [ ] 用户界面集成 (spec-1.6)

### V2.0+ 未来功能
详见 [未来功能规划](./specs/spec-2.0-future-features.md)

## 🎯 产品目标

- **用户体验**: 3秒内完成路线图生成
- **视觉质量**: 达到专业设计水准
- **功能完整度**: 覆盖90%的基础旅行规划需求
- **性能指标**: 页面加载时间 <2秒，交互响应 <200ms

## 🤝 贡献指南

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/spec-x.x-功能名称`)
3. 提交更改 (`git commit -m 'feat: 添加某功能'`)
4. 推送到分支 (`git push origin feature/spec-x.x-功能名称`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 联系我们

- 项目主页: [GitHub Repository](https://github.com/travel-route-map/travel-route-map)
- 问题反馈: [Issues](https://github.com/travel-route-map/travel-route-map/issues)
- 功能建议: [Discussions](https://github.com/travel-route-map/travel-route-map/discussions)

---

**让旅行规划变得简单而美好** ✈️