#!/usr/bin/env python3
"""
@numericalTools 后端测试脚本
"""

import sys
import os
import asyncio
from pathlib import Path

# 添加backend路径到sys.path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from app.models.game_config import GameConfiguration, GameRules, PrizeLevel, JackpotConfig, SimulationConfig
from app.core.simulation_engine import UniversalSimulationEngine


def create_test_config():
    """创建测试配置"""
    
    # 创建奖级配置
    prize_levels = [
        PrizeLevel(
            level=1,
            name="一等奖",
            match_condition=6,
            fixed_prize=None,
            prize_percentage=0.9
        ),
        PrizeLevel(
            level=2,
            name="二等奖", 
            match_condition=5,
            fixed_prize=50000.0,
            prize_percentage=None
        ),
        PrizeLevel(
            level=3,
            name="三等奖",
            match_condition=4,
            fixed_prize=1500.0,
            prize_percentage=None
        ),
        PrizeLevel(
            level=4,
            name="四等奖",
            match_condition=3,
            fixed_prize=60.0,
            prize_percentage=None
        ),
        PrizeLevel(
            level=5,
            name="五等奖",
            match_condition=2,
            fixed_prize=20.0,
            prize_percentage=None
        )
    ]
    
    # 创建奖池配置
    jackpot_config = JackpotConfig(
        enabled=True,
        initial_amount=30000000.0,
        contribution_rate=0.15,
        return_rate=0.9,
        min_jackpot=10000000.0
    )
    
    # 创建游戏规则
    game_rules = GameRules(
        game_type="lottery",
        name="42选6彩票测试",
        description="测试用的42选6彩票游戏",
        number_range=(1, 42),
        selection_count=6,
        ticket_price=20.0,
        prize_levels=prize_levels,
        jackpot=jackpot_config
    )
    
    # 创建模拟配置
    simulation_config = SimulationConfig(
        rounds=100,  # 测试用较小的轮数
        players_range=(1000, 2000),
        bets_range=(5, 10),
        seed=12345  # 固定种子以便重现结果
    )
    
    # 创建完整配置
    game_config = GameConfiguration(
        id="test_config",
        game_rules=game_rules,
        simulation_config=simulation_config
    )
    
    return game_config


async def test_simulation_engine():
    """测试模拟引擎"""
    print("🧪 测试模拟引擎...")
    
    # 创建测试配置
    config = create_test_config()
    print(f"✅ 配置创建成功: {config.game_rules.name}")
    
    # 创建模拟引擎
    engine = UniversalSimulationEngine(config)
    print(f"✅ 模拟引擎创建成功: {engine.simulation_id}")
    
    # 设置进度回调
    async def progress_callback(progress):
        print(f"📊 进度: {progress.progress_percentage:.1f}% "
              f"({progress.current_round}/{progress.total_rounds})")
    
    engine.set_progress_callback(progress_callback)
    
    # 运行模拟
    print("🚀 开始模拟...")
    result = await engine.run_simulation()
    
    # 检查结果
    if result.status == "completed":
        print("✅ 模拟完成!")
        
        if result.summary:
            summary = result.summary
            print(f"📈 模拟结果:")
            print(f"   总轮数: {summary.total_rounds}")
            print(f"   总玩家数: {summary.total_players:,}")
            print(f"   总投注金额: ¥{summary.total_bet_amount:,.2f}")
            print(f"   总派奖金额: ¥{summary.total_payout:,.2f}")
            print(f"   平均RTP: {summary.average_rtp:.2%}")
            print(f"   头奖中出次数: {summary.jackpot_hits}")
            print(f"   最终奖池: ¥{summary.final_jackpot:,.2f}")
            
            print(f"\n🏆 各奖级统计:")
            for prize_stat in summary.prize_summary:
                print(f"   {prize_stat.name}: {prize_stat.winners_count}人中奖, "
                      f"总奖金¥{prize_stat.total_amount:,.2f}")
        
        print(f"\n⏱️  模拟耗时: {result.duration:.2f}秒")
        
    else:
        print(f"❌ 模拟失败: {result.error_message}")
        return False
    
    return True


def test_config_validation():
    """测试配置验证"""
    print("\n🧪 测试配置验证...")
    
    try:
        # 测试正常配置
        config = create_test_config()
        print("✅ 正常配置验证通过")
        
        # 测试异常配置
        try:
            invalid_config = GameRules(
                game_type="lottery",
                name="无效配置",
                number_range=(10, 5),  # 无效范围
                selection_count=6,
                ticket_price=20.0,
                prize_levels=[]
            )
            print("❌ 应该抛出验证错误")
            return False
        except Exception as e:
            print(f"✅ 正确捕获验证错误: {type(e).__name__}")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置验证测试失败: {e}")
        return False


def test_helper_functions():
    """测试工具函数"""
    print("\n🧪 测试工具函数...")
    
    try:
        from app.utils.helpers import (
            calculate_combinations, 
            calculate_probability,
            format_currency,
            format_percentage
        )
        
        # 测试组合数计算
        c_42_6 = calculate_combinations(42, 6)
        print(f"✅ C(42,6) = {c_42_6:,}")
        
        # 测试概率计算
        prob = calculate_probability(42, 6, 6)
        print(f"✅ 42选6中6个的概率: {prob:.10f}")
        
        # 测试格式化函数
        currency = format_currency(1234567.89)
        percentage = format_percentage(0.9234)
        print(f"✅ 货币格式化: {currency}")
        print(f"✅ 百分比格式化: {percentage}")
        
        return True
        
    except Exception as e:
        print(f"❌ 工具函数测试失败: {e}")
        return False


async def main():
    """主测试函数"""
    print("=" * 60)
    print("🔧 @numericalTools 后端功能测试")
    print("=" * 60)
    
    tests = [
        ("配置验证", test_config_validation),
        ("工具函数", test_helper_functions),
        ("模拟引擎", test_simulation_engine)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            if result:
                print(f"✅ {test_name} 测试通过")
                passed += 1
            else:
                print(f"❌ {test_name} 测试失败")
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
    
    print(f"\n{'='*60}")
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过!")
        return True
    else:
        print("⚠️  部分测试失败")
        return False


if __name__ == "__main__":
    # 运行测试
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
