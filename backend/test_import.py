#!/usr/bin/env python3
"""
测试导入
"""

try:
    print("测试导入 app.api.config...")
    from app.api import config
    print("✅ config 导入成功")
    print(f"config.router: {config.router}")
except Exception as e:
    print(f"❌ config 导入失败: {e}")

try:
    print("\n测试导入 app.api.simulation...")
    from app.api import simulation
    print("✅ simulation 导入成功")
except Exception as e:
    print(f"❌ simulation 导入失败: {e}")

try:
    print("\n测试导入 app.api.reports...")
    from app.api import reports
    print("✅ reports 导入成功")
except Exception as e:
    print(f"❌ reports 导入失败: {e}")

print("\n测试完成")
