#!/usr/bin/env python3
"""
测试修复后的功能
"""

import requests
import json

def test_rtp_display_fix():
    """测试RTP显示修复"""
    base_url = "http://localhost:8001"
    
    print("🔧 测试RTP显示修复...")
    
    try:
        # 获取模拟列表
        response = requests.get(f"{base_url}/api/v1/simulation/list", timeout=5)
        if response.status_code == 200:
            simulations = response.json().get('simulations', [])
            if simulations:
                simulation_id = simulations[0]['simulation_id']
                print(f"   找到运行中的模拟: {simulation_id}")
                
                # 获取进度数据
                progress_response = requests.get(
                    f"{base_url}/api/v1/simulation/progress/{simulation_id}", 
                    timeout=5
                )
                
                if progress_response.status_code == 200:
                    progress = progress_response.json()
                    real_time_stats = progress.get('real_time_stats')
                    
                    if real_time_stats:
                        current_rtp = real_time_stats.get('current_rtp', 0)
                        print(f"   ✅ 原始RTP值: {current_rtp}")
                        print(f"   ✅ 前端应显示: {current_rtp * 100:.2f}%")
                        
                        # 验证RTP值在合理范围内
                        if 0.5 <= current_rtp <= 1.5:
                            print(f"   ✅ RTP值在合理范围内")
                        else:
                            print(f"   ⚠️ RTP值可能异常: {current_rtp}")
                    else:
                        print("   ❌ 没有实时统计数据")
                else:
                    print(f"   ❌ 进度查询失败: {progress_response.status_code}")
            else:
                print("   ❌ 没有运行中的模拟")
        else:
            print(f"   ❌ 获取模拟列表失败: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ 测试异常: {e}")

def test_config_edit_flow():
    """测试配置编辑流程"""
    base_url = "http://localhost:8001"
    
    print("\n📝 测试配置编辑流程...")
    
    try:
        # 1. 获取配置列表
        response = requests.get(f"{base_url}/api/v1/config/list", timeout=5)
        if response.status_code == 200:
            configs = response.json().get('configs', [])
            if configs:
                config_name = configs[0]['name']
                print(f"   找到配置: {config_name}")
                
                # 2. 加载配置（模拟点击"编辑"按钮）
                load_response = requests.get(f"{base_url}/api/v1/config/load/{config_name}", timeout=5)
                
                if load_response.status_code == 200:
                    config = load_response.json()['config']
                    print(f"   ✅ 配置加载成功")
                    print(f"   ✅ 游戏名称: {config.get('game_rules', {}).get('name', 'N/A')}")
                    print(f"   ✅ 模拟轮数: {config.get('simulation_config', {}).get('rounds', 'N/A')}")
                    print(f"   ✅ 前端应自动切换到编辑标签页")
                else:
                    print(f"   ❌ 配置加载失败: {load_response.status_code}")
            else:
                print("   ❌ 没有可用的配置")
        else:
            print(f"   ❌ 获取配置列表失败: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ 测试异常: {e}")

def test_realtime_data_completeness():
    """测试实时数据完整性"""
    base_url = "http://localhost:8001"
    
    print("\n📊 测试实时数据完整性...")
    
    try:
        # 获取模拟列表
        response = requests.get(f"{base_url}/api/v1/simulation/list", timeout=5)
        if response.status_code == 200:
            simulations = response.json().get('simulations', [])
            if simulations:
                simulation_id = simulations[0]['simulation_id']
                print(f"   测试模拟: {simulation_id}")
                
                # 测试进度API
                progress_response = requests.get(
                    f"{base_url}/api/v1/simulation/progress/{simulation_id}", 
                    timeout=5
                )
                
                if progress_response.status_code == 200:
                    progress = progress_response.json()
                    
                    # 检查必要字段
                    required_fields = ['simulation_id', 'status', 'current_round', 'total_rounds', 'progress_percentage']
                    missing_fields = [field for field in required_fields if field not in progress]
                    
                    if not missing_fields:
                        print("   ✅ 进度API数据完整")
                    else:
                        print(f"   ❌ 进度API缺少字段: {missing_fields}")
                    
                    # 检查实时统计
                    real_time_stats = progress.get('real_time_stats')
                    if real_time_stats:
                        stats_fields = ['current_rtp', 'current_jackpot', 'total_bet_amount', 'total_payout']
                        missing_stats = [field for field in stats_fields if field not in real_time_stats]
                        
                        if not missing_stats:
                            print("   ✅ 实时统计数据完整")
                        else:
                            print(f"   ❌ 实时统计缺少字段: {missing_stats}")
                    else:
                        print("   ❌ 没有实时统计数据")
                
                # 测试实时图表数据API
                chart_response = requests.get(
                    f"{base_url}/api/v1/simulation/realtime-data/{simulation_id}", 
                    timeout=5
                )
                
                if chart_response.status_code == 200:
                    chart_data = chart_response.json()
                    chart_info = chart_data.get('chart_data', {})
                    
                    if 'rtp_trend' in chart_info and 'prize_distribution' in chart_info:
                        print("   ✅ 图表数据API完整")
                        print(f"   📈 RTP趋势数据点: {len(chart_info.get('rtp_trend', []))}")
                        print(f"   🏆 奖级分布: {len(chart_info.get('prize_distribution', []))}个奖级")
                    else:
                        print("   ❌ 图表数据不完整")
                else:
                    print(f"   ❌ 图表数据API失败: {chart_response.status_code}")
                    
            else:
                print("   ❌ 没有运行中的模拟")
        else:
            print(f"   ❌ 获取模拟列表失败: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ 测试异常: {e}")

if __name__ == "__main__":
    print("🧪 开始测试修复后的功能...\n")
    
    test_rtp_display_fix()
    test_config_edit_flow()
    test_realtime_data_completeness()
    
    print("\n🎯 测试完成！")
    print("📱 请在浏览器中访问 http://localhost:3001 验证前端显示")
    print("   1. 检查RTP是否显示为百分比形式（如：80.25%）")
    print("   2. 在配置管理页面点击'编辑'按钮，确认自动切换到编辑标签页")
    print("   3. 在运行模拟页面查看实时数据统计和图表")
