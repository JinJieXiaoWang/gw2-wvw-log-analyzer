# AI 分析系统深度设计 v3

> **版本**: v3.0-draft
> **日期**: 2026-05-16
> **状态**: 设计讨论中
> **数据基准**: dps.report API (Elite Insights JSON 2.59.0.0)

---

## 零、数据基线 —— dps.report API 返回了什么

所有设计基于 EI JSON 格式（即 dps.report 上传 .zevtc 后返回的数据）。项目中已完整解析并存储的核心数据结构：

### 0.1 顶层元数据
```
durationMS, timeStartStd, timeEndStd, fightName, recordedBy, success, isCM, detailedWvW
```

### 0.2 players[] —— 每个玩家（已提取 50+ 标量字段存入 FightStats 表）
```
dpsAll[{dps, damage, powerDps, condiDps, breakbarDamage, actorDps, ...}]
statsAll[{criticalRate, flankingRate, glanceRate, missed, interrupts, killed, downed,
          swapCount, avgBoons, avgConditions, skillCastUptime, wasted, saved, ...}]
defenses[{damageTaken, blockedCount, evadedCount, dodgeCount, downCount, deadCount,
          downDuration, deadDuration, barrierDamageAbsorbed, ...}]
support[{healing, boonStrips, condiCleanse, resurrects, stunBreak, appliedCcDuration, ...}]
buffUptimes[{id, name, uptime}...]       → 已提取为 might/fury/quickness/alacrity/protection/stability 覆盖率
buffUptimesActive[{id, name, uptime}...] → 同上（自身施加）
rotation[{id, skills[{time, duration, autoAttack, quickness}]}] → 技能时间线（JSON存储）
deathRecap[{time, ...}]                  → 死亡回顾（JSON存储）
weapons[]                                → 武器配置（JSON存储）
consumables{food, utility}              → 食物/扳手（JSON存储）
```

### 0.3 targets[] —— 敌方目标
```
dpsAll[{dps, damage, ...}] per player → 对每个目标的伤害分布
defenses[{damageTaken, ...}]           → 目标承受的伤害
name, totalHealth, finalHealth, healthPercentBurned, enemyPlayer
```

### 0.4 skillMap —— 技能ID → 名称/图标映射
### 0.5 phases[] —— 战斗阶段标记
### 0.6 buffMap —— Buff ID → 名称/图标映射

### 0.7 已预计算的摘要层 (ei_summary_service.build_ei_summary)
```
fight 基本聚合 (total_damage/healing/kills/deaths/player_count)
players[] 全标量字段排行榜
aggregate (总伤/直伤/症状/破蔑视 + 团队KPI)
profession_distribution (职业分布)
groups[] (小队分组 + 组内汇总)
buff_leaders (各buff Top5)
support_leaders (破法/净化/拉人 Top5)
defense_leaders (承伤/闪避 Top5)
top_dps_players (DPS Top10)
```

---

## 一、AI 分析的设计原则

1. **数据已就绪，不新增解析** —— 所有需要的数据已经从 EI JSON 提取并入库，AI 分析只做"数据组装→提示词→LLM调用"这一段
2. **规则引擎做统计，LLM 做解读** —— 数值计算用规则（0成本），语义解读和战术建议用 LLM
3. **按需深度** —— 列表页用轻量分析，详情页用深度分析，不一次性塞全部数据
4. **所有设计以 EI JSON 字段名为准** —— 确保数据来源可追溯

---

## 二、功能设计

### 功能1：团战战术分析（Battle Tactical Analysis）

**触发时机**：用户在某场战斗的详情页点击"AI 分析"

**输入数据（从已有数据组装）**：

```
第一层 —— 团队画像（~500 token）
  - 战斗时长、地图、参与人数
  - 职业分布：{守护: 8, 死灵: 6, 元素: 4, ...}
  - 小队编组：每个小队的人数、职业构成、是否有指挥官
  - 总伤害/总治疗/总击杀/总死亡/总倒地

第二层 —— 伤害结构（~300 token）
  - 团队总伤中直伤/症状/破蔑视占比
  - 团队平均暴击率、命中率
  - DPS Top5 + 伤害占比（占团队总伤百分比）
  - 对倒地表玩家的伤害比例（againstDownedDamage 占比过高提示"打尸体"问题）

第三层 —— Buff/支援结构（~400 token）
  - 关键buff平均覆盖率：might/fury/protection/quickness/alacrity/stability
  - 每队关键buff覆盖率对比（发现buff断档的小队）
  - 总净化量、总破法量、总拉人次数
  - 治疗输出 Top3 + 治疗占比

第四层 —— 生存分析（~300 token）
  - 总死亡/总倒地次数
  - 死亡分布：按小队统计死亡数
  - 高死亡玩家 Top5（含死亡次数和职业）
  - 团队平均闪避率、格挡率
```

**LLM 提示词结构**：

```
System: 你是 GW2 WvW 团战战术分析师。基于 EI 解析数据给出专业分析。

User:
[团队画像] ...（第一层数据）
[伤害结构] ...（第二层数据）
[Buff结构] ...（第三层数据）
[生存分析] ...（第四层数据）

请分析：
1. 团队伤害结构是否合理（直伤/症状配比是否符合当前meta）
2. 小队编组有效性（每队是否有足够的辅助/输出）
3. Buff覆盖是否达标（指出具体的短板buff和短板小队）
4. 死亡原因推测（站位问题 vs 辅助不足 vs 个人操作）
5. 3条具体可执行的改进建议

输出 JSON：{summary, damage_assessment, buff_assessment, survival_assessment,
             squad_analysis, top_3_recommendations, overall_score}
```

**预期输出产物**：
- 战术总结（自然语言，100-200字）
- 伤害评分（0-100）
- Buff评分（0-100）
- 生存评分（0-100）
- 小队编组评价（每组一段评价）
- 3条建议（每条带类型标记：编组/职业/操作/装备）

**不做什么**：
- 不分析单个玩家的技能循环（那是功能2的范围）
- 不对比历史数据（那是功能3的范围）
- 不让LLM做数值计算（所有数字在组装提示词前已算好）

---

### 功能2：个人技能循环分析（Player Skill Rotation Analysis）

**触发时机**：用户在战斗详情页点击某个玩家的"技能分析"

**输入数据（从已有的 rotation_json + skillMap + dpsAll 组装）**：

```
第一层 —— 玩家画像（~150 token）
  - 职业、专精推测（基于使用的技能推断）、武器配置
  - 总DPS、直伤DPS、症状DPS、暴击率、侧翼率
  - 击杀数、倒地数、死亡数

第二层 —— 技能使用统计（~500 token）
  从 rotation_json 预计算（规则引擎，不消耗LLM）：
  - 技能释放次数排名 Top10（从 rotation_json 统计 skill_casts）
  - 普攻占比（autoAttack 技能次数 / 总技能次数）
  - 爆发技能使用次数 + 平均间隔
  - 武器切换次数 → 推断是否频繁切武器
  
第三层 —— 技能时间线摘要（~600 token）
  从 rotation_json 提取关键事件序列（不是全部事件）：
  - 爆发技能的时间戳列表
  - 长时间技能空档（>3秒无技能释放）
  - 倒地/死亡时间点

第四层 —— 对标数据（~200 token）
  - 同职业同场其他玩家的平均DPS（对照基准）
  - 同职业玩家平均技能释放次数
```

**LLM 提示词结构**：

```
System: 你是 GW2 WvW 职业技能循环专家。分析玩家的技能使用数据并给出优化建议。

User:
[玩家画像] ...
[技能使用统计] ...
[技能时间线摘要] ...
[同职业对标数据] ...

请分析：
1. 技能循环是否符合WvW团战场景（vs 纯PvE循环）
2. 爆发技能使用时机是否合理
3. 是否存在明显的技能空档或资源浪费
4. 武器切换策略是否合理
5. 3条具体的操作改进建议

输出 JSON：{rotation_score, burst_assessment, gap_analysis, weapon_swap_assessment,
             top_3_mistakes, top_3_suggestions}
```

**规则预计算逻辑（不调LLM）**：

```
从 rotation_json 统计：
1. skill_casts: Map<skillId, count>           → 技能使用频次
2. auto_attack_ratio: aaCount / totalCount     → 普攻占比
3. burst_interval: 两次爆发技之间的平均时间     → 爆发节奏
4. skill_gaps: 相邻技能间隔 > 3000ms 的次数   → 空档次数
5. weapon_swap_count: statsAll.swapCount       → 切武器次数
6. profession_peers_avg_dps: 同职业平均DPS      → 对标基准
```

---

### 功能3：历史趋势分析（Historical Trend Analysis）

**触发时机**：dashboard 页或出勤统计页查看趋势

**输入数据（按时间序列聚合）**：

```
按天/周聚合的对战数据：
  - 每天(或每周)的战斗场次
  - 平均DPS、平均击杀数、平均死亡数
  - 平均buff覆盖率趋势（might/fury/protection）
  - 参与人数趋势
  - 职业分布变化（是否有人频繁换职业）
```

**分析维度**：
1. 伤害输出趋势（上升/稳定/下降 + 置信度）
2. 生存能力趋势
3. Buff覆盖趋势
4. 活跃度趋势（参与人次）
5. 异常检测（某天数据明显偏离均值）

**LLM 提示词结构**：

```
User: 以下是团队近{fight_count}场战斗的趋势数据：
- 时间范围：{time_range}
- 场均DPS趋势：[day1: xxx, day2: xxx, ...]
- 场均击杀趋势：[...]
- 场均死亡趋势：[...]
- Buff覆盖率趋势：[...]
- 参战人数趋势：[...]

请分析趋势并给出：
1. 整体趋势判断（提升/下降/稳定）
2. 最显著的变化指标及可能原因
3. 异常点识别
4. 3条趋势优化建议
```

**注意**：趋势分析的数据组装需要先按时间窗口做聚合查询。当前系统没有这个预计算，需要新增一个**轻量聚合查询**（不是预计算表，只是一条 GROUP BY 的 SQL）。

---

### 功能4：Build 合规检查（Build Compliance Check）

**触发时机**：出勤统计页对成员的 Build 进行批量检查

**输入数据（从 EiPlayer 的 weapons_json + consumables_json）**：

```
- 武器配置 (weapons_json)
- 食物/扳手 (consumables_json)
- 职业 (profession)
```

**分析逻辑**（规则为主，LLM 为辅）：

```
规则引擎（不调LLM）：
1. 检查是否装备了武器（weapons_json 非空）
2. 检查是否使用了食物和扳手（consumables 非空）
3. 检查武器是否符合职业（如死灵不能带剑）

LLM（仅在需要时调用）：
1. 武器搭配是否符合当前WvW Meta
2. Build建议（基于职业+武器推断Build类型，给出优化建议）
```

**注意**：EI JSON **不包含** traits（特性）、runes（符文）、sigils（符印）、装备属性等详细Build信息。dps.report API 返回的数据中，只有 weapons 和 consumables 字段。因此 Build 分析的深度天生受限，不应设计超出数据范围的功能。如果需要完整 Build 分析，需要用户额外提供 gw2skills.net 的 Build 链接或使用 GW2 API 查询。

---

## 三、数据流设计

```
┌──────────────────────────────────────────────────────────────────────┐
│                        现有流程（不变）                                │
│                                                                      │
│  .zevtc 上传 → EI 解析 → EiPlayer / FightStats / EiTarget 入库       │
│                              │                                       │
│                              ▼                                       │
│                   ei_summary_service.build_ei_summary()               │
│                   （已实现：聚合+排行榜+小队+职业分布）                  │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│                     新增：AI 数据组装层                                │
│                                                                      │
│   ai_data_assembler.py （新模块）                                     │
│                                                                      │
│   assemble_tactical_context(log_id) → {团队画像, 伤害结构, Buff结构,   │
│                                         生存分析}                      │
│   assemble_rotation_context(log_id, account) → {玩家画像, 技能统计,    │
│                                                   时间线, 对标}        │
│   assemble_trend_context(days) → {时间序列聚合数据}                    │
│   assemble_build_check_context(log_id) → {武器/消耗品列表}             │
│                                                                      │
│   所有函数：                                                           │
│     - 输入：数据库已有字段                                              │
│     - 输出：可直接填入提示词模板的结构化 dict                            │
│     - 不做任何 LLM 调用，只做数据查询和格式化                            │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│                     已有：AI 调用层（不变）                             │
│                                                                      │
│   AIOrchestrator.analyze_with_llm() → 接收 context dict → 调 LLM     │
│   QualityEvaluator → 质量评估                                          │
│   FallbackHandler → 降级处理                                          │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

关键新增模块只需要一个：**AI 数据组装器**（ai_data_assembler.py）。其余管线全部复用现有的。

---

## 四、关于"喂原始 zevtc 给 AI"的结论

### 4.1 为什么不可行

| 因素 | 数据 |
|---|---|
| 一场50人×20分钟WvW团战的EI JSON大小 | 80MB - 150MB |
| 解压后的 token 数（估算） | 500万 - 1000万 token |
| GPT-4 Turbo 上下文窗口 | 128K token |
| Claude 3.5 上下文窗口 | 200K token |
| 差距 | **约 40-80 倍** |

### 4.2 正确做法

不是"喂原始文件"，而是"从已解析的结构化数据中**按分析目标选择性提取**"。

```
原始 zevtc (80MB) → EI JSON → 数据库存储
                                  │
                  ┌───────────────┼───────────────┐
                  ▼               ▼               ▼
            战术分析提取     技能分析提取      趋势分析提取
            (~1,500 token)  (~1,500 token)   (~800 token)
```

项目已有的解析管线（28个 zevtc service 文件 + EiPlayer/FightStats 模型）已经完成了最困难的数据提取工作。需要新增的只是 **"按分析目标组装数据"** 这一层。

### 4.3 哪些原始数据值得"选择性喂给 AI"

| EI JSON 原始字段 | 当前利用情况 | 对AI分析的价值 | 建议 |
|---|---|---|---|
| `rotation[{skills[]}]` | 已存JSON但未分析 | **高** — 技能循环核心数据 | 预统计后喂入（不喂原始数组） |
| `deathRecap[]` | 已存JSON但未分析 | **高** — 死亡原因诊断 | 提取致死技能+时间点后喂入 |
| `buffUptimes[]` | 已提取6个核心buff | **高** — 需提取更多buff（resist/resolution/vigor/aegis） | 扩展buff提取列表 |
| `dpsAll[]` per target | 仅总伤 | **中** — 可分析集火效率 | 提取对敌方玩家的伤害分布 |
| `targetDamage1S[]` | 未使用 | **低** — 数据量太大，逐秒数据AI无法消化 | 不喂AI，仅在规则引擎中用 |
| `phases[]` | 已存但未用于AI | **中** — 可分段分析 | 提供阶段起止时间标注 |

---

## 五、实施路线

| 阶段 | 内容 | 新增/改动 | 优先级 |
|---|---|---|---|
| **Phase 1** | AI 数据组装器 + 新版提示词模板（功能1 战术分析） | 新增 ai_data_assembler.py + 修改 ai_prompt_templates.py | P0 |
| **Phase 2** | 重连 analyze_fight 端点 + 前端触发按钮 | 修改 ai_service.py + routers/ai.py + 前端组件 | P0 |
| **Phase 3** | 功能2 技能循环分析 | 扩展 ai_data_assembler + 新增提示词模板 | P1 |
| **Phase 4** | 功能3 趋势分析 | 新增聚合查询 + 提示词模板 | P1 |
| **Phase 5** | 功能4 Build 合规检查 | 规则为主，LLM为辅 | P2 |
| **Phase 6** | LLM-as-Judge 质量评估升级 | 修改 QualityEvaluator | P2 |

---

## 六、待讨论的设计决策

1. **AI 分析是同步还是异步？** —— 当前是同步调用（60s超时）。考虑到 LLM 响应可能需要10-30秒，建议改为：提交分析任务 → 返回 task_id → 前端轮询/SSE 获取结果。但这增加了复杂度。

2. **分析结果是否持久化到数据库？** —— ai_reports 表已存在，设计为持久化。好处是同一场战斗不重复分析（缓存命中），且可以浏览历史分析。

3. **是否需要多模型投票？** —— 过度设计。建议单模型 + 质量评估 + 降级链，当前架构已支持。

4. **Build 分析的数据源问题** —— EI JSON 不包含 traits/runes/sigils/装备属性。是否需要用户额外输入 Build 链接？建议先不做深度 Build 分析，仅做武器+消耗品合规检查。
