# 日志解析器规范与设计文档

> **版本**: v3.0
> **更新日期**: 2026-05-05
> **整合责任人**: 系统文档维护团队
> **变更摘要**:
> - 更新为双解析路径架构（dps.report API 优先 + 本地 EnhancedZevtcParser 降级）
> - 更新输出数据格式（fights/fight_stats + ei_* JSON 同步表）
> - 删除 ZEVTC 原始二进制数据解析相关描述

---

## 历史版本

| 版本 | 日期 | 变更内容 | 责任人 |
|------|------|----------|--------|
| v3.0 | 2026-05-05 | 更新为双解析路径架构 | 系统 |
| v2.0.0 | 2026-05-01 | 整合全部解析器相关文档 | 系统 |
| v1.2.0 | 2026-04-29 | EI 3.21.1.0 兼容性升级 | System |
| v1.1.0 | 2026-04-28 | 新增 data.json 字段说明 | System |
| v1.0.0 | 2026-04-27 | 初始解析器能力分析 | 技术团队 |

---

# 一、解析器架构

## 1.1 双解析路径

当前系统采用**双解析路径**设计：

### 路径一：dps.report API（优先）

```
用户上传 .zevtc
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ 1. 上传文件到 dps.report API                                 │
│    POST https://dps.report/uploadContent                    │
│    Content-Type: multipart/form-data                        │
│                                                             │
│ 2. 获取返回结果                                             │
│    - permalink: dps.report 报告链接                         │
│    - json_url: EI JSON 数据链接                             │
│                                                             │
│ 3. 下载 EI JSON                                             │
│    GET {json_url}                                           │
│                                                             │
│ 4. 解析 EI JSON → 同步到数据库                              │
│    - fights / fight_stats (聚合表)                          │
│    - ei_player / ei_target / ei_skill_map / ei_phase        │
└─────────────────────────────────────────────────────────────┘
```

**优点**:
- 解析质量与 EI 官方完全一致
- 无需本地 EI 环境
- 自动获取最新 EI 版本

**风险**:
- 网络依赖
- API 限流（429 Too Many Requests）
- 服务临时不可用

### 路径二：本地 EnhancedZevtcParser（降级）

当 dps.report API 失败时，系统自动降级到本地解析：

```
用户上传 .zevtc
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ 1. 本地解析 .zevtc 二进制文件                               │
│    - 解析文件头（EVTC 格式验证）                            │
│    - 提取玩家、目标、统计信息                               │
│                                                             │
│ 2. 输出 EI 兼容 JSON                                        │
│    - 格式兼容 EI 2.59.0.0                                   │
│                                                             │
│ 3. 同步到数据库                                             │
│    - 同路径一的数据库写入逻辑                               │
└─────────────────────────────────────────────────────────────┘
```

**优点**:
- 无网络依赖
- 完全可控
- 不触发 API 限流

**风险**:
- 解析结果可能与 EI 官方略有差异
- 某些高级统计（如 damage1S 时间序列）可能不完整
- 需要维护本地解析器

### 1.2 降级逻辑

```python
# 伪代码：解析入口
def parse_log(file_path: str, log_id: int) -> ParseResult:
    # 策略1: 优先使用 dps.report API
    try:
        result = call_dps_report_api(file_path, timeout=300)
        if result.success:
            sync_ei_json_to_db(result.json_data, log_id, source="api")
            return ParseResult.success(source="dps.report")
    except (Timeout, RateLimit, ServiceUnavailable) as e:
        logger.warning(f"dps.report API 失败: {e}, 降级到本地解析")
    
    # 策略2: 降级到本地 EnhancedZevtcParser
    try:
        json_data = local_parser.parse(file_path)
        sync_ei_json_to_db(json_data, log_id, source="local")
        return ParseResult.success(source="local")
    except Exception as e:
        logger.error(f"本地解析也失败: {e}")
        return ParseResult.failed(error=str(e))
```

---

## 2. 输入格式

### 2.1 支持的文件格式

| 格式 | 扩展名 | 说明 | 来源 |
|------|--------|------|------|
| **ZEVTC** | `.zevtc` | ZIP压缩的EVTC二进制日志 | ArcDPS 插件输出 |
| **EVTC** | `.evtc` | 原始二进制日志（解压后） | 罕见 |
| **EI JSON** | `.json` | Elite Insights 解析输出 | dps.report API |

### 2.2 文件验证

上传时进行以下验证：

```python
# 1. 文件大小检查
if file_size > MAX_UPLOAD_SIZE:  # 默认 100MB
    raise FileTooLargeError()

# 2. 魔数检查（ZEVTC = ZIP格式）
if magic[:4] != b'PK\x03\x04':
    raise InvalidFileFormatError("不是有效的 ZIP/ZEVTC 文件")

# 3. 内部 EVTC 验证（解压后）
if evtc_magic[:4] != b'EVTC':
    raise InvalidFileFormatError("ZIP 内部不是有效的 EVTC 文件")
```

---

## 3. 输出数据格式

### 3.1 数据库写入目标

解析完成后，数据写入以下表：

| 表 | 数据来源 | 说明 |
|----|---------|------|
| `evtc_log` | 文件元数据 | 更新 parse_status, parse_time_ms, dps_report_permalink |
| `fights` | EI JSON 根字段 | fightName, durationMS, recordedBy, mapID 等 |
| `fight_stats` | EI JSON `players[]` | 聚合统计：damage, dps, critical_rate, down_count 等 |
| `ei_player` | EI JSON `players[]` | 完整玩家数据，JSON 列存储 |
| `ei_target` | EI JSON `targets[]` | 完整目标数据，JSON 列存储 |
| `ei_skill_map` | EI JSON `skillMap` | 技能映射，JSON 列存储 |
| `ei_phase` | EI JSON `phases[]` | 战斗阶段，JSON 列存储 |
| `ei_report` | dps.report 返回 | 完整报告数据（HTML 导入时） |

> **注意**: v3.0 起不再写入 `evtc_header`, `evtc_agent`, `evtc_skill`, `evtc_event` 等原始二进制数据表。

### 3.2 EI JSON 字段说明

基于 **Elite Insights 2.59.0.0** 输出格式。

#### 根级别字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `eliteInsightsVersion` | `string` | EI 版本号，当前 "2.59.0.0" |
| `triggerID` | `number` | 触发器ID |
| `fightName` | `string` | 战斗名称 |
| `duration` | `string` | 格式化时长 |
| `durationMS` | `number` | 时长（毫秒）|
| `timeStart` / `timeEnd` | `string` | 开始/结束时间 |
| `recordedBy` | `string` | 记录者角色名 |
| `recordedAccountBy` | `string` | 记录者账号 |
| `success` | `boolean` | 战斗是否成功 |
| `isCM` | `boolean` | 是否挑战模式 |
| `anonymous` | `boolean` | 是否匿名 |
| `detailedWvW` | `boolean` | 是否详细WvW日志 |
| `isWvW` | `boolean` | 是否WvW模式 |
| `players` | `Player[]` | 玩家数组 |
| `targets` | `Target[]` | 目标数组 |
| `phases` | `Phase[]` | 阶段数组 |
| `skillMap` | `Object` | 技能映射 |
| `buffMap` | `Object` | Buff映射 |
| `damageModMap` | `Object` | 伤害修饰符映射 |

#### Players 字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `account` | `string` | 账号名，格式 `Name.XXXX` |
| `name` | `string` | 角色名 |
| `profession` | `string` | 职业专精 |
| `group` | `number` | 小队编号 |
| `hasCommanderTag` | `boolean` | 是否有指挥官标记 |
| `weapons` | `string[]` | 武器配置 |
| `dpsAll` | `DpsStats[]` | 综合DPS统计 |
| `dpsTargets` | `DpsStats[][]` | 对每个目标的DPS |
| `statsAll` | `CombatStats[]` | 综合战斗统计 |
| `statsTargets` | `CombatStats[][]` | 对每个目标的统计 |
| `defenses` | `Defenses[]` | 防御统计 |
| `support` | `Support[]` | 支援统计 |
| `buffUptimes` | `BuffUptime[]` | Buff覆盖数据 |
| `rotation` | `Rotation[]` | 技能循环 |
| `targetDamage1S` | `number[][]` | 每秒对目标伤害 |
| `targetPowerDamage1S` | `number[][]` | 每秒对目标直伤 |
| `targetConditionDamage1S` | `number[][]` | 每秒对目标症状伤害 |
| `targetDamageDist` | `DamageDist[][]` | 伤害分布 |

#### DpsStats 子对象

| 字段 | 类型 | 说明 |
|------|------|------|
| `dps` | `number` | 秒伤 |
| `damage` | `number` | 总伤害 |
| `condiDps` | `number` | 症状DPS |
| `condiDamage` | `number` | 症状总伤害 |
| `powerDps` | `number` | 直伤DPS |
| `powerDamage` | `number` | 直伤总伤害 |
| `breakbarDamage` | `number` | 破盾伤害 |
| `actorDps` | `number` | 玩家秒伤（不含宠物）|
| `actorDamage` | `number` | 玩家总伤害（不含宠物）|

#### CombatStats 子对象

| 字段 | 类型 | 说明 |
|------|------|------|
| `criticalRate` | `number` | 暴击率 |
| `flankingRate` | `number` | 侧击率 |
| `glanceRate` | `number` | 浅击率 |
| `missed` | `number` | 未命中次数 |
| `evaded` | `number` | 闪避次数 |
| `blocked` | `number` | 格挡次数 |
| `interrupts` | `number` | 打断次数 |
| `killed` | `number` | 击杀数 |
| `downed` | `number` | 击倒数 |
| `swapCount` | `number` | 武器切换次数 |
| `avgBoons` | `number` | 平均Buff数 |

---

## 4. Schema 定义

### 4.1 EI 格式 Schema

```python
# backend/app/schemas/ei_format.py

class DpsStats(BaseModel):
    dps: int = 0
    damage: int = 0
    condiDps: int = 0
    condiDamage: int = 0
    powerDps: int = 0
    powerDamage: int = 0
    breakbarDamage: float = 0.0
    actorDps: int = 0
    actorDamage: int = 0

class CombatStats(BaseModel):
    criticalRate: float = 0.0
    flankingRate: float = 0.0
    glanceRate: float = 0.0
    missed: int = 0
    evaded: int = 0
    blocked: int = 0
    interrupts: int = 0
    killed: int = 0
    downed: int = 0
    swapCount: int = 0
    avgBoons: float = 0.0

class Player(BaseModel):
    account: str = ""
    name: str = ""
    profession: str = ""
    group: int = 1
    hasCommanderTag: bool = False
    weapons: List[str] = []
    dpsAll: List[DpsStats] = []
    statsAll: List[CombatStats] = []
    defenses: List = []
    support: List = []
    buffUptimes: List = []
    rotation: List = []
    # ... 其他字段

class EIFormatData(BaseModel):
    eliteInsightsVersion: str = "2.59.0.0"
    fightName: str = ""
    durationMS: int = 0
    recordedBy: str = ""
    recordedAccountBy: str = ""
    players: List[Player] = []
    targets: List[Target] = []
    phases: List[Phase] = []
    skillMap: Dict[str, SkillEntry] = {}
```

### 4.2 API Schema

```python
# backend/app/schemas/log.py
class LogCreate(BaseModel):
    filename: str
    file_sha256: str
    file_size_compressed: int
    file_size_raw: int

class LogResponse(BaseModel):
    log_id: int
    filename: str
    parse_status: str
    dps_report_permalink: Optional[str]
    upload_time: datetime

# backend/app/schemas/fight.py
class FightResponse(BaseModel):
    id: int
    log_id: int
    fight_name: str
    duration_ms: int
    duration_str: str
    map_name: str
    player_count: int

class FightStatsResponse(BaseModel):
    id: int
    fight_id: int
    account_name: str
    character_name: str
    profession: str
    damage: int
    dps: int
    critical_rate: float
    down_count: int
    death_count: int
```

---

## 5. 服务层架构

### 5.1 服务目录结构

```
backend/app/services/
├── zevtc/                          # ZEVTC 解析相关服务
│   ├── parser_service.py           # EnhancedZevtcParser 封装
│   ├── log_import_service.py       # 日志导入主流程（含 dps.report API）
│   ├── log_service.py              # 日志查询服务
│   ├── fight_service.py            # 战斗查询服务
│   ├── member_service.py           # 成员管理服务
│   ├── batch_parse_service.py      # 批量解析服务
│   ├── data_validator.py           # 数据验证
│   ├── field_mapper.py             # 字段映射
│   └── rate_limiter.py             # 请求限流
│
├── ei/                             # EI 数据同步服务
│   ├── unified_service.py          # 统一数据服务（自动选择最佳数据源）
│   └── report_service.py           # EI 报告服务
│
├── wvw/                            # WvW 报告服务
│   └── ...
│
└── game_data/                      # 游戏数据服务
    └── ...
```

### 5.2 统一数据服务

`app/services/ei/unified_service.py` 为前端提供统一接口：

```python
def get_unified_ei_data(db: Session, log_id: int) -> Optional[Dict]:
    """
    自动选择最佳数据源：
    1. 优先检查 ei_report（HTML 导入的完整数据）
    2. 如果没有，从 ei_player/ei_target/ei_phase 组装 EI 格式数据
    3. 如果都没有，返回 None
    """
    # 策略1: ei_report
    report = db.query(EiReport).filter(EiReport.log_id == log_id).first()
    if report and report.summary_json:
        return _from_ei_report(report)
    
    # 策略2: ZEVTC 同步表组装
    has_synced = db.query(EiPlayer).filter(EiPlayer.log_id == log_id).first()
    if has_synced:
        return _from_zevtc_sync(db, log_id)
    
    return None
```

---

## 6. 数据流架构

### 6.1 完整解析流程

```
用户上传 .zevtc
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 1: 文件接收与预检                                       │
│   - 校验文件大小 (<100MB)                                   │
│   - 校验 ZIP 魔数 (PK\x03\x04)                              │
│   - 校验内部 EVTC 魔数 (EVTC)                               │
│   - 计算 SHA-256 指纹                                       │
│   - 查询 evtc_log 去重                                      │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 2: 重复导入判定                                         │
│   - 指纹匹配 → 返回已有记录ID + 跳过/更新选项                │
│   - 无匹配 → 继续解析                                        │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 3: 优先调用 dps.report API                              │
│   - 上传文件                                                │
│   - 获取 permalink + json_url                               │
│   - 下载 EI JSON                                            │
│   - 超时: 300秒                                             │
│   - 失败 → 自动降级到本地解析                                │
└─────────────────────────────────────────────────────────────┘
    │ (API 失败时)
    ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 4: 本地 EnhancedZevtcParser 解析（降级路径）            │
│   - 解析 .zevtc 二进制文件                                  │
│   - 输出 EI 兼容 JSON                                       │
│   - 超时: 600秒                                             │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 5: JSON 验证与抽取                                      │
│   - Pydantic 校验 EIFormatData                              │
│   - 抽取核心字段到 fights / fight_stats                      │
│   - 保留完整 JSON 到 ei_* 表                                 │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 6: 数据库写入                                           │
│   - 事务包裹：log → fight → fight_stats → ei_*              │
│   - 全部成功 → commit                                       │
│   - 任何失败 → rollback + 标记 failed                        │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 7: 文件管理                                             │
│   - KEEP_RAW_FILE_AFTER_PARSE=True: 保留文件                 │
│   - KEEP_RAW_FILE_AFTER_PARSE=False: 删除文件                │
│   - 更新 log.parse_status = 'completed'                      │
└─────────────────────────────────────────────────────────────┘
```

### 6.2 批量解析流程

```python
# app/services/zevtc/batch_parse_service.py
class BatchParseService:
    def batch_parse(self, log_ids: List[int]):
        for log_id in log_ids:
            # 检查限流
            if self.rate_limiter.is_limited():
                time.sleep(self.rate_limiter.wait_time())
            
            # 尝试 API 解析
            result = self.parse_via_api(log_id)
            if not result.success:
                # 降级到本地
                result = self.parse_via_local(log_id)
            
            # 更新状态
            self.update_parse_status(log_id, result)
```

---

## 7. 性能优化

### 7.1 批量插入优化

```python
# ei_player 批量插入
db.bulk_insert_mappings(EiPlayer, player_rows)

# ei_skill_map 批量插入
db.bulk_insert_mappings(EiSkillMap, skill_rows)
```

### 7.2 并发控制

```python
# 批量解析配置
BATCH_CONFIG = {
    "max_concurrent": 4,           # 最大并发解析数
    "api_rate_limit": 10,          # 每分钟 API 请求上限
    "api_timeout": 300,            # API 超时(秒)
    "local_timeout": 600,          # 本地解析超时(秒)
}
```

### 7.3 缓存策略

```python
# EI JSON 缓存（可选）
@lru_cache(maxsize=128)
def get_ei_json(log_id: int) -> Dict:
    """缓存解析结果，避免重复解析"""
    return load_ei_json_from_db(log_id)
```

---

## 8. 向后兼容性

### 8.1 EI 版本兼容

当前系统基于 **EI 2.59.0.0** 格式。Schema 中所有字段使用默认值，确保向前兼容：

```python
class Player(BaseModel):
    account: str = ""           # 空字符串默认
    dpsAll: List[DpsStats] = []  # 空列表默认
    # 新增字段不会影响旧数据解析
```

### 8.2 数据迁移

如需升级 EI 版本：
1. 更新 `app/schemas/ei_format.py`
2. 更新字段映射逻辑
3. 重新解析历史日志（可选）

---

## 9. 相关文件清单

| 文件 | 路径 | 说明 |
|------|------|------|
| 统一配置 | `backend/app/core/config.py` | KEEP_RAW_FILE_AFTER_PARSE 等 |
| EI Schema | `backend/app/schemas/ei_format.py` | EIFormatData / Player / Target / Phase |
| Log Schema | `backend/app/schemas/log.py` | LogCreate / LogUpdate / LogResponse |
| Fight Schema | `backend/app/schemas/fight.py` | FightResponse / FightStatsResponse |
| 解析服务 | `backend/app/services/zevtc/parser_service.py` | EnhancedZevtcParser 封装 |
| 导入服务 | `backend/app/services/zevtc/log_import_service.py` | 导入主流程（含 API 调用） |
| 批量服务 | `backend/app/services/zevtc/batch_parse_service.py` | 批量解析 |
| 统一服务 | `backend/app/services/ei/unified_service.py` | 自动选择数据源 |
| EI 模型 | `backend/app/models/zevtc_data.py` | ei_player / ei_target / ei_skill_map / ei_phase |
| Fight 模型 | `backend/app/models/fight.py` | fights |
| FightStats 模型 | `backend/app/models/fight_stats.py` | fight_stats |

---

**文档维护**: 如有解析器架构变更，请同步更新本文档和相关 Schema 定义。
