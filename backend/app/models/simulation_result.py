"""
模拟结果数据模型
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime


class PrizeStatistics(BaseModel):
    """奖级统计"""
    level: int = Field(..., description="奖级等级")
    name: str = Field(..., description="奖级名称")
    winners_count: int = Field(..., description="中奖人数")
    total_amount: float = Field(..., description="总奖金金额")
    probability: float = Field(..., description="中奖概率")


class RoundResult(BaseModel):
    """单轮结果"""
    round_number: int = Field(..., description="轮次编号")
    players_count: int = Field(..., description="参与玩家数")
    total_bets: int = Field(..., description="总投注数")
    total_bet_amount: float = Field(..., description="总投注金额")
    total_payout: float = Field(..., description="总派奖金额")
    rtp: float = Field(..., description="返奖率")
    jackpot_amount: float = Field(..., description="奖池金额")
    prize_stats: List[PrizeStatistics] = Field(..., description="各奖级统计")
    winning_numbers: Optional[List[int]] = Field(None, description="开奖号码")
    winners_count: Optional[int] = Field(None, description="中奖人数")
    non_winners_count: Optional[int] = Field(None, description="未中奖人数")


class SimulationSummary(BaseModel):
    """模拟汇总统计"""
    total_rounds: int = Field(..., description="总轮数")
    total_players: int = Field(..., description="总玩家数")
    total_bets: int = Field(..., description="总投注数")
    total_bet_amount: float = Field(..., description="总投注金额")
    total_payout: float = Field(..., description="总派奖金额")
    average_rtp: float = Field(..., description="平均返奖率")
    rtp_variance: float = Field(..., description="返奖率方差")

    # 中奖统计
    total_winners: Optional[int] = Field(None, description="总中奖人数")
    total_non_winners: Optional[int] = Field(None, description="总未中奖人数")
    winning_rate: Optional[float] = Field(None, description="中奖率")
    
    # 奖池统计
    initial_jackpot: float = Field(..., description="初始奖池")
    final_jackpot: float = Field(..., description="最终奖池")
    jackpot_hits: int = Field(..., description="头奖中出次数")
    
    # 各奖级汇总
    prize_summary: List[PrizeStatistics] = Field(..., description="各奖级汇总统计")
    
    # 概率分析
    theoretical_rtp: Optional[float] = Field(None, description="理论返奖率")
    rtp_deviation: Optional[float] = Field(None, description="返奖率偏差")


class SimulationProgress(BaseModel):
    """模拟进度"""
    current_round: int = Field(..., description="当前轮次")
    total_rounds: int = Field(..., description="总轮次")
    progress_percentage: float = Field(..., description="进度百分比")
    elapsed_time: float = Field(..., description="已用时间（秒）")
    estimated_remaining: Optional[float] = Field(None, description="预计剩余时间（秒）")
    status: str = Field(..., description="状态")


class ChartData(BaseModel):
    """图表数据"""
    chart_type: str = Field(..., description="图表类型")
    title: str = Field(..., description="图表标题")
    data: Dict[str, Any] = Field(..., description="图表数据")
    config: Optional[Dict[str, Any]] = Field(None, description="图表配置")


class SimulationResult(BaseModel):
    """完整模拟结果"""
    simulation_id: str = Field(..., description="模拟ID")
    game_config_id: Optional[str] = Field(None, description="游戏配置ID")
    
    # 基本信息
    start_time: datetime = Field(..., description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    duration: Optional[float] = Field(None, description="耗时（秒）")
    status: str = Field(..., description="状态")
    
    # 配置信息
    game_name: str = Field(..., description="游戏名称")
    simulation_rounds: int = Field(..., description="模拟轮数")
    
    # 结果数据
    summary: Optional[SimulationSummary] = Field(None, description="汇总统计")
    round_results: List[RoundResult] = Field(default_factory=list, description="各轮结果")
    
    # 可视化数据
    charts: List[ChartData] = Field(default_factory=list, description="图表数据")
    
    # 错误信息
    error_message: Optional[str] = Field(None, description="错误信息")


class SimulationRequest(BaseModel):
    """模拟请求"""
    game_config: Dict[str, Any] = Field(..., description="游戏配置")
    simulation_config: Dict[str, Any] = Field(..., description="模拟配置")
    options: Optional[Dict[str, Any]] = Field(None, description="额外选项")


class SimulationResponse(BaseModel):
    """模拟响应"""
    simulation_id: str = Field(..., description="模拟ID")
    status: str = Field(..., description="状态")
    message: str = Field(..., description="消息")
    result: Optional[SimulationResult] = Field(None, description="结果数据")
