# @numericalTools 性能优化指南

## 🚀 性能优化概述

本文档提供了针对 @numericalTools 的性能优化建议和最佳实践。

## 📊 当前性能基准

基于测试结果，当前系统性能表现：

### 模拟性能
- **小规模模拟** (100轮): ~3.25秒
- **中规模模拟** (1,000轮): 预计 ~32秒
- **大规模模拟** (10,000轮): 预计 ~5分钟
- **超大规模模拟** (100,000轮): 预计 ~50分钟

### 内存使用
- **基础内存**: ~50MB
- **每万轮增加**: ~10MB
- **最大建议轮数**: 1,000,000轮

## 🔧 后端性能优化

### 1. 算法优化

#### 集合操作优化
```python
# 当前实现 - 已优化
def check_matches(self, player_numbers: Set[int], winning_numbers: Set[int]) -> int:
    return len(player_numbers & winning_numbers)  # 使用集合交集，O(min(m,n))
```

#### 批量处理优化
```python
# 建议实现 - 批量生成号码
def generate_batch_numbers(self, batch_size: int) -> List[Set[int]]:
    """批量生成玩家号码，减少函数调用开销"""
    min_num, max_num = self.game_rules.number_range
    numbers_list = []
    for _ in range(batch_size):
        numbers = set(random.sample(range(min_num, max_num + 1), self.game_rules.selection_count))
        numbers_list.append(numbers)
    return numbers_list
```

#### NumPy向量化优化
```python
# 建议实现 - 使用NumPy加速
import numpy as np

def vectorized_simulation(self, rounds: int):
    """使用NumPy向量化操作加速模拟"""
    # 预分配数组
    results = np.zeros((rounds, 4))  # [bet_amount, payout, rtp, jackpot]
    
    # 批量生成随机数
    players_counts = np.random.randint(
        self.sim_config.players_range[0], 
        self.sim_config.players_range[1] + 1, 
        size=rounds
    )
    
    # 向量化计算
    for i in range(rounds):
        # 模拟逻辑
        pass
    
    return results
```

### 2. 内存管理优化

#### 流式处理
```python
def stream_simulation_results(self):
    """流式处理大规模模拟结果"""
    # 使用生成器避免内存堆积
    for round_num in range(1, self.sim_config.rounds + 1):
        result = self.simulate_round(round_num)
        yield result
        
        # 定期清理内存
        if round_num % 1000 == 0:
            gc.collect()
```

#### 结果压缩存储
```python
def compress_results(self, results: List[RoundResult]) -> bytes:
    """压缩存储模拟结果"""
    import pickle
    import gzip
    
    # 只保存关键数据
    compressed_data = {
        'summary': self.generate_summary(),
        'key_metrics': self.extract_key_metrics(results)
    }
    
    return gzip.compress(pickle.dumps(compressed_data))
```

### 3. 并发处理优化

#### 异步处理
```python
import asyncio
from concurrent.futures import ProcessPoolExecutor

async def parallel_simulation(self, rounds: int, workers: int = 4):
    """并行处理模拟"""
    chunk_size = rounds // workers
    
    with ProcessPoolExecutor(max_workers=workers) as executor:
        tasks = []
        for i in range(workers):
            start_round = i * chunk_size
            end_round = start_round + chunk_size if i < workers - 1 else rounds
            
            task = asyncio.get_event_loop().run_in_executor(
                executor, 
                self.simulate_chunk, 
                start_round, 
                end_round
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        return self.merge_results(results)
```

## 🌐 前端性能优化

### 1. 组件优化

#### 虚拟化长列表
```javascript
import { FixedSizeList as List } from 'react-window';

const VirtualizedTable = ({ data }) => {
  const Row = ({ index, style }) => (
    <div style={style}>
      {/* 渲染单行数据 */}
      {data[index]}
    </div>
  );

  return (
    <List
      height={400}
      itemCount={data.length}
      itemSize={50}
    >
      {Row}
    </List>
  );
};
```

#### 图表性能优化
```javascript
// 使用 React.memo 避免不必要的重渲染
const OptimizedChart = React.memo(({ data, config }) => {
  // 数据采样，避免渲染过多点
  const sampledData = useMemo(() => {
    if (data.length > 1000) {
      const step = Math.ceil(data.length / 1000);
      return data.filter((_, index) => index % step === 0);
    }
    return data;
  }, [data]);

  return <Plot data={sampledData} layout={config} />;
});
```

### 2. 状态管理优化

#### 分页加载
```javascript
const useInfiniteScroll = (fetchMore) => {
  const [loading, setLoading] = useState(false);
  
  const loadMore = useCallback(async () => {
    if (loading) return;
    setLoading(true);
    await fetchMore();
    setLoading(false);
  }, [loading, fetchMore]);
  
  return { loadMore, loading };
};
```

## 🗄️ 数据库优化

### 1. 索引优化
```sql
-- 为常用查询添加索引
CREATE INDEX idx_simulation_status ON simulations(status);
CREATE INDEX idx_simulation_created_at ON simulations(created_at);
CREATE INDEX idx_config_game_type ON game_configs(game_type);
```

### 2. 查询优化
```python
# 使用分页查询
def get_simulations_paginated(page: int = 1, size: int = 20):
    offset = (page - 1) * size
    return db.query(Simulation).offset(offset).limit(size).all()

# 使用预加载避免N+1查询
def get_simulation_with_results(simulation_id: str):
    return db.query(Simulation).options(
        joinedload(Simulation.results)
    ).filter(Simulation.id == simulation_id).first()
```

## 📈 监控和分析

### 1. 性能监控
```python
import time
import psutil
from functools import wraps

def monitor_performance(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss
        
        result = func(*args, **kwargs)
        
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss
        
        logger.info(f"{func.__name__} - 耗时: {end_time - start_time:.2f}s, "
                   f"内存变化: {(end_memory - start_memory) / 1024 / 1024:.2f}MB")
        
        return result
    return wrapper
```

### 2. 性能分析工具
```python
# 使用 cProfile 分析性能瓶颈
import cProfile
import pstats

def profile_simulation():
    profiler = cProfile.Profile()
    profiler.enable()
    
    # 运行模拟
    engine.run_simulation()
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(20)  # 显示前20个最耗时的函数
```

## 🎯 优化建议

### 短期优化 (1-2周)
1. **实现批量处理**: 减少函数调用开销
2. **添加进度缓存**: 避免重复计算
3. **优化前端渲染**: 使用虚拟化组件
4. **添加数据压缩**: 减少内存使用

### 中期优化 (1-2月)
1. **实现并行处理**: 利用多核CPU
2. **添加数据库**: 持久化存储结果
3. **实现缓存机制**: Redis缓存热点数据
4. **优化算法**: 使用更高效的数学库

### 长期优化 (3-6月)
1. **分布式计算**: 支持集群部署
2. **GPU加速**: 使用CUDA加速计算
3. **智能采样**: 自适应采样策略
4. **预测模型**: 机器学习优化

## 📊 性能测试

### 基准测试脚本
```python
def benchmark_simulation():
    """性能基准测试"""
    test_cases = [
        (100, "小规模"),
        (1000, "中规模"), 
        (10000, "大规模")
    ]
    
    for rounds, desc in test_cases:
        config = create_test_config(rounds)
        engine = UniversalSimulationEngine(config)
        
        start_time = time.time()
        result = await engine.run_simulation()
        end_time = time.time()
        
        print(f"{desc}测试 ({rounds}轮): {end_time - start_time:.2f}秒")
        print(f"平均每轮: {(end_time - start_time) / rounds * 1000:.2f}毫秒")
```

## 🔍 故障排除

### 常见性能问题
1. **内存泄漏**: 检查循环引用和未释放的资源
2. **CPU占用过高**: 分析算法复杂度和优化热点
3. **响应缓慢**: 检查数据库查询和网络请求
4. **前端卡顿**: 优化渲染逻辑和状态更新

### 调试工具
- **后端**: cProfile, memory_profiler, py-spy
- **前端**: React DevTools, Chrome DevTools
- **系统**: htop, iotop, netstat

---

通过以上优化措施，@numericalTools 可以在保持准确性的同时显著提升性能，支持更大规模的模拟需求。
