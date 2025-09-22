# AI路线规划关键路径集成测试
# 覆盖从用户输入到最终生图的完整业务流程

Feature: AI智能路线规划
  作为一个用户
  我想要输入旅游地点
  以便获得智能优化的路线图

  Background:
    Given 系统已启动并运行在 "http://localhost:8000"
    And LLM服务已正确配置
    And 视觉渲染服务已初始化

  @critical_path @llm_integration
  Scenario: 用户输入自然语言生成完整路线图
    Given 用户在输入框中输入 "我想去北京、上海、广州旅游"
    When 用户点击生成路线按钮
    Then 系统应该调用LLM服务解析地点
    And 应该识别出3个有效地点:
      | 地点名称 | 坐标范围验证 |
      | 北京     | 116.0-117.0, 39.0-40.0 |
      | 上海     | 121.0-122.0, 31.0-32.0 |
      | 广州     | 113.0-114.0, 23.0-24.0 |
    And 应该生成优化的路线连接
    And 应该渲染出完整的路线图
    And 图像应该包含所有地点标记
    And 路线应该使用平滑的贝塞尔曲线连接

  @critical_path @visual_rendering
  Scenario: 多种输入格式的路线生成
    Given 用户使用不同的输入格式
    When 用户输入 "<input_format>"
    Then 系统应该正确解析并生成路线图
    And 生成的图像应该符合视觉规范

    Examples:
      | input_format |
      | 北京→上海→广州 |
      | 北京，上海，广州 |
      | 帝都 魔都 花城 |

  @critical_path @error_handling
  Scenario: LLM服务异常时的降级处理
    Given LLM服务暂时不可用
    When 用户输入 "北京 上海 广州"
    Then 系统应该使用备用地点解析服务
    And 仍然能够生成基础路线图
    And 用户应该收到服务降级提示

  @performance @critical_path
  Scenario: 大规模路线的性能测试
    Given 用户输入包含8个城市的复杂路线
    When 系统处理路线生成请求
    Then LLM解析应该在5秒内完成
    And 路线生成应该在3秒内完成
    And 视觉渲染应该在2秒内完成
    And 总体响应时间应该在10秒内

  @visual_quality @critical_path
  Scenario: 视觉渲染质量验证
    Given 用户生成了一条包含5个地点的路线
    When 系统完成视觉渲染
    Then 生成的图像应该满足以下质量标准:
      | 质量指标 | 期望值 |
      | 图像分辨率 | >= 1200x800 |
      | 地点标记清晰度 | 所有标记可见且不重叠 |
      | 路线平滑度 | 使用贝塞尔曲线，无锯齿 |
      | 颜色对比度 | 符合WCAG 2.1 AA标准 |
      | 字体可读性 | 16px以上，清晰可读 |

  @integration @api_endpoints
  Scenario: API端点集成验证
    Given 系统提供完整的API服务
    When 客户端调用各个API端点
    Then 所有端点应该正常响应:
      | 端点 | 期望状态码 | 响应时间 |
      | GET /api/v1/ai/health | 200 | < 1s |
      | POST /api/v1/ai/parse-locations | 200 | < 5s |
      | POST /api/v1/ai/generate-route | 200 | < 8s |

  @data_flow @critical_path
  Scenario: 端到端数据流验证
    Given 用户开始一个完整的路线规划流程
    When 用户输入 "从杭州到苏州再到南京"
    Then 数据应该按以下流程传递:
      | 步骤 | 输入数据 | 输出数据 | 验证点 |
      | 1. 地点解析 | 自然语言文本 | LocationInfo[] | 坐标准确性 |
      | 2. 路线生成 | LocationInfo[] | RouteVisualization | 连接合理性 |
      | 3. 视觉渲染 | RouteVisualization | Canvas图像 | 视觉质量 |
    And 每个步骤的数据格式应该符合API规范
    And 数据传递应该无丢失或损坏

  @edge_cases @critical_path
  Scenario Outline: 边界情况处理
    Given 用户输入了边界情况的数据
    When 用户输入 "<edge_case_input>"
    Then 系统应该 "<expected_behavior>"
    And 应该返回适当的用户提示

    Examples:
      | edge_case_input | expected_behavior |
      | 北京 | 提示至少需要2个地点 |
      | 北京 上海 广州 深圳 杭州 南京 西安 成都 重庆 | 提示最多支持8个地点 |
      | 北京 火星 上海 | 识别有效地点，忽略无效地点 |
      | 北京 北京 上海 | 自动去重，提示重复地点 |

  @accessibility @visual_rendering
  Scenario: 可访问性和视觉规范验证
    Given 用户生成了路线图
    When 系统完成渲染
    Then 生成的图像应该符合可访问性标准:
      | 可访问性要求 | 验证标准 |
      | 颜色对比度 | 文字与背景对比度 >= 4.5:1 |
      | 字体大小 | 地点标签 >= 16px |
      | 色彩无障碍 | 支持色盲友好的颜色方案 |
      | 高DPI支持 | 支持Retina显示屏 |

  @concurrent_users @performance
  Scenario: 并发用户场景测试
    Given 系统同时处理多个用户请求
    When 10个用户同时发起路线生成请求
    Then 每个请求都应该在合理时间内完成
    And 系统资源使用应该保持稳定
    And 不应该出现请求丢失或错误

  @cache_optimization @performance
  Scenario: 缓存优化验证
    Given 用户首次生成某条路线
    When 用户再次生成相同的路线
    Then 第二次生成应该显著更快
    And 应该利用缓存的LLM解析结果
    And 视觉渲染可以复用样式配置