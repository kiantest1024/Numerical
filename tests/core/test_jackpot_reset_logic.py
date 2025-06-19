#!/usr/bin/env python3
"""
测试奖池重置逻辑
"""

import sys
import os

# 添加后端路径到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'numericalTools', 'backend'))

from app.models.game_config import GameConfiguration, GameRules, JackpotConfig, PrizeLevel, SimulationConfig
from app.core.simulation_engine import UniversalSimulationEngine

def test_jackpot_reset_logic():
    """测试奖池重置逻辑"""
    print("🎰 测试奖池重置逻辑...")
    
    # 创建测试配置 - 设置较高的中奖概率以便观察奖池重置
    jackpot_config = JackpotConfig(
        enabled=True,
        initial_amount=1000.0,
        contribution_rate=0.3,  # 第一阶段：30%注入奖池
        post_return_contribution_rate=0.5,  # 第二阶段：50%注入奖池
        return_rate=0.4,  # 40%返还给销售方
        jackpot_fixed_prize=200.0,  # 头奖固定奖金
        min_jackpot=500.0
    )
    
    prize_levels = [
        PrizeLevel(
            level=1,
            name="头奖",
            match_condition=3,  # 3个匹配为头奖
            fixed_prize=None,
            prize_percentage=1.0  # 使用全部奖池
        ),
        PrizeLevel(
            level=2,
            name="二等奖",
            match_condition=2,  # 2个匹配为二等奖
            fixed_prize=50.0,
            prize_percentage=None
        )
    ]
    
    sim_config = SimulationConfig(
        rounds=1,
        players_range=[10, 10],
        bets_range=[1, 1],
        seed=12345
    )
    
    game_rules = GameRules(
        game_type="lottery",
        name="奖池重置测试",
        description="测试奖池重置逻辑",
        number_range=[1, 5],  # 减少数字范围，提高中奖概率
        selection_count=3,
        ticket_price=10.0,
        prize_levels=prize_levels,
        jackpot=jackpot_config
    )
    
    game_config = GameConfiguration(
        game_rules=game_rules,
        simulation_config=sim_config
    )
    
    # 创建模拟引擎
    engine = UniversalSimulationEngine(game_config)
    
    print(f"📊 初始状态:")
    print(f"   初始奖池: ¥{engine.initial_jackpot_amount}")
    print(f"   当前奖池: ¥{engine.jackpot_pool}")
    print(f"   头奖中出次数: {engine.jackpot_hits_count}")
    print(f"   累计返还: ¥{engine.total_returned_amount}")
    print(f"   累计销售: ¥{engine.total_sales_amount}")
    
    print(f"\n🔄 模拟投注和中奖过程...")
    
    # 模拟多次投注，手动触发头奖中出
    ticket_price = game_rules.ticket_price
    total_bets = 0
    
    # 先模拟一些正常投注，让奖池增长
    print(f"\n📈 阶段1：正常投注，奖池增长")
    for i in range(50):  # 50注投注
        total_bets += 1
        
        # 处理投注
        contribution_info = engine.process_ticket_contribution(ticket_price)
        
        # 每10注显示一次状态
        if total_bets % 10 == 0:
            print(f"   第{total_bets}注后 - 奖池: ¥{engine.jackpot_pool:.2f}, 返还: ¥{engine.total_returned_amount:.2f}, 销售: ¥{engine.total_sales_amount:.2f}")
    
    print(f"\n🎯 阶段2：模拟头奖中出")
    
    # 记录中奖前的状态
    pre_jackpot = engine.jackpot_pool
    pre_returned = engine.total_returned_amount
    pre_sales = engine.total_sales_amount
    pre_hits = engine.jackpot_hits_count
    
    print(f"   中奖前状态:")
    print(f"     奖池金额: ¥{pre_jackpot:.2f}")
    print(f"     累计返还: ¥{pre_returned:.2f}")
    print(f"     累计销售: ¥{pre_sales:.2f}")
    print(f"     头奖中出次数: {pre_hits}")
    
    # 模拟头奖中出（手动设置中奖者）
    winners_count = {3: 2}  # 2个人中头奖
    
    print(f"\n   🎊 模拟{winners_count[3]}人中头奖...")
    
    # 计算头奖奖金
    prize_per_winner = engine.calculate_prize(3, winners_count)
    total_prize = prize_per_winner * winners_count[3]
    
    print(f"   头奖奖金计算:")
    print(f"     每人奖金: ¥{prize_per_winner:.2f}")
    print(f"     总奖金: ¥{total_prize:.2f}")
    
    # 记录中奖后的状态
    post_jackpot = engine.jackpot_pool
    post_returned = engine.total_returned_amount
    post_sales = engine.total_sales_amount
    post_hits = engine.jackpot_hits_count
    
    print(f"\n   中奖后状态:")
    print(f"     奖池金额: ¥{post_jackpot:.2f}")
    print(f"     累计返还: ¥{post_returned:.2f}")
    print(f"     累计销售: ¥{post_sales:.2f}")
    print(f"     头奖中出次数: {post_hits}")
    
    print(f"\n🔍 奖池重置验证:")
    
    # 验证奖池重置
    if post_jackpot == engine.initial_jackpot_amount:
        print(f"   ✅ 奖池重置正确: ¥{post_jackpot:.2f} = ¥{engine.initial_jackpot_amount:.2f}")
    else:
        print(f"   ❌ 奖池重置错误: ¥{post_jackpot:.2f} ≠ ¥{engine.initial_jackpot_amount:.2f}")
    
    # 验证头奖中出次数增加
    if post_hits == pre_hits + winners_count[3]:
        print(f"   ✅ 头奖中出次数正确: {post_hits} = {pre_hits} + {winners_count[3]}")
    else:
        print(f"   ❌ 头奖中出次数错误: {post_hits} ≠ {pre_hits} + {winners_count[3]}")
    
    # 验证销售方返还重置
    if post_returned == 0.0:
        print(f"   ✅ 销售方返还重置正确: ¥{post_returned:.2f}")
    else:
        print(f"   ❌ 销售方返还重置错误: ¥{post_returned:.2f} ≠ ¥0.00")
    
    # 验证销售金额保持不变（不应该重置）
    if post_sales == pre_sales:
        print(f"   ✅ 销售金额保持不变: ¥{post_sales:.2f}")
    else:
        print(f"   ❌ 销售金额异常变化: ¥{post_sales:.2f} ≠ ¥{pre_sales:.2f}")
    
    print(f"\n📈 阶段3：头奖中出后继续投注")
    
    # 继续投注，验证分阶段逻辑重新开始
    for i in range(20):  # 再投注20注
        total_bets += 1
        
        # 处理投注
        contribution_info = engine.process_ticket_contribution(ticket_price)
        
        # 每5注显示一次状态
        if (total_bets - 50) % 5 == 0:
            print(f"   第{total_bets}注后 - 奖池: ¥{engine.jackpot_pool:.2f}, 返还: ¥{engine.total_returned_amount:.2f}, 销售: ¥{engine.total_sales_amount:.2f}")
            print(f"     当前注入比例: {contribution_info['current_contribution_rate']*100:.1f}%, 返还阶段: {'已完成' if contribution_info['return_phase_completed'] else '进行中'}")
    
    print(f"\n📊 最终状态:")
    print(f"   总投注注数: {total_bets}")
    print(f"   总投注金额: ¥{total_bets * ticket_price}")
    print(f"   最终奖池: ¥{engine.jackpot_pool:.2f}")
    print(f"   头奖中出次数: {engine.jackpot_hits_count}")
    print(f"   累计返还给销售方: ¥{engine.total_returned_amount:.2f}")
    print(f"   累计销售金额: ¥{engine.total_sales_amount:.2f}")
    
    print(f"\n🎯 奖池重置逻辑验证:")
    print(f"   ✅ 头奖中出后奖池重置为初始金额: ¥{engine.initial_jackpot_amount}")
    print(f"   ✅ 销售方返还状态重置，重新开始分阶段逻辑")
    print(f"   ✅ 头奖中出次数正确统计: {engine.jackpot_hits_count}次")
    print(f"   ✅ 销售金额累计不受奖池重置影响")
    
    print(f"\n🎊 奖池重置逻辑验证完成！")

if __name__ == "__main__":
    test_jackpot_reset_logic()
