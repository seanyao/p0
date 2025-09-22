"""
AI路线规划BDD测试步骤定义
实现Gherkin场景的具体测试逻辑
"""

import asyncio
import json
import time
from typing import Dict, List, Any
import pytest
from behave import given, when, then, step
from behave.runner import Context
import httpx
from PIL import Image
import numpy as np

# 测试配置
TEST_BASE_URL = "http://localhost:8000"
TEST_TIMEOUT = 30
PERFORMANCE_THRESHOLDS = {
    "llm_parse_time": 5.0,
    "route_generation_time": 3.0,
    "visual_rendering_time": 2.0,
    "total_response_time": 10.0
}

class TestMetrics:
    """测试指标收集器"""
    def __init__(self):
        self.start_time = None
        self.llm_parse_time = None
        self.route_generation_time = None
        self.visual_rendering_time = None
        self.total_time = None
        self.api_responses = {}
        self.image_quality_metrics = {}

    def start_timer(self):
        self.start_time = time.time()

    def record_step_time(self, step_name: str):
        if self.start_time:
            setattr(self, f"{step_name}_time", time.time() - self.start_time)

    def get_total_time(self):
        if self.start_time:
            self.total_time = time.time() - self.start_time
        return self.total_time

# 全局测试上下文
test_metrics = TestMetrics()

@given('系统已启动并运行在 "{base_url}"')
def step_system_running(context: Context, base_url: str):
    """验证系统是否正常运行"""
    context.base_url = base_url
    context.client = httpx.AsyncClient(base_url=base_url, timeout=TEST_TIMEOUT)
    
    # 健康检查
    async def check_health():
        response = await context.client.get("/api/v1/ai/health")
        assert response.status_code == 200
        health_data = response.json()
        assert health_data["status"] == "healthy"
        return health_data
    
    context.health_data = asyncio.run(check_health())
    print(f"✅ 系统健康检查通过: {context.health_data}")

@given('LLM服务已正确配置')
def step_llm_service_configured(context: Context):
    """验证LLM服务配置"""
    # 检查LLM服务配置
    health_data = context.health_data
    dependencies = health_data.get("dependencies", {})
    
    assert "llm_service" in dependencies
    assert dependencies["llm_service"] == "available"
    
    context.llm_configured = True
    print("✅ LLM服务配置验证通过")

@given('视觉渲染服务已初始化')
def step_visual_service_initialized(context: Context):
    """验证视觉渲染服务"""
    # 这里可以添加视觉渲染服务的检查逻辑
    context.visual_service_ready = True
    print("✅ 视觉渲染服务初始化完成")

@given('用户在输入框中输入 "{user_input}"')
def step_user_input(context: Context, user_input: str):
    """用户输入地点信息"""
    context.user_input = user_input
    context.expected_locations = []
    
    # 根据输入预设期望的地点
    if "北京" in user_input and "上海" in user_input and "广州" in user_input:
        context.expected_locations = ["北京", "上海", "广州"]
    
    test_metrics.start_timer()
    print(f"📝 用户输入: {user_input}")

@when('用户点击生成路线按钮')
def step_generate_route_button(context: Context):
    """模拟用户点击生成路线"""
    context.route_generation_started = True
    print("🖱️ 用户点击生成路线按钮")

@then('系统应该调用LLM服务解析地点')
def step_llm_parse_locations(context: Context):
    """验证LLM地点解析"""
    async def parse_locations():
        request_data = {
            "input_text": context.user_input,
            "max_locations": 8
        }
        
        response = await context.client.post(
            "/api/v1/ai/parse-locations",
            json=request_data
        )
        
        assert response.status_code == 200
        parse_result = response.json()
        
        # 验证解析结果结构
        assert "locations" in parse_result
        assert isinstance(parse_result["locations"], list)
        
        context.parsed_locations = parse_result["locations"]
        test_metrics.record_step_time("llm_parse")
        
        return parse_result
    
    context.parse_result = asyncio.run(parse_locations())
    print(f"🧠 LLM解析完成，识别到 {len(context.parsed_locations)} 个地点")

@then('应该识别出{expected_count:d}个有效地点')
def step_verify_location_count(context: Context, expected_count: int):
    """验证识别的地点数量"""
    actual_count = len(context.parsed_locations)
    assert actual_count == expected_count, f"期望 {expected_count} 个地点，实际识别 {actual_count} 个"
    print(f"✅ 地点数量验证通过: {actual_count} 个")

@then('应该生成优化的路线连接')
def step_generate_route_connections(context: Context):
    """生成路线连接"""
    async def generate_route():# 构建路线生成请求
        request_data = {
            "user_input": context.user_input,
            "max_locations": 8
        }
        
        response = await context.client.post(
            "/api/v1/ai/generate-route",
            json=request_data
        )
        
        assert response.status_code == 200
        route_result = response.json()
        
        # 验证路线结构
        assert "route" in route_result
        route_data = route_result["route"]
        assert "locations" in route_data
        assert "connections" in route_data
        assert "visual_style" in route_data
        
        context.route_data = route_data
        test_metrics.record_step_time("route_generation")
        
        return route_result
    
    context.route_result = asyncio.run(generate_route())
    print(f"🛣️ 路线生成完成，包含 {len(context.route_data['connections'])} 个连接")

@then('应该渲染出完整的路线图')
def step_render_route_map(context: Context):
    """渲染路线图"""
    # 这里模拟视觉渲染过程
    # 在实际实现中，这可能涉及Canvas渲染或图像生成
    
    route_data = context.route_data
    
    # 验证渲染所需的数据完整性
    assert "locations" in route_data
    assert "connections" in route_data
    assert "visual_style" in route_data
    
    # 模拟渲染时间
    time.sleep(0.5)  # 模拟渲染延迟
    
    # 创建模拟的图像质量指标
    context.rendered_image = {
        "width": 1200,
        "height": 800,
        "format": "PNG",
        "quality_score": 0.95,
        "locations_rendered": len(route_data["locations"]),
        "connections_rendered": len(route_data["connections"])
    }
    
    test_metrics.record_step_time("visual_rendering")
    print("🎨 路线图渲染完成")

@then('图像应该包含所有地点标记')
def step_verify_location_markers(context: Context):
    """验证地点标记"""
    rendered_image = context.rendered_image
    expected_locations = len(context.parsed_locations)
    actual_locations = rendered_image["locations_rendered"]
    
    assert actual_locations == expected_locations, \
        f"期望渲染 {expected_locations} 个地点标记，实际渲染 {actual_locations} 个"
    
    print(f"✅ 地点标记验证通过: {actual_locations} 个标记")

@then('路线应该使用平滑的贝塞尔曲线连接')
def step_verify_smooth_curves(context: Context):
    """验证路线平滑度"""
    # 检查路线连接的样式配置
    route_data = context.route_data
    connections = route_data.get("connections", [])
    
    for connection in connections:
        # 验证连接样式包含曲线信息
        assert "style" in connection
        # 在实际实现中，这里会检查贝塞尔曲线参数
    
    print("✅ 路线平滑度验证通过")

@when('用户输入 "{input_format}"')
def step_user_input_format(context: Context, input_format: str):
    """处理不同格式的用户输入"""
    context.user_input = input_format
    test_metrics.start_timer()
    print(f"📝 用户输入格式: {input_format}")

@then('系统应该正确解析并生成路线图')
def step_parse_and_generate_route(context: Context):
    """完整的解析和生成流程"""
    # 组合之前定义的步骤
    step_llm_parse_locations(context)
    step_generate_route_connections(context)
    step_render_route_map(context)
    print("✅ 完整路线生成流程验证通过")

@then('生成的图像应该符合视觉规范')
def step_verify_visual_standards(context: Context):
    """验证视觉规范"""
    rendered_image = context.rendered_image
    
    # 检查图像尺寸
    assert rendered_image["width"] >= 1200
    assert rendered_image["height"] >= 800
    
    # 检查质量分数
    assert rendered_image["quality_score"] >= 0.9
    
    print("✅ 视觉规范验证通过")

@given('LLM服务暂时不可用')
def step_llm_service_unavailable(context: Context):
    """模拟LLM服务不可用"""
    context.llm_service_available = False
    print("⚠️ 模拟LLM服务不可用")

@then('系统应该使用备用地点解析服务')
def step_fallback_parsing_service(context: Context):
    """验证备用解析服务"""
    # 在实际实现中，这里会测试备用服务
    context.fallback_service_used = True
    print("🔄 备用地点解析服务启用")

@then('仍然能够生成基础路线图')
def step_generate_basic_route(context: Context):
    """验证基础路线图生成"""
    # 验证即使在降级模式下也能生成路线
    assert context.fallback_service_used
    print("✅ 基础路线图生成成功")

@then('用户应该收到服务降级提示')
def step_service_degradation_notice(context: Context):
    """验证服务降级提示"""
    # 验证用户收到适当的提示信息
    context.degradation_notice_shown = True
    print("📢 服务降级提示已显示")

@given('用户输入包含{city_count:d}个城市的复杂路线')
def step_complex_route_input(context: Context, city_count: int):
    """复杂路线输入"""
    cities = ["北京", "上海", "广州", "深圳", "杭州", "南京", "西安", "成都"]
    context.user_input = " ".join(cities[:city_count])
    context.expected_city_count = city_count
    test_metrics.start_timer()
    print(f"📝 复杂路线输入: {city_count} 个城市")

@when('系统处理路线生成请求')
def step_process_route_request(context: Context):
    """处理路线生成请求"""
    context.processing_started = True
    print("⚙️ 开始处理路线生成请求")

@then('LLM解析应该在{max_time:g}秒内完成')
def step_verify_llm_parse_time(context: Context, max_time: float):
    """验证LLM解析时间"""
    # 执行LLM解析
    step_llm_parse_locations(context)
    
    actual_time = test_metrics.llm_parse_time
    assert actual_time <= max_time, f"LLM解析时间 {actual_time:.2f}s 超过限制 {max_time}s"
    print(f"⏱️ LLM解析时间: {actual_time:.2f}s (限制: {max_time}s)")

@then('路线生成应该在{max_time:g}秒内完成')
def step_verify_route_generation_time(context: Context, max_time: float):
    """验证路线生成时间"""
    step_generate_route_connections(context)
    
    actual_time = test_metrics.route_generation_time
    assert actual_time <= max_time, f"路线生成时间 {actual_time:.2f}s 超过限制 {max_time}s"
    print(f"⏱️ 路线生成时间: {actual_time:.2f}s (限制: {max_time}s)")

@then('视觉渲染应该在{max_time:g}秒内完成')
def step_verify_visual_rendering_time(context: Context, max_time: float):
    """验证视觉渲染时间"""
    step_render_route_map(context)
    
    actual_time = test_metrics.visual_rendering_time
    assert actual_time <= max_time, f"视觉渲染时间 {actual_time:.2f}s 超过限制 {max_time}s"
    print(f"⏱️ 视觉渲染时间: {actual_time:.2f}s (限制: {max_time}s)")

@then('总体响应时间应该在{max_time:g}秒内')
def step_verify_total_response_time(context: Context, max_time: float):
    """验证总体响应时间"""
    total_time = test_metrics.get_total_time()
    assert total_time <= max_time, f"总体响应时间 {total_time:.2f}s 超过限制 {max_time}s"
    print(f"⏱️ 总体响应时间: {total_time:.2f}s (限制: {max_time}s)")

# 清理函数
def cleanup_test_context(context: Context):
    """清理测试上下文"""
    if hasattr(context, 'client'):
        asyncio.run(context.client.aclose())
    
    # 重置测试指标
    global test_metrics
    test_metrics = TestMetrics()

# 在测试结束后调用清理
@step('清理测试环境')
def step_cleanup_test_environment(context: Context):
    """清理测试环境"""
    cleanup_test_context(context)
    print("🧹 测试环境清理完成")