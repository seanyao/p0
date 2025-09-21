import re
import asyncio
from typing import List, Dict, Optional, Tuple
import httpx
from app.models import ParseResult, ValidationResult, Coordinate
from app.config import config

class LocationParser:
    """地名解析服务"""
    
    def __init__(self):
        self.amap_config = config.get_amap_config()
        self.limits = config.get_limits()
        self.cache: Dict[str, Coordinate] = {}
        
        # 地名别名映射
        self.alias_map = {
            '帝都': '北京',
            '魔都': '上海',
            '花城': '广州',
            '羊城': '广州',
            '春城': '昆明',
            '泉城': '济南',
            '冰城': '哈尔滨',
            '山城': '重庆',
            '蓉城': '成都',
            '星城': '长沙',
            '江城': '武汉',
            '鹭岛': '厦门'
        }
        
        # 常见错别字映射
        self.typo_map = {
            '北经': '北京',
            '上海市': '上海',
            '广洲': '广州',
            '深圳市': '深圳',
            '杭洲': '杭州',
            '南经': '南京',
            '西按': '西安',
            '成都市': '成都',
            '重庆市': '重庆',
            '武汗': '武汉'
        }
    
    async def parse_input(self, input_text: str) -> ParseResult:
        """解析用户输入的地名文本"""
        try:
            # 1. 清理和分割输入
            locations = self._split_input(input_text)
            
            # 2. 验证地名数量
            if len(locations) < self.limits['min_locations']:
                return ParseResult(
                    success=False,
                    errors=[f"请输入至少{self.limits['min_locations']}个地名"]
                )
            
            if len(locations) > self.limits['max_locations']:
                return ParseResult(
                    success=False,
                    errors=[f"最多支持{self.limits['max_locations']}个地名"]
                )
            
            # 3. 验证地名有效性
            validation_result = await self.validate_locations(locations)
            if not validation_result.valid:
                return ParseResult(
                    success=False,
                    locations=locations,
                    errors=validation_result.messages
                )
            
            # 4. 获取地理坐标
            coordinates = []
            errors = []
            
            for location in locations:
                try:
                    coord = await self.get_coordinates(location)
                    if coord:
                        coordinates.append(coord)
                    else:
                        errors.append(f"未找到地名：{location}")
                except Exception as e:
                    errors.append(f"解析地名 {location} 时出错：{str(e)}")
            
            # 5. 返回结果
            success = len(errors) == 0 and len(coordinates) == len(locations)
            
            return ParseResult(
                success=success,
                locations=locations,
                coordinates=coordinates,
                errors=errors,
                suggestions=self._generate_suggestions(input_text) if not success else []
            )
            
        except Exception as e:
            return ParseResult(
                success=False,
                errors=[f"解析过程中发生错误：{str(e)}"]
            )
    
    def _split_input(self, input_text: str) -> List[str]:
        """分割输入文本为地名列表"""
        # 清理输入
        text = input_text.strip()
        
        # 支持多种分隔符：箭头、逗号、空格
        # 先处理箭头
        text = re.sub(r'\s*→\s*', ',', text)
        text = re.sub(r'\s*->\s*', ',', text)
        
        # 再处理逗号和空格
        locations = re.split(r'[,，\s]+', text)
        
        # 过滤空字符串，但保留重复项用于后续验证
        result = []
        for loc in locations:
            loc = loc.strip()
            if loc:
                result.append(loc)
        
        return result
    
    async def validate_locations(self, locations: List[str]) -> ValidationResult:
        """验证地名列表的有效性"""
        invalid_locations = []
        duplicate_locations = []
        messages = []
        
        # 检查重复
        seen = set()
        for loc in locations:
            if loc in seen:
                duplicate_locations.append(loc)
            seen.add(loc)
        
        if duplicate_locations:
            messages.append(f"发现重复地名：{', '.join(duplicate_locations)}")
        
        # 检查地名有效性（这里简化处理，实际应该调用地图API验证）
        for loc in locations:
            normalized_loc = self._normalize_location(loc)
            if not normalized_loc:
                invalid_locations.append(loc)
        
        if invalid_locations:
            messages.append(f"无效地名：{', '.join(invalid_locations)}")
        
        valid = len(invalid_locations) == 0 and len(duplicate_locations) == 0
        
        return ValidationResult(
            valid=valid,
            invalid_locations=invalid_locations,
            duplicate_locations=duplicate_locations,
            messages=messages
        )
    
    def _normalize_location(self, location: str) -> Optional[str]:
        """标准化地名"""
        # 处理别名
        if location in self.alias_map:
            return self.alias_map[location]
        
        # 处理错别字
        if location in self.typo_map:
            return self.typo_map[location]
        
        # 简单验证：至少包含中文字符
        if re.search(r'[\u4e00-\u9fff]', location):
            return location
        
        return None
    
    async def get_coordinates(self, location_name: str) -> Optional[Coordinate]:
        """获取地名的地理坐标"""
        # 标准化地名
        normalized_name = self._normalize_location(location_name)
        if not normalized_name:
            return None
        
        # 检查缓存
        if normalized_name in self.cache:
            return self.cache[normalized_name]
        
        try:
            # 调用高德地图API
            async with httpx.AsyncClient() as client:
                params = {
                    'key': self.amap_config['api_key'],
                    'address': normalized_name,
                    'output': 'json'
                }
                
                response = await client.get(
                    f"{self.amap_config['base_url']}/geocode/geo",
                    params=params,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get('status') == '1' and data.get('geocodes'):
                        geocode = data['geocodes'][0]
                        location_str = geocode.get('location', '')
                        
                        if location_str:
                            lng, lat = map(float, location_str.split(','))
                            
                            coordinate = Coordinate(
                                lng=lng,
                                lat=lat,
                                name=geocode.get('formatted_address', normalized_name),
                                level=self._determine_level(geocode.get('level', ''))
                            )
                            
                            # 缓存结果
                            self.cache[normalized_name] = coordinate
                            return coordinate
                
        except Exception as e:
            print(f"获取坐标失败 {location_name}: {e}")
        
        return None
    
    def _determine_level(self, level_str: str) -> str:
        """确定行政级别"""
        if '省' in level_str or '自治区' in level_str or '直辖市' in level_str:
            return 'province'
        elif '市' in level_str:
            return 'city'
        else:
            return 'district'
    
    def _generate_suggestions(self, input_text: str) -> List[str]:
        """生成修正建议"""
        suggestions = []
        
        # 检查是否包含常见错别字
        for typo, correct in self.typo_map.items():
            if typo in input_text:
                suggestions.append(f"是否想输入：{input_text.replace(typo, correct)}")
        
        # 检查是否包含别名
        for alias, standard in self.alias_map.items():
            if alias in input_text:
                suggestions.append(f"建议使用标准地名：{input_text.replace(alias, standard)}")
        
        return suggestions[:3]  # 最多返回3个建议

    async def suggest_corrections(self, input_text: str) -> List[str]:
        """智能建议修正"""
        return self._generate_suggestions(input_text)