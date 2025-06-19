# 测试文件说明

本目录包含了@numericalTools项目的所有测试文件，按功能分类组织。

## 📁 目录结构

```
tests/
├── README.md                    # 本文件
├── core/                        # 核心功能测试
│   ├── test_jackpot_logic.py    # 奖池逻辑测试
│   ├── test_prize_calculation.py # 奖金计算测试
│   └── test_simulation_engine.py # 模拟引擎测试
├── api/                         # API接口测试
│   ├── test_config_api.py       # 配置API测试
│   └── test_simulation_api.py   # 模拟API测试
├── integration/                 # 集成测试
│   ├── test_complete_workflow.py # 完整工作流测试
│   └── test_realtime_data.py    # 实时数据测试
└── validation/                  # 验证测试
    ├── test_readme_validation.py # README功能验证
    └── test_system_validation.py # 系统验证
```

## 🧪 测试分类

### 核心功能测试 (core/)
- **奖池逻辑测试**: 验证奖池重置、分阶段注入等核心逻辑
- **奖金计算测试**: 验证各奖级奖金计算的正确性
- **模拟引擎测试**: 验证模拟引擎的核心算法

### API接口测试 (api/)
- **配置API测试**: 验证配置的增删改查功能
- **模拟API测试**: 验证模拟启动、进度、结果等API

### 集成测试 (integration/)
- **完整工作流测试**: 验证从配置到模拟到结果的完整流程
- **实时数据测试**: 验证实时数据获取和显示功能

### 验证测试 (validation/)
- **README功能验证**: 验证README文档中描述的功能
- **系统验证**: 验证整个系统的稳定性和正确性

## 🚀 运行测试

### 运行所有测试
```bash
cd numericalTools/tests
python -m pytest
```

### 运行特定分类的测试
```bash
# 运行核心功能测试
python -m pytest core/

# 运行API测试
python -m pytest api/

# 运行集成测试
python -m pytest integration/

# 运行验证测试
python -m pytest validation/
```

### 运行单个测试文件
```bash
python test_jackpot_logic.py
```

## 📋 测试覆盖范围

- ✅ 奖池机制和重置逻辑
- ✅ 分阶段资金分配
- ✅ 奖金计算和统计
- ✅ 未中奖人数统计
- ✅ 实时数据显示
- ✅ 配置管理功能
- ✅ API接口完整性
- ✅ 前后端集成
- ✅ 数据库操作
- ✅ 错误处理机制
