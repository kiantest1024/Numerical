#!/usr/bin/env python3
"""
测试模拟启动响应
"""

import requests
import json

def test_simulation_start():
    base_url = "http://localhost:8001"
    
    print("🔍 测试模拟启动响应...")
    
    try:
        # 1. 获取配置列表
        response = requests.get(f"{base_url}/api/v1/config/list")
        if response.status_code != 200:
            print(f"获取配置失败: {response.status_code}")
            return
            
        configs = response.json().get('configs', [])
        if not configs:
            print("没有可用的配置")
            return
            
        config_name = configs[0]['name']
        print(f"使用配置: {config_name}")
        
        # 2. 加载配置
        response = requests.get(f"{base_url}/api/v1/config/load/{config_name}")
        if response.status_code != 200:
            print(f"加载配置失败: {response.status_code}")
            return
            
        config = response.json()['config']
        
        # 3. 启动模拟
        simulation_request = {
            "game_config": config["game_rules"],
            "simulation_config": config["simulation_config"]
        }
        
        print("\n📤 发送启动请求...")
        print(f"请求数据: {json.dumps(simulation_request, indent=2, ensure_ascii=False)}")
        
        response = requests.post(f"{base_url}/api/v1/simulation/start", json=simulation_request)
        
        print(f"\n📥 响应状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"响应内容: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            simulation_id = result.get("simulation_id")
            status = result.get("status")
            
            print(f"\n✅ 模拟启动成功!")
            print(f"   模拟ID: {simulation_id}")
            print(f"   状态: {status}")
            print(f"   消息: {result.get('message')}")
            
            # 4. 立即查询进度
            if simulation_id:
                print(f"\n🔍 查询进度...")
                progress_response = requests.get(f"{base_url}/api/v1/simulation/progress/{simulation_id}")
                print(f"进度查询状态码: {progress_response.status_code}")
                if progress_response.status_code == 200:
                    progress = progress_response.json()
                    print(f"进度数据: {json.dumps(progress, indent=2, ensure_ascii=False)}")
                else:
                    print(f"进度查询失败: {progress_response.text}")
        else:
            print(f"❌ 启动失败: {response.text}")
            
    except Exception as e:
        print(f"❌ 异常: {e}")

if __name__ == "__main__":
    test_simulation_start()
