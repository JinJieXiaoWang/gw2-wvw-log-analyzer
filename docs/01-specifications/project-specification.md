# GW2 WvW 日志解析与评分系统 - 技术规范与开发计划

> **版本**: v3.0.0
> **更新日期**: 2026-05-05
> **整合责任人**: 系统文档维护团队
> **变更摘要**:
> - 依据当前代码更新技术栈描述
> - 补充多数据库支持（SQLite/MySQL/PostgreSQL）
> - 更新前端技术栈（Vite + PrimeVue Aura + Tailwind CSS）

---

## 历史版本

| 版本 | 日期 | 变更内容 | 责任人 |
|------|------|----------|--------|
| v3.0.0 | 2026-05-05 | 依据代码更新技术栈，补充多数据库支持 | 系统 |
| v2.0.0 | 2026-05-01 | 合并 SPEC 与 DEV_PLAN，精简优化 | 系统 |
| v1.0.0 | 2026-04-27 | 初始版本 | 帅妹妹丶.8297 |

---

# 第一部分：技术规范

# GW2 WvW 日志解析与评分系统 - 技术规范文档

## 1. 产品概述

### 1.1 产品定位
公会内部使用的激战2(Guild Wars 2) WvW战场日志解析、出勤统计、战斗数据分析、Build管理、AI智能复盘分析工具。聚焦WvW大团实战场景，服务于团员提升与公会管理。

### 1.2 核心用户
- **普通成员(访客)**: 可浏览全部日志数据、出勤排行、技能分析、战斗图表、Build解析、数据看板、AI复盘报告等展示类内容
- **管理员**: 拥有日志上传、数据修正、系统配置、AI分析规则配置等后台维护权限

### 1.3 权限策略
- **非强制登录模式**: 所有公会成员无需登录即可进入系统
- **访客模式**: 隐藏所有操作型按钮，仅保留浏览、筛选、查看、导出功能
- **管理员模式**: 通过极简账号密码登录，解锁全部功能

---

## 2. 技术架构

### 2.1 技术栈选型

#### 后端技术栈
| 组件 | 技术选型 | 说明 |
|------|----------|------|
| Web框架 | FastAPI 0.115+ | 高性能异步框架，自动API文档 |
| 数据库 | SQLite / MySQL 8.0+ / PostgreSQL 14+ | 通过 `DB_TYPE` 环境变量切换 |
| ORM | SQLAlchemy 2.0+ | 支持多数据库，自动建表 |
| 数据验证 | Pydantic 2.10+ | 自动生成JSON Schema |
| 密码加密 | passlib[bcrypt] | 安全密码哈希 |
| 认证 | PyJWT 2.10+ | JWT Bearer Token，有效期 2 小时 |
| 日志框架 | Python logging | 自定义日志工具 |
| ASGI服务器 | Uvicorn 0.34+ | ASGI应用服务器 |
| 测试框架 | Pytest 8.0+ | 单元测试与覆盖率 |
| 任务调度 | APScheduler 3.11+ | 定时任务 |
| AI 客户端 | OpenAI 1.60+ | 多模型提供商支持 |

#### 前端技术栈
| 组件 | 技术选型 | 说明 |
|------|----------|------|
| 框架 | Vue 3 | Composition API，`<script setup lang="ts">` |
| 语言 | TypeScript | 严格模式 |
| 构建工具 | Vite | 快速开发与构建 |
| 样式 | Tailwind CSS | `darkMode: 'class'`，CSS 变量驱动 |
| UI 组件库 | PrimeVue (Aura 预设) | 游戏主题预设 `GameThemePreset` |
| 状态管理 | Pinia | Composition API 风格 |
| 路由 | Vue Router | `createRouter` + `createWebHistory` |
| HTTP 客户端 | Axios | 通过 `ApiFactory` / `HttpClient` 封装 |
| 构建验证 | Vue TSC + Vite Build | 类型检查与构建 |

#### 部署技术栈
| 组件 | 技术选型 | 说明 |
|------|----------|------|
| 裸机部署 | Debian 12 + Systemd + Nginx | `scripts/deploy/install.sh` 一键部署 |
| 容器部署 | Docker Compose + Nginx | 3 服务架构（app/db/nginx） |
| Python 版本 | 3.13（源码编译） | 裸机部署时从源码编译 |
| 反向代理 | Nginx | API 代理 + 前端 SPA + 上传文件服务 |
| 框架 | Vue 3 (Composition API) |
| UI组件库 | PrimeVue |
| CSS框架 | Tailwind CSS |
| 图表库 | ECharts |
| 状态管理 | Pinia |
| 路由 | Vue Router |

### 2.2 项目结构

```
gw2-log-system/
├── app/
│   ├── __init__.py
│   ├── main.py                    # 应用入口
│   ├── config/                    # 配置管理
│   │   ├── __init__.py
│   │   ├── settings.py           # 应用配置
│   │   └── database.py           # 数据库配置
│   ├── models/                    # 数据模型层
│   │   ├── __init__.py
│   │   ├── user.py               # 用户/管理员模型
│   │   ├── log.py                # 日志文件模型
│   │   ├── fight.py               # 战斗记录模型
│   │   ├── member.py             # 成员模型
│   │   ├── skill.py               # 技能记录模型
│   │   ├── build.py               # Build配置模型
│   │   └── ai_report.py          # AI分析报告模型
│   ├── schemas/                    # 数据验证模式
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── log.py
│   │   ├── fight.py
│   │   ├── member.py
│   │   ├── skill.py
│   │   ├── build.py
│   │   ├── ai_report.py
│   │   └── common.py
│   ├── services/                   # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── auth_service.py        # 认证服务
│   │   ├── log_service.py        # 日志解析服务
│   │   ├── fight_service.py      # 战斗数据服务
│   │   ├── member_service.py     # 成员出勤服务
│   │   ├── skill_service.py      # 技能分析服务
│   │   ├── build_service.py      # Build解析服务
│   │   └── ai_service.py         # AI分析服务
│   ├── routers/                    # API路由层
│   │   ├── __init__.py
│   │   ├── auth.py               # 认证接口
│   │   ├── logs.py               # 日志管理接口
│   │   ├── fights.py             # 战斗数据接口
│   │   ├── members.py            # 成员出勤接口
│   │   ├── skills.py             # 技能分析接口
│   │   ├── builds.py             # Build管理接口
│   │   └── ai.py                 # AI分析接口
│   └── utils/                     # 工具函数
│       ├── __init__.py
│       ├── logger.py              # 日志工具
│       ├── exceptions.py          # 自定义异常
│       └── security.py            # 安全工具
├── database/
│   └── migrations/                # 数据库迁移
│       ├── __init__.py
│       └── init_db.py            # 初始化脚本
├── tests/                         # 单元测试
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_auth_service.py
│   ├── test_log_service.py
│   ├── test_member_service.py
│   └── test_api.py
├── logs/                          # 日志文件目录
├── uploads/                       # 上传文件目录
├── app.db                         # SQLite数据库文件
├── requirements.txt               # Python依赖
├── .env.example                   # 环境变量示例
├── .gitignore
├── SPEC.md                        # 技术规范文档
├── README.md                      # 项目说明
└── DEV_PLAN.md                    # 开发计划
```

---

## 3. 数据库架构

### 3.1 ER关系图

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   admins    │      │    logs     │      │   fights    │
├─────────────┤      ├─────────────┤      ├─────────────┤
│ id (PK)     │──┐   │ id (PK)     │──────│ id (PK)     │
│ username    │  │   │ filename    │      │ log_id (FK) │
│ password    │  │   │ upload_time │      │ start_time  │
│ created_at  │  │   │ parse_status│      │ end_time    │
└─────────────┘  │   │ server      │      │ map_name    │
                 │   │ guild_tag   │      │ server_name │
                 │   │ admin_id(FK)│      │ total_dmg   │
                 │   └─────────────┘      │ total_heal  │
                 │                         │ kill_count  │
                 │                         │ death_count│
                 │                         └─────────────┘
                 │                                │
                 │                                │
┌─────────────┐  │                         ┌─────────────┐
│   members   │  │                         │ fight_stats │
├─────────────┤  │                         ├─────────────┤
│ id (PK)     │◄─┤                         │ id (PK)     │
│ account_name│  │                         │ fight_id(FK)│
│ profession  │  │                         │ member_id(FK│
│ guild_name  │  │                         │ damage      │
└─────────────┘  │                         │ healing     │
                  │                         │ kills       │
                  │                         │ deaths      │
                  │                         │ time_in_com │
                  └────────────────────────►└─────────────┘

┌─────────────┐      ┌─────────────┐
│   builds    │      │ skill_events│
├─────────────┤      ├─────────────┤
│ id (PK)     │      │ id (PK)     │
│ member_id(FK)     │ fight_id(FK) │
│ build_code  │      │ member_id(FK)     │
│ profession  │      │ skill_id    │
│ build_name  │      │ timestamp   │
│ is_ideal    │      │ duration_ms │
│ created_at  │      │ is_burst    │
└─────────────┘      │ is_mistake  │
                      └─────────────┘

┌─────────────┐      ┌─────────────┐
│ ai_reports  │      │  skills    │
├─────────────┤      ├─────────────┤
│ id (PK)     │      │ id (PK)     │
│ report_type │      │ gw2_skill_id│
│ target_type │      │ name_cn     │
│ target_id   │      │ name_en     │
│ content     │      │ description │
│ summary     │      │ profession  │
│ created_by(FK)     │ category    │
│ created_at  │      └─────────────┘
│ is_public   │
└─────────────┘
```

### 3.2 数据表定义

#### admins (管理员表)
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK, AUTO | 主键 |
| username | VARCHAR(50) | UNIQUE, NOT NULL | 管理员用户名 |
| password_hash | VARCHAR(255) | NOT NULL | 密码哈希 |
| created_at | DATETIME | DEFAULT NOW | 创建时间 |
| last_login | DATETIME | NULL | 最后登录时间 |

#### logs (日志文件表)
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK, AUTO | 主键 |
| filename | VARCHAR(255) | NOT NULL | 原始文件名 |
| file_path | VARCHAR(500) | NOT NULL | 存储路径 |
| upload_time | DATETIME | DEFAULT NOW | 上传时间 |
| parse_status | VARCHAR(20) | DEFAULT 'pending' | 解析状态: pending/parsing/completed/failed |
| parse_time | DATETIME | NULL | 解析完成时间 |
| server | VARCHAR(100) | NULL | 服务器名称 |
| map_name | VARCHAR(100) | NULL | 地图名称 |
| guild_tag | VARCHAR(20) | NULL | 公会标签 |
| uploaded_by | INTEGER | FK(admins.id) | 上传者 |

#### fights (战斗记录表)
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK, AUTO | 主键 |
| log_id | INTEGER | FK(logs.id), NOT NULL | 所属日志 |
| start_time | DATETIME | NOT NULL | 战斗开始时间 |
| end_time | DATETIME | NULL | 战斗结束时间 |
| duration_sec | INTEGER | DEFAULT 0 | 持续时间(秒) |
| map_name | VARCHAR(100) | NULL | 地图名称 |
| server_name | VARCHAR(100) | NULL | 服务器 |
| total_damage | BIGINT | DEFAULT 0 | 总伤害 |
| total_healing | BIGINT | DEFAULT 0 | 总治疗 |
| kill_count | INTEGER | DEFAULT 0 | 击杀数 |
| death_count | INTEGER | DEFAULT 0 | 死亡数 |
| is_ai_analyzed | BOOLEAN | DEFAULT FALSE | AI分析状态 |

#### members (成员表)
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK, AUTO | 主键 |
| account_name | VARCHAR(100) | NOT NULL | 账号名称 |
| profession | VARCHAR(50) | NULL | 职业 |
| guild_tag | VARCHAR(20) | NULL | 公会标签 |
| join_date | DATE | NULL | 加入日期 |

#### fight_stats (战斗统计表)
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK, AUTO | 主键 |
| fight_id | INTEGER | FK(fights.id), NOT NULL | 战斗ID |
| member_id | INTEGER | FK(members.id), NOT NULL | 成员ID |
| damage | BIGINT | DEFAULT 0 | 造成伤害 |
| healing | BIGINT | DEFAULT 0 | 治疗量 |
| kills | INTEGER | DEFAULT 0 | 击杀数 |
| deaths | INTEGER | DEFAULT 0 | 死亡数 |
| time_in_combat | INTEGER | DEFAULT 0 | 参战时间(秒) |
| damage_taken | BIGINT | DEFAULT 0 | 承受伤害 |
| down_count | INTEGER | DEFAULT 0 | 倒地次数 |
| res_count | INTEGER | DEFAULT 0 | 复活次数 |

#### skills (技能表)
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK, AUTO | 主键 |
| gw2_skill_id | VARCHAR(20) | UNIQUE, NOT NULL | GW2技能ID |
| name_cn | VARCHAR(100) | NULL | 中文名 |
| name_en | VARCHAR(100) | NOT NULL | 英文名 |
| description | TEXT | NULL | 描述 |
| profession | VARCHAR(50) | NULL | 所属职业 |
| category | VARCHAR(50) | NULL | 技能类别 |

#### skill_events (技能事件表)
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK, AUTO | 主键 |
| fight_id | INTEGER | FK(fights.id), NOT NULL | 战斗ID |
| member_id | INTEGER | FK(members.id), NOT NULL | 成员ID |
| skill_id | INTEGER | FK(skills.id), NOT NULL | 技能ID |
| timestamp | FLOAT | NOT NULL | 时间戳(秒) |
| duration_ms | INTEGER | DEFAULT 0 | 持续时间 |
| is_burst | BOOLEAN | DEFAULT FALSE | 是否爆发技能 |
| is_mistake | BOOLEAN | DEFAULT FALSE | AI识别失误 |
| mistake_type | VARCHAR(50) | NULL | 失误类型 |
| damage | BIGINT | DEFAULT 0 | 技能伤害 |

#### builds (Build配置表)
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK, AUTO | 主键 |
| member_id | INTEGER | FK(members.id), NOT NULL | 成员ID |
| build_code | TEXT | NOT NULL | Build代码 |
| build_name | VARCHAR(100) | NULL | Build名称 |
| profession | VARCHAR(50) | NOT NULL | 职业 |
| gear_json | TEXT | NULL | 装备JSON |
| traits_json | TEXT | NULL | 天赋JSON |
| skills_json | TEXT | NULL | 技能JSON |
| runes_json | TEXT | NULL | 符文JSON |
| is_ideal | BOOLEAN | DEFAULT FALSE | 是否理想Build |
| created_at | DATETIME | DEFAULT NOW | 创建时间 |
| updated_at | DATETIME | NULL | 更新时间 |

#### ai_reports (AI分析报告表)
| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK, AUTO | 主键 |
| report_type | VARCHAR(50) | NOT NULL | 报告类型: fight/skill/build/trend |
| target_type | VARCHAR(50) | NOT NULL | 目标类型: fight/member/build |
| target_id | INTEGER | NOT NULL | 目标ID |
| content | TEXT | NOT NULL | 报告内容(JSON) |
| summary | TEXT | NULL | 摘要 |
| ai_score | FLOAT | NULL | AI评分(0-100) |
| created_by | INTEGER | FK(admins.id), NULL | 创建者 |
| created_at | DATETIME | DEFAULT NOW | 创建时间 |
| is_public | BOOLEAN | DEFAULT TRUE | 是否公开 |
| is_deleted | BOOLEAN | DEFAULT FALSE | 软删除 |

---

## 4. API接口规范

### 4.1 基础信息
- **Base URL**: `/api/v1`
- **Content-Type**: `application/json`
- **认证方式**: Session Cookie (管理员接口)
- **CORS**: 支持 `http://localhost:5173`, `http://localhost:3000`

### 4.2 统一响应格式

#### 成功响应
```json
{
  "success": true,
  "message": "操作成功",
  "data": { ... },
  "timestamp": "2026-04-27T12:00:00Z"
}
```

#### 错误响应
```json
{
  "success": false,
  "message": "错误描述",
  "error_code": "ERROR_CODE",
  "timestamp": "2026-04-27T12:00:00Z"
}
```

### 4.3 接口列表

#### 4.3.1 认证接口 (Auth)

| 方法 | 路径 | 描述 | 权限 |
|------|------|------|------|
| POST | /auth/login | 管理员登录 | 公开 |
| POST | /auth/logout | 管理员登出 | 管理员 |
| GET | /auth/status | 获取登录状态 | 公开 |

#### 4.3.2 日志管理接口 (Logs)

| 方法 | 路径 | 描述 | 权限 |
|------|------|------|------|
| GET | /logs | 获取日志列表 | 公开 |
| GET | /logs/{log_id} | 获取日志详情 | 公开 |
| POST | /logs | 上传日志文件 | 管理员 |
| DELETE | /logs/{log_id} | 删除日志 | 管理员 |
| GET | /logs/{log_id}/fights | 获取日志关联的战斗 | 公开 |
| POST | /logs/{log_id}/parse | 解析日志文件 | 管理员 |

#### 4.3.3 战斗数据接口 (Fights)

| 方法 | 路径 | 描述 | 权限 |
|------|------|------|------|
| GET | /fights | 获取战斗列表 | 公开 |
| GET | /fights/{fight_id} | 获取战斗详情 | 公开 |
| GET | /fights/{fight_id}/stats | 获取战斗统计 | 公开 |
| GET | /fights/{fight_id}/skills | 获取技能事件 | 公开 |

#### 4.3.4 成员出勤接口 (Members)

| 方法 | 路径 | 描述 | 权限 |
|------|------|------|------|
| GET | /members | 获取成员列表 | 公开 |
| GET | /members/{member_id} | 获取成员详情 | 公开 |
| GET | /members/{member_id}/attendance | 获取出勤记录 | 公开 |
| GET | /members/{member_id}/stats | 获取成员统计 | 公开 |
| GET | /members/ranking | 获取成员排名 | 公开 |
| GET | /members/professions | 获取职业分布 | 公开 |

#### 4.3.5 技能分析接口 (Skills)

| 方法 | 路径 | 描述 | 权限 |
|------|------|------|------|
| GET | /skills | 获取技能列表 | 公开 |
| GET | /skills/{skill_id} | 获取技能详情 | 公开 |
| GET | /skills/{fight_id}/events | 获取战斗技能事件 | 公开 |
| GET | /skills/{member_id}/rotation | 获取循环分析 | 公开 |

#### 4.3.6 Build管理接口 (Builds)

| 方法 | 路径 | 描述 | 权限 |
|------|------|------|------|
| GET | /builds | 获取Build列表 | 公开 |
| GET | /builds/{build_id} | 获取Build详情 | 公开 |
| POST | /builds | 创建Build | 管理员 |
| PUT | /builds/{build_id} | 更新Build | 管理员 |
| DELETE | /builds/{build_id} | 删除Build | 管理员 |
| POST | /builds/parse | 解析Build代码 | 公开 |
| POST | /builds/compare | 对比两个Build | 公开 |

#### 4.3.7 AI分析接口 (AI)

| 方法 | 路径 | 描述 | 权限 |
|------|------|------|------|
| POST | /ai/analyze/fight/{fight_id} | AI分析战斗 | 管理员 |
| POST | /ai/analyze/member/{member_id} | AI分析成员 | 管理员 |
| POST | /ai/analyze/skill/{member_id} | AI分析技能循环 | 管理员 |
| POST | /ai/analyze/build/{build_id} | AI分析Build | 管理员 |
| GET | /ai/reports | 获取AI报告列表 | 公开 |
| GET | /ai/reports/{report_id} | 获取AI报告详情 | 公开 |
| DELETE | /ai/reports/{report_id} | 删除AI报告 | 管理员 |
| GET | /ai/trend | AI数据趋势分析 | 公开 |
| GET | /ai/suggestions | AI优化建议 | 公开 |

#### 4.3.8 数据看板接口 (Dashboard)

| 方法 | 路径 | 描述 | 权限 |
|------|------|------|------|
| GET | /dashboard/overview | 获取数据大盘 | 公开 |
| GET | /dashboard/recent | 获取近期数据 | 公开 |
| GET | /dashboard/trends | 获取趋势数据 | 公开 |

### 4.4 错误码定义

| 错误码 | HTTP状态码 | 说明 |
|--------|------------|------|
| UNAUTHORIZED | 401 | 未授权 |
| FORBIDDEN | 403 | 禁止访问 |
| NOT_FOUND | 404 | 资源不存在 |
| VALIDATION_ERROR | 422 | 参数验证失败 |
| CONFLICT | 409 | 资源冲突 |
| INTERNAL_ERROR | 500 | 服务器内部错误 |
| PARSE_ERROR | 400 | 解析错误 |

---

## 5. 业务功能模块

### 5.1 日志管理模块
- **zevtc文件上传**: 支持批量上传、拖拽上传、进度显示
- **日志解析**: 解析zevtc格式、提取战斗数据、技能数据
- **日志筛选**: 按时间、地图、服务器、公会筛选
- **日志状态**: pending → parsing → completed/failed

### 5.2 战斗分析模块
- **战斗统计**: 伤害、治疗、击杀、死亡、时长
- **职业分布**: 各职业参与数量和贡献
- **伤害治疗图表**: 柱状图、饼图展示
- **团队对比**: 己方vs敌方数据对比

### 5.3 出勤统计模块
- **出勤排行**: 按参战时长、战绩评分排序
- **出勤明细**: 每场战斗的参与情况
- **击杀死亡数据**: 多维度统计数据
- **公开导出**: CSV/Excel格式导出

### 5.4 技能循环分析模块
- **技能时序图**: 展示技能释放顺序
- **循环对比**: 理想循环 vs 实战循环
- **失误识别**: AI自动识别失误点
- **优化建议**: 个性化优化方案

### 5.5 Build解析模块
- **代码解析**: 解析GW2 Build代码
- **装备展示**: 装备、天赋、技能、符文
- **Build对比**: 两个Build并排对比
- **收藏保存**: 管理员保存个人Build

### 5.6 AI分析模块
- **战斗AI分析**: 识别战斗短板、生成优化建议
- **技能AI复盘**: 对比理想循环、标注失误
- **Build AI优化**: WvW大团场景适配建议
- **数据洞察**: 长期数据异常识别、趋势预测
- **AI报告管理**: 生成、导出、分享、删除

### 5.7 数据看板模块
- **公会大盘**: 核心指标汇总展示
- **近期战场**: 最新战斗动态
- **职业热度**: 各职业使用统计
- **趋势图表**: 长期数据折线图

---

## 6. 安全设计

### 6.1 认证与授权
- 管理员账号密码登录 (Session Cookie)
- 访客无需登录，仅浏览
- 接口权限检查装饰器

### 6.2 数据安全
- 密码bcrypt加密存储
- SQL注入防护 (ORM参数化查询)
- 文件上传类型校验
- XSS防护 (Pydantic验证)

### 6.3 API安全
- CORS跨域限制
- 请求频率限制 (可选)
- 敏感操作日志记录

---

## 7. 配置管理

### 7.1 环境变量 (.env)
```bash
# 应用配置
APP_NAME=GW2 WvW日志系统
APP_VERSION=1.0.0
DEBUG=False

# API配置
API_PREFIX=/api/v1
SECRET_KEY=your-secret-key

# 数据库配置
DATABASE_URL=sqlite:///./database/app.db

# CORS配置
BACKEND_CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=./logs/app.log

# 文件上传配置
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE=104857600  # 100MB
```

---

## 8. 开发规范

### 8.1 代码规范
- **Python**: PEP 8，4空格缩进，snake_case命名
- **注释**: 所有函数添加中文注释
- **模块头部**: 模块功能、作者、日期、依赖说明

### 8.2 Git提交规范
- feat: 新功能
- fix: 修复bug
- docs: 文档更新
- refactor: 重构
- test: 测试相关

### 8.3 测试规范
- 单元测试覆盖率 ≥ 80%
- 服务层和API层全面测试
- 使用pytest + pytest-cov

---

## 9. 部署说明

### 9.1 环境要求
- Python 3.10+
- 无需额外数据库软件 (SQLite内置)

### 9.2 启动步骤
```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 初始化数据库
python database/migrations/init_db.py

# 3. 启动服务
python main.py
# 或
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 9.3 API文档
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 10. 可扩展性设计

### 10.1 横向扩展
- RESTful API设计支持微服务拆分
- 数据库连接池管理
- 异步任务队列预留 (Celery)

### 10.2 功能扩展
- 模块化路由注册
- 服务类依赖注入
- 配置驱动功能开关

### 10.3 数据扩展
- 历史数据归档策略
- 数据库索引优化
- 报表数据预聚合

---

*文档版本: 1.0.0*
*最后更新: 2026-04-27*


---

# 第二部分：开发计划

# GW2 WvW 日志系统 - 开发计划

## 1. 项目概述

### 1.1 项目目标
为公会内部搭建一个完整的激战2(Guild Wars 2) WvW战场日志解析、出勤统计、战斗数据分析、Build管理和AI智能复盘分析系统。

### 1.2 核心功能范围
- **日志管理**: zevtc文件上传、解析、存储
- **战斗分析**: 伤害、治疗、击杀、死亡等数据统计
- **出勤统计**: 成员参战时长、战绩评分排行
- **技能循环**: 技能释放时序、循环对比、失误分析
- **Build解析**: 代码解析、装备天赋展示、Build对比
- **AI分析**: 战斗短板识别、技能循环优化、Build适配建议
- **数据看板**: 公会大盘、近期战场、趋势图表

### 1.3 权限设计
- **访客模式**: 无需登录，仅可浏览公开数据
- **操作员模式**: 需要登录，可进行上传、修改、删除等操作
- **超级管理员模式**: 预置管理员账号，拥有最高权限，禁止删除

### 1.4 预置管理员账号
- **账号信息**: 用户名 `admin`，默认密码 `Gw2@Admin2026`
- **初始化时机**: 系统首次启动或数据库初始化时自动创建
- **保护机制**: 禁止删除操作，确保系统至少有一个管理员账号

---

## 2. 开发阶段规划

### 2.1 第一阶段：基础架构搭建 (预计 3-5 天)

#### 后端基础设施
- [x] 项目结构搭建
- [x] 配置管理模块
- [x] 数据库配置与迁移
- [x] 日志记录模块
- [x] 异常处理机制

#### 数据模型
- [x] 管理员模型 (Admin)
- [x] 日志文件模型 (Log)
- [x] 战斗记录模型 (Fight)
- [x] 成员模型 (Member)
- [x] 战斗统计模型 (FightStats)
- [x] 技能模型 (Skill)
- [x] 技能事件模型 (SkillEvent)
- [x] Build模型 (Build)
- [x] AI报告模型 (AIReport)

#### API基础接口
- [x] 认证接口 (登录/登出/状态)
- [x] 日志管理接口 (CRUD)
- [x] 战斗数据接口 (列表/详情/统计)
- [x] 成员出勤接口 (列表/详情/排名)
- [x] 技能分析接口
- [x] Build管理接口
- [x] AI分析接口
- [x] 数据看板接口

### 2.2 第二阶段：核心功能开发 (预计 5-7 天)

#### 日志解析功能
- [ ] zevtc文件格式解析器
- [ ] 战斗数据提取
- [ ] 成员信息提取
- [ ] 技能数据提取
- [ ] 批量解析支持

#### 数据分析功能
- [ ] 伤害/治疗统计计算
- [ ] 职业分布分析
- [ ] 团队贡献计算
- [ ] KPI指标设计

#### AI分析功能
- [ ] 战斗短板识别算法
- [ ] 技能循环评估模型
- [ ] Build适配度分析
- [ ] 趋势预测模型
- [ ] 优化建议生成

### 2.3 第三阶段：前端对接与优化 (预计 5-7 天)

#### 前端开发（需前端团队配合）
- [ ] 首页数据大盘
- [ ] 日志管理页面
- [ ] 战斗详情页面
- [ ] 出勤统计页面
- [ ] 技能分析页面
- [ ] Build解析页面
- [ ] AI报告页面
- [ ] 管理员后台

#### 性能优化
- [ ] 数据库索引优化
- [ ] API响应优化
- [ ] 大数据量分页处理
- [ ] 缓存策略

### 2.4 第四阶段：测试与部署 (预计 3-5 天)

#### 测试工作
- [ ] 单元测试完善 (覆盖率 ≥ 80%)
- [ ] API集成测试
- [ ] 性能测试
- [ ] 安全测试

#### 部署准备
- [ ] 生产环境配置
- [ ] 数据备份策略
- [ ] 监控告警配置
- [ ] 文档完善

---

## 3. 接口清单

### 3.1 认证接口 `/api/v1/auth`
| 方法 | 路径 | 描述 | 权限 |
|------|------|------|------|
| POST | /login | 登录 | 公开 |
| POST | /logout | 登出 | 管理员 |
| GET | /status | 登录状态 | 公开 |

### 3.2 日志管理 `/api/v1/logs`
| 方法 | 路径 | 描述 | 权限 |
|------|------|------|------|
| GET | / | 日志列表 | 公开 |
| GET | /{log_id} | 日志详情 | 公开 |
| POST | / | 上传日志 | 管理员 |
| PUT | /{log_id} | 更新日志 | 管理员 |
| DELETE | /{log_id} | 删除日志 | 管理员 |
| POST | /{log_id}/parse | 解析日志 | 管理员 |

### 3.3 战斗数据 `/api/v1/fights`
| 方法 | 路径 | 描述 | 权限 |
|------|------|------|------|
| GET | / | 战斗列表 | 公开 |
| GET | /{fight_id} | 战斗详情 | 公开 |
| GET | /{fight_id}/stats | 战斗统计 | 公开 |

### 3.4 成员出勤 `/api/v1/members`
| 方法 | 路径 | 描述 | 权限 |
|------|------|------|------|
| GET | / | 成员列表 | 公开 |
| GET | /{member_id} | 成员详情 | 公开 |
| GET | /{member_id}/stats | 成员统计 | 公开 |
| GET | /ranking | 成员排名 | 公开 |
| GET | /professions | 职业分布 | 公开 |

### 3.5 技能分析 `/api/v1/skills`
| 方法 | 路径 | 描述 | 权限 |
|------|------|------|------|
| GET | / | 技能列表 | 公开 |
| GET | /{skill_id} | 技能详情 | 公开 |
| GET | /{fight_id}/events | 技能事件 | 公开 |
| GET | /{member_id}/rotation | 循环分析 | 公开 |

### 3.6 Build管理 `/api/v1/builds`
| 方法 | 路径 | 描述 | 权限 |
|------|------|------|------|
| GET | / | Build列表 | 公开 |
| GET | /{build_id} | Build详情 | 公开 |
| POST | / | 创建Build | 管理员 |
| PUT | /{build_id} | 更新Build | 管理员 |
| DELETE | /{build_id} | 删除Build | 管理员 |
| POST | /parse | 解析代码 | 公开 |
| POST | /compare | Build对比 | 公开 |

### 3.7 AI分析 `/api/v1/ai`
| 方法 | 路径 | 描述 | 权限 |
|------|------|------|------|
| GET | /reports | AI报告列表 | 公开 |
| GET | /reports/{report_id} | 报告详情 | 公开 |
| DELETE | /reports/{report_id} | 删除报告 | 管理员 |
| POST | /analyze/fight/{fight_id} | 分析战斗 | 管理员 |
| POST | /analyze/member/{member_id} | 分析成员 | 管理员 |
| POST | /analyze/build/{build_id} | 分析Build | 管理员 |
| GET | /trend | 趋势分析 | 公开 |
| GET | /suggestions | 优化建议 | 公开 |

### 3.8 数据看板 `/api/v1/dashboard`
| 方法 | 路径 | 描述 | 权限 |
|------|------|------|------|
| GET | /overview | 数据大盘 | 公开 |
| GET | /recent | 近期数据 | 公开 |
| GET | /trends | 趋势数据 | 公开 |

---

## 4. 技术规范

### 4.1 后端技术栈
- **Web框架**: FastAPI 0.100+
- **数据库**: SQLite (Python内置)
- **ORM**: SQLAlchemy 2.0+
- **数据验证**: Pydantic 2.0+
- **密码加密**: passlib[bcrypt]
- **ASGI服务器**: Uvicorn
- **测试框架**: Pytest

### 4.2 前端技术栈 (参考UI设计规范)
- **框架**: Vue 3 (Composition API)
- **UI组件库**: PrimeVue
- **CSS框架**: Tailwind CSS
- **图表库**: ECharts
- **状态管理**: Pinia
- **路由**: Vue Router

### 4.3 代码规范
- **Python**: PEP 8，4空格缩进
- **JavaScript**: ESLint + Prettier
- **注释**: 中英文结合，关键函数详细注释
- **Git提交**: Conventional Commits

---

## 5. 数据库架构

### 5.1 核心表结构

```
admins          - 管理员表
logs            - 日志文件表
fights          - 战斗记录表
members         - 成员表
fight_stats     - 战斗统计表
skills          - 技能表
skill_events    - 技能事件表
builds          - Build配置表
ai_reports      - AI报告表
```

详见 `SPEC.md` 文档。

---

## 6. 开发环境配置

### 6.1 后端环境
```bash
# 1. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 初始化数据库
python database/migrations/init_db.py

# 4. 启动开发服务器
python main.py
# 或
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 6.2 前端环境
```bash
# 1. 安装依赖
npm install

# 2. 启动开发服务器
npm run dev
```

---

## 7. 测试计划

### 7.1 测试覆盖率目标
- **整体覆盖率**: ≥ 80%
- **核心业务逻辑**: 100%
- **API接口**: 100%

### 7.2 测试类型
1. **单元测试**: 服务层、工具函数
2. **集成测试**: API接口、数据库操作
3. **端到端测试**: 关键业务流程

---

## 8. 里程碑

| 里程碑 | 内容 | 目标时间 |
|--------|------|----------|
| M1 | 完成基础架构和核心API | 第1周 |
| M2 | 完成日志解析和数据分析 | 第2周 |
| M3 | 完成AI分析功能 | 第3周 |
| M4 | 前端对接和优化 | 第4周 |
| M5 | 测试完善和部署上线 | 第5周 |

---

## 9. 风险管理

| 风险 | 影响 | 应对措施 |
|------|------|----------|
| zevtc解析复杂度 | 高 | 预留更多时间研究格式 |
| AI模型准确性 | 中 | 先使用规则引擎，后期迭代 |
| 前端对接延迟 | 中 | 保持API文档同步更新 |
| 性能瓶颈 | 中 | 提前做压力测试 |

---

## 10. 后续规划

### 10.1 功能扩展
- 实时战斗监控
- 微信/Discord通知
- 多公会支持
- 移动端适配

### 10.2 性能优化
- Redis缓存
- 数据库读写分离
- API响应压缩
- CDN加速静态资源

---

*文档版本: 1.0.0*
*创建日期: 2026-04-27*
*最后更新: 2026-04-27*

