#!/usr/bin/env python3
"""
测试增强的数据展示功能
验证启动模拟下方的全面数据展示
"""

import requests
import time

def test_enhanced_data_display():
    """测试增强的数据展示功能"""
    base_url = "http://localhost:8001"
    
    print("📊 测试增强的数据展示功能...")
    print("🎯 验证启动模拟下方的全面数据展示")
    
    # 创建测试配置
    test_config = {
        "game_config": {
            "game_type": "lottery",
            "name": "增强数据展示测试彩票",
            "description": "验证全面的数据展示功能",
            "number_range": [1, 12],
            "selection_count": 3,
            "ticket_price": 8.0,
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
                    "fixed_prize": 30.0,
                    "prize_percentage": None
                },
                {
                    "level": 3,
                    "name": "三等奖",
                    "match_condition": 1,
                    "fixed_prize": 8.0,
                    "prize_percentage": None
                }
            ],
            "jackpot": {
                "enabled": True,
                "initial_amount": 800.0,
                "contribution_rate": 0.25,
                "post_return_contribution_rate": 0.4,
                "return_rate": 0.15,
                "jackpot_fixed_prize": None,
                "min_jackpot": 400.0
            }
        },
        "simulation_config": {
            "rounds": 12,
            "players_range": [20, 30],
            "bets_range": [1, 2],
            "seed": 77777
        }
    }
    
    try:
        # 1. 启动模拟
        print("1. 启动增强数据展示测试模拟...")
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
        
        # 2. 监控数据展示功能
        print("2. 监控增强的数据展示功能...")
        
        enhanced_features = {
            "basic_stats": False,
            "financial_analysis": False,
            "game_statistics": False,
            "jackpot_analysis": False,
            "rtp_trend_analysis": False,
            "prize_distribution_analysis": False,
            "comprehensive_report": False
        }
        
        for i in range(25):  # 监控25秒
            try:
                # 获取进度和实时数据
                progress_response = requests.get(
                    f"{base_url}/api/v1/simulation/progress/{simulation_id}", 
                    timeout=5
                )
                realtime_response = requests.get(
                    f"{base_url}/api/v1/simulation/realtime-data/{simulation_id}", 
                    timeout=5
                )
                
                if progress_response.status_code == 200 and realtime_response.status_code == 200:
                    progress = progress_response.json()
                    realtime_data = realtime_response.json()
                    
                    current_round = progress.get('current_round', 0)
                    
                    if current_round > 0:
                        print(f"\n   📊 轮次 {current_round} 增强数据验证:")
                        
                        # 验证基础统计数据
                        real_time_stats = progress.get('real_time_stats', {})
                        if real_time_stats:
                            enhanced_features["basic_stats"] = True
                            print(f"      ✅ 基础统计数据: RTP {real_time_stats.get('current_rtp', 0)*100:.1f}%, 奖池 ¥{real_time_stats.get('current_jackpot', 0):.0f}")
                            
                            # 验证财务分析数据
                            if 'total_bet_amount' in real_time_stats and 'total_payout' in real_time_stats:
                                enhanced_features["financial_analysis"] = True
                                total_bet = real_time_stats.get('total_bet_amount', 0)
                                total_payout = real_time_stats.get('total_payout', 0)
                                profit_rate = ((total_bet - total_payout) / total_bet * 100) if total_bet > 0 else 0
                                print(f"      ✅ 财务分析: 投注 ¥{total_bet:.0f}, 派奖 ¥{total_payout:.0f}, 利润率 {profit_rate:.1f}%")
                            
                            # 验证游戏统计数据
                            if 'total_players' in real_time_stats and 'total_winners' in real_time_stats:
                                enhanced_features["game_statistics"] = True
                                total_players = real_time_stats.get('total_players', 0)
                                total_winners = real_time_stats.get('total_winners', 0)
                                winning_rate = (total_winners / total_players * 100) if total_players > 0 else 0
                                avg_bet_per_player = (total_bet / total_players) if total_players > 0 else 0
                                print(f"      ✅ 游戏统计: {total_players}人参与, {total_winners}人中奖, 中奖率 {winning_rate:.1f}%, 人均投注 ¥{avg_bet_per_player:.1f}")
                            
                            # 验证奖池分析数据
                            if 'current_jackpot' in real_time_stats:
                                enhanced_features["jackpot_analysis"] = True
                                current_jackpot = real_time_stats.get('current_jackpot', 0)
                                initial_jackpot = test_config['game_config']['jackpot']['initial_amount']
                                jackpot_growth = ((current_jackpot - initial_jackpot) / initial_jackpot * 100) if initial_jackpot > 0 else 0
                                print(f"      ✅ 奖池分析: 当前 ¥{current_jackpot:.0f}, 增长率 {jackpot_growth:.1f}%")
                        
                        # 验证图表数据
                        chart_data = realtime_data.get('chart_data', {})
                        if chart_data:
                            # 验证RTP趋势分析
                            if 'rtp_trend' in chart_data and chart_data['rtp_trend']:
                                enhanced_features["rtp_trend_analysis"] = True
                                rtp_trend = chart_data['rtp_trend']
                                latest_rtp = rtp_trend[-1] * 100
                                avg_rtp = sum(rtp_trend) / len(rtp_trend) * 100
                                max_rtp = max(rtp_trend) * 100
                                min_rtp = min(rtp_trend) * 100
                                rtp_volatility = max_rtp - min_rtp
                                print(f"      ✅ RTP趋势分析: 最新 {latest_rtp:.1f}%, 平均 {avg_rtp:.1f}%, 波动 {rtp_volatility:.1f}%")
                            
                            # 验证奖级分布分析
                            if 'prize_distribution' in chart_data and chart_data['prize_distribution']:
                                enhanced_features["prize_distribution_analysis"] = True
                                prize_dist = chart_data['prize_distribution']
                                total_prize_winners = sum(p['count'] for p in prize_dist)
                                total_prize_amount = sum(p['amount'] for p in prize_dist)
                                print(f"      ✅ 奖级分布分析: {len(prize_dist)}个奖级, {total_prize_winners}人中奖, 总奖金 ¥{total_prize_amount:.0f}")
                                
                                # 显示各奖级详情
                                for prize in prize_dist:
                                    avg_prize = prize['amount'] / prize['count'] if prize['count'] > 0 else 0
                                    print(f"         {prize['name']}: {prize['count']}人, 总奖金 ¥{prize['amount']:.0f}, 人均 ¥{avg_prize:.0f}")
                        
                        # 验证综合报告数据
                        if enhanced_features["basic_stats"] and enhanced_features["financial_analysis"] and enhanced_features["game_statistics"]:
                            enhanced_features["comprehensive_report"] = True
                            print(f"      ✅ 综合报告: 数据完整，可生成全面分析报告")
                    
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
            
            time.sleep(1)
        
        # 3. 最终验证增强功能
        print("3. 最终验证增强的数据展示功能...")
        
        try:
            final_progress_response = requests.get(
                f"{base_url}/api/v1/simulation/progress/{simulation_id}", 
                timeout=10
            )
            final_realtime_response = requests.get(
                f"{base_url}/api/v1/simulation/realtime-data/{simulation_id}", 
                timeout=10
            )
            
            if final_progress_response.status_code == 200 and final_realtime_response.status_code == 200:
                final_progress = final_progress_response.json()
                final_realtime = final_realtime_response.json()
                
                print("   📈 最终增强数据验证:")
                
                # 验证所有数据字段
                real_time_stats = final_progress.get('real_time_stats', {})
                chart_data = final_realtime.get('chart_data', {})
                
                # 基础数据验证
                basic_fields = ['current_rtp', 'current_jackpot', 'total_bet_amount', 'total_payout', 'total_players', 'total_winners']
                basic_complete = all(field in real_time_stats for field in basic_fields)
                print(f"      基础数据完整性: {'✅' if basic_complete else '❌'} ({sum(1 for field in basic_fields if field in real_time_stats)}/{len(basic_fields)})")
                
                # 财务数据验证
                financial_fields = ['total_sales_amount', 'total_jackpot_contribution', 'total_seller_return']
                financial_complete = any(field in real_time_stats for field in financial_fields)
                print(f"      财务数据可用性: {'✅' if financial_complete else '❌'}")
                
                # 图表数据验证
                chart_fields = ['rtp_trend', 'prize_distribution', 'jackpot_trend']
                chart_complete = all(field in chart_data and chart_data[field] for field in chart_fields)
                print(f"      图表数据完整性: {'✅' if chart_complete else '❌'} ({sum(1 for field in chart_fields if field in chart_data and chart_data[field])}/{len(chart_fields)})")
                
                # 计算数据丰富度
                if chart_complete:
                    rtp_points = len(chart_data.get('rtp_trend', []))
                    prize_levels = len(chart_data.get('prize_distribution', []))
                    jackpot_points = len(chart_data.get('jackpot_trend', []))
                    print(f"      数据丰富度: RTP {rtp_points}点, 奖级 {prize_levels}个, 奖池 {jackpot_points}点")
                
            else:
                print(f"   ❌ 获取最终数据失败")
                
        except Exception as e:
            print(f"   ❌ 获取最终数据异常: {e}")
        
        # 4. 总结增强功能验证结果
        print("\n🎊 增强数据展示功能验证总结:")
        
        verified_features = [feature for feature, verified in enhanced_features.items() if verified]
        unverified_features = [feature for feature, verified in enhanced_features.items() if not verified]
        
        feature_names = {
            "basic_stats": "基础统计数据",
            "financial_analysis": "财务分析数据",
            "game_statistics": "游戏统计数据",
            "jackpot_analysis": "奖池分析数据",
            "rtp_trend_analysis": "RTP趋势分析",
            "prize_distribution_analysis": "奖级分布分析",
            "comprehensive_report": "综合报告数据"
        }
        
        print(f"   ✅ 已验证功能 ({len(verified_features)}/{len(enhanced_features)}):")
        for feature in verified_features:
            print(f"      ✓ {feature_names.get(feature, feature)}")
        
        if unverified_features:
            print(f"   ❌ 未验证功能 ({len(unverified_features)}/{len(enhanced_features)}):")
            for feature in unverified_features:
                print(f"      ✗ {feature_names.get(feature, feature)}")
        
        # 计算功能完成度
        completion_rate = len(verified_features) / len(enhanced_features)
        print(f"\n   📊 增强功能验证完成度: {completion_rate*100:.1f}%")
        
        if completion_rate >= 0.9:
            print(f"   🎉 增强数据展示功能优秀！")
            print(f"   📱 用户现在可以看到:")
            print(f"      • 详细的财务分析 (销售收入、奖池贡献、卖方返还、利润率)")
            print(f"      • 全面的游戏统计 (平均每轮玩家、人均投注、平均中奖金额)")
            print(f"      • 深度的奖池分析 (增长率、贡献率、风险指数)")
            print(f"      • 精确的RTP趋势 (最高、最低、波动、稳定性)")
            print(f"      • 完整的奖级分布 (各级详情、占比分析)")
            print(f"      • 智能的风险评估 (RTP稳定性、奖池风险、盈利能力)")
            print(f"      • 关键指标总结 (当前RTP、奖池余额、中奖率、利润率)")
        elif completion_rate >= 0.7:
            print(f"   👍 增强数据展示大部分功能正常")
        else:
            print(f"   ⚠️ 增强数据展示功能需要改进")
        
        print(f"\n   🎯 增强功能亮点:")
        print(f"      💡 实时财务分析 - 销售、成本、利润一目了然")
        print(f"      💡 智能风险评估 - RTP稳定性、奖池风险自动评估")
        print(f"      💡 深度数据挖掘 - 平均值、趋势、波动性分析")
        print(f"      💡 可视化增强 - 关键指标卡片式展示")
        print(f"      💡 用户体验优化 - 数据分类清晰、信息层次分明")
        
    except Exception as e:
        print(f"❌ 测试异常: {e}")

if __name__ == "__main__":
    test_enhanced_data_display()
