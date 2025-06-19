#!/usr/bin/env python3
"""
快速启动后端服务的脚本
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    # 切换到backend目录
    backend_dir = Path(__file__).parent / "backend"
    os.chdir(backend_dir)
    
    print("🚀 启动 @numericalTools 后端服务...")
    print(f"📁 工作目录: {backend_dir}")
    print("🌐 服务地址: http://localhost:8000")
    print("📚 API文档: http://localhost:8000/docs")
    print("=" * 50)
    
    try:
        # 启动uvicorn服务器
        subprocess.run([
            "uvicorn",
            "app.main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ], check=True)
    except KeyboardInterrupt:
        print("\n🛑 服务已停止")
    except subprocess.CalledProcessError as e:
        print(f"❌ 启动失败: {e}")
        print("\n请确保已安装依赖:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ 未找到uvicorn命令")
        print("\n请安装FastAPI和uvicorn:")
        print("pip install fastapi uvicorn")
        sys.exit(1)

if __name__ == "__main__":
    main()
