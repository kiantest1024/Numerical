"""
数据库模型定义
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, JSON
from sqlalchemy.sql import func
from app.database import Base
import uuid

class GameConfig(Base):
    """游戏配置表"""
    __tablename__ = "game_configs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), unique=True, nullable=False, index=True)
    display_name = Column(String(255), nullable=False)
    description = Column(Text)
    game_type = Column(String(50), nullable=False)
    
    # 配置数据（JSON格式存储）
    config_data = Column(JSON, nullable=False)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 状态
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<GameConfig(name='{self.name}', display_name='{self.display_name}')>"

class SimulationRecord(Base):
    """模拟记录表"""
    __tablename__ = "simulation_records"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    simulation_id = Column(String(36), unique=True, nullable=False, index=True)
    config_name = Column(String(255), nullable=False)
    
    # 模拟参数
    game_name = Column(String(255), nullable=False)
    simulation_rounds = Column(Integer, nullable=False)
    
    # 模拟状态
    status = Column(String(50), nullable=False, default='pending')  # pending, running, completed, error, stopped
    
    # 时间信息
    start_time = Column(DateTime(timezone=True))
    end_time = Column(DateTime(timezone=True))
    duration = Column(Float)  # 持续时间（秒）
    
    # 结果数据（JSON格式存储）
    result_data = Column(JSON)
    
    # 错误信息
    error_message = Column(Text)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<SimulationRecord(simulation_id='{self.simulation_id}', status='{self.status}')>"

class SimulationProgress(Base):
    """模拟进度表"""
    __tablename__ = "simulation_progress"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    simulation_id = Column(String(36), nullable=False, index=True)
    
    # 进度信息
    current_round = Column(Integer, default=0)
    total_rounds = Column(Integer, nullable=False)
    progress_percentage = Column(Float, default=0.0)
    
    # 时间信息
    elapsed_time = Column(Float, default=0.0)  # 已用时间（秒）
    estimated_remaining = Column(Float)  # 预计剩余时间（秒）
    
    # 实时统计
    current_rtp = Column(Float)  # 当前RTP
    total_bet_amount = Column(Float, default=0.0)  # 总投注金额
    total_payout_amount = Column(Float, default=0.0)  # 总派奖金额
    
    # 时间戳
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<SimulationProgress(simulation_id='{self.simulation_id}', progress={self.progress_percentage:.1f}%)>"

class SystemLog(Base):
    """系统日志表"""
    __tablename__ = "system_logs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # 日志信息
    level = Column(String(20), nullable=False)  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    message = Column(Text, nullable=False)
    module = Column(String(100))  # 模块名
    function = Column(String(100))  # 函数名
    
    # 关联信息
    simulation_id = Column(String(36))  # 关联的模拟ID
    config_name = Column(String(255))  # 关联的配置名
    
    # 额外数据
    extra_data = Column(JSON)
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<SystemLog(level='{self.level}', message='{self.message[:50]}...')>"
