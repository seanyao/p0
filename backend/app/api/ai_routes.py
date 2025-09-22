"""
AI路线规划API端点
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional
import logging
import time

from ..services.llm_service import llm_service, LocationInfo, RouteVisualization

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/ai", tags=["AI路线规划"])


class RouteRequest(BaseModel):
    """路线规划请求模型"""
    user_input: str = Field(..., description="用户输入的旅行描述", min_length=1, max_length=1000)
    style_preference: Optional[str] = Field("artistic", description="视觉风格偏好")
    max_locations: Optional[int] = Field(20, description="最大地点数量", ge=1, le=20)


class RouteResponse(BaseModel):
    """路线规划响应模型"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    locations: List[LocationInfo] = Field(default_factory=list, description="识别的地点")
    route: Optional[RouteVisualization] = Field(None, description="生成的路线")
    processing_time: float = Field(..., description="处理时间（秒）")


@router.post("/parse-locations", response_model=RouteResponse)
async def parse_locations(request: RouteRequest):
    """
    解析用户输入中的地点信息
    
    Args:
        request: 包含用户输入的请求
        
    Returns:
        解析结果，包含识别的地点信息
    """
    import time
    start_time = time.time()
    
    try:
        logger.info(f"开始解析地点: {request.user_input[:100]}...")
        
        # 调用LLM服务解析地点
        locations = await llm_service.parse_locations(request.user_input)
        
        # 检查地点数量限制
        if len(locations) > request.max_locations:
            locations = locations[:request.max_locations]
            logger.warning(f"地点数量超限，截取前{request.max_locations}个")
        
        processing_time = time.time() - start_time
        
        return RouteResponse(
            success=True,
            message=f"成功识别{len(locations)}个地点",
            locations=locations,
            processing_time=processing_time
        )
        
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"地点解析失败: {e}")
        
        raise HTTPException(
            status_code=500,
            detail=f"地点解析失败: {str(e)}"
        )


@router.post("/generate-route", response_model=RouteResponse)
async def generate_route(request: RouteRequest):
    """
    生成完整的AI路线规划
    
    Args:
        request: 包含用户输入的请求
        
    Returns:
        完整的路线规划结果
    """
    import time
    start_time = time.time()
    
    try:
        logger.info(f"开始生成路线: {request.user_input[:100]}...")
        
        # 第一步：解析地点
        locations = await llm_service.parse_locations(request.user_input)
        
        if not locations:
            raise HTTPException(
                status_code=400,
                detail="未能识别到有效地点，请检查输入内容"
            )
        
        # 检查地点数量限制
        if len(locations) > request.max_locations:
            locations = locations[:request.max_locations]
            logger.warning(f"地点数量超限，截取前{request.max_locations}个")
        
        # 第二步：生成路线
        route = await llm_service.generate_route(locations)
        
        processing_time = time.time() - start_time
        
        return RouteResponse(
            success=True,
            message=f"成功生成包含{len(locations)}个地点的路线",
            locations=locations,
            route=route,
            processing_time=processing_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"路线生成失败: {e}")
        
        raise HTTPException(
            status_code=500,
            detail=f"路线生成失败: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """
    健康检查端点
    
    Returns:
        服务状态信息
    """
    try:
        # 检查LLM服务状态
        if not llm_service.config:
            return {
                "status": "unhealthy",
                "message": "LLM配置未加载",
                "timestamp": time.time()
            }
        
        return {
            "status": "healthy",
            "message": "AI路线规划服务正常",
            "model": llm_service.config.model,
            "timestamp": time.time()
        }
        
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return {
            "status": "unhealthy",
            "message": f"服务异常: {str(e)}",
            "timestamp": time.time()
        }


# 示例请求数据
EXAMPLE_REQUESTS = {
    "simple": {
        "user_input": "我想去北京看天安门，然后去西安看兵马俑",
        "style_preference": "artistic",
        "max_locations": 10
    },
    "complex": {
        "user_input": "计划一次日本之旅，从东京开始，去富士山、京都、大阪，最后回到东京，希望能看到樱花和传统文化",
        "style_preference": "artistic",
        "max_locations": 15
    }
}