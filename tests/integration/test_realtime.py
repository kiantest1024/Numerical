#!/usr/bin/env python3
"""
测试实时数据功能
"""

import requests
import json
import time

def test_realtime_simulation():
    base_url = "http://localhost:8001"
    
    print("🚀 测试实时模拟数据功能...")
    
    try:
        # 1. 获取配置列表
        print("1. 获取配置列表...")
        response = requests.get(f"{base_url}/api/v1/config/list", timeout=5)
        if response.status_code != 200:
            print(f"   ❌ 获取配置失败: {response.status_code}")
            return
            
        configs = response.json().get('configs', [])
        if not configs:
            print("   ❌ 没有可用的配置")
            return
            
        config_name = configs[0]['name']
        print(f"   ✅ 使用配置: {config_name}")
        
        # 2. 加载配置
        print("2. 加载配置...")
        response = requests.get(f"{base_url}/api/v1/config/load/{config_name}", timeout=5)
        if response.status_code != 200:
            print(f"   ❌ 加载配置失败: {response.status_code}")
            return
            
        config = response.json()['config']
        print("   ✅ 配置加载成功")
        
        # 3. 启动模拟
        print("3. 启动模拟...")
        simulation_request = {
            "game_config": config["game_rules"],
            "simulation_config": config["simulation_config"]
        }
        
        response = requests.post(f"{base_url}/api/v1/simulation/start", 
                               json=simulation_request, timeout=10)
        
        if response.status_code != 200:
            print(f"   ❌ 模拟启动失败: {response.status_code}")
            return
            
        result = response.json()
        simulation_id = result.get("simulation_id")
        print(f"   ✅ 模拟启动成功: {simulation_id}")
        
        # 4. 测试实时数据功能
        print("4. 测试实时数据功能...")
        for i in range(10):  # 测试10次
            try:
                # 测试进度API（包含实时统计）
                progress_response = requests.get(
                    f"{base_url}/api/v1/simulation/progress/{simulation_id}", 
                    timeout=5
                )
                
                if progress_response.status_code == 200:
                    progress = progress_response.json()
                    print(f"   📊 进度: {progress.get('progress_percentage', 0):.1f}% "
                          f"(轮次: {progress.get('current_round', 0)}/{progress.get('total_rounds', 0)})")
                    
                    # 显示实时统计
                    real_time_stats = progress.get('real_time_stats')
                    if real_time_stats:
                        print(f"      💰 当前RTP: {real_time_stats.get('current_rtp', 0):.4f}")
                        print(f"      🎰 奖池金额: {real_time_stats.get('current_jackpot', 0):.2f}")
                        print(f"      🎯 已完成轮次: {real_time_stats.get('completed_rounds', 0)}")
                        
                        # 显示奖级统计
                        prize_stats = real_time_stats.get('prize_stats', {})
                        if prize_stats:
                            print("      🏆 奖级统计:")
                            for level, stats in prize_stats.items():
                                if stats['winners_count'] > 0:
                                    print(f"         {stats['name']}: {stats['winners_count']}人中奖, "
                                          f"总奖金: {stats['total_amount']:.2f}")
                
                # 测试实时图表数据API
                chart_response = requests.get(
                    f"{base_url}/api/v1/simulation/realtime-data/{simulation_id}", 
                    timeout=5
                )
                
                if chart_response.status_code == 200:
                    chart_data = chart_response.json()
                    chart_info = chart_data.get('chart_data', {})
                    
                    rtp_trend = chart_info.get('rtp_trend', [])
                    if rtp_trend:
                        print(f"      📈 RTP趋势: 最新RTP={rtp_trend[-1]:.4f}, "
                              f"数据点数={len(rtp_trend)}")
                    
                    prize_dist = chart_info.get('prize_distribution', [])
                    if prize_dist:
                        print(f"      🎲 奖级分布: {len(prize_dist)}个奖级有中奖")
                
                else:
                    print(f"   ❌ 图表数据查询失败: {chart_response.status_code}")
                
            except Exception as e:
                print(f"   ❌ 查询异常: {e}")
            
            print("   " + "-" * 50)
            time.sleep(2)  # 等待2秒再查询
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")

if __name__ == "__main__":
    test_realtime_simulation()
