#!/usr/bin/env python3
"""
测试未中奖人数统计
"""

import requests
import time

def test_non_winners_statistics():
    """测试未中奖人数统计"""
    base_url = "http://localhost:8001"
    
    print("🎰 测试未中奖人数统计...")
    
    # 创建测试配置
    test_config = {
        "config_name": "未中奖人数统计测试",
        "game_rules": {
            "game_type": "lottery",
            "name": "未中奖人数统计测试彩票",
            "description": "测试未中奖人数统计功能",
            "number_range": [1, 20],  # 较大的数字范围，降低中奖概率
            "selection_count": 5,     # 选择5个数字，增加难度
            "ticket_price": 10.0,
            "prize_levels": [
                {
                    "level": 1,
                    "name": "一等奖",
                    "match_condition": 5,  # 5个全中
                    "fixed_prize": None,
                    "prize_percentage": 1.0
                },
                {
                    "level": 2,
                    "name": "二等奖",
                    "match_condition": 4,  # 4个匹配
                    "fixed_prize": 100.0,
                    "prize_percentage": None
                },
                {
                    "level": 3,
                    "name": "三等奖",
                    "match_condition": 3,  # 3个匹配
                    "fixed_prize": 50.0,
                    "prize_percentage": None
                },
                {
                    "level": 4,
                    "name": "四等奖",
                    "match_condition": 2,  # 2个匹配
                    "fixed_prize": 20.0,
                    "prize_percentage": None
                }
            ],
            "jackpot": {
                "enabled": True,
                "initial_amount": 1000.0,
                "contribution_rate": 0.2,
                "post_return_contribution_rate": 0.4,
                "return_rate": 0.3,
                "jackpot_fixed_prize": 500.0,
                "min_jackpot": 500.0
            }
        },
        "simulation_config": {
            "rounds": 20,  # 适中的轮数
            "players_range": [100, 200],  # 大量玩家便于观察中奖率
            "bets_range": [1, 2],
            "seed": 98765
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
            print(f"      数字范围: {test_config['game_rules']['number_range']}")
            print(f"      选择数量: {test_config['game_rules']['selection_count']}")
            print(f"      奖级设置: {len(test_config['game_rules']['prize_levels'])}个奖级")
            print(f"      玩家范围: {test_config['simulation_config']['players_range']}")
        else:
            print(f"   ❌ 配置保存失败: {save_response.status_code}")
            print(f"      错误: {save_response.text}")
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
            print(f"      错误: {start_response.text}")
            return
        
        # 3. 监控未中奖人数统计
        print("3. 监控未中奖人数统计...")
        
        for i in range(60):  # 最多等待60秒
            try:
                progress_response = requests.get(
                    f"{base_url}/api/v1/simulation/progress/{simulation_id}", 
                    timeout=5
                )
                
                if progress_response.status_code == 200:
                    progress = progress_response.json()
                    
                    print(f"   📊 进度: {progress.get('progress_percentage', 0):.1f}% "
                          f"(轮次: {progress.get('current_round', 0)}/{progress.get('total_rounds', 0)})")
                    
                    # 检查实时统计
                    real_time_stats = progress.get('real_time_stats')
                    if real_time_stats:
                        total_players = real_time_stats.get('total_players', 0)
                        total_winners = real_time_stats.get('total_winners', 0)
                        total_non_winners = real_time_stats.get('total_non_winners', 0)
                        winning_rate = real_time_stats.get('winning_rate', 0)
                        current_rtp = real_time_stats.get('current_rtp', 0)
                        
                        print(f"      👥 总玩家数: {total_players}")
                        print(f"      🎉 总中奖人数: {total_winners}")
                        print(f"      😞 总未中奖人数: {total_non_winners}")
                        print(f"      📈 中奖率: {winning_rate*100:.2f}%")
                        print(f"      💰 当前RTP: {current_rtp*100:.2f}%")
                        
                        # 验证统计数据的一致性
                        calculated_total = total_winners + total_non_winners
                        if calculated_total == total_players:
                            print(f"      ✅ 统计数据一致: {total_winners} + {total_non_winners} = {total_players}")
                        else:
                            print(f"      ❌ 统计数据不一致: {total_winners} + {total_non_winners} = {calculated_total} ≠ {total_players}")
                        
                        # 显示各奖级中奖情况
                        prize_stats = real_time_stats.get('prize_stats', {})
                        if prize_stats:
                            print("      🏆 各奖级中奖情况:")
                            total_prize_winners = 0
                            for level, stats in prize_stats.items():
                                if stats['winners_count'] > 0:
                                    print(f"         {stats['name']}: {stats['winners_count']}人中奖, 总奖金: ¥{stats['total_amount']:.2f}")
                                    total_prize_winners += stats['winners_count']
                            
                            if total_prize_winners > 0:
                                print(f"      📊 各奖级中奖人数总计: {total_prize_winners}")
                    
                    # 检查是否完成
                    if progress.get('completed') or progress.get('status') == 'completed':
                        print("   ✅ 模拟完成！")
                        break
                        
                else:
                    print(f"   ❌ 进度查询失败: {progress_response.status_code}")
                    break
                
            except Exception as e:
                print(f"   ❌ 查询异常: {e}")
                break
            
            print("   " + "-" * 80)
            time.sleep(2)
        
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
                print(f"      总轮数: {summary.get('total_rounds', 0)}")
                print(f"      总玩家数: {summary.get('total_players', 0)}")
                print(f"      总中奖人数: {summary.get('total_winners', 0)}")
                print(f"      总未中奖人数: {summary.get('total_non_winners', 0)}")
                print(f"      中奖率: {summary.get('winning_rate', 0)*100:.2f}%")
                print(f"      平均RTP: {summary.get('average_rtp', 0)*100:.2f}%")
                print(f"      头奖中出次数: {summary.get('jackpot_hits', 0)}")
                
                # 验证最终统计的一致性
                final_total_players = summary.get('total_players', 0)
                final_total_winners = summary.get('total_winners', 0)
                final_total_non_winners = summary.get('total_non_winners', 0)
                
                print("   🎯 未中奖人数统计验证:")
                if final_total_winners + final_total_non_winners == final_total_players:
                    print(f"      ✅ 最终统计数据一致: {final_total_winners} + {final_total_non_winners} = {final_total_players}")
                else:
                    print(f"      ❌ 最终统计数据不一致: {final_total_winners} + {final_total_non_winners} ≠ {final_total_players}")
                
                # 计算未中奖率
                non_winning_rate = (final_total_non_winners / final_total_players) if final_total_players > 0 else 0
                print(f"      📊 未中奖率: {non_winning_rate*100:.2f}%")
                print(f"      📊 中奖率验证: {summary.get('winning_rate', 0)*100:.2f}% + {non_winning_rate*100:.2f}% = {(summary.get('winning_rate', 0) + non_winning_rate)*100:.2f}%")
                
                # 显示各奖级汇总
                prize_summary = summary.get('prize_summary', [])
                if prize_summary:
                    print("   🏆 各奖级汇总:")
                    for prize in prize_summary:
                        if prize['winners_count'] > 0:
                            print(f"      {prize['name']}: {prize['winners_count']}人中奖, 总奖金: ¥{prize['total_amount']:.2f}")
                
            else:
                print(f"   ❌ 获取结果失败: {result_response.status_code}")
                
        except Exception as e:
            print(f"   ❌ 获取结果异常: {e}")
        
    except Exception as e:
        print(f"❌ 测试异常: {e}")

if __name__ == "__main__":
    test_non_winners_statistics()
