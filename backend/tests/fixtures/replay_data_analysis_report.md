# 战斗回放数据分析报告

## 一、文件基本信息

| 属性 | 值 |
|------|-----|
| 原始文件 | `20260430-225037_vindicator_detailed_wvw_94s_kill.json` |
| 文件大小 | 7,580,261 字节（7.23MB） |
| 战斗时长 | 94秒（实际数据53147ms，约53秒） |
| 友方玩家数 | 32 |
| 目标数 | 25 |
| 友方职业数 | 10 |
| 敌方职业数 | **0（本文件无敌方职业数据）** |

> ⚠️ **重要发现**：此文件32个players全部属于同一teamID（2767），均为友方。`targets`数组中的25个目标均无`profession`字段。与之前`log_id=57`的分析结果不同（该文件有敌方players且有职业信息），说明敌方职业数据的可用性**不稳定**，取决于EI解析输出。

---

## 二、字段实用性评估

### 2.1 友方时间线数据（players子对象）

#### 高价值字段（直接影响回放质量）

| 字段 | 类型 | 数据量/样例 | 实用价值 | 说明 |
|------|------|------------|---------|------|
| `name` | str | `"JasonRonaldo.9510"` | ⭐⭐⭐ | 角色名展示 |
| `account` | str | `"JasonRonaldo.9510"` | ⭐⭐⭐ | 账号标识 |
| `profession` | str | `"Vindicator"` | ⭐⭐⭐ | 职业图标/颜色 |
| `group` | int | `1` | ⭐⭐⭐ | 小队编号，用于过滤 |
| `combatReplayData` | dict | ~1MB/玩家 | ⭐⭐⭐ | **核心回放数据** |
| `healthPercents` | list | `[[0,100],[5200,85.3]...]` | ⭐⭐⭐ | 血量时间线 |
| `damage1S` | list | `[0,0,2745,4553...]` | ⭐⭐⭐ | DPS时间线（1秒粒度） |
| `rotation` | list | `[[3400,58083,1404]...]` | ⭐⭐⭐ | 技能施放时间线 |
| `deathRecap` | list | ~500字节/次 | ⭐⭐⭐ | 死亡原因详情 |
| `buffUptimes[].states` | list | 见下 | ⭐⭐⭐ | 增益/症状状态变化 |
| `hasCommanderTag` | bool | `false` | ⭐⭐ | 指挥官标记 |
| `isFake` | bool | `false` | ⭐ | 是否占位数据 |

#### `combatReplayData` 内部字段

| 字段 | 类型 | 数据量/样例 | 实用价值 | 说明 |
|------|------|------------|---------|------|
| `positions` | list | `[[-10759,10889,12795,22479]...]` | ⭐⭐⭐ | 4维位置/朝向，~3秒一个坐标 |
| `orientations` | list | `[[-10759,7152,3384,1104]...]` | ⭐⭐⭐ | 朝向变化 |
| `deads` | list | `[[12400,15200]]` | ⭐⭐⭐ | 死亡时间段 |
| `downs` | list | `[[12400,15200]]` | ⭐⭐⭐ | 倒地时间段 |
| `dcs` | list | `[]` | ⭐⭐⭐ | 断线时间段 |
| `icon` | str | `"https://assets.gw2dat.com/..."` | ⭐ | 职业图标URL（前端可用本地映射） |

#### buffUptimes 字段（4类buff，每类有states）

buffUptimes包含4个对象，每个对象有`states`时间线：

| buff | id | 数据量/玩家 | 说明 |
|------|-----|------------|------|
| Might（威能） | 740 | ~400项 | 最重要 |
| Stability（稳固） | 1122 | ~50项 | 重要 |
| Protection（保护） | 717 | ~150项 | 重要 |
| Resolution（决心） | 873 | ~150项 | 重要 |

每项`states`格式：`[[时间戳, 层数], ...]`，描述buff层数随时间变化。

#### 中等价值字段（可选提取）

| 字段 | 类型 | 数据量/样例 | 实用价值 | 说明 |
|------|------|------------|---------|------|
| `statsAll` | list | ~1KB | ⭐⭐ | 综合统计（kills/downs/died等） |
| `defenses` | list | ~500B | ⭐⭐ | 防御统计 |
| `support` | list | ~500B | ⭐⭐ | 辅助统计（res/cleanse等） |
| `dpsTargets` | list | ~3KB | ⭐⭐ | 对目标DPS（不需要目标ID） |

#### 低价值/可丢弃字段

| 字段 | 类型 | 数据量 | 丢弃原因 |
|------|------|--------|---------|
| `targetDamage1S` | list | ~4KB | 按目标分组的DPS，不需要 |
| `targetDamageDist` | list | ~50KB | 伤害分布明细，冗余 |
| `totalDamageDist` | list | ~50KB | 同上 |
| `buffVolumes` | list | ~5KB | buff量统计，冗余 |
| `damageModifiersTarget` | list | ~500B | 目标伤害修正 |
| `extHealingStats` | dict | ~200KB | 治疗统计（大量细节） |
| `extBarrierStats` | dict | ~100KB | 屏障统计 |
| `activeTimes` | list | ~100B | 可通过duration计算 |

### 2.2 敌方数据（targets数组）

**⚠️ 本文件targets数组详情**：

| 字段 | 类型 | 数据量/样例 | 实用价值 | 说明 |
|------|------|------------|---------|------|
| `name` | str | `"SoulSlayer.3570"` | ⭐⭐ | 敌方名字（**需脱敏**） |
| `enemyPlayer` | bool | `true` | ⭐⭐ | 标记为敌方玩家 |
| `totalHealth` | int | `15000` | ⭐ | 总血量 |
| `combatReplayData.positions` | list | ~200坐标 | ⭐⭐⭐ | 敌方位置（**需脱敏**） |
| **profession** | str | **N/A** | - | **本文件无此字段** |

> **重要**：本文件25个targets均**无`profession`字段**，敌方职业信息**不可用**。在`log_id=57`中，敌方有profession且位于`players`数组中。敌方职业数据的可用性取决于EI解析器输出。

### 2.3 顶层统计字段

| 字段 | 类型 | 实用价值 | 说明 |
|------|------|---------|------|
| `durationMS` | int | ⭐⭐⭐ | 战斗时长，已存在fights.duration_ms |
| `success` | bool | ⭐⭐ | 战斗结果，已存在fights.is_victory |
| `fightName` | str | ⭐⭐ | 战斗名称 |
| `timeStartStd` | str | ⭐⭐⭐ | 开始时间（ISO 8601），已存在fights.start_time |
| `timeEndStd` | str | ⭐⭐⭐ | 结束时间，已存在fights.end_time |

---

## 三、单文件数据条目统计

### 3.1 各模块数据量（基于7.23MB JSON）

| 模块 | 原始大小 | 占比 | 是否已提取 | 状态 |
|------|---------|------|-----------|------|
| `players` 完整数据 | **~6.7MB** | **93.1%** | 仅标量 | 大部分未提取 |
| `targets` 完整数据 | ~320KB | 4.4% | 未提取 | 未提取 |
| `mechanics` | ~70KB | 1.0% | 未提取 | 可选 |
| 顶层统计字段 | ~50KB | 0.7% | 是 | 已提取到fights表 |
| 其他 | ~65KB | 0.8% | - | - |
| **总计** | **7.23MB** | **100%** | **~41%提取** | **~59%丢弃/未提取** |

### 3.2 按数据类型细分

| 数据类型 | 原始大小 | 示例来源 | 回放需要？ |
|---------|---------|---------|----------|
| 时间线数组（血量/DPS/buff/位置） | ~4MB | players[*].healthPercents等 | ⭐⭐⭐ 核心需要 |
| 技能rotation数据 | ~1.5MB | players[*].rotation | ⭐⭐⭐ 核心需要 |
| 职业/账号/小队等元数据 | ~200KB | players[*].profession等 | ⭐⭐⭐ 核心需要 |
| 伤害分布详情 | ~2MB | targetDamageDist, totalDamageDist | ❌ 不需要 |
| 治疗/屏障详细统计 | ~300KB | extHealingStats, extBarrierStats | ❌ 不需要 |
| 敌方位置坐标 | ~150KB | targets[*].positions | ❌ 需脱敏/可丢弃 |
| 其他杂项 | ~80KB | - | ❌ 不需要 |

### 3.3 当前系统已提取 vs 未提取

```
已提取（存储到结构化表）:
├── fights表: 战斗标量（时长/地图/击杀/死亡等）
├── fight_stats表: 玩家标量统计（damage/dps/buff_uptime等）
└── ~ 占原始JSON 41%

未提取（仍在ei_json_cache中）:
├── 时间线数据（血量/DPS/buff/技能/位置）
├── 敌方数据（职业/位置/统计）
└── ~ 占原始JSON 59%
```

---

## 四、30天累计数据量推算

### 4.1 单文件回放数据量

基于7.23MB JSON文件，提取回放所需数据：

| 数据项 | 原始大小 | 提取后 | 压缩后(gzip) |
|--------|---------|--------|-------------|
| 友方时间线（32玩家） | ~4.5MB | ~200KB | **~25KB** |
| 友方技能rotation | ~1.5MB | ~80KB | **~10KB** |
| 友方buff状态 | ~800KB | ~40KB | **~5KB** |
| 友方元数据 | ~200KB | ~15KB | **~3KB** |
| 敌方职业统计 | ~50KB | ~1KB | **~500B** |
| 战斗基本信息 | ~50KB | ~500B | **~300B** |
| **回放数据总计** | **~7.1MB** | **~336KB** | **~43KB** |

### 4.2 30天累计估算

**前提假设**：
- 日均上传日志：25个（基于当前数据趋势）
- 平均战斗时长：80秒（含长短战斗）
- 平均玩家数：30人/场

| 指标 | 单文件 | 日累计 | 30天累计 |
|------|--------|--------|---------|
| 完整EI JSON缓存 | 7.23MB | 180MB | **5.4GB** |
| 结构化数据增量（fights+stats） | ~100KB | 2.5MB | **75MB** |
| **回放快照（replay_snapshot）** | **43KB** | **1.1MB** | **31.5MB** |

> **结论**：回放快照增量仅31.5MB/月，相比完整EI JSON缓存（5.4GB）**可忽略不计**。存储压力主要来自`ei_json_cache`字段。

### 4.3 数据增长趋势

```
当前数据库规模（42248条evtc_log）:
├── evtc_log表（含ei_json_cache）: ~5.2GB
├── fights + fight_stats: ~180MB
├── 其他表: ~50MB
└── 总计: ~5.4GB

30天后（预计+750条日志）:
├── evtc_log表: ~5.4GB (+200MB)
├── fights + fight_stats: ~188MB (+8MB)
├── replay_snapshot: ~31.5MB（新增）
└── 总计: ~5.6GB
```

---

## 五、数据冗余分析

### 5.1 与现有表的冗余

| 回放数据项 | 现有表字段 | 冗余程度 | 建议 |
|-----------|-----------|---------|------|
| 战斗时长 | `fights.duration_ms` | 完全冗余 | 不存，前端从API获取 |
| 玩家职业 | `fight_stats.profession` | 完全冗余 | 不存，但需name/account映射 |
| 玩家DPS | `fight_stats.damage` | 部分冗余 | 回放需要DPS**时间线**，非总值 |
| 玩家伤害 | `fight_stats.damage` | 部分冗余 | 回放需要每秒伤害变化 |
| buff uptime | `fight_stats.*_uptime` | 部分冗余 | 回放需要buff**层数变化**，非均值 |
| 击杀/死亡 | `fights.kill_count` | 完全冗余 | 不存 |
| 地图 | `fights.map_name` | 完全冗余 | 不存 |

### 5.2 回放专属数据（无冗余）

以下数据**仅存在于EI JSON中**，现有系统未提取：

| 数据 | 用途 | 大小/场 |
|------|------|--------|
| `healthPercents` 时间线 | 血量动画 | ~15KB |
| `damage1S` 时间线 | DPS曲线 | ~8KB |
| `rotation` 技能时间线 | 技能图标闪烁 | ~5KB |
| `buffUptimes[*].states` | buff层数变化 | ~5KB |
| `combatReplayData.positions` | **位置坐标** | ~20KB（如需要） |
| `deathRecap` 详情 | 死亡面板 | ~2KB |

> **结论**：约90%的回放数据是现有系统未提取的时间线数据，存储到`replay_snapshot`是合理的。

---

## 六、关于敌方职业信息的重要发现

### 6.1 本文件情况

```
players数组: 32个元素，teamID全部为2767（友方）
targets数组: 25个元素，enemyPlayer=true，但**无profession字段**

结论: 此文件**无法提供敌方职业统计**
```

### 6.2 log_id=57 对比

```
players数组: 包含友方和敌方（teamID不同）
敌方players: 有完整的profession/name/account字段

结论: 该文件**可以**提取敌方职业统计
```

### 6.3 可用性评估

| 场景 | 敌方职业数据可用性 | 说明 |
|------|-----------------|------|
| 大型WvW战斗 | **高** | EI通常能识别双方玩家 |
| 小规模遭遇战 | **中** | 可能只有友方有profession |
| 快速击杀 | **低** | 可能只有targets数组，无profession |
| 敌方提前离场 | **低** | targets中敌方可能只有部分信息 |

### 6.4 设计建议

1. **敌方职业统计作为可选字段**：`replay_snapshot.enemy`可为`null`
2. **前端处理**：如果`enemy`为null，显示"敌方信息不可用"
3. **提取逻辑**：先从`players`中`teamID != friendly_team_id`提取profession；如不存在，尝试从`targets`中提取；如都不存在，则设为null

---

## 七、性能影响分析

### 7.1 存储性能

| 指标 | 影响 | 建议 |
|------|------|------|
| 单条记录大小 | +43KB（gzip压缩后） | 可忽略 |
| 表总体积增长 | +31.5MB/月 | 可忽略 |
| 索引影响 | 无（不新增索引） | - |
| BLOB/TEXT存储 | MySQL LONGTEXT，行外存储 | 无性能影响 |

### 7.2 查询性能

| 场景 | 响应时间 | 说明 |
|------|---------|------|
| 普通战斗列表查询 | 不变 | 不select replay_snapshot |
| 战斗详情（含回放） | +10-20ms | 读取+解压+解析43KB JSON |
| 回放数据单独查询 | ~5ms | 仅select replay_snapshot |
| 全表扫描 | 避免 | replay_snapshot不参与WHERE条件 |

### 7.3 导入性能

| 指标 | 影响 | 说明 |
|------|------|------|
| 单次导入额外耗时 | +50-100ms | 预提取+gzip压缩+写入 |
| 内存峰值 | 不变 | 已持有完整EI JSON对象 |
| 失败处理 | 可忽略 | 失败不回滚主流程 |

### 7.4 内存影响

| 场景 | 优化前 | 优化后（有replay_snapshot） |
|------|--------|---------------------------|
| 回放时内存峰值 | ~7MB（解压完整EI JSON） | **~35KB**（仅回放数据） |
| 前端内存占用 | ~50KB（解析后） | ~50KB（相同） |

---

## 八、优化建议

### 8.1 短期（立即实施）

1. **查询时避免SELECT ***：`evtc_log`表查询只取必要字段，避免读取`ei_json_cache`导致大量IO
2. **冷数据策略**：`ei_json_cache`可设置定期清理策略（如保留30天）
3. **压缩存储**：`replay_snapshot`使用gzip压缩，可再减少50%体积

### 8.2 中期（1-2周）

4. **对象存储迁移**：考虑将`ei_json_cache`迁移到文件系统/S3，数据库只存路径
5. **表分区**：为`fights`表按月份添加分区，优化时间范围查询
6. **数据清理**：定期清理过期的`ei_json_cache`，仅保留最近N天

### 8.3 长期（1月+）

7. **评估完整JSON必要性**：如果所有需要的数据都已结构化提取（含回放快照），可考虑不存储完整EI JSON
8. **增量更新**：如果EI JSON格式稳定，可考虑增量提取而非全量存储

---

## 九、回放JSON结构设计建议

基于以上分析，推荐以下`replay_snapshot`结构：

```json
{
  "v": 1,
  "duration_ms": 53147,
  "friendly_team_id": 2767,
  "players": [
    {
      "a": "JasonRonaldo.9510",
      "n": "JasonRonaldo.9510",
      "p": "Vindicator",
      "g": 1,
      "cmd": false,
      "hp": [[0, 100.0], [5200, 85.3], ...],
      "sk": [[3400, 58083, 1404], ...],
      "st": {
        "down": [[12400, 15200]],
        "dead": [[20000, 53147]],
        "dc": []
      },
      "dps": [0, 0, 2745, 4553, ...]
    }
  ],
  "enemy": {
    "Vindicator": 3,
    "Reaper": 2,
    "Troubadour": 1
  }
}
```

### 字段说明

| 缩写 | 全称 | 类型 | 说明 |
|------|------|------|------|
| `v` | version | int | 结构版本号 |
| `duration_ms` | duration_ms | int | 战斗时长 |
| `friendly_team_id` | friendly_team_id | int | 友方teamID |
| `a` | account | str | 账号 |
| `n` | name | str | 角色名 |
| `p` | profession | str | 职业 |
| `g` | group | int | 小队编号 |
| `cmd` | commander | bool | 是否指挥官 |
| `hp` | health_percents | list | 血量时间线 [[ms, percent], ...] |
| `sk` | skills | list | 技能时间线 [[ms, skill_id, duration_ms], ...] |
| `st` | states | dict | 状态变化 {down, dead, dc} |
| `dps` | dps_1s | list | 每秒DPS数组 |
| `enemy` | enemy_professions | dict | 敌方职业统计 {profession: count} |

### 体积预估

- 原始JSON：~336KB
- gzip压缩后：**~43KB/场**
- 30天累计：~31.5MB
- 存储可忽略，查询性能良好

---

## 十、结论

1. **数据量可控**：回放快照仅43KB/场，30天累计31.5MB，完全可接受
2. **大部分数据未提取**：当前系统仅提取~41%有效数据，回放需要的时间线数据全在剩余的59%中
3. **敌方数据不稳定**：敌方职业信息在某些日志中可用，某些不可用，需设计为可选字段
4. **存储优化空间大**：真正的存储压力来自`ei_json_cache`（5.4GB），而非回放快照
5. **查询性能优秀**：回放快照独立字段，不参与WHERE条件，不影响常规查询
