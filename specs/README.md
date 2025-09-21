# 📋 Specs 目录说明

> **项目**: 旅游路线图工具 (TravelRouteMap)  
> **创建时间**: 2024年1月  
> **工作流程**: 遵循 [Specs Workflow 规范](../.trae/rules/specs_workflow.md)

## 目录结构

```
specs/
├── README.md                    # 本说明文档
├── spec-1.0-project-overview.md # 项目总览和架构设计
├── spec-1.1-location-parser.md  # 地名解析功能
├── spec-1.2-route-generator.md  # 路线生成功能  
├── spec-1.3-visual-renderer.md  # 视觉渲染功能
├── spec-1.4-style-adjuster.md   # 样式调整功能
├── spec-1.5-export-share.md     # 导出分享功能
└── spec-1.6-ui-interface.md     # 用户界面功能
```

## 状态说明

- **draft**: 想法记录，暂不实施
- **in_progress**: 正在开发中
- **completed**: 已完成
- **blocked**: 被外部因素阻塞
- **cancelled**: 已取消，不再需要

## 优先级说明

- **Must**: 核心功能，必须实现
- **Should**: 重要功能，优先实现
- **Could**: 增值功能，资源允许时实现
- **Won't**: 当前版本不做

## 开发流程

1. **创建Spec** → 状态 `draft`
2. **准备实施** → 状态 `in_progress`，创建Git分支
3. **开发完成** → 合并分支，状态 `completed`
4. **遇到问题** → 状态 `blocked` 或 `cancelled`

## 分支命名规范

```
spec-1.1 → feature/spec-1.1-location-parser
spec-1.2 → feature/spec-1.2-route-generator
```

---

**遵循原则**: 每个任务1-2小时完成，保持文档与代码同步更新