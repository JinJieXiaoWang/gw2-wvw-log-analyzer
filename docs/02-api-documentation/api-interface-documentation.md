# GW2 WvW 日志系统 API 接口文档

> **版本**: v3.0  
> **更新日期**: 2026-05-05  
> **端点总数**: 129（覆盖 112+ 唯一路径）  
> **适用范围**: 后端 FastAPI 全部路由模块

---

## 历史版本记录

| 版本 | 日期 | 说明 |
|------|------|------|
| v1.0.0 | 2026-05-01 | 初始版本，基于 OpenAPI Schema 自动生成，共 162 个端点 |
| v3.0 | 2026-05-05 | 重构版本，按实际 FastAPI 路由模块重新组织，修正路径前缀错误，补充认证说明与已知问题附录 |

---

## 目录

- [全局约定](#全局约定)
- [1. 认证](#1-认证)
- [2. 日志管理](#2-日志管理)
- [3. AI 分析](#3-ai-分析)
- [4. 数据看板](#4-数据看板)
- [5. 出勤统计](#5-出勤统计)
- [6. EI 分析（精简）](#6-ei-分析精简)
- [7. EI 完整报告](#7-ei-完整报告)
- [8. WvW 战斗报告](#8-wvw-战斗报告)
- [9. 战斗数据](#9-战斗数据)
- [10. 评分系统](#10-评分系统)
- [11. Build 图书馆](#11-build-图书馆)
- [12. 字典管理](#12-字典管理)
- [13. 用户管理](#13-用户管理)
- [14. 系统监控](#14-系统监控)
- [15. 性能监控](#15-性能监控)
- [16. 存储管理](#16-存储管理)
- [17. 设置管理](#17-设置管理)
- [18. 游戏数据](#18-游戏数据)
- [19. BDCode 解析](#19-bdcode-解析)
- [20. 测试工具](#20-测试工具)
- [附录 A：已知问题](#附录-a已知问题)
- [附录 B：通用响应结构](#附录-b通用响应结构)
- [附录 C：常见 HTTP 状态码](#附录-c常见-http-状态码)
- [附录 D：分页参数约定](#附录-d分页参数约定)
- [附录 E：前端集成注意事项](#附录-e前端集成注意事项)

---

## 全局约定

### Base URL

| 环境 | URL |
|------|-----|
| 开发环境 | `http://localhost:8000` |
| 生产环境 | 以实际部署地址为准 |

### 全局 API 前缀

- **默认前缀**: `/api/v1`
- **例外**: `bdcode` 模块使用独立前缀 `/api/bdcode`（不带 `/api/v1`）

### 认证方式

- **类型**: JWT Bearer Token
- **有效期**: 2 小时
- **获取方式**: `POST /api/v1/auth/login`
- **使用方式**: 在请求头中携带

```
Authorization: Bearer <access_token>
```

### 响应格式

除 `ei_report`、`wvw_report`、`bdcode` 三个模块使用独立响应模型外，其余所有模块均统一包装为 `ApiResponse`（来自 `app.schemas.common`）：

```json
{
  "success": true,
  "message": "操作成功",
  "data": { ... },
  "error_code": null,
  "timestamp": "2026-05-05T05:11:13",
  "code": 200
}
```

### 访问控制标识

| 标识 | 含义 |
|------|------|
| 🔒 | 需要 JWT 认证 |
| 🔒👑 | 需要超级管理员权限 |
| 🌐 | 公开访问（无需认证） |

---

## 1. 认证

**模块文件**: `app/routers/auth.py`  
**路由前缀**: `/auth`  
**端点数量**: 5

| 序号 | Method | 路径 | 认证 | 功能简述 |
|------|--------|------|------|----------|
| 1.1 | POST | `/api/v1/auth/login` | 🌐 | 管理员登录，返回 JWT Token |
| 1.2 | POST | `/api/v1/auth/logout` | 🔒 | 管理员登出（客户端清除 Token） |
| 1.3 | GET | `/api/v1/auth/status` | 🔒 | 获取当前登录状态 |
| 1.4 | GET | `/api/v1/auth/profile` | 🔒 | 获取当前用户信息 |
| 1.5 | POST | `/api/v1/auth/change-password` | 🔒 | 修改当前用户密码 |

---

## 2. 日志管理

**模块文件**: `app/routers/logs.py`  
**路由前缀**: `/logs`  
**端点数量**: 17

| 序号 | Method | 路径 | 认证 | 功能简述 |
|------|--------|------|------|----------|
| 2.1 | GET | `/api/v1/logs` | 🔒 | 获取日志列表（支持分页、筛选） |
| 2.2 | POST | `/api/v1/logs` | 🔒 | 上传日志文件（.zevtc / .evtc） |
| 2.3 | GET | `/api/v1/logs/{log_id}` | 🔒 | 获取指定日志详情 |
| 2.4 | PUT | `/api/v1/logs/{log_id}` | 🔒 | 更新日志信息 |
| 2.5 | DELETE | `/api/v1/logs/{log_id}` | 🔒 | 删除指定日志 |
| 2.6 | POST | `/api/v1/logs/{log_id}/parse` | 🔒 | 解析日志文件（触发 EI 解析） |
| 2.7 | GET | `/api/v1/logs/{log_id}/parse/progress` | 🔒 | 获取日志解析进度 |
| 2.8 | GET | `/api/v1/logs/{log_id}/parse/result` | 🔒 | 获取解析结果 |
| 2.9 | POST | `/api/v1/logs/{log_id}/validate` | 🔒 | 验证解析数据完整性 |
| 2.10 | POST | `/api/v1/logs/batch-parse` | 🔒 | 创建批量解析任务 |
| 2.11 | GET | `/api/v1/logs/batch-parse` | 🔒 | 获取批量解析任务列表 |
| 2.12 | GET | `/api/v1/logs/batch-parse/{task_id}` | 🔒 | 获取指定批量任务详情 |
| 2.13 | GET | `/api/v1/logs/batch-parse/{task_id}/progress` | 🔒 | 获取批量任务进度 |
| 2.14 | GET | `/api/v1/logs/batch-parse/{task_id}/result` | 🔒 | 获取批量任务结果 |
| 2.15 | DELETE | `/api/v1/logs/batch-parse/{task_id}` | 🔒 | 删除批量解析任务 |
| 2.16 | POST | `/api/v1/logs/batch-delete` | 🔒 | 批量删除日志 |
| 2.17 | GET | `/api/v1/logs/export` | 🔒 | 导出日志数据 |

---

## 3. AI 分析

**模块文件**: `app/routers/ai.py`  
**路由前缀**: `/ai`  
**端点数量**: 7

| 序号 | Method | 路径 | 认证 | 功能简述 |
|------|--------|------|------|----------|
| 3.1 | GET | `/api/v1/ai/reports` | 🔒 | 获取 AI 分析报告列表（支持分页、筛选） |
| 3.2 | GET | `/api/v1/ai/reports/{report_id}` | 🔒 | 获取指定 AI 报告详情 |
| 3.3 | DELETE | `/api/v1/ai/reports/{report_id}` | 🔒 | 删除指定 AI 报告 |
| 3.4 | POST | `/api/v1/ai/analyze/fight/{fight_id}` | 🔒 | AI 分析指定战斗 |
| 3.5 | POST | `/api/v1/ai/analyze/build/{build_id}` | 🔒 | AI 分析指定 Build |
| 3.6 | GET | `/api/v1/ai/trend` | 🔒 | 获取 AI 趋势分析数据 |
| 3.7 | GET | `/api/v1/ai/suggestions` | 🔒 | 获取 AI 优化建议 |

---

## 4. 数据看板

**模块文件**: `app/routers/dashboard.py`  
**路由前缀**: `/dashboard`  
**端点数量**: 9

| 序号 | Method | 路径 | 认证 | 功能简述 |
|------|--------|------|------|----------|
| 4.1 | GET | `/api/v1/dashboard/overview` | 🔒 | 获取核心 KPI 概览 |
| 4.2 | GET | `/api/v1/dashboard/trends` | 🔒 | 获取时间趋势数据 |
| 4.3 | GET | `/api/v1/dashboard/profession-distribution` | 🔒 | 获取职业分布统计 |
| 4.4 | GET | `/api/v1/dashboard/map-stats` | 🔒 | 获取地图统计 |
| 4.5 | GET | `/api/v1/dashboard/top-players` | 🔒 | 获取玩家排行 |
| 4.6 | GET | `/api/v1/dashboard/recent-fights` | 🔒 | 获取最近战斗 |
| 4.7 | GET | `/api/v1/dashboard/parse-status` | 🔒 | 获取解析状态分布 |
| 4.8 | GET | `/api/v1/dashboard/ai-score-distribution` | 🔒 | 获取 AI 评分分布 |
| 4.9 | GET | `/api/v1/dashboard/buff-overview` | 🔒 | 获取 Buff 覆盖率概览 |

---

## 5. 出勤统计

**模块文件**: `app/routers/attendance.py`  
**路由前缀**: `/attendance`  
**端点数量**: 4

| 序号 | Method | 路径 | 认证 | 功能简述 |
|------|--------|------|------|----------|
| 5.1 | GET | `/api/v1/attendance/accounts` | 🔒 | 获取账号出勤列表 |
| 5.2 | GET | `/api/v1/attendance/accounts/{account_name}` | 🔒 | 获取指定账号出勤详情 |
| 5.3 | GET | `/api/v1/attendance/accounts/{account_name}/characters/{character_name}` | 🔒 | 获取角色战斗记录 |
| 5.4 | GET | `/api/v1/attendance/filters` | 🔒 | 获取出勤筛选选项 |

---

## 6. EI 分析（精简）

**模块文件**: `app/routers/ei_analysis.py`  
**路由前缀**: `/ei-analysis`  
**端点数量**: 3

| 序号 | Method | 路径 | 认证 | 功能简述 |
|------|--------|------|------|----------|
| 6.1 | GET | `/api/v1/ei-analysis/{log_id}` | 🔒 | 获取日志战斗摘要 |
| 6.2 | GET | `/api/v1/ei-analysis/{log_id}/player/{account}` | 🔒 | 获取玩家在指定日志中的详细数据 |
| 6.3 | GET | `/api/v1/ei-analysis/{log_id}/player/{account}/rotation` | 🔒 | 获取玩家技能循环 |

---

## 7. EI 完整报告

**模块文件**: `app/routers/ei_report.py`  
**路由前缀**: `/ei-report`  
**响应模型**: 独立响应模型（非 `ApiResponse` 统一包装）  
**端点数量**: 13

| 序号 | Method | 路径 | 认证 | 功能简述 |
|------|--------|------|------|----------|
| 7.1 | GET | `/api/v1/ei-report/logs` | 🔒 | 获取已导入的 EI 报告列表 |
| 7.2 | GET | `/api/v1/ei-report/logs/{log_id}/meta` | 🔒 | 获取 EI 报告元数据 |
| 7.3 | GET | `/api/v1/ei-report/logs/{log_id}/summary` | 🔒 | 获取 EI 报告摘要（~1-5MB） |
| 7.4 | GET | `/api/v1/ei-report/logs/{log_id}/data` | 🔒 | 流式返回完整 `_logData`（gzip 压缩） |
| 7.5 | GET | `/api/v1/ei-report/logs/{log_id}/graph` | 🔒 | 流式返回 `_graphData`（gzip 压缩） |
| 7.6 | GET | `/api/v1/ei-report/logs/{log_id}/players/{player_index}` | 🔒 | 获取指定玩家完整数据 |
| 7.7 | GET | `/api/v1/ei-report/logs/{log_id}/targets/{target_index}` | 🔒 | 获取指定目标完整数据 |
| 7.8 | GET | `/api/v1/ei-report/logs/{log_id}/phases/{phase_index}` | 🔒 | 获取指定阶段数据与统计 |
| 7.9 | GET | `/api/v1/ei-report/logs/{log_id}/players/{player_index}/graph` | 🔒 | 获取玩家图表数据 |
| 7.10 | GET | `/api/v1/ei-report/logs/{log_id}/targets/{target_index}/graph` | 🔒 | 获取目标图表数据 |
| 7.11 | POST | `/api/v1/ei-report/logs/{log_id}/import` | 🔒 | 从 EI HTML 导入报告 |
| 7.12 | GET | `/api/v1/ei-report/logs/{log_id}/unified` | 🔒 | 获取统一 EI 数据（自动选择数据源） |
| 7.13 | DELETE | `/api/v1/ei-report/logs/{log_id}` | 🔒 | 删除 EI 报告 |

---

## 8. WvW 战斗报告

**模块文件**: `app/routers/wvw_report.py`  
**路由前缀**: `/wvw-report`  
**响应模型**: 独立响应模型（非 `ApiResponse` 统一包装）  
**端点数量**: 8

| 序号 | Method | 路径 | 认证 | 功能简述 |
|------|--------|------|------|----------|
| 8.1 | GET | `/api/v1/wvw-report/logs` | 🔒 | 获取不同数据源格式的日志列表 |
| 8.2 | GET | `/api/v1/wvw-report/logs/{log_id}/summary` | 🔒 | 获取战斗概览（squad composition、核心指标） |
| 8.3 | GET | `/api/v1/wvw-report/logs/{log_id}/players` | 🔒 | 获取战斗玩家列表（含表现排行） |
| 8.4 | GET | `/api/v1/wvw-report/logs/{log_id}/players/{player_id}` | 🔒 | 获取指定玩家详细数据 |
| 8.5 | GET | `/api/v1/wvw-report/logs/{log_id}/targets` | 🔒 | 获取目标列表 |
| 8.6 | GET | `/api/v1/wvw-report/logs/{log_id}/phases` | 🔒 | 获取阶段列表 |
| 8.7 | GET | `/api/v1/wvw-report/logs/{log_id}/timeline` | 🔒 | 获取战斗时间线 |
| 8.8 | GET | `/api/v1/wvw-report/logs/{log_id}/skill-map` | 🔒 | 获取技能映射表 |

---

## 9. 战斗数据

**模块文件**: `app/routers/fights.py`  
**路由前缀**: `/fights`  
**端点数量**: 4

| 序号 | Method | 路径 | 认证 | 功能简述 |
|------|--------|------|------|----------|
| 9.1 | GET | `/api/v1/fights` | 🔒 | 获取战斗列表 |
| 9.2 | GET | `/api/v1/fights/{fight_id}` | 🔒 | 获取战斗详情 |
| 9.3 | GET | `/api/v1/fights/{fight_id}/stats` | 🔒 | 获取战斗统计数据 |
| 9.4 | GET | `/api/v1/fights/by-log/{log_id}/players` | 🔒 | 获取日志关联战斗中的玩家列表 |

---

## 10. 评分系统

**模块文件**: `app/routers/scoring.py`  
**路由前缀**: `/scoring`  
**端点数量**: 2

| 序号 | Method | 路径 | 认证 | 功能简述 |
|------|--------|------|------|----------|
| 10.1 | GET | `/api/v1/scoring/rules` | 🔒 | 获取评分规则配置 |
| 10.2 | GET | `/api/v1/scoring/fight/{fight_id}` | 🔒 | 计算指定战斗的所有玩家评分 |

---

## 11. Build 图书馆

**模块文件**: `app/routers/builds.py`  
**路由前缀**: `/builds`  
**端点数量**: 5

| 序号 | Method | 路径 | 认证 | 功能简述 |
|------|--------|------|------|----------|
| 11.1 | GET | `/api/v1/builds` | 🔒 | 获取 Build 列表（支持职业、成员筛选） |
| 11.2 | GET | `/api/v1/builds/{build_id}` | 🔒 | 获取指定 Build 详情 |
| 11.3 | POST | `/api/v1/builds` | 🔒 | 创建 Build |
| 11.4 | PUT | `/api/v1/builds/{build_id}` | 🔒 | 更新 Build |
| 11.5 | DELETE | `/api/v1/builds/{build_id}` | 🔒 | 删除 Build |

---

## 12. 字典管理

**模块文件**: `app/routers/dictionary.py`  
**路由前缀**: `/dictionary`  
**端点数量**: 14

| 序号 | Method | 路径 | 认证 | 功能简述 |
|------|--------|------|------|----------|
| 12.1 | GET | `/api/v1/dictionary/types` | 🔒 | 获取字典类型列表（支持分页、状态筛选） |
| 12.2 | GET | `/api/v1/dictionary/types/all` | 🔒 | 获取所有启用的字典类型（不分页） |
| 12.3 | GET | `/api/v1/dictionary/types/{dict_id}` | 🔒 | 获取单个字典类型详情 |
| 12.4 | POST | `/api/v1/dictionary/types` | 🔒👑 | 创建字典类型 |
| 12.5 | PUT | `/api/v1/dictionary/types/{dict_id}` | 🔒👑 | 更新字典类型 |
| 12.6 | DELETE | `/api/v1/dictionary/types/{dict_id}` | 🔒👑 | 删除字典类型 |
| 12.7 | GET | `/api/v1/dictionary/data` | 🔒 | 获取字典项列表（按类型筛选） |
| 12.8 | GET | `/api/v1/dictionary/data/{dict_code}` | 🔒 | 获取单个字典项详情 |
| 12.9 | GET | `/api/v1/dictionary/options/{dict_type}` | 🌐 | 获取指定字典类型的下拉选项（公开接口） |
| 12.10 | POST | `/api/v1/dictionary/data` | 🔒👑 | 创建字典项 |
| 12.11 | PUT | `/api/v1/dictionary/data/{dict_code}` | 🔒👑 | 更新字典项 |
| 12.12 | DELETE | `/api/v1/dictionary/data/{dict_code}` | 🔒👑 | 删除字典项 |
| 12.13 | POST | `/api/v1/dictionary/reload-cache` | 🔒 | 刷新字典缓存到内存 |
| 12.14 | POST | `/api/v1/dictionary/init` | 🔒👑 | 初始化系统预置字典数据 |

---

## 13. 用户管理

**模块文件**: `app/routers/users.py`  
**路由前缀**: `/users`  
**端点数量**: 10

| 序号 | Method | 路径 | 认证 | 功能简述 |
|------|--------|------|------|----------|
| 13.1 | GET | `/api/v1/users` | 🔒👑 | 获取用户列表（仅超级管理员） |
| 13.2 | GET | `/api/v1/users/profile` | 🔒 | 获取当前用户资料 |
| 13.3 | GET | `/api/v1/users/{user_id}` | 🔒👑 | 获取指定用户详情 |
| 13.4 | POST | `/api/v1/users` | 🔒👑 | 创建用户 |
| 13.5 | PUT | `/api/v1/users/{user_id}` | 🔒👑 | 更新用户 |
| 13.6 | DELETE | `/api/v1/users/{user_id}` | 🔒👑 | 删除用户 |
| 13.7 | POST | `/api/v1/users/change-password` | 🔒 | 修改当前用户密码 |
| 13.8 | POST | `/api/v1/users/{user_id}/reset-password` | 🔒👑 | 重置指定用户密码 |
| 13.9 | POST | `/api/v1/users/{user_id}/toggle-active` | 🔒👑 | 切换用户活跃状态 |
| 13.10 | GET | `/api/v1/users/roles/list` | 🔒 | 获取角色列表 |

---

## 14. 系统监控

**模块文件**: `app/routers/monitor.py`  
**路由前缀**: `/monitor`  
**端点数量**: 5

| 序号 | Method | 路径 | 认证 | 功能简述 |
|------|--------|------|------|----------|
| 14.1 | GET | `/api/v1/monitor/errors/stats` | 🔒 | 获取错误统计 |
| 14.2 | GET | `/api/v1/monitor/errors/report` | 🔒 | 获取完整错误报告 |
| 14.3 | POST | `/api/v1/monitor/errors/clear` | 🔒 | 清空错误统计 |
| 14.4 | POST | `/api/v1/monitor/errors/export` | 🔒 | 导出错误报告 |
| 14.5 | GET | `/api/v1/monitor/health` | 🔒 | 系统健康检查 |

---

## 15. 性能监控

**模块文件**: `app/routers/monitoring.py`  
**路由前缀**: `/api/v1/monitoring`（已在 router 中定义，main.py 再叠加 `/api/v1`）  
**端点数量**: 5

| 序号 | Method | 路径 | 认证 | 功能简述 |
|------|--------|------|------|----------|
| 15.1 | GET | `/api/v1/api/v1/monitoring/performance` | 🔒 | 获取性能统计信息 |
| 15.2 | GET | `/api/v1/api/v1/monitoring/performance/summary` | 🔒 | 获取性能摘要 |
| 15.3 | POST | `/api/v1/api/v1/monitoring/performance/reset` | 🔒 | 重置性能统计 |
| 15.4 | GET | `/api/v1/api/v1/monitoring/benchmark` | 🔒 | 获取基准测试结果 |
| 15.5 | POST | `/api/v1/api/v1/monitoring/benchmark/compare` | 🔒 | 比较基准测试 |

> ⚠️ **注意**: 以上路径存在前缀重复问题，详见 [附录 A：已知问题](#附录-a已知问题)。

---

## 16. 存储管理

**模块文件**: `app/routers/storage.py`  
**路由前缀**: `/storage`  
**端点数量**: 7

| 序号 | Method | 路径 | 认证 | 功能简述 |
|------|--------|------|------|----------|
| 16.1 | GET | `/api/v1/storage/status` | 🔒 | 获取存储状态（容量、使用率） |
| 16.2 | GET | `/api/v1/storage/monitor/records` | 🔒 | 获取监控记录 |
| 16.3 | GET | `/api/v1/storage/cleanup/records` | 🔒 | 获取清理记录 |
| 16.4 | POST | `/api/v1/storage/cleanup/age` | 🔒 | 按保留天数清理过期文件 |
| 16.5 | POST | `/api/v1/storage/cleanup/storage` | 🔒 | 按存储容量清理 |
| 16.6 | POST | `/api/v1/storage/cleanup/parsed` | 🔒 | 清理已解析文件 |
| 16.7 | POST | `/api/v1/storage/monitor/record` | 🔒 | 手动记录监控数据 |

---

## 17. 设置管理

**模块文件**: `app/routers/settings.py`  
**路由前缀**: `/settings`  
**端点数量**: 3

| 序号 | Method | 路径 | 认证 | 功能简述 |
|------|--------|------|------|----------|
| 17.1 | GET | `/api/v1/settings` | 🔒 | 获取系统设置 |
| 17.2 | PUT | `/api/v1/settings` | 🔒 | 更新系统设置 |
| 17.3 | POST | `/api/v1/settings/reset` | 🔒 | 重置系统设置为默认值 |

---

## 18. 游戏数据

**模块文件**: `app/routers/game_data.py`  
**路由前缀**: `/game-data`  
**端点数量**: 1

| 序号 | Method | 路径 | 认证 | 功能简述 |
|------|--------|------|------|----------|
| 18.1 | GET | `/api/v1/game-data/info` | 🔒 | 获取游戏数据版本信息 |

---

## 19. BDCode 解析

**模块文件**: `app/routers/bdcode.py`  
**路由前缀**: `/api/bdcode`（独立前缀，不带 `/api/v1`）  
**响应模型**: 独立响应模型（`BDCodeParseResponse`、`BDCodeBatchResponse` 等）  
**端点数量**: 6

| 序号 | Method | 路径 | 认证 | 功能简述 |
|------|--------|------|------|----------|
| 19.1 | POST | `/api/bdcode/parse` | 🌐 | 解析单个 BDCode 获取完整 Build 信息 |
| 19.2 | GET | `/api/bdcode/parse/{bd_code}` | 🌐 | 通过 URL 参数解析 BDCode |
| 19.3 | POST | `/api/bdcode/validate` | 🌐 | 验证 BDCode 格式是否正确 |
| 19.4 | POST | `/api/bdcode/batch` | 🌐 | 批量解析 BDCode（最多 50 个） |
| 19.5 | GET | `/api/bdcode/stats` | 🌐 | 获取 BDCode 解析服务统计信息 |
| 19.6 | GET | `/api/bdcode/health` | 🌐 | BDCode 解析服务健康检查 |

---

## 20. 测试工具

**模块文件**: `app/routers/test_dps_report.py`  
**路由前缀**: `/test`  
**端点数量**: 1

| 序号 | Method | 路径 | 认证 | 功能简述 |
|------|--------|------|------|----------|
| 20.1 | POST | `/api/v1/test/dps-report` | 🔒 | 测试 dps.report 解析接口 |

---

## 附录 A：已知问题

### A.1 路由前缀重复

**问题**: `monitoring.py` 的 `APIRouter` 已经在模块内定义了 `prefix="/api/v1/monitoring"`，而 `main.py` 注册该 router 时再次叠加了 `settings.API_PREFIX`（即 `/api/v1`），导致实际访问路径变为 `/api/v1/api/v1/monitoring/*`。

**影响端点**:
- `/api/v1/api/v1/monitoring/performance`
- `/api/v1/api/v1/monitoring/performance/summary`
- `/api/v1/api/v1/monitoring/performance/reset`
- `/api/v1/api/v1/monitoring/benchmark`
- `/api/v1/api/v1/monitoring/benchmark/compare`

**建议**: 前端调用时请以 `/docs` 中展示的实际路径为准；后端修复方案为移除 `monitoring.py` 中 router 的 `prefix`，统一由 `main.py` 控制。

### A.2 未注册路由模块

**问题**: `app/routers/database_management.py` 存在于代码库中，但 **未在 `main.py` 中注册**，当前不可通过 HTTP 访问。

**状态**: 待后续版本决定是否启用。

### A.3 响应模型不统一

**问题**: 大部分模块使用 `ApiResponse` 统一包装，但以下三个模块使用独立响应模型：

| 模块 | 文件 | 独立模型 |
|------|------|----------|
| EI 完整报告 | `ei_report.py` | `EiFullDataResponse`、`EiGraphDataResponse`、`EiImportResponse` 等 |
| WvW 战斗报告 | `wvw_report.py` | `WvwPhasesResponse`、`WvwReportResponse` 等 |
| BDCode 解析 | `bdcode.py` | `BDCodeParseResponse`、`BDCodeBatchResponse`、`BDCodeStatsResponse`、`BDCodeValidationResponse` |

**影响**: 前端解析这三个模块的响应时，不能统一按 `ApiResponse` 结构处理，需单独适配。

### A.4 认证模块无 Refresh Token 端点

**问题**: 前端常量 `API_ENDPOINTS.AUTH.REFRESH` 定义了 `/api/v1/auth/refresh`，但后端 `auth.py` 中实际未实现该端点。Token 过期后需重新调用 `/api/v1/auth/login` 获取新 Token。

---

## 附录 B：通用响应结构

### B.1 ApiResponse 包装结构

适用于除 `ei_report`、`wvw_report`、`bdcode` 外的所有模块：

```json
{
  "success": true,
  "message": "操作成功",
  "data": { ... },
  "error_code": null,
  "timestamp": "2026-05-05T05:11:13",
  "code": 200
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `success` | boolean | 请求是否成功 |
| `message` | string | 提示信息 |
| `data` | any | 业务数据 |
| `error_code` | string \| null | 错误码（成功时为 null） |
| `timestamp` | string | ISO 8601 格式时间戳 |
| `code` | int | HTTP 状态码 |

### B.2 独立响应模型示例

**BDCode 解析成功响应** (`POST /api/bdcode/parse`):

```json
{
  "success": true,
  "error": null,
  "data": {
    "bd_code": "...",
    "profession_id": 1,
    "profession": "Guardian",
    "profession_cn": "守护者",
    "specializations": [],
    "skills": {}
  },
  "bd_code": "..."
}
```

---

## 附录 C：常见 HTTP 状态码

| 状态码 | 说明 | 场景 |
|--------|------|------|
| 200 | 成功 | 请求处理成功 |
| 400 | 请求参数错误 | 业务校验失败（如密码错误） |
| 401 | 未认证 | 缺少 Token 或 Token 无效/过期 |
| 403 | 无权限 | 用户存在但无操作权限（如非超级管理员访问用户列表） |
| 404 | 资源不存在 | 请求的日志/用户/战斗等不存在 |
| 422 | 参数校验失败 | FastAPI 自动校验失败（类型错误、必填缺失） |
| 500 | 服务器内部错误 | 未捕获异常 |

---

## 附录 D：分页参数约定

列表接口通常支持以下查询参数：

| 参数名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `page` | int | 1 | 页码 |
| `page_size` | int | 20 | 每页数量 |
| `search` | string | - | 关键字搜索 |
| `sort_by` | string | - | 排序字段 |
| `sort_order` | string | desc | 排序方向（asc / desc） |

---

## 附录 E：前端集成注意事项

1. **Base URL**: 所有 `/api/v1/*` 端点前缀固定，开发环境建议配置代理。
2. **超时设置**: 上传/解析类接口可能耗时较长，建议设置 60s 以上超时。
3. **重试策略**: 500 错误可指数退避重试；401 错误应跳转登录页。
4. **数据缓存**: 字典数据、游戏数据等静态内容可本地缓存。
5. **路由前缀 Bug**: `/api/v1/api/v1/monitoring/*` 存在重复前缀，前端调用时请使用实际路径（以 `/docs` 中展示为准）。
6. **前端常量参考**: 前端 `src/constants/apiEndpoints.ts` 按领域分组定义了所有端点常量（AUTH、LOGS、ATTENDANCE、BUILD、DASHBOARD、AI、FIGHTS、DICTIONARY、WVW_REPORT、EI、COMBAT_ANALYSIS 等），建议与本文档对照使用。

---

> **文档维护说明**: 本文档应与后端代码保持同步更新。新增/修改路由后，请同步更新本文件对应章节，并检查端点总数、前缀、认证要求是否与 `main.py` 注册信息一致。
