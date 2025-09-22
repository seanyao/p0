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

import openai
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
        """
        初始化LLM服务
        
        Args:
            config_path: 配置文件路径，如果为None则使用默认路径
        """
        self.config = None
        self.client = None
        self._load_config(config_path)
    
    def _load_config(self, config_path: Optional[str] = None):
        """加载并验证配置文件"""
        try:
            # 使用配置验证器加载配置
            self.config = LLMConfig(**load_and_validate_config(config_path)['llm'])
            
            # 初始化OpenAI客户端
            self.client = openai.AsyncOpenAI(
                api_key=self.config.api_key,
                base_url=self.config.api_url,
                timeout=self.config.timeout
            )
            
            logger.info(f"LLM服务初始化成功，模型: {self.config.model}")
            
        except ConfigValidationError as e:
            logger.error(f"配置验证失败: {e}")
            raise
        except Exception as e:
            logger.error(f"LLM服务初始化失败: {e}")
            raise
    
    async def parse_locations(self, user_input: str) -> List[LocationInfo]:
        """
        解析用户输入中的地点信息
        
        Args:
            user_input: 用户输入的文本
            
        Returns:
            解析出的地点信息列表
        """
        if not self.client or not self.config:
            raise RuntimeError("LLM服务未正确初始化")
        
        prompt = self._build_location_parsing_prompt(user_input)
        
        try:
            response = await self._call_llm(prompt)
            locations = self._parse_location_response(response)
            return locations
            
        except Exception as e:
            logger.error(f"地点解析失败: {e}")
            raise
    
    async def generate_route(self, locations: List[LocationInfo]) -> RouteVisualization:
        """
        生成路线可视化方案
        
        Args:
            locations: 地点信息列表
            
        Returns:
            路线可视化方案
        """
        if not self.client or not self.config:
            raise RuntimeError("LLM服务未正确初始化")
        
        prompt = self._build_route_generation_prompt(locations)
        
        try:
            response = await self._call_llm(prompt)
            route = self._parse_route_response(response, locations)
            return route
            
        except Exception as e:
            logger.error(f"路线生成失败: {e}")
            raise
    
    async def _call_llm(self, prompt: str) -> str:
        """调用LLM API"""
        messages = [
            {"role": "system", "content": "你是一个专业的地理信息和路线规划专家。"},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = await self.client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature
            )
            
            return response.choices[0].message.content
            
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
    
    def _build_route_generation_prompt(self, locations: List[LocationInfo]) -> str:
        """构建路线生成提示词"""
        locations_str = "\n".join([
            f"- {loc.display_name} ({loc.coordinates[0]}, {loc.coordinates[1]})"
            for loc in locations
        ])
        
        return f"""
请为给定的地点生成最佳的视觉化路线。

地点信息：
{locations_str}

请生成：
1. 合理的地点连接顺序
2. 美观的路线路径
3. 适合的地图视角和缩放
4. 协调的视觉样式

要求：
- 路线连接要有地理合理性
- 优化视觉美观效果
- 考虑地图布局平衡
- 确保所有地点都清晰可见

输出格式：
{{
  "connections": [
    {{
      "from_index": 0,
      "to_index": 1,
      "style": "curved|straight",
      "color": "#color_code"
    }}
  ],
  "map_bounds": {{
    "north": 纬度,
    "south": 纬度,
    "east": 经度,
    "west": 经度
  }},
  "visual_style": {{
    "theme": "artistic|modern|classic",
    "color_scheme": "warm|cool|vibrant"
  }}
}}
"""
    
    def _parse_location_response(self, response: str) -> List[LocationInfo]:
        """解析地点识别响应"""
        try:
            import json
            data = json.loads(response)
            locations = []
            
            for loc_data in data.get("locations", []):
                location = LocationInfo(**loc_data)
                locations.append(location)
            
            return locations
            
        except Exception as e:
            logger.error(f"解析地点响应失败: {e}")
            # 返回空列表作为fallback
            return []
    
    def _parse_route_response(self, response: str, locations: List[LocationInfo]) -> RouteVisualization:
        """解析路线生成响应"""
        try:
            import json
            data = json.loads(response)
            
            route = RouteVisualization(
                locations=locations,
                connections=data.get("connections", []),
                map_bounds=data.get("map_bounds", {}),
                visual_style=data.get("visual_style", {})
            )
            
            return route
            
        except Exception as e:
            logger.error(f"解析路线响应失败: {e}")
            # 返回基础路线作为fallback
            return RouteVisualization(
                locations=locations,
                connections=[],
                map_bounds={},
                visual_style={}
            )
    
    async def close(self):
        """关闭HTTP客户端"""
        if self.client:
            await self.client.aclose()


# 全局LLM服务实例
llm_service = LLMService()