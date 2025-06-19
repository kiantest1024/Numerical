"""
工具函数
"""

import math
import random
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta


def calculate_combinations(n: int, r: int) -> int:
    """
    计算组合数 C(n,r)
    
    Args:
        n: 总数
        r: 选择数
        
    Returns:
        组合数
    """
    if r > n or r < 0:
        return 0
    if r == 0 or r == n:
        return 1
    
    # 使用更高效的计算方法
    r = min(r, n - r)
    result = 1
    for i in range(r):
        result = result * (n - i) // (i + 1)
    return result


def calculate_probability(total_numbers: int, selection_count: int, matches: int) -> float:
    """
    计算中奖概率
    
    Args:
        total_numbers: 总号码数
        selection_count: 选择号码数
        matches: 匹配数
        
    Returns:
        中奖概率
    """
    if matches > selection_count or matches < 0:
        return 0.0
    
    # 计算总的组合数
    total_combinations = calculate_combinations(total_numbers, selection_count)
    
    # 计算匹配的组合数
    match_combinations = (
        calculate_combinations(selection_count, matches) *
        calculate_combinations(total_numbers - selection_count, selection_count - matches)
    )
    
    return match_combinations / total_combinations if total_combinations > 0 else 0.0


def format_currency(amount: float, currency: str = "¥") -> str:
    """
    格式化货币显示
    
    Args:
        amount: 金额
        currency: 货币符号
        
    Returns:
        格式化后的货币字符串
    """
    return f"{currency}{amount:,.2f}"


def format_percentage(value: float, decimal_places: int = 2) -> str:
    """
    格式化百分比显示
    
    Args:
        value: 数值（0-1之间）
        decimal_places: 小数位数
        
    Returns:
        格式化后的百分比字符串
    """
    return f"{value * 100:.{decimal_places}f}%"


def format_duration(seconds: float) -> str:
    """
    格式化时间长度
    
    Args:
        seconds: 秒数
        
    Returns:
        格式化后的时间字符串
    """
    if seconds < 60:
        return f"{seconds:.1f}秒"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}分钟"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}小时"


def generate_simulation_id() -> str:
    """
    生成模拟ID
    
    Returns:
        唯一的模拟ID
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    random_suffix = random.randint(1000, 9999)
    return f"sim_{timestamp}_{random_suffix}"


def validate_number_range(min_val: int, max_val: int) -> bool:
    """
    验证数字范围
    
    Args:
        min_val: 最小值
        max_val: 最大值
        
    Returns:
        是否有效
    """
    return min_val > 0 and max_val > min_val


def validate_selection_count(selection_count: int, range_size: int) -> bool:
    """
    验证选择数量
    
    Args:
        selection_count: 选择数量
        range_size: 范围大小
        
    Returns:
        是否有效
    """
    return 0 < selection_count <= range_size


def calculate_theoretical_rtp(prize_levels: List[Dict[str, Any]], 
                            total_numbers: int, 
                            selection_count: int,
                            ticket_price: float) -> float:
    """
    计算理论RTP
    
    Args:
        prize_levels: 奖级配置
        total_numbers: 总号码数
        selection_count: 选择数量
        ticket_price: 单注价格
        
    Returns:
        理论RTP
    """
    total_expected_payout = 0.0
    
    for level in prize_levels:
        matches = level.get('match_condition', 0)
        fixed_prize = level.get('fixed_prize')
        
        if fixed_prize is not None:
            probability = calculate_probability(total_numbers, selection_count, matches)
            expected_payout = probability * fixed_prize
            total_expected_payout += expected_payout
    
    return total_expected_payout / ticket_price if ticket_price > 0 else 0.0


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    安全除法，避免除零错误
    
    Args:
        numerator: 分子
        denominator: 分母
        default: 默认值
        
    Returns:
        除法结果或默认值
    """
    return numerator / denominator if denominator != 0 else default


def clamp(value: float, min_val: float, max_val: float) -> float:
    """
    将值限制在指定范围内
    
    Args:
        value: 输入值
        min_val: 最小值
        max_val: 最大值
        
    Returns:
        限制后的值
    """
    return max(min_val, min(value, max_val))


def convert_to_native_types(obj: Any) -> Any:
    """
    将NumPy类型转换为Python原生类型
    
    Args:
        obj: 输入对象
        
    Returns:
        转换后的对象
    """
    if isinstance(obj, (np.int64, np.int32, np.int16, np.int8)):
        return int(obj)
    if isinstance(obj, (np.float64, np.float32)):
        return float(obj)
    if isinstance(obj, dict):
        return {key: convert_to_native_types(value) for key, value in obj.items()}
    if isinstance(obj, list):
        return [convert_to_native_types(item) for item in obj]
    return obj


def estimate_simulation_time(rounds: int, players_range: tuple, bets_range: tuple) -> float:
    """
    估算模拟时间
    
    Args:
        rounds: 模拟轮数
        players_range: 玩家数范围
        bets_range: 投注数范围
        
    Returns:
        估算时间（秒）
    """
    avg_players = (players_range[0] + players_range[1]) / 2
    avg_bets = (bets_range[0] + bets_range[1]) / 2
    total_operations = rounds * avg_players * avg_bets
    
    # 基于经验的时间估算（每百万次操作约需1秒）
    estimated_seconds = total_operations / 1_000_000
    
    return max(1.0, estimated_seconds)  # 至少1秒
