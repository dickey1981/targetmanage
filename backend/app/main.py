"""
智能目标管理系统主应用
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from contextlib import asynccontextmanager

from .api import auth, user
from .config.settings import get_settings

# 获取配置
settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    print("🚀 智能目标管理系统启动中...")
    yield
    # 关闭时执行
    print("👋 智能目标管理系统已关闭")

# 创建FastAPI应用
app = FastAPI(
    title="智能目标管理系统",
    description="一个面向个人用户的智能化目标管理服务",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册API路由
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(user.router, prefix="/api/user", tags=["用户"])

# 根路径
@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "智能目标管理系统API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }

# 健康检查
@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "timestamp": "2025-01-01T00:00:00Z",
        "service": "智能目标管理系统",
        "version": "1.0.0"
    }

# 测试接口
@app.get("/api/test")
async def test_api():
    """测试API接口"""
    return {
        "success": True,
        "message": "API连接正常",
        "data": {
            "timestamp": "2025-01-01T00:00:00Z",
            "service": "智能目标管理系统"
        }
    }

# 全局异常处理
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """HTTP异常处理"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "error_code": exc.status_code
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """通用异常处理"""
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "服务器内部错误",
            "error_code": 500
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
