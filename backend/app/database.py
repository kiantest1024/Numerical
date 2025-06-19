"""
数据库配置和连接管理
"""

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
import logging

logger = logging.getLogger(__name__)

# 数据库配置
DATABASE_CONFIG = {
    "host": "172.16.1.30",
    "port": 3306,
    "username": "root",
    "password": "lottoplay.ph",
    "database": "numerical_tools"
}

# 构建数据库URL
DATABASE_URL = f"mysql+pymysql://{DATABASE_CONFIG['username']}:{DATABASE_CONFIG['password']}@{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['database']}?charset=utf8mb4"

# 创建数据库引擎
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False  # 设置为True可以看到SQL语句
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基础模型类
Base = declarative_base()

# 元数据
metadata = MetaData()

def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_database():
    """初始化数据库"""
    try:
        # 创建数据库（如果不存在）
        from sqlalchemy import create_engine, text
        
        # 连接到MySQL服务器（不指定数据库）
        server_url = f"mysql+pymysql://{DATABASE_CONFIG['username']}:{DATABASE_CONFIG['password']}@{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}"
        server_engine = create_engine(server_url)
        
        with server_engine.connect() as conn:
            # 创建数据库
            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {DATABASE_CONFIG['database']} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
            conn.commit()
        
        server_engine.dispose()
        
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        
        logger.info("数据库初始化成功")
        return True
        
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        return False

def test_connection():
    """测试数据库连接"""
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            return result.fetchone() is not None
    except Exception as e:
        logger.error(f"数据库连接测试失败: {e}")
        return False
