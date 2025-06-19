"""
配置管理API路由
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
import json
import os
from datetime import datetime
from sqlalchemy.orm import Session

from ..models.game_config import GameConfiguration, GameType, PrizeLevel, JackpotConfig
from ..core.config import settings
from ..database import get_db, init_database, test_connection
from ..services.database_service import DatabaseService

router = APIRouter()

# 配置存储路径
CONFIG_DIR = os.path.join(settings.UPLOAD_DIR, "configs")
os.makedirs(CONFIG_DIR, exist_ok=True)


@router.get("/templates")
async def get_config_templates():
    """获取预设配置模板"""
    templates = {
        "lottery_42_6": {
            "name": "42选6彩票",
            "description": "经典42选6彩票游戏",
            "game_rules": {
                "game_type": "lottery",
                "name": "42选6彩票",
                "description": "从1-42中选择6个数字",
                "number_range": [1, 42],
                "selection_count": 6,
                "ticket_price": 20.0,
                "prize_levels": [
                    {
                        "level": 1,
                        "name": "一等奖",
                        "match_condition": 6,
                        "fixed_prize": None,
                        "prize_percentage": 0.9
                    },
                    {
                        "level": 2,
                        "name": "二等奖",
                        "match_condition": 5,
                        "fixed_prize": 50000.0,
                        "prize_percentage": None
                    },
                    {
                        "level": 3,
                        "name": "三等奖",
                        "match_condition": 4,
                        "fixed_prize": 1500.0,
                        "prize_percentage": None
                    },
                    {
                        "level": 4,
                        "name": "四等奖",
                        "match_condition": 3,
                        "fixed_prize": 60.0,
                        "prize_percentage": None
                    },
                    {
                        "level": 5,
                        "name": "五等奖",
                        "match_condition": 2,
                        "fixed_prize": 20.0,
                        "prize_percentage": None
                    }
                ],
                "jackpot": {
                    "enabled": True,
                    "initial_amount": 30000000.0,
                    "contribution_rate": 0.15,
                    "return_rate": 0.9,
                    "min_jackpot": 10000000.0
                }
            },
            "simulation_config": {
                "rounds": 1000,
                "players_range": [50000, 100000],
                "bets_range": [5, 15],
                "seed": None
            }
        },
        "lottery_37_2": {
            "name": "37选2彩票",
            "description": "简单的37选2彩票游戏",
            "game_rules": {
                "game_type": "lottery",
                "name": "37选2彩票",
                "description": "从1-37中选择2个数字",
                "number_range": [1, 37],
                "selection_count": 2,
                "ticket_price": 10.0,
                "prize_levels": [
                    {
                        "level": 1,
                        "name": "一等奖",
                        "match_condition": 2,
                        "fixed_prize": 500.0,
                        "prize_percentage": None
                    },
                    {
                        "level": 2,
                        "name": "二等奖",
                        "match_condition": 1,
                        "fixed_prize": 10.0,
                        "prize_percentage": None
                    }
                ],
                "jackpot": {
                    "enabled": False,
                    "initial_amount": 0.0,
                    "contribution_rate": 0.0,
                    "return_rate": 0.0,
                    "min_jackpot": 0.0
                }
            },
            "simulation_config": {
                "rounds": 10000,
                "players_range": [1000, 5000],
                "bets_range": [1, 5],
                "seed": None
            }
        },
        "custom_game": {
            "name": "自定义游戏",
            "description": "可完全自定义的游戏模板",
            "game_rules": {
                "game_type": "custom",
                "name": "自定义游戏",
                "description": "请根据需要修改配置",
                "number_range": [1, 10],
                "selection_count": 3,
                "ticket_price": 5.0,
                "prize_levels": [
                    {
                        "level": 1,
                        "name": "一等奖",
                        "match_condition": 3,
                        "fixed_prize": 100.0,
                        "prize_percentage": None
                    }
                ],
                "jackpot": {
                    "enabled": False,
                    "initial_amount": 0.0,
                    "contribution_rate": 0.0,
                    "return_rate": 0.0,
                    "min_jackpot": 0.0
                }
            },
            "simulation_config": {
                "rounds": 1000,
                "players_range": [100, 500],
                "bets_range": [1, 3],
                "seed": None
            }
        }
    }
    
    return {"templates": templates}


@router.post("/save")
async def save_config(config: Dict[str, Any], config_name: str, db: Session = Depends(get_db)):
    """保存配置"""
    try:
        # 验证配置
        game_config = GameConfiguration(**config)

        # 添加时间戳
        config_data = config.copy()
        config_data["id"] = config_name
        config_data["created_at"] = datetime.now().isoformat()
        config_data["updated_at"] = datetime.now().isoformat()

        # 保存到数据库
        try:
            saved_config = DatabaseService.save_game_config(db, config_name, config_data)

            # 记录日志
            DatabaseService.log_system_event(
                db, "INFO", f"配置 '{config_name}' 保存成功",
                module="config", function="save_config", config_name=config_name
            )

            return {
                "success": True,
                "message": f"配置 '{config_name}' 保存成功",
                "config_id": config_name
            }

        except Exception as db_error:
            # 数据库保存失败，回退到文件保存
            print(f"数据库保存失败，使用文件保存: {db_error}")

            # 保存到文件（备用方案）
            config_file = os.path.join(CONFIG_DIR, f"{config_name}.json")
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)

            return {
                "success": True,
                "message": f"配置 '{config_name}' 保存成功（文件模式）",
                "config_id": config_name,
                "warning": "数据库不可用，已保存到文件"
            }

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"保存配置失败: {str(e)}")


@router.get("/load/{config_name}")
async def load_config(config_name: str, db: Session = Depends(get_db)):
    """加载配置"""
    try:
        # 首先尝试从数据库加载
        config_record = DatabaseService.get_game_config(db, config_name)

        if config_record:
            return {"config": config_record.config_data}

        # 数据库中没有，尝试从文件加载
        config_file = os.path.join(CONFIG_DIR, f"{config_name}.json")

        if not os.path.exists(config_file):
            raise HTTPException(status_code=404, detail="配置未找到")

        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = json.load(f)

        return {"config": config_data}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"加载配置失败: {str(e)}")


@router.get("/list")
async def list_configs(db: Session = Depends(get_db)):
    """列出所有保存的配置"""
    configs = []

    try:
        # 首先尝试从数据库获取
        db_configs = DatabaseService.list_game_configs(db)

        for config_record in db_configs:
            configs.append({
                "name": config_record.name,
                "display_name": config_record.display_name,
                "description": config_record.description,
                "game_type": config_record.game_type,
                "created_at": config_record.created_at.isoformat() if config_record.created_at else None,
                "updated_at": config_record.updated_at.isoformat() if config_record.updated_at else None
            })

        # 如果数据库中没有配置，尝试从文件加载
        if not configs and os.path.exists(CONFIG_DIR):
            for filename in os.listdir(CONFIG_DIR):
                if filename.endswith('.json'):
                    config_name = filename[:-5]  # 移除.json后缀
                    config_file = os.path.join(CONFIG_DIR, filename)

                    try:
                        with open(config_file, 'r', encoding='utf-8') as f:
                            config_data = json.load(f)

                        configs.append({
                            "name": config_name,
                            "display_name": config_data.get("game_rules", {}).get("name", config_name),
                            "description": config_data.get("game_rules", {}).get("description", ""),
                            "game_type": config_data.get("game_rules", {}).get("game_type", "unknown"),
                            "created_at": config_data.get("created_at"),
                            "updated_at": config_data.get("updated_at")
                        })

                    except Exception as e:
                        # 跳过损坏的配置文件
                        continue

    except Exception as e:
        print(f"数据库查询失败，使用文件模式: {e}")
        # 数据库查询失败，回退到文件模式
        if os.path.exists(CONFIG_DIR):
            for filename in os.listdir(CONFIG_DIR):
                if filename.endswith('.json'):
                    config_name = filename[:-5]
                    config_file = os.path.join(CONFIG_DIR, filename)

                    try:
                        with open(config_file, 'r', encoding='utf-8') as f:
                            config_data = json.load(f)

                        configs.append({
                            "name": config_name,
                            "display_name": config_data.get("game_rules", {}).get("name", config_name),
                            "description": config_data.get("game_rules", {}).get("description", ""),
                            "game_type": config_data.get("game_rules", {}).get("game_type", "unknown"),
                            "created_at": config_data.get("created_at"),
                            "updated_at": config_data.get("updated_at")
                        })

                    except Exception:
                        continue

    return {"configs": configs}


@router.delete("/delete/{config_name}")
async def delete_config(config_name: str):
    """删除配置"""
    config_file = os.path.join(CONFIG_DIR, f"{config_name}.json")
    
    if not os.path.exists(config_file):
        raise HTTPException(status_code=404, detail="配置文件未找到")
    
    try:
        os.remove(config_file)
        return {"message": f"配置 '{config_name}' 删除成功"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除配置失败: {str(e)}")


@router.post("/validate")
async def validate_config(config: Dict[str, Any]):
    """验证配置"""
    try:
        # 尝试解析配置
        game_config = GameConfiguration(**config)
        
        # 进行额外的业务逻辑验证
        validation_errors = []
        
        # 检查奖级配置
        prize_levels = game_config.game_rules.prize_levels
        if not prize_levels:
            validation_errors.append("至少需要配置一个奖级")
        
        # 检查匹配条件是否合理
        max_selection = game_config.game_rules.selection_count
        for level in prize_levels:
            if level.match_condition > max_selection:
                validation_errors.append(f"奖级 {level.name} 的匹配条件 ({level.match_condition}) 不能超过选择数量 ({max_selection})")
        
        # 检查奖池配置
        if game_config.game_rules.jackpot.enabled:
            if game_config.game_rules.jackpot.contribution_rate <= 0:
                validation_errors.append("启用奖池时，注入比例必须大于0")
        
        # 检查模拟配置
        if game_config.simulation_config.rounds > settings.MAX_SIMULATION_ROUNDS:
            validation_errors.append(f"模拟轮数不能超过 {settings.MAX_SIMULATION_ROUNDS}")
        
        if validation_errors:
            return {
                "valid": False,
                "message": "配置验证失败",
                "errors": validation_errors
            }
        
        return {
            "valid": True,
            "message": "配置验证通过",
            "config": game_config.dict()
        }
        
    except Exception as e:
        return {
            "valid": False,
            "message": f"配置验证失败: {str(e)}",
            "errors": [str(e)]
        }


@router.get("/game-types")
async def get_game_types():
    """获取支持的游戏类型"""
    return {
        "game_types": [
            {
                "value": "lottery",
                "label": "彩票类游戏",
                "description": "数字选择类彩票游戏"
            },
            {
                "value": "scratch",
                "label": "刮刮乐",
                "description": "即开型彩票游戏"
            },
            {
                "value": "slot",
                "label": "老虎机",
                "description": "转轮类游戏"
            },
            {
                "value": "custom",
                "label": "自定义",
                "description": "完全自定义的游戏类型"
            }
        ]
    }
