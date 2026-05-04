# 解析器问题诊断与修复手册

> **版本**: v2.0
> **更新日期**: 2026-05-05
> **整合责任人**: 系统文档维护团队
> **变更摘要**:
> - 更新为与实际解析器一致（dps.report API 优先 + 本地 EnhancedZevtcParser 降级）
> - 删除 ZEVTC 原始二进制解析相关故障排查内容
> - 新增 dps.report API 限流、降级逻辑、EI JSON 格式兼容等常见问题

---

## 历史版本

| 版本 | 日期 | 变更内容 | 责任人 |
|------|------|----------|--------|
| v2.0 | 2026-05-05 | 更新为双解析路径架构 | 系统 |
| v2.0.0 | 2026-05-01 | 整合全部解析器修复记录 | 系统 |
| v1.1.0 | 2026-04-29 | 新增伤害值异常与上传问题修复 | System |
| v1.0.0 | 2026-05-01 | 初始解析器问题分析与修复 | 系统优化团队 |

---

# 一、解析架构概述

## 1.1 双解析路径

当前系统采用**双解析路径**设计：

```
用户上传 .zevtc
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ 主路径: dps.report API (优先)                                │
│   - 上传 .zevtc 到 dps.report                                │
│   - 返回 EI JSON + permalink                                │
│   - 直接同步到 ei_* 表                                       │
│   - 优点: 解析质量高、无需本地 EI 环境                        │
│   - 风险: 网络依赖、API 限流                                  │
└─────────────────────────────────────────────────────────────┘
    │ (失败时自动降级)
    ▼
┌─────────────────────────────────────────────────────────────┐
│ 降级路径: 本地 EnhancedZevtcParser                           │
│   - 解析 .zevtc 二进制文件                                   │
│   - 输出 EI 兼容 JSON                                        │
│   - 同步到 ei_* 表                                           │
│   - 优点: 无网络依赖、完全可控                                │
│   - 风险: 解析结果可能与 EI 官方略有差异                      │
└─────────────────────────────────────────────────────────────┘
```

## 1.2 输出数据格式

解析完成后，数据写入以下表：

| 表 | 数据来源 | 说明 |
|----|---------|------|
| `fights` | EI JSON 根字段 | 战斗概览 |
| `fight_stats` | EI JSON `players[]` | 玩家聚合统计 |
| `ei_player` | EI JSON `players[]` | 完整玩家数据(JSON) |
| `ei_target` | EI JSON `targets[]` | 完整目标数据(JSON) |
| `ei_skill_map` | EI JSON `skillMap` | 技能映射(JSON) |
| `ei_phase` | EI JSON `phases[]` | 战斗阶段(JSON) |

> **注意**: v3.0 起不再存储 ZEVTC 原始二进制数据（evtc_header/agent/skill/event 等）。

---

# 二、常见问题排查

## 问题1: dps.report API 限流/超时

**症状**:
```
HTTP 429 Too Many Requests
或
requests.exceptions.Timeout: HTTPSConnectionPool ...
```

**可能原因**:
1. 短时间内上传过多文件，触发 dps.report 限流
2. 网络连接不稳定
3. dps.report 服务临时不可用

**解决方案**:
1. **自动降级**: 系统会自动降级到本地 EnhancedZevtcParser 解析
2. **批量上传间隔**: 在批量导入时增加上传间隔（建议 5-10 秒/文件）
3. **重试机制**: 配置重试次数和退避策略

```python
# 批量导入时增加间隔
import time
for file in files:
    upload_and_parse(file)
    time.sleep(5)  # 避免触发限流
```

---

## 问题2: 本地解析降级后数据差异

**症状**:
- dps.report 解析和本地解析的 DPS 数值有细微差异
- 某些字段（如 `damage1S` 时间序列）本地解析为空或不完整

**可能原因**:
1. EnhancedZevtcParser 与 EI 官方实现存在差异
2. 本地解析器版本（2.59.0.0）与 dps.report 上的 EI 版本不同
3. 某些高级统计需要 EI 的完整分析，本地简化解析无法提供

**解决方案**:
1. **数据一致性校验**: 对比 dps.report 和本地解析的核心字段（durationMS、player_count、total_damage）
2. **标记数据源**: 在 `evtc_log.parse_status` 或 `ei_report` 中记录数据来源（api/legacy_api/local）
3. **优先使用 API 数据**: 如果 dps.report 可用，优先使用其返回的数据

---

## 问题3: EI JSON 格式兼容性

**症状**:
```
pydantic.ValidationError: 1 validation error for EIFormatData
players.0.dpsAll
  Field required
```

**可能原因**:
1. EI 版本升级导致字段变更
2. dps.report 返回的 JSON 与本地 schema 不一致
3. 某些 WvW 日志缺少标准字段

**解决方案**:
1. **检查 EI 版本**: 对比 `eliteInsightsVersion` 与系统支持的版本（当前 2.59.0.0）
2. **字段容错**: 所有 EI schema 字段使用默认值
3. **版本升级**: 如需支持新版本，更新 `app/schemas/ei_format.py`

```python
# schemas/ei_format.py 中的容错设计
class Player(BaseModel):
    account: str = ""  # 默认值，避免必填报错
    dpsAll: List[DpsStats] = []  # 空列表默认
    # ...
```

---

## 问题4: 数据库字段类型不匹配

**症状**:
```
sqlalchemy.exc.DataError: (pymysql.err.DataError) (1265, "Data truncated for column 'critical_rate'")
```

**可能原因**:
1. 百分比字段（`critical_rate`, `flanking_rate`, `glance_rate`）被错误地作为整数保存
2. EI JSON 中的浮点值传入整数字段

**解决方案**:
```python
# 使用 safe_float() 而非 safe_int()
critical_rate=safe_float(stats_data.get("criticalRate", 0)),
flanking_rate=safe_float(stats_data.get("flankingRate", 0)),
glance_rate=safe_float(stats_data.get("glanceRate", 0)),
```

---

## 问题5: 文件上传后解析状态卡住

**症状**:
- `evtc_log.parse_status` 长时间处于 `parsing` 状态
- 前端显示"解析中"但无进度更新

**可能原因**:
1. dps.report API 请求挂起
2. 本地解析进程崩溃但数据库状态未更新
3. 并发解析导致死锁

**解决方案**:
1. **设置解析超时**: 建议 300 秒
2. **健康检查任务**: 定时扫描 `parsing` 状态超过 10 分钟的日志，重置为 `failed`
3. **手动重置**:
```sql
UPDATE evtc_log SET parse_status = 'failed', error_message = 'Timeout' 
WHERE parse_status = 'parsing' AND parsed_at < DATE_SUB(NOW(), INTERVAL 10 MINUTE);
```

---

## 问题6: 伤害值异常（历史问题）

**症状**:
某些角色的伤害值异常高（如 720M+），不合理。

**根因**:
此问题**不在后端代码**，而在 EI 原始解析器或原始数据本身。可能原因：
1. EI 解析时某些条件伤害事件被重复累加
2. WvW 大型战斗中 NPC 伤害被错误归属到玩家
3. 症状伤害计算存在边界情况溢出

**解决方案**:
后端已在 API 服务层添加伤害值合理性校验：
```python
# 当 damage 异常偏离 power_damage + condi_damage 时
damage_sum = power_damage + condi_damage
damage_diff_ratio = abs(raw_damage - damage_sum) / max(raw_damage, 1)

if damage_diff_ratio > 0.5 and raw_damage > 100_000_000:
    corrected_damage = damage_sum
```

---

## 问题7: 数据库表结构不同步

**症状**:
```
sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) no such column: raw_json
```

**可能原因**:
代码模型更新后，数据库表结构未同步更新。

**解决方案**:
1. **自动建表**: 确保 `AUTO_CREATE_TABLES=True`（默认开启）
2. **强制重建**（开发环境）:
```python
from app.config.database import init_db
init_db(force_recreate=True)  # ⚠️ 会删除所有数据
```
3. **安全迁移**（生产环境）: 使用 Alembic 或手动添加列

---

# 三、调试工具与日志

## 3.1 解析日志定位

查看日志文件 `logs/app.log`，搜索以下关键词：

| 关键词 | 说明 |
|--------|------|
| `dps.report` | API 请求/响应日志 |
| `EnhancedZevtcParser` | 本地解析日志 |
| `parse failed` / `解析失败` | 解析错误 |
| `EI sync` / `ei_sync` | EI 数据同步日志 |
| `DATABASE_ERROR` | 数据库操作错误 |

## 3.2 常用诊断命令

```bash
# 检查数据库连接
python -c "from app.config.database import test_connection; print(test_connection())"

# 检查配置
python -c "from app.core.config import get_settings; s=get_settings(); print(s.get_config_summary())"

# 检查表结构
python -c "from app.config.database import init_db; init_db()"

# 手动触发解析（调试用）
python -c "
from app.services.zevtc.log_import_service import import_log_file
import_log_file('path/to/file.zevtc', uploaded_by=1)
"
```

## 3.3 dps.report API 测试

```bash
# 直接测试 dps.report API
curl -X POST https://dps.report/uploadContent \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your_file.zevtc"

# 检查返回的 JSON 链接
curl https://dps.report/getJson?permalink=YOUR_PERMALINK
```

---

# 四、降级策略配置

## 4.1 强制使用本地解析

在特定场景下（如内网环境、dps.report 不可用），可配置强制使用本地解析：

```python
# 在解析服务中配置
PREFER_LOCAL_PARSER = True  # 默认 False（优先 API）
```

## 4.2 批量解析优化

```python
# 批量导入时配置
BATCH_PARSE_CONFIG = {
    "api_timeout": 300,           # API 超时(秒)
    "api_retry_count": 3,         # API 重试次数
    "api_retry_delay": 5,         # API 重试间隔(秒)
    "local_parse_timeout": 600,   # 本地解析超时(秒)
    "max_concurrent": 4,          # 最大并发解析数
    "rate_limit_per_minute": 10,  # 每分钟 API 请求上限
}
```

---

# 五、问题排查快速参考

| 错误信息 | 可能原因 | 解决方案 |
|---------|---------|---------|
| `HTTP 429` / `Too Many Requests` | dps.report 限流 | 降低上传频率，启用自动降级 |
| `Timeout` | 网络/API 不可用 | 检查网络，自动降级到本地解析 |
| `pydantic.ValidationError` | EI JSON 字段变更 | 更新 schema，使用字段默认值 |
| `Data truncated` | 字段类型不匹配 | 检查 safe_int/safe_float 使用 |
| `parse_status` 卡住 | 解析进程崩溃 | 手动重置状态，检查日志 |
| `no such column` | 表结构未同步 | 运行 init_db() 或 Alembic 迁移 |
| `Damage value anomaly` | EI 原始数据问题 | 使用后端伤害值校验修正 |

---

# 六、相关文件清单

### 解析服务
| 文件 | 说明 |
|------|------|
| `backend/app/services/zevtc/parser_service.py` | ZEVTC 解析服务封装 |
| `backend/app/services/zevtc/log_import_service.py` | 日志导入主流程（含 dps.report API 调用） |
| `backend/app/services/zevtc/batch_parse_service.py` | 批量解析服务 |
| `backend/app/services/ei/unified_service.py` | EI 统一数据服务 |
| `backend/app/services/ei/report_service.py` | EI 报告服务 |

### Schema
| 文件 | 说明 |
|------|------|
| `backend/app/schemas/ei_format.py` | EI 2.59.0.0 格式定义 |
| `backend/app/schemas/log.py` | LogCreate/Update/Response |
| `backend/app/schemas/fight.py` | FightResponse/FightStatsResponse |

### 配置
| 文件 | 说明 |
|------|------|
| `backend/app/core/config.py` | 统一配置（含 KEEP_RAW_FILE_AFTER_PARSE） |
| `backend/app/config/database.py` | 数据库连接管理 |

---

**文档维护**: 如有新增问题，请在此文档中补充并更新版本号。
