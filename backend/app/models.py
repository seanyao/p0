from typing import List, Optional, Literal
from pydantic import BaseModel, Field, field_validator

class Coordinate(BaseModel):
    """地理坐标模型"""
    lng: float = Field(..., description="经度")
    lat: float = Field(..., description="纬度")
    name: str = Field(..., description="标准地名")
    level: Literal['province', 'city', 'district'] = Field(..., description="行政级别")

class ParseResult(BaseModel):
    """地名解析结果模型"""
    success: bool = Field(..., description="解析是否成功")
    locations: List[str] = Field(default_factory=list, description="解析出的地名列表")
    coordinates: List[Coordinate] = Field(default_factory=list, description="地理坐标列表")
    errors: List[str] = Field(default_factory=list, description="错误信息列表")
    suggestions: List[str] = Field(default_factory=list, description="建议修正列表")

class ValidationResult(BaseModel):
    """地名验证结果模型"""
    valid: bool = Field(..., description="验证是否通过")
    invalid_locations: List[str] = Field(default_factory=list, description="无效地名列表")
    duplicate_locations: List[str] = Field(default_factory=list, description="重复地名列表")
    messages: List[str] = Field(default_factory=list, description="验证消息列表")

class LocationParseRequest(BaseModel):
    """地名解析请求模型"""
    input: str = Field(..., min_length=1, max_length=500, description="用户输入的地名文本")
    
    @field_validator('input')
    @classmethod
    def validate_input(cls, v):
        if not v.strip():
            raise ValueError("输入不能为空")
        return v.strip()

class LocationParseResponse(BaseModel):
    """地名解析响应模型"""
    success: bool = Field(..., description="请求是否成功")
    data: Optional[ParseResult] = Field(None, description="解析结果数据")
    message: str = Field("", description="响应消息")
    code: int = Field(200, description="响应状态码")

class HealthCheckResponse(BaseModel):
    """健康检查响应模型"""
    status: str = Field(..., description="服务状态")
    version: str = Field(..., description="服务版本")
    timestamp: str = Field(..., description="检查时间戳")
    dependencies: dict = Field(default_factory=dict, description="依赖服务状态")

# 路线生成相关模型

class PathPoint(BaseModel):
    """路径点模型"""
    lng: float = Field(..., description="经度")
    lat: float = Field(..., description="纬度")
    type: Literal['start', 'end', 'control'] = Field(..., description="路径点类型")
    index: int = Field(..., description="在路径中的索引")

class MapBounds(BaseModel):
    """地图边界模型"""
    southwest: Coordinate = Field(..., description="西南角坐标")
    northeast: Coordinate = Field(..., description="东北角坐标")

class LabelPosition(BaseModel):
    """标签位置模型"""
    lng: float = Field(..., description="标签经度")
    lat: float = Field(..., description="标签纬度")
    name: str = Field(..., description="标签名称")
    offset_x: float = Field(default=0, description="X轴偏移量")
    offset_y: float = Field(default=0, description="Y轴偏移量")
    position: Literal['top', 'bottom', 'left', 'right'] = Field(default='top', description="标签相对位置")

class RouteData(BaseModel):
    """路线数据模型"""
    coordinates: List[Coordinate] = Field(..., description="地点坐标列表")
    pathPoints: List[PathPoint] = Field(default_factory=list, description="路径点数据")
    bounds: MapBounds = Field(..., description="地图边界")
    center: Coordinate = Field(..., description="地图中心点")
    zoom: float = Field(..., description="缩放级别")
    labelPositions: List[LabelPosition] = Field(default_factory=list, description="标签位置列表")

class RouteGenerateRequest(BaseModel):
    """路线生成请求模型"""
    coordinates: List[Coordinate] = Field(..., min_length=2, max_length=20, description="地点坐标列表")
    
    @field_validator('coordinates')
    @classmethod
    def validate_coordinates(cls, v):
        if len(v) < 2:
            raise ValueError("至少需要2个坐标点")
        return v

class RouteGenerateResponse(BaseModel):
    """路线生成响应模型"""
    success: bool = Field(..., description="请求是否成功")
    data: Optional[RouteData] = Field(None, description="路线数据")
    message: str = Field("", description="响应消息")
    code: int = Field(200, description="响应状态码")