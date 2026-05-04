# Elite Insights 数据格式规范与解析器能力分析

> **版本**: v3.0  
> **更新日期**: 2026-05-05  
> **责任人**: 帅姐姐  
> **整合来源**: EI_DATA_FORMAT_SPECIFICATION.md, Elite Insights解析器能力分析与API设计方案.md, HTML_VUE_COMPARISON_ANALYSIS.md

## 版本变更记录

| 版本 | 日期 | 变更内容 | 责任人 |
|------|------|----------|--------|
| v3.0 | 2026-05-05 | 依据代码更新：补充 EI 3.21.1.0 格式说明，更新解析路径为 dps.report API + 本地解析器 | 系统 |
| v2.0 | 2026-05-01 | 整合EI数据格式规范、解析器能力分析、HTML/Vue对比分析 | 帅姐姐 |
| v1.0 | 2026-04-28 | 初始版本 | 技术团队 |

---

## 版本信息
- **文档版本**: v3.0
- **创建日期**: 2026-04-28
- **更新日期**: 2026-05-05
- **适用版本**: Elite Insights 3.21.1.0+
- **解析方式**: dps.report API 优先，失败自动降级至本地 `EnhancedZevtcParser`

---

## 1. 数据结构概述

### 1.1 整体架构

```
EliteInsightsLog
├── 基础信息 (Basic Info)
├── 战斗阶段 (Phases)
├── 目标数据 (Targets)
├── 玩家数据 (Players)
└── 扩展数据 (Extensions)
```

### 1.2 数据类型约定

| 类型 | 说明 | 示例 |
|------|------|------|
| `number` | 数值类型，支持整数和浮点数 | `12345`, `3.14` |
| `string` | 字符串类型 | `"Vindicator"` |
| `boolean` | 布尔类型 | `true`, `false` |
| `array<T>` | 泛型数组 | `[1, 2, 3]` |
| `object` | 对象类型 | `{ key: value }` |

---

## 2. 精英洞察日志主结构

### 2.1 EliteInsightsLog 接口

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `eliteInsightsVersion` | `string` | 是 | EI解析器版本号 |
| `triggerID` | `number` | 是 | 战斗触发ID |
| `eiEncounterID` | `number` | 是 | EI战斗ID |
| `fightName` | `string` | 是 | 战斗名称 |
| `fightIcon` | `string` | 否 | 战斗图标URL |
| `arcVersion` | `string` | 是 | arcdps版本号 |
| `gw2Build` | `number` | 是 | GW2游戏版本号 |
| `language` | `string` | 是 | 语言标识 |
| `languageID` | `number` | 是 | 语言ID |
| `recordedBy` | `string` | 是 | 记录者角色名 |
| `recordedAccountBy` | `string` | 是 | 记录者账号名 |
| `timeStart` | `string` | 是 | 战斗开始时间 |
| `timeEnd` | `string` | 是 | 战斗结束时间 |
| `duration` | `number` | 是 | 战斗时长（秒） |
| `durationMS` | `number` | 是 | 战斗时长（毫秒） |
| `logStartOffset` | `number` | 是 | 日志起始偏移 |
| `success` | `boolean` | 是 | 是否成功 |
| `isCM` | `boolean` | 是 | 是否挑战模式 |
| `anonymous` | `boolean` | 是 | 是否匿名 |
| `detailedWvW` | `boolean` | 是 | 是否WVW详细模式 |
| `phases` | `Phase[]` | 是 | 战斗阶段数组 |
| `targets` | `Target[]` | 是 | 目标数组 |
| `players` | `Player[]` | 是 | 玩家数组 |

---

## 3. Phase（战斗阶段）

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `name` | `string` | 是 | 阶段名称 |
| `start` | `number` | 是 | 开始时间（毫秒） |
| `end` | `number` | 是 | 结束时间（毫秒） |
| `breakbarPhase` | `boolean` | 是 | 是否破盾阶段 |
| `phaseIndex` | `number` | 是 | 阶段索引 |
| `phaseTargets` | `number[]` | 是 | 阶段目标ID数组 |
| `canSubPhase` | `boolean` | 是 | 是否可子阶段 |
| `isSubPhase` | `boolean` | 是 | 是否子阶段 |

---

## 4. Target（目标）

### 4.1 基础字段

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `id` | `number` | 是 | 目标ID |
| `instanceID` | `number` | 是 | 实例ID |
| `name` | `string` | 是 | 目标名称 |
| `teamID` | `number` | 是 | 队伍ID |
| `isFake` | `boolean` | 是 | 是否假目标 |
| `enemyPlayer` | `boolean` | 是 | 是否敌方玩家 |
| `firstAware` | `number` | 是 | 首次发现时间（毫秒） |
| `lastAware` | `number` | 是 | 最后发现时间（毫秒） |
| `totalHealth` | `number` | 是 | 总血量 |
| `finalHealth` | `number` | 是 | 最终血量 |
| `healthPercentBurned` | `number` | 是 | 血量燃烧百分比 |
| `condition` | `number` | 是 | 症状属性 |
| `concentration` | `number` | 是 | 聚能属性 |
| `healing` | `number` | 是 | 治疗属性 |
| `toughness` | `number` | 是 | 坚韧属性 |
| `hitboxHeight` | `number` | 是 | 碰撞箱高度 |
| `hitboxWidth` | `number` | 是 | 碰撞箱宽度 |

### 4.2 伤害数据

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `dpsAll` | `TargetDps[]` | 是 | DPS统计数组 |
| `statsAll` | `TargetStats[]` | 是 | 统计数据数组 |
| `defenses` | `TargetDefense[]` | 是 | 防御数据数组 |
| `totalDamageDist` | `any[][]` | 是 | 伤害分布数据 |
| `totalDamageTaken` | `any[][]` | 是 | 承受伤害数据 |
| `damage1S` | `number[][]` | 是 | 每秒伤害数据 |
| `powerDamage1S` | `number[][]` | 是 | 每秒直伤数据 |
| `conditionDamage1S` | `number[][]` | 是 | 每秒症状伤害数据 |

---

## 5. Player（玩家）

### 5.1 基础字段

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `instanceID` | `number` | 是 | 实例ID |
| `account` | `string` | 是 | 账号名 |
| `name` | `string` | 是 | 角色名 |
| `profession` | `string` | 是 | 职业名称 |
| `group` | `number` | 是 | 分组号 |
| `teamID` | `number` | 是 | 队伍ID |
| `role` | `string` | 否 | 角色定位（DPS/Support/Healer） |
| `hasCommanderTag` | `boolean` | 是 | 是否指挥官 |
| `friendlyNPC` | `boolean` | 是 | 是否友方NPC |
| `notInSquad` | `boolean` | 是 | 是否不在小队 |
| `isFake` | `boolean` | 是 | 是否假玩家 |

### 5.2 综合统计字段

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `total_score` | `number` | 是 | 总评分 |
| `dps` | `number` | 是 | DPS值 |
| `cc` | `number` | 是 | CC值 |
| `cleanses` | `number` | 是 | 症状清除数 |
| `strips` | `number` | 是 | 增益剥离数 |
| `downs` | `number` | 是 | 倒地次数 |
| `deaths` | `number` | 是 | 死亡次数 |

### 5.3 评分详情

```typescript
interface ScoreDetails {
  effectiveDamage: number    // 有效伤害评分
  breakbarDamage: number     // 破盾伤害评分
  survival: number           // 生存评分
  boonStrips?: number        // 增益剥离评分（可选）
  condiCleanses?: number     // 症状清除评分（可选）
}
```

### 5.4 DPS统计

```typescript
interface PlayerDps {
  dps: number                // 每秒伤害
  damage: number             // 总伤害
  condiDps: number           // 症状DPS
  condiDamage: number        // 症状总伤害
  powerDps: number           // 直伤DPS
  powerDamage: number        // 直伤总伤害
  breakbarDamage: number     // 破盾伤害
  actorDps: number           // 执行者DPS
  actorDamage: number        // 执行者总伤害
  actorCondiDps: number      // 执行者症状DPS
  actorCondiDamage: number   // 执行者症状伤害
  actorPowerDps: number      // 执行者直伤DPS
  actorPowerDamage: number   // 执行者直伤伤害
  actorBreakbarDamage: number// 执行者破盾伤害
}
```

### 5.5 战斗统计

```typescript
interface PlayerStats {
  wasted: number                    // 浪费值
  timeWasted: number                // 浪费时间
  saved: number                     // 节省值
  timeSaved: number                 // 节省时间
  stackDist: number                 // 堆叠距离
  distToCom: number                 // 战斗距离
  avgBoons: number                  // 平均增益层数
  avgActiveBoons: number            // 平均激活增益层数
  avgConditions: number             // 平均症状层数
  avgActiveConditions: number       // 平均激活症状层数
  swapCount: number                 // 切换次数
  skillCastUptime: number           // 技能施法占比
  skillCastUptimeNoAA: number       // 不含平A的施法占比
  totalDamageCount: number          // 总伤害次数
  totalDmg: number                  // 总伤害
  directDamageCount: number         // 直接伤害次数
  directDmg: number                 // 直接伤害
  connectedDirectDamageCount: number// 命中直接伤害次数
  connectedDirectDmg: number        // 命中直接伤害
  connectedDamageCount: number      // 命中伤害次数
  connectedDmg: number              // 命中伤害
  critableDirectDamageCount: number // 可暴击直接伤害次数
  criticalRate: number              // 暴击率
  criticalDmg: number               // 暴击伤害倍率
  flankingRate: number              // 侧翼攻击率
  againstMovingRate: number         // 对移动目标伤害率
  glanceRate: number                // 偏斜率
  missed: number                    // 未命中次数
  evaded: number                    // 被闪避次数
  blocked: number                   // 被格挡次数
  interrupts: number                // 打断次数
  invulned: number                  // 被无敌次数
  killed: number                    // 击杀次数
  downed: number                    // 击倒次数
  downContribution: number          // 击倒贡献
  connectedPowerCount: number       // 命中直伤次数
  connectedPowerAbove90HPCount: number // 90%以上血量命中次数
  connectedConditionCount: number   // 命中症状次数
  connectedConditionAbove90HPCount: number // 90%以上血量症状命中
  againstDownedCount: number        // 对倒地目标攻击次数
  againstDownedDamage: number       // 对倒地目标伤害
}
```

### 5.6 防御统计

```typescript
interface PlayerDefense {
  damageTaken: number           // 承受伤害
  downedDamageTaken: number     // 倒地时承受伤害
  breakbarDamageTaken: number   // 破盾伤害承受
  blockedCount: number          // 格挡次数
  evadedCount: number           // 闪避次数
  missedCount: number           // 闪避次数
  dodgeCount: number            // 翻滚次数
  invulnedCount: number         // 无敌次数
  damageBarrier: number         // 屏障伤害
  interruptedCount: number      // 被打断次数
  downCount: number             // 倒地次数
  downDuration: number          // 倒地时长（毫秒）
  deadCount: number             // 死亡次数
  deadDuration: number          // 死亡时长（毫秒）
  dcCount: number               // 掉线次数
  dcDuration: number            // 掉线时长（毫秒）
  boonStrips: number            // 增益剥离次数
  boonStripsTime: number        // 增益剥离时间
  conditionCleanses: number     // 症状清除次数
  conditionCleansesTime: number // 症状清除时间
}
```

### 5.7 辅助统计

```typescript
interface PlayerSupport {
  condiCleanse: number   // 症状清除数
  boonStrips: number     // 增益剥离数
}
```

### 5.8 增益数据

```typescript
interface PlayerBuffUptime {
  id: number
  buffData: {
    uptime: number           // 覆盖时间（毫秒）
    buffApplied: number      // 施加次数
    wasted: number           // 浪费次数
    extended: number         // 延长次数
    unknownExtended: number  // 未知延长次数
    stackRemoval: number     // 层数移除次数
    stackDist: number[]      // 层数分布
  }[]
  uptime: number             // 总覆盖时间
}
```

### 5.9 玩家增益快照

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `buffs` | `{ [buffId: string]: { id: number; uptime_ms: number } }` | 是 | 增益覆盖数据 |

---

## 6. 职业映射表

### 6.1 职业名称映射

| 英文名称 | 中文名称 |
|----------|----------|
| Dragonhunter | 猎龙者 |
| Daredevil | 独行侠 |
| Spellbreaker | 破法者 |
| Vindicator | 裁决者 |
| Chronomancer | 时空术士 |
| Firebrand | 燃火者 |
| Mechanist | 玉偃师 |
| Mesmer | 幻术师 |
| Engineer | 工程师 |
| Guardian | 守护者 |
| Warrior | 战士 |
| Revenant | 魂武者 |
| Thief | 潜行者 |
| Ranger | 游侠 |
| Necromancer | 死灵法师 |
| Elementalist | 元素使 |

### 6.2 职业颜色映射

| 职业 | RGB值 |
|------|-------|
| Dragonhunter | rgb(232,159,72) |
| Daredevil | rgb(232,127,12) |
| Spellbreaker | rgb(239,217,125) |
| Vindicator | rgb(129,182,228) |
| Chronomancer | rgb(170,151,217) |
| Firebrand | rgb(245,173,31) |
| Mechanist | rgb(208,156,89) |
| Mesmer | rgb(153,102,204) |
| Engineer | rgb(184,116,44) |
| Guardian | rgb(251,207,75) |
| Warrior | rgb(255,218,107) |
| Revenant | rgb(141,194,244) |
| Thief | rgb(231,124,3) |
| Ranger | rgb(119,186,79) |
| Necromancer | rgb(68,138,92) |
| Elementalist | rgb(238,105,105) |

---

## 7. 数据更新频率

| 数据类型 | 更新频率 | 说明 |
|----------|----------|------|
| 战斗基础信息 | 一次性 | 战斗结束后固定 |
| 玩家实时数据 | 每秒 | 伤害、血量等实时更新 |
| 增益数据 | 每帧 | 增益状态实时变化 |
| 统计数据 | 战斗结束 | 最终统计结果 |

---

## 8. 数据验证规则

### 8.1 必填字段验证

```typescript
// 玩家数据必填验证
const requiredPlayerFields = [
  'instanceID', 'account', 'name', 'profession',
  'group', 'teamID', 'hasCommanderTag', 'friendlyNPC',
  'notInSquad', 'isFake', 'dpsAll', 'statsAll',
  'defenses', 'support', 'total_score', 'dps'
]
```

### 8.2 数值范围约束

| 字段 | 最小值 | 最大值 |
|------|--------|--------|
| `duration` | 0 | 无限制 |
| `dps` | 0 | 无限制 |
| `total_score` | 0 | 10000 |
| `criticalRate` | 0 | 1 |
| `downs` | 0 | 无限制 |
| `deaths` | 0 | 无限制 |

---

## 9. 数据关联关系

```
EliteInsightsLog
    │
    ├── phases[].phaseTargets[] ───→ targets[].id
    │
    ├── targets[]
    │       └── dpsAll[].actorDamage ───→ players[].dpsAll[].damage
    │
    └── players[]
            ├── dpsAll[].damage ───→ 总伤害统计
            ├── statsAll[].killed ───→ 击杀统计
            ├── defenses[].downCount ───→ 倒地统计
            └── support[].condiCleanse ───→ 辅助统计
```

---

## 10. 数据版本兼容性

| EI版本 | 兼容性 | 说明 |
|--------|--------|------|
| 3.21+ | 完全兼容 | 完整支持所有字段 |
| 3.10-3.20 | 部分兼容 | 部分字段可能缺失 |
| < 3.10 | 不兼容 | 需升级解析器 |

---

## 附录：技能ID映射示例

| 技能ID | 技能名称 | 职业 |
|--------|----------|------|
| 1187 | 力量怒吼 | Warrior |
| 725 | 愤怒 | Warrior |
| 1056 | 守护者之怒 | Guardian |
| 1060 | 正义之怒 | Guardian |

---

**文档结束**