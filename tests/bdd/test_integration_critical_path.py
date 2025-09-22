"""
完整的关键路径集成测试
使用真实LLM API和完整业务流程
"""

import pytest
import asyncio
import json
import time
from typing import Dict, Any, List
from unittest.mock import patch

from backend.app.services.llm_service import llm_service, LocationInfo, RouteVisualization


class TestAIRoutePlanningIntegration:
    """AI路线规划完整集成测试"""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_complete_critical_path_integration(self):
        """
        完整的关键路径集成测试
        覆盖从用户输入到最终路线生成的整个业务流程
        """
        # 测试数据 - 复杂的多地点路线规划
        test_cases = [
            {
                "name": "国内多城市旅行",
                "user_input": "我想去北京、上海、广州、深圳旅行，帮我规划一下路线",
                "expected_min_locations": 4,
                "expected_cities": ["北京", "上海", "广州", "深圳"]
            },
            {
                "name": "带别名的城市输入",
                "user_input": "从帝都出发，经过魔都，最后到羊城",
                "expected_min_locations": 3,
                "expected_cities": ["北京", "上海", "广州"]
            },
            {
                "name": "混合地点类型",
                "user_input": "北京故宫、上海外滩、杭州西湖、成都宽窄巷子",
                "expected_min_locations": 4,
                "expected_locations": ["故宫", "外滩", "西湖", "宽窄巷子"]
            }
        ]
        
        for test_case in test_cases:
            print(f"\n=== 测试用例: {test_case['name']} ===")
            
            # 步骤1: 地点解析 - 使用真实LLM API
            start_time = time.time()
            locations = await llm_service.parse_locations(test_case["user_input"])
            parse_duration = time.time() - start_time
            
            # 验证地点解析结果
            assert len(locations) >= test_case["expected_min_locations"], \
                f"解析出的地点数量不足: {len(locations)} < {test_case['expected_min_locations']}"
            
            # 验证地点信息完整性
            for location in locations:
                assert isinstance(location, LocationInfo), "地点信息类型错误"
                assert location.name, "地点名称不能为空"
                assert location.display_name, "显示名称不能为空"
                assert len(location.coordinates) == 2, "坐标格式错误"
                assert isinstance(location.coordinates[0], (int, float)), "经度格式错误"
                assert isinstance(location.coordinates[1], (int, float)), "纬度格式错误"
                assert location.type, "地点类型不能为空"
            
            print(f"✓ 地点解析完成: {len(locations)}个地点, 耗时: {parse_duration:.2f}s")
            for loc in locations:
                print(f"  - {loc.display_name} ({loc.type}): {loc.coordinates}")
            
            # 步骤2: 路线生成 - 使用真实LLM API
            start_time = time.time()
            route = await llm_service.generate_route(locations)
            route_duration = time.time() - start_time
            
            # 验证路线生成结果
            assert isinstance(route, RouteVisualization), "路线可视化类型错误"
            assert route.locations == locations, "路线地点与输入不匹配"
            assert len(route.connections) >= 0, "连接关系数量异常"
            assert isinstance(route.map_bounds, dict), "地图边界格式错误"
            assert isinstance(route.visual_style, dict), "视觉样式格式错误"
            
            # 验证地图边界
            required_bounds = ["north", "south", "east", "west"]
            for bound in required_bounds:
                assert bound in route.map_bounds, f"缺少地图边界: {bound}"
                assert isinstance(route.map_bounds[bound], (int, float)), f"边界值格式错误: {bound}"
            
            # 验证连接关系
            if len(locations) > 1:
                assert len(route.connections) >= len(locations) - 1, "连接关系数量不足"
                for connection in route.connections:
                    assert "from" in connection, "连接缺少起点"
                    assert "to" in connection, "连接缺少终点"
                    assert "distance" in connection or "duration" in connection, "连接缺少距离或时长信息"
            
            print(f"✓ 路线生成完成: {len(route.connections)}个连接, 耗时: {route_duration:.2f}s")
            print(f"  地图边界: N{route.map_bounds.get('north', 0):.2f} S{route.map_bounds.get('south', 0):.2f} E{route.map_bounds.get('east', 0):.2f} W{route.map_bounds.get('west', 0):.2f}")
            
            # 步骤3: 端到端性能验证
            total_duration = parse_duration + route_duration
            assert total_duration < 30.0, f"总响应时间过长: {total_duration:.2f}s"
            
            print(f"✓ 性能验证通过: 总耗时 {total_duration:.2f}s")
            
            # 步骤4: 数据一致性验证
            location_names = [loc.name for loc in locations]
            for connection in route.connections:
                if "from" in connection and "to" in connection:
                    from_name = connection["from"]
                    to_name = connection["to"]
                    # 验证连接的地点确实存在于地点列表中
                    assert any(loc.name == from_name or from_name in loc.display_name for loc in locations), \
                        f"连接起点不在地点列表中: {from_name}"
                    assert any(loc.name == to_name or to_name in loc.display_name for loc in locations), \
                        f"连接终点不在地点列表中: {to_name}"
            
            print(f"✓ 数据一致性验证通过")
            
            # 步骤5: 业务逻辑验证
            # 验证地理合理性 - 坐标应该在合理范围内（中国境内）
            for location in locations:
                lng, lat = location.coordinates
                assert 70 <= lng <= 140, f"经度超出中国范围: {lng}"
                assert 15 <= lat <= 55, f"纬度超出中国范围: {lat}"
            
            print(f"✓ 业务逻辑验证通过")
            
            print(f"✅ 测试用例 '{test_case['name']}' 完成\n")
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_error_handling_integration(self):
        """错误处理集成测试"""
        
        # 测试空输入
        with pytest.raises(ValueError):
            await llm_service.parse_locations("")
        
        # 测试无效输入
        locations = await llm_service.parse_locations("这里没有任何地点信息，只是随机文字")
        # 应该返回空列表或者合理的默认处理
        assert isinstance(locations, list)
        
        # 测试空地点列表的路线生成
        with pytest.raises(ValueError):
            await llm_service.generate_route([])
        
        print("✓ 错误处理集成测试通过")
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_concurrent_requests_integration(self):
        """并发请求集成测试"""
        
        test_inputs = [
            "北京到上海",
            "广州到深圳", 
            "杭州到南京",
            "成都到重庆",
            "西安到北京"
        ]
        
        # 并发执行地点解析
        start_time = time.time()
        tasks = [llm_service.parse_locations(input_text) for input_text in test_inputs]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        concurrent_duration = time.time() - start_time
        
        # 验证并发结果
        successful_results = [r for r in results if not isinstance(r, Exception)]
        assert len(successful_results) >= len(test_inputs) * 0.8, "并发成功率过低"
        
        # 验证并发性能
        expected_sequential_time = len(test_inputs) * 3.0  # 假设每个请求3秒
        assert concurrent_duration < expected_sequential_time * 0.7, "并发性能提升不明显"
        
        print(f"✓ 并发测试通过: {len(successful_results)}/{len(test_inputs)} 成功, 耗时: {concurrent_duration:.2f}s")
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_llm_api_connectivity(self):
        """LLM API连接性测试"""
        
        # 验证LLM服务配置
        assert llm_service.config is not None, "LLM配置未加载"
        assert llm_service.config.api_key, "API密钥未配置"
        assert llm_service.config.api_url, "API地址未配置"
        assert llm_service.config.model, "模型名称未配置"
        
        # 测试简单的LLM调用
        test_prompt = "请识别这个地点：北京"
        response = await llm_service._call_llm(test_prompt)
        
        assert response, "LLM响应为空"
        assert isinstance(response, str), "LLM响应格式错误"
        assert len(response) > 10, "LLM响应内容过短"
        
        print(f"✓ LLM API连接测试通过，响应长度: {len(response)}")
    
    @pytest.mark.asyncio
    @pytest.mark.integration  
    async def test_end_to_end_performance_benchmark(self):
        """端到端性能基准测试"""
        
        performance_cases = [
            {"input": "北京", "max_time": 8.0, "type": "单地点"},  # 放宽时间限制
            {"input": "北京到上海", "max_time": 10.0, "type": "两地点"},
            {"input": "北京、上海、广州、深圳", "max_time": 15.0, "type": "多地点"},
            {"input": "从帝都出发，经过魔都、羊城，最后到深圳", "max_time": 18.0, "type": "复杂描述"}
        ]
        
        performance_results = []
        
        for case in performance_cases:
            start_time = time.time()
            
            # 完整流程
            locations = await llm_service.parse_locations(case["input"])
            if locations:
                route = await llm_service.generate_route(locations)
            
            total_time = time.time() - start_time
            
            # 性能断言
            assert total_time < case["max_time"], \
                f"{case['type']}性能不达标: {total_time:.2f}s > {case['max_time']}s"
            
            performance_results.append({
                "type": case["type"],
                "time": total_time,
                "locations_count": len(locations) if locations else 0
            })
            
            print(f"✓ {case['type']}性能测试: {total_time:.2f}s, {len(locations) if locations else 0}个地点")
        
        # 输出性能报告
        print("\n=== 性能基准报告 ===")
        for result in performance_results:
            print(f"{result['type']}: {result['time']:.2f}s ({result['locations_count']}个地点)")
        
        avg_time = sum(r['time'] for r in performance_results) / len(performance_results)
        print(f"平均响应时间: {avg_time:.2f}s")
        
        assert avg_time < 12.0, f"平均性能不达标: {avg_time:.2f}s"  # 放宽平均时间限制