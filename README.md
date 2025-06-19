# Numericals - 通用数值模拟验证工具

## 📋 项目概述

Numericals是一个专为游戏RTP验证需求设计的通用数值模拟验证工具。支持包含jackpot和未包含jackpot的各种游戏类型，提供高性能的大规模数值模拟和精确的RTP计算。

## 🎯 核心功能

### 游戏配置
- **多种游戏类型**: 支持彩票、刮刮乐、老虎机等多种游戏类型
- **灵活规则设置**: 自定义数字范围、选择数量、奖级配置
- **奖池机制**: 支持Jackpot设置，包括初始奖池、注入比例、返还比例
- **配置模板**: 提供预设模板，快速开始

### 数值模拟
- **高性能计算**: 基于NumPy和Pandas优化，支持百万级轮次模拟
- **参数化配置**: 模拟轮数、用户数范围、投注比数范围完全可配置
- **实时进度**: 模拟过程实时监控和进度反馈
- **随机性保证**: 高质量随机数生成，确保模拟公正性

### 结果分析
- **精确RTP计算**: 分别计算普通奖金RTP和Jackpot奖金RTP
- **统计分析**: 各奖级中奖人数、概率分析、趋势分析
- **可视化展示**: 丰富的图表展示，包括RTP趋势、奖级分布等
- **报告导出**: 支持HTML、Excel、JSON格式报告导出

## 🏗️ 技术架构

### 后端 (FastAPI + Python)
- **框架**: FastAPI - 高性能异步Web框架
- **数值计算**: NumPy, Pandas - 高效数值计算和数据处理
- **模拟引擎**: 自研通用模拟引擎，支持多种游戏类型
- **API设计**: RESTful API，支持实时进度推送

### 前端 (React)
- **框架**: React 18 - 现代化前端框架
- **UI组件**: Ant Design - 企业级UI设计语言
- **可视化**: Chart.js, Plotly.js - 专业图表库
- **状态管理**: React Hooks - 简洁的状态管理

### 部署
- **容器化**: Docker + Docker Compose
- **反向代理**: Nginx
- **跨平台**: 支持Windows、Linux、macOS

## 🚀 快速开始

### 环境要求
- Docker 20.0+
- Docker Compose 2.0+
- 或者：Python 3.11+, Node.js 18+

### Docker部署（推荐）

1. **克隆项目**
```bash
git clone <repository-url>
cd numericalTools
```

2. **启动服务**
```bash
docker-compose up -d
```

3. **访问应用**
- 前端界面: http://localhost:3000
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

### 本地开发

1. **后端启动**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

2. **前端启动**
```bash
cd frontend
npm install
npm start
```

## 📖 使用指南

### 1. 游戏配置
- 选择游戏类型（彩票、刮刮乐等）
- 设置基础参数（数字范围、选择数量、单注价格）
- 配置奖级（匹配条件、奖金设置）
- 设置奖池机制（可选）

### 2. 运行模拟
- 设置模拟参数（轮数、玩家数范围、投注范围）
- 启动模拟并实时监控进度
- 支持暂停和停止操作

### 3. 结果分析
- 查看汇总统计数据
- 分析RTP趋势和变化
- 查看各奖级详细统计
- 导出分析报告

## 🔧 配置说明

### 游戏规则配置
```json
{
  "game_type": "lottery",
  "name": "42选6彩票",
  "number_range": [1, 42],
  "selection_count": 6,
  "ticket_price": 20.0,
  "prize_levels": [
    {
      "level": 1,
      "name": "一等奖",
      "match_condition": 6,
      "prize_percentage": 0.9
    }
  ],
  "jackpot": {
    "enabled": true,
    "initial_amount": 30000000.0,
    "contribution_rate": 0.15,
    "return_rate": 0.9
  }
}
```

### 模拟配置
```json
{
  "rounds": 1000,
  "players_range": [50000, 100000],
  "bets_range": [5, 15],
  "seed": null
}
```

## 📊 性能特性

- **高效算法**: 使用集合操作优化号码匹配
- **内存管理**: 智能内存管理，支持大规模模拟
- **并发处理**: 支持多个模拟任务并发执行
- **实时监控**: 实时进度反馈和状态更新

## 🔒 安全特性

- **输入验证**: 严格的参数验证和边界检查
- **错误处理**: 完善的错误处理和恢复机制
- **资源限制**: 防止资源滥用的限制机制

## 📈 扩展性

- **插件化设计**: 支持自定义游戏类型
- **API扩展**: 开放的API接口，支持第三方集成
- **配置灵活**: 高度可配置的参数系统

## 🤝 贡献指南

欢迎提交Issue和Pull Request来改进项目。

## 📄 许可证

本项目采用MIT许可证。

## 📞 联系方式

如有问题或建议，请通过以下方式联系：
- 提交Issue
- 发送邮件

---

**@numericalTools** - 让数值模拟验证更简单、更准确、更高效！
