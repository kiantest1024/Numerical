"""
数据库服务层
"""

from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from ..database import get_db
from ..models import GameConfig, SimulationRecord, SimulationProgress, SystemLog
from typing import List, Optional, Dict, Any
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class DatabaseService:
    """数据库服务类"""
    
    @staticmethod
    def save_game_config(db: Session, name: str, config_data: Dict[str, Any]) -> GameConfig:
        """保存游戏配置"""
        try:
            # 检查是否已存在
            existing_config = db.query(GameConfig).filter(GameConfig.name == name).first()
            
            if existing_config:
                # 更新现有配置
                existing_config.display_name = config_data.get("game_rules", {}).get("name", name)
                existing_config.description = config_data.get("game_rules", {}).get("description", "")
                existing_config.game_type = config_data.get("game_rules", {}).get("game_type", "unknown")
                existing_config.config_data = config_data
                existing_config.updated_at = datetime.now()
                
                db.commit()
                db.refresh(existing_config)
                return existing_config
            else:
                # 创建新配置
                new_config = GameConfig(
                    name=name,
                    display_name=config_data.get("game_rules", {}).get("name", name),
                    description=config_data.get("game_rules", {}).get("description", ""),
                    game_type=config_data.get("game_rules", {}).get("game_type", "unknown"),
                    config_data=config_data
                )
                
                db.add(new_config)
                db.commit()
                db.refresh(new_config)
                return new_config
                
        except Exception as e:
            db.rollback()
            logger.error(f"保存配置失败: {e}")
            raise
    
    @staticmethod
    def get_game_config(db: Session, name: str) -> Optional[GameConfig]:
        """获取游戏配置"""
        try:
            return db.query(GameConfig).filter(
                and_(GameConfig.name == name, GameConfig.is_active == True)
            ).first()
        except Exception as e:
            logger.error(f"获取配置失败: {e}")
            return None
    
    @staticmethod
    def list_game_configs(db: Session) -> List[GameConfig]:
        """列出所有游戏配置"""
        try:
            return db.query(GameConfig).filter(GameConfig.is_active == True).order_by(desc(GameConfig.updated_at)).all()
        except Exception as e:
            logger.error(f"列出配置失败: {e}")
            return []
    
    @staticmethod
    def delete_game_config(db: Session, name: str) -> bool:
        """删除游戏配置（软删除）"""
        try:
            config = db.query(GameConfig).filter(GameConfig.name == name).first()
            if config:
                config.is_active = False
                config.updated_at = datetime.now()
                db.commit()
                return True
            return False
        except Exception as e:
            db.rollback()
            logger.error(f"删除配置失败: {e}")
            return False
    
    @staticmethod
    def save_simulation_record(db: Session, simulation_id: str, config_name: str, 
                             game_name: str, simulation_rounds: int) -> SimulationRecord:
        """保存模拟记录"""
        try:
            record = SimulationRecord(
                simulation_id=simulation_id,
                config_name=config_name,
                game_name=game_name,
                simulation_rounds=simulation_rounds,
                status='pending'
            )
            
            db.add(record)
            db.commit()
            db.refresh(record)
            return record
            
        except Exception as e:
            db.rollback()
            logger.error(f"保存模拟记录失败: {e}")
            raise
    
    @staticmethod
    def update_simulation_status(db: Session, simulation_id: str, status: str, 
                               start_time: Optional[datetime] = None,
                               end_time: Optional[datetime] = None,
                               duration: Optional[float] = None,
                               result_data: Optional[Dict] = None,
                               error_message: Optional[str] = None) -> bool:
        """更新模拟状态"""
        try:
            record = db.query(SimulationRecord).filter(SimulationRecord.simulation_id == simulation_id).first()
            if record:
                record.status = status
                if start_time:
                    record.start_time = start_time
                if end_time:
                    record.end_time = end_time
                if duration is not None:
                    record.duration = duration
                if result_data:
                    record.result_data = result_data
                if error_message:
                    record.error_message = error_message
                
                record.updated_at = datetime.now()
                db.commit()
                return True
            return False
        except Exception as e:
            db.rollback()
            logger.error(f"更新模拟状态失败: {e}")
            return False
    
    @staticmethod
    def get_simulation_record(db: Session, simulation_id: str) -> Optional[SimulationRecord]:
        """获取模拟记录"""
        try:
            return db.query(SimulationRecord).filter(SimulationRecord.simulation_id == simulation_id).first()
        except Exception as e:
            logger.error(f"获取模拟记录失败: {e}")
            return None
    
    @staticmethod
    def list_simulation_records(db: Session, limit: int = 100) -> List[SimulationRecord]:
        """列出模拟记录"""
        try:
            return db.query(SimulationRecord).order_by(desc(SimulationRecord.created_at)).limit(limit).all()
        except Exception as e:
            logger.error(f"列出模拟记录失败: {e}")
            return []
    
    @staticmethod
    def update_simulation_progress(db: Session, simulation_id: str, current_round: int,
                                 total_rounds: int, progress_percentage: float,
                                 elapsed_time: float, estimated_remaining: Optional[float] = None,
                                 current_rtp: Optional[float] = None,
                                 total_bet_amount: Optional[float] = None,
                                 total_payout_amount: Optional[float] = None) -> bool:
        """更新模拟进度"""
        try:
            # 查找现有进度记录
            progress = db.query(SimulationProgress).filter(SimulationProgress.simulation_id == simulation_id).first()
            
            if progress:
                # 更新现有记录
                progress.current_round = current_round
                progress.total_rounds = total_rounds
                progress.progress_percentage = progress_percentage
                progress.elapsed_time = elapsed_time
                if estimated_remaining is not None:
                    progress.estimated_remaining = estimated_remaining
                if current_rtp is not None:
                    progress.current_rtp = current_rtp
                if total_bet_amount is not None:
                    progress.total_bet_amount = total_bet_amount
                if total_payout_amount is not None:
                    progress.total_payout_amount = total_payout_amount
                progress.updated_at = datetime.now()
            else:
                # 创建新记录
                progress = SimulationProgress(
                    simulation_id=simulation_id,
                    current_round=current_round,
                    total_rounds=total_rounds,
                    progress_percentage=progress_percentage,
                    elapsed_time=elapsed_time,
                    estimated_remaining=estimated_remaining,
                    current_rtp=current_rtp,
                    total_bet_amount=total_bet_amount or 0.0,
                    total_payout_amount=total_payout_amount or 0.0
                )
                db.add(progress)
            
            db.commit()
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"更新模拟进度失败: {e}")
            return False
    
    @staticmethod
    def get_simulation_progress(db: Session, simulation_id: str) -> Optional[SimulationProgress]:
        """获取模拟进度"""
        try:
            return db.query(SimulationProgress).filter(SimulationProgress.simulation_id == simulation_id).first()
        except Exception as e:
            logger.error(f"获取模拟进度失败: {e}")
            return None
    
    @staticmethod
    def log_system_event(db: Session, level: str, message: str, module: str = None,
                        function: str = None, simulation_id: str = None,
                        config_name: str = None, extra_data: Dict = None) -> bool:
        """记录系统日志"""
        try:
            log_entry = SystemLog(
                level=level,
                message=message,
                module=module,
                function=function,
                simulation_id=simulation_id,
                config_name=config_name,
                extra_data=extra_data
            )
            
            db.add(log_entry)
            db.commit()
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"记录系统日志失败: {e}")
            return False
