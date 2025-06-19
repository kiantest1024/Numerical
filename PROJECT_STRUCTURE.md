# @numericalTools 项目结构

## 📁 项目目录结构

```
numericalTools/
├── 📄 README.md                    # 项目说明文档
├── 📄 USER_MANUAL.md               # 用户使用手册
├── 📄 DEPLOYMENT_GUIDE.md          # 部署指南
├── 📄 PROJECT_STRUCTURE.md         # 项目结构说明（本文件）
├── 🐳 docker-compose.yml           # Docker编排配置
├── 🚀 start.py                     # 统一启动脚本
│
├── 📂 backend/                     # 后端服务
│   ├── 📄 Dockerfile               # 后端Docker配置
│   ├── 📄 requirements.txt         # Python依赖
│   ├── 📂 app/                     # 应用主目录
│   │   ├── 📄 __init__.py
│   │   ├── 📄 main.py              # FastAPI应用入口
│   │   ├── 📄 database.py          # 数据库配置
│   │   ├── 📂 api/                 # API路由
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 config.py        # 配置管理API
│   │   │   ├── 📄 simulation.py    # 模拟执行API
│   │   │   └── 📄 reports.py       # 报告生成API
│   │   ├── 📂 core/                # 核心业务逻辑
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 config.py        # 应用配置
│   │   │   └── 📄 simulation_engine.py # 模拟引擎
│   │   ├── 📂 models/              # 数据模型
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 game_config.py   # 游戏配置模型
│   │   │   └── 📄 simulation_result.py # 模拟结果模型
│   │   ├── 📂 services/            # 业务服务
│   │   │   └── 📄 database_service.py # 数据库服务
│   │   └── 📂 utils/               # 工具函数
│   │       ├── 📄 __init__.py
│   │       └── 📄 helpers.py       # 辅助函数
│   └── 📂 uploads/                 # 上传文件存储
│       └── 📂 configs/             # 配置文件存储
│
├── 📂 frontend/                    # 前端应用
│   ├── 📄 Dockerfile               # 前端Docker配置
│   ├── 📄 nginx.conf               # Nginx配置
│   ├── 📄 package.json             # Node.js依赖
│   ├── 📄 package-lock.json        # 依赖锁定文件
│   ├── 📂 public/                  # 静态资源
│   │   ├── 📄 index.html
│   │   ├── 📄 favicon.ico
│   │   └── 📄 manifest.json
│   └── 📂 src/                     # 源代码
│       ├── 📄 index.js             # 应用入口
│       ├── 📄 App.js               # 主应用组件
│       ├── 📄 App.css              # 全局样式
│       ├── 📄 index.css            # 基础样式
│       ├── 📄 setupProxy.js        # 代理配置
│       ├── 📂 components/          # 通用组件
│       │   └── 📄 Layout.js        # 布局组件
│       └── 📂 pages/               # 页面组件
│           ├── 📄 HomePage.js      # 首页
│           ├── 📄 ConfigPage.js    # 配置管理页
│           ├── 📄 SimulationPage.js # 模拟运行页
│           ├── 📄 ResultsPage.js   # 结果分析页
│           └── 📄 ReportsPage.js   # 报告下载页
│
└── 📂 tests/                       # 测试文件
    ├── 📄 README.md                # 测试说明
    ├── 📂 api/                     # API测试
    ├── 📂 core/                    # 核心逻辑测试
    ├── 📂 integration/             # 集成测试
    └── 📂 validation/              # 验证测试
```

## 🎯 核心功能模块

### 后端模块

#### 1. 模拟引擎 (`core/simulation_engine.py`)
- **功能**: 通用数值模拟计算引擎
- **特性**: 支持有/无奖池游戏，实时进度追踪，异步执行
- **核心类**: `UniversalSimulationEngine`

#### 2. API路由 (`api/`)
- **配置管理** (`config.py`): 游戏配置的增删改查
- **模拟执行** (`simulation.py`): 模拟启动、进度查询、结果获取
- **报告生成** (`reports.py`): HTML/JSON/Excel报告生成

#### 3. 数据模型 (`models/`)
- **游戏配置** (`game_config.py`): 游戏规则、奖级、奖池配置
- **模拟结果** (`simulation_result.py`): 模拟进度、结果、统计数据

### 前端模块

#### 1. 页面组件 (`pages/`)
- **首页** (`HomePage.js`): 项目介绍和快速导航
- **配置管理** (`ConfigPage.js`): 游戏配置的创建和管理
- **模拟运行** (`SimulationPage.js`): 模拟执行和实时监控
- **结果分析** (`ResultsPage.js`): 详细的结果分析和可视化
- **报告下载** (`ReportsPage.js`): 报告生成和下载

#### 2. 核心特性
- **实时数据**: WebSocket实时更新模拟进度
- **数据可视化**: 使用Plotly.js展示图表
- **响应式设计**: 适配不同屏幕尺寸
- **多语言支持**: 中文界面

## 🔧 技术栈

### 后端技术
- **框架**: FastAPI (Python 3.8+)
- **数据库**: MySQL (生产) / SQLite (开发)
- **计算库**: NumPy (数值计算)
- **异步**: asyncio (异步处理)

### 前端技术
- **框架**: React 18
- **UI库**: Ant Design
- **图表**: Plotly.js
- **路由**: React Router
- **样式**: CSS3 + Flexbox/Grid

### 部署技术
- **容器化**: Docker + Docker Compose
- **Web服务器**: Nginx (生产环境)
- **进程管理**: Uvicorn (ASGI服务器)

## 📊 数据流

```
用户界面 → API请求 → 业务逻辑 → 模拟引擎 → 数据存储
    ↑                                           ↓
实时更新 ← WebSocket ← 进度回调 ← 异步执行 ← 结果计算
```

## 🚀 启动方式

### 开发环境
```bash
# 统一启动（推荐）
python start.py --mode dev

# 分别启动
cd backend && uvicorn app.main:app --reload --port 8001
cd frontend && npm start
```

### 生产环境
```bash
# Docker部署（推荐）
docker-compose up -d

# 手动部署
python start.py --mode docker
```

## 📝 配置文件

### 环境配置
- **开发环境**: SQLite数据库，调试模式
- **生产环境**: MySQL数据库，性能优化

### 关键配置
- **数据库连接**: `backend/app/core/config.py`
- **前端代理**: `frontend/src/setupProxy.js`
- **Docker配置**: `docker-compose.yml`

## 🧪 测试结构

### 测试分类
- **API测试**: 接口功能验证
- **核心测试**: 业务逻辑验证
- **集成测试**: 端到端功能验证
- **验证测试**: 修复功能验证

### 运行测试
```bash
# 快速API测试
python tests/validation/quick_test.py

# 功能验证测试
python tests/validation/test_fixes.py
```

## 📋 项目清理说明

本项目已进行全面清理，删除了以下冗余内容：

### 已删除的文件
- ❌ `start_backend.py` - 冗余启动脚本
- ❌ `backend/run.py` - 重复启动脚本
- ❌ `frontend/start_frontend.bat` - 平台特定脚本
- ❌ `doc/prompt.txt` - 开发时的临时文档
- ❌ `tests/api/test_api.py` - 重复的API测试
- ❌ `tests/api/test_backend.py` - 重复的后端测试

### 已清理的代码
- ✅ 删除未使用的导入语句
- ✅ 清理冗余注释和调试代码
- ✅ 移除重复的函数和变量
- ✅ 优化代码结构和格式

### 保留的核心功能
- ✅ 完整的模拟引擎功能
- ✅ 全面的前端界面
- ✅ 完善的API接口
- ✅ 实时数据更新
- ✅ 报告生成功能
- ✅ 有用的测试文件

## 🎯 项目优势

1. **架构清晰**: 前后端分离，模块化设计
2. **功能完整**: 涵盖配置、模拟、分析、报告全流程
3. **性能优化**: 异步处理，实时更新，大规模计算支持
4. **用户友好**: 现代化界面，直观操作，详细文档
5. **部署简单**: Docker一键部署，多环境支持
6. **代码质量**: 清理冗余，结构优化，易于维护
