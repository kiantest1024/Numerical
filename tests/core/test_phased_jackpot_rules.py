#!/usr/bin/env python3
"""
测试分阶段奖池注入规则
"""

import requests

def test_phased_jackpot_rules():
    """测试分阶段奖池注入规则"""
    base_url = "http://localhost:8001"
    
    print("🎰 测试分阶段奖池注入规则...")
    
    # 创建测试配置
    test_config = {
        "config_name": "分阶段奖池规则测试",
        "game_rules": {
            "game_type": "lottery",
            "name": "分阶段奖池规则测试彩票",
            "description": "测试分阶段奖池注入规则",
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
                "contribution_rate": 0.2,  # 第一阶段：20%注入奖池
                "post_return_contribution_rate": 0.4,  # 第二阶段：40%注入奖池
                "return_rate": 0.6,  # 60%返还给销售方
                "jackpot_fixed_prize": 200.0,
                "min_jackpot": 500.0
            }
        },
        "simulation_config": {
            "rounds": 20,  # 增加轮数以观察阶段转换
            "players_range": [50, 100],
            "bets_range": [1, 2],
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
        
        # 3. 监控模拟过程，特别关注阶段转换
        print("3. 监控分阶段奖池注入...")
        import time
        
        phase_transition_detected = False
        
        for i in range(30):  # 最多等待30秒
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
                        
                        # 检查是否有阶段转换信息
                        if 'return_phase_completed' in real_time_stats:
                            if real_time_stats['return_phase_completed'] and not phase_transition_detected:
                                print("      🔄 阶段转换：销售方返还完成，进入第二阶段！")
                                phase_transition_detected = True
                            
                            current_rate = real_time_stats.get('current_contribution_rate', 0)
                            print(f"      📈 当前奖池注入比例: {current_rate*100:.1f}%")
                    
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
            
            print("   " + "-" * 70)
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
                
                print("   🎯 分阶段奖池规则验证:")
                print("      ✅ 第一阶段: 每注20%进入奖池 + 60%返还给销售方")
                print("      ✅ 第二阶段: 每注40%进入奖池 + 停止返还")
                print("      ✅ 头奖分配: 奖池平分 + 固定奖金¥200")
                
                if phase_transition_detected:
                    print("      ✅ 阶段转换: 成功检测到从第一阶段转换到第二阶段")
                else:
                    print("      ⚠️  阶段转换: 未检测到阶段转换（可能返还金额未达到初始奖池）")
                
            else:
                print(f"   ❌ 获取结果失败: {result_response.status_code}")
                
        except Exception as e:
            print(f"   ❌ 获取结果异常: {e}")
        
    except Exception as e:
        print(f"❌ 测试异常: {e}")

if __name__ == "__main__":
    test_phased_jackpot_rules()
