# GW2-APEX 文档分类与管理规范
> **版本**: v1.0  
> **更新日期**: 2026-05-05  
> **适用范围**: 本文档适用于GW2-APEX 项目文档体系的维护与管理

---

## 一、分类原分
为适配线上部署需求，将项目文档按**受众对象**一*生命周期**划分为两大类）
| 分类 | 受众 | 生命周期 | Git 策略 |
|------|------|----------|----------|
| **线上文档** | 系统用户、运维人员、API 消费考| 长期维护 | ✅纳入 Git |
| **内部文档** | 开发团队成告| 随项目演进归档| ❌不纳充Git |

---

## 二、线上文档（纳入 Git）
线上文档是与**系统功能使用直接相关**的核心文档，部署后仍需持续维护与查阅、
### 2.1 文档清单

#### 根目录导航文档| 文档 | 说明 | 保留理由 |
|------|------|----------|
| `README.md` | 文档中心总览与导航| 用户/开发者入变|
| `change-log.md` | 版本变更日志 | 用户了解功能迭代 |
| `document-classification.md` | 本文档，说明分类规范 | 维护文档体系秩序 |

#### 架构与规范| 文档 | 说明 | 保留理由 |
|------|------|----------|
| `architecture-guide.md` | 前端架构规范指南 | 长期维护架构一致性|
| `code-review-checklist.md` | 代码审查检查清南| 保障代码质量 |
| `combat-replay-architecture.md` | 战斗回放系统架构 | 核心子系统架构说明|

#### 项目开发规范| 文档 | 说明 | 保留理由 |
|------|------|----------|
| `01-project-guide/development-standards.md` | 开发规范指南（编码/CSS/组件/主题）| 新成告onboarding 必备 |

#### API 接口文档
| 文档 | 说明 | 保留理由 |
|------|------|----------|
| `02-api-documentation/api-interface-documentation.md` | 完整 API 接口文档（62 端点）| 用户/前端/后端对接依据 |
| `02-api-documentation/auth-api.md` | 认证接口文档 | 对接必备 |
| `02-api-documentation/combat-analysis-api.md` | 战斗分析 API | 对接必备 |
| `02-api-documentation/dictionary-api.md` | 字典功能 API | 对接必备 |
| `02-api-documentation/batch-parse-api.md` | 批量解析 API | 对接必备 |
| `build-library-api-spec.md` | Build 图书首API 规范 | 对接必备 |

#### 数据规范
| 文档 | 说明 | 保留理由 |
|------|------|----------|
| `03-data-analysis/ei-data-format.md` | Elite Insights 数据格式规范 | 数据解析参考|

#### 数据库设计| 文档 | 说明 | 保留理由 |
|------|------|----------|
| `database/DATABASE_SCHEMA_DESIGN.md` | 数据库表结构设计说明 | 运维与扩展参考|
| `database/zevtc-complete-schema-design.md` | ZEVTC 完整 Schema 设计 | 运维与扩展参考|
| `database/PARSE_AND_CLEAN_STRATEGY.md` | 解析与清洗策留| 数据维护参考|
| `database/STORAGE_CAPACITY_ANALYSIS.md` | 存储容量分析 | 运维规划参考|
| `database/gw2_wvw_log_schema.sql` | 数据库初始化脚本 | **部署必需** |
| `database/zevtc_complete_schema.sql` | ZEVTC 完整 Schema SQL | **部署必需** |

---

## 三、内部文档（不纳充Git）
内部文档属于**开发阶段专用*，具有临时性、一次性或历史归档性质。已统一迁移自`docs-internal/` 目录，并通过 `.gitignore` 排除、
### 3.1 文档清单

#### 审计与评估报告（一次性）
| 文档 | 说明 | 存放位置 |
|------|------|----------|
| `PROJECT_STRUCTURE_AUDIT_REPORT.md` | 项目结构审计报告 | `docs-internal/` |

#### 质量与测试报告（阶段性）
| 文档 | 说明 | 存放位置 |
|------|------|----------|
| `code-audit-report.md` | 代码审计报告 | `docs-internal/quality-reports/` |
| `integration-test-report.md` | 前后端集成测试报告| `docs-internal/quality-reports/` |
| `optimization-report.md` | 项目优化报告 | `docs-internal/quality-reports/` |

#### 验证与一致性报告（一次性）
| 文档 | 说明 | 存放位置 |
|------|------|----------|
| `doc-code-cross-validation.md` | 文档与代码一致性分构| `docs-internal/validation/` |

#### 开发过程文档（历史操作记录）| 文档 | 说明 | 存放位置 |
|------|------|----------|
| `api-integration-guide.md` | API 对接总规范（开发过程版）| `docs-internal/` |
| `FRONTEND_INTEGRATION_GUIDE.md` | 前端登录状态管理技术文档| `docs-internal/` |
| `VIEWS_REFACTORING_GUIDE.md` | Views 目录重构说明 | `docs-internal/` |
| `project-overview.md` | 项目概览（v1 整合版，内容已被新版覆盖）| `docs-internal/` |

#### 设计提案与草案（未最终确定）
| 文档 | 说明 | 存放位置 |
|------|------|----------|
| `ui-redesign-proposal.md` | UI 重设计方档| `docs-internal/` |

#### 问题排查与测试记录（临时性）
| 文档 | 说明 | 存放位置 |
|------|------|----------|
| `前端渲染问题报告.md` | 前端渲染差异问题报告 | `docs-internal/` |
| `图片颜色主题适配测试指南.md` | 图片颜色主题适配测试 | `docs-internal/` |

#### 数据库兼容性与工具脚本
| 文档 | 说明 | 存放位置 |
|------|------|----------|
| `ZEVTC_ADMINS_SQL_COMPATIBILITY_REPORT.md` | SQL 兼容性报告| `docs-internal/database/` |
| `ZEVTC_SCHEMA_COMPATIBILITY_REPORT.md` | Schema 兼容性报告| `docs-internal/database/` |
| `zevtc_parser.py` | Python 解析工具脚本 | `docs-internal/database/` |

#### 历史归档
| 文档 | 说明 | 存放位置 |
|------|------|----------|
| `archive/*` | 原始 30 份文档的历史归档 | `docs-internal/archive/` |

---

## 四、管理规范
### 4.1 新增文档准入规则

1. **线上文档**新增前需确认（   - 是否与系统功能使用直接相关？
   - 部署后是否仍需维护更新（   - 受众是否包含用户或运维人员？

2. **内部文档**应直接存放至 `docs-internal/` 对应子目录，无需额外审批、
### 4.2 定期清理机制

| 周期 | 动作 |
|------|------|
| 每季应| 检查`docs-internal/` 中是否有过期临时文件，及时清理|
| 每次大版本发常| 将当前版本的开发过程文档归档至 `docs-internal/archive/` |
| 每年 | 评估 `docs-internal/archive/` 内容，删除超迁2 年且无回溯价值的文档 |

### 4.3 备份建议

`docs-internal/` 目录虚excluded from Git，但建议通过以下方式备份）
- **团队知识应*: 迁移自Notion / Confluence / 飞书文档
- **私有仓库**: 创建独立的`gw2-apex-internal` 私有仓库管理
- **本地快照**: 定期打包存档至团队共享网目
---

## 五、目录结构速览

```
docs/
├── README.md                          # 文档总览
├── change-log.md                      # 版本变更日志
├── document-classification.md         # 本文档├── architecture-guide.md              # 架构规范
├── build-library-api-spec.md          # Build图书馆API
├── code-review-checklist.md           # 代码审查清单
├── combat-replay-architecture.md      # 战斗回放架构
─├── 01-project-guide/
─  └── development-standards.md       # 开发规范─├── 02-api-documentation/              # API接口文档
─  ├── api-interface-documentation.md
─  ├── auth-api.md
─  ├── combat-analysis-api.md
─  ├── dictionary-api.md
─  └── batch-parse-api.md
─├── 03-data-analysis/
─  └── ei-data-format.md              # 数据格式规范
─├── database/                          # 数据库设计+ 部署脚本
─  ├── DATABASE_SCHEMA_DESIGN.md
─  ├── zevtc-complete-schema-design.md
─  ├── PARSE_AND_CLEAN_STRATEGY.md
─  ├── STORAGE_CAPACITY_ANALYSIS.md
─  ├── gw2_wvw_log_schema.sql
─  └── zevtc_complete_schema.sql
─└── internal/                          # ❌不纳入Git
    ├── api-integration-guide.md
    ├── FRONTEND_INTEGRATION_GUIDE.md
    ├── project-overview.md
    ├── PROJECT_STRUCTURE_AUDIT_REPORT.md
    ├── ui-redesign-proposal.md
    ├── VIEWS_REFACTORING_GUIDE.md
    ├── 前端渲染问题报告.md
    ├── 图片颜色主题适配测试指南.md
    ├── archive/                         # 历史归档
    ├── database/                        # 兼容性报告+ 工具脚本
    ├── quality-reports/                 # 质量报告
    └── validation/                      # 验证报告
```
