#!/usr/bin/env python3
"""
测试实时数据显示功能
验证RTP趋势和奖级分布数据是否正确获取和显示
"""

import requests
import time
import json

def test_realtime_data_display():
    """测试实时数据显示功能"""
    base_url = "http://localhost:8001"
    
    print("📊 测试实时数据显示功能...")
    print("🎯 验证RTP趋势和奖级分布数据统计")
    
    # 创建测试配置，确保有足够的数据用于图表显示
    test_config = {
        "game_config": {
            "game_type": "lottery",
            "name": "实时数据显示测试彩票",
            "description": "验证RTP趋势和奖级分布数据显示",
            "number_range": [1, 15],  # 小范围，容易中奖
            "selection_count": 3,     # 选择3个数字
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
                },
                {
                    "level": 3,
                    "name": "三等奖",
                    "match_condition": 1,
                    "fixed_prize": 10.0,
                    "prize_percentage": None
                }
            ],
            "jackpot": {
                "enabled": True,
                "initial_amount": 1000.0,
                "contribution_rate": 0.3,
                "post_return_contribution_rate": 0.5,
                "return_rate": 0.2,
                "jackpot_fixed_prize": None,
                "min_jackpot": 500.0
            }
        },
        "simulation_config": {
            "rounds": 20,  # 足够的轮数生成图表数据
            "players_range": [30, 50],
            "bets_range": [1, 2],
            "seed": 88888
        }
    }
    
    try:
        # 1. 启动模拟
        print("1. 启动模拟...")
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
            print(f"      错误: {start_response.text}")
            return
        
        # 2. 监控实时数据获取
        print("2. 监控实时数据获取...")
        
        realtime_data_checks = {
            "rtp_trend_data": False,
            "prize_distribution_data": False,
            "jackpot_trend_data": False,
            "chart_data_structure": False
        }
        
        max_checks = 30  # 最多检查30次
        for i in range(max_checks):
            try:
                # 获取进度数据
                progress_response = requests.get(
                    f"{base_url}/api/v1/simulation/progress/{simulation_id}", 
                    timeout=5
                )
                
                # 获取实时数据
                realtime_response = requests.get(
                    f"{base_url}/api/v1/simulation/realtime-data/{simulation_id}", 
                    timeout=5
                )
                
                if progress_response.status_code == 200 and realtime_response.status_code == 200:
                    progress = progress_response.json()
                    realtime_data = realtime_response.json()
                    
                    current_round = progress.get('current_round', 0)
                    
                    if current_round > 0:
                        print(f"\n   📊 轮次 {current_round} 实时数据检查:")
                        
                        # 检查实时数据结构
                        if 'chart_data' in realtime_data:
                            realtime_data_checks["chart_data_structure"] = True
                            chart_data = realtime_data['chart_data']
                            print(f"      ✅ 图表数据结构存在")
                            
                            # 检查RTP趋势数据
                            if 'rtp_trend' in chart_data and chart_data['rtp_trend']:
                                realtime_data_checks["rtp_trend_data"] = True
                                rtp_trend = chart_data['rtp_trend']
                                print(f"      ✅ RTP趋势数据: {len(rtp_trend)}个数据点")
                                if len(rtp_trend) > 0:
                                    latest_rtp = rtp_trend[-1] * 100
                                    avg_rtp = sum(rtp_trend) / len(rtp_trend) * 100
                                    print(f"         最新RTP: {latest_rtp:.2f}%")
                                    print(f"         平均RTP: {avg_rtp:.2f}%")
                            else:
                                print(f"      ❌ RTP趋势数据缺失或为空")
                            
                            # 检查奖级分布数据
                            if 'prize_distribution' in chart_data and chart_data['prize_distribution']:
                                realtime_data_checks["prize_distribution_data"] = True
                                prize_dist = chart_data['prize_distribution']
                                print(f"      ✅ 奖级分布数据: {len(prize_dist)}个奖级")
                                for prize in prize_dist:
                                    print(f"         {prize['name']}: {prize['count']}人中奖, 总奖金¥{prize['amount']:.2f}")
                            else:
                                print(f"      ❌ 奖级分布数据缺失或为空")
                            
                            # 检查奖池趋势数据
                            if 'jackpot_trend' in chart_data and chart_data['jackpot_trend']:
                                realtime_data_checks["jackpot_trend_data"] = True
                                jackpot_trend = chart_data['jackpot_trend']
                                print(f"      ✅ 奖池趋势数据: {len(jackpot_trend)}个数据点")
                                if len(jackpot_trend) > 0:
                                    latest_jackpot = jackpot_trend[-1]
                                    print(f"         当前奖池: ¥{latest_jackpot:.2f}")
                            else:
                                print(f"      ❌ 奖池趋势数据缺失或为空")
                        else:
                            print(f"      ❌ 图表数据结构缺失")
                        
                        # 检查进度数据中的RTP趋势
                        real_time_stats = progress.get('real_time_stats', {})
                        if 'recent_rtps' in real_time_stats and real_time_stats['recent_rtps']:
                            recent_rtps = real_time_stats['recent_rtps']
                            print(f"      ✅ 进度数据中的最近RTP: {len(recent_rtps)}个数据点")
                            print(f"         最近RTP值: {[f'{rtp*100:.1f}%' for rtp in recent_rtps[-5:]]}")
                        else:
                            print(f"      ❌ 进度数据中的最近RTP缺失")
                    
                    # 检查是否完成
                    if progress.get('completed') or progress.get('status') == 'completed':
                        print("\n   ✅ 模拟完成！")
                        break
                        
                else:
                    print(f"   ❌ 数据获取失败: 进度{progress_response.status_code}, 实时{realtime_response.status_code}")
                    break
                
            except Exception as e:
                print(f"   ❌ 查询异常: {e}")
                break
            
            time.sleep(1)  # 每秒查询一次
        
        # 3. 最终验证完成后的数据
        print("3. 最终验证完成后的数据...")
        try:
            final_realtime_response = requests.get(
                f"{base_url}/api/v1/simulation/realtime-data/{simulation_id}", 
                timeout=10
            )
            
            if final_realtime_response.status_code == 200:
                final_data = final_realtime_response.json()
                print("   📈 最终实时数据验证:")
                
                if 'chart_data' in final_data:
                    chart_data = final_data['chart_data']
                    
                    # 验证最终RTP趋势数据
                    if 'rtp_trend' in chart_data and chart_data['rtp_trend']:
                        rtp_count = len(chart_data['rtp_trend'])
                        print(f"      ✅ 最终RTP趋势数据: {rtp_count}个数据点")
                        if rtp_count >= test_config['simulation_config']['rounds']:
                            print(f"      ✅ RTP数据点数量符合预期 ({rtp_count} >= {test_config['simulation_config']['rounds']})")
                        else:
                            print(f"      ⚠️ RTP数据点数量可能不足 ({rtp_count} < {test_config['simulation_config']['rounds']})")
                    
                    # 验证最终奖级分布数据
                    if 'prize_distribution' in chart_data and chart_data['prize_distribution']:
                        prize_count = len(chart_data['prize_distribution'])
                        print(f"      ✅ 最终奖级分布数据: {prize_count}个奖级")
                        total_winners = sum(prize['count'] for prize in chart_data['prize_distribution'])
                        total_amount = sum(prize['amount'] for prize in chart_data['prize_distribution'])
                        print(f"      📊 总中奖人数: {total_winners}, 总奖金: ¥{total_amount:.2f}")
                    
                    # 验证最终奖池趋势数据
                    if 'jackpot_trend' in chart_data and chart_data['jackpot_trend']:
                        jackpot_count = len(chart_data['jackpot_trend'])
                        print(f"      ✅ 最终奖池趋势数据: {jackpot_count}个数据点")
                
            else:
                print(f"   ❌ 获取最终数据失败: {final_realtime_response.status_code}")
                
        except Exception as e:
            print(f"   ❌ 获取最终数据异常: {e}")
        
        # 4. 总结验证结果
        print("\n🎊 实时数据显示功能验证总结:")
        
        verified_features = [feature for feature, verified in realtime_data_checks.items() if verified]
        unverified_features = [feature for feature, verified in realtime_data_checks.items() if not verified]
        
        print(f"   ✅ 已验证功能 ({len(verified_features)}/{len(realtime_data_checks)}):")
        for feature in verified_features:
            feature_name = {
                "rtp_trend_data": "RTP趋势数据",
                "prize_distribution_data": "奖级分布数据", 
                "jackpot_trend_data": "奖池趋势数据",
                "chart_data_structure": "图表数据结构"
            }.get(feature, feature)
            print(f"      ✓ {feature_name}")
        
        if unverified_features:
            print(f"   ❌ 未验证功能 ({len(unverified_features)}/{len(realtime_data_checks)}):")
            for feature in unverified_features:
                feature_name = {
                    "rtp_trend_data": "RTP趋势数据",
                    "prize_distribution_data": "奖级分布数据", 
                    "jackpot_trend_data": "奖池趋势数据",
                    "chart_data_structure": "图表数据结构"
                }.get(feature, feature)
                print(f"      ✗ {feature_name}")
        
        # 计算验证完成度
        verification_rate = len(verified_features) / len(realtime_data_checks)
        print(f"\n   📊 实时数据功能验证完成度: {verification_rate*100:.1f}%")
        
        if verification_rate >= 0.9:
            print(f"   🎉 实时数据显示功能基本正常！")
        elif verification_rate >= 0.7:
            print(f"   👍 实时数据显示大部分功能正常")
        else:
            print(f"   ⚠️ 实时数据显示功能可能存在问题")
        
        print(f"\n   📋 前端显示建议:")
        print(f"      💡 确保前端正确处理chart_data字段")
        print(f"      💡 检查realtimeData状态更新逻辑")
        print(f"      💡 验证图表组件的数据绑定")
        print(f"      💡 确认实时数据获取间隔设置")
        
    except Exception as e:
        print(f"❌ 测试异常: {e}")

if __name__ == "__main__":
    test_realtime_data_display()
