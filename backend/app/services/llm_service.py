"""
LLM服务集成
提供AI路线规划的核心功能，包括地点解析和路线生成
"""

import os
import yaml
import asyncio
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path

import httpx
from pydantic import BaseModel, Field

from ..utils.config_validator import load_and_validate_config, ConfigValidationError

logger = logging.getLogger(__name__)


class LocationInfo(BaseModel):
    """地点信息模型"""
    name: str = Field(..., description="地点名称")
    display_name: str = Field(..., description="显示名称")
    coordinates: List[float] = Field(..., description="经纬度坐标 [lng, lat]")
    type: str = Field(..., description="地点类型")
    description: Optional[str] = Field(None, description="简短描述")


class RouteVisualization(BaseModel):
    """路线可视化模型"""
    locations: List[LocationInfo] = Field(..., description="路线地点")
    connections: List[Dict[str, Any]] = Field(..., description="路线连接")
    map_bounds: Dict[str, float] = Field(..., description="地图边界")
    visual_style: Dict[str, Any] = Field(..., description="视觉样式")


class LLMConfig(BaseModel):
    """LLM配置模型"""
    api_key: str
    api_url: str
    model: str
    max_tokens: int = 1000
    temperature: float = 0.3
    timeout: int = 30


class LLMService:
    """LLM服务类"""
    
    def __init__(self, config_path: Optional[str] = None):
        """初始化LLM服务"""
        self.config = self._load_config(config_path)
        self.client = httpx.AsyncClient()
        logger.info("LLM服务初始化完成")
    
    def _load_config(self, config_path: Optional[str] = None) -> LLMConfig:
        """加载LLM配置"""
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config" / "llm_config.yaml"
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            
            return LLMConfig(
                api_key=config_data['llm']['api_key'],
                api_url=config_data['llm']['api_url'],
                model=config_data['llm']['model'],
                max_tokens=config_data['llm'].get('max_tokens', 1000),
                temperature=config_data['llm'].get('temperature', 0.3),
                timeout=config_data['llm'].get('timeout', 30)
            )
            
        except Exception as e:
            logger.error(f"加载LLM配置失败: {e}")
            raise ConfigValidationError(f"配置加载失败: {e}")
    
    async def parse_locations(self, user_input: str) -> List[LocationInfo]:
        """
        解析用户输入中的地点信息
        
        Args:
            user_input: 用户输入的文本
            
        Returns:
            解析出的地点信息列表
        """
        # 验证输入
        if not user_input or not user_input.strip():
            raise ValueError("用户输入不能为空")
        
        if not self.client or not self.config:
            raise RuntimeError("LLM服务未正确初始化")
        
        logger.info(f"使用真实LLM API解析地点: {user_input}")
        
        # 构建地点解析提示词
        prompt = self._build_location_parsing_prompt(user_input)
        
        # 调用LLM API
        response = await self._call_llm(prompt)
        
        # 解析LLM响应
        locations = self._parse_location_response(response)
        
        logger.info(f"LLM解析出{len(locations)}个地点")
        return locations
    
    async def generate_route(self, locations: List[LocationInfo]) -> RouteVisualization:
        """
        生成路线可视化
        
        Args:
            locations: 地点信息列表
            
        Returns:
            路线可视化对象
        """
        # 验证输入
        if not locations:
            raise ValueError("地点列表不能为空")
        
        if not self.client or not self.config:
            raise RuntimeError("LLM服务未正确初始化")
        
        logger.info(f"LLM生成路线，包含{len(locations)}个地点")
        
        # 构建路线生成提示词
        prompt = self._build_route_generation_prompt(locations)
        
        # 调用LLM API
        response = await self._call_llm(prompt)
        
        # 解析LLM响应
        route_visualization = self._parse_route_response(response, locations)
        
        logger.info(f"LLM生成路线成功，包含{len(route_visualization.connections)}个连接")
        return route_visualization
    
    def _build_route_generation_prompt(self, locations: List[LocationInfo]) -> str:
        """构建路线生成提示词"""
        location_names = [loc.name for loc in locations]
        location_details = []
        for loc in locations:
            location_details.append(f"- {loc.display_name}: {loc.description}")
        
        prompt = f"""
请为以下地点生成一个最优的旅行路线：

地点列表：
{chr(10).join(location_details)}

要求：
1. 生成地点之间的连接关系，包括距离和预估时长
2. 考虑地理位置的合理性，优化路线顺序
3. 提供地图边界框信息
4. 推荐合适的视觉样式

请以JSON格式返回结果，包含：
- connections: 连接关系数组，每个包含from, to, distance(km), duration(分钟)
- map_bounds: 地图边界，包含north, south, east, west
- visual_style: 视觉样式，包含theme, color_scheme, line_style

地点坐标信息：
{chr(10).join([f"- {loc.name}: [{loc.coordinates[0]}, {loc.coordinates[1]}]" for loc in locations])}
"""
        return prompt
    
    def _parse_route_response(self, response: str, locations: List[LocationInfo]) -> RouteVisualization:
        """解析路线生成响应"""
        try:
            import json
            import re
            
            # 提取JSON部分，LLM可能返回包含说明文字的响应
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # 如果没有找到```json```标记，尝试直接解析
                json_str = response.strip()
            
            logger.info(f"提取的路线JSON字符串: {json_str[:200]}...")
            
            data = json.loads(json_str)
            
            # 构建连接信息，确保包含距离和时长
            connections = []
            route_connections = data.get("connections", [])
            
            for i, conn in enumerate(route_connections):
                connection = {
                    "from": conn.get("from", f"location_{i}"),
                    "to": conn.get("to", f"location_{i+1}"),
                    "distance": conn.get("distance", f"{100 + i*50}km"),  # 默认距离
                    "duration": conn.get("duration", f"{2 + i}小时"),      # 默认时长
                    "transport": conn.get("transport", "高铁"),
                    "description": conn.get("description", f"从{conn.get('from', '起点')}到{conn.get('to', '终点')}")
                }
                connections.append(connection)
            
            # 如果没有连接信息，为相邻地点创建默认连接
            if not connections and len(locations) > 1:
                for i in range(len(locations) - 1):
                    connection = {
                        "from": locations[i].name,
                        "to": locations[i + 1].name,
                        "distance": f"{150 + i*100}km",
                        "duration": f"{2 + i}小时",
                        "transport": "高铁",
                        "description": f"从{locations[i].name}到{locations[i + 1].name}"
                    }
                    connections.append(connection)
            
            # 计算地图边界
            if locations:
                lngs = [loc.coordinates[0] for loc in locations]
                lats = [loc.coordinates[1] for loc in locations]
                map_bounds = {
                    "north": max(lats) + 0.5,
                    "south": min(lats) - 0.5,
                    "east": max(lngs) + 0.5,
                    "west": min(lngs) - 0.5
                }
            else:
                map_bounds = {"north": 40, "south": 30, "east": 120, "west": 110}
            
            # 视觉样式
            visual_style = data.get("visual_style", {
                "theme": "modern",
                "color_scheme": "blue",
                "line_style": "solid",
                "marker_style": "circle"
            })
            
            route_viz = RouteVisualization(
                locations=locations,
                connections=connections,
                map_bounds=map_bounds,
                visual_style=visual_style
            )
            
            logger.info(f"成功生成路线可视化，包含{len(connections)}个连接")
            return route_viz
            
        except Exception as e:
            logger.error(f"解析路线响应失败: {e}")
            logger.error(f"原始响应: {response[:500]}...")
            
            # 返回基本的路线可视化作为fallback
            connections = []
            if len(locations) > 1:
                for i in range(len(locations) - 1):
                    connection = {
                        "from": locations[i].name,
                        "to": locations[i + 1].name,
                        "distance": f"{150 + i*100}km",
                        "duration": f"{2 + i}小时",
                        "transport": "高铁",
                        "description": f"从{locations[i].name}到{locations[i + 1].name}"
                    }
                    connections.append(connection)
            
            # 计算地图边界
            if locations:
                lngs = [loc.coordinates[0] for loc in locations]
                lats = [loc.coordinates[1] for loc in locations]
                map_bounds = {
                    "north": max(lats) + 0.5,
                    "south": min(lats) - 0.5,
                    "east": max(lngs) + 0.5,
                    "west": min(lngs) - 0.5
                }
            else:
                map_bounds = {"north": 40, "south": 30, "east": 120, "west": 110}
            
            return RouteVisualization(
                locations=locations,
                connections=connections,
                map_bounds=map_bounds,
                visual_style={
                    "theme": "modern",
                    "color_scheme": "blue",
                    "line_style": "solid",
                    "marker_style": "circle"
                }
            )
    
    async def _call_llm(self, prompt: str) -> str:
        """调用LLM API"""
        messages = [
            {"role": "system", "content": "你是一个专业的地理信息和路线规划专家。"},
            {"role": "user", "content": prompt}
        ]
        
        try:
            headers = {
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.config.model,
                "messages": messages,
                "max_tokens": self.config.max_tokens,
                "temperature": self.config.temperature
            }
            
            response = await self.client.post(
                self.config.api_url,
                headers=headers,
                json=payload,
                timeout=self.config.timeout
            )
            
            response.raise_for_status()
            result = response.json()
            
            return result["choices"][0]["message"]["content"]
            
        except Exception as e:
            logger.error(f"LLM API调用失败: {e}")
            raise
    
    def _build_location_parsing_prompt(self, user_input: str) -> str:
        """构建地点解析提示词"""
        return f"""
请从用户输入中识别所有提到的地点，并提供准确的地理信息。

用户输入：{user_input}

请识别并返回：
1. 所有提到的城市、景点、地标
2. 每个地点的准确名称和坐标
3. 地点的类型分类
4. 适合的显示名称

要求：
- 准确识别地点名称，包括中英文对照
- 提供精确的经纬度坐标
- 合理分类地点类型
- 处理模糊或不完整的地名
- 返回结构化的JSON数据

输出格式：
{{
  "locations": [
    {{
      "name": "地点原名",
      "display_name": "显示名称", 
      "coordinates": [经度, 纬度],
      "type": "city|attraction|landmark|natural",
      "description": "简短描述"
    }}
  ]
}}
"""
    
    def _parse_location_response(self, response: str) -> List[LocationInfo]:
        """解析地点识别响应"""
        try:
            import json
            import re
            
            # 提取JSON部分，LLM可能返回包含说明文字的响应
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # 如果没有找到```json```标记，尝试直接解析
                json_str = response.strip()
            
            logger.info(f"提取的JSON字符串: {json_str[:200]}...")
            
            data = json.loads(json_str)
            locations = []
            
            for loc_data in data.get("locations", []):
                # 确保数据格式正确，避免Pydantic验证错误
                clean_data = {
                    "name": str(loc_data.get("name", "")),
                    "display_name": str(loc_data.get("display_name", loc_data.get("name", ""))),
                    "coordinates": list(loc_data.get("coordinates", [0.0, 0.0])),
                    "type": str(loc_data.get("type", "city")),
                    "description": str(loc_data.get("description", "")) if loc_data.get("description") else None
                }
                
                location = LocationInfo(**clean_data)
                locations.append(location)
            
            logger.info(f"成功解析出{len(locations)}个地点")
            return locations
            
        except Exception as e:
            logger.error(f"解析地点响应失败: {e}")
            logger.error(f"原始响应: {response[:500]}...")
            # 返回空列表作为fallback
            return []
    
    async def close(self):
        """关闭HTTP客户端"""
        if self.client:
            await self.client.aclose()


# 全局LLM服务实例
llm_service = LLMService()