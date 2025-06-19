@echo off
echo 🚀 启动 @numericalTools 前端服务...
echo 📁 工作目录: %cd%
echo 🌐 服务地址: http://localhost:3000
echo ===============================================

if not exist node_modules (
    echo 📦 安装依赖...
    npm install
)

echo 🚀 启动开发服务器...
npm start
