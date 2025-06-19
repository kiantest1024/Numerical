#!/usr/bin/env python3
"""
验证分阶段奖池逻辑的正确性
"""

import sys
import os

# 添加后端路径到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'numericalTools', 'backend'))

from app.models.game_config import GameConfiguration, GameRules, JackpotConfig, PrizeLevel, SimulationConfig
from app.core.simulation_engine import UniversalSimulationEngine

def test_phased_jackpot_logic():
    """测试分阶段奖池逻辑"""
    print("🎰 验证分阶段奖池逻辑...")
    
    # 创建测试配置
    jackpot_config = JackpotConfig(
        enabled=True,
        initial_amount=1000.0,
        contribution_rate=0.2,  # 第一阶段：20%
        post_return_contribution_rate=0.4,  # 第二阶段：40%
        return_rate=0.6,  # 60%返还给销售方
        jackpot_fixed_prize=100.0,
        min_jackpot=500.0
    )
    
    prize_levels = [
        PrizeLevel(
            level=1,
            name="一等奖",
            match_condition=3,
            fixed_prize=None,
            prize_percentage=1.0
        ),
        PrizeLevel(
            level=2,
            name="二等奖",
            match_condition=2,
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
        name="分阶段奖池测试",
        description="测试分阶段奖池逻辑",
        number_range=[1, 10],
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
    print(f"   累计返还: ¥{engine.total_returned_amount}")
    print(f"   第一阶段注入比例: {jackpot_config.contribution_rate*100}%")
    print(f"   第二阶段注入比例: {jackpot_config.post_return_contribution_rate*100}%")
    print(f"   销售方返还比例: {jackpot_config.return_rate*100}%")
    
    print("\n🔄 模拟投注过程...")
    
    # 模拟多次投注，观察阶段转换
    ticket_price = game_rules.ticket_price
    total_bets = 0
    
    for i in range(200):  # 模拟200注投注
        total_bets += 1
        
        # 处理投注
        contribution_info = engine.process_ticket_contribution(ticket_price)
        
        # 每10注显示一次状态
        if total_bets % 10 == 0:
            print(f"\n📊 第{total_bets}注后状态:")
            print(f"   当前奖池: ¥{engine.jackpot_pool:.2f}")
            print(f"   累计返还: ¥{engine.total_returned_amount:.2f} / ¥{engine.initial_jackpot_amount}")
            print(f"   本注奖池注入: ¥{contribution_info['jackpot_contribution']:.2f}")
            print(f"   本注销售方返还: ¥{contribution_info['seller_return']:.2f}")
            print(f"   当前注入比例: {contribution_info['current_contribution_rate']*100:.1f}%")
            print(f"   返还阶段完成: {'是' if contribution_info['return_phase_completed'] else '否'}")
            
            # 检查阶段转换
            if contribution_info['return_phase_completed']:
                print(f"   🎉 阶段转换已完成！现在使用{jackpot_config.post_return_contribution_rate*100}%注入比例")
                break
        
        # 如果返还阶段完成，再投注几注验证第二阶段
        if contribution_info['return_phase_completed'] and total_bets > 100:
            print(f"\n✅ 验证第二阶段逻辑（第{total_bets}注）:")
            print(f"   奖池注入比例: {contribution_info['current_contribution_rate']*100}% (应该是{jackpot_config.post_return_contribution_rate*100}%)")
            print(f"   销售方返还: ¥{contribution_info['seller_return']} (应该是0)")
            
            if total_bets >= 110:  # 验证10注第二阶段投注
                break
    
    print(f"\n📈 最终状态:")
    print(f"   总投注注数: {total_bets}")
    print(f"   总投注金额: ¥{total_bets * ticket_price}")
    print(f"   最终奖池: ¥{engine.jackpot_pool:.2f}")
    print(f"   累计返还给销售方: ¥{engine.total_returned_amount:.2f}")
    print(f"   返还阶段完成: {'是' if engine.total_returned_amount >= engine.initial_jackpot_amount else '否'}")
    
    # 验证逻辑正确性
    print(f"\n🎯 逻辑验证:")
    
    # 计算预期的返还金额
    expected_return = min(engine.initial_jackpot_amount, total_bets * ticket_price * jackpot_config.return_rate)
    print(f"   预期累计返还: ¥{expected_return:.2f}")
    print(f"   实际累计返还: ¥{engine.total_returned_amount:.2f}")
    print(f"   返还金额正确: {'✅' if abs(expected_return - engine.total_returned_amount) < 0.01 else '❌'}")
    
    # 验证阶段转换点
    transition_point = engine.initial_jackpot_amount / (ticket_price * jackpot_config.return_rate)
    print(f"   理论阶段转换点: 第{transition_point:.1f}注")
    print(f"   实际阶段转换: {'已发生' if engine.total_returned_amount >= engine.initial_jackpot_amount else '未发生'}")
    
    print(f"\n🎊 分阶段奖池逻辑验证完成！")

if __name__ == "__main__":
    test_phased_jackpot_logic()
