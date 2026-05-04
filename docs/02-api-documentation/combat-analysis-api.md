# GW2 WVW 日志解析管理系统 - 战斗分析 API 文档

> **版本**: v3.0  
> **更新日期**: 2026-05-05  
> **责任人**: 帅姐姐  
> **整合来源**: COMBAT_ANALYSIS_API.md, COMBAT_ANALYSIS_API_EVALUATION_REPORT.md, COMBAT_ANALYSIS_API_INTEGRATION_REPORT.md

## 版本变更记录

| 版本 | 日期 | 变更内容 | 责任人 |
|------|------|----------|--------|
| v3.0 | 2026-05-05 | 依据代码更新：`combat_analysis` 已降级，更新为新推荐管线（fights/ei-analysis/wvw-report） | 系统 |
| v2.0 | 2026-05-01 | 整合战斗分析 API 文档与对接问题记录，添加已知问题附录 | 帅姐姐 |
| v1.0 | 2026-04-29 | 初始版本 | 技术团队 |

---

## 一、概述

### 1.1 功能说明

> ⚠️ **重要变更**：`combat_analysis` 路由已降级，不再推荐使用。
>
> 新推荐管线：
> - **`/api/v1/fights/*`** — 战斗列表与统计（核心聚合数据）
> - **`/api/v1/ei-analysis/*`** — EI 精简分析（技能循环、玩家详细数据）
> - **`/api/v1/wvw-report/*`** — WvW 完整战斗报告（战斗概览、排行榜、时间线）

战斗分析 API 提供完整的战斗数据解析与分析功能，包括：
- 战斗详情信息获取（`GET /api/v1/fights/{fight_id}`）
- 玩家列表与统计数据（`GET /api/v1/fights/by-log/{log_id}/players`）
- 玩家详细信息与能力指标（`GET /api/v1/ei-analysis/{log_id}/player/{account}`）
- 技能循环数据（`GET /api/v1/ei-analysis/{log_id}/player/{account}/rotation`）
- WvW 战斗概览与排行榜（`GET /api/v1/wvw-report/logs/{log_id}/summary`, `GET /api/v1/wvw-report/logs/{log_id}/players`）
- 战斗时间线（`GET /api/v1/wvw-report/logs/{log_id}/timeline`）

### 1.2 重要说明

⚠️ **关键提示**：
- 所有战斗分析 API 要求日志必须处于 `completed` 状态
- 若日志状态为 `pending`、`parsing` 或 `error`，API 将返回错误
- 建议在调用分析 API 前，先通过日志状态查询接口确认状态

### 1.3 基础路径（已降级）

```
/api/v1/combat-analysis  ❌ 已降级，请勿使用
```

> **迁移建议**：
> - 原 `/api/v1/combat-analysis/logs/{log_id}/fight/details` → `GET /api/v1/fights/{fight_id}`
> - 原 `/api/v1/combat-analysis/logs/{log_id}/players` → `GET /api/v1/fights/by-log/{log_id}/players`
> - 原 `/api/v1/combat-analysis/logs/{log_id}/player/{account}` → `GET /api/v1/ei-analysis/{log_id}/player/{account}`
> - 原 `/api/v1/combat-analysis/logs/{log_id}/player/{account}/rotation` → `GET /api/v1/ei-analysis/{log_id}/player/{account}/rotation`

---

## 二、统一响应格式

```json
{
  "success": true,
  "message": "操作成功",
  "code": 200,
  "data": {}
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| success | boolean | 是 | 请求是否成功 |
| message | string | 是 | 响应消息 |
| code | int | 是 | 状态码 |
| data | any | 否 | 响应数据 |

---

## 三、API 接口详情

### 3.1 获取战斗详情

**接口路径**：`GET /api/v1/combat-analysis/logs/{log_id}/fight/details`

**路径参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| log_id | int | 是 | 日志 ID |

**响应示例**：
```json
{
  "success": true,
  "message": "获取战斗详情成功",
  "code": 200,
  "data": {
    "fight_id": 1,
    "log_id": 1,
    "basic_info": {
      "fight_name": "Detailed WvW - Eternal Battlegrounds",
      "map_id": 38,
      "map_name": "Eternal Battlegrounds",
      "duration_ms": 367295,
      "duration": "06m 07s 295ms",
      "time_start": "2026-04-26T21:58:04+08:00",
      "time_end": "2026-04-26T22:04:12+08:00"
    },
    "meta_info": {
      "elite_insights_version": "3.21.1.0",
      "arc_version": "EVTC20260416",
      "gw2_build": 199340,
      "is_success": true,
      "is_cm": false,
      "is_detailed_wvw": true,
      "recorded_by": "帅气的彦祖",
      "recorded_account_by": "帅妹妹丶.8297"
    },
    "summary": {
      "total_damage": 456789123,
      "total_healing": 0,
      "kill_count": 45,
      "death_count": 23,
      "player_count": 50
    }
  }
}
```

---

### 3.2 获取玩家列表

**接口路径**：`GET /api/v1/combat-analysis/logs/{log_id}/players`

**查询参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| sort_by | string | 否 | damage | 排序字段：damage, dps, kills, deaths |
| order | string | 否 | desc | 排序方向：asc, desc |

**响应示例**：
```json
{
  "success": true,
  "data": {
    "players": [
      {
        "account_name": "玩家账号.1234",
        "name": "角色名",
        "profession": "Vindicator",
        "elite_spec": null,
        "group": 1,
        "team_id": 2,
        "has_commander_tag": false,
        "damage": 12345678,
        "dps": 33614,
        "power_damage": 10234567,
        "condi_damage": 2111111,
        "kills": 8,
        "deaths": 2,
        "downs": 3,
        "time_in_combat": 360123,
        "damage_taken": 456789
      }
    ],
    "total": 50
  }
}
```

---

### 3.3 获取玩家详细信息

**接口路径**：`GET /api/v1/combat-analysis/logs/{log_id}/players/{account_name}`

**响应示例**：
```json
{
  "success": true,
  "data": {
    "player_info": {
      "account_name": "玩家账号.1234",
      "name": "角色名",
      "profession": "Vindicator",
      "group": 1,
      "team_id": 2
    },
    "dps_all": {
      "dps": 33614,
      "damage": 12345678,
      "condi_dps": 5749,
      "power_dps": 27865,
      "breakbar_damage": 123456
    },
    "stats_all": {
      "avg_boons": 4.2,
      "avg_active_boons": 3.1,
      "critical_rate": 65.4,
      "flanking_rate": 23.5,
      "glance_rate": 8.2,
      "killed": 8,
      "downed": 12
    },
    "defenses": {
      "damage_taken": 456789,
      "blocked_count": 15,
      "evaded_count": 23,
      "dodge_count": 45,
      "down_count": 3,
      "dead_count": 2,
      "boon_strips": 34,
      "condi_cleanse": 45
    }
  }
}
```

---

### 3.4 获取玩家 Buff 数据

**接口路径**：`GET /api/v1/combat-analysis/logs/{log_id}/players/{account_name}/buffs`

**响应示例**：
```json
{
  "success": true,
  "data": {
    "player": "玩家账号.1234",
    "buffs": [
      {
        "buff_id": 740,
        "buff_name": "Might",
        "uptime_ms": 350000,
        "uptime_percent": 95.3,
        "avg_stacks": 18.5
      }
    ]
  }
}
```

---

### 3.5 获取玩家技能伤害分布

**接口路径**：`GET /api/v1/combat-analysis/logs/{log_id}/players/{account_name}/skill-damage`

**响应示例**：
```json
{
  "success": true,
  "data": {
    "player": "玩家账号.1234",
    "skills": [
      {
        "skill_id": 12345,
        "skill_name": "技能名称",
        "total_damage": 456789,
        "hit_count": 45,
        "crit_rate": 66.67,
        "max_hit": 23456,
        "avg_hit": 10150
      }
    ]
  }
}
```

---

### 3.6 获取玩家技能循环

**接口路径**：`GET /api/v1/combat-analysis/logs/{log_id}/players/{account_name}/rotation`

**查询参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| limit | int | 否 | 1000 | 返回技能数量限制，最大 10000 |

---

### 3.7 获取玩家 DPS 时间序列

**接口路径**：`GET /api/v1/combat-analysis/logs/{log_id}/players/{account_name}/dps-series`

**查询参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| type | string | 否 | all | 数据类型：all, power, condi |

---

### 3.8 获取团队 Buff 汇总

**接口路径**：`GET /api/v1/combat-analysis/logs/{log_id}/team-buffs`

---

### 3.9 获取排行榜

**接口路径**：`GET /api/v1/combat-analysis/logs/{log_id}/leaderboard`

**查询参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| type | string | 否 | damage | 排行榜类型：damage, dps, kills, deaths |
| limit | int | 否 | 20 | 返回数量限制，最大 100 |

---

### 3.10 获取原始解析数据

**接口路径**：`GET /api/v1/combat-analysis/logs/{log_id}/raw`

返回完整的 Elite Insights 原始 JSON 数据。

---

## 四、数据模型

### 4.1 玩家统计基础字段

| 字段名 | 类型 | 说明 |
|--------|------|------|
| account_name | string | 玩家账号名 |
| name | string | 角色名 |
| profession | string | 职业名称 |
| group | int | 队伍编号 |
| team_id | int | 团队 ID |
| has_commander_tag | boolean | 是否有指挥官标记 |

### 4.2 DPS 相关字段

| 字段名 | 类型 | 说明 |
|--------|------|------|
| damage | int | 总伤害 |
| dps | int | 每秒伤害 |
| power_damage | int | 直伤伤害 |
| condi_damage | int | 症状伤害 |
| breakbar_damage | int | 破条伤害 |

### 4.3 防御统计字段

| 字段名 | 类型 | 说明 |
|--------|------|------|
| damage_taken | int | 承受总伤害 |
| blocked_count | int | 格挡次数 |
| evaded_count | int | 闪避次数 |
| dodge_count | int | 翻滚次数 |
| down_count | int | 击倒次数 |
| dead_count | int | 死亡次数 |

---

## 五、错误码定义

| HTTP 状态码 | 说明 |
|-------------|------|
| 200 | 请求成功 |
| 400 | 请求错误（参数错误或日志未完成解析） |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

| 业务错误信息 | 说明 |
|--------------|------|
| 日志不存在 | 请求的日志 ID 在数据库中不存在 |
| 日志未完成解析，当前状态: xxx | 日志未解析完成，无法获取分析数据 |
| 玩家不存在或数据获取失败 | 无法找到指定玩家或数据解析异常 |

---

## 六、使用示例

### 6.1 完整使用流程

```javascript
// 1. 检查日志状态
async function checkLogStatus(logId) {
  const response = await fetch(`/api/v1/logs/${logId}`)
  const result = await response.json()
  return result.data.parse_status === 'completed'
}

// 2. 获取战斗详情
async function getFightDetails(logId) {
  const response = await fetch(`/api/v1/combat-analysis/logs/${logId}/fight/details`)
  return await response.json()
}

// 3. 获取玩家列表并排序
async function getPlayersByDps(logId) {
  const response = await fetch(`/api/v1/combat-analysis/logs/${logId}/players?sort_by=dps&order=desc`)
  return await response.json()
}
```

### 6.2 错误处理

```javascript
async function safeApiCall(apiFunction, ...args) {
  try {
    const result = await apiFunction(...args)
    if (!result.success) {
      console.error('API 调用失败:', result.message)
      return null
    }
    return result.data
  } catch (error) {
    console.error('网络请求异常:', error)
    return null
  }
}
```

---

## 附录 A：已知问题与注意事项

### A.1 字段命名规范差异 (snake_case vs camelCase)

后端使用 `snake_case`，前端通常使用 `camelCase`。

**前端解决方案**：
```typescript
// 服务层转换（推荐）
function transformToCamelCase(data: any): any {
  if (Array.isArray(data)) return data.map(transformToCamelCase)
  if (data && typeof data === 'object') {
    return Object.keys(data).reduce((result, key) => {
      const camelKey = key.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase())
      result[camelKey] = transformToCamelCase(data[key])
      return result
    }, {} as any)
  }
  return data
}
```

### A.2 部分前端字段缺失

以下字段前端需要但后端未直接提供，需要前端自行计算或从原始数据获取：

| 字段 | 说明 | 解决方案 |
|------|------|----------|
| `total_score` | 玩家评分 | 根据职业配置和伤害数据前端计算 |
| `cc` | 破条/控制 | 直接使用 `breakbar_damage` |
| `cleanses` | 症状清除 | 从 `defenses.condi_cleanse` 获取 |
| `strips` | 增益剥离 | 从 `defenses.boon_strips` 获取 |
| `weapons` | 武器配置 | 从 `/raw` 接口原始数据提取 |

### A.3 数据映射关系

| 前端字段 | 后端字段 | 说明 |
|----------|----------|------|
| `duration` | `basic_info.duration_ms` | 战斗时长（毫秒） |
| `logStart` | `basic_info.time_start` | 战斗开始时间 |
| `logEnd` | `basic_info.time_end` | 战斗结束时间 |
| `arcVersion` | `meta_info.arc_version` | ArcDPS 版本 |
| `gw2Build` | `meta_info.gw2_build` | GW2 版本 |
| `account` | `account_name` | 账号名 |
| `dpsAll[0].damage` | `damage` | 总伤害 |
| `dpsAll[0].powerDamage` | `power_damage` | 直伤 |
| `dpsAll[0].condiDamage` | `condi_damage` | 症状伤害 |

### A.4 前端行动清单

| 序号 | 任务 | 优先级 |
|------|------|--------|
| 1 | 实现字段名转换层 (snake_case → camelCase) | 🔴 高 |
| 2 | 实现评分计算逻辑 | 🟡 中 |
| 3 | 实现 weapons 字段提取 | 🟡 中 |
| 4 | 实现数据缓存机制 | 🟡 中 |
| 5 | 优化错误处理和用户提示 | 🟢 低 |

---

## 附录 B：常见 Buff ID 对照

| Buff ID | Buff 名称 |
|---------|-----------|
| 740 | Might（威能） |
| 725 | Fury（狂怒） |
| 1187 | Quickness（急速） |
| 30328 | Alacrity（敏捷） |
| 717 | Protection（保护） |
| 718 | Regeneration（再生） |
| 1122 | Stability（稳固） |

---

*本文档整合了战斗分析 API 文档、对接问题记录和评估报告。原始详细内容请参阅 `docs/archive/` 目录。*
