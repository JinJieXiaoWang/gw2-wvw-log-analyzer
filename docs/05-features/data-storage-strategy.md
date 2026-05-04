# 数据存储策略与数据流架构

> **版本**: v2.0
> **更新日期**: 2026-05-05
> **整合责任人**: 系统文档维护团队
> **变更摘要**: 更新为与实际存储策略一致，删除 evtc_* 原始数据表描述，聚焦 EI 大文件 gzip 存储 + fights/fight_stats 聚合表

---

## 一、设计目标

1. **原始数据完整性**：EI 解析后的完整数据以 gzip 文件形式存储
2. **派生数据可复用**：`fights` / `fight_stats` 存储预计算聚合指标，避免每次 API 请求重复计算
3. **前端接口可用性**：新 API 路由从 `fights` / `fight_stats` / `ei_*` 表读取，不再依赖 `raw_json` 大字段
4. **重解析原子性**：重新解析时，同一事务内删除旧数据并插入新数据，杜绝数据混用

---

## 二、表架构与关联关系

### 2.1 核心表关系图

```
fights (战斗聚合表) ──1:N── fight_stats (玩家战斗统计)
                              │
                              └── 前端排行榜、概览等 API 数据源

ei_report (EI 报告) ──1:1── log_id (日志)
              │
              ├── log_data_path ──→ 文件系统 (gzip _logData)
              ├── graph_data_path ──→ 文件系统 (gzip _graphData)
              └── cr_data_path ──→ 文件系统 (gzip _crData)
```

### 2.2 各表职责

| 表名 | 存储内容 | 数据量级 | 主键 | 外键 |
|------|---------|---------|------|------|
| `fights` | 战斗聚合信息（时长、地图、结果等） | ~1 条/日志 | `fight_id` BIGINT | `log_id` → logs |
| `fight_stats` | 玩家战斗统计（伤害、治疗、击杀、死亡等） | ~N 条/日志 | `fight_stats_id` BIGINT | `fight_id` → fights |
| `ei_report` | EI 报告元数据 + 文件路径 | 1 条/日志 | `report_id` BIGINT | `log_id` → logs (UNIQUE) |
| `ei_player` | EI 解析后的玩家 JSON（含 rotation_json） | ~50 条/日志 | `player_id` BIGINT | `log_id` → logs |
| `ei_target` | EI 解析后的目标 JSON | ~10 条/日志 | `target_id` BIGINT | `log_id` → logs |
| `ei_skill_map` | EI 技能映射 JSON（skillMap） | ~1200 条/日志 | `map_id` BIGINT | `log_id` → logs |
| `ei_phase` | EI 阶段 JSON（phases） | ~10 条/日志 | `phase_id` BIGINT | `log_id` → logs |

### 2.3 数据分层策略

| 层级 | 表/存储 | 说明 |
|------|---------|------|
| **L0 原始层** | `ei_report.log_data_path` / `graph_data_path` / `cr_data_path`（文件系统 gzip） | EI 解析完整数据，体积大，按需读取 |
| **L1 聚合层** | `fights`, `fight_stats` | 预计算常用聚合指标，API 直接读取 |
| **L2 EI 层** | `ei_player`, `ei_target`, `ei_skill_map`, `ei_phase` | EI 解析器输出的结构化 JSON，与前端 Schema 对齐 |

---

## 三、数据组装方案（API 层 → 前端）

### 3.1 组装原则

- **只读**：分析服务只查询数据库，不写数据库
- **聚合下沉**：重型计算（SUM/COUNT/GROUP BY）尽量在数据库层完成
- **大文件按需加载**：EI 完整数据（_logData/_graphData）仅在需要时从文件系统读取

### 3.2 各前端需求的组装逻辑

| 前端需求 | 数据源 | 组装方式 |
|---------|--------|---------|
| 战斗概览 | `fights` + `fight_stats` 聚合 | 直接读取单条/聚合记录 |
| 玩家列表 | `fight_stats` | 按 fight_id 查询，按伤害/治疗等排序 |
| 玩家详细统计 | `fight_stats` + `ei_player` | 聚合表取标量，EI 表取详细 JSON |
| 技能循环 | `ei_player.rotation_json` | 直接读取 rotation_json 字段 |
| 排行榜 | `fight_stats` | 按指定指标排序 |
| EI 完整报告 | `ei_report` + 文件系统 | summary_json 首屏加载，大文件按需 gzip 流式读取 |
| WvW 战斗报告 | `fights` + `fight_stats` | 聚合数据直接查询 |

### 3.3 性能优化要点

1. **`fight_stats` 查询必须带 `fight_id` 条件**：所有查询都使用 `WHERE fight_id = ?`，利用复合索引提升性能
2. **玩家统计使用单条 SQL 聚合**：避免 Python 循环大量数据
3. **EI 大文件 gzip 压缩存储**：压缩比约 10:1，显著减少磁盘占用和网络传输
4. **秒级聚合已预计算**：`fight_stats` 在解析时生成，API 直接读取

---

## 四、重新解析策略与事务处理

### 4.1 策略选择：先删除，后重新入库（Delete-Then-Insert）

**不采用 UPDATE 的原因**：
- 派生数据量可能变化（不同版本解析器产出的统计项不同）
- 旧数据与新数据可能行数不一致，UPDATE 无法处理行数变化
- EI 文件需整体替换，无法增量更新

**采用 Delete-Then-Insert 的优势**：
- 逻辑简单，无数据残留
- 性能更好（批量 DELETE + 批量 INSERT）
- 天然支持行数变化
- 文件系统侧同步替换 gzip 文件

### 4.2 事务边界设计

```
[SQLAlchemy Session]          [PyMySQL Connection]
     │                               │
     ├─ 更新 log.parse_status = 'parsing' ─┤
     │                               │
     │                    BEGIN TRANSACTION
     │                               │
     │                    DELETE FROM fight_stats WHERE fight_id IN (...)
     │                    DELETE FROM fights WHERE log_id = ?
     │                    DELETE FROM ei_player WHERE log_id = ?
     │                    DELETE FROM ei_target WHERE log_id = ?
     │                    DELETE FROM ei_skill_map WHERE log_id = ?
     │                    DELETE FROM ei_phase WHERE log_id = ?
     │                    DELETE FROM ei_report WHERE log_id = ?
     │                               │
     │                    INSERT INTO fights ...
     │                    INSERT INTO fight_stats ... (batch)
     │                    INSERT INTO ei_report ...
     │                    INSERT INTO ei_player ... (batch)
     │                    INSERT INTO ei_target ... (batch)
     │                    INSERT INTO ei_skill_map ... (batch)
     │                    INSERT INTO ei_phase ... (batch)
     │                               │
     │                    写入文件系统 (gzip)
     │                               │
     │                    COMMIT / ROLLBACK
     │                               │
     ├─ 更新 log.parse_status = 'completed' ─┤
     │                    (或 'failed')
     │                               │
```

### 4.3 事务一致性说明

- **数据层原子性**：解析导入在单个数据库 transaction 内完成所有 DELETE 和 INSERT。若任何一步失败，整个事务回滚，旧数据不会被删除。
- **文件系统一致性**：gzip 文件在数据库事务提交后写入。若文件写入失败，需通过定时扫描或后台任务补偿。
- **状态层最终一致性**：`log.parse_status` 的更新通过 SQLAlchemy Session 独立提交。极端情况下（数据库事务成功但状态 commit 失败），可能出现数据已更新但状态仍为 `parsing` 的情况，可通过后台重试或定时扫描 `parsing` 超过 N 分钟的记录来解决。

### 4.4 重解析入口

```python
# 通过后台任务重新解析
POST /logs/{log_id}/parse           → parse_log_background() → 导入服务(overwrite=True)

# 或通过专用重解析接口
POST /logs/{log_id}/reparse         → 重解析服务
```

### 4.5 幂等性保证

- **SHA256 指纹**：`logs.file_sha256` 是文件唯一标识
- **去重逻辑**：导入服务先查 SHA256
- `overwrite=False` → 抛出重复文件错误，跳过导入
- `overwrite=True` → 触发原子性 Delete-Then-Insert

---

## 五、文件系统存储策略

### 5.1 EI 大文件存储路径

| 数据类型 | 文件路径示例 | 压缩格式 |
|---------|-------------|---------|
| _logData | `uploads/ei_reports/{log_id}/log_data.json.gz` | gzip |
| _graphData | `uploads/ei_reports/{log_id}/graph_data.json.gz` | gzip |
| _crData | `uploads/ei_reports/{log_id}/cr_data.json.gz` | gzip |

### 5.2 存储特点

- **高压缩比**：原始 JSON ~138MB → gzip 后 ~1.7MB（约 80:1）
- **流式读取**：API 直接返回 gzip 流，前端按需解压
- **生命周期管理**：删除报告时同步删除关联文件

---

## 六、与旧表体系的共存策略

当前项目处于新旧体系交替期：

| 体系 | 表 | API 路由 | 状态 |
|------|-----|---------|------|
| 旧体系 | `fights`, `fight_stats`, `fight_details`, `members` | `combat_analysis.py` (部分可用), `attendance.py`, `fights.py`, `members.py` | 维护中 |
| 新体系 | `ei_report`, `ei_*` | `ei_report.py`, `ei_analysis.py`, `wvw_report.py` | 推荐使用 |

**过渡建议**：
1. 新上传的文件通过 EI 导入服务写入 `ei_report` + 文件系统
2. 前端新功能优先调用 `/ei-report/*` 和 `/ei-analysis/*` 接口
3. WvW 通用统计继续从 `fights` / `fight_stats` 读取
4. 当所有前端功能完成迁移后，逐步评估旧表废弃策略
