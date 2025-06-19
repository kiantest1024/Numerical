"""
@numericalTools - 通用数值模拟验证工具
FastAPI主应用程序
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import os
import logging
from contextlib import asynccontextmanager

from .api import simulation, config, reports
from .core.config import settings
from .database import init_database, test_connection

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("🚀 @numericalTools 启动中...")

    # 初始化数据库
    try:
        if test_connection():
            logger.info("数据库连接测试成功")
            if init_database():
                logger.info("数据库初始化成功")
            else:
                logger.warning("数据库初始化失败，将使用文件存储")
        else:
            logger.warning("数据库连接失败，将使用文件存储")
    except Exception as e:
        logger.error(f"数据库初始化异常: {e}")
        logger.warning("将使用文件存储作为备用方案")

    yield
    logger.info("🛑 @numericalTools 关闭中...")


# 创建FastAPI应用
app = FastAPI(
    title="@numericalTools",
    description="通用数值模拟验证工具 - 专为游戏RTP验证设计",
    version="1.0.0",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册API路由
app.include_router(simulation.router, prefix="/api/v1/simulation", tags=["simulation"])
app.include_router(config.router, prefix="/api/v1/config", tags=["config"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["reports"])

# 健康检查端点
@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "@numericalTools",
        "version": "1.0.0"
    }

# 根路径
@app.get("/")
async def root():
    """根路径信息"""
    return {
        "name": "@numericalTools",
        "description": "通用数值模拟验证工具",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# 静态文件服务（用于前端）
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "build")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=os.path.join(frontend_path, "static")), name="static")
    app.mount("/app", StaticFiles(directory=frontend_path, html=True), name="frontend")
    logger.info(f"前端文件服务路径: {frontend_path}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
