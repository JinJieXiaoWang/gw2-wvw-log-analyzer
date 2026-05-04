# ZEVTC 数据库 Schema 设计文档

> **版本**: v3.0
> **日期**: 2026-05-05
> **更新说明**:
> - ZEVTC 原始数据体系已废弃，删除 7 个原始数据模型（evtc_header/agent/skill/event/player_instance/combat_meta/event_per_second）
> - 当前仅保留 EI 同步模型与核心聚合表
> - 更新为与实际模型完全一致

---

## 1. 设计概览

### 1.1 架构说明

本系统采用**双数据源架构**：

1. **EI JSON 同步层**：通过 dps.report API 或本地 EnhancedZevtcParser 解析 `.zevtc` 文件，将 Elite Insights 输出同步到 `ei_*` 表
2. **聚合统计层**：从 EI 数据提取核心战斗统计，存入 `fights` 和 `fight_stats` 表
3. **文件存储层**：原始 `.zevtc` 文件可选择保留（由 `KEEP_RAW_FILE_AFTER_PARSE` 控制）

> **重要变更**：v3.0 起，ZEVTC 原始二进制数据（Header/Agent/Skill/Event 等）不再存入数据库。原始 `.zevtc` 文件如需保留，以 gzip 文件形式存储于文件系统；解析完全依赖 EI 工具链。

### 1.2 Schema 表结构总览

| 层级 | 表名 | 说明 |
|------|------|------|
| **管理** | `evtc_log` | 日志实例主表（上传注册表） |
| **核心聚合** | `fights` | 战斗概览信息 |
| **核心聚合** | `fight_stats` | 玩家战斗统计数据 |
| **EI玩家** | `ei_player` | EI JSON players[] 同步 |
| **EI目标** | `ei_target` | EI JSON targets[] 同步 |
| **EI技能** | `ei_skill_map` | EI JSON skillMap 同步 |
| **EI阶段** | `ei_phase` | EI JSON phases[] 同步 |
| **EI报告** | `ei_report` | HTML 导入的完整 EI 数据 |
| **成员** | `members` | 玩家账号与角色映射 |
| **账号角色** | `account_characters` | 账号历史角色记录 |
| **系统** | `sys_user` | 系统用户 |
| **字典** | `sys_dict_*` | 枚举字典表 |

### 1.3 已废弃的表（v3.0 删除）

以下 7 个表已在 v3.0 中删除：

| 表名 | 废弃原因 |
|------|----------|
| `evtc_header` | ZEVTC 原始二进制 Header 不再存储 |
| `evtc_agent` | ZEVTC 原始 Agent 表不再存储 |
| `evtc_skill` | ZEVTC 原始 Skill 表不再存储 |
| `evtc_event` | ZEVTC 原始 Event 表不再存储（原最大表，648K 行/日志） |
| `evtc_player_instance` | Agent→instid 映射随原始体系废弃 |
| `evtc_combat_meta` | 原始战斗元数据由 EI 聚合替代 |
| `evtc_event_per_second` | 秒级聚合由 EI JSON 提供 |

---

## 2. 逐表详细设计

### 2.1 `evtc_log` — 日志实例主表

**设计目的**: 管理每次上传/解析的日志实例，作为所有子表的外键根。

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|---------|------|------|
| `log_id` | `BIGINT` | PK, AUTO_INCREMENT | 日志实例全局唯一ID |
| `log_uuid` | `CHAR(36)` | UNIQUE, NOT NULL | UUID v4，跨系统唯一标识 |
| `filename` | `VARCHAR(255)` | NOT NULL | 原始上传文件名 |
| `file_sha256` | `CHAR(64)` | UNIQUE, NOT NULL | 文件SHA-256指纹，用于去重判定 |
| `file_size_compressed` | `INT` | NOT NULL | zevtc压缩后大小(字节) |
| `file_size_raw` | `INT` | NOT NULL | evtc解压后大小(字节) |
| `file_path` | `VARCHAR(500)` | NULL | 文件存储路径 |
| `parse_status` | `ENUM(...)` | NOT NULL DEFAULT 'pending' | 解析状态: pending/parsing/completed/failed/partial |
| `parse_time_ms` | `INT` | NULL | 解析耗时(毫秒) |
| `dps_report_permalink` | `VARCHAR(500)` | NULL | dps.report 报告链接 |
| `upload_time` | `DATETIME(3)` | NOT NULL DEFAULT CURRENT_TIMESTAMP(3) | 上传时间 |
| `upload_ip` | `VARCHAR(50)` | NULL | 上传者IP地址 |
| `uploaded_by` | `INT` | FK → sys_user.id | 上传者ID |
| `parsed_at` | `DATETIME(3)` | NULL | 解析完成时间 |
| `error_message` | `TEXT` | NULL | 解析失败时的错误堆栈 |

**索引设计**:
- `idx_log_parse_status`: 快速筛选待解析/失败任务
- `idx_log_upload_time`: 时间范围查询
- `idx_log_file_sha256`: 去重判定
- `idx_log_filename`: 文件名查询
- `idx_log_uploader_id`: 按上传者查询

---

### 2.2 `fights` — 战斗概览表

**设计目的**: 存储从 EI JSON 提取的战斗概览信息。

| 字段名 | 数据类型 | 说明 |
|--------|---------|------|
| `id` | `BIGINT` | PK, 自增 |
| `log_id` | `BIGINT` | FK → evtc_log.log_id, CASCADE |
| `fight_name` | `VARCHAR(255)` | 战斗名称 |
| `duration_ms` | `INT` | 战斗时长(毫秒) |
| `duration_str` | `VARCHAR(50)` | 格式化时长 |
| `start_time` | `DATETIME(3)` | 战斗开始时间 |
| `end_time` | `DATETIME(3)` | 战斗结束时间 |
| `map_id` | `INT` | 地图ID |
| `map_name` | `VARCHAR(100)` | 地图名称 |
| `recorded_by` | `VARCHAR(100)` | 记录者角色名 |
| `recorded_account_by` | `VARCHAR(100)` | 记录者账号 |
| `elite_insights_version` | `VARCHAR(20)` | EI版本 |
| `arc_version` | `VARCHAR(50)` | ArcDPS版本 |
| `gw2_build` | `INT` | GW2构建版本 |
| `success` | `BOOLEAN` | 战斗是否成功 |
| `is_cm` | `BOOLEAN` | 是否挑战模式 |
| `detailed_wv_w` | `BOOLEAN` | 是否详细WvW |
| `player_count` | `INT` | 玩家数量 |
| `target_count` | `INT` | 目标数量 |
| `total_damage` | `BIGINT` | 总伤害 |
| `created_at` | `DATETIME` | 创建时间 |

---

### 2.3 `fight_stats` — 玩家战斗统计表

**设计目的**: 存储每个玩家在每场战斗中的核心统计数据。

| 字段名 | 数据类型 | 说明 |
|--------|---------|------|
| `id` | `BIGINT` | PK, 自增 |
| `fight_id` | `BIGINT` | FK → fights.id, CASCADE |
| `member_id` | `BIGINT` | FK → members.id |
| `account_name` | `VARCHAR(100)` | 玩家账号 |
| `character_name` | `VARCHAR(100)` | 角色名 |
| `profession` | `VARCHAR(50)` | 职业/专精 |
| `group_id` | `SMALLINT` | 小队编号 |
| `damage` | `BIGINT` | 总伤害 |
| `power_damage` | `BIGINT` | 直伤 |
| `condi_damage` | `BIGINT` | 症状伤害 |
| `dps` | `INT` | 秒伤 |
| `power_dps` | `INT` | 直伤DPS |
| `condi_dps` | `INT` | 症状DPS |
| `breakbar_damage` | `BIGINT` | 破盾伤害 |
| `critical_rate` | `FLOAT` | 暴击率 |
| `flanking_rate` | `FLOAT` | 侧击率 |
| `glance_rate` | `FLOAT` | 浅击率 |
| `damage_taken` | `BIGINT` | 承受伤害 |
| `down_count` | `INT` | 倒地次数 |
| `death_count` | `INT` | 死亡次数 |
| `kills` | `INT` | 击杀数 |
| `downed` | `INT` | 击倒数 |
| `boon_strips` | `INT` | 增益移除数 |
| `condi_cleanses` | `INT` | 症状清除数 |
| `resurrects` | `INT` | 复活次数 |
| `healing` | `BIGINT` | 治疗量 |
| `time_in_combat` | `INT` | 战斗时间(毫秒) |
| `created_at` | `DATETIME` | 创建时间 |

---

### 2.4 `ei_player` — EI 玩家同步表

**设计目的**: 1:1 同步 EI JSON 的 `players[]` 数组，以 JSON 列保留原始嵌套结构。

| 字段名 | 数据类型 | 说明 |
|--------|---------|------|
| `player_id` | `BIGINT` | PK, 自增 |
| `log_id` | `BIGINT` | FK → evtc_log.log_id, CASCADE |
| `agent_index` | `INT` | 关联 agent 索引（历史兼容） |
| `account` | `VARCHAR(100)` | 玩家账户名 |
| `character_name` | `VARCHAR(100)` | 角色名称 |
| `profession` | `VARCHAR(50)` | 职业 |
| `group_id` | `SMALLINT` | 小队编号 |
| `has_commander_tag` | `SMALLINT` | 是否有指挥官标记 |
| `is_fake` | `SMALLINT` | 是否为假玩家 |
| `weapons_json` | `JSON` | 武器配置 |
| `consumables_json` | `JSON` | 食物与扳手 |
| `dps_all_json` | `JSON` | dpsAll 数组 |
| `stats_all_json` | `JSON` | statsAll 数组 |
| `defenses_json` | `JSON` | defenses 数组 |
| `support_json` | `JSON` | support 数组 |
| `buff_uptimes_json` | `JSON` | buffUptimes 数组 |
| `rotation_json` | `JSON` | rotation 数组 |
| `death_recap_json` | `JSON` | deathRecap 数组 |

**索引**:
- `uk_log_agent_ei`: (log_id, agent_index) UNIQUE
- `idx_profession`: profession

---

### 2.5 `ei_target` — EI 目标同步表

**设计目的**: 同步 EI JSON 的 `targets[]` 数组。

| 字段名 | 数据类型 | 说明 |
|--------|---------|------|
| `target_id` | `BIGINT` | PK, 自增 |
| `log_id` | `BIGINT` | FK → evtc_log.log_id, CASCADE |
| `agent_index` | `INT` | 关联 agent 索引 |
| `name` | `VARCHAR(100)` | 目标名称 |
| `enemy_player` | `SMALLINT` | 是否为敌方玩家 |
| `total_health` | `BIGINT` | 总生命值 |
| `final_health` | `BIGINT` | 最终生命值 |
| `health_percent_burned` | `INT` | 生命燃烧百分比 |
| `dps_all_json` | `JSON` | dpsAll 数组 |
| `defenses_json` | `JSON` | defenses 数组 |

---

### 2.6 `ei_skill_map` — EI 技能映射表

**设计目的**: 同步 EI JSON 的 `skillMap` 对象。

| 字段名 | 数据类型 | 说明 |
|--------|---------|------|
| `map_id` | `BIGINT` | PK, 自增 |
| `log_id` | `BIGINT` | FK → evtc_log.log_id, CASCADE |
| `skill_key` | `VARCHAR(20)` | JSON中的技能键 (s12345) |
| `gw2_skill_id` | `INT` | GW2官方技能ID |
| `name` | `VARCHAR(100)` | 技能名称 |
| `auto_attack` | `SMALLINT` | 是否为自动攻击 |
| `can_crit` | `SMALLINT` | 是否可暴击 |
| `is_swap` | `SMALLINT` | 是否为武器切换 |
| `is_instant_cast` | `SMALLINT` | 是否为瞬发 |
| `is_trait_proc` | `SMALLINT` | 是否为特性触发 |
| `icon` | `VARCHAR(500)` | 技能图标URL |

---

### 2.7 `ei_phase` — EI 战斗阶段表

**设计目的**: 同步 EI JSON 的 `phases[]` 数组。

| 字段名 | 数据类型 | 说明 |
|--------|---------|------|
| `phase_id` | `BIGINT` | PK, 自增 |
| `log_id` | `BIGINT` | FK → evtc_log.log_id, CASCADE |
| `phase_index` | `INT` | 阶段索引 |
| `name` | `VARCHAR(100)` | 阶段名称 |
| `start_ms` | `INT` | 阶段开始时间(毫秒) |
| `end_ms` | `INT` | 阶段结束时间(毫秒) |
| `breakbar_phase` | `SMALLINT` | 是否为破蔑视阶段 |
| `targets_json` | `JSON` | 目标信息JSON |

---

### 2.8 `ei_report` — EI 完整报告表

**设计目的**: 存储从 dps.report 或 HTML 导入的完整 EI 数据。

| 字段名 | 数据类型 | 说明 |
|--------|---------|------|
| `id` | `BIGINT` | PK, 自增 |
| `log_id` | `BIGINT` | FK → evtc_log.log_id, CASCADE |
| `permalink` | `VARCHAR(500)` | dps.report 链接 |
| `json_url` | `VARCHAR(500)` | JSON 数据链接 |
| `html_url` | `VARCHAR(500)` | HTML 报告链接 |
| `duration_ms` | `INT` | 战斗时长 |
| `elite_insights_version` | `VARCHAR(20)` | EI版本 |
| `fight_name` | `VARCHAR(255)` | 战斗名称 |
| `recorded_by` | `VARCHAR(100)` | 记录者 |
| `recorded_account_by` | `VARCHAR(100)` | 记录者账号 |
| `success` | `BOOLEAN` | 是否成功 |
| `summary_json` | `JSON` | 摘要数据 |
| `created_at` | `DATETIME` | 创建时间 |

---

## 3. 数据流架构

### 3.1 解析流程

```
用户上传 .zevtc
    │
    ▼
┌─────────────────────────────────────────────────────┐
│ Step 1: 文件预检                                      │
│   - 校验文件大小、计算 SHA-256                        │
│   - 查询 evtc_log 去重                                │
└─────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────┐
│ Step 2: 优先调用 dps.report API                       │
│   - 上传 .zevtc 到 dps.report                         │
│   - 获取 EI JSON 和 permalink                         │
│   - 成功 → 直接同步到 ei_* 表                         │
│   - 失败 → 降级到本地解析                             │
└─────────────────────────────────────────────────────┘
    │
    ▼ (降级路径)
┌─────────────────────────────────────────────────────┐
│ Step 3: 本地 EnhancedZevtcParser 解析                 │
│   - 解析 .zevtc 二进制文件                            │
│   - 输出 EI 兼容 JSON                                 │
└─────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────┐
│ Step 4: 数据同步                                      │
│   - EI JSON → ei_player / ei_target / ei_skill_map   │
│   - EI JSON → ei_phase                               │
│   - 提取聚合数据 → fights + fight_stats               │
└─────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────┐
│ Step 5: 文件管理                                      │
│   - KEEP_RAW_FILE_AFTER_PARSE=True: 保留 gzip 文件    │
│   - KEEP_RAW_FILE_AFTER_PARSE=False: 删除原始文件     │
└─────────────────────────────────────────────────────┘
```

### 3.2 查询路径

```
前端请求战斗详情
    │
    ▼
┌─────────────────────────────────────────────────────┐
│ 统一数据服务 (app/services/ei/unified_service.py)     │
│                                                      │
│  策略1: 优先检查 ei_report（HTML导入的完整数据）      │
│     └── 有数据 → 直接返回完整 EI 格式                 │
│                                                      │
│  策略2: 从 ei_player/ei_target/ei_phase 组装         │
│     └── 有同步数据 → 组装为 EI 格式返回               │
│                                                      │
│  策略3: 无数据 → 返回空或触发重新解析                 │
└─────────────────────────────────────────────────────┘
```

---

## 4. 数据完整性保障

### 4.1 外键级联

```
evtc_log (根表)
  ├── fights (1:N, CASCADE DELETE)
  │   └── fight_stats (1:N, CASCADE DELETE)
  ├── ei_player (1:N, CASCADE DELETE)
  ├── ei_target (1:N, CASCADE DELETE)
  ├── ei_skill_map (1:N, CASCADE DELETE)
  ├── ei_phase (1:N, CASCADE DELETE)
  └── ei_report (1:1, CASCADE DELETE)
```

**清理一条日志**: `DELETE FROM evtc_log WHERE log_id = X`，所有子表数据自动级联删除。

### 4.2 唯一约束

| 表 | 唯一约束 | 目的 |
|----|----------|------|
| `evtc_log` | `file_sha256` | 防止同一文件重复导入 |
| `evtc_log` | `log_uuid` | 全局唯一标识 |
| `ei_player` | `(log_id, agent_index)` | 每日志每 agent 唯一 |
| `ei_target` | `(log_id, agent_index)` | 每日志每 target 唯一 |
| `ei_skill_map` | `(log_id, skill_key)` | 每日志每技能唯一 |
| `ei_phase` | `(log_id, phase_index)` | 每日志每阶段唯一 |

### 4.3 事务包裹

```python
# 单条日志导入事务示例
try:
    db.begin()
    # 1. 插入/更新 evtc_log
    # 2. 插入 fights
    # 3. 批量插入 fight_stats
    # 4. 批量插入 ei_player / ei_target / ei_skill_map / ei_phase
    db.commit()
except Exception:
    db.rollback()
    raise
```

---

## 5. 与 EI JSON 的数据映射

### 5.1 EI JSON → 数据库字段映射

| EI JSON 路径 | 数据库表 | 字段/处理方式 |
|-------------|---------|-------------|
| `eliteInsightsVersion` | `fights` | `elite_insights_version` |
| `fightName` | `fights` | `fight_name` |
| `durationMS` | `fights` | `duration_ms` |
| `recordedBy` | `fights` | `recorded_by` |
| `recordedAccountBy` | `fights` | `recorded_account_by` |
| `players[]` | `ei_player` | 每元素一行，嵌套 JSON 列存储 |
| `players[i].account` | `ei_player` | `account` |
| `players[i].name` | `ei_player` | `character_name` |
| `players[i].profession` | `ei_player` | `profession` |
| `players[i].dpsAll` | `ei_player` | `dps_all_json` (JSON) |
| `players[i].statsAll` | `ei_player` | `stats_all_json` (JSON) |
| `players[i].defenses` | `ei_player` | `defenses_json` (JSON) |
| `players[i].support` | `ei_player` | `support_json` (JSON) |
| `players[i].buffUptimes` | `ei_player` | `buff_uptimes_json` (JSON) |
| `players[i].rotation` | `ei_player` | `rotation_json` (JSON) |
| `targets[]` | `ei_target` | 每元素一行 |
| `skillMap` | `ei_skill_map` | 每键值对一行 |
| `phases[]` | `ei_phase` | 每元素一行 |

### 5.2 聚合统计提取

`fights` 和 `fight_stats` 的数据从 `ei_player` 的 JSON 列中提取：

```python
# 示例：从 ei_player.dps_all_json 提取 DPS
dps_all = json.loads(ei_player.dps_all_json)
damage = dps_all[0]["damage"]
duration_sec = fight.duration_ms / 1000
dps = damage / duration_sec
```

---

## 6. 性能优化设计

### 6.1 索引策略

- `evtc_log.file_sha256`: 去重查询（UNIQUE 索引）
- `evtc_log.parse_status`: 待处理任务筛选
- `fights.log_id`: 关联查询
- `fight_stats.fight_id`: 关联查询 + 排序
- `ei_player.log_id`: 关联查询
- `ei_player.profession`: 按职业筛选

### 6.2 JSON 列查询优化

对于 MySQL 8.0+ / PostgreSQL，可使用 JSON 路径索引：

```sql
-- MySQL: 为 JSON 列创建虚拟列索引
ALTER TABLE ei_player ADD COLUMN dps INT 
    GENERATED ALWAYS AS (JSON_UNQUOTE(JSON_EXTRACT(dps_all_json, '$[0].dps'))) STORED;
CREATE INDEX idx_ei_player_dps ON ei_player(dps);

-- PostgreSQL: GIN 索引
CREATE INDEX idx_ei_player_dps_json ON ei_player USING GIN (dps_all_json);
```

### 6.3 批量插入

```python
# ei_player 批量插入示例
db.bulk_insert_mappings(EiPlayer, player_rows)
```

---

## 7. 文件清单

| 文件 | 路径 | 说明 |
|------|------|------|
| 模型定义 | `backend/app/models/zevtc_data.py` | ei_player/ei_target/ei_skill_map/ei_phase |
| 模型定义 | `backend/app/models/log.py` | evtc_log |
| 模型定义 | `backend/app/models/fight.py` | fights |
| 模型定义 | `backend/app/models/fight_stats.py` | fight_stats |
| EI Schema | `backend/app/schemas/ei_format.py` | EIFormatData / Player / Target / Phase |
| 统一服务 | `backend/app/services/ei/unified_service.py` | 自动选择最佳数据源 |
| 配置 | `backend/app/core/config.py` | 数据库配置集中管理 |
