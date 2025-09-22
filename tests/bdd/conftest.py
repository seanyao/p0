"""
BDD集成测试配置
设置测试环境、fixtures和测试工具
"""

import pytest
import asyncio
import os
import sys
from pathlib import Path
from typing import Generator, Dict, Any
import httpx
from fastapi.testclient import TestClient

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "backend"))

# 导入应用
try:
    from backend.main import app
    from backend.app.services.llm_service import llm_service
    from backend.app.utils.config_validator import load_and_validate_config
except ImportError as e:
    print(f"Warning: Could not import backend modules: {e}")
    app = None

# 测试配置
TEST_CONFIG = {
    "base_url": "http://localhost:8000",
    "timeout": 30,
    "max_retries": 3,
    "performance_thresholds": {
        "llm_parse_time": 5.0,
        "route_generation_time": 3.0,
        "visual_rendering_time": 2.0,
        "total_response_time": 10.0
    }
}

class BDDTestContext:
    """BDD测试上下文管理器"""
    
    def __init__(self):
        self.base_url = TEST_CONFIG["base_url"]
        self.client = None
        self.async_client = None
        self.test_data = {}
        self.metrics = {}
        self.cleanup_tasks = []
    
    async def setup(self):
        """设置测试环境"""
        # 创建异步HTTP客户端
        self.async_client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=TEST_CONFIG["timeout"]
        )
        
        # 验证服务可用性
        await self._verify_service_availability()
        
    async def teardown(self):
        """清理测试环境"""
        # 执行清理任务
        for cleanup_task in self.cleanup_tasks:
            try:
                await cleanup_task()
            except Exception as e:
                print(f"Cleanup task failed: {e}")
        
        # 关闭HTTP客户端
        if self.async_client:
            await self.async_client.aclose()
    
    async def _verify_service_availability(self):
        """验证服务可用性"""
        try:
            response = await self.async_client.get("/api/v1/ai/health")
            if response.status_code != 200:
                raise Exception(f"Health check failed: {response.status_code}")
            
            health_data = response.json()
            if health_data.get("status") != "healthy":
                raise Exception(f"Service not healthy: {health_data}")
                
        except Exception as e:
            print(f"Service availability check failed: {e}")
            raise

@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环用于异步测试"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def bdd_context():
    """BDD测试上下文fixture"""
    context = BDDTestContext()
    await context.setup()
    yield context
    await context.teardown()

@pytest.fixture
def sync_client():
    """同步测试客户端"""
    if app is None:
        pytest.skip("Backend app not available")
    return TestClient(app)

@pytest.fixture
async def async_client():
    """异步HTTP客户端"""
    async with httpx.AsyncClient(
        base_url="http://localhost:8000",
        timeout=30.0
    ) as client:
        yield client

@pytest.fixture
def test_locations():
    """测试用地点数据"""
    return {
        "simple_route": [
            {"name": "北京", "coordinates": [116.4074, 39.9042]},
            {"name": "上海", "coordinates": [121.4737, 31.2304]},
            {"name": "广州", "coordinates": [113.2644, 23.1291]}
        ],
        "complex_route": [
            {"name": "北京", "coordinates": [116.4074, 39.9042]},
            {"name": "上海", "coordinates": [121.4737, 31.2304]},
            {"name": "广州", "coordinates": [113.2644, 23.1291]},
            {"name": "深圳", "coordinates": [114.0579, 22.5431]},
            {"name": "杭州", "coordinates": [120.1551, 30.2741]},
            {"name": "南京", "coordinates": [118.7969, 32.0603]},
            {"name": "西安", "coordinates": [108.9398, 34.3416]},
            {"name": "成都", "coordinates": [104.0668, 30.5728]}
        ],
        "edge_cases": {
            "single_location": [{"name": "北京", "coordinates": [116.4074, 39.9042]}],
            "duplicate_locations": [
                {"name": "北京", "coordinates": [116.4074, 39.9042]},
                {"name": "北京", "coordinates": [116.4074, 39.9042]},
                {"name": "上海", "coordinates": [121.4737, 31.2304]}
            ],
            "invalid_coordinates": [
                {"name": "火星", "coordinates": [999.0, 999.0]},
                {"name": "上海", "coordinates": [121.4737, 31.2304]}
            ]
        }
    }

@pytest.fixture
def test_inputs():
    """测试用输入数据"""
    return {
        "natural_language": "我想去北京、上海、广州旅游",
        "arrow_format": "北京→上海→广州",
        "comma_format": "北京，上海，广州",
        "mixed_format": "北京→上海，广州",
        "alias_format": "帝都 魔都 花城",
        "typo_format": "北经 上海 广洲",
        "edge_cases": {
            "too_few": "北京",
            "too_many": "北京 上海 广州 深圳 杭州 南京 西安 成都 重庆",
            "duplicate": "北京 上海 北京",
            "invalid": "北京 火星 上海"
        }
    }

@pytest.fixture
def performance_monitor():
    """性能监控器"""
    class PerformanceMonitor:
        def __init__(self):
            self.metrics = {}
            self.start_times = {}
        
        def start_timer(self, operation: str):
            import time
            self.start_times[operation] = time.time()
        
        def end_timer(self, operation: str):
            import time
            if operation in self.start_times:
                elapsed = time.time() - self.start_times[operation]
                self.metrics[operation] = elapsed
                return elapsed
            return None
        
        def get_metrics(self):
            return self.metrics.copy()
        
        def verify_threshold(self, operation: str, threshold: float):
            if operation in self.metrics:
                actual = self.metrics[operation]
                assert actual <= threshold, f"{operation} took {actual:.2f}s, exceeds threshold {threshold}s"
                return True
            return False
    
    return PerformanceMonitor()

@pytest.fixture
def image_quality_validator():
    """图像质量验证器"""
    class ImageQualityValidator:
        def __init__(self):
            self.quality_standards = {
                "min_width": 1200,
                "min_height": 800,
                "min_quality_score": 0.9,
                "min_contrast_ratio": 4.5,
                "min_font_size": 16
            }
        
        def validate_dimensions(self, width: int, height: int):
            assert width >= self.quality_standards["min_width"]
            assert height >= self.quality_standards["min_height"]
            return True
        
        def validate_quality_score(self, score: float):
            assert score >= self.quality_standards["min_quality_score"]
            return True
        
        def validate_accessibility(self, image_data: Dict[str, Any]):
            # 验证可访问性标准
            if "contrast_ratio" in image_data:
                assert image_data["contrast_ratio"] >= self.quality_standards["min_contrast_ratio"]
            
            if "font_size" in image_data:
                assert image_data["font_size"] >= self.quality_standards["min_font_size"]
            
            return True
    
    return ImageQualityValidator()

@pytest.fixture
def api_validator():
    """API响应验证器"""
    class APIValidator:
        def validate_location_parse_response(self, response_data: Dict[str, Any]):
            """验证地点解析响应"""
            assert "locations" in response_data
            assert isinstance(response_data["locations"], list)
            
            for location in response_data["locations"]:
                assert "name" in location
                assert "coordinates" in location
                assert isinstance(location["coordinates"], list)
                assert len(location["coordinates"]) == 2
            
            return True
        
        def validate_route_generation_response(self, response_data: Dict[str, Any]):
            """验证路线生成响应"""
            assert "route" in response_data
            route = response_data["route"]
            
            assert "locations" in route
            assert "connections" in route
            assert "visual_style" in route
            
            return True
        
        def validate_health_response(self, response_data: Dict[str, Any]):
            """验证健康检查响应"""
            assert "status" in response_data
            assert response_data["status"] == "healthy"
            assert "timestamp" in response_data
            
            return True
    
    return APIValidator()

# 测试标记定义
pytest_plugins = []

def pytest_configure(config):
    """配置pytest标记"""
    config.addinivalue_line("markers", "critical_path: 关键路径测试")
    config.addinivalue_line("markers", "llm_integration: LLM集成测试")
    config.addinivalue_line("markers", "visual_rendering: 视觉渲染测试")
    config.addinivalue_line("markers", "performance: 性能测试")
    config.addinivalue_line("markers", "edge_cases: 边界情况测试")
    config.addinivalue_line("markers", "accessibility: 可访问性测试")
    config.addinivalue_line("markers", "concurrent_users: 并发用户测试")

def pytest_collection_modifyitems(config, items):
    """修改测试收集"""
    # 为关键路径测试添加优先级
    critical_path_items = []
    other_items = []
    
    for item in items:
        if "critical_path" in item.keywords:
            critical_path_items.append(item)
        else:
            other_items.append(item)
    
    # 关键路径测试优先执行
    items[:] = critical_path_items + other_items

# 测试报告钩子
def pytest_runtest_makereport(item, call):
    """生成测试报告"""
    if call.when == "call":
        # 记录测试结果
        if hasattr(item, "funcargs"):
            if "performance_monitor" in item.funcargs:
                monitor = item.funcargs["performance_monitor"]
                metrics = monitor.get_metrics()
                if metrics:
                    print(f"\n性能指标: {metrics}")

# 环境变量设置
def pytest_sessionstart(session):
    """测试会话开始"""
    # 设置测试环境变量
    os.environ["TESTING"] = "true"
    os.environ["LOG_LEVEL"] = "DEBUG"
    
    print("\n🚀 BDD集成测试开始")
    print(f"测试配置: {TEST_CONFIG}")

def pytest_sessionfinish(session, exitstatus):
    """测试会话结束"""
    print(f"\n✅ BDD集成测试完成，退出状态: {exitstatus}")
    
    # 清理环境变量
    if "TESTING" in os.environ:
        del os.environ["TESTING"]