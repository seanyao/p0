# 项目规则文档

本目录包含项目的所有规则和规范文档，按功能模块拆分便于查看和管理。

## 📋 文档索引

### 核心规范
- **[项目规范](./project_rules.md)** - Specs Workflow、任务规范、最佳实践
- **[Git 分支策略](./git_workflow.md)** - 分支管理、协作流程、冲突处理

### 角色定义
- **[Jobs/Musk 产品决策角色](./jobs_musk_role.md)** - 产品需求评估、优先级决策、用户体验标准
- **[Linus 技术实施角色](./linus_role.md)** - 技术架构、代码实现、系统优化

## 🎯 快速导航

### 产品决策
- 需要评估新需求？→ [Jobs/Musk 角色 - 需求评估方法](./jobs_musk_role.md#需求评估三步法)
- 要确定功能优先级？→ [Jobs/Musk 角色 - Moscow决策框架](./jobs_musk_role.md#moscow-优先级决策框架)
- 制定产品愿景？→ [Jobs/Musk 角色 - 产品愿景制定](./jobs_musk_role.md#产品愿景制定)

### 日常开发
- 想记录新想法？→ [项目规范 - Specs Workflow](./project_rules.md#specs-workflow简化版)
- 要开始实施功能？→ [Git 分支策略 - 工作流程](./git_workflow.md#分支工作流程)
- 遇到代码冲突？→ [Git 分支策略 - 冲突处理](./git_workflow.md#冲突处理)

### 团队协作
- 多人协作开发？→ [Git 分支策略 - 团队协作](./git_workflow.md#团队协作)
- 代码审查流程？→ [Git 分支策略 - 代码审查](./git_workflow.md#代码审查流程)
- 紧急修复处理？→ [Git 分支策略 - 紧急修复](./git_workflow.md#紧急修复)

### 技术实施
- 需求分析方法？→ [Linus 角色定义 - 需求确认流程](./linus_role.md#需求确认流程)
- 代码审查标准？→ [Linus 角色定义 - 代码审查输出](./linus_role.md#代码审查输出)
- 技术决策原则？→ [Linus 角色定义 - 核心哲学](./linus_role.md#我的核心哲学)

## 🔄 规则更新历史

### v2.0 (当前版本)
- ✅ 拆分规则文档为独立模块
- ✅ 简化Spec状态管理（5个状态）
- ✅ 集成Git分支策略
- ✅ 支持"先记录，后实施"工作方式
- ✅ 添加详细的工作流程指导

### v1.0 (历史版本)
- 单一规则文件
- 复杂的状态管理
- 基础的Specs Workflow

## 💡 使用建议

### 新手入门
1. 先阅读 [项目规范](./project_rules.md) 了解基本工作流
2. 学习 [Git 分支策略](./git_workflow.md) 掌握协作方式
3. 参考 [Linus 角色定义](./linus_role.md) 理解分析方法

### 日常参考
- 开发前：检查项目规范中的状态定义
- 开发中：遵循Git分支策略的最佳实践
- 遇到问题：使用Linus式问题分析方法

### 团队管理
- 定期回顾规则执行情况
- 根据实际使用情况调整规范
- 保持规则文档的及时更新

## 🎯 核心原则

### 简洁性
- **5个状态**：draft / in_progress / completed / blocked / cancelled
- **清晰流程**：想法记录 → 实施开发 → 完成合并
- **最小复杂度**：避免过度设计和不必要的流程

### 实用性
- **解决真实问题**：支持"先记录后实施"的实际需求
- **工具集成**：与Git分支策略无缝配合
- **团队友好**：便于多人协作和并行开发

### 可维护性
- **模块化文档**：按功能拆分，便于查找和更新
- **版本控制**：规则变更有明确的历史记录
- **持续改进**：根据使用反馈不断优化

---

**"Good rules are like good code - simple, clear, and they solve real problems."** - Linus Torvalds