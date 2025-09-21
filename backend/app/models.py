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