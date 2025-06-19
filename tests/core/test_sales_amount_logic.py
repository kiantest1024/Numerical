#!/usr/bin/env python3
"""
测试销售金额逻辑
"""

import sys
import os

# 添加后端路径到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'numericalTools', 'backend'))

from app.models.game_config import GameConfiguration, GameRules, JackpotConfig, PrizeLevel, SimulationConfig
from app.core.simulation_engine import UniversalSimulationEngine

def test_sales_amount_logic():
    """测试销售金额逻辑"""
    print("🎰 测试销售金额逻辑...")
    
    # 创建测试配置
    jackpot_config = JackpotConfig(
        enabled=True,
        initial_amount=1000.0,
        contribution_rate=0.2,  # 第一阶段：20%注入奖池
        post_return_contribution_rate=0.4,  # 第二阶段：40%注入奖池
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
        name="销售金额测试",
        description="测试销售金额逻辑",
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
    print(f"   累计销售: ¥{engine.total_sales_amount}")
    print(f"   第一阶段注入比例: {jackpot_config.contribution_rate*100}%")
    print(f"   第二阶段注入比例: {jackpot_config.post_return_contribution_rate*100}%")
    print(f"   销售方返还比例: {jackpot_config.return_rate*100}%")
    
    print("\n🔄 模拟投注过程...")
    
    # 模拟多次投注，观察资金分配
    ticket_price = game_rules.ticket_price
    total_bets = 0
    
    print(f"\n📋 资金分配详情（每注¥{ticket_price}）:")
    print("=" * 80)
    
    for i in range(200):  # 模拟200注投注
        total_bets += 1
        
        # 处理投注
        contribution_info = engine.process_ticket_contribution(ticket_price)
        
        # 每20注显示一次状态
        if total_bets % 20 == 0:
            print(f"\n📊 第{total_bets}注后状态:")
            print(f"   当前奖池: ¥{engine.jackpot_pool:.2f}")
            print(f"   累计返还: ¥{engine.total_returned_amount:.2f} / ¥{engine.initial_jackpot_amount}")
            print(f"   累计销售: ¥{engine.total_sales_amount:.2f}")
            print(f"   本注分配:")
            print(f"     - 奖池注入: ¥{contribution_info['jackpot_contribution']:.2f} ({contribution_info['current_contribution_rate']*100:.1f}%)")
            print(f"     - 销售方返还: ¥{contribution_info['seller_return']:.2f}")
            print(f"     - 销售金额: ¥{contribution_info['sales_amount']:.2f}")
            print(f"   返还阶段完成: {'是' if contribution_info['return_phase_completed'] else '否'}")
            
            # 验证资金分配总和
            total_allocation = (contribution_info['jackpot_contribution'] + 
                              contribution_info['seller_return'] + 
                              contribution_info['sales_amount'])
            print(f"   资金分配验证: ¥{total_allocation:.2f} (应该等于¥{ticket_price})")
            
            # 检查阶段转换
            if contribution_info['return_phase_completed']:
                print(f"   🎉 阶段转换已完成！现在使用{jackpot_config.post_return_contribution_rate*100}%注入比例")
                
                # 验证第二阶段逻辑
                if total_bets >= 180:  # 验证几注第二阶段投注
                    expected_jackpot = ticket_price * jackpot_config.post_return_contribution_rate
                    expected_sales = ticket_price - expected_jackpot
                    print(f"   第二阶段验证:")
                    print(f"     - 预期奖池注入: ¥{expected_jackpot:.2f}")
                    print(f"     - 实际奖池注入: ¥{contribution_info['jackpot_contribution']:.2f}")
                    print(f"     - 预期销售金额: ¥{expected_sales:.2f}")
                    print(f"     - 实际销售金额: ¥{contribution_info['sales_amount']:.2f}")
                    print(f"     - 预期销售方返还: ¥0.00")
                    print(f"     - 实际销售方返还: ¥{contribution_info['seller_return']:.2f}")
                    break
    
    print(f"\n📈 最终状态:")
    print(f"   总投注注数: {total_bets}")
    print(f"   总投注金额: ¥{total_bets * ticket_price}")
    print(f"   最终奖池: ¥{engine.jackpot_pool:.2f}")
    print(f"   累计返还给销售方: ¥{engine.total_returned_amount:.2f}")
    print(f"   累计销售金额: ¥{engine.total_sales_amount:.2f}")
    print(f"   返还阶段完成: {'是' if engine.total_returned_amount >= engine.initial_jackpot_amount else '否'}")
    
    # 验证资金分配的正确性
    print(f"\n🎯 资金分配验证:")
    
    # 计算总投注金额
    total_bet_amount = total_bets * ticket_price
    
    # 计算各部分金额
    total_jackpot_contribution = engine.jackpot_pool - engine.initial_jackpot_amount
    total_seller_return = engine.total_returned_amount
    total_sales = engine.total_sales_amount
    
    print(f"   总投注金额: ¥{total_bet_amount:.2f}")
    print(f"   奖池注入总额: ¥{total_jackpot_contribution:.2f}")
    print(f"   销售方返还总额: ¥{total_seller_return:.2f}")
    print(f"   销售金额总额: ¥{total_sales:.2f}")
    
    # 验证总和
    calculated_total = total_jackpot_contribution + total_seller_return + total_sales
    print(f"   计算总和: ¥{calculated_total:.2f}")
    print(f"   分配正确性: {'✅' if abs(calculated_total - total_bet_amount) < 0.01 else '❌'}")
    
    # 验证阶段转换点
    transition_point = engine.initial_jackpot_amount / (ticket_price * jackpot_config.return_rate)
    print(f"   理论阶段转换点: 第{transition_point:.1f}注")
    print(f"   实际阶段转换: {'已发生' if engine.total_returned_amount >= engine.initial_jackpot_amount else '未发生'}")
    
    # 计算销售金额占比
    sales_percentage = (total_sales / total_bet_amount) * 100 if total_bet_amount > 0 else 0
    print(f"   销售金额占比: {sales_percentage:.2f}%")
    
    print(f"\n🎊 销售金额逻辑验证完成！")

if __name__ == "__main__":
    test_sales_amount_logic()
