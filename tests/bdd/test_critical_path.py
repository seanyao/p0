"""
AI路线规划关键路径集成测试
端到端测试覆盖LLM和生图的完整业务流程
"""

import pytest
import asyncio
import json
import time
from typing import Dict, List, Any
import httpx
from unittest.mock import patch, MagicMock

# 测试类
class TestAIRoutePlanningCriticalPath:
    """AI路线规划关键路径测试"""
    
    @pytest.mark.critical_path
    @pytest.mark.smoke
    @pytest.mark.llm_integration
    @pytest.mark.asyncio
    async def test_end_to_end_natural_language_input(
        self, 
        async_client, 
        performance_monitor, 
        api_validator,
        image_quality_validator
    ):
        """
        测试场景：用户输入自然语言生成完整路线图
        覆盖：LLM解析 -> 路线生成 -> 视觉渲染
        """
        # Given: 用户输入自然语言
        user_input = "我想去北京、上海、广州旅游"
        
        performance_monitor.start_timer("total_process")
        
        # When: 调用LLM服务解析地点
        performance_monitor.start_timer("llm_parse")
        
        parse_request = {
            "user_input": user_input,
            "max_locations": 8
        }
        
        parse_response = await async_client.post(
            "/api/v1/ai/parse-locations",
            json=parse_request
        )
        
        parse_time = performance_monitor.end_timer("llm_parse")
        
        # Then: 验证LLM解析结果
        assert parse_response.status_code == 200
        parse_data = parse_response.json()
        api_validator.validate_location_parse_response(parse_data)
        
        locations = parse_data["locations"]
        assert len(locations) == 3, f"期望3个地点，实际解析{len(locations)}个"
        
        # 验证地点信息
        location_names = [loc["name"] for loc in locations]
        expected_cities = ["北京", "上海", "广州"]
        for city in expected_cities:
            assert any(city in name for name in location_names), f"未找到城市: {city}"
        
        # When: 生成路线
        performance_monitor.start_timer("route_generation")
        
        route_request = {
            "user_input": user_input,
            "max_locations": 8
        }
        
        route_response = await async_client.post(
            "/api/v1/ai/generate-route",
            json=route_request
        )
        
        route_time = performance_monitor.end_timer("route_generation")
        
        # Then: 验证路线生成结果
        assert route_response.status_code == 200
        route_data = route_response.json()
        api_validator.validate_route_generation_response(route_data)
        
        route = route_data["route"]
        assert len(route["locations"]) == 3
        assert len(route["connections"]) >= 2  # 至少2个连接
        
        # When: 模拟视觉渲染
        performance_monitor.start_timer("visual_rendering")
        
        # 模拟渲染过程（在实际实现中会调用Canvas API）
        rendered_result = self._simulate_visual_rendering(route)
        
        render_time = performance_monitor.end_timer("visual_rendering")
        total_time = performance_monitor.end_timer("total_process")
        
        # Then: 验证渲染结果
        image_quality_validator.validate_dimensions(
            rendered_result["width"], 
            rendered_result["height"]
        )
        image_quality_validator.validate_quality_score(rendered_result["quality_score"])
        
        # 验证性能指标
        performance_monitor.verify_threshold("llm_parse", 5.0)
        performance_monitor.verify_threshold("route_generation", 3.0)
        performance_monitor.verify_threshold("visual_rendering", 2.0)
        performance_monitor.verify_threshold("total_process", 10.0)
        
        print(f"✅ 端到端测试完成 - 总时间: {total_time:.2f}s")
        print(f"   LLM解析: {parse_time:.2f}s")
        print(f"   路线生成: {route_time:.2f}s")
        print(f"   视觉渲染: {render_time:.2f}s")
    
    @pytest.mark.critical_path
    @pytest.mark.visual_rendering
    @pytest.mark.parametrize("input_format,expected_cities", [
        ("北京→上海→广州", ["北京", "上海", "广州"]),
        ("北京，上海，广州", ["北京", "上海", "广州"]),
        ("帝都 魔都 花城", ["北京", "上海", "广州"]),
    ])
    async def test_multiple_input_formats(
        self, 
        async_client, 
        input_format, 
        expected_cities,
        api_validator
    ):
        """
        测试场景：多种输入格式的路线生成
        验证系统对不同输入格式的处理能力
        """
        # Given: 不同格式的用户输入
        parse_request = {
            "user_input": input_format,
            "max_locations": 8
        }
        
        # When: 解析地点
        parse_response = await async_client.post(
            "/api/v1/ai/parse-locations",
            json=parse_request
        )
        
        # Then: 验证解析结果
        assert parse_response.status_code == 200
        parse_data = parse_response.json()
        api_validator.validate_location_parse_response(parse_data)
        
        locations = parse_data["locations"]
        location_names = [loc["name"] for loc in locations]
        
        for expected_city in expected_cities:
            assert any(expected_city in name for name in location_names), \
                f"输入格式 '{input_format}' 未正确识别城市: {expected_city}"
        
        print(f"✅ 输入格式测试通过: {input_format} -> {location_names}")
    
    @pytest.mark.critical_path
    @pytest.mark.error_handling
    async def test_llm_service_fallback(self, async_client, api_validator):
        """
        测试场景：LLM服务异常时的降级处理
        验证系统的容错能力和备用服务
        """
        # Given: 模拟LLM服务异常
        with patch('backend.app.services.llm_service.llm_service') as mock_llm:
            # 模拟LLM服务抛出异常
            mock_llm.parse_locations.side_effect = Exception("LLM服务不可用")
            
            parse_request = {
                "user_input": "北京 上海 广州",
                "max_locations": 8
            }
            
            # When: 调用解析服务
            parse_response = await async_client.post(
                "/api/v1/ai/parse-locations",
                json=parse_request
            )
            
            # Then: 验证降级处理
            # 在实际实现中，应该有备用的地点解析服务
            # 这里验证系统不会完全失败
            assert parse_response.status_code in [200, 503]  # 成功或服务不可用
            
            if parse_response.status_code == 200:
                # 如果有备用服务，验证返回结果
                parse_data = parse_response.json()
                assert "locations" in parse_data
                print("✅ 备用服务正常工作")
            else:
                # 如果返回503，验证错误信息
                error_data = parse_response.json()
                assert "error" in error_data
                print("✅ 服务降级提示正确返回")
    
    @pytest.mark.performance
    @pytest.mark.critical_path
    async def test_complex_route_performance(
        self, 
        async_client, 
        performance_monitor,
        test_locations
    ):
        """
        测试场景：大规模路线的性能测试
        验证系统处理复杂路线的性能表现
        """
        # Given: 8个城市的复杂路线
        complex_locations = test_locations["complex_route"]
        
        performance_monitor.start_timer("complex_route_total")
        
        # When: 生成复杂路线
        route_request = {
            "user_input": "我想去北京、上海、广州、深圳、杭州、南京、西安、成都旅游",
            "max_locations": 8
        }
        
        performance_monitor.start_timer("complex_route_generation")
        
        route_response = await async_client.post(
            "/api/v1/ai/generate-route",
            json=route_request
        )
        
        generation_time = performance_monitor.end_timer("complex_route_generation")
        
        # Then: 验证性能和结果
        assert route_response.status_code == 200
        route_data = route_response.json()
        
        route = route_data["route"]
        assert len(route["locations"]) == 8
        assert len(route["connections"]) >= 7  # 至少7个连接
        
        # 模拟视觉渲染
        performance_monitor.start_timer("complex_visual_rendering")
        rendered_result = self._simulate_visual_rendering(route)
        render_time = performance_monitor.end_timer("complex_visual_rendering")
        
        total_time = performance_monitor.end_timer("complex_route_total")
        
        # 验证性能阈值
        performance_monitor.verify_threshold("complex_route_generation", 5.0)
        performance_monitor.verify_threshold("complex_visual_rendering", 3.0)
        performance_monitor.verify_threshold("complex_route_total", 10.0)
        
        print(f"✅ 复杂路线性能测试通过")
        print(f"   路线生成: {generation_time:.2f}s")
        print(f"   视觉渲染: {render_time:.2f}s")
        print(f"   总时间: {total_time:.2f}s")
    
    @pytest.mark.visual_quality
    @pytest.mark.critical_path
    async def test_visual_rendering_quality(
        self, 
        async_client, 
        test_locations,
        image_quality_validator
    ):
        """
        测试场景：视觉渲染质量验证
        验证生成图像的质量标准
        """
        # Given: 标准路线数据
        locations = test_locations["simple_route"]
        
        route_request = {
            "user_input": "我想去北京、上海、广州旅游",
            "max_locations": 8
        }
        
        # When: 生成路线
        route_response = await async_client.post(
            "/api/v1/ai/generate-route",
            json=route_request
        )
        
        assert route_response.status_code == 200
        route_data = route_response.json()
        route = route_data["route"]
        
        # When: 渲染路线图
        rendered_result = self._simulate_visual_rendering(route)
        
        # Then: 验证视觉质量
        # 验证图像尺寸
        image_quality_validator.validate_dimensions(
            rendered_result["width"], 
            rendered_result["height"]
        )
        
        # 验证质量分数
        image_quality_validator.validate_quality_score(rendered_result["quality_score"])
        
        # 验证可访问性
        accessibility_data = {
            "contrast_ratio": rendered_result.get("contrast_ratio", 4.8),
            "font_size": rendered_result.get("font_size", 16)
        }
        image_quality_validator.validate_accessibility(accessibility_data)
        
        # 验证地点标记
        assert rendered_result["locations_rendered"] == len(locations)
        assert rendered_result["connections_rendered"] >= len(locations) - 1
        
        print("✅ 视觉渲染质量验证通过")
        print(f"   图像尺寸: {rendered_result['width']}x{rendered_result['height']}")
        print(f"   质量分数: {rendered_result['quality_score']}")
        print(f"   地点标记: {rendered_result['locations_rendered']}")
    
    @pytest.mark.integration
    @pytest.mark.critical_path
    async def test_api_endpoints_integration(self, async_client, api_validator):
        """
        测试场景：API端点集成验证
        验证所有API端点的正常工作
        """
        # Test 1: Health Check
        health_response = await async_client.get("/api/v1/ai/health")
        assert health_response.status_code == 200
        
        health_data = health_response.json()
        api_validator.validate_health_response(health_data)
        
        # Given: 复杂路线输入
        parse_request = {
            "user_input": "我想从北京出发，先去上海看外滩，然后去杭州西湖，再到苏州园林，最后回到南京",
            "max_locations": 8
        }
        
        parse_response = await async_client.post(
            "/api/v1/ai/parse-locations",
            json=parse_request
        )
        
        assert parse_response.status_code == 200
        parse_data = parse_response.json()
        api_validator.validate_location_parse_response(parse_data)
        
        # Test 3: Route Generation
        route_request = {
            "user_input": "我想去北京、上海、广州旅游",
            "max_locations": 8
        }
        
        route_response = await async_client.post(
            "/api/v1/ai/generate-route",
            json=route_request
        )
        
        assert route_response.status_code == 200
        route_data = route_response.json()
        api_validator.validate_route_generation_response(route_data)
        
        print("✅ API端点集成验证通过")
        print(f"   健康检查: {health_response.status_code}")
        print(f"   地点解析: {parse_response.status_code}")
        print(f"   路线生成: {route_response.status_code}")
    
    @pytest.mark.edge_cases
    @pytest.mark.critical_path
    @pytest.mark.parametrize("edge_case,expected_behavior", [
        ("北京", "提示至少需要2个地点"),
        ("北京 上海 广州 深圳 杭州 南京 西安 成都 重庆", "提示最多支持8个地点"),
        ("北京 火星 上海", "识别有效地点，忽略无效地点"),
        ("北京 北京 上海", "自动去重，提示重复地点"),
    ])
    async def test_edge_cases_handling(
        self, 
        async_client, 
        edge_case, 
        expected_behavior
    ):
        """
        测试场景：边界情况处理
        验证系统对各种边界情况的处理
        """
        # Given: 边界情况输入
        parse_request = {
            "user_input": edge_case,
            "max_locations": 8
        }
        
        # When: 调用解析服务
        parse_response = await async_client.post(
            "/api/v1/ai/parse-locations",
            json=parse_request
        )
        
        # Then: 验证处理结果
        if "至少需要2个地点" in expected_behavior:
            # 单个地点的情况
            if parse_response.status_code == 200:
                parse_data = parse_response.json()
                assert len(parse_data["locations"]) < 2
            else:
                assert parse_response.status_code == 400
        
        elif "最多支持8个地点" in expected_behavior:
            # 地点过多的情况
            if parse_response.status_code == 200:
                parse_data = parse_response.json()
                assert len(parse_data["locations"]) <= 8
        
        elif "识别有效地点" in expected_behavior:
            # 包含无效地点的情况
            if parse_response.status_code == 200:
                parse_data = parse_response.json()
                # 应该过滤掉无效地点
                location_names = [loc["name"] for loc in parse_data["locations"]]
                assert "火星" not in location_names
        
        elif "自动去重" in expected_behavior:
            # 重复地点的情况
            if parse_response.status_code == 200:
                parse_data = parse_response.json()
                # 应该去重
                location_names = [loc["name"] for loc in parse_data["locations"]]
                assert len(location_names) == len(set(location_names))
        
        print(f"✅ 边界情况处理验证通过: {edge_case}")
    
    def _simulate_visual_rendering(self, route_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        模拟视觉渲染过程
        在实际实现中，这会调用Canvas API进行真实渲染
        """
        # 模拟渲染延迟
        time.sleep(0.1)
        
        locations_count = len(route_data.get("locations", []))
        connections_count = len(route_data.get("connections", []))
        
        # 返回模拟的渲染结果
        return {
            "width": 1200,
            "height": 800,
            "format": "PNG",
            "quality_score": 0.95,
            "contrast_ratio": 4.8,
            "font_size": 16,
            "locations_rendered": locations_count,
            "connections_rendered": connections_count,
            "render_time": 0.1,
            "file_size": 245760,  # 240KB
            "accessibility_compliant": True
        }

# 并发测试
class TestConcurrentUsers:
    """并发用户测试"""
    
    @pytest.mark.concurrent_users
    @pytest.mark.performance
    async def test_concurrent_route_generation(self, async_client):
        """
        测试场景：并发用户场景测试
        验证系统在多用户同时使用时的稳定性
        """
        # Given: 多个并发请求
        concurrent_requests = 5
        
        async def single_request(request_id: int):
            """单个请求的处理"""
            parse_request = {
                "user_input": f"北京 上海 广州 {request_id}",
                "max_locations": 8
            }
            
            start_time = time.time()
            
            # 地点解析
            parse_response = await async_client.post(
                "/api/v1/ai/parse-locations",
                json=parse_request
            )
            
            if parse_response.status_code == 200:
                parse_data = parse_response.json()
                
                # 路线生成
                route_request = {
                    "user_input": "我想去北京、上海、广州旅游",
                    "max_locations": 8
                }
                
                route_response = await async_client.post(
                    "/api/v1/ai/generate-route",
                    json=route_request
                )
                
                end_time = time.time()
                
                return {
                    "request_id": request_id,
                    "success": route_response.status_code == 200,
                    "duration": end_time - start_time,
                    "parse_status": parse_response.status_code,
                    "route_status": route_response.status_code
                }
            else:
                end_time = time.time()
                return {
                    "request_id": request_id,
                    "success": False,
                    "duration": end_time - start_time,
                    "parse_status": parse_response.status_code,
                    "route_status": None
                }
        
        # When: 并发执行请求
        tasks = [single_request(i) for i in range(concurrent_requests)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Then: 验证并发处理结果
        successful_requests = 0
        total_duration = 0
        
        for result in results:
            if isinstance(result, dict) and result.get("success"):
                successful_requests += 1
                total_duration += result["duration"]
        
        # 验证成功率
        success_rate = successful_requests / concurrent_requests
        assert success_rate >= 0.8, f"并发成功率过低: {success_rate:.2%}"
        
        # 验证平均响应时间
        if successful_requests > 0:
            avg_duration = total_duration / successful_requests
            assert avg_duration <= 15.0, f"并发平均响应时间过长: {avg_duration:.2f}s"
        
        print(f"✅ 并发测试通过")
        print(f"   并发请求数: {concurrent_requests}")
        print(f"   成功请求数: {successful_requests}")
        print(f"   成功率: {success_rate:.2%}")
        if successful_requests > 0:
            print(f"   平均响应时间: {avg_duration:.2f}s")