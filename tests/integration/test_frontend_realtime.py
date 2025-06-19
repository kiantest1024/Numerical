#!/usr/bin/env python3
"""
测试前端实时数据功能
"""

import requests
import json
import time

def test_frontend_realtime():
    base_url = "http://localhost:8001"
    
    print("🚀 启动模拟并测试前端实时数据...")
    
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
        print(f"   🌐 前端可以访问: http://localhost:3001")
        print(f"   📊 在'运行模拟'页面应该能看到实时数据")
        
        # 4. 持续监控，让用户有时间查看前端
        print("\n4. 持续监控模拟状态 (按Ctrl+C停止)...")
        try:
            while True:
                # 获取进度
                progress_response = requests.get(
                    f"{base_url}/api/v1/simulation/progress/{simulation_id}", 
                    timeout=5
                )
                
                if progress_response.status_code == 200:
                    progress = progress_response.json()
                    print(f"   📊 进度: {progress.get('progress_percentage', 0):.1f}% "
                          f"(轮次: {progress.get('current_round', 0)}/{progress.get('total_rounds', 0)})")
                    
                    # 检查是否完成
                    if progress.get('completed') or progress.get('status') == 'completed':
                        print("   ✅ 模拟已完成！")
                        break
                        
                    # 显示实时统计
                    real_time_stats = progress.get('real_time_stats')
                    if real_time_stats:
                        print(f"      💰 当前RTP: {real_time_stats.get('current_rtp', 0):.4f}")
                        print(f"      🎰 奖池: ¥{real_time_stats.get('current_jackpot', 0):,.2f}")
                        
                        # 显示奖级统计
                        prize_stats = real_time_stats.get('prize_stats', {})
                        if prize_stats:
                            print("      🏆 奖级统计:")
                            for level, stats in prize_stats.items():
                                if stats['winners_count'] > 0:
                                    print(f"         {stats['name']}: {stats['winners_count']}人, "
                                          f"¥{stats['total_amount']:,.2f}")
                
                else:
                    print(f"   ❌ 进度查询失败: {progress_response.status_code}")
                    break
                
                print("   " + "-" * 60)
                time.sleep(3)  # 每3秒更新一次
                
        except KeyboardInterrupt:
            print("\n   ⏹️ 用户停止监控")
            
        print(f"\n🎯 请在浏览器中访问 http://localhost:3001 查看实时数据展示")
        print(f"   模拟ID: {simulation_id}")
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")

if __name__ == "__main__":
    test_frontend_realtime()
