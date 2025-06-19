#!/usr/bin/env python3
"""
@numericalTools 启动脚本
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 8):
        print("❌ 错误: 需要Python 3.8或更高版本")
        sys.exit(1)
    print(f"✅ Python版本: {sys.version}")


def check_dependencies():
    """检查依赖"""
    try:
        import fastapi
        import uvicorn
        import numpy
        print("✅ 后端依赖检查通过")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install -r backend/requirements.txt")
        return False


def start_backend(port=8000, reload=True):
    """启动后端服务"""
    print(f"🚀 启动后端服务 (端口: {port})")
    
    backend_dir = Path(__file__).parent / "backend"
    os.chdir(backend_dir)
    
    cmd = [
        "uvicorn",
        "app.main:app",
        "--host", "0.0.0.0",
        "--port", str(port)
    ]
    
    if reload:
        cmd.append("--reload")
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n🛑 后端服务已停止")
    except subprocess.CalledProcessError as e:
        print(f"❌ 启动后端失败: {e}")
        sys.exit(1)


def start_frontend(port=3000):
    """启动前端服务"""
    print(f"🚀 启动前端服务 (端口: {port})")
    
    frontend_dir = Path(__file__).parent / "frontend"
    
    if not (frontend_dir / "node_modules").exists():
        print("📦 安装前端依赖...")
        os.chdir(frontend_dir)
        subprocess.run(["npm", "install"], check=True)
    
    os.chdir(frontend_dir)
    
    try:
        env = os.environ.copy()
        env["PORT"] = str(port)
        subprocess.run(["npm", "start"], env=env, check=True)
    except KeyboardInterrupt:
        print("\n🛑 前端服务已停止")
    except subprocess.CalledProcessError as e:
        print(f"❌ 启动前端失败: {e}")
        sys.exit(1)


def start_docker():
    """使用Docker启动"""
    print("🐳 使用Docker启动服务...")
    
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    try:
        # 检查Docker是否可用
        subprocess.run(["docker", "--version"], 
                      check=True, 
                      capture_output=True)
        subprocess.run(["docker-compose", "--version"], 
                      check=True, 
                      capture_output=True)
        
        # 启动服务
        subprocess.run(["docker-compose", "up", "-d"], check=True)
        
        print("✅ 服务启动成功!")
        print("📱 前端地址: http://localhost:3000")
        print("🔧 后端API: http://localhost:8000")
        print("📚 API文档: http://localhost:8000/docs")
        print("\n使用 'docker-compose logs -f' 查看日志")
        print("使用 'docker-compose down' 停止服务")
        
    except subprocess.CalledProcessError:
        print("❌ Docker或Docker Compose未安装或不可用")
        print("请安装Docker Desktop或使用 --dev 模式")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 停止服务...")
        subprocess.run(["docker-compose", "down"])


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="@numericalTools 启动脚本")
    parser.add_argument("--mode", 
                       choices=["docker", "backend", "frontend", "dev"],
                       default="docker",
                       help="启动模式")
    parser.add_argument("--backend-port", 
                       type=int, 
                       default=8000,
                       help="后端端口")
    parser.add_argument("--frontend-port", 
                       type=int, 
                       default=3000,
                       help="前端端口")
    parser.add_argument("--no-reload", 
                       action="store_true",
                       help="禁用热重载")
    
    args = parser.parse_args()
    
    print("=" * 50)
    print("🔧 @numericalTools 启动脚本")
    print("=" * 50)
    
    if args.mode == "docker":
        start_docker()
    
    elif args.mode == "backend":
        check_python_version()
        if not check_dependencies():
            sys.exit(1)
        start_backend(args.backend_port, not args.no_reload)
    
    elif args.mode == "frontend":
        start_frontend(args.frontend_port)
    
    elif args.mode == "dev":
        check_python_version()
        if not check_dependencies():
            sys.exit(1)
        
        print("🔧 开发模式: 需要手动启动前端和后端")
        print(f"后端: cd backend && uvicorn app.main:app --reload --port {args.backend_port}")
        print(f"前端: cd frontend && npm start")
        
        # 只启动后端
        start_backend(args.backend_port, not args.no_reload)


if __name__ == "__main__":
    main()
