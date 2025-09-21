import pytest
import pytest_asyncio
import asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient
from main import app

@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环用于异步测试"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()

@pytest.fixture
def client():
    """创建测试客户端"""
    return TestClient(app)

@pytest_asyncio.fixture
async def async_client():
    """创建异步测试客户端"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
def sample_locations():
    """测试用的地名数据"""
    return {
        "valid_input": "北京 上海 广州",
        "arrow_format": "北京→上海→广州",
        "comma_format": "北京，上海，广州",
        "mixed_format": "北京→上海，广州",
        "alias_input": "帝都 魔都 花城",
        "typo_input": "北经 上海 广洲",
        "too_few": "北京",
        "too_many": "北京 上海 广州 深圳 杭州 南京 西安 成都 重庆",
        "duplicate": "北京 上海 北京",
        "invalid": "北京 火星 上海"
    }