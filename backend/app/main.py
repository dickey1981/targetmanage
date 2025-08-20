"""
FastAPI应用入口点
Main entry point for the FastAPI application
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn

from app.config.settings import settings
from app.config.database import engine, create_tables
from app.api.v1 import auth, users, goals, tasks, progress, ai_services, admin
from app.middleware.logging import LoggingMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    print("🚀 启动目标管理系统后端服务...")
    await create_tables()
    print("✅ 数据库表创建完成")
    
    yield
    
    # 关闭时执行
    print("🛑 关闭目标管理系统后端服务...")


# 创建FastAPI应用
app = FastAPI(
    title="目标管理系统 API",
    description="提供目标管理、任务拆分、进度跟踪等功能的后端API服务",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# CORS中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 自定义中间件
app.add_middleware(LoggingMiddleware)

# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理器"""
    return JSONResponse(
        status_code=500,
        content={
            "message": "服务器内部错误",
            "detail": str(exc) if settings.DEBUG else "请联系管理员"
        }
    )

# 健康检查
@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "service": "目标管理系统后端",
        "version": "1.0.0"
    }

# API路由注册
app.include_router(auth.router, prefix="/api/v1/auth", tags=["认证"])
app.include_router(users.router, prefix="/api/v1/users", tags=["用户管理"])
app.include_router(goals.router, prefix="/api/v1/goals", tags=["目标管理"])
app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["任务管理"])
app.include_router(progress.router, prefix="/api/v1/progress", tags=["进度跟踪"])
app.include_router(ai_services.router, prefix="/api/v1/ai", tags=["AI服务"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["后台管理"])


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
