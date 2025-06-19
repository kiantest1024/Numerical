"""
游戏配置数据模型
"""

from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional, Union
from enum import Enum


class GameType(str, Enum):
    """游戏类型枚举"""
    LOTTERY = "lottery"  # 彩票类游戏
    SCRATCH = "scratch"  # 刮刮乐
    SLOT = "slot"        # 老虎机
    CUSTOM = "custom"    # 自定义


class PrizeLevel(BaseModel):
    """奖级配置"""
    level: int = Field(..., description="奖级等级（1为最高奖级）")
    name: str = Field(..., description="奖级名称")
    match_condition: int = Field(..., description="匹配条件（如匹配6个数字）")
    fixed_prize: Optional[float] = Field(None, description="固定奖金（如果不是奖池分配）")
    prize_percentage: Optional[float] = Field(None, description="奖池分配百分比")
    
    @validator('match_condition')
    def validate_match_condition(cls, v):
        if v < 0:
            raise ValueError("匹配条件不能为负数")
        return v
    
    @validator('fixed_prize')
    def validate_fixed_prize(cls, v):
        if v is not None and v < 0:
            raise ValueError("固定奖金不能为负数")
        return v


class JackpotConfig(BaseModel):
    """奖池配置"""
    enabled: bool = Field(default=False, description="是否启用奖池")
    initial_amount: float = Field(default=0.0, description="初始奖池金额")
    contribution_rate: float = Field(default=0.15, description="投注金额进入奖池的比例")
    return_rate: float = Field(default=0.9, description="奖池返还比例")
    min_jackpot: float = Field(default=0.0, description="最小奖池保底金额")
    
    @validator('contribution_rate', 'return_rate')
    def validate_rates(cls, v):
        if not 0 <= v <= 1:
            raise ValueError("比例必须在0-1之间")
        return v


class GameRules(BaseModel):
    """游戏规则配置"""
    game_type: GameType = Field(..., description="游戏类型")
    name: str = Field(..., description="游戏名称")
    description: Optional[str] = Field(None, description="游戏描述")
    
    # 基础设置
    number_range: tuple[int, int] = Field(..., description="数字范围 (最小值, 最大值)")
    selection_count: int = Field(..., description="选择数量")
    ticket_price: float = Field(..., description="单注价格")
    
    # 奖级设置
    prize_levels: List[PrizeLevel] = Field(..., description="奖级配置列表")
    
    # 奖池设置
    jackpot: JackpotConfig = Field(default_factory=JackpotConfig, description="奖池配置")
    
    @validator('number_range')
    def validate_number_range(cls, v):
        if v[0] >= v[1]:
            raise ValueError("数字范围最小值必须小于最大值")
        if v[0] < 1:
            raise ValueError("数字范围最小值不能小于1")
        return v
    
    @validator('selection_count')
    def validate_selection_count(cls, v, values):
        if 'number_range' in values:
            range_size = values['number_range'][1] - values['number_range'][0] + 1
            if v > range_size:
                raise ValueError("选择数量不能超过数字范围大小")
        if v < 1:
            raise ValueError("选择数量必须大于0")
        return v
    
    @validator('ticket_price')
    def validate_ticket_price(cls, v):
        if v <= 0:
            raise ValueError("单注价格必须大于0")
        return v


class SimulationConfig(BaseModel):
    """模拟配置"""
    rounds: int = Field(..., description="模拟轮数", ge=1, le=10_000_000)
    players_range: tuple[int, int] = Field(..., description="玩家数量范围 (最小值, 最大值)")
    bets_range: tuple[int, int] = Field(..., description="投注数量范围 (最小值, 最大值)")
    seed: Optional[int] = Field(None, description="随机种子（用于可重现的结果）")
    
    @validator('players_range', 'bets_range')
    def validate_ranges(cls, v):
        if v[0] > v[1]:
            raise ValueError("范围最小值不能大于最大值")
        if v[0] < 1:
            raise ValueError("范围最小值必须大于0")
        return v


class GameConfiguration(BaseModel):
    """完整游戏配置"""
    id: Optional[str] = Field(None, description="配置ID")
    game_rules: GameRules = Field(..., description="游戏规则")
    simulation_config: SimulationConfig = Field(..., description="模拟配置")
    created_at: Optional[str] = Field(None, description="创建时间")
    updated_at: Optional[str] = Field(None, description="更新时间")
