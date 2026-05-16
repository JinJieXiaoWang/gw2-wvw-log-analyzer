# AI战术复盘与成长顾问系统 - 功能设计方案

> 版本: v1.0  
> 日期: 2026-05-15  
> 状态: 后端引擎已实现，待前端集成  

---

## 1. 项目概述

### 1.1 背景与目标

当前AI分析模块已完成基础设施搭建（12/12端点测试通过），但分析功能停留在基础统计层面，缺乏对公会成员有实质性帮助的深度分析。

**核心目标**：构建基于真实战斗数据的AI深度分析引擎，为公会成员提供可操作的战术复盘和成长指导，避免纯数据统计。

### 1.2 五大分析模块

| 模块 | 功能定位 | 核心价值 |
|------|---------|---------|
| 个人战力成长档案 | 六维战力雷达图 + 成长轨迹 | 让成员清晰看到自己的优劣势和进步方向 |
| 死亡归因与生存分析 | 死亡原因分类 + 生存训练方案 | 降低死亡率，提升团战存活率 |
| 小队协同效能诊断 | 角色配比 + Buff互补分析 | 优化小队配置，提升团战效率 |
| Build执行效能验证 | 理论 vs 实际表现差距 | 确保Build配置被正确执行 |
| 战斗关键片段复盘 | 关键时刻识别 + 决策评估 | 抓住复盘重点，避免看完整场录像 |

---

## 2. 系统架构

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              前端层 (Vue 3)                              │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐   │
│  │ 成长档案面板  │ │ 死亡归因面板  │ │ 小队协同面板  │ │ Build验证面板 │   │
│  │ GrowthRadar  │ │ DeathTimeline│ │ SquadGrid    │ │ Checklist    │   │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘   │
│  ┌──────────────┐ ┌─────────────────────────────────────────────────┐   │
│  │ 关键片段面板  │ │              AI分析统一入口 (DataAiAnalysisView)  │   │
│  │ CombatTimeline│ │                                                   │   │
│  └──────────────┘ └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼ HTTP/REST
┌─────────────────────────────────────────────────────────────────────────┐
│                           API网关层 (FastAPI)                            │
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │ 现有端点: status / analyze/fight / analyze/member / analyze/build   ││
│  │         / suggestions / trend / reports / test / cache/clear        ││
│  ├─────────────────────────────────────────────────────────────────────┤│
│  │ 新增端点:                                                           ││
│  │  POST /analyze/personal-growth   → PersonalGrowthAnalyzer          ││
│  │  POST /analyze/death-attribution → DeathAttributionAnalyzer        ││
│  │  POST /analyze/squad-synergy     → SquadSynergyAnalyzer            ││
│  │  POST /analyze/build-execution   → BuildExecutionAnalyzer          ││
│  │  POST /analyze/critical-moments  → CriticalMomentsAnalyzer         ││
│  └─────────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         AI分析引擎层 (Python)                            │
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │ AIAnalysisService (统一入口)                                        ││
│  │   ├── analyze_personal_growth()   → PersonalGrowthAnalyzer         ││
│  │   ├── analyze_death_attribution() → DeathAttributionAnalyzer       ││
│  │   ├── analyze_squad_synergy()     → SquadSynergyAnalyzer           ││
│  │   ├── analyze_build_execution()   → BuildExecutionAnalyzer         ││
│  │   └── analyze_critical_moments()  → CriticalMomentsAnalyzer        ││
│  └─────────────────────────────────────────────────────────────────────┘│
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │ 数据聚合层: FightStatsAggregator / EiJsonExtractor / SquadAggregator││
│  └─────────────────────────────────────────────────────────────────────┘│
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │ AI编排层: AIOrchestrator.analyze_with_llm()                         ││
│  │   → PromptTemplateRegistry (9个模板)                                ││
│  │   → ResponseOptimizer / ResponseAdjuster / QualityEvaluator         ││
│  │   → DeepSeek/OpenAI API                                            ││
│  └─────────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           数据层 (SQLite)                                │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐   │
│  │   fights     │ │ fight_stats  │ │  ei_player   │ │   builds     │   │
│  │  (战斗元数据) │ │  (46+统计字段)│ │  (EI原始JSON)│ │ (Build配置)  │   │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘   │
│  ┌──────────────┐                                                      │
│  │  ai_reports  │  ← 新增报告类型: personal_growth/death_attribution/ │   │
│  │  (AI报告表)   │                    squad_synergy/build_execution/   │   │
│  │               │                    critical_moments                  │   │
│  └──────────────┘                                                      │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 数据流程图

```
┌──────────┐    选择分析类型    ┌──────────────┐
│  用户    │ ────────────────→ │  前端界面     │
└──────────┘                   └──────┬───────┘
                                      │ 调用API
                                      ▼
                             ┌────────────────┐
                             │  FastAPI路由    │
                             │  ai.py          │
                             └───────┬────────┘
                                     │ 分发到对应分析器
                                     ▼
                    ┌────────────────────────────────┐
                    │      AIAnalysisService          │
                    │  (统一入口，管理分析器生命周期)  │
                    └───────────────┬────────────────┘
                                    │
            ┌───────────────────────┼───────────────────────┐
            ▼                       ▼                       ▼
   ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
   │  规则分析引擎    │    │  数据聚合层      │    │  LLM增强层      │
   │  (实时计算)      │◄───│  DB查询/JSON提取 │───►│  DeepSeek API   │
   │  无外部依赖      │    │  46+字段/原始JSON│    │  提示词模板驱动  │
   └─────────────────┘    └─────────────────┘    └─────────────────┘
            │                       │                       │
            └───────────────────────┼───────────────────────┘
                                    ▼
                           ┌────────────────┐
                           │  结果融合层     │
                           │  rule_result   │
                           │  + llm_result  │
                           └───────┬────────┘
                                   │ 可选保存报告
                                   ▼
                          ┌────────────────┐
                          │   ai_reports   │
                          │   (SQLite)     │
                          └───────┬────────┘
                                  │ 返回结果
                                  ▼
                           ┌────────────────┐
                           │    前端展示     │
                           │  图表/建议/详情 │
                           └────────────────┘
```

### 2.3 分析器内部流程（以成长档案为例）

```
PersonalGrowthAnalyzer.analyze(account)
    │
    ├──► FightStatsAggregator.get_player_history(account) → 历史记录
    │         └─► DB查询: fight_stats JOIN fights WHERE account=?
    │
    ├──► _calculate_dimension_scores() → 六维得分
    │         ├─► 输出能力: damage/dps/power_damage/condi_damage/critical_rate
    │         ├─► 生存能力: damage_taken/blocked/evaded/dodge/down/dead
    │         ├─► 辅助贡献: healing/resurrects/cleanse/strips
    │         ├─► Buff管理: might/quickness/alacrity/fury uptime
    │         ├─► 控制能力: cc_duration/cc_count/interrupts/stun_break
    │         └─► 站位意识: stack_dist/dist_to_com/flanking_rate
    │
    ├──► _calculate_percentiles() → 公会百分位
    │         └─► 与同职业公会成员对比排名
    │
    ├──► _calculate_trends() → 趋势分析
    │         └─► 前半段vs后半段对比
    │
    ├──► _generate_suggestions() → 规则建议
    │         ├─► 弱维度改进建议
    │         ├─► 改善趋势鼓励
    │         └─► 强维度表扬
    │
    └──► _llm_enhance() → LLM增强（可选）
              └─► AIOrchestrator + personal_growth_v1模板
```

---

## 3. 核心算法说明

### 3.1 六维战力评分算法

**输入**: 玩家历史N场战斗的 `fight_stats` 记录

**输出**: 6个维度的0-100分评分

```
维度得分计算:
1. 对维度内各字段取算术平均值作为单场维度值
   dimension_value = Σ(field_value) / count(fields)

2. 历史均值作为原始分
   raw_score = Σ(dimension_value_per_fight) / count(fights)

3. 映射到0-100分（后续可引入职业基准值校准）
   score = clamp(raw_score / baseline * 100, 0, 100)
```

### 3.2 公会百分位算法

**输入**: 玩家某维度值 + 同职业所有玩家的该维度值列表

**输出**: 0-100的百分位排名

```python
def calculate_player_percentile(player_value, guild_values):
    if not guild_values:
        return 50
    count = len(guild_values)
    below = sum(1 for v in guild_values if v < player_value)
    return int((below / count) * 100)
```

### 3.3 趋势判断算法

**输入**: 时间序列数据 [v1, v2, ..., vn]

**输出**: improving / declining / stable

```python
def compute_trend(values):
    if len(values) < 5:
        return "stable"
    mid = len(values) // 2
    first_half = mean(values[:mid])
    second_half = mean(values[mid:])
    diff_pct = (second_half - first_half) / max(first_half, 1)
    
    if diff_pct > 0.15:   return "improving"
    if diff_pct < -0.15:  return "declining"
    return "stable"
```

### 3.4 死亡归因分类算法

基于启发式规则的多权重分类：

| 归因类型 | 触发条件 | 权重计算 |
|---------|---------|---------|
| 走位失误 | dist_to_com > 800 | weight = (dist - 800) / 400 |
| Buff断档 | protection < 30% 且 stability < 20% | weight = 1 - (prot+stab)/100 |
| 被集火 | damage_taken > 500k 且 防御动作 < 3 | weight = dt / 1,000,000 |
| 技能未交 | dodge == 0 且 down_count > 0 | weight = 0.7 |
| 控制链 | received_cc > 5000ms 且 removed < 1000ms | weight = cc / 10000 |
| 治疗缺口 | damage_taken > 800k | weight = (dt - 800k) / 400k |

选择权重最高的原因作为主要归因。

### 3.5 小队协同评分算法

```
synergy_score = 50                              # 基础分
+ (2~4输出职业 ? 15 : 0)                        # 角色配比
+ (1~2辅助职业 ? 15 : 0)
+ (≥1控制职业 ? 10 : 0)
+ complement_score * 0.1                        # Buff互补
+ (avg_might > 70% ? 5 : 0)                     # Buff覆盖
+ (avg_quickness > 50% ? 5 : 0)
= clamp(score, 0, 100)
```

### 3.6 Build执行验证算法

1. **Build类型推断**: 基于Build描述 + 实际伤害占比（直伤/症状/治疗）
2. **期望指标匹配**: 根据Build类型设置理论期望值
3. **差距计算**: `gap = expected - actual`
4. **状态判定**: pass (≥80%期望) / fail (<80%期望) / warn / info
5. **总分**: `pass_count / total_scored * 100`

---

## 4. API设计文档

### 4.1 新增端点总览

| 端点 | 方法 | 功能 | 保存报告 |
|------|------|------|---------|
| `/api/v1/ai/analyze/personal-growth` | POST | 个人战力成长档案 | ✅ |
| `/api/v1/ai/analyze/death-attribution` | POST | 死亡归因与生存分析 | ✅ |
| `/api/v1/ai/analyze/squad-synergy` | POST | 小队协同效能诊断 | ✅ |
| `/api/v1/ai/analyze/build-execution` | POST | Build执行效能验证 | ✅ |
| `/api/v1/ai/analyze/critical-moments` | POST | 战斗关键片段复盘 | ✅ |

### 4.2 个人战力成长档案

**请求**:
```http
POST /api/v1/ai/analyze/personal-growth?account=user.1234&fight_count=30&save_report=true
```

**响应**:
```json
{
  "success": true,
  "report_id": 42,
  "analysis_type": "personal_growth",
  "data": {
    "account": "user.1234",
    "profession": "Firebrand",
    "analysis_period": {
      "fight_count": 30,
      "first_fight": "2026-04-15T20:00:00",
      "last_fight": "2026-05-15T21:30:00"
    },
    "dimension_scores": {
      "damage_output": {"score": 45, "label": "输出能力", "trend": "improving"},
      "survival": {"score": 72, "label": "生存能力", "trend": "stable"},
      "support": {"score": 88, "label": "辅助贡献", "trend": "improving"},
      "buff_management": {"score": 65, "label": "Buff管理", "trend": "stable"},
      "cc_control": {"score": 38, "label": "控制能力", "trend": "declining"},
      "positioning": {"score": 55, "label": "站位意识", "trend": "improving"}
    },
    "percentiles": {
      "damage_output": 25,
      "survival": 60,
      "support": 85,
      "buff_management": 45,
      "cc_control": 20,
      "positioning": 40
    },
    "trends": {
      "overall": "improving",
      "dps_trend": "improving",
      "survival_trend": "stable",
      "score_trend": "improving",
      "confidence": 90
    },
    "suggestions": [
      {
        "category": "priority",
        "dimension": "控制能力",
        "score": 38,
        "message": "控制能力较弱（38分），建议重点提升",
        "actions": ["在敌方读条时使用打断技能", "配合团队CC链", "保留解控技能"]
      },
      {
        "category": "strength",
        "dimension": "辅助贡献",
        "percentile": 85,
        "message": "辅助贡献是突出优势（公会前15%），可指导他人"
      }
    ],
    "overall_score": 60,
    "_analysis_mode": "rule_based"
  }
}
```

### 4.3 死亡归因与生存分析

**请求**:
```http
POST /api/v1/ai/analyze/death-attribution?account=user.1234&save_report=true
```

**响应**:
```json
{
  "success": true,
  "report_id": 43,
  "analysis_type": "death_attribution",
  "data": {
    "account": "user.1234",
    "death_stats": {
      "total_fights": 20,
      "fights_with_death": 8,
      "death_rate": 40.0,
      "avg_damage_taken": 850000,
      "high_death_fights": [...]
    },
    "attributions": [
      {
        "fight_id": 123,
        "primary_reason": "positioning_error",
        "primary_label": "走位失误",
        "confidence": 0.85,
        "all_reasons": ["positioning_error", "buff_gap"],
        "weights": {"positioning_error": 0.85, "buff_gap": 0.35}
      }
    ],
    "suggestions": [
      {
        "priority": "high",
        "issue": "走位失误",
        "message": "3次死亡与脱离团队有关，请紧跟指挥官标记",
        "actions": ["团战时保持与堆叠点600码以内", "使用小地图观察指挥官位置"]
      }
    ],
    "survival_score": 55
  }
}
```

### 4.4 小队协同效能诊断

**请求**:
```http
POST /api/v1/ai/analyze/squad-synergy?fight_id=100&group_id=1&save_report=true
```

**响应**:
```json
{
  "success": true,
  "report_id": 44,
  "analysis_type": "squad_synergy",
  "data": {
    "fight_id": 100,
    "squad_count": 3,
    "squads": [
      {
        "group_id": 1,
        "member_count": 5,
        "members": [...],
        "role_distribution": {"damage": 2, "support": 2, "control": 1},
        "squad_metrics": {
          "total_damage": 2500000,
          "total_healing": 1800000,
          "avg_might_uptime": 75.5,
          "avg_quickness_uptime": 62.0
        },
        "buff_analysis": {
          "has_quickness_provider": true,
          "has_healer": true,
          "missing_roles": [],
          "complement_score": 100
        },
        "synergy_score": 85,
        "suggestions": []
      }
    ]
  }
}
```

### 4.5 Build执行效能验证

**请求**:
```http
POST /api/v1/ai/analyze/build-execution?account=user.1234&build_id=5&save_report=true
```

**响应**:
```json
{
  "success": true,
  "report_id": 45,
  "analysis_type": "build_execution",
  "data": {
    "account": "user.1234",
    "profession": "Weaver",
    "build_type": "power",
    "execution_check": {
      "checks": [
        {"check": "power_damage_ratio", "actual": 65.0, "expected": 70.0, "status": "warn", "gap": 5.0},
        {"check": "critical_rate", "actual": 55.0, "expected": 60.0, "status": "fail", "gap": 5.0},
        {"check": "skill_engagement", "actual": "武器切换12次, 技能施放率75%", "status": "pass"}
      ],
      "pass_count": 1,
      "fail_count": 1,
      "overall_score": 50
    },
    "equipment_check": {
      "has_food": true,
      "has_utility": false,
      "issues": ["未使用扳手/磨刀石（Utility），建议携带"],
      "equipment_score": 80
    },
    "execution_score": 50
  }
}
```

### 4.6 战斗关键片段复盘

**请求**:
```http
POST /api/v1/ai/analyze/critical-moments?fight_id=100&save_report=true
```

**响应**:
```json
{
  "success": true,
  "report_id": 46,
  "analysis_type": "critical_moments",
  "data": {
    "fight_id": 100,
    "fight_info": {
      "map_name": "Red Desert Borderlands",
      "duration_sec": 180
    },
    "moments": [
      {
        "type": "opening_burst",
        "label": "开场爆发期",
        "time_start": 0,
        "time_end": 36,
        "importance": "high",
        "evaluations": [
          {
            "account": "user.1234",
            "performance": {"dps": 4200, "might_uptime": 65, "rating": "excellent"},
            "note": "开场爆发期应全力输出并确保吃到团队增益"
          }
        ]
      },
      {
        "type": "crisis_moment",
        "label": "危机时刻",
        "importance": "critical",
        "evaluations": [...]
      }
    ],
    "moment_count": 4
  }
}
```

---

## 5. 数据资产与扩展

### 5.1 现有数据资产

**`fight_stats` 表（46+标量字段）**:
- 输出: damage, dps, power_damage, condi_damage, breakbar_damage, critical_rate, flanking_rate
- 生存: damage_taken, blocked_count, evaded_count, dodge_count, down_count, dead_count
- 辅助: healing, resurrects, condi_cleanse_ally, boon_strips_ally
- Buff: might_uptime, quickness_uptime, alacrity_uptime, fury_uptime, protection_uptime, stability_uptime
- 控制: applied_cc_duration, applied_cc_count, interrupts, stun_break
- 站位: stack_dist, dist_to_com
- 其他: skill_cast_uptime, wasted, saved, swap_count

**`ei_player` 表（原始JSON）**:
- `rotation_json`: 技能循环时间线
- `death_recap_json`: 死亡回放（伤害来源时间线）
- `buff_uptimes_json`: Buff覆盖详情
- `weapons_json`: 武器配置
- `consumables_json`: 食物/扳手

### 5.2 数据字段扩展方案（预留）

| 扩展字段 | 目标表 | 说明 | 优先级 |
|---------|--------|------|--------|
| `damage_per_second_timeline` | ei_player | 每秒DPS时间线（用于关键片段） | 中 |
| `death_timestamp_ms` | ei_player | 死亡发生时间戳 | 高 |
| `squad_comp_history` | fight_stats | 历史小队配置JSON | 低 |
| `peer_comparison_snapshot` | ai_reports | 每次分析的公会快照 | 低 |

---

## 6. 前端组件规划

### 6.1 新增可视化组件

| 组件 | 用途 | 库/方案 |
|------|------|---------|
| `GrowthRadarChart` | 六维战力雷达图 | Chart.js / ECharts |
| `TrendLineChart` | 历史趋势折线图 | Chart.js |
| `PercentileBar` | 公会百分位条形图 | CSS/custom |
| `DeathTimeline` | 死亡归因时间线 | Custom SVG |
| `SquadSynergyGrid` | 小队协同矩阵 | Custom CSS Grid |
| `BuildChecklist` | Build验证检查清单 | Custom |
| `CombatTimeline` | 战斗关键片段时间轴 | Custom |
| `SuggestionCard` | 建议卡片组件 | Tailwind |

### 6.2 页面布局建议

在现有 `DataAiAnalysisView.vue` 基础上扩展：

```
┌────────────────────────────────────────────────────────────┐
│  顶部导航栏: [战斗分析] [玩家分析] [成长档案] [死亡归因] [小队协同] [Build验证] [关键片段] │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  根据选中标签展示对应分析面板                                │
│                                                            │
│  成长档案面板: 雷达图 + 趋势图 + 建议列表                    │
│  死亡归因面板: 统计卡片 + 归因分布 + 训练方案                │
│  小队协同面板: 小队列表 + 角色分布 + Buff互补状态            │
│  Build验证面板: 检查清单 + 装备状态 + 优化路径               │
│  关键片段面板: 时间轴 + 关键时刻卡片 + 评估详情              │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

---

## 7. 实施计划与时间线

### 7.1 里程碑划分

```
Week 1 (已完成): 后端基础设施
├── ✅ AI模块前后端联通测试 (12/12通过)
├── ✅ 数据聚合层 (FightStatsAggregator/EiJsonExtractor/SquadAggregator)
├── ✅ 5个分析器核心类实现
├── ✅ 5个提示词模板注册
├── ✅ 集成服务层 (AIAnalysisService)
└── ✅ 5个新API端点注册

Week 2: AI + LLM链路完善
├── 后端分析器规则算法调优（基于真实数据验证）
├── LLM增强链路测试与Prompt调优
├── 数据字段扩展（death_timestamp等）
├── 后端单元测试覆盖
└── API文档完善

Week 3: 前端页面开发
├── GrowthRadarChart / TrendLineChart 实现
├── 死亡归因 / 小队协同 / Build验证 / 关键片段 面板
├── 与后端新API对接
├── 报告列表支持新类型筛选
└── 响应式适配与交互优化

Week 4: 系统集成与测试
├── 端到端测试（E2E）
├── 性能优化（大数据量查询优化）
├── 边缘情况处理（无数据/数据不足）
├── 用户验收测试
└── 文档完善

Week 5: 上线与迭代
├── 生产环境部署
├── 收集用户反馈
├── 第一轮迭代优化
└── 功能扩展规划
```

### 7.2 当前进度

| 任务 | 状态 | 完成度 |
|------|------|--------|
| 后端数据聚合层 | ✅ 完成 | 100% |
| 5个分析器核心类 | ✅ 完成 | 100% |
| 提示词模板扩展 | ✅ 完成 | 100% |
| 集成服务层 | ✅ 完成 | 100% |
| API路由扩展 | ✅ 完成 | 100% |
| 后端导入测试 | ✅ 通过 | 100% |
| 前端可视化组件 | ⏳ 待开发 | 0% |
| 前端API对接 | ⏳ 待开发 | 0% |
| 算法调优 | ⏳ 待验证 | 0% |
| 端到端测试 | ⏳ 待执行 | 0% |

### 7.3 风险与对策

| 风险 | 影响 | 对策 |
|------|------|------|
| 数据库无足够历史数据 | 分析结果为空/不准 | 引导用户先导入战斗日志；降低最小分析场次阈值 |
| LLM响应质量不稳定 | AI建议不可用 | 规则引擎兜底；Prompt持续迭代；质量评分过滤 |
| 前端渲染性能（大数据量） | 页面卡顿 | 后端分页/采样；前端虚拟滚动；Web Worker |
| 缓存不生效（Python 3.13） | 运行旧代码 | 修改后手动清除 `__pycache__` |

---

## 8. 与现有系统的兼容性

### 8.1 数据库兼容

- 复用现有 `ai_reports` 表，`report_type` 字段支持新增5个类型
- 无Schema变更需求

### 8.2 API兼容

- 新增端点为独立路径，不影响现有端点
- 现有 `analyze/fight`, `analyze/member`, `analyze/build` 保持不动

### 8.3 前端兼容

- 新增分析面板为独立组件，不影响现有布局
- 报告列表已支持按 `report_type` 筛选，自动适配新类型

---

## 9. 附录

### 9.1 新增文件清单

```
backend/app/services/ai_analysis/
├── __init__.py
├── data_aggregator.py          # 数据聚合层
├── ai_analysis_service.py      # 集成服务层
└── analyzers/
    ├── __init__.py
    ├── personal_growth.py      # 个人成长档案
    ├── death_attribution.py    # 死亡归因
    ├── squad_synergy.py        # 小队协同
    ├── build_execution.py      # Build验证
    └── critical_moments.py     # 关键片段

backend/app/core/ai_prompt_templates.py  # 已扩展5个新模板
backend/app/routers/ai/ai.py             # 已扩展5个新端点
```

### 9.2 新增API端点清单

```
POST /api/v1/ai/analyze/personal-growth
POST /api/v1/ai/analyze/death-attribution
POST /api/v1/ai/analyze/squad-synergy
POST /api/v1/ai/analyze/build-execution
POST /api/v1/ai/analyze/critical-moments
```
