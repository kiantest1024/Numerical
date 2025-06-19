#!/usr/bin/env python3
"""
测试容易中奖的奖级总奖金计算
"""

import requests
import time

def test_easy_win_prize_calculation():
    """测试容易中奖的奖级总奖金计算"""
    base_url = "http://localhost:8001"
    
    print("🏆 测试容易中奖的奖级总奖金计算...")
    
    # 创建极容易中奖的测试配置
    test_config = {
        "config_name": "容易中奖奖级总奖金计算测试",
        "game_rules": {
            "game_type": "lottery",
            "name": "容易中奖奖级总奖金计算测试彩票",
            "description": "测试奖级总奖金是否正确累计所有轮次",
            "number_range": [1, 3],   # 极小的数字范围
            "selection_count": 1,     # 只选择1个数字，中奖概率1/3
            "ticket_price": 10.0,
            "prize_levels": [
                {
                    "level": 1,
                    "name": "一等奖",
                    "match_condition": 1,  # 1个匹配就中奖
                    "fixed_prize": 50.0,   # 固定奖金50元
                    "prize_percentage": None
                }
            ],
            "jackpot": {
                "enabled": False  # 关闭奖池，简化计算
            }
        },
        "simulation_config": {
            "rounds": 2,  # 只模拟2轮，便于手工验证
            "players_range": [6, 6],  # 固定6个玩家
            "bets_range": [1, 1],  # 每人只投注1次
            "seed": 99999  # 固定种子，结果可重现
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
            print(f"   📊 配置详情:")
            print(f"      数字范围: {test_config['game_rules']['number_range']} (中奖概率约33%)")
            print(f"      选择数量: {test_config['game_rules']['selection_count']}")
            print(f"      一等奖固定奖金: ¥{test_config['game_rules']['prize_levels'][0]['fixed_prize']}")
            print(f"      模拟轮数: {test_config['simulation_config']['rounds']}")
            print(f"      每轮玩家数: {test_config['simulation_config']['players_range'][0]}")
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
        
        # 4. 获取详细结果进行验证
        print("4. 获取详细结果进行验证...")
        try:
            result_response = requests.get(
                f"{base_url}/api/v1/simulation/result/{simulation_id}", 
                timeout=10
            )
            
            if result_response.status_code == 200:
                result = result_response.json()
                summary = result.get('summary', {})
                round_results = result.get('round_results', [])
                
                print("   📊 轮次详细分析:")
                total_manual_calculation = 0.0
                total_winners_manual = 0
                
                for i, round_result in enumerate(round_results, 1):
                    print(f"      轮次 {i}:")
                    print(f"         玩家数: {round_result.get('players_count', 0)}")
                    print(f"         中奖人数: {round_result.get('winners_count', 0)}")
                    print(f"         未中奖人数: {round_result.get('non_winners_count', 0)}")
                    print(f"         开奖号码: {round_result.get('winning_numbers', [])}")
                    
                    # 分析奖级统计
                    prize_stats = round_result.get('prize_stats', [])
                    for prize in prize_stats:
                        if prize['level'] == 1:  # 一等奖
                            winners = prize['winners_count']
                            amount = prize['total_amount']
                            print(f"         一等奖: {winners}人中奖, 总奖金: ¥{amount}")
                            total_manual_calculation += amount
                            total_winners_manual += winners
                            
                            # 验证单轮奖金计算
                            expected_round_amount = winners * 50.0
                            if abs(amount - expected_round_amount) < 0.01:
                                print(f"         ✅ 单轮奖金正确: {winners} × ¥50 = ¥{amount}")
                            else:
                                print(f"         ❌ 单轮奖金错误: {winners} × ¥50 = ¥{expected_round_amount} ≠ ¥{amount}")
                
                print(f"\n   🧮 手工计算验证:")
                print(f"      手工计算总中奖人数: {total_winners_manual}")
                print(f"      手工计算总奖金: ¥{total_manual_calculation}")
                
                # 获取系统汇总结果
                prize_summary = summary.get('prize_summary', [])
                system_total_winners = 0
                system_total_amount = 0.0
                
                for prize in prize_summary:
                    if prize['level'] == 1:  # 一等奖
                        system_total_winners = prize['winners_count']
                        system_total_amount = prize['total_amount']
                        break
                
                print(f"\n   💻 系统计算结果:")
                print(f"      系统计算总中奖人数: {system_total_winners}")
                print(f"      系统计算总奖金: ¥{system_total_amount}")
                
                # 验证计算是否一致
                print(f"\n   🎯 计算验证:")
                if total_winners_manual == system_total_winners:
                    print(f"      ✅ 中奖人数计算一致: {total_winners_manual} = {system_total_winners}")
                else:
                    print(f"      ❌ 中奖人数计算不一致: {total_winners_manual} ≠ {system_total_winners}")
                
                if abs(total_manual_calculation - system_total_amount) < 0.01:
                    print(f"      ✅ 总奖金计算一致: ¥{total_manual_calculation} = ¥{system_total_amount}")
                else:
                    print(f"      ❌ 总奖金计算不一致: ¥{total_manual_calculation} ≠ ¥{system_total_amount}")
                
                # 验证固定奖金逻辑
                expected_total = total_winners_manual * 50.0  # 每人50元固定奖金
                print(f"\n   💰 固定奖金验证:")
                print(f"      预期总奖金: {total_winners_manual} × ¥50 = ¥{expected_total}")
                if abs(system_total_amount - expected_total) < 0.01:
                    print(f"      ✅ 固定奖金计算正确")
                else:
                    print(f"      ❌ 固定奖金计算错误")
                
                # 显示最终统计
                print(f"\n   📈 最终统计:")
                print(f"      总轮数: {summary.get('total_rounds', 0)}")
                print(f"      总玩家数: {summary.get('total_players', 0)}")
                print(f"      总中奖人数: {summary.get('total_winners', 0)}")
                print(f"      总未中奖人数: {summary.get('total_non_winners', 0)}")
                print(f"      中奖率: {summary.get('winning_rate', 0)*100:.2f}%")
                print(f"      平均RTP: {summary.get('average_rtp', 0)*100:.2f}%")
                
                # 总结测试结果
                if (total_winners_manual == system_total_winners and 
                    abs(total_manual_calculation - system_total_amount) < 0.01 and
                    abs(system_total_amount - expected_total) < 0.01):
                    print(f"\n   🎉 奖级总奖金计算测试通过！")
                    print(f"      ✅ 系统正确累计了所有轮次的奖金")
                    print(f"      ✅ 固定奖金计算正确")
                    print(f"      ✅ 数据一致性验证通过")
                else:
                    print(f"\n   ❌ 奖级总奖金计算测试失败！")
                
            else:
                print(f"   ❌ 获取结果失败: {result_response.status_code}")
                
        except Exception as e:
            print(f"   ❌ 获取结果异常: {e}")
        
    except Exception as e:
        print(f"❌ 测试异常: {e}")

if __name__ == "__main__":
    test_easy_win_prize_calculation()
