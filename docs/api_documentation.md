# GW2 WvW日志解析系统 - API接口文档

## 目录

1. [认证模块](#1-认证模块)
2. [日志管理模块](#2-日志管理模块)
3. [战斗数据模块](#3-战斗数据模块)
4. [EI分析模块](#4-ei分析模块)
5. [出勤统计模块](#5-出勤统计模块)
6. [数据看板模块](#6-数据看板模块)
7. [Build图书馆模块](#7-build图书馆模块)
8. [BDCode解析模块](#8-bdcode解析模块)
9. [评分系统模块](#9-评分系统模块)
10. [AI分析模块](#10-ai分析模块)
11. [用户管理模块](#11-用户管理模块)
12. [字典管理模块](#12-字典管理模块)
13. [游戏数据模块](#13-游戏数据模块)
14. [系统监控模块](#14-系统监控模块)
15. [其他模块](#15-其他模块)

---

## 基础信息

- **API版本**: v1
- **基础路径**: `/api/v1`
- **认证方式**: JWT Bearer Token
- **响应格式**: JSON

---

## 1. 认证模块

| 接口名称 | 路径 | 方法 | 认证要求 | 描述 |
|---------|------|------|---------|------|
| 操作员登录 | `/auth/login` | POST | 否 | 登录获取JWT令牌 |
| 操作员登出 | `/auth/logout` | POST | 是 | 登出当前用户 |
| 获取登录状态 | `/auth/status` | GET | 否 | 检查当前登录状态 |
| 获取用户信息 | `/auth/profile` | GET | 是 | 获取当前用户详情 |
| 修改密码 | `/auth/change-password` | POST | 是 | 修改当前用户密码 |

---

## 2. 日志管理模块

| 接口名称 | 路径 | 方法 | 认证要求 | 描述 |
|---------|------|------|---------|------|
| 获取日志列表 | `/logs` | GET | 否 | 分页获取日志列表 |
| 获取日志详情 | `/logs/{log_id}` | GET | 否 | 获取指定日志详情 |
| 上传日志文件 | `/logs` | POST | 是 | 上传.zevtc/.evtc/.zip文件 |
| 更新日志 | `/logs/{log_id}` | PUT | 是 | 更新日志信息 |
| 删除日志 | `/logs/{log_id}` | DELETE | 是 | 删除日志 |
| 解析日志 | `/logs/{log_id}/parse` | POST | 是 | 后台解析日志文件 |
| 获取解析进度 | `/logs/{log_id}/parse/progress` | GET | 否 | 获取解析进度 |
| 获取解析结果 | `/logs/{log_id}/parse/result` | GET | 否 | 获取解析结果 |
| 验证解析数据 | `/logs/{log_id}/validate` | POST | 否 | 验证解析数据 |
| 批量删除日志 | `/logs/batch-delete` | POST | 是 | 批量删除日志 |
| 导出日志数据 | `/logs/export` | GET | 否 | 导出日志数据(JSON/CSV) |
| 创建批量解析任务 | `/logs/batch-parse` | POST | 是 | 创建批量解析任务 |
| 获取批量解析任务列表 | `/logs/batch-parse` | GET | 是 | 获取批量解析任务列表 |
| 获取批量解析任务详情 | `/logs/batch-parse/{task_id}` | GET | 是 | 获取任务详情 |
| 获取批量解析进度 | `/logs/batch-parse/{task_id}/progress` | GET | 是 | 获取任务进度 |
| 获取批量解析结果 | `/logs/batch-parse/{task_id}/result` | GET | 是 | 获取任务结果 |
| 删除批量解析任务 | `/logs/batch-parse/{task_id}` | DELETE | 是 | 删除任务 |

---

## 3. 战斗数据模块

| 接口名称 | 路径 | 方法 | 认证要求 | 描述 |
|---------|------|------|---------|------|
| 获取战斗列表 | `/fights` | GET | 否 | 分页获取战斗列表 |
| 获取战斗详情 | `/fights/{fight_id}` | GET | 否 | 获取战斗详情 |
| 获取战斗统计 | `/fights/{fight_id}/stats` | GET | 否 | 获取战斗统计数据 |
| 获取日志玩家排行 | `/fights/by-log/{log_id}/players` | GET | 否 | 获取日志玩家排行榜 |

---

## 4. EI分析模块

| 接口名称 | 路径 | 方法 | 认证要求 | 描述 |
|---------|------|------|---------|------|
| 获取战斗摘要 | `/ei-analysis/{log_id}` | GET | 否 | 获取精简版战斗摘要(~15KB) |
| 获取玩家技能循环 | `/ei-analysis/{log_id}/player/{account}/rotation` | GET | 否 | 获取玩家技能循环 |
| 获取玩家详情 | `/ei-analysis/{log_id}/player/{account}` | GET | 否 | 获取玩家详细数据 |

---

## 5. 出勤统计模块

| 接口名称 | 路径 | 方法 | 认证要求 | 描述 |
|---------|------|------|---------|------|
| 获取账号出勤列表 | `/attendance/accounts` | GET | 否 | 获取账号出勤聚合列表 |
| 获取账号出勤详情 | `/attendance/accounts/{account_name}` | GET | 否 | 获取账号出勤详情 |
| 获取角色战斗记录 | `/attendance/accounts/{account_name}/characters/{character_name}` | GET | 否 | 获取角色详细战斗记录 |
| 获取筛选选项 | `/attendance/filters` | GET | 否 | 获取服务器/地图/职业选项 |

---

## 6. 数据看板模块

| 接口名称 | 路径 | 方法 | 认证要求 | 描述 |
|---------|------|------|---------|------|
| 获取核心KPI概览 | `/dashboard/overview` | GET | 否 | 获取数据看板核心指标 |
| 获取时间趋势 | `/dashboard/trends` | GET | 否 | 获取时间趋势数据 |
| 获取职业分布 | `/dashboard/profession-distribution` | GET | 否 | 获取职业分布数据 |
| 获取地图统计 | `/dashboard/map-stats` | GET | 否 | 获取地图战斗统计 |
| 获取玩家排行 | `/dashboard/top-players` | GET | 否 | 获取玩家排行榜 |
| 获取最近战斗 | `/dashboard/recent-fights` | GET | 否 | 获取最近战斗记录 |
| 获取解析状态分布 | `/dashboard/parse-status` | GET | 否 | 获取解析状态分布 |
| 获取AI评分分布 | `/dashboard/ai-score-distribution` | GET | 否 | 获取AI评分分布 |
| 获取Buff覆盖率概览 | `/dashboard/buff-overview` | GET | 否 | 获取Buff覆盖率概览 |

---

## 7. Build图书馆模块

| 接口名称 | 路径 | 方法 | 认证要求 | 描述 |
|---------|------|------|---------|------|
| 获取Build列表 | `/builds` | GET | 否 | 分页获取Build列表 |
| 获取单个Build | `/builds/{build_id}` | GET | 否 | 获取Build详情 |
| 创建Build | `/builds` | POST | 是(write) | 创建新Build |
| 更新Build | `/builds/{build_id}` | PUT | 是(write) | 更新Build |
| 删除Build | `/builds/{build_id}` | DELETE | 是(delete) | 删除Build |

---

## 8. BDCode解析模块

| 接口名称 | 路径 | 方法 | 认证要求 | 描述 |
|---------|------|------|---------|------|
| 解析BDCode | `/api/bdcode/parse` | POST | 否 | 解析单个BDCode |
| URL解析BDCode | `/api/bdcode/parse/{bd_code}` | GET | 否 | 通过URL参数解析 |
| 验证BDCode | `/api/bdcode/validate` | POST | 否 | 验证BDCode格式 |
| 批量解析BDCode | `/api/bdcode/batch` | POST | 否 | 批量解析(最多50个) |
| 获取统计信息 | `/api/bdcode/stats` | GET | 否 | 获取解析服务统计 |
| 健康检查 | `/api/bdcode/health` | GET | 否 | 检查服务状态 |

---

## 9. 评分系统模块

| 接口名称 | 路径 | 方法 | 认证要求 | 描述 |
|---------|------|------|---------|------|
| 获取评分规则 | `/scoring/rules` | GET | 否 | 获取评分规则配置 |
| 计算战斗评分 | `/scoring/fight/{fight_id}` | GET | 否 | 计算战斗所有玩家评分 |

---

## 10. AI分析模块

| 接口名称 | 路径 | 方法 | 认证要求 | 描述 |
|---------|------|------|---------|------|
| 获取AI报告列表 | `/ai/reports` | GET | 否 | 获取AI报告列表 |
| 获取AI报告详情 | `/ai/reports/{report_id}` | GET | 否 | 获取报告详情 |
| 删除AI报告 | `/ai/reports/{report_id}` | DELETE | 是 | 删除报告 |
| AI分析战斗 | `/ai/analyze/fight/{fight_id}` | POST | 是 | 对战斗进行AI分析 |
| AI分析Build | `/ai/analyze/build/{build_id}` | POST | 是 | 对Build进行AI分析 |
| 获取趋势分析 | `/ai/trend` | GET | 否 | 获取AI趋势分析 |
| 获取优化建议 | `/ai/suggestions` | GET | 否 | 获取AI优化建议 |

---

## 11. 用户管理模块

| 接口名称 | 路径 | 方法 | 认证要求 | 描述 |
|---------|------|------|---------|------|
| 获取用户列表 | `/users` | GET | 是(super_admin) | 获取用户列表 |
| 获取当前用户资料 | `/users/profile` | GET | 是 | 获取当前用户资料 |
| 获取指定用户 | `/users/{user_id}` | GET | 是(super_admin) | 获取指定用户 |
| 创建用户 | `/users` | POST | 是(super_admin) | 创建新用户 |
| 更新用户 | `/users/{user_id}` | PUT | 是(super_admin) | 更新用户信息 |
| 删除用户 | `/users/{user_id}` | DELETE | 是(super_admin) | 删除用户 |
| 修改密码 | `/users/change-password` | POST | 是 | 修改当前用户密码 |
| 重置用户密码 | `/users/{user_id}/reset-password` | POST | 是(super_admin) | 重置用户密码 |
| 切换用户状态 | `/users/{user_id}/toggle-active` | POST | 是(super_admin) | 切换活跃状态 |
| 获取角色列表 | `/users/roles/list` | GET | 否 | 获取系统角色列表 |

---

## 12. 字典管理模块

### 12.1 字典类型管理

| 接口名称 | 路径 | 方法 | 认证要求 | 描述 |
|---------|------|------|---------|------|
| 获取字典类型列表 | `/dictionary/types` | GET | 是 | 分页获取字典类型 |
| 获取所有字典类型 | `/dictionary/types/all` | GET | 是 | 获取所有启用类型 |
| 获取单个字典类型 | `/dictionary/types/{dict_id}` | GET | 是 | 获取类型详情 |
| 创建字典类型 | `/dictionary/types` | POST | 是(super_admin) | 创建新类型 |
| 更新字典类型 | `/dictionary/types/{dict_id}` | PUT | 是(super_admin) | 更新类型 |
| 删除字典类型 | `/dictionary/types/{dict_id}` | DELETE | 是(super_admin) | 删除类型 |

### 12.2 字典数据管理

| 接口名称 | 路径 | 方法 | 认证要求 | 描述 |
|---------|------|------|---------|------|
| 获取字典项列表 | `/dictionary/data` | GET | 是 | 获取字典项列表 |
| 获取单个字典项 | `/dictionary/data/{dict_code}` | GET | 是 | 获取字典项详情 |
| 获取字典选项 | `/dictionary/options/{dict_type}` | GET | 否 | 获取下拉选项(公开) |
| 创建字典项 | `/dictionary/data` | POST | 是(super_admin) | 创建新字典项 |
| 更新字典项 | `/dictionary/data/{dict_code}` | PUT | 是(super_admin) | 更新字典项 |
| 删除字典项 | `/dictionary/data/{dict_code}` | DELETE | 是(super_admin) | 删除字典项 |
| 刷新字典缓存 | `/dictionary/reload-cache` | POST | 是 | 刷新内存缓存 |
| 初始化字典数据 | `/dictionary/init` | POST | 是(super_admin) | 初始化预置数据 |

---

## 13. 游戏数据模块

| 接口名称 | 路径 | 方法 | 认证要求 | 描述 |
|---------|------|------|---------|------|
| 获取数据版本信息 | `/game-data/info` | GET | 否 | 获取游戏数据版本 |

---

## 14. 系统监控模块

| 接口名称 | 路径 | 方法 | 认证要求 | 描述 |
|---------|------|------|---------|------|
| 获取错误统计 | `/monitor/errors/stats` | GET | 是 | 获取系统错误统计 |
| 获取错误报告 | `/monitor/errors/report` | GET | 是 | 获取详细错误报告 |
| 清空错误统计 | `/monitor/errors/clear` | POST | 是 | 清空错误统计 |
| 导出错误 | `/monitor/errors/export` | POST | 是 | 导出错误到文件 |
| 健康检查 | `/monitor/health` | GET | 否 | 系统健康检查 |

---

## 15. 其他模块

### 15.1 性能监控

| 接口名称 | 路径 | 方法 | 认证要求 | 描述 |
|---------|------|------|---------|------|
| 获取性能指标 | `/api/v1/monitoring/metrics` | GET | 是 | 获取性能指标数据 |

### 15.2 存储管理

| 接口名称 | 路径 | 方法 | 认证要求 | 描述 |
|---------|------|------|---------|------|
| 获取存储统计 | `/storage/stats` | GET | 否 | 获取存储统计信息 |
| 清理存储 | `/storage/cleanup` | POST | 是 | 清理存储空间 |

### 15.3 设置管理

| 接口名称 | 路径 | 方法 | 认证要求 | 描述 |
|---------|------|------|---------|------|
| 获取设置 | `/settings` | GET | 否 | 获取系统设置 |
| 更新设置 | `/settings` | PUT | 是 | 更新系统设置 |

### 15.4 测试工具

| 接口名称 | 路径 | 方法 | 认证要求 | 描述 |
|---------|------|------|---------|------|
| DPS报告测试 | `/test/dps-report` | GET | 否 | DPS报告测试接口 |

---

## 附录：响应格式说明

### 成功响应
```json
{
  "success": true,
  "code": 200,
  "message": "操作成功",
  "data": { ... }
}
```

### 失败响应
```json
{
  "success": false,
  "code": 404,
  "message": "资源不存在",
  "data": null
}
```

### 分页响应
```json
{
  "success": true,
  "code": 200,
  "message": "获取成功",
  "data": {
    "items": [...],
    "total": 100,
    "page": 1,
    "page_size": 20
  }
}
```

---

## 附录：认证权限说明

| 角色 | 权限 | 说明 |
|------|------|------|
| super_admin | read, write, upload, delete, manage_users | 超级管理员，完整权限 |
| operator | read, write, upload, delete | 操作员，可管理数据 |
| user | read | 普通用户，只读权限 |
| guest | read | 游客，只读权限 |

---

**文档版本**: v2.0
**生成日期**: 2026-05-06
**更新说明**: 移除未使用的EI完整报告接口，优化接口分类结构
**适用系统**: GW2 WvW日志解析系统