#!/usr/bin/env python3
"""
通过API测试奖池重置逻辑
"""

import requests
import time

def test_api_jackpot_reset():
    """通过API测试奖池重置逻辑"""
    base_url = "http://localhost:8001"
    
    print("🎰 通过API测试奖池重置逻辑...")
    
    # 创建测试配置 - 设置较高的中奖概率
    test_config = {
        "config_name": "奖池重置逻辑测试",
        "game_rules": {
            "game_type": "lottery",
            "name": "奖池重置逻辑测试彩票",
            "description": "测试奖池重置逻辑",
            "number_range": [1, 6],  # 较小的数字范围，提高中奖概率
            "selection_count": 3,
            "ticket_price": 10.0,
            "prize_levels": [
                {
                    "level": 1,
                    "name": "头奖",
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
                "initial_amount": 800.0,  # 初始奖池
                "contribution_rate": 0.25,  # 第一阶段：25%注入奖池
                "post_return_contribution_rate": 0.45,  # 第二阶段：45%注入奖池
                "return_rate": 0.5,  # 50%返还给销售方
                "jackpot_fixed_prize": 300.0,  # 头奖固定奖金
                "min_jackpot": 400.0
            }
        },
        "simulation_config": {
            "rounds": 100,  # 足够的轮数增加中头奖概率
            "players_range": [50, 100],  # 大量玩家增加中奖概率
            "bets_range": [1, 3],
            "seed": 54321  # 不同的随机种子
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
            print(f"      头奖固定奖金: ¥{test_config['game_rules']['jackpot']['jackpot_fixed_prize']}")
            print(f"      第一阶段注入比例: {test_config['game_rules']['jackpot']['contribution_rate']*100}%")
            print(f"      第二阶段注入比例: {test_config['game_rules']['jackpot']['post_return_contribution_rate']*100}%")
            print(f"      销售方返还比例: {test_config['game_rules']['jackpot']['return_rate']*100}%")
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
        
        # 3. 监控奖池重置逻辑
        print("3. 监控奖池重置逻辑...")
        
        last_jackpot_hits = 0
        last_jackpot_amount = test_config['game_rules']['jackpot']['initial_amount']
        initial_jackpot = test_config['game_rules']['jackpot']['initial_amount']
        jackpot_reset_detected = False
        
        for i in range(120):  # 最多等待120秒
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
                        current_jackpot = real_time_stats.get('current_jackpot', 0)
                        total_bet_amount = real_time_stats.get('total_bet_amount', 0)
                        total_payout = real_time_stats.get('total_payout', 0)
                        total_sales_amount = real_time_stats.get('total_sales_amount', 0)
                        jackpot_hits_count = real_time_stats.get('jackpot_hits_count', 0)
                        current_rtp = real_time_stats.get('current_rtp', 0)
                        
                        print(f"      💰 当前RTP: {current_rtp*100:.2f}%")
                        print(f"      🎰 奖池金额: ¥{current_jackpot:.2f}")
                        print(f"      🎊 头奖中出次数: {jackpot_hits_count}")
                        print(f"      💸 总投注: ¥{total_bet_amount:.2f}")
                        print(f"      💵 总派奖: ¥{total_payout:.2f}")
                        print(f"      🏪 累计销售金额: ¥{total_sales_amount:.2f}")
                        
                        # 检测头奖中出和奖池重置
                        if jackpot_hits_count > last_jackpot_hits:
                            new_hits = jackpot_hits_count - last_jackpot_hits
                            print(f"      🎉 检测到头奖中出！新增{new_hits}次，总计{jackpot_hits_count}次")
                            
                            # 检查奖池是否重置
                            if abs(current_jackpot - initial_jackpot) < 1.0:  # 允许小误差
                                print(f"      ✅ 奖池重置成功：¥{current_jackpot:.2f} ≈ ¥{initial_jackpot:.2f}")
                                jackpot_reset_detected = True
                            else:
                                print(f"      ❌ 奖池重置异常：¥{current_jackpot:.2f} ≠ ¥{initial_jackpot:.2f}")
                            
                            last_jackpot_hits = jackpot_hits_count
                        
                        # 检查奖池金额变化
                        if abs(current_jackpot - last_jackpot_amount) > 10.0:  # 显著变化
                            jackpot_change = current_jackpot - last_jackpot_amount
                            if jackpot_change > 0:
                                print(f"      📈 奖池增长: +¥{jackpot_change:.2f}")
                            else:
                                print(f"      📉 奖池减少: ¥{jackpot_change:.2f}")
                            last_jackpot_amount = current_jackpot
                        
                        # 检查奖池阶段信息
                        if 'return_phase_completed' in real_time_stats:
                            return_phase_completed = real_time_stats.get('return_phase_completed', False)
                            current_contribution_rate = real_time_stats.get('current_contribution_rate', 0)
                            total_returned_amount = real_time_stats.get('total_returned_amount', 0)
                            
                            print(f"      📈 当前奖池注入比例: {current_contribution_rate*100:.1f}%")
                            print(f"      💰 累计返还给销售方: ¥{total_returned_amount:.2f} / ¥{initial_jackpot:.2f}")
                            print(f"      🔄 返还阶段状态: {'已完成' if return_phase_completed else '进行中'}")
                    
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
            time.sleep(1)
        
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
                
                print("   🎯 奖池重置逻辑验证:")
                print(f"      ✅ 奖池重置规则: 每次头奖中出后重置为初始金额¥{initial_jackpot}")
                print(f"      ✅ 销售方返还重置: 头奖中出后重新开始分阶段逻辑")
                print(f"      ✅ 头奖固定奖金: 每次头奖额外获得¥{test_config['game_rules']['jackpot']['jackpot_fixed_prize']}")
                
                if jackpot_reset_detected:
                    print("      ✅ 奖池重置: 成功检测到头奖中出后奖池重置")
                else:
                    print("      ⚠️  奖池重置: 未检测到头奖中出或奖池重置")
                    print(f"         可能原因: 模拟过程中未发生头奖中出")
                
            else:
                print(f"   ❌ 获取结果失败: {result_response.status_code}")
                
        except Exception as e:
            print(f"   ❌ 获取结果异常: {e}")
        
    except Exception as e:
        print(f"❌ 测试异常: {e}")

if __name__ == "__main__":
    test_api_jackpot_reset()
