
# GW2 WvW 日志系统 - 内存优化指南

## 概述

2026-05-06 对系统进行了全面的内存使用审查和优化，旨在消除所有可能导致内存溢出(OOM)的潜在风险点。

## 优化内容

### 1. 增强版内存监控中间件

**文件**: `app/middleware/enhanced_memory_monitor.py`

**功能**:
- 自动GC触发：内存超过阈值时自动触发垃圾回收
- 多级内存限制：软限制(警告) → 硬限制(错误) → 严重限制(拒绝请求)
- 内存历史记录：跟踪内存使用趋势
- 请求级内存监控：记录内存增长超标的请求

**配置项** (在 .env 中):
```env
MEMORY_DELTA_THRESHOLD_MB=100          # 单次请求内存增量阈值
MEMORY_RSS_SOFT_LIMIT_MB=1536         # 软限制（警告）
MEMORY_RSS_HARD_LIMIT_MB=2048         # 硬限制（错误）
MEMORY_RSS_CRITICAL_LIMIT_MB=2560     # 严重限制（拒绝请求）
AUTO_GC_THRESHOLD_MB=800              # 自动GC触发阈值
```

### 2. 增强版内存缓存

**文件**: `app/utils/enhanced_cache.py`

**功能**:
- 内存大小跟踪：计算缓存对象实际内存占用
- 双重限制：基于条目数量 + 基于内存大小
- 自动过期清理
- LRU驱逐策略
- 详细统计信息

**配置项**:
```env
CACHE_MAX_ITEMS=1000                  # 最大缓存条目数
CACHE_MAX_SIZE_MB=200                 # 最大缓存内存（MB）
CACHE_DEFAULT_TTL_SECONDS=3600        # 默认过期时间
```

### 3. 解析器内存优化

**文件**: `app/core/zevtc/parser.py`

**改进**:
- 分步清理：处理完一部分数据后立即释放
- 事件数据清理：事件处理完立即删除
- 解析完成清理：完整解析后清理所有中间数据
- 异常安全：异常情况下也保证清理

**关键改动**:
- 在 `_build_skills_from_core()` 后删除技能数据
- 在 `_second_pass_events()` 后删除事件数据（最大内存占用部分）
- 添加 `_cleanup()` 方法进行完整清理
- 在正常返回和异常抛出前都调用清理

### 4. 内存监控API

**文件**: `app/routers/memory_monitor.py`

**API端点**:
- `GET /api/memory/status` - 获取内存和缓存状态
- `POST /api/memory/gc` - 强制触发GC
- `GET /api/memory/cache/stats` - 获取缓存统计
- `POST /api/memory/cache/clear` - 清空所有缓存
- `DELETE /api/memory/cache/{key_pattern}` - 按模式删除缓存
- `GET /api/memory/check` - 检查内存是否超限

### 5. 已有的优化

系统中已存在的良好实践：
- 批量解析服务中已有GC触发 (`batch_parse_service.py`)
- 日志导入服务中已有分步清理 (`log_import_service.py`)
- 基础内存监控中间件已存在 (`memory_monitor.py`)

## 内存风险分析

### 高风险区域已优化:

1. **日志解析**: 事件数据是最大内存占用点，现已分步清理
2. **缓存膨胀**: 新增内存大小限制，防止无限制增长
3. **并发处理**: 单线程解析避免内存竞争
4. **大对象生命周期**: 主动清理而非依赖GC

## 使用建议

### 开发环境

使用默认配置即可，监控内存使用情况。

### 生产环境

根据服务器内存调整配置：

**小内存服务器 (2GB)**:
```env
MEMORY_RSS_SOFT_LIMIT_MB=1024
MEMORY_RSS_HARD_LIMIT_MB=1536
MEMORY_RSS_CRITICAL_LIMIT_MB=1792
AUTO_GC_THRESHOLD_MB=600
CACHE_MAX_SIZE_MB=100
```

**中等内存服务器 (4GB)**:
```env
MEMORY_RSS_SOFT_LIMIT_MB=2048
MEMORY_RSS_HARD_LIMIT_MB=3072
MEMORY_RSS_CRITICAL_LIMIT_MB=3584
AUTO_GC_THRESHOLD_MB=1200
CACHE_MAX_SIZE_MB=300
```

**大内存服务器 (8GB+)**:
```env
MEMORY_RSS_SOFT_LIMIT_MB=4096
MEMORY_RSS_HARD_LIMIT_MB=6144
MEMORY_RSS_CRITICAL_LIMIT_MB=7168
AUTO_GC_THRESHOLD_MB=2400
CACHE_MAX_SIZE_MB=500
```

## 监控与维护

### 日志监控

关注以下关键日志:
- `[memory] 请求内存显著增长` - 发现内存泄漏点
- `[memory] 内存超限` - 接近OOM风险
- `[memory] GC回收` - GC频繁说明内存压力大

### API监控

定期调用:
```bash
# 查看内存状态
curl http://localhost:8000/api/memory/status

# 必要时手动GC
curl -X POST http://localhost:8000/api/memory/gc
```

## 测试验证

### 压力测试建议

1. 批量解析大日志文件
2. 同时发起多个解析请求
3. 监控内存使用曲线
4. 验证GC是否及时触发

## 回退方案

如果新优化出现问题，可以:

1. 回退到旧的内存监控中间件
2. 禁用自动GC功能
3. 调整内存限制阈值

## 总结

本次优化全面提升了系统的内存管理能力，主要改进:
- ✅ 主动内存管理而非被动等待
- ✅ 多级预警机制
- ✅ 大对象及时清理
- ✅ 可配置的内存限制
- ✅ 完整的监控API
- ✅ 异常安全的资源释放

系统现在能够更好地应对高负载和大日志文件的处理，大幅降低OOM风险。

