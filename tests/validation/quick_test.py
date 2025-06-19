#!/usr/bin/env python3
"""
快速API测试
"""

import requests

def test_api():
    base_url = "http://localhost:8001"
    
    print("测试根路径...")
    try:
        response = requests.get(f"{base_url}/")
        print(f"根路径: {response.status_code}")
        if response.status_code == 200:
            print(response.json())
    except Exception as e:
        print(f"根路径错误: {e}")
    
    print("\n测试健康检查...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"健康检查: {response.status_code}")
        if response.status_code == 200:
            print(response.json())
    except Exception as e:
        print(f"健康检查错误: {e}")
    
    print("\n测试API文档...")
    try:
        response = requests.get(f"{base_url}/docs")
        print(f"API文档: {response.status_code}")
    except Exception as e:
        print(f"API文档错误: {e}")
    
    print("\n测试配置模板...")
    try:
        response = requests.get(f"{base_url}/api/v1/config/templates")
        print(f"配置模板: {response.status_code}")
        if response.status_code != 200:
            print(f"错误内容: {response.text}")
    except Exception as e:
        print(f"配置模板错误: {e}")

if __name__ == "__main__":
    test_api()
