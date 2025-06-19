#!/usr/bin/env python3
"""
测试修复后的未中奖人数统计
"""

import requests
import time

def test_fixed_non_winners():
    """测试修复后的未中奖人数统计"""
    base_url = "http://localhost:8001"
    
    print("🎰 测试修复后的未中奖人数统计...")
    
    # 创建简单的测试配置
    test_config = {
        "config_name": "修复后未中奖人数统计测试",
        "game_rules": {
            "game_type": "lottery",
            "name": "修复后未中奖人数统计测试彩票",
            "description": "测试修复后的未中奖人数统计功能",
            "number_range": [1, 10],  # 较小的数字范围
            "selection_count": 3,     # 选择3个数字
            "ticket_price": 10.0,
            "prize_levels": [
                {
                    "level": 1,
                    "name": "一等奖",
                    "match_condition": 3,  # 3个全中
                    "fixed_prize": None,
                    "prize_percentage": 1.0
                },
                {
                    "level": 2,
                    "name": "二等奖",
                    "match_condition": 2,  # 2个匹配
                    "fixed_prize": 50.0,
                    "prize_percentage": None
                }
            ],
            "jackpot": {
                "enabled": True,
                "initial_amount": 500.0,
                "contribution_rate": 0.2,
                "post_return_contribution_rate": 0.4,
                "return_rate": 0.3,
                "jackpot_fixed_prize": 100.0,
                "min_jackpot": 200.0
            }
        },
        "simulation_config": {
            "rounds": 5,  # 少量轮数便于验证
            "players_range": [50, 100],  # 适中的玩家数量
            "bets_range": [1, 1],  # 每人只投注1次
            "seed": 12345
        }
    }
    
    try:
        # 1. 保存测试配置
        print("1. 保存测试配置...")
        save_response = requests.post(
            f"{base_url}/api/v1/config/save?config_name={test_config['config_name']}", 
            json=test_config,
            timeout=10
        )
        
        if save_response.status_code == 200:
            print("   ✅ 测试配置保存成功")
        else:
            print(f"   ❌ 配置保存失败: {save_response.status_code}")
            return
        
        # 2. 启动模拟
        print("2. 启动模拟...")
        simulation_request = {
            "game_config": test_config["game_rules"],
            "simulation_config": test_config["simulation_config"]
        }
        
        start_response = requests.post(
            f"{base_url}/api/v1/simulation/start", 
            json=simulation_request,
            timeout=10
        )
        
        if start_response.status_code == 200:
            result = start_response.json()
            simulation_id = result.get("simulation_id")
            print(f"   ✅ 模拟启动成功: {simulation_id}")
        else:
            print(f"   ❌ 模拟启动失败: {start_response.status_code}")
            return
        
        # 3. 等待模拟完成
        print("3. 等待模拟完成...")
        time.sleep(3)  # 等待3秒让模拟完成
        
        # 4. 获取最终结果
        print("4. 获取最终结果...")
        try:
            result_response = requests.get(
                f"{base_url}/api/v1/simulation/result/{simulation_id}", 
                timeout=10
            )
            
            if result_response.status_code == 200:
                result = result_response.json()
                summary = result.get('summary', {})
                
                print("   📈 最终统计:")
                total_players = summary.get('total_players', 0)
                total_winners = summary.get('total_winners', 0)
                total_non_winners = summary.get('total_non_winners', 0)
                winning_rate = summary.get('winning_rate', 0)
                
                print(f"      总轮数: {summary.get('total_rounds', 0)}")
                print(f"      总玩家数: {total_players}")
                print(f"      总中奖人数: {total_winners}")
                print(f"      总未中奖人数: {total_non_winners}")
                print(f"      中奖率: {winning_rate*100:.2f}%")
                print(f"      平均RTP: {summary.get('average_rtp', 0)*100:.2f}%")
                
                # 验证统计数据的一致性
                print("   🎯 未中奖人数统计验证:")
                calculated_total = total_winners + total_non_winners
                if calculated_total == total_players:
                    print(f"      ✅ 统计数据一致: {total_winners} + {total_non_winners} = {total_players}")
                else:
                    print(f"      ❌ 统计数据不一致: {total_winners} + {total_non_winners} = {calculated_total} ≠ {total_players}")
                    print(f"         差异: {abs(calculated_total - total_players)}人")
                
                # 计算未中奖率
                non_winning_rate = (total_non_winners / total_players) if total_players > 0 else 0
                print(f"      📊 未中奖率: {non_winning_rate*100:.2f}%")
                print(f"      📊 中奖率验证: {winning_rate*100:.2f}% + {non_winning_rate*100:.2f}% = {(winning_rate + non_winning_rate)*100:.2f}%")
                
                # 验证百分比总和
                total_percentage = winning_rate + non_winning_rate
                if abs(total_percentage - 1.0) < 0.01:
                    print(f"      ✅ 百分比总和正确: {total_percentage*100:.2f}% ≈ 100%")
                else:
                    print(f"      ❌ 百分比总和错误: {total_percentage*100:.2f}% ≠ 100%")
                
                # 显示各奖级汇总
                prize_summary = summary.get('prize_summary', [])
                if prize_summary:
                    print("   🏆 各奖级汇总:")
                    total_prize_winners = 0
                    for prize in prize_summary:
                        if prize['winners_count'] > 0:
                            print(f"      {prize['name']}: {prize['winners_count']}人中奖, 总奖金: ¥{prize['total_amount']:.2f}")
                            total_prize_winners += prize['winners_count']
                    
                    if total_prize_winners > 0:
                        print(f"   📊 各奖级中奖人数总计: {total_prize_winners}")
                        if total_prize_winners == total_winners:
                            print(f"      ✅ 奖级中奖人数与总中奖人数一致")
                        else:
                            print(f"      ❌ 奖级中奖人数与总中奖人数不一致: {total_prize_winners} ≠ {total_winners}")
                
            else:
                print(f"   ❌ 获取结果失败: {result_response.status_code}")
                
        except Exception as e:
            print(f"   ❌ 获取结果异常: {e}")
        
    except Exception as e:
        print(f"❌ 测试异常: {e}")

if __name__ == "__main__":
    test_fixed_non_winners()
