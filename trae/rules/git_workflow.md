# Git 分支策略

## 分支命名规范

### 功能分支
```bash
feature/spec-{spec-number}-{brief-description}

# 示例
feature/spec-1.1-user-authentication
feature/spec-2.3-photo-compression
feature/spec-3.1-mobile-ui-optimization
```

### 修复分支
```bash
hotfix/fix-{issue-description}
bugfix/spec-{spec-number}-{bug-description}

# 示例
hotfix/fix-login-timeout
bugfix/spec-2.1-image-upload-error
```

## 分支工作流程

### 标准流程
1. **创建Spec** → 状态设为 `draft`
2. **准备实施** → 状态改为 `in_progress`
3. **创建分支** → `git checkout -b feature/spec-X.X-description`
4. **并行开发** → 多个分支同时进行
5. **测试验证** → 在分支内完成测试
6. **合并主线** → `git merge` 或 `git rebase`
7. **清理分支** → `git branch -d feature/spec-X.X-description`
8. **更新状态** → Spec状态改为 `completed`

### 分支管理最佳实践

#### 创建和切换
```bash
# 从main创建新功能分支
git checkout main
git pull origin main
git checkout -b feature/spec-2.1-photo-upload

# 切换到现有分支
git checkout feature/spec-2.2-image-compression
```

#### 定期同步
```bash
# 定期同步main分支的最新变更
git checkout main
git pull origin main
git checkout feature/spec-2.1-photo-upload
git rebase main  # 或 git merge main
```

#### 完成和清理
```bash
# 功能完成后合并到main
git checkout main
git merge feature/spec-2.1-photo-upload
git push origin main

# 删除本地分支
git branch -d feature/spec-2.1-photo-upload

# 删除远程分支（如果有）
git push origin --delete feature/spec-2.1-photo-upload
```

#### 实验性功能处理
```bash
# 实验失败，直接删除分支
git checkout main
git branch -D feature/spec-2.2-experimental-feature

# 无需复杂的代码回滚操作
```

## 分支状态管理

### 当前活跃分支查看
```bash
# 查看所有分支
git branch -a

# 查看分支状态
git status

# 查看分支历史
git log --oneline --graph --all
```

### 分支与Spec状态对应
```
Spec状态 → Git分支状态

draft        → 无分支（仅文档）
in_progress  → 有对应功能分支
completed    → 分支已合并并删除
blocked      → 分支暂停开发
cancelled    → 分支已删除
```

## 冲突处理

### 预防冲突
- **一个Spec一个分支**：保持功能隔离
- **定期同步主线**：避免冲突积累
- **小步快跑**：频繁提交，减少冲突范围

### 解决冲突
```bash
# 合并时遇到冲突
git merge main
# 手动解决冲突后
git add .
git commit -m "Resolve merge conflicts"

# 或使用rebase
git rebase main
# 解决冲突后
git add .
git rebase --continue
```

## 团队协作

### 多人协作同一功能
```bash
# 创建共享功能分支
git checkout -b feature/spec-3.1-complex-feature
git push -u origin feature/spec-3.1-complex-feature

# 其他人加入开发
git checkout feature/spec-3.1-complex-feature
git pull origin feature/spec-3.1-complex-feature
```

### 代码审查流程
1. 功能分支开发完成
2. 推送到远程仓库
3. 创建Pull Request/Merge Request
4. 代码审查和讨论
5. 审查通过后合并到main
6. 删除功能分支

## 风险控制

### 实验性功能
- **独立分支开发**：失败可直接删除
- **不影响主线**：main分支保持稳定
- **快速试错**：低成本验证想法

### 版本回滚
- **主线保护**：重要功能合并前充分测试
- **分支隔离**：问题分支可快速隔离
- **历史清晰**：每个功能有明确的提交历史

### 紧急修复
```bash
# 紧急修复流程
git checkout main
git checkout -b hotfix/fix-critical-bug
# 修复bug
git add .
git commit -m "Fix critical bug"
git checkout main
git merge hotfix/fix-critical-bug
git branch -d hotfix/fix-critical-bug
```

## 最佳实践总结

### ✅ 推荐做法
- 一个Spec对应一个功能分支
- 分支命名清晰描述功能
- 定期同步main分支变更
- 功能完成后及时清理分支
- 使用描述性的提交信息

### ❌ 避免做法
- 在main分支直接开发功能
- 长期不合并的功能分支
- 多个功能混在一个分支
- 不清理已完成的分支
- 强制推送覆盖历史

### 🎯 核心原则
- **隔离性**：每个功能独立开发
- **可追溯**：清晰的开发历史
- **可回滚**：安全的实验环境
- **简洁性**：避免复杂的分支结构