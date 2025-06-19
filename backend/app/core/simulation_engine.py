"""
通用数值模拟引擎
基于现有lottery_simulator_optimized.py进行重构和扩展
"""

import random
import numpy as np
import pandas as pd
import time
import asyncio
from typing import List, Dict, Tuple, Optional, Set
from collections import deque, defaultdict
import uuid
from datetime import datetime

from ..models.game_config import GameConfiguration, GameRules, JackpotConfig, PrizeLevel
from ..models.simulation_result import (
    SimulationResult, SimulationSummary, RoundResult, 
    PrizeStatistics, SimulationProgress
)


class UniversalSimulationEngine:
    """通用模拟引擎"""
    
    def __init__(self, game_config: GameConfiguration):
        """
        初始化模拟引擎
        
        Args:
            game_config: 游戏配置
        """
        self.game_config = game_config
        self.game_rules = game_config.game_rules
        self.sim_config = game_config.simulation_config
        
        # 模拟状态
        self.simulation_id = str(uuid.uuid4())
        self.current_round = 0
        self.start_time = None
        self.is_running = False
        self.should_stop = False
        
        # 奖池和资金池
        self.jackpot_pool = self.game_rules.jackpot.initial_amount
        self.funding_pool = 0.0
        
        # 奖级映射
        self.prize_map = self._build_prize_map()
        
        # 结果存储
        self.round_results = []
        self.detailed_records = deque(maxlen=10000)  # 限制内存使用
        
        # 进度回调
        self.progress_callback = None
        
        # 设置随机种子
        if self.sim_config.seed:
            random.seed(self.sim_config.seed)
            np.random.seed(self.sim_config.seed)
    
    def _build_prize_map(self) -> Dict[int, float]:
        """构建奖级映射"""
        prize_map = {}
        for prize_level in self.game_rules.prize_levels:
            if prize_level.fixed_prize is not None:
                prize_map[prize_level.match_condition] = prize_level.fixed_prize
            else:
                # 奖池分配类型，运行时计算
                prize_map[prize_level.match_condition] = 0.0
        return prize_map
    
    def generate_winning_numbers(self) -> Set[int]:
        """生成开奖号码"""
        min_num, max_num = self.game_rules.number_range
        return set(random.sample(range(min_num, max_num + 1), self.game_rules.selection_count))
    
    def generate_player_numbers(self) -> Set[int]:
        """生成玩家选号"""
        min_num, max_num = self.game_rules.number_range
        return set(random.sample(range(min_num, max_num + 1), self.game_rules.selection_count))
    
    def check_matches(self, player_numbers: Set[int], winning_numbers: Set[int]) -> int:
        """检查匹配数量"""
        return len(player_numbers & winning_numbers)
    
    def process_ticket_contribution(self, ticket_price: float) -> float:
        """
        处理单注投注的资金分配
        返回进入奖池的金额
        """
        if not self.game_rules.jackpot.enabled:
            return 0.0
        
        contribution_rate = self.game_rules.jackpot.contribution_rate
        return_rate = self.game_rules.jackpot.return_rate
        
        if self.funding_pool < 0:
            # 优先偿还资金池
            repay_amount = min(ticket_price * (1 - return_rate), -self.funding_pool)
            self.funding_pool += repay_amount
            # 剩余部分进入奖池
            jackpot_contrib = ticket_price * contribution_rate * return_rate
        else:
            # 全部按比例进入奖池
            jackpot_contrib = ticket_price * contribution_rate
        
        self.jackpot_pool += jackpot_contrib
        return jackpot_contrib
    
    def calculate_prize(self, matches: int, winners_count: Dict[int, int]) -> float:
        """计算奖金"""
        if matches not in self.prize_map:
            return 0.0
        
        # 查找对应的奖级配置
        prize_level = None
        for level in self.game_rules.prize_levels:
            if level.match_condition == matches:
                prize_level = level
                break
        
        if not prize_level:
            return 0.0
        
        # 固定奖金
        if prize_level.fixed_prize is not None:
            return prize_level.fixed_prize
        
        # 奖池分配
        if prize_level.prize_percentage is not None and matches == max(self.prize_map.keys()):
            # 最高奖级使用奖池
            if winners_count[matches] > 0:
                total_jackpot = self.jackpot_pool * prize_level.prize_percentage
                prize_per_winner = total_jackpot / winners_count[matches]
                
                # 从奖池中扣除
                self.jackpot_pool -= total_jackpot
                # 如果奖池不足，从资金池借贷
                if self.jackpot_pool < 0:
                    self.funding_pool += self.jackpot_pool
                    self.jackpot_pool = 0
                
                return prize_per_winner
        
        return 0.0
    
    def simulate_round(self, round_number: int) -> RoundResult:
        """模拟单轮游戏"""
        # 生成本轮参数
        players_count = random.randint(*self.sim_config.players_range)
        
        # 生成开奖号码
        winning_numbers = self.generate_winning_numbers()
        winning_list = sorted(list(winning_numbers))
        
        # 初始化统计
        total_bets = 0
        total_bet_amount = 0.0
        total_payout = 0.0
        winners_count = defaultdict(int)
        winners_amount = defaultdict(float)
        
        # 模拟每个玩家
        for player_id in range(players_count):
            bets_count = random.randint(*self.sim_config.bets_range)
            total_bets += bets_count
            
            for bet_id in range(bets_count):
                bet_amount = self.game_rules.ticket_price
                total_bet_amount += bet_amount
                
                # 处理资金分配
                self.process_ticket_contribution(bet_amount)
                
                # 生成玩家选号
                player_numbers = self.generate_player_numbers()
                matches = self.check_matches(player_numbers, winning_numbers)
                
                # 统计中奖
                if matches >= 2:  # 假设2个匹配以上才有奖
                    winners_count[matches] += 1
        
        # 计算奖金
        for matches, count in winners_count.items():
            if count > 0:
                prize_per_winner = self.calculate_prize(matches, winners_count)
                total_prize = prize_per_winner * count
                winners_amount[matches] = total_prize
                total_payout += total_prize
        
        # 计算RTP
        rtp = (total_payout / total_bet_amount) if total_bet_amount > 0 else 0.0
        
        # 构建奖级统计
        prize_stats = []
        for prize_level in self.game_rules.prize_levels:
            matches = prize_level.match_condition
            count = winners_count.get(matches, 0)
            amount = winners_amount.get(matches, 0.0)
            
            # 简化概率计算，避免复杂的组合数计算导致卡顿
            probability = 1.0 / (2 ** matches) if matches > 0 else 0.0  # 简化概率估算
            
            prize_stats.append(PrizeStatistics(
                level=prize_level.level,
                name=prize_level.name,
                winners_count=count,
                total_amount=amount,
                probability=probability
            ))
        
        return RoundResult(
            round_number=round_number,
            players_count=players_count,
            total_bets=total_bets,
            total_bet_amount=total_bet_amount,
            total_payout=total_payout,
            rtp=rtp,
            jackpot_amount=self.jackpot_pool,
            prize_stats=prize_stats,
            winning_numbers=winning_list
        )
    
    def _calculate_combinations(self, n: int, r: int) -> int:
        """计算组合数 C(n,r)"""
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
    
    def set_progress_callback(self, callback):
        """设置进度回调函数"""
        self.progress_callback = callback
    
    def stop_simulation(self):
        """停止模拟"""
        self.should_stop = True
    
    async def run_simulation(self) -> SimulationResult:
        """运行完整模拟"""
        self.start_time = datetime.now()
        self.is_running = True
        self.should_stop = False
        
        try:
            # 初始化结果
            result = SimulationResult(
                simulation_id=self.simulation_id,
                game_config_id=self.game_config.id,
                start_time=self.start_time,
                status="running",
                game_name=self.game_rules.name,
                simulation_rounds=self.sim_config.rounds
            )
            
            # 运行模拟
            for round_num in range(1, self.sim_config.rounds + 1):
                if self.should_stop:
                    break

                self.current_round = round_num
                round_result = self.simulate_round(round_num)
                self.round_results.append(round_result)

                # 更新进度
                if self.progress_callback:
                    progress = SimulationProgress(
                        current_round=round_num,
                        total_rounds=self.sim_config.rounds,
                        progress_percentage=(round_num / self.sim_config.rounds) * 100,
                        elapsed_time=(datetime.now() - self.start_time).total_seconds(),
                        status="running"
                    )
                    await self.progress_callback(progress)

                # 每10轮让出控制权，允许其他协程运行
                if round_num % 10 == 0:
                    await asyncio.sleep(0.01)  # 让出控制权，允许进度查询
            
            # 生成汇总统计
            summary = self._generate_summary()
            
            # 完成模拟
            end_time = datetime.now()
            duration = (end_time - self.start_time).total_seconds()
            
            result.end_time = end_time
            result.duration = duration
            result.status = "completed" if not self.should_stop else "stopped"
            result.summary = summary
            result.round_results = self.round_results
            
            return result
            
        except Exception as e:
            # 处理错误
            result.status = "error"
            result.error_message = str(e)
            result.end_time = datetime.now()
            return result
        
        finally:
            self.is_running = False
    
    def _generate_summary(self) -> SimulationSummary:
        """生成汇总统计"""
        if not self.round_results:
            return None
        
        # 计算汇总数据
        total_rounds = len(self.round_results)
        total_players = sum(r.players_count for r in self.round_results)
        total_bets = sum(r.total_bets for r in self.round_results)
        total_bet_amount = sum(r.total_bet_amount for r in self.round_results)
        total_payout = sum(r.total_payout for r in self.round_results)
        
        # 计算平均RTP和方差
        rtps = [r.rtp for r in self.round_results]
        average_rtp = np.mean(rtps)
        rtp_variance = np.var(rtps)
        
        # 奖池统计
        initial_jackpot = self.game_rules.jackpot.initial_amount
        final_jackpot = self.jackpot_pool
        
        # 计算头奖中出次数（假设最高匹配数为头奖）
        max_matches = max(level.match_condition for level in self.game_rules.prize_levels)
        jackpot_hits = sum(
            sum(1 for stat in r.prize_stats if stat.level == 1 and stat.winners_count > 0)
            for r in self.round_results
        )
        
        # 各奖级汇总
        prize_summary = []
        for prize_level in self.game_rules.prize_levels:
            total_winners = sum(
                sum(stat.winners_count for stat in r.prize_stats if stat.level == prize_level.level)
                for r in self.round_results
            )
            total_amount = sum(
                sum(stat.total_amount for stat in r.prize_stats if stat.level == prize_level.level)
                for r in self.round_results
            )
            
            # 计算平均概率
            probabilities = [
                stat.probability for r in self.round_results 
                for stat in r.prize_stats if stat.level == prize_level.level
            ]
            avg_probability = np.mean(probabilities) if probabilities else 0.0
            
            prize_summary.append(PrizeStatistics(
                level=prize_level.level,
                name=prize_level.name,
                winners_count=total_winners,
                total_amount=total_amount,
                probability=avg_probability
            ))
        
        return SimulationSummary(
            total_rounds=total_rounds,
            total_players=total_players,
            total_bets=total_bets,
            total_bet_amount=total_bet_amount,
            total_payout=total_payout,
            average_rtp=average_rtp,
            rtp_variance=rtp_variance,
            initial_jackpot=initial_jackpot,
            final_jackpot=final_jackpot,
            jackpot_hits=jackpot_hits,
            prize_summary=prize_summary
        )
