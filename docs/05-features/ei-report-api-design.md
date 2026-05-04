# EI 完整报告 API 设计文档

> **版本**: v2.0
> **更新日期**: 2026-05-05
> **整合责任人**: 系统文档维护团队
> **变更摘要**: 更新为与实际 ei_report.py 端点完全一致，补充 unified / DELETE 端点，修正存储策略描述

---

## 1. 页面分析：EI HTML 数据结构

### 1.1 文件概况

- **文件**: `tests/20260426-220412_vindicator_detailed_wvw_367s_kill.html`
- **大小**: 36 MB（Elite Insights 3.21.1.0 生成）
- **类型**: WvW Detailed Report（Eternal Battlegrounds）

### 1.2 核心数据结构

EI HTML 页面内联了 3 组核心数据：

| 数据变量 | 解压后大小 | 用途 |
|---------|-----------|------|
| `_logData` | ~138 MB JSON | 完整统计报告（玩家、目标、阶段、技能、BUFF 等） |
| `_graphData` | ~129 MB JSON | 时间序列图表数据（每秒伤害、血量、BUFF 状态） |
| `_crData` | 通常为空 | Combat Replay 战斗回放数据 |

### 1.3 `_logData` 顶层结构

```
_logData
├── 元数据                    # logName, duration, mapID, recordedBy, arcVersion 等
├── players[51]               # 玩家列表（含 details: 伤害分布、技能循环、BUFF 图表）
├── targets[83]               # 目标列表（含 details: 伤害统计、防御统计）
├── enemies[47]               # 敌人列表
├── phases[1]                 # 战斗阶段（含 dpsStats, buffsStatContainer, mechanicStats 等）
├── skillMap[727]             # 技能定义表（ID → 名称、图标、类型）
├── buffMap[196]              # BUFF 定义表（ID → 名称、图标、堆叠方式）
├── damageModMap[42]          # 伤害修饰符定义
├── mechanicMap[12]           # 机制定义
├── boons[12] / conditions[13] / debuffs[2]  # BUFF/症状/ debuff ID 列表
└── dmgModifiers* / persBuffs # 伤害修饰符配置
```

### 1.4 页面功能组件

| 组件 | 所需数据 | 数据量级 |
|-----|---------|---------|
| Encounter 概览 | 元数据 + phases | ~10 KB |
| Statistics 主视图（Summary Tab） | players 基础信息 + phases 统计 | ~5 MB |
| 玩家详情（Player Details） | player.details | ~500 KB/人 |
| 伤害分布（Damage Distribution） | dmgDistributions + skillMap | ~1 MB |
| 技能循环（Rotation） | rotation + skillMap | ~200 KB |
| BUFF 图表（Boon Graph） | boonGraph + buffMap | ~500 KB |
| 阶段统计（Phase Stats） | phases[].buffsStatContainer + dpsStats | ~10 MB |
| 图表（Graphs/Plots） | _graphData.players[].damage / healthStates | ~2 MB/人 |
| Combat Replay | _crData + _graphData | 视情况而定 |

---

## 2. 设计方案

### 2.1 核心策略

采用 **"元数据存 DB + 大文件存磁盘 + 按需分层 API"** 的混合架构：

1. **摘要 JSON（summary_json）**: 存储在数据库 `ei_report` 表的 JSON 列中
   - 包含：元数据、定义表（skillMap/buffMap）、players/targets 基础信息（不含 details）
   - 体积：~1-5 MB，适合直接数据库查询

2. **完整数据（_logData）**: gzip 压缩后存入文件系统
   - 路径：`uploads/ei_reports/{log_id}/log_data.json.gz`
   - 体积：~20-30 MB（压缩后）

3. **图表数据（_graphData）**: gzip 压缩后存入文件系统
   - 路径：`uploads/ei_reports/{log_id}/graph_data.json.gz`
   - 体积：~20-30 MB（压缩后）

### 2.2 数据库 Schema

```sql
CREATE TABLE `ei_report` (
    `report_id`         BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `log_id`            BIGINT UNSIGNED NOT NULL,
    `report_type`       VARCHAR(50) NOT NULL DEFAULT 'detailed_wvw',
    `ei_version`        VARCHAR(50),
    `summary_json`      JSON,                          -- 摘要数据
    `log_data_path`     VARCHAR(500),                  -- 完整 _logData 文件路径
    `graph_data_path`   VARCHAR(500),                  -- 完整 _graphData 文件路径
    `cr_data_path`      VARCHAR(500),                  -- Combat Replay 文件路径
    `log_name`          VARCHAR(200),
    `duration_ms`       BIGINT,
    `player_count`      BIGINT,
    `target_count`      BIGINT,
    `success`           VARCHAR(10),
    `recorded_by`       VARCHAR(100),
    `recorded_account_by` VARCHAR(100),
    `map_id`            BIGINT,
    `region`            VARCHAR(50),
    `wvw`               VARCHAR(10),
    `created_at`        DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at`        DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`report_id`),
    UNIQUE KEY `uk_ei_report_log_id` (`log_id`)
);
```

---

## 3. API 接口列表

### 3.1 基础端点

| 方法 | 路径 | 功能 | 数据量 |
|-----|------|------|--------|
| GET | `/api/v1/ei-report/logs` | 已导入报告列表（分页） | ~10 KB |
| GET | `/api/v1/ei-report/logs/{log_id}/meta` | 报告元数据（存在性检查） | ~1 KB |
| GET | `/api/v1/ei-report/logs/{log_id}/summary` | 报告摘要（前端首屏加载） | ~1-5 MB |
| GET | `/api/v1/ei-report/logs/{log_id}/data` | 完整 `_logData`（gzip 流式） | ~20-30 MB |
| GET | `/api/v1/ei-report/logs/{log_id}/graph` | 完整 `_graphData`（gzip 流式） | ~20-30 MB |

### 3.2 按需加载端点

| 方法 | 路径 | 功能 | 数据量 |
|-----|------|------|--------|
| GET | `/api/v1/ei-report/logs/{log_id}/players/{player_index}` | 单个玩家完整数据（含 details） | ~500 KB |
| GET | `/api/v1/ei-report/logs/{log_id}/targets/{target_index}` | 单个目标完整数据（含 details） | ~200 KB |
| GET | `/api/v1/ei-report/logs/{log_id}/phases/{phase_index}` | 单个阶段完整统计 | ~5-10 MB |

### 3.3 管理与统一数据端点

| 方法 | 路径 | 功能 |
|-----|------|------|
| POST | `/api/v1/ei-report/logs/{log_id}/import` | 从 EI HTML 文件导入报告 |
| GET | `/api/v1/ei-report/logs/{log_id}/unified` | 统一 EI 数据（整合多源数据） |
| DELETE | `/api/v1/ei-report/logs/{log_id}` | 删除报告（DB + 文件） |

---

## 4. 前端 1:1 还原建议

### 4.1 加载策略

```
首屏加载:
  1. GET /meta      → 检查报告是否存在
  2. GET /summary   → 加载摘要数据（ players 列表、定义表、元数据）
  3. 渲染 Summary Tab / 玩家列表

按需加载:
  4. 用户点击某玩家 → GET /players/{idx}
  5. 用户切换 Graph Tab → GET /graph（或从本地缓存读取）
  6. 用户点击 Phase 详情 → GET /phases/{idx}

完整数据（可选）:
  7. 后台预加载 /data 和 /graph（gzip 流式解压到内存/IndexedDB）
```

### 4.2 数据格式兼容性

API 返回的 `_logData` / `_graphData` 结构与 EI HTML 中的原始结构**完全一致**，前端可直接复用 EI 的 Vue 组件逻辑，无需数据转换。

---

## 5. 实现文件清单

| 文件 | 说明 |
|------|------|
| `app/models/ei_report.py` | ORM 模型 `EiReport` |
| `app/services/ei_report_service.py` | 导入、查询、文件读写服务 |
| `app/routers/ei_report.py` | API 路由（全部端点） |
| `app/schemas/ei_report.py` | Pydantic Schema |
| `app/routers/__init__.py` | 导出 `ei_report_router` |
| `main.py` | 注册路由 |

---

## 6. 测试验证

### 6.1 数据导入测试

```bash
# 使用测试 HTML 文件导入
POST /api/v1/ei-report/logs/1/import
{
  "html_path": "tests/20260426-220412_vindicator_detailed_wvw_367s_kill.html",
  "report_type": "detailed_wvw"
}

# 结果
Import successful!
  log_name=Detailed WvW - Eternal Battlegrounds
  player_count=51
  target_count=83
  duration_ms=367295
  log_data=1.74MB (compressed from ~138MB)
  graph_data=1.74MB (compressed from ~129MB)
```

### 6.2 API 端点验证

| 端点 | 状态 | 说明 |
|------|------|------|
| GET `/logs` | ✅ 200 | 返回报告列表 |
| GET `/logs/1/meta` | ✅ 200 | 元数据完整 |
| GET `/logs/1/summary` | ✅ 200 | players, targets, skills, buffs |
| GET `/logs/1/data` | ✅ 200 | gzip 流式完整 _logData |
| GET `/logs/1/graph` | ✅ 200 | gzip 流式完整 _graphData |
| GET `/logs/1/players/0` | ✅ 200 | 玩家详情含 rotation, boonGraph, dmgDistributions |
| GET `/logs/1/targets/0` | ✅ 200 | 目标详情 |
| GET `/logs/1/phases/0` | ✅ 200 | 阶段含 dpsStats, buffsStatContainer, mechanicStats |
| GET `/logs/1/unified` | ✅ 200 | 统一 EI 数据 |
| DELETE `/logs/1` | ✅ 200 | 删除报告及关联文件 |

---

## 7. 已知限制与后续优化

1. **数据体积**: 单次 `/data` 或 `/graph` 响应仍达 20-30 MB，建议在服务端增加 HTTP Range 支持或进一步拆分数据块
2. **导入来源**: 当前仅支持从 EI HTML 文件导入，后续可扩展为直接解析 EI 生成的 `.json` 文件
3. **全文搜索**: 当前 `summary_json` 存储在数据库 JSON 列中，如需对玩家名称、技能名称等进行全文搜索，建议建立单独的搜索索引表
4. **缓存策略**: 建议在 CDN / 反向代理层对 `/data` 和 `/graph` 进行长时间缓存（数据不变）
