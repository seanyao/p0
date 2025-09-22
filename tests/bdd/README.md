# AI路线规划BDD集成测试

## 概述

本测试套件采用行为驱动开发(BDD)方法，为AI路线规划系统提供端到端的集成测试，重点覆盖LLM服务和视觉渲染功能的关键路径。

## 测试架构

```
tests/bdd/
├── features/                    # Gherkin特性文件
│   └── ai_route_planning.feature
├── step_definitions/           # 步骤定义
│   └── ai_route_steps.py
├── test_critical_path.py       # 关键路径测试
├── conftest.py                 # 测试配置和fixtures
├── pytest.ini                 # pytest配置
├── run_tests.py               # 测试运行脚本
└── README.md                  # 本文档
```

## 关键路径测试覆盖

### 🎯 核心业务流程
- **用户输入解析**: 自然语言 → 结构化地点数据
- **LLM服务集成**: 地点解析 + 路线生成
- **视觉渲染**: 路线数据 → 可视化地图
- **端到端流程**: 完整的用户体验路径

### 🔍 测试场景分类

#### 1. 关键路径测试 (`@critical_path`)
- ✅ 端到端自然语言输入测试
- ✅ 多种输入格式支持测试
- ✅ 复杂路线性能测试
- ✅ 视觉渲染质量验证
- ✅ API端点集成测试

#### 2. LLM集成测试 (`@llm_integration`)
- ✅ 地点解析准确性验证
- ✅ 路线生成逻辑测试
- ✅ LLM服务降级处理
- ✅ 多语言输入支持

#### 3. 视觉渲染测试 (`@visual_rendering`)
- ✅ 图像质量验证
- ✅ 可访问性标准检查
- ✅ 多设备适配测试
- ✅ 渲染性能优化

#### 4. 性能测试 (`@performance`)
- ✅ 响应时间基准测试
- ✅ 并发用户场景测试
- ✅ 大规模数据处理
- ✅ 资源使用监控

#### 5. 错误处理测试 (`@error_handling`)
- ✅ 服务异常降级处理
- ✅ 网络错误恢复机制
- ✅ 数据验证和清理
- ✅ 用户友好错误提示

#### 6. 边界情况测试 (`@edge_cases`)
- ✅ 单个地点处理
- ✅ 地点数量限制
- ✅ 无效地点过滤
- ✅ 重复地点去重

## 快速开始

### 1. 环境准备

```bash
# 安装测试依赖
pip install pytest pytest-asyncio httpx pytest-html

# 确保后端服务运行
cd backend && python3 main.py
```

### 2. 运行测试

```bash
# 进入测试目录
cd tests/bdd

# 运行所有关键路径测试
python run_tests.py all

# 运行冒烟测试（快速验证）
python run_tests.py smoke

# 运行性能测试
python run_tests.py performance

# 运行特定标记的测试
python run_tests.py --markers llm_integration visual_rendering
```

### 3. 查看测试报告

测试完成后，HTML报告将生成在 `tests/bdd/reports/` 目录中。

## 测试配置

### 环境变量
```bash
# 后端服务地址
export BACKEND_URL=http://localhost:8000

# LLM服务配置
export LLM_CONFIG_PATH=/path/to/llm_config.yaml

# 测试数据目录
export TEST_DATA_DIR=/path/to/test/data
```

### pytest标记说明

| 标记 | 描述 | 用途 |
|------|------|------|
| `critical_path` | 关键路径测试 | 核心业务流程验证 |
| `llm_integration` | LLM集成测试 | AI服务功能验证 |
| `visual_rendering` | 视觉渲染测试 | 图像生成质量验证 |
| `performance` | 性能测试 | 响应时间和吞吐量 |
| `error_handling` | 错误处理测试 | 异常情况处理 |
| `edge_cases` | 边界情况测试 | 极端输入处理 |
| `integration` | 集成测试 | API端点集成 |
| `concurrent_users` | 并发测试 | 多用户场景 |
| `smoke` | 冒烟测试 | 基本功能验证 |

## 测试数据

### 标准测试地点
```python
# 简单路线（3个地点）
simple_route = ["北京", "上海", "广州"]

# 复杂路线（8个地点）
complex_route = ["北京", "上海", "广州", "深圳", "杭州", "南京", "西安", "成都"]

# 边界情况
edge_cases = [
    "北京",  # 单个地点
    "北京 火星 上海",  # 包含无效地点
    "北京 北京 上海",  # 重复地点
]
```

### 性能基准
- **LLM解析**: < 5秒
- **路线生成**: < 3秒  
- **视觉渲染**: < 2秒
- **端到端流程**: < 10秒
- **并发成功率**: > 80%

## 测试最佳实践

### 1. 测试隔离
- 每个测试用例独立运行
- 使用fixtures管理测试数据
- 测试后自动清理资源

### 2. 错误处理
- 验证错误响应格式
- 检查错误码和消息
- 测试降级服务功能

### 3. 性能监控
- 记录关键操作耗时
- 监控资源使用情况
- 设置性能阈值告警

### 4. 可维护性
- 使用描述性测试名称
- 添加详细的测试文档
- 定期更新测试用例

## 故障排除

### 常见问题

#### 1. 后端服务连接失败
```bash
# 检查服务状态
python run_tests.py --check-backend

# 手动启动后端
cd backend && python3 main.py
```

#### 2. LLM服务配置错误
```bash
# 检查配置文件
cat backend/config/llm_config.yaml

# 验证API密钥
curl -H "Authorization: Bearer YOUR_API_KEY" https://api.openai.com/v1/models
```

#### 3. 测试依赖缺失
```bash
# 安装所有依赖
pip install -r requirements.txt

# 仅安装测试依赖
pip install pytest pytest-asyncio httpx pytest-html
```

#### 4. 权限问题
```bash
# 添加执行权限
chmod +x run_tests.py

# 检查文件权限
ls -la tests/bdd/
```

## 持续集成

### GitHub Actions示例
```yaml
name: BDD Integration Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Start backend service
        run: cd backend && python3 main.py &
      - name: Run BDD tests
        run: cd tests/bdd && python run_tests.py all
      - name: Upload test reports
        uses: actions/upload-artifact@v2
        with:
          name: test-reports
          path: tests/bdd/reports/
```

## 扩展测试

### 添加新的测试场景
1. 在 `features/` 中添加Gherkin场景
2. 在 `step_definitions/` 中实现步骤定义
3. 在 `test_critical_path.py` 中添加测试方法
4. 更新 `conftest.py` 中的fixtures

### 自定义测试标记
```python
# 在pytest.ini中添加新标记
markers =
    mobile: 移动端测试
    api_v2: API v2版本测试
    security: 安全性测试
```

## 贡献指南

1. 遵循现有的测试结构和命名规范
2. 为新功能添加相应的测试用例
3. 确保测试具有良好的可读性和可维护性
4. 更新相关文档和注释

## 联系方式

如有问题或建议，请联系开发团队或提交Issue。