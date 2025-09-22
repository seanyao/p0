from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import router
from app.api.ai_routes import router as ai_router
from app.config import config

# 获取应用配置
app_config = config.get_app_config()

# 创建FastAPI应用
app = FastAPI(
    title=app_config.get('title', 'Travel Route Map API'),
    version=app_config.get('version', '1.0.0'),
    description="旅游路线图生成工具的后端API服务",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(router, prefix="/api/v1", tags=["location"])
app.include_router(ai_router)

@app.get("/")
async def root():
    """根路径，返回API信息"""
    return {
        "message": "Travel Route Map API",
        "version": app_config.get('version', '1.0.0'),
        "docs": "/docs",
        "health": "/api/v1/health"
    }

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=app_config.get('host', '0.0.0.0'),
        port=app_config.get('port', 8000),
        reload=app_config.get('debug', True)
    )