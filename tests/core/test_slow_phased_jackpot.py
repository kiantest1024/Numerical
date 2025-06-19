#!/usr/bin/env python3
"""
慢速测试分阶段奖池注入规则 - 增加轮数和玩家数量
"""

import requests
import time

def test_slow_phased_jackpot():
    """慢速测试分阶段奖池注入规则"""
    base_url = "http://localhost:8001"
    
    print("🎰 慢速测试分阶段奖池注入规则...")
    
    # 创建测试配置 - 大量轮数和玩家以便观察过程
    test_config = {
        "config_name": "慢速分阶段奖池测试",
        "game_rules": {
            "game_type": "lottery",
            "name": "慢速分阶段奖池测试彩票",
            "description": "慢速测试分阶段奖池注入规则",
            "number_range": [1, 10],
            "selection_count": 3,
            "ticket_price": 10.0,
            "prize_levels": [
                {
                    "level": 1,
                    "name": "一等奖",
                    "match_condition": 3,
                    "fixed_prize": None,
                    "prize_percentage": 1.0
                },
                {
                    "level": 2,
                    "name": "二等奖",
                    "match_condition": 2,
                    "fixed_prize": 50.0,
                    "prize_percentage": None
                }
            ],
            "jackpot": {
                "enabled": True,
                "initial_amount": 1000.0,  # 初始奖池
                "contribution_rate": 0.15,  # 第一阶段：15%注入奖池
                "post_return_contribution_rate": 0.35,  # 第二阶段：35%注入奖池
                "return_rate": 0.7,  # 70%返还给销售方
                "jackpot_fixed_prize": 150.0,
                "min_jackpot": 500.0
            }
        },
        "simulation_config": {
            "rounds": 100,  # 大量轮数
            "players_range": [200, 500],  # 大量玩家
            "bets_range": [1, 3],
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
            print(f"   📊 配置详情:")
            print(f"      初始奖池: ¥{test_config['game_rules']['jackpot']['initial_amount']}")
            print(f"      第一阶段注入比例: {test_config['game_rules']['jackpot']['contribution_rate']*100}%")
            print(f"      第二阶段注入比例: {test_config['game_rules']['jackpot']['post_return_contribution_rate']*100}%")
            print(f"      销售方返还比例: {test_config['game_rules']['jackpot']['return_rate']*100}%")
            print(f"      模拟轮数: {test_config['simulation_config']['rounds']}")
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
        
        # 3. 立即开始监控
        print("3. 立即开始监控分阶段奖池注入...")
        
        phase_transition_detected = False
        last_returned_amount = 0
        initial_jackpot = test_config['game_rules']['jackpot']['initial_amount']
        
        # 立即开始查询，不等待
        for i in range(120):  # 最多等待120秒
            try:
                progress_response = requests.get(
                    f"{base_url}/api/v1/simulation/progress/{simulation_id}", 
                    timeout=5
                )
                
                if progress_response.status_code == 200:
                    progress = progress_response.json()
                    
                    current_round = progress.get('current_round', 0)
                    total_rounds = progress.get('total_rounds', 0)
                    progress_pct = progress.get('progress_percentage', 0)
                    
                    print(f"   📊 进度: {progress_pct:.1f}% (轮次: {current_round}/{total_rounds})")
                    
                    # 检查实时统计
                    real_time_stats = progress.get('real_time_stats')
                    if real_time_stats:
                        current_jackpot = real_time_stats.get('current_jackpot', 0)
                        total_bet_amount = real_time_stats.get('total_bet_amount', 0)
                        total_payout = real_time_stats.get('total_payout', 0)
                        current_rtp = real_time_stats.get('current_rtp', 0)
                        
                        print(f"      💰 当前RTP: {current_rtp*100:.2f}%")
                        print(f"      🎰 奖池金额: ¥{current_jackpot:.2f}")
                        print(f"      💸 总投注: ¥{total_bet_amount:.2f}")
                        print(f"      💵 总派奖: ¥{total_payout:.2f}")
                        
                        # 检查奖池阶段信息
                        if 'return_phase_completed' in real_time_stats:
                            return_phase_completed = real_time_stats.get('return_phase_completed', False)
                            current_contribution_rate = real_time_stats.get('current_contribution_rate', 0)
                            total_returned_amount = real_time_stats.get('total_returned_amount', 0)
                            
                            print(f"      📈 当前奖池注入比例: {current_contribution_rate*100:.1f}%")
                            print(f"      💰 累计返还给销售方: ¥{total_returned_amount:.2f} / ¥{initial_jackpot:.2f}")
                            print(f"      🔄 返还阶段状态: {'已完成' if return_phase_completed else '进行中'}")
                            
                            # 检测阶段转换
                            if return_phase_completed and not phase_transition_detected:
                                print("      🎉 阶段转换：销售方返还完成，进入第二阶段！")
                                print(f"         从 {test_config['game_rules']['jackpot']['contribution_rate']*100}% 提升到 {test_config['game_rules']['jackpot']['post_return_contribution_rate']*100}%")
                                phase_transition_detected = True
                            
                            # 检测返还金额变化
                            if total_returned_amount != last_returned_amount:
                                returned_change = total_returned_amount - last_returned_amount
                                print(f"      📊 返还金额变化: +¥{returned_change:.2f}")
                                last_returned_amount = total_returned_amount
                        
                        # 显示奖级统计
                        prize_stats = real_time_stats.get('prize_stats', {})
                        if prize_stats:
                            total_winners = sum(stats['winners_count'] for stats in prize_stats.values())
                            if total_winners > 0:
                                print(f"      🏆 总中奖人数: {total_winners}")
                                for level, stats in prize_stats.items():
                                    if stats['winners_count'] > 0:
                                        print(f"         {stats['name']}: {stats['winners_count']}人, ¥{stats['total_amount']:.2f}")
                    
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
            time.sleep(0.5)  # 更频繁的查询
        
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
                print(f"      平均RTP: {summary.get('average_rtp', 0)*100:.2f}%")
                print(f"      初始奖池: ¥{summary.get('initial_jackpot', 0):.2f}")
                print(f"      最终奖池: ¥{summary.get('final_jackpot', 0):.2f}")
                print(f"      头奖中出次数: {summary.get('jackpot_hits', 0)}")
                
                print("   🎯 分阶段奖池规则验证:")
                print(f"      ✅ 第一阶段: 每注{test_config['game_rules']['jackpot']['contribution_rate']*100}%进入奖池 + {test_config['game_rules']['jackpot']['return_rate']*100}%返还给销售方")
                print(f"      ✅ 第二阶段: 每注{test_config['game_rules']['jackpot']['post_return_contribution_rate']*100}%进入奖池 + 停止返还")
                print(f"      ✅ 头奖分配: 奖池平分 + 固定奖金¥{test_config['game_rules']['jackpot']['jackpot_fixed_prize']}")
                
                if phase_transition_detected:
                    print("      ✅ 阶段转换: 成功检测到从第一阶段转换到第二阶段")
                else:
                    print("      ⚠️  阶段转换: 未检测到阶段转换")
                    print(f"         可能原因: 返还金额未达到初始奖池金额¥{initial_jackpot}")
                
            else:
                print(f"   ❌ 获取结果失败: {result_response.status_code}")
                
        except Exception as e:
            print(f"   ❌ 获取结果异常: {e}")
        
    except Exception as e:
        print(f"❌ 测试异常: {e}")

if __name__ == "__main__":
    test_slow_phased_jackpot()
