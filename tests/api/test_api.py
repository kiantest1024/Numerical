#!/usr/bin/env python3
"""
@numericalTools API功能测试脚本
测试完整的API流程
"""

import requests
import json
import time
import sys
from datetime import datetime


class APITester:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def test_health_check(self):
        """测试健康检查"""
        print("🔍 测试健康检查...")
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                print("✅ 健康检查通过")
                return True
            else:
                print(f"❌ 健康检查失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 健康检查异常: {e}")
            return False
    
    def test_get_templates(self):
        """测试获取配置模板"""
        print("📋 测试获取配置模板...")
        try:
            response = self.session.get(f"{self.base_url}/api/v1/config/templates")
            if response.status_code == 200:
                templates = response.json()["templates"]
                print(f"✅ 获取到 {len(templates)} 个模板")
                return templates
            else:
                print(f"❌ 获取模板失败: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ 获取模板异常: {e}")
            return None
    
    def test_save_config(self, config_name="test_config"):
        """测试保存配置"""
        print(f"💾 测试保存配置: {config_name}...")
        
        # 使用42选6彩票模板
        config_data = {
            "game_rules": {
                "game_type": "lottery",
                "name": "API测试42选6彩票",
                "description": "API测试用的42选6彩票游戏",
                "number_range": [1, 42],
                "selection_count": 6,
                "ticket_price": 20.0,
                "prize_levels": [
                    {
                        "level": 1,
                        "name": "一等奖",
                        "match_condition": 6,
                        "fixed_prize": None,
                        "prize_percentage": 0.9
                    },
                    {
                        "level": 2,
                        "name": "二等奖",
                        "match_condition": 5,
                        "fixed_prize": 50000.0,
                        "prize_percentage": None
                    }
                ],
                "jackpot": {
                    "enabled": True,
                    "initial_amount": 10000000.0,
                    "contribution_rate": 0.15,
                    "return_rate": 0.9,
                    "min_jackpot": 5000000.0
                }
            },
            "simulation_config": {
                "rounds": 50,  # 测试用较小轮数
                "players_range": [1000, 2000],
                "bets_range": [5, 10],
                "seed": 12345
            }
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/config/save?config_name={config_name}",
                json=config_data
            )
            if response.status_code == 200:
                print("✅ 配置保存成功")
                return True
            else:
                print(f"❌ 配置保存失败: {response.status_code}")
                print(response.text)
                return False
        except Exception as e:
            print(f"❌ 配置保存异常: {e}")
            return False
    
    def test_load_config(self, config_name="test_config"):
        """测试加载配置"""
        print(f"📂 测试加载配置: {config_name}...")
        try:
            response = self.session.get(f"{self.base_url}/api/v1/config/load/{config_name}")
            if response.status_code == 200:
                config = response.json()["config"]
                print("✅ 配置加载成功")
                return config
            else:
                print(f"❌ 配置加载失败: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ 配置加载异常: {e}")
            return None
    
    def test_start_simulation(self, config):
        """测试启动模拟"""
        print("🚀 测试启动模拟...")
        
        simulation_request = {
            "game_config": config["game_rules"],
            "simulation_config": config["simulation_config"]
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/simulation/start",
                json=simulation_request
            )
            if response.status_code == 200:
                result = response.json()
                simulation_id = result["simulation_id"]
                print(f"✅ 模拟启动成功: {simulation_id}")
                return simulation_id
            else:
                print(f"❌ 模拟启动失败: {response.status_code}")
                print(response.text)
                return None
        except Exception as e:
            print(f"❌ 模拟启动异常: {e}")
            return None
    
    def test_monitor_simulation(self, simulation_id, max_wait=60):
        """测试监控模拟进度"""
        print(f"📊 测试监控模拟进度: {simulation_id}...")
        
        start_time = time.time()
        while time.time() - start_time < max_wait:
            try:
                response = self.session.get(f"{self.base_url}/api/v1/simulation/progress/{simulation_id}")
                if response.status_code == 200:
                    progress = response.json()
                    
                    if progress.get("completed"):
                        print(f"✅ 模拟完成: {progress['status']}")
                        return True
                    else:
                        percentage = progress.get("progress_percentage", 0)
                        current_round = progress.get("current_round", 0)
                        total_rounds = progress.get("total_rounds", 0)
                        print(f"📈 进度: {percentage:.1f}% ({current_round}/{total_rounds})")
                        time.sleep(2)
                else:
                    print(f"❌ 获取进度失败: {response.status_code}")
                    return False
            except Exception as e:
                print(f"❌ 监控异常: {e}")
                return False
        
        print("⏰ 监控超时")
        return False
    
    def test_get_result(self, simulation_id):
        """测试获取模拟结果"""
        print(f"📈 测试获取模拟结果: {simulation_id}...")
        try:
            response = self.session.get(f"{self.base_url}/api/v1/simulation/result/{simulation_id}")
            if response.status_code == 200:
                result = response.json()
                print("✅ 结果获取成功")
                
                # 显示关键统计
                if result.get("summary"):
                    summary = result["summary"]
                    print(f"   总轮数: {summary.get('total_rounds', 0)}")
                    print(f"   总投注金额: ¥{summary.get('total_bet_amount', 0):,.2f}")
                    print(f"   总派奖金额: ¥{summary.get('total_payout', 0):,.2f}")
                    print(f"   平均RTP: {summary.get('average_rtp', 0):.2%}")
                    print(f"   头奖中出: {summary.get('jackpot_hits', 0)}次")
                
                return result
            else:
                print(f"❌ 结果获取失败: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ 结果获取异常: {e}")
            return None
    
    def test_generate_report(self, simulation_id):
        """测试生成报告"""
        print(f"📄 测试生成HTML报告: {simulation_id}...")
        try:
            response = self.session.get(f"{self.base_url}/api/v1/reports/generate/{simulation_id}?format=html")
            if response.status_code == 200:
                print("✅ HTML报告生成成功")
                return True
            else:
                print(f"❌ 报告生成失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 报告生成异常: {e}")
            return False
    
    def run_full_test(self):
        """运行完整测试流程"""
        print("=" * 60)
        print("🧪 @numericalTools API完整功能测试")
        print("=" * 60)
        
        tests_passed = 0
        total_tests = 7
        
        # 1. 健康检查
        if self.test_health_check():
            tests_passed += 1
        
        # 2. 获取模板
        templates = self.test_get_templates()
        if templates:
            tests_passed += 1
        
        # 3. 保存配置
        config_name = f"api_test_{int(time.time())}"
        if self.test_save_config(config_name):
            tests_passed += 1
        
        # 4. 加载配置
        config = self.test_load_config(config_name)
        if config:
            tests_passed += 1
        
        # 5. 启动模拟
        simulation_id = None
        if config:
            simulation_id = self.test_start_simulation(config)
            if simulation_id:
                tests_passed += 1
        
        # 6. 监控模拟
        if simulation_id:
            if self.test_monitor_simulation(simulation_id):
                tests_passed += 1
        
        # 7. 获取结果
        if simulation_id:
            result = self.test_get_result(simulation_id)
            if result:
                tests_passed += 1
        
        # 8. 生成报告（额外测试）
        if simulation_id:
            self.test_generate_report(simulation_id)
        
        print("\n" + "=" * 60)
        print(f"📊 测试结果: {tests_passed}/{total_tests} 通过")
        
        if tests_passed == total_tests:
            print("🎉 所有核心功能测试通过!")
            return True
        else:
            print("⚠️  部分功能测试失败")
            return False


def main():
    """主函数"""
    print("🔧 @numericalTools API功能测试")
    print("请确保后端服务已启动 (http://localhost:8001)")

    # 等待用户确认
    input("按回车键开始测试...")

    tester = APITester()
    success = tester.run_full_test()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
