from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from app.models import (
    LocationParseRequest, 
    LocationParseResponse, 
    HealthCheckResponse,
    RouteGenerateRequest,
    RouteGenerateResponse
)
from app.services import LocationParser
from app.services.route_generator import RouteGenerator
from app.config import config

router = APIRouter()

# 全局服务实例
location_parser = LocationParser()
route_generator = RouteGenerator()

@router.post("/parse", response_model=LocationParseResponse)
async def parse_locations(request: LocationParseRequest):
    """
    解析地名接口
    
    - **input**: 用户输入的地名文本，支持多种格式
    - 返回解析结果，包括坐标信息和错误提示
    """
    try:
        result = await location_parser.parse_input(request.input)
        
        return LocationParseResponse(
            success=result.success,
            data=result,
            message="解析完成" if result.success else "解析失败",
            code=200 if result.success else 400
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"服务器内部错误: {str(e)}"
        )

@router.post("/generate-route", response_model=RouteGenerateResponse)
async def generate_route(request: RouteGenerateRequest):
    """
    生成路线接口
    
    - **coordinates**: 地点坐标列表，至少2个坐标点
    - 返回路线数据，包括路径点、地图边界、标签位置等
    """
    try:
        route_data = await route_generator.generate_route(request.coordinates)
        
        return RouteGenerateResponse(
            success=True,
            data=route_data,
            message="路线生成成功",
            code=200
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"请求参数错误: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"服务器内部错误: {str(e)}"
        )

@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """
    健康检查接口
    
    返回服务状态和版本信息
    """
    app_config = config.get_app_config()
    amap_config = config.get_amap_config()
    
    # 检查高德地图API配置
    amap_status = "configured" if amap_config.get('api_key') else "not_configured"
    
    return HealthCheckResponse(
        status="healthy",
        version=app_config.get('version', '1.0.0'),
        timestamp=datetime.now().isoformat(),
        dependencies={
            "amap_api": amap_status,
            "config": "loaded"
        }
    )

@router.get("/suggest/{input_text}")
async def suggest_corrections(input_text: str):
    """
    获取输入建议接口
    
    - **input_text**: 用户输入的文本
    - 返回修正建议列表
    """
    try:
        suggestions = await location_parser.suggest_corrections(input_text)
        
        return {
            "success": True,
            "suggestions": suggestions,
            "message": "建议获取成功"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取建议失败: {str(e)}"
        )