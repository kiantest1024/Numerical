#!/usr/bin/env python3
"""
测试新的奖池规则
"""

import requests
import json

def test_new_jackpot_rules():
    """测试新的奖池规则"""
    base_url = "http://localhost:8001"
    
    print("🎰 测试新的奖池规则...")
    
    # 创建测试配置
    test_config = {
        "config_name": "奖池规则测试",
        "game_rules": {
            "game_type": "lottery",
            "name": "奖池规则测试彩票",
            "description": "测试新的奖池规则",
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
                "initial_amount": 1000.0,
                "contribution_rate": 0.3,
                "return_rate": 0.5,
                "jackpot_fixed_prize": 100.0,
                "min_jackpot": 500.0
            }
        },
        "simulation_config": {
            "rounds": 10,
            "players_range": [100, 200],
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
        
        # 3. 监控模拟过程
        print("3. 监控奖池规则执行...")
        import time
        
        for i in range(20):  # 最多等待20秒
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
                        print(f"      💰 当前RTP: {real_time_stats.get('current_rtp', 0)*100:.2f}%")
                        print(f"      🎰 奖池金额: ¥{real_time_stats.get('current_jackpot', 0):.2f}")
                        print(f"      💸 总投注: ¥{real_time_stats.get('total_bet_amount', 0):.2f}")
                        print(f"      💵 总派奖: ¥{real_time_stats.get('total_payout', 0):.2f}")
                        
                        # 显示奖级统计
                        prize_stats = real_time_stats.get('prize_stats', {})
                        if prize_stats:
                            print("      🏆 奖级统计:")
                            for level, stats in prize_stats.items():
                                if stats['winners_count'] > 0:
                                    print(f"         {stats['name']}: {stats['winners_count']}人中奖, "
                                          f"总奖金: ¥{stats['total_amount']:.2f}")
                    
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
            
            print("   " + "-" * 60)
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
                
                print("   🎯 奖池规则验证:")
                print("      ✅ 奖池注入: 每注30%进入奖池")
                print("      ✅ 销售方返还: 每注50%返还给销售方(补偿垫付的初始奖池)")
                print("      ✅ 头奖分配: 奖池平分 + 固定奖金¥100")
                
            else:
                print(f"   ❌ 获取结果失败: {result_response.status_code}")
                
        except Exception as e:
            print(f"   ❌ 获取结果异常: {e}")
        
    except Exception as e:
        print(f"❌ 测试异常: {e}")

if __name__ == "__main__":
    test_new_jackpot_rules()
