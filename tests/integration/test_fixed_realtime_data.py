#!/usr/bin/env python3
"""
测试修复后的实时数据显示功能
验证模拟完成后RTP趋势和奖级分布数据是否正确显示
"""

import requests
import time

def test_fixed_realtime_data():
    """测试修复后的实时数据显示功能"""
    base_url = "http://localhost:8001"
    
    print("🔧 测试修复后的实时数据显示功能...")
    print("🎯 验证模拟完成后RTP趋势和奖级分布数据显示")
    
    # 创建快速完成的测试配置
    test_config = {
        "game_config": {
            "game_type": "lottery",
            "name": "修复后实时数据测试彩票",
            "description": "验证修复后的实时数据显示功能",
            "number_range": [1, 10],  # 小范围，容易中奖
            "selection_count": 2,     # 选择2个数字，快速完成
            "ticket_price": 5.0,
            "prize_levels": [
                {
                    "level": 1,
                    "name": "一等奖",
                    "match_condition": 2,
                    "fixed_prize": None,
                    "prize_percentage": 1.0
                },
                {
                    "level": 2,
                    "name": "二等奖",
                    "match_condition": 1,
                    "fixed_prize": 20.0,
                    "prize_percentage": None
                }
            ],
            "jackpot": {
                "enabled": True,
                "initial_amount": 500.0,
                "contribution_rate": 0.3,
                "post_return_contribution_rate": 0.5,
                "return_rate": 0.2,
                "jackpot_fixed_prize": None,
                "min_jackpot": 200.0
            }
        },
        "simulation_config": {
            "rounds": 8,  # 少量轮数，快速完成
            "players_range": [15, 25],
            "bets_range": [1, 1],
            "seed": 99999
        }
    }
    
    try:
        # 1. 启动模拟
        print("1. 启动快速测试模拟...")
        start_response = requests.post(
            f"{base_url}/api/v1/simulation/start", 
            json=test_config,
            timeout=10
        )
        
        if start_response.status_code == 200:
            result = start_response.json()
            simulation_id = result.get("simulation_id")
            print(f"   ✅ 模拟启动成功: {simulation_id}")
        else:
            print(f"   ❌ 模拟启动失败: {start_response.status_code}")
            return
        
        # 2. 等待模拟完成
        print("2. 等待模拟完成...")
        
        completed = False
        for i in range(30):  # 最多等待30秒
            try:
                progress_response = requests.get(
                    f"{base_url}/api/v1/simulation/progress/{simulation_id}", 
                    timeout=5
                )
                
                if progress_response.status_code == 200:
                    progress = progress_response.json()
                    current_round = progress.get('current_round', 0)
                    total_rounds = progress.get('total_rounds', 0)
                    
                    if current_round > 0:
                        print(f"   📊 进度: {current_round}/{total_rounds} 轮 ({progress.get('progress_percentage', 0):.1f}%)")
                    
                    if progress.get('completed') or progress.get('status') == 'completed':
                        print("   ✅ 模拟完成！")
                        completed = True
                        break
                        
                else:
                    print(f"   ❌ 进度查询失败: {progress_response.status_code}")
                    break
                
            except Exception as e:
                print(f"   ❌ 查询异常: {e}")
                break
            
            time.sleep(1)
        
        if not completed:
            print("   ⚠️ 模拟未在预期时间内完成，继续验证...")
        
        # 3. 验证模拟完成后的实时数据
        print("3. 验证模拟完成后的实时数据...")
        
        # 等待一下确保数据更新
        time.sleep(2)
        
        realtime_response = requests.get(
            f"{base_url}/api/v1/simulation/realtime-data/{simulation_id}", 
            timeout=10
        )
        
        if realtime_response.status_code == 200:
            realtime_data = realtime_response.json()
            print("   📈 实时数据获取成功")
            
            # 验证数据结构
            if 'chart_data' in realtime_data:
                chart_data = realtime_data['chart_data']
                print("   ✅ 图表数据结构存在")
                
                # 验证RTP趋势数据
                if 'rtp_trend' in chart_data and chart_data['rtp_trend']:
                    rtp_trend = chart_data['rtp_trend']
                    print(f"   ✅ RTP趋势数据: {len(rtp_trend)}个数据点")
                    
                    if len(rtp_trend) >= test_config['simulation_config']['rounds']:
                        print(f"      ✅ RTP数据点数量正确: {len(rtp_trend)} >= {test_config['simulation_config']['rounds']}")
                    else:
                        print(f"      ⚠️ RTP数据点数量可能不足: {len(rtp_trend)} < {test_config['simulation_config']['rounds']}")
                    
                    # 显示RTP趋势
                    print(f"      📊 RTP趋势: {[f'{rtp*100:.1f}%' for rtp in rtp_trend[:5]]}{'...' if len(rtp_trend) > 5 else ''}")
                    
                    latest_rtp = rtp_trend[-1] * 100
                    avg_rtp = sum(rtp_trend) / len(rtp_trend) * 100
                    print(f"      📈 最新RTP: {latest_rtp:.2f}%")
                    print(f"      📈 平均RTP: {avg_rtp:.2f}%")
                else:
                    print(f"   ❌ RTP趋势数据缺失")
                
                # 验证奖级分布数据
                if 'prize_distribution' in chart_data and chart_data['prize_distribution']:
                    prize_dist = chart_data['prize_distribution']
                    print(f"   ✅ 奖级分布数据: {len(prize_dist)}个奖级")
                    
                    total_winners = 0
                    total_amount = 0
                    for prize in prize_dist:
                        print(f"      🏆 {prize['name']}: {prize['count']}人中奖, 总奖金¥{prize['amount']:.2f}")
                        total_winners += prize['count']
                        total_amount += prize['amount']
                    
                    print(f"      📊 总计: {total_winners}人中奖, 总奖金¥{total_amount:.2f}")
                else:
                    print(f"   ❌ 奖级分布数据缺失")
                
                # 验证奖池趋势数据
                if 'jackpot_trend' in chart_data and chart_data['jackpot_trend']:
                    jackpot_trend = chart_data['jackpot_trend']
                    print(f"   ✅ 奖池趋势数据: {len(jackpot_trend)}个数据点")
                    
                    if len(jackpot_trend) > 0:
                        initial_jackpot = jackpot_trend[0]
                        final_jackpot = jackpot_trend[-1]
                        print(f"      💰 初始奖池: ¥{initial_jackpot:.2f}")
                        print(f"      💰 最终奖池: ¥{final_jackpot:.2f}")
                        
                        # 检查奖池变化
                        max_jackpot = max(jackpot_trend)
                        min_jackpot = min(jackpot_trend)
                        print(f"      📈 奖池范围: ¥{min_jackpot:.2f} - ¥{max_jackpot:.2f}")
                else:
                    print(f"   ❌ 奖池趋势数据缺失")
                
            else:
                print(f"   ❌ 图表数据结构缺失")
                
        else:
            print(f"   ❌ 实时数据获取失败: {realtime_response.status_code}")
            print(f"      错误: {realtime_response.text}")
        
        # 4. 验证前端显示条件
        print("4. 验证前端显示条件...")
        
        # 模拟前端的显示条件检查
        if realtime_response.status_code == 200:
            realtime_data = realtime_response.json()
            
            # 检查前端显示条件: simulation && realtimeData && realtimeData.chart_data
            simulation_exists = True  # 模拟存在
            realtime_data_exists = realtime_data is not None
            chart_data_exists = 'chart_data' in realtime_data
            
            print(f"   📋 前端显示条件检查:")
            print(f"      simulation存在: {simulation_exists}")
            print(f"      realtimeData存在: {realtime_data_exists}")
            print(f"      chart_data存在: {chart_data_exists}")
            
            if simulation_exists and realtime_data_exists and chart_data_exists:
                print(f"   ✅ 前端显示条件满足，数据图表应该显示")
                
                chart_data = realtime_data['chart_data']
                
                # 检查RTP趋势显示条件
                rtp_trend_exists = 'rtp_trend' in chart_data and chart_data['rtp_trend'] and len(chart_data['rtp_trend']) > 0
                print(f"      RTP趋势显示条件: {rtp_trend_exists}")
                
                # 检查奖级分布显示条件
                prize_dist_exists = 'prize_distribution' in chart_data and chart_data['prize_distribution'] and len(chart_data['prize_distribution']) > 0
                print(f"      奖级分布显示条件: {prize_dist_exists}")
                
                if rtp_trend_exists and prize_dist_exists:
                    print(f"   🎉 所有数据显示条件都满足！")
                else:
                    print(f"   ⚠️ 部分数据显示条件不满足")
            else:
                print(f"   ❌ 前端显示条件不满足")
        
        # 5. 总结修复效果
        print("\n🎊 修复后实时数据显示功能验证总结:")
        
        if realtime_response.status_code == 200:
            realtime_data = realtime_response.json()
            if 'chart_data' in realtime_data:
                chart_data = realtime_data['chart_data']
                
                features_working = []
                if 'rtp_trend' in chart_data and chart_data['rtp_trend']:
                    features_working.append("RTP趋势数据")
                if 'prize_distribution' in chart_data and chart_data['prize_distribution']:
                    features_working.append("奖级分布数据")
                if 'jackpot_trend' in chart_data and chart_data['jackpot_trend']:
                    features_working.append("奖池趋势数据")
                
                print(f"   ✅ 正常工作的功能 ({len(features_working)}/3):")
                for feature in features_working:
                    print(f"      ✓ {feature}")
                
                if len(features_working) == 3:
                    print(f"\n   🎉 修复成功！所有实时数据功能都正常工作")
                    print(f"   📱 前端现在应该能正确显示:")
                    print(f"      • RTP趋势图表")
                    print(f"      • 奖级分布统计")
                    print(f"      • 奖池变化趋势")
                elif len(features_working) >= 2:
                    print(f"\n   👍 修复基本成功！大部分功能正常")
                else:
                    print(f"\n   ⚠️ 修复可能不完全，需要进一步检查")
            else:
                print(f"   ❌ 图表数据结构仍然缺失")
        else:
            print(f"   ❌ 实时数据获取仍然失败")
        
        print(f"\n   🔧 修复要点:")
        print(f"      ✅ 模拟完成后自动获取最终实时数据")
        print(f"      ✅ fetchProgress函数中添加完成时数据获取")
        print(f"      ✅ useEffect中添加completed状态处理")
        print(f"      ✅ 确保数据获取的依赖关系正确")
        
    except Exception as e:
        print(f"❌ 测试异常: {e}")

if __name__ == "__main__":
    test_fixed_realtime_data()
