# 数据库 Schema 设计

> **版本**: v3.0.0  
> **更新日期**: 2026-05-05  
> **数据库引擎**: SQLAlchemy 2.0  
> **支持数据库**: SQLite / MySQL 8.0+ / PostgreSQL 14+  
> **变更摘要**: 全面重写，与实际代码模型完全对齐；移除所有已废弃的 ZEVTC 原始数据表描述；新增 EI JSON 同步体系说明

---

## 历史版本

| 版本 | 日期 | 变更内容 | 责任人 |
|------|------|----------|--------|
| v3.0.0 | 2026-05-05 | 全面重写，与实际代码模型对齐；移除废弃 ZEVTC 原始表；新增 EI 同步体系 | 系统 |
| v2.0.0 | 2026-05-01 | 合并 Schema 设计与兼容性报告 | 系统 |
| v1.1.0 | 2026-05-01 | 补充 ZEVTC 兼容性分析 | System |
| v1.0.0 | 2026-05-01 | 初始 Schema 设计 | System |

---

## 一、架构概述

### 1.1 数据架构演进

当前系统经历了三个阶段的架构演进：

| 阶段 | 时间 | 数据流 | 核心表 |
|------|------|--------|--------|
| **阶段一** | 早期 | 自主解析 Pipeline → `evtc_*` 原始数据表 | `evtc_header`, `evtc_agent`, `evtc_skill`, `evtc_event`, `evtc_combat_meta`, `evtc_event_per_second`, `evtc_player_instance` |
| **阶段二** | 中期 | EI 数据同步 → `ei_*` 关系表 + 原始表并存 | 上述表 + `ei_player`, `ei_target`, `ei_skill_map`, `ei_phase` |
| **阶段三（当前）** | 2026-05 | dps.report API + 本地解析 → `fights`/`fight_stats`/`members` + EI JSON 同步 | 仅保留 `evtc_log`, `fights`, `fight_stats`, `members`, `account_characters`, `ei_*` 及系统表 |

> **⚠️ 关键发现：ZEVTC 原始数据体系已废弃**
> 
> `evtc_header`, `evtc_agent`, `evtc_skill`, `evtc_event`, `evtc_combat_meta`, `evtc_event_per_second`, `evtc_player_instance` 等 7 个原始数据模型已**全部删除**。当前系统不再直接存储二进制 EVTC 事件的逐条解析结果，而是采用以下两种策略：
> 1. **聚合表**: `fights` + `fight_stats` 存储每人每场战斗的核心统计指标
> 2. **EI JSON 同步**: `ei_player`, `ei_target`, `ei_skill_map`, `ei_phase` 存储 EI 解析后 JSON 的关键节点数据，`ei_report` 存储完整报告的元数据与文件路径

### 1.2 模型文件清单

`backend/app/models/` 目录下共 **13 个 `.py` 文件**，定义 **16 张表**（不含关联表）：

| 文件名 | 模型类 | 对应表名 | 说明 |
|--------|--------|----------|------|
| `log.py` | `Log` | `evtc_log` | 日志文件注册表（核心入口） |
| `fight.py` | `Fight` | `fights` | 战斗记录表 |
| `fight_stats.py` | `FightStats` | `fight_stats` | 战斗统计表（每人每场战斗一条） |
| `member.py` | `Member` | `members` | 成员表（账号维度） |
| `account_character.py` | `AccountCharacter` | `account_characters` | 账号角色映射表 |
| `zevtc_data.py` | `EiPlayer` | `ei_player` | EI 玩家数据 |
| `zevtc_data.py` | `EiTarget` | `ei_target` | EI 目标数据 |
| `zevtc_data.py` | `EiSkillMap` | `ei_skill_map` | EI 技能映射 |
| `zevtc_data.py` | `EiPhase` | `ei_phase` | EI 战斗阶段 |
| `sys_user.py` | `SysUser` | `sys_user` | 系统用户 |
| `storage.py` | `StorageCleanupRecord` | `storage_cleanup_records` | 存储清理记录 |
| `storage.py` | `StorageMonitorRecord` | `storage_monitor_records` | 存储监控记录 |
| `build.py` | `Build` | `builds` | Build 图书馆 |
| `dictionary.py` | `SysDictType` | `sys_dict_type` | 字典类型 |
| `dictionary.py` | `SysDictData` | `sys_dict_data` | 字典数据 |
| `ai_report.py` | `AIReport` | `ai_reports` | AI 分析报告 |
| `ei_report.py` | `EiReport` | `ei_report` | EI 完整报告存储 |
| `batch_parse.py` | `BatchParseTask` | `batch_parse_tasks` | 批量解析任务 |
| `batch_parse.py` | `BatchParseTaskItem` | `batch_parse_task_items` | 批量解析任务项 |

---

## 二、实体关系（ER）设计

### 2.1 核心关系图

```
┌─────────────────┐     1:N      ┌─────────────┐     1:N      ┌─────────────────┐
│    sys_user     │──────────────│  evtc_log   │──────────────│     fights      │
│   (系统用户)     │              │ (日志注册表)  │              │   (战斗记录)     │
│                 │◄─────────────│             │◄─────────────│                 │
└─────────────────┘   uploaded_by └──────┬──────┘   log_id     └────────┬────────┘
       ▲    ▲                           │                            │
       │    │                           │ 1:N                        │ 1:N
       │    │                    ┌──────┴──────┐              ┌──────┴──────┐
       │    │                    ▼             ▼              ▼             ▼
       │    │            ┌──────────┐  ┌────────────┐  ┌────────────┐  ┌──────────┐
       │    │            │ei_player │  │ ei_target  │  │ ei_report  │  │fight_stats│
       │    │            │(EI玩家)  │  │ (EI目标)   │  │(EI完整报告) │  │(战斗统计) │
       │    │            └──────────┘  └────────────┘  └────────────┘  └────┬─────┘
       │    │            ┌──────────┐  ┌────────────┐                       │
       │    │            │ei_skill_ │  │  ei_phase  │                       │ N:1
       │    │            │  map     │  │(EI战斗阶段)│                       ▼
       │    │            └──────────┘  └────────────┘                ┌─────────────┐
       │    │                                                         │   members   │
       │    │                                                         │  (成员账号)  │
       │    │                                                         └─────────────┘
       │    │
       │    │        ┌────────────────────┐      1:N      ┌─────────────────────────┐
       │    └────────│ batch_parse_tasks  │───────────────│ batch_parse_task_items  │
       │      created_by                    │              │                         │
       │                                     └─────────────│        log_id ──────────┼─► evtc_log
       │                                                   └─────────────────────────┘
       │
       └────────────────┐
            created_by  │
                        ▼
               ┌─────────────────┐
               │    ai_reports   │
               │  (AI分析报告)    │
               └─────────────────┘
```

### 2.2 关系汇总表

| 父表 | 子表 | 外键字段 | 级联策略 | 关系类型 |
|------|------|----------|----------|----------|
| `evtc_log` | `fights` | `log_id` | `all, delete-orphan` | 1:N |
| `evtc_log` | `ei_player` | `log_id` | `CASCADE` | 1:N |
| `evtc_log` | `ei_target` | `log_id` | `CASCADE` | 1:N |
| `evtc_log` | `ei_skill_map` | `log_id` | `CASCADE` | 1:N |
| `evtc_log` | `ei_phase` | `log_id` | `CASCADE` | 1:N |
| `evtc_log` | `ei_report` | `log_id` | `CASCADE` | 1:1 (unique) |
| `evtc_log` | `batch_parse_task_items` | `log_id` | — | 1:N (被引用) |
| `fights` | `fight_stats` | `fight_id` | `all, delete-orphan` | 1:N |
| `members` | `fight_stats` | `member_id` | — | 1:N |
| `sys_user` | `evtc_log` | `uploaded_by` | — | 1:N |
| `sys_user` | `ai_reports` | `created_by` | — | 1:N |
| `sys_user` | `batch_parse_tasks` | `created_by` | — | 1:N |
| `batch_parse_tasks` | `batch_parse_task_items` | `task_id` | `all, delete-orphan` | 1:N |

---

## 三、表结构详细说明

### 3.1 `evtc_log` — 日志文件注册表（核心入口）

**设计思路**: 作为整个系统的核心父表，负责文件上传、去重、解析生命周期跟踪。不直接存储任何解析后的业务数据，这些数据由子表独立维护。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| `log_id` | `BIGINT` | PK, AUTO_INCREMENT | 日志实例主键 |
| `log_uuid` | `CHAR(36)` | UNIQUE, NOT NULL | 全局唯一 UUID(v4) |
| `filename` | `VARCHAR(255)` | NOT NULL | 原始上传文件名 |
| `file_sha256` | `CHAR(64)` | UNIQUE, NOT NULL | 原始文件 SHA-256 指纹（去重用） |
| `file_size_compressed` | `INT` | NOT NULL | `.zevtc` 压缩后大小（字节） |
| `file_size_raw` | `INT` | NOT NULL | `.evtc` 解压后大小（字节） |
| `file_path` | `VARCHAR(500)` | NULLABLE | 文件存储路径 |
| `parse_status` | `ENUM('pending','parsing','completed','failed','partial')` | NOT NULL, DEFAULT 'pending' | 解析状态 |
| `parse_time_ms` | `INT` | NULLABLE | 解析耗时（毫秒） |
| `dps_report_permalink` | `VARCHAR(500)` | NULLABLE | dps.report 报告链接 |
| `parsed_at` | `DateTime(TZ)` | NULLABLE | 解析完成时间 |
| `error_message` | `TEXT` | NULLABLE | 解析失败时的错误信息 |
| `upload_time` | `DateTime(TZ)` | server_default=now() | 上传时间 |
| `upload_ip` | `VARCHAR(50)` | NULLABLE | 上传者 IP 地址 |
| `uploaded_by` | `INT` | FK → `sys_user.id` | 上传者 ID |

**索引**:
- `idx_log_parse_status` (`parse_status`)
- `idx_log_upload_time` (`upload_time`)
- `idx_log_file_sha256` (`file_sha256`)
- `idx_log_filename` (`filename`)
- `idx_log_uploader_id` (`uploaded_by`)

**关联关系**:
- `uploader` → `SysUser` (N:1)
- `fights` → `Fight` (1:N, cascade="all, delete-orphan")

---

### 3.2 `fights` — 战斗记录表

**设计思路**: 每场战斗一条记录，从 `evtc_log` 派生。存储战斗的基础元数据、时间范围、场地信息和总体统计。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| `id` | `INT` | PK, AUTO_INCREMENT | 战斗记录 ID |
| `log_id` | `BIGINT` | FK → `evtc_log.log_id`, NOT NULL | 关联日志 ID |
| `start_time` | `DateTime(TZ)` | NOT NULL | 战斗开始时间 |
| `end_time` | `DateTime(TZ)` | NULLABLE | 战斗结束时间 |
| `duration_sec` | `INT` | DEFAULT 0 | 战斗时长（秒） |
| `duration_ms` | `BIGINT` | DEFAULT 0 | 战斗时长（毫秒） |
| `map_name` | `VARCHAR(100)` | NULLABLE | 地图名称 |
| `server_name` | `VARCHAR(100)` | NULLABLE | 服务器名称 |
| `recorded_by` | `VARCHAR(100)` | NULLABLE | 录制者角色名 |
| `recorded_account` | `VARCHAR(100)` | NULLABLE | 录制者账号 |
| `total_damage` | `BIGINT` | DEFAULT 0 | 总伤害量 |
| `total_healing` | `BIGINT` | DEFAULT 0 | 总治疗量 |
| `kill_count` | `INT` | DEFAULT 0 | 击杀数 |
| `death_count` | `INT` | DEFAULT 0 | 死亡数 |
| `player_count` | `INT` | DEFAULT 0 | 玩家数量 |
| `is_ai_analyzed` | `BOOLEAN` | DEFAULT FALSE | 是否已完成 AI 分析 |
| `created_at` | `DateTime(TZ)` | server_default=now() | 记录创建时间 |

**索引**:
- `idx_fight_log_id` (`log_id`)
- `idx_fight_map_name` (`map_name`)
- `idx_fight_start_time` (`start_time`)

**关联关系**:
- `log` → `Log` (N:1)
- `fight_stats` → `FightStats` (1:N, cascade="all, delete-orphan")

---

### 3.3 `fight_stats` — 战斗统计表

**设计思路**: 每人每场战斗一条记录（约 50 行/日志）。核心聚合表，直接支撑 DPS 排行榜、生存能力分析、Buff 覆盖率查询等高频场景。身份信息冗余存储以避免 JOIN。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| `id` | `INT` | PK, AUTO_INCREMENT | 主键 ID |
| `fight_id` | `INT` | FK → `fights.id`, NOT NULL | 关联战斗记录 ID |
| `member_id` | `INT` | FK → `members.id`, NOT NULL | 关联成员记录 ID |
| `account` | `VARCHAR(100)` | NOT NULL | 玩家账户名（冗余） |
| `character_name` | `VARCHAR(100)` | NULLABLE | 角色名称（冗余） |
| `profession` | `VARCHAR(50)` | NULLABLE | 职业（冗余） |
| `group_id` | `INT` | DEFAULT 1 | 小队编号（1-5） |
| `team_id` | `INT` | DEFAULT 0 | 队伍 ID（0=蓝队，1=红队，2=绿队） |
| `has_commander_tag` | `INT` | DEFAULT 0 | 是否有指挥官标记（1=是，0=否） |
| `damage` | `BIGINT` | DEFAULT 0 | 总伤害量 |
| `dps` | `INT` | DEFAULT 0 | 每秒伤害 |
| `power_damage` | `BIGINT` | DEFAULT 0 | 直伤伤害 |
| `condi_damage` | `BIGINT` | DEFAULT 0 | 症状伤害 |
| `breakbar_damage` | `BIGINT` | DEFAULT 0 | 破蔑视伤害 |
| `healing` | `BIGINT` | DEFAULT 0 | 治疗量 |
| `critical_rate` | `NUMERIC(5,2)` | DEFAULT 0 | 暴击率（百分比） |
| `flanking_rate` | `NUMERIC(5,2)` | DEFAULT 0 | 背击率（百分比） |
| `glance_rate` | `NUMERIC(5,2)` | DEFAULT 0 | 偏斜率（百分比） |
| `missed` | `INT` | DEFAULT 0 | 未命中次数 |
| `killed` | `INT` | DEFAULT 0 | 击杀敌人数量 |
| `downed` | `INT` | DEFAULT 0 | 击倒敌人数量 |
| `interrupts` | `INT` | DEFAULT 0 | 打断次数 |
| `swap_count` | `INT` | DEFAULT 0 | 切换目标次数 |
| `damage_taken` | `BIGINT` | DEFAULT 0 | 承受伤害量 |
| `blocked_count` | `INT` | DEFAULT 0 | 格挡次数 |
| `evaded_count` | `INT` | DEFAULT 0 | 闪避次数 |
| `dodge_count` | `INT` | DEFAULT 0 | 翻滚次数 |
| `down_count` | `INT` | DEFAULT 0 | 倒地次数 |
| `dead_count` | `INT` | DEFAULT 0 | 死亡次数 |
| `boon_strips` | `INT` | DEFAULT 0 | 移除增益次数 |
| `condition_cleanses` | `INT` | DEFAULT 0 | 清除症状次数 |
| `resurrects` | `INT` | DEFAULT 0 | 复活队友次数 |
| `condi_cleanse_ally` | `INT` | DEFAULT 0 | 清除队友症状次数 |
| `boon_strips_ally` | `INT` | DEFAULT 0 | 移除队友增益次数 |
| `might_uptime` | `NUMERIC(5,2)` | DEFAULT 0 | 力量（Might）覆盖率 |
| `fury_uptime` | `NUMERIC(5,2)` | DEFAULT 0 | 狂怒（Fury）覆盖率 |
| `quickness_uptime` | `NUMERIC(5,2)` | DEFAULT 0 | 急速（Quickness）覆盖率 |
| `alacrity_uptime` | `NUMERIC(5,2)` | DEFAULT 0 | 敏捷（Alacrity）覆盖率 |
| `protection_uptime` | `NUMERIC(5,2)` | DEFAULT 0 | 保护（Protection）覆盖率 |
| `stability_uptime` | `NUMERIC(5,2)` | DEFAULT 0 | 稳定（Stability）覆盖率 |
| `ai_score` | `NUMERIC(5,2)` | DEFAULT 0 | AI 评分 |
| `score_grade` | `VARCHAR(10)` | DEFAULT '' | 评分等级（S/A/B/C/D） |

**索引**:
- `idx_fight_stats_fight_member` (`fight_id`, `member_id`)
- `idx_fight_stats_profession` (`profession`)
- `idx_fight_stats_dps` (`dps`)
- `idx_fight_stats_damage` (`damage`)

**关联关系**:
- `fight` → `Fight` (N:1)
- `member` → `Member` (N:1)

---

### 3.4 `members` — 成员表

**设计思路**: 仅保存账号维度（`account_name`），角色名、职业等详细信息请去 `account_characters` 表查询。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| `id` | `INT` | PK, AUTO_INCREMENT | 成员 ID |
| `account_name` | `VARCHAR(100)` | UNIQUE, NOT NULL, INDEX | 账号名称 |
| `guild_tag` | `VARCHAR(20)` | NULLABLE | 公会标签 |
| `join_date` | `DATE` | NULLABLE | 加入日期 |

**关联关系**:
- `fight_stats` → `FightStats` (1:N)

---

### 3.5 `account_characters` — 账号角色映射表

**设计思路**: 支持同一 `account_name` 对应多个 `character_name` 的映射关系，自动跟踪首次/末次出现日期和出现次数。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| `id` | `INT` | PK, AUTO_INCREMENT | 主键 ID |
| `account_name` | `VARCHAR(100)` | NOT NULL, INDEX | 账号名称 |
| `character_name` | `VARCHAR(100)` | NOT NULL, INDEX | 角色名称 |
| `profession` | `VARCHAR(50)` | NULLABLE | 职业 |
| `first_seen_date` | `DATE` | NOT NULL | 首次出现日期 |
| `last_seen_date` | `DATE` | NOT NULL | 末次出现日期 |
| `seen_count` | `INT` | DEFAULT 1 | 出现次数 |

**索引**:
- `uk_account_character` (`account_name`, `character_name`) — UNIQUE
- `idx_account_name` (`account_name`)
- `idx_character_name` (`character_name`)

---

### 3.6 EI JSON 同步表群（`zevtc_data.py`）

> 以下 4 张表存储从 Elite Insights JSON 同步的关键节点数据，用于在需要时重建详细分析视图，而不必每次都解析完整的 100MB+ JSON 文件。

#### `ei_player` — EI 玩家数据

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| `player_id` | `BIGINT` | PK, AUTO_INCREMENT | 主键 ID |
| `log_id` | `BIGINT` | FK → `evtc_log.log_id`, ON DELETE CASCADE, NOT NULL | 关联日志 ID |
| `agent_index` | `INT` | NULLABLE | 原始 agent 索引 |
| `account` | `VARCHAR(100)` | NULLABLE | 玩家账户名 |
| `character_name` | `VARCHAR(100)` | NOT NULL | 角色名称 |
| `profession` | `VARCHAR(50)` | NOT NULL | 职业 |
| `group_id` | `SMALLINT` | NULLABLE | 小队编号 |
| `has_commander_tag` | `SMALLINT` | DEFAULT 0 | 是否有指挥官标记 |
| `is_fake` | `SMALLINT` | DEFAULT 0 | 是否为假玩家（宠物、召唤物等） |
| `weapons_json` | `JSON` | NULLABLE | 武器配置 JSON |
| `consumables_json` | `JSON` | NULLABLE | 食物与扳手配置 JSON |
| `dps_all_json` | `JSON` | NULLABLE | `dpsAll` 数组 JSON |
| `stats_all_json` | `JSON` | NULLABLE | `statsAll` 数组 JSON |
| `defenses_json` | `JSON` | NULLABLE | `defenses` 数组 JSON |
| `support_json` | `JSON` | NULLABLE | `support` 数组 JSON |
| `buff_uptimes_json` | `JSON` | NULLABLE | `buffUptimes` 数组 JSON |
| `rotation_json` | `JSON` | NULLABLE | `rotation` 数组 JSON |
| `death_recap_json` | `JSON` | NULLABLE | `deathRecap` 数组 JSON |

**索引**:
- `uk_log_agent_ei` (`log_id`, `agent_index`) — UNIQUE
- `idx_profession` (`profession`)

#### `ei_target` — EI 目标数据

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| `target_id` | `BIGINT` | PK, AUTO_INCREMENT | 主键 ID |
| `log_id` | `BIGINT` | FK → `evtc_log.log_id`, ON DELETE CASCADE, NOT NULL | 关联日志 ID |
| `agent_index` | `INT` | NULLABLE | 原始 agent 索引 |
| `name` | `VARCHAR(100)` | NOT NULL | 目标名称 |
| `enemy_player` | `SMALLINT` | DEFAULT 0 | 是否为敌方玩家 |
| `total_health` | `BIGINT` | NULLABLE | 总生命值 |
| `final_health` | `BIGINT` | NULLABLE | 最终生命值 |
| `health_percent_burned` | `INT` | NULLABLE | 生命燃烧百分比 |
| `dps_all_json` | `JSON` | NULLABLE | `dpsAll` 数组 JSON |
| `defenses_json` | `JSON` | NULLABLE | `defenses` 数组 JSON |

**索引**:
- `uk_log_target_agent` (`log_id`, `agent_index`) — UNIQUE

#### `ei_skill_map` — EI 技能映射

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| `map_id` | `BIGINT` | PK, AUTO_INCREMENT | 主键 ID |
| `log_id` | `BIGINT` | FK → `evtc_log.log_id`, ON DELETE CASCADE, NOT NULL | 关联日志 ID |
| `skill_key` | `VARCHAR(20)` | NOT NULL | JSON 中的技能键（如 `s12345`） |
| `gw2_skill_id` | `INT` | NOT NULL | GW2 官方技能 ID |
| `name` | `VARCHAR(100)` | NULLABLE | 技能名称 |
| `auto_attack` | `SMALLINT` | DEFAULT 0 | 是否为自动攻击 |
| `can_crit` | `SMALLINT` | DEFAULT 0 | 是否可暴击 |
| `is_swap` | `SMALLINT` | DEFAULT 0 | 是否为武器切换 |
| `is_instant_cast` | `SMALLINT` | DEFAULT 0 | 是否为瞬发 |
| `is_trait_proc` | `SMALLINT` | DEFAULT 0 | 是否为特性触发 |
| `icon` | `VARCHAR(500)` | NULLABLE | 技能图标 URL |

**索引**:
- `uk_log_skill_key` (`log_id`, `skill_key`) — UNIQUE

#### `ei_phase` — EI 战斗阶段

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| `phase_id` | `BIGINT` | PK, AUTO_INCREMENT | 主键 ID |
| `log_id` | `BIGINT` | FK → `evtc_log.log_id`, ON DELETE CASCADE, NOT NULL | 关联日志 ID |
| `phase_index` | `INT` | NOT NULL | 阶段索引 |
| `name` | `VARCHAR(100)` | NOT NULL | 阶段名称 |
| `start_ms` | `INT` | NOT NULL | 阶段开始时间（毫秒） |
| `end_ms` | `INT` | NOT NULL | 阶段结束时间（毫秒） |
| `breakbar_phase` | `SMALLINT` | DEFAULT 0 | 是否为破蔑视阶段 |
| `targets_json` | `JSON` | NULLABLE | 目标信息 JSON |

**索引**:
- `uk_log_phase` (`log_id`, `phase_index`) — UNIQUE

---

### 3.7 `sys_user` — 系统用户

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| `id` | `INT` | PK, AUTO_INCREMENT, INDEX | 自增主键 |
| `username` | `VARCHAR(50)` | UNIQUE, NOT NULL, INDEX | 用户名 |
| `password_hash` | `VARCHAR(255)` | NOT NULL | 密码哈希 |
| `role` | `VARCHAR(20)` | NOT NULL, DEFAULT 'operator' | 角色：super_admin/operator/user/guest |
| `is_active` | `BOOLEAN` | DEFAULT TRUE | 是否启用 |
| `is_predefined` | `BOOLEAN` | NOT NULL, DEFAULT FALSE | 是否预定义用户 |
| `email` | `VARCHAR(100)` | NULLABLE | 邮箱 |
| `created_at` | `DateTime(TZ)` | server_default=now() | 创建时间 |
| `last_login` | `DateTime(TZ)` | NULLABLE | 最后登录时间 |
| `token_version` | `INT` | NOT NULL, DEFAULT 0 | 令牌版本（密码修改后使旧 token 失效） |

---

### 3.8 `ei_report` — EI 完整报告存储

**设计思路**: 由于原始 JSON 体积巨大（可达 100MB+），采用"元数据存 DB + 大文件存磁盘"的混合策略。`summary_json` 存储摘要数据用于快速查询；`log_data_path` / `graph_data_path` / `cr_data_path` 指向 gzip 压缩后的完整 JSON 文件。

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| `report_id` | `BIGINT` | PK, AUTO_INCREMENT | 自增主键 |
| `log_id` | `BIGINT` | FK → `evtc_log.log_id`, ON DELETE CASCADE, NOT NULL, UNIQUE | 关联日志（1:1） |
| `report_type` | `VARCHAR(50)` | NOT NULL, DEFAULT 'detailed_wvw' | 报告类型 |
| `ei_version` | `VARCHAR(50)` | NULLABLE | EI 解析器版本 |
| `summary_json` | `JSON` | NULLABLE | EI 报告摘要数据（players/targets/phases 基础信息） |
| `log_data_path` | `VARCHAR(500)` | NULLABLE | 完整 `_logData` JSON 压缩文件路径 |
| `graph_data_path` | `VARCHAR(500)` | NULLABLE | 完整 `_graphData` JSON 压缩文件路径 |
| `cr_data_path` | `VARCHAR(500)` | NULLABLE | Combat Replay 数据压缩文件路径 |
| `log_name` | `VARCHAR(200)` | NULLABLE | 战斗名称 |
| `duration_ms` | `BIGINT` | NULLABLE | 战斗时长（毫秒） |
| `player_count` | `BIGINT` | NULLABLE | 玩家数量 |
| `target_count` | `BIGINT` | NULLABLE | 目标数量 |
| `success` | `VARCHAR(10)` | NULLABLE | 是否成功 |
| `recorded_by` | `VARCHAR(100)` | NULLABLE | 录制者角色名 |
| `recorded_account_by` | `VARCHAR(100)` | NULLABLE | 录制者账号 |
| `map_id` | `BIGINT` | NULLABLE | 地图 ID |
| `region` | `VARCHAR(50)` | NULLABLE | 服务器区域 |
| `wvw` | `VARCHAR(10)` | NULLABLE | 是否为 WvW |
| `created_at` | `DateTime(TZ)` | server_default=now() | 记录创建时间 |
| `updated_at` | `DateTime(TZ)` | server_default=now(), onupdate=now() | 记录更新时间 |

**索引**:
- `idx_ei_report_type` (`report_type`)
- `idx_ei_report_map` (`map_id`)

---

### 3.9 `ai_reports` — AI 分析报告

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| `id` | `INT` | PK, AUTO_INCREMENT, INDEX | 自增主键 |
| `report_type` | `VARCHAR(50)` | NOT NULL | 报告类型 |
| `target_type` | `VARCHAR(50)` | NOT NULL | 目标类型 |
| `target_id` | `INT` | NOT NULL | 目标 ID |
| `content` | `TEXT` | NOT NULL | 报告内容 |
| `summary` | `TEXT` | NULLABLE | 报告摘要 |
| `ai_score` | `FLOAT` | NULLABLE | AI 评分 |
| `created_by` | `INT` | FK → `sys_user.id`, NULLABLE | 创建者 ID |
| `created_at` | `DateTime(TZ)` | server_default=now() | 创建时间 |
| `is_public` | `INT` | DEFAULT 1 | 是否公开 |
| `is_deleted` | `INT` | DEFAULT 0 | 是否删除 |

---

### 3.10 `batch_parse_tasks` / `batch_parse_task_items` — 批量解析任务

#### `batch_parse_tasks`

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| `id` | `INT` | PK, AUTO_INCREMENT, INDEX | 自增主键 |
| `task_name` | `VARCHAR(255)` | NULLABLE | 任务名称 |
| `status` | `VARCHAR(20)` | DEFAULT 'pending' | 状态：pending/processing/completed/failed/partial |
| `total_count` | `INT` | DEFAULT 0 | 总数量 |
| `processed_count` | `INT` | DEFAULT 0 | 已处理数量 |
| `success_count` | `INT` | DEFAULT 0 | 成功数量 |
| `failed_count` | `INT` | DEFAULT 0 | 失败数量 |
| `created_at` | `DateTime(TZ)` | server_default=now() | 创建时间 |
| `started_at` | `DateTime(TZ)` | NULLABLE | 开始时间 |
| `completed_at` | `DateTime(TZ)` | NULLABLE | 完成时间 |
| `created_by` | `INT` | FK → `sys_user.id`, NULLABLE | 创建者 ID |
| `error_message` | `TEXT` | NULLABLE | 错误信息 |
| `log_ids` | `JSON` | NULLABLE | 日志 ID 列表 |

**索引**:
- `idx_batch_task_status` (`status`)
- `idx_batch_task_created` (`created_at`)

**关联关系**:
- `creator` → `SysUser` (N:1)
- `items` → `BatchParseTaskItem` (1:N, cascade="all, delete-orphan")

#### `batch_parse_task_items`

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| `id` | `INT` | PK, AUTO_INCREMENT, INDEX | 自增主键 |
| `task_id` | `INT` | FK → `batch_parse_tasks.id`, NOT NULL | 关联任务 ID |
| `log_id` | `BIGINT` | FK → `evtc_log.log_id`, NOT NULL | 关联日志 ID |
| `status` | `VARCHAR(20)` | DEFAULT 'pending' | 状态：pending/processing/completed/failed/retrying |
| `started_at` | `DateTime(TZ)` | NULLABLE | 开始时间 |
| `completed_at` | `DateTime(TZ)` | NULLABLE | 完成时间 |
| `error_message` | `TEXT` | NULLABLE | 错误信息 |
| `retry_count` | `INT` | DEFAULT 0 | 已重试次数 |
| `max_retries` | `INT` | DEFAULT 3 | 最大重试次数 |
| `next_retry_at` | `DateTime(TZ)` | NULLABLE | 下次重试时间 |
| `error_code` | `VARCHAR(50)` | NULLABLE | 错误代码：429/timeout/parse_error/unknown |

**索引**:
- `idx_batch_item_task` (`task_id`)
- `idx_batch_item_log` (`log_id`)
- `idx_batch_item_status_retry` (`status`, `next_retry_at`)

**关联关系**:
- `task` → `BatchParseTask` (N:1)
- `log` → `Log` (N:1)

---

### 3.11 `builds` — Build 图书馆

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| `id` | `INT` | PK, AUTO_INCREMENT | 自增主键 |
| `slug` | `VARCHAR(100)` | UNIQUE, NOT NULL, INDEX | URL 标识 |
| `title` | `VARCHAR(100)` | NOT NULL | Build 标题 |
| `profession` | `VARCHAR(50)` | NOT NULL, INDEX | 职业名称 |
| `profession_color` | `VARCHAR(20)` | NULLABLE | 职业颜色（HEX） |
| `elite_spec` | `VARCHAR(50)` | NULLABLE | 精英特长 |
| `role` | `VARCHAR(20)` | NOT NULL, INDEX | 主角色：dps/support |
| `sub_roles` | `JSON` | DEFAULT `[]` | 子角色列表：boon/heal/tank/cc |
| `armor_type` | `VARCHAR(100)` | NULLABLE | 护甲类型 |
| `weapons` | `JSON` | DEFAULT `[]` | 武器配置 |
| `relic` | `VARCHAR(100)` | NULLABLE | Relic |
| `rune` | `VARCHAR(100)` | NULLABLE | 符文 |
| `food` | `VARCHAR(100)` | NULLABLE | 食物 |
| `wrench` | `VARCHAR(100)` | NULLABLE | 扳手（通用技能） |
| `infusion` | `VARCHAR(100)` | NULLABLE | 灌注 |
| `attr_requirements` | `JSON` | DEFAULT `[]` | 属性要求列表 |
| `bd_code` | `VARCHAR(255)` | NOT NULL | GW2 Build Code |
| `trait_lines` | `JSON` | DEFAULT `[]` | 特性线配置 |
| `rotation_commands` | `JSON` | DEFAULT `[]` | 循环指令 |
| `mechanics` | `JSON` | DEFAULT `[]` | 机制说明 |
| `videos` | `JSON` | DEFAULT `[]` | 视频链接 |
| `author` | `VARCHAR(50)` | NOT NULL | 作者 |
| `word_count` | `INT` | DEFAULT 0 | 字数统计 |
| `is_meta` | `BOOLEAN` | DEFAULT FALSE | 是否推荐配置 |
| `created_at` | `DateTime(TZ)` | server_default=now() | 创建时间 |
| `updated_at` | `DateTime(TZ)` | server_default=now(), onupdate=now() | 更新时间 |

---

### 3.12 `sys_dict_type` / `sys_dict_data` — 字典表

#### `sys_dict_type`

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| `dict_id` | `INT` | PK, AUTO_INCREMENT, INDEX | 自增主键 |
| `dict_type` | `VARCHAR(100)` | UNIQUE, NOT NULL, INDEX | 字典类型编码 |
| `dict_name` | `VARCHAR(200)` | NOT NULL | 字典类型名称 |
| `status` | `INT` | NOT NULL, DEFAULT 0 | 状态：0-启用，1-禁用 |
| `sort_order` | `INT` | NOT NULL, DEFAULT 0 | 排序顺序 |
| `remark` | `TEXT` | NULLABLE | 备注说明 |
| `is_system` | `INT` | NOT NULL, DEFAULT 0 | 是否系统预置：0-否，1-是 |

#### `sys_dict_data`

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| `dict_code` | `INT` | PK, AUTO_INCREMENT, INDEX | 自增主键 |
| `dict_sort` | `INT` | NOT NULL, DEFAULT 0 | 排序顺序 |
| `dict_label` | `VARCHAR(200)` | NOT NULL | 字典标签 |
| `dict_value` | `VARCHAR(200)` | NOT NULL | 字典值 |
| `dict_type` | `VARCHAR(100)` | NOT NULL, INDEX | 字典类型 |
| `data_type` | `VARCHAR(100)` | NULLABLE | 数据类型 |
| `css_class` | `VARCHAR(200)` | NULLABLE | CSS 样式类/颜色值 |
| `list_class` | `VARCHAR(100)` | NULLABLE | 列表样式类 |
| `is_default` | `INT` | NOT NULL, DEFAULT 0 | 是否默认值：0-否，1-是 |
| `status` | `INT` | NOT NULL, DEFAULT 0 | 状态：0-启用，1-禁用 |
| `remark` | `TEXT` | NULLABLE | 备注说明 |

**约束**:
- `uk_dict_type_value`: (`dict_type`, `dict_value`) — UNIQUE

---

### 3.13 `storage_cleanup_records` — 存储清理记录

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| `id` | `INT` | PK, AUTO_INCREMENT, INDEX | 自增主键 |
| `cleanup_type` | `VARCHAR(50)` | NOT NULL | 清理类型：manual/auto/scheduled |
| `start_time` | `DateTime(TZ)` | server_default=now() | 开始时间 |
| `end_time` | `DateTime(TZ)` | NULLABLE | 结束时间 |
| `files_deleted` | `INT` | DEFAULT 0 | 删除文件数 |
| `space_freed` | `FLOAT` | DEFAULT 0.0 | 释放空间（字节） |
| `status` | `VARCHAR(20)` | DEFAULT 'in_progress' | 状态：in_progress/completed/failed |
| `error_message` | `TEXT` | NULLABLE | 错误信息 |
| `triggered_by` | `VARCHAR(100)` | NULLABLE | 触发者 |

**索引**:
- `idx_cleanup_start_time` (`start_time`)
- `idx_cleanup_status` (`status`)

---

### 3.14 `storage_monitor_records` — 存储监控记录

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| `id` | `INT` | PK, AUTO_INCREMENT, INDEX | 自增主键 |
| `record_time` | `DateTime(TZ)` | server_default=now() | 记录时间 |
| `total_size` | `FLOAT` | NOT NULL | 总存储使用量（字节） |
| `file_count` | `INT` | NOT NULL | 文件总数 |
| `log_file_count` | `INT` | DEFAULT 0 | 日志文件数量 |
| `warning_triggered` | `BOOLEAN` | DEFAULT FALSE | 是否触发警告 |

**索引**:
- `idx_monitor_record_time` (`record_time`)

---

## 四、索引设计策略

### 4.1 唯一索引（UK）

| 表名 | 唯一索引 | 字段组合 | 说明 |
|------|----------|----------|------|
| `evtc_log` | `log_uuid` | `log_uuid` | 日志全局唯一 |
| `evtc_log` | `file_sha256` | `file_sha256` | 文件去重 |
| `members` | `account_name` | `account_name` | 账号唯一 |
| `account_characters` | `uk_account_character` | (`account_name`, `character_name`) | 同一账号下角色唯一 |
| `ei_player` | `uk_log_agent_ei` | (`log_id`, `agent_index`) | 同一日志内 agent 唯一 |
| `ei_target` | `uk_log_target_agent` | (`log_id`, `agent_index`) | 同一日志内 agent 唯一 |
| `ei_skill_map` | `uk_log_skill_key` | (`log_id`, `skill_key`) | 同一日志内技能键唯一 |
| `ei_phase` | `uk_log_phase` | (`log_id`, `phase_index`) | 同一日志内阶段唯一 |
| `sys_user` | `username` | `username` | 用户名唯一 |
| `builds` | `slug` | `slug` | URL 标识唯一 |
| `sys_dict_type` | `dict_type` | `dict_type` | 字典类型唯一 |
| `sys_dict_data` | `_dict_type_value_uc` | (`dict_type`, `dict_value`) | 同类型下字典值唯一 |
| `ei_report` | `log_id` | `log_id` | 日志与报告 1:1 |

### 4.2 普通索引

| 表名 | 索引名 | 字段 | 用途 |
|------|--------|------|------|
| `evtc_log` | `idx_log_parse_status` | `parse_status` | 按状态筛选 |
| `evtc_log` | `idx_log_upload_time` | `upload_time` | 时间范围查询 |
| `evtc_log` | `idx_log_file_sha256` | `file_sha256` | 去重校验 |
| `evtc_log` | `idx_log_filename` | `filename` | 文件名搜索 |
| `evtc_log` | `idx_log_uploader_id` | `uploaded_by` | 按上传者筛选 |
| `fights` | `idx_fight_log_id` | `log_id` | 关联查询 |
| `fights` | `idx_fight_map_name` | `map_name` | 按地图筛选 |
| `fights` | `idx_fight_start_time` | `start_time` | 时间范围查询 |
| `fight_stats` | `idx_fight_stats_fight_member` | (`fight_id`, `member_id`) | 关联查询 |
| `fight_stats` | `idx_fight_stats_profession` | `profession` | 按职业筛选 |
| `fight_stats` | `idx_fight_stats_dps` | `dps` | DPS 排序 |
| `fight_stats` | `idx_fight_stats_damage` | `damage` | 伤害排序 |
| `account_characters` | `idx_account_name` | `account_name` | 账号查询 |
| `account_characters` | `idx_character_name` | `character_name` | 角色名查询 |
| `ei_player` | `idx_profession` | `profession` | 按职业筛选 |
| `ei_report` | `idx_ei_report_type` | `report_type` | 按类型筛选 |
| `ei_report` | `idx_ei_report_map` | `map_id` | 按地图筛选 |
| `batch_parse_tasks` | `idx_batch_task_status` | `status` | 按状态筛选 |
| `batch_parse_tasks` | `idx_batch_task_created` | `created_at` | 时间范围查询 |
| `batch_parse_task_items` | `idx_batch_item_task` | `task_id` | 关联查询 |
| `batch_parse_task_items` | `idx_batch_item_log` | `log_id` | 关联查询 |
| `batch_parse_task_items` | `idx_batch_item_status_retry` | (`status`, `next_retry_at`) | 轮询重试 |
| `storage_cleanup_records` | `idx_cleanup_start_time` | `start_time` | 时间范围查询 |
| `storage_cleanup_records` | `idx_cleanup_status` | `status` | 按状态筛选 |
| `storage_monitor_records` | `idx_monitor_record_time` | `record_time` | 时间范围查询 |

---

## 五、关键查询示例

### 5.1 查询指定日志的 DPS 排行榜

```sql
SELECT
    fs.account,
    fs.character_name,
    fs.profession,
    fs.group_id,
    fs.dps,
    fs.damage,
    fs.power_damage,
    fs.condi_damage,
    fs.breakbar_damage,
    fs.ai_score,
    fs.score_grade
FROM fight_stats fs
JOIN fights f ON fs.fight_id = f.id
WHERE f.log_id = ?
ORDER BY fs.dps DESC;
```

### 5.2 查询指定账号的跨战斗表现

```sql
SELECT
    el.filename,
    f.map_name,
    f.start_time,
    fs.profession,
    fs.dps,
    fs.damage,
    fs.damage_taken,
    fs.down_count,
    fs.dead_count,
    fs.ai_score,
    fs.score_grade
FROM fight_stats fs
JOIN fights f ON fs.fight_id = f.id
JOIN evtc_log el ON f.log_id = el.log_id
WHERE fs.account = '帅妹妹丶.8297'
ORDER BY f.start_time DESC;
```

### 5.3 查询指定日志的 EI 玩家摘要

```sql
SELECT
    agent_index,
    account,
    character_name,
    profession,
    group_id,
    has_commander_tag
FROM ei_player
WHERE log_id = ?
ORDER BY agent_index;
```

### 5.4 查询 Buff 覆盖率排行

```sql
SELECT
    account,
    character_name,
    profession,
    might_uptime,
    fury_uptime,
    quickness_uptime,
    alacrity_uptime,
    protection_uptime,
    stability_uptime
FROM fight_stats
WHERE fight_id = ?
ORDER BY quickness_uptime DESC;
```

---

## 六、数据库兼容性说明

### 6.1 多数据库支持

当前系统使用 SQLAlchemy 2.0 作为 ORM，支持以下三种数据库：

| 数据库 | 版本要求 | 生产环境建议 | 注意事项 |
|--------|----------|--------------|----------|
| **SQLite** | 3.35+ | 开发/测试/轻量部署 | 文件型，零配置；并发写入性能有限 |
| **MySQL** | 8.0+ | 中小规模生产环境 | 需配置 `utf8mb4`；`JSON` 类型支持良好 |
| **PostgreSQL** | 14+ | 大规模生产环境 | JSON/数组支持最优；推荐用于高并发场景 |

### 6.2 类型映射差异

SQLAlchemy 统一声明，底层自动映射：

| SQLAlchemy 类型 | SQLite | MySQL | PostgreSQL |
|-----------------|--------|-------|------------|
| `JSON` | TEXT (JSON1) | JSON | JSONB |
| `DateTime(timezone=True)` | TEXT | DATETIME(6) | TIMESTAMPTZ |
| `Enum` | VARCHAR | ENUM | ENUM/VARCHAR |
| `Numeric(5,2)` | NUMERIC | DECIMAL(5,2) | NUMERIC(5,2) |
| `Boolean` | INTEGER (0/1) | TINYINT(1) | BOOLEAN |
| `SmallInteger` | INTEGER | SMALLINT | SMALLINT |

---

## 七、废弃模型说明（已删除）

以下模型已在代码中**完全移除**，数据库中若仍存在历史表，可安全删除：

| 原表名 | 原模型文件 | 废弃原因 |
|--------|-----------|----------|
| `evtc_header` | 原 `evtc_header.py` | ZEVTC 原始数据体系废弃 |
| `evtc_agent` | 原 `evtc_agent.py` | ZEVTC 原始数据体系废弃 |
| `evtc_skill` | 原 `evtc_skill.py` | ZEVTC 原始数据体系废弃 |
| `evtc_event` | 原 `evtc_event.py` | ZEVTC 原始数据体系废弃 |
| `evtc_combat_meta` | 原 `evtc_combat_meta.py` | ZEVTC 原始数据体系废弃 |
| `evtc_event_per_second` | 原 `evtc_event_per_second.py` | ZEVTC 原始数据体系废弃 |
| `evtc_player_instance` | 原 `evtc_player_instance.py` | ZEVTC 原始数据体系废弃 |

> 当前系统不再维护二进制 EVTC 的逐条事件解析结果。原始 `.zevtc` / `.evtc` 文件仍保存在磁盘（`file_path` 指向的位置），需要详细事件级分析时，可重新调用 EI 解析器生成 JSON。

---

## 八、文件清单

| 文件 | 说明 |
|------|------|
| `backend/app/models/__init__.py` | 模型统一导入与注册 |
| `backend/app/models/log.py` | `evtc_log` 模型 |
| `backend/app/models/fight.py` | `fights` 模型 |
| `backend/app/models/fight_stats.py` | `fight_stats` 模型 |
| `backend/app/models/member.py` | `members` 模型 |
| `backend/app/models/account_character.py` | `account_characters` 模型 |
| `backend/app/models/zevtc_data.py` | `ei_player`, `ei_target`, `ei_skill_map`, `ei_phase` 模型 |
| `backend/app/models/sys_user.py` | `sys_user` 模型 |
| `backend/app/models/ei_report.py` | `ei_report` 模型 |
| `backend/app/models/ai_report.py` | `ai_reports` 模型 |
| `backend/app/models/batch_parse.py` | `batch_parse_tasks`, `batch_parse_task_items` 模型 |
| `backend/app/models/build.py` | `builds` 模型 |
| `backend/app/models/dictionary.py` | `sys_dict_type`, `sys_dict_data` 模型 |
| `backend/app/models/storage.py` | `storage_cleanup_records`, `storage_monitor_records` 模型 |
