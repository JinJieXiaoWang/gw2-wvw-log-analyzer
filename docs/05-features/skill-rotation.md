# 技能循环功能设计文档

> **版本**: v2.0
> **更新日期**: 2026-05-05
> **整合责任人**: 系统文档维护团队
> **变更摘要**: 精简为与实际代码完全一致，聚焦数据来源与前端组件

---

## 文档信息

| 项目 | 内容 |
|------|------|
| 版本 | v2.0 |
| 更新日期 | 2026-05-05 |
| 文档类型 | 功能模块设计文档 |
| 适用对象 | 前后端开发团队 |

---

## 1. 功能概述

技能循环功能用于展示玩家在 WvW 战斗中的技能施放序列，帮助玩家分析和优化自己的技能使用策略。

---

## 2. API 端点

### 2.1 获取玩家技能循环

| 项目 | 内容 |
|------|------|
| 端点 | `GET /api/v1/ei-analysis/{log_id}/player/{account}/rotation` |
| 路由文件 | `app/routers/ei_analysis.py` |

**路径参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| log_id | integer | 是 | 日志 ID |
| account | string | 是 | 玩家账号名 |

**数据来源**：
- 技能循环数据直接从 `ei_player.rotation_json` 字段中读取
- 该字段由 EI 解析器在解析日志时生成，存储为 JSON 格式

---

## 3. 前端组件

技能循环相关的前端 Vue 组件位于 `src/components/skillRotation/` 目录：

| 组件 | 路径 | 功能 |
|------|------|------|
| ActualRotation | `skillRotation/ActualRotation.vue` | 实际技能循环展示 |
| IdealRotation | `skillRotation/IdealRotation.vue` | 理想技能循环对比 |
| SkillTimeline | `skillRotation/SkillTimeline.vue` | 技能时间轴可视化 |

---

## 4. 数据说明

### 4.1 `ei_player.rotation_json` 字段

该字段存储 EI 解析器输出的原始技能循环 JSON 数据，包含：

- 技能 ID
- 施放时间戳
- 施放持续时间
- 技能状态（成功 / 取消 / 打断等）

### 4.2 数据流

```
EI 解析器生成 rotation_json
         │
         ▼
存入数据库 ei_player.rotation_json
         │
         ▼
后端 API 直接读取并返回
         │
         ▼
前端组件渲染技能循环可视化
```

---

## 5. 文件清单

| 文件路径 | 说明 |
|---------|------|
| `app/routers/ei_analysis.py` | 技能循环 API 路由 |
| `app/models/ei_player.py` | EI 玩家模型（含 rotation_json） |
| `src/components/skillRotation/ActualRotation.vue` | 实际循环组件 |
| `src/components/skillRotation/IdealRotation.vue` | 理想循环组件 |
| `src/components/skillRotation/SkillTimeline.vue` | 时间轴组件 |
