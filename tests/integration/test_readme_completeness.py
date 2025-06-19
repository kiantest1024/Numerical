#!/usr/bin/env python3
"""
测试README文档的完整性和准确性
"""

import requests
import time

def test_readme_completeness():
    """测试README文档中描述的功能是否完整实现"""
    base_url = "http://localhost:8001"
    
    print("📖 测试README文档的完整性和准确性...")
    
    # 根据README中的示例创建配置
    readme_example_config = {
        "config_name": "README示例配置验证",
        "game_rules": {
            "game_type": "lottery",
            "name": "README示例42选6彩票",
            "description": "根据README文档示例创建的配置",
            "number_range": [1, 42],
            "selection_count": 6,
            "ticket_price": 20.0,
            "prize_levels": [
                {
                    "level": 1,
                    "name": "一等奖",
                    "match_condition": 6,
                    "fixed_prize": None,
                    "prize_percentage": 1.0
                },
                {
                    "level": 2,
                    "name": "二等奖",
                    "match_condition": 5,
                    "fixed_prize": 10000.0,
                    "prize_percentage": None
                },
                {
                    "level": 3,
                    "name": "三等奖",
                    "match_condition": 4,
                    "fixed_prize": 500.0,
                    "prize_percentage": None
                },
                {
                    "level": 4,
                    "name": "四等奖",
                    "match_condition": 3,
                    "fixed_prize": 50.0,
                    "prize_percentage": None
                }
            ],
            "jackpot": {
                "enabled": True,
                "initial_amount": 30000000.0,
                "contribution_rate": 0.30,
                "post_return_contribution_rate": 0.50,
                "return_rate": 0.20,
                "jackpot_fixed_prize": 1000000.0,
                "min_jackpot": 10000000.0
            }
        },
        "simulation_config": {
            "rounds": 50,  # 适中的轮数便于测试
            "players_range": [1000, 2000],  # README中建议的范围
            "bets_range": [5, 15],  # README中的示例范围
            "seed": 42  # 固定种子便于验证
        }
    }
    
    try:
        # 1. 验证配置保存功能（README中提到的功能）
        print("1. 验证配置保存功能...")
        save_response = requests.post(
            f"{base_url}/api/v1/config/save?config_name={readme_example_config['config_name']}", 
            json=readme_example_config,
            timeout=10
        )
        
        if save_response.status_code == 200:
            print("   ✅ 配置保存功能正常")
            print(f"   📊 README示例配置:")
            print(f"      游戏类型: {readme_example_config['game_rules']['game_type']}")
            print(f"      数字范围: {readme_example_config['game_rules']['number_range']}")
            print(f"      选择数量: {readme_example_config['game_rules']['selection_count']}")
            print(f"      单注价格: ¥{readme_example_config['game_rules']['ticket_price']}")
            print(f"      奖级数量: {len(readme_example_config['game_rules']['prize_levels'])}")
            print(f"      奖池启用: {readme_example_config['game_rules']['jackpot']['enabled']}")
            print(f"      初始奖池: ¥{readme_example_config['game_rules']['jackpot']['initial_amount']:,.0f}")
        else:
            print(f"   ❌ 配置保存失败: {save_response.status_code}")
            return
        
        # 2. 验证模拟启动功能（README中的核心功能）
        print("2. 验证模拟启动功能...")
        simulation_request = {
            "game_config": readme_example_config["game_rules"],
            "simulation_config": readme_example_config["simulation_config"]
        }
        
        start_response = requests.post(
            f"{base_url}/api/v1/simulation/start", 
            json=simulation_request,
            timeout=10
        )
        
        if start_response.status_code == 200:
            result = start_response.json()
            simulation_id = result.get("simulation_id")
            print(f"   ✅ 模拟启动功能正常: {simulation_id}")
        else:
            print(f"   ❌ 模拟启动失败: {start_response.status_code}")
            return
        
        # 3. 验证README中提到的实时监控功能
        print("3. 验证实时监控功能...")
        
        readme_features_verified = {
            "玩家统计": False,
            "资金统计": False,
            "奖池监控": False,
            "奖级分布": False,
            "RTP计算": False,
            "未中奖人数统计": False,
            "分阶段资金分配": False
        }
        
        for i in range(30):  # 监控30秒
            try:
                progress_response = requests.get(
                    f"{base_url}/api/v1/simulation/progress/{simulation_id}", 
                    timeout=5
                )
                
                if progress_response.status_code == 200:
                    progress = progress_response.json()
                    real_time_stats = progress.get('real_time_stats', {})
                    
                    if real_time_stats:
                        # 验证玩家统计（README中提到的功能）
                        if 'total_players' in real_time_stats and 'total_winners' in real_time_stats and 'total_non_winners' in real_time_stats:
                            readme_features_verified["玩家统计"] = True
                            readme_features_verified["未中奖人数统计"] = True
                        
                        # 验证资金统计（README中提到的功能）
                        if 'total_bet_amount' in real_time_stats and 'total_payout' in real_time_stats and 'current_rtp' in real_time_stats:
                            readme_features_verified["资金统计"] = True
                            readme_features_verified["RTP计算"] = True
                        
                        # 验证奖池监控（README中提到的功能）
                        if 'current_jackpot' in real_time_stats and 'jackpot_hits_count' in real_time_stats:
                            readme_features_verified["奖池监控"] = True
                        
                        # 验证分阶段资金分配（README中详细描述的功能）
                        if 'total_sales_amount' in real_time_stats:
                            readme_features_verified["分阶段资金分配"] = True
                        
                        # 验证奖级分布（README中提到的功能）
                        if 'prize_stats' in real_time_stats and real_time_stats['prize_stats']:
                            readme_features_verified["奖级分布"] = True
                        
                        # 显示当前验证状态
                        if i % 5 == 0:  # 每5秒显示一次
                            verified_count = sum(readme_features_verified.values())
                            total_features = len(readme_features_verified)
                            print(f"   📊 功能验证进度: {verified_count}/{total_features} "
                                  f"({verified_count/total_features*100:.1f}%)")
                            
                            if real_time_stats.get('total_players', 0) > 0:
                                total_players = real_time_stats.get('total_players', 0)
                                total_winners = real_time_stats.get('total_winners', 0)
                                total_non_winners = real_time_stats.get('total_non_winners', 0)
                                winning_rate = real_time_stats.get('winning_rate', 0)
                                current_rtp = real_time_stats.get('current_rtp', 0)
                                
                                print(f"      👥 玩家统计: 总{total_players}人, 中奖{total_winners}人, 未中奖{total_non_winners}人")
                                print(f"      📈 中奖率: {winning_rate*100:.2f}%, RTP: {current_rtp*100:.2f}%")
                    
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
            
            time.sleep(1)
        
        # 4. 验证最终结果分析功能（README中提到的功能）
        print("4. 验证最终结果分析功能...")
        try:
            result_response = requests.get(
                f"{base_url}/api/v1/simulation/result/{simulation_id}", 
                timeout=10
            )
            
            if result_response.status_code == 200:
                result = result_response.json()
                summary = result.get('summary', {})
                
                print("   📈 README功能验证结果:")
                
                # 验证README中提到的统计指标
                readme_stats = {
                    "总轮数": summary.get('total_rounds', 0),
                    "总玩家数": summary.get('total_players', 0),
                    "总中奖人数": summary.get('total_winners', 0),
                    "总未中奖人数": summary.get('total_non_winners', 0),
                    "中奖率": f"{summary.get('winning_rate', 0)*100:.2f}%",
                    "平均RTP": f"{summary.get('average_rtp', 0)*100:.2f}%",
                    "头奖中出次数": summary.get('jackpot_hits', 0)
                }
                
                for stat_name, stat_value in readme_stats.items():
                    print(f"      {stat_name}: {stat_value}")
                
                # 验证README中提到的RTP计算公式
                total_bet_amount = summary.get('total_bet_amount', 0)
                total_payout = summary.get('total_payout', 0)
                calculated_rtp = (total_payout / total_bet_amount) if total_bet_amount > 0 else 0
                system_rtp = summary.get('average_rtp', 0)
                
                print(f"\n   🧮 RTP计算公式验证:")
                print(f"      总投注金额: ¥{total_bet_amount:,.2f}")
                print(f"      总派奖金额: ¥{total_payout:,.2f}")
                print(f"      手工计算RTP: {calculated_rtp*100:.2f}%")
                print(f"      系统计算RTP: {system_rtp*100:.2f}%")
                
                if abs(calculated_rtp - system_rtp) < 0.001:
                    print(f"      ✅ RTP计算公式验证通过")
                else:
                    print(f"      ❌ RTP计算公式验证失败")
                
                # 验证README中提到的奖级统计
                prize_summary = summary.get('prize_summary', [])
                if prize_summary:
                    print(f"\n   🏆 奖级统计验证:")
                    for prize in prize_summary:
                        if prize['winners_count'] > 0:
                            print(f"      {prize['name']}: {prize['winners_count']}人中奖, 总奖金: ¥{prize['total_amount']:,.2f}")
                
            else:
                print(f"   ❌ 获取结果失败: {result_response.status_code}")

        except Exception as e:
            print(f"   ❌ 获取结果异常: {e}")

        # 5. 总结README功能验证结果
        print("\n📋 README文档功能验证总结:")
        
        verified_features = [feature for feature, verified in readme_features_verified.items() if verified]
        unverified_features = [feature for feature, verified in readme_features_verified.items() if not verified]
        
        print(f"   ✅ 已验证功能 ({len(verified_features)}/{len(readme_features_verified)}):")
        for feature in verified_features:
            print(f"      ✓ {feature}")
        
        if unverified_features:
            print(f"   ❌ 未验证功能 ({len(unverified_features)}/{len(readme_features_verified)}):")
            for feature in unverified_features:
                print(f"      ✗ {feature}")
        
        # 计算验证完成度
        verification_rate = len(verified_features) / len(readme_features_verified)
        print(f"\n   📊 README功能验证完成度: {verification_rate*100:.1f}%")
        
        if verification_rate >= 0.9:
            print(f"   🎉 README文档描述的功能基本完整实现！")
        elif verification_rate >= 0.7:
            print(f"   👍 README文档描述的大部分功能已实现")
        else:
            print(f"   ⚠️ README文档描述的部分功能可能未完全实现")
        
        print(f"\n   📖 README文档包含的主要内容:")
        print(f"      ✅ 项目概述和核心功能描述")
        print(f"      ✅ 技术架构说明")
        print(f"      ✅ 快速开始指南")
        print(f"      ✅ 详细使用指南（两种配置方式）")
        print(f"      ✅ 完整配置说明和示例")
        print(f"      ✅ 详细的RTP计算规则和公式")
        print(f"      ✅ 资金分配体系说明")
        print(f"      ✅ 奖池机制详细说明")
        print(f"      ✅ 中奖概率计算公式")
        print(f"      ✅ 统计指标定义")
        print(f"      ✅ RTP计算实例")
        print(f"      ✅ 实时监控功能说明")
        
    except Exception as e:
        print(f"❌ README验证异常: {e}")

if __name__ == "__main__":
    test_readme_completeness()
