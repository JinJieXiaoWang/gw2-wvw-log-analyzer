# GW2 WvW 日志解析管理系统 —文档分类与管理方档
> **版本**: v2.0  
> **更新日期**: 2026-05-05  
> **适用范围**: `docs/` 目录下全部开发文档 
> **制定原则**: 以「受众对象+ 生命周期 + 部署后价值」三维标准进行系统性划分
---

## 一、分类原则与标准

### 1.1 三维分类模型

| 维度 | 第一类（纳入 Git）| 第二类（不纳充Git）|
|------|-------------------|---------------------|
| **受众对象** | 用户、运维人员、API 消费者、新团队成员 | 仅限开发团队内部，且为特定任务服务 |
| **生命周期** | 与系统同生命周期，长期维报| 随任务结束即完结，不再更文|
| **部署后价值* | 部署后仍需查阅、参考、迭件| 部署后无查阅价值，仅用于回源|

### 1.2 第一类—必须纳入 Git 的核心标准
满足以下**任一条件**即必须纳入版本控制：

1. **功能契约型*：定义系统对外提供的功能、接口、数据格式（API 文档、数据规范）
2. **架构规范型*：约束团队开发行为的规范与标准（编码规范、架构指南、审查清单）
3. **运维依赖型*：部署、配置、数据库初始化等运维操作直接依赖的文档或脚本
4. **产品基准型*：描述产品核心功能、权限规则、需求范围的产品文档
5. **长期参考型**：新成员 onboarding、日常开发中需要反复查阅的指南

### 1.3 第二类—无需纳入 Git 的排除标准
满足以下**任一条件**即应排除在版本控制之外：

1. **一次性报告*：针对特定时间点的审计、评估、分析报告，完成后不再更文2. **问题排查记录**：已解决的Bug 排查过程与根因分析，问题修复后失去持续价值3. **阶段性产版*：某一开发阶段的测试报告、优化报告，后续已被整合或覆目4. **历史归档**：内容已被新版文档合并吸收的旧版文档
5. **临时性文件*：数据样本、空模板、工具生成的中间文件
6. **任务型记录*：特定任务完成后的总结报告，不具备通用参考价值
---

## 二、第一类文档清单（纳入 Git）
> **命名规范**：统一采用 `小写短横线命名法`（kebab-case），目录采用 `两位数字-主题` 格式  
> **存放路径**：统一置于 `docs/` 根目录及编号子目录下

### 2.1 根目录导航与版本文档

| 序号 | 文档路径 | 说明 | 保留理由 |
|------|---------|------|----------|
| 1 | `docs/README.md` | 文档中心总览与导航| 所有人员入口文档|
| 2 | `docs/change-log.md` | 系统版本变更日志 | 用户与开发者了解功能迭件|
| 3 | `docs/version-log.md` | 文档体系版本变更日志 | 追踪文档本身的演进历变|
| 4 | `docs/document-classification.md` | 本文档（分类与管理方案） | 维护文档体系秩序 |

### 2.2 架构与规范文档
| 序号 | 文档路径 | 说明 | 保留理由 |
|------|---------|------|----------|
| 5 | `docs/architecture-guide.md` | 前端架构规范与分层设计| 长期维护架构一致性，新成员必说|
| 6 | `docs/code-review-checklist.md` | 代码审查检查清南| 保障代码质量的持续规范|
| 7 | `docs/combat-replay-architecture.md` | 战斗回放系统架构设计 | 核心子系统架构说明|

### 2.3 项目开发规范（`01-project-guide/` + `01-specifications/`）
| 序号 | 文档路径 | 说明 | 保留理由 |
|------|---------|------|----------|
| 8 | `docs/01-project-guide/development-standards.md` | 开发规范指南（编码/CSS/组件/主题）| 新成告onboarding 必备 |
| 9 | `docs/01-specifications/project-specification.md` | 技术规范与开发计分| 定义技术栈与里程碑 |
| 10 | `docs/01-specifications/frontend-backend-conventions.md` | 前后端对接方式约定| API 调用规范与协作标准|

### 2.4 API 接口文档（`02-api-documentation/`）
> **说明**：`02-api/` 目录为旧版API 文档，内容已被`02-api-documentation/` 整合覆盖，建议删除。保留`02-api-documentation/` 作为唯一 API 文档源、
| 序号 | 文档路径 | 说明 | 保留理由 |
|------|---------|------|----------|
| 11 | `docs/02-api-documentation/api-interface-documentation.md` | 完整 API 接口文档（62 端点）| 前后端对接核心依据|
| 12 | `docs/02-api-documentation/auth-api.md` | 认证接口文档 | 对接必备 |
| 13 | `docs/02-api-documentation/combat-analysis-api.md` | 战斗分析 API | 对接必备 |
| 14 | `docs/02-api-documentation/dictionary-api.md` | 字典功能 API | 对接必备 |
| 15 | `docs/02-api-documentation/batch-parse-api.md` | 批量解析 API | 对接必备 |
| 16 | `docs/build-library-api-spec.md` | Build 图书首API 规范 | 对接必备 |
| 17 | `docs/openapi_schema.json` | FastAPI 原生 OpenAPI 规格 | API 自动化工具依资|

### 2.5 数据规范（`03-data-analysis/`）
| 序号 | 文档路径 | 说明 | 保留理由 |
|------|---------|------|----------|
| 18 | `docs/03-data-analysis/ei-data-format.md` | Elite Insights 数据格式规范 | 数据解析核心参考|

### 2.6 数据库设计（`03-database/`）
> **说明**：`database/` 目录为旧版数据库文档，内容与 `03-database/` 高度重复，建议以 `03-database/` 为准，删除`database/` 目录、
| 序号 | 文档路径 | 说明 | 保留理由 |
|------|---------|------|----------|
| 19 | `docs/03-database/database-guide.md` | 数据库操作与测试指南 | 运维与扩展参考|
| 20 | `docs/03-database/schema-design.md` | 数据库表结构设计说明 | 运维与扩展参考|
| 21 | `docs/03-database/storage-strategy.md` | 存储策略与容量分构| 运维规划参考|
| 22 | `docs/03-database/zevtc-complete-schema-design.md` | ZEVTC 完整 Schema 设计 | 核心数据架构参考|
| 23 | `docs/03-database/zevtc_complete_schema.sql` | ZEVTC 完整 Schema SQL 脚本 | **部署必需** |
| 24 | `docs/03-database/gw2_wvw_log_schema.sql` | 数据库初始化脚本（若一database/ 下一致，择一保留）| **部署必需** |

### 2.7 功能模块设计（`04-parser/` + `05-features/`）
| 序号 | 文档路径 | 说明 | 保留理由 |
|------|---------|------|----------|
| 25 | `docs/04-parser/parser-specification.md` | 解析器规范与设计文档 | 解析器维护与升级依据 |
| 26 | `docs/04-parser/parser-troubleshooting.md` | 解析器问题排查手内| 常见问题参考，持续积累 |
| 27 | `docs/05-features/skill-rotation.md` | 技能循环功能与问题排查手册 | 核心功能说明与维护指南|
| 28 | `docs/05-features/ai-integration.md` | AI 模型集成实现方案 | AI 模块架构与配置参考|
| 29 | `docs/05-features/batch-parse.md` | 批量解析功能设计文档 | 核心功能说明 |
| 30 | `docs/05-features/ei-report-api-design.md` | EI 完整报告 API 设计 | 报告模块设计参考|
| 31 | `docs/05-features/data-storage-strategy.md` | ZEVTC 多表数据存储策略 | 数据架构核心参考|

### 2.8 部署与运维文档
| 序号 | 文档路径 | 说明 | 保留理由 |
|------|---------|------|----------|
| 32 | `docs/07-reports/deploy-debian12.md` | Debian 12 裸机部署指南 | **部署必需**，运维核心参考|
| 33 | `docs/07-reports/deploy-docker-ecs.md` | Docker/ECS 部署指南 | **部署必需**，运维核心参考|

### 2.9 产品需求文档
| 序号 | 文档路径 | 说明 | 保留理由 |
|------|---------|------|----------|
| 34 | `docs/需求文档md` | 完整产品需求文档| 产品功能基准，需求溯源|

---

## 三、第二类文档清单（不纳入 Git）
> **处理建议**：统一迁移至项目根目录 `docs-internal/` 目录下，并在 `.gitignore` 中排除 
> **命名规范**：保持原名或添加日期前缀以便排序  
> **子目录结构*：按 `reports/`, `audits/`, `issues/`, `archives/`, `assets/` 分类存放

### 3.1 一次性审计与评估报告

| 序号 | 当前路径 | 说明 | 迁移目标路径 |
|------|---------|------|-------------|
| 1 | `docs/CODE_QUALITY_AUDIT_REPORT_20260504.md` | 代码质量审计报告（026-05-04）| `docs-internal/audits/` |
| 2 | `docs/EVTC_TABLE_DELETION_ASSESSMENT.md` | EVTC 表删除可行性评优| `docs-internal/audits/` |
| 3 | `docs/EVTC_TABLE_DELETION_FINAL_ASSESSMENT.md` | EVTC 表删除最终评优| `docs-internal/audits/` |
| 4 | `docs/DATA_CONSISTENCY_ANALYSIS.md` | 数据一致性问题分构| `docs-internal/audits/` |
| 5 | `docs/evtc_event_audit_report.md` | EVTC 事件审计报告 | `docs-internal/audits/` |
| 6 | `docs/evtc_event_optimization_plan.md` | EVTC 事件优化计划 | `docs-internal/audits/` |
| 7 | `docs/ZEVTC_PARSE_ANALYSIS_20260426.md` | ZEVTC 解析分析（026-04-26）| `docs-internal/audits/` |

### 3.2 阶段性质量与优化报告

| 序号 | 当前路径 | 说明 | 迁移目标路径 |
|------|---------|------|-------------|
| 8 | `docs/07-reports/code-optimization-report-20260501.md` | 代码优化报告（026-05-01）| `docs-internal/reports/optimization/` |
| 9 | `docs/07-reports/optimization-report.md` | 系统优化报告整合版| `docs-internal/reports/optimization/` |
| 10 | `docs/07-reports/code-review-report.md` | 代码审查报告 | `docs-internal/reports/quality/` |
| 11 | `docs/07-reports/EVTC_TABLE_ASSESSMENT_REPORT.md` | EVTC 表评估报告| `docs-internal/reports/quality/` |
| 12 | `docs/07-reports/EVTC_TABLE_DELETION_ASSESSMENT.md` | EVTC 表删除评估（reports 版） | `docs-internal/reports/quality/` |
| 13 | `docs/07-reports/config_refactor_fastapi_20260504.md` | FastAPI 配置重构报告 | `docs-internal/reports/quality/` |
| 14 | `docs/07-reports/database_config_audit_20260504.md` | 数据库配置审计报告| `docs-internal/reports/quality/` |
| 15 | `docs/07-reports/evtc_table_audit_report_20260504.md` | EVTC 表审计报告| `docs-internal/reports/quality/` |
| 16 | `docs/07-reports/evtc_table_deletion_assessment_20260504.md` | EVTC 表删除评估（20260504 版） | `docs-internal/reports/quality/` |
| 17 | `docs/07-reports/PARSE_ENDPOINT_AUDIT_REPORT_20260504.md` | Parse 端点审计报告 | `docs-internal/reports/quality/` |
| 18 | `docs/EI_JSON_INGESTION_OPTIMIZATION.md` | EI JSON 数据导入优化 | `docs-internal/reports/optimization/` |
| 19 | `docs/EI_JSON_INGESTION_OPTIMIZATION_SUMMARY.md` | EI JSON 优化总结 | `docs-internal/reports/optimization/` |

### 3.3 测试报告

| 序号 | 当前路径 | 说明 | 迁移目标路径 |
|------|---------|------|-------------|
| 20 | `docs/06-testing/test-reports-archive.md` | 测试报告归档（整合版）| `docs-internal/reports/testing/` |
| 21 | `docs/07-reports/API_TEST_SUMMARY.md` | API 全面测试报告 | `docs-internal/reports/testing/` |
| 22 | `docs/07-reports/api_test_report.html` | API 测试 HTML 报告 | `docs-internal/reports/testing/` |

### 3.4 问题排查记录（已解决）
| 序号 | 当前路径 | 说明 | 迁移目标路径 |
|------|---------|------|-------------|
| 23 | `docs/前端渲染问题报告.md` | 前端渲染差异问题排查 | `docs-internal/issues/` |
| 24 | `docs/前端问题快速通知.md` | 前端问题快速通知 | `docs-internal/issues/` |
| 25 | `docs/07-reports/UPLOAD_BUG_ANALYSIS.md` | 上传失败根因分析与修复| `docs-internal/issues/` |

### 3.5 任务完成与迁移报告
| 序号 | 当前路径 | 说明 | 迁移目标路径 |
|------|---------|------|-------------|
| 26 | `docs/07-reports/task-completion-log.md` | 任务完成总结报告 | `docs-internal/reports/tasks/` |
| 27 | `docs/07-reports/ZEVTC_MIGRATION_REPORT.md` | ZEVTC 迁移实现报告 | `docs-internal/reports/tasks/` |

### 3.6 技术分析与过程文档（历史版本）

| 序号 | 当前路径 | 说明 | 迁移目标路径 |
|------|---------|------|-------------|
| 28 | `docs/COMPREHENSIVE_TECHNICAL_ANALYSIS.md` | 全面技术分析报告| `docs-internal/reports/technical/` |
| 29 | `docs/FRONTEND_INTEGRATION_GUIDE.md` | 前端登录状态管理技术文档| `docs-internal/reports/technical/` |
| 30 | `docs/API说明.md` | API 说明（旧版，已被新文档覆盖） | `docs-internal/archives/` |

### 3.7 临时资源文件

| 序号 | 当前路径 | 说明 | 迁移目标路径 |
|------|---------|------|-------------|
| 31 | `docs/08-assets/field_mapping_reference.csv` | 空文件（0 字节）| `docs-internal/assets/` 或删除|
| 32 | `docs/08-assets/sample_skill_rotation_data.json` | 技能循环数据样本| `docs-internal/assets/` |
| 33 | `docs/08-assets/可用玩家标识第json` | 玩家标识符数据样本| `docs-internal/assets/` |

### 3.8 重复/被整合的旧版文档（建议删除或归档）
| 序号 | 当前路径 | 说明 | 处理建议 |
|------|---------|------|----------|
| 34 | `docs/02-api/` 目录（ 个文件） | 旧版 API 文档 | 内容已被 `02-api-documentation/` 整合覆盖（*建议删除** |
| 35 | `docs/database/` 目录（ 个文件） | 旧版数据库文档| 内容已被 `03-database/` 整合覆盖（*建议删除** |
| 36 | `docs/08-assets/gw2_wvw_log_schema.sql` | 数据应Schema（assets 版） | 一`03-database/` 成`database/` 下文件重复，择一保留后其余删除|

---

## 四、重复文档清理建计
### 4.1 API 文档去重

| 保留 | 删除 | 理由 |
|------|------|------|
| `02-api-documentation/` | `02-api/` | `02-api-documentation/` 内容更完整（`api-interface-documentation.md` 131KB vs 130KB，`dictionary-api.md` 20KB vs 96KB但结构更清晰，且包含 `batch-parse-api.md`）|

### 4.2 数据库文档去重
| 保留 | 删除 | 理由 |
|------|------|------|
| `03-database/` | `database/` | `03-database/` 文件更新且结构更符合编号分类体系；`schema-design.md`（08KB）已整合更多内容 |

### 4.3 SQL 脚本去重

需人工比对以下三个位置的`.sql` 文件，保留最新版本：
- `database/gw2_wvw_log_schema.sql`（9,081 字节）- `03-database/zevtc_complete_schema.sql`（4,201 字节）- `database/zevtc_complete_schema.sql`（2,037 字节）
**建议**：保留`03-database/` 下的版本，删除`database/` 和`08-assets/` 下的重复 SQL、
---

## 五、管理方案实施细分
### 5.1 目录结构规范

#### Git 管理部分（`docs/`）
```
docs/
├── README.md                          # 文档中心总览
├── change-log.md                      # 系统版本变更日志
├── version-log.md                     # 文档体系版本日志
├── document-classification.md         # 本文档├── architecture-guide.md              # 前端架构规范
├── code-review-checklist.md           # 代码审查清单
├── combat-replay-architecture.md      # 战斗回放架构
├── build-library-api-spec.md          # Build图书馆API规范
├── openapi_schema.json                # OpenAPI规格
├── 需求文档md                         # 产品需求文档├── 01-project-guide/                  # 项目规范
─  ├── development-standards.md
─  └── frontend-backend-conventions.md（建议从 01-specifications 移入（├── 01-specifications/                 # 技术规样─  └── project-specification.md
├── 02-api-documentation/              # API接口文档（唯一API文档源）
─  ├── api-interface-documentation.md
─  ├── auth-api.md
─  ├── combat-analysis-api.md
─  ├── dictionary-api.md
─  └── batch-parse-api.md
├── 03-data-analysis/                  # 数据规范
─  └── ei-data-format.md
├── 03-database/                       # 数据库设计+ 部署脚本
─  ├── database-guide.md
─  ├── schema-design.md
─  ├── storage-strategy.md
─  ├── zevtc-complete-schema-design.md
─  ├── zevtc_complete_schema.sql
─  └── gw2_wvw_log_schema.sql（确认与 database/ 下版本后择一保留（├── 04-parser/                         # 解析器文档─  ├── parser-specification.md
─  └── parser-troubleshooting.md
├── 05-features/                       # 功能模块设计
─  ├── skill-rotation.md
─  ├── ai-integration.md
─  ├── batch-parse.md
─  ├── ei-report-api-design.md
─  └── data-storage-strategy.md
├── 06-deployment/                     # 部署指南（建议从 07-reports 移出（─  ├── deploy-debian12.md
─  └── deploy-docker-ecs.md
└── 08-assets/                         # 保留的通用资源（清理重复SQL后）
    └── （清理后仅保留通用模板类资源）
```

#### 面Git 管理部分（`docs-internal/`）
```
docs-internal/
├── audits/                            # 审计与评估报告─  ├── CODE_QUALITY_AUDIT_REPORT_20260504.md
─  ├── EVTC_TABLE_DELETION_ASSESSMENT.md
─  ├── EVTC_TABLE_DELETION_FINAL_ASSESSMENT.md
─  ├── DATA_CONSISTENCY_ANALYSIS.md
─  ├── evtc_event_audit_report.md
─  ├── evtc_event_optimization_plan.md
─  └── ZEVTC_PARSE_ANALYSIS_20260426.md
├── reports/
─  ├── optimization/                  # 优化报告
─  ─  ├── code-optimization-report-20260501.md
─  ─  ├── optimization-report.md
─  ─  ├── EI_JSON_INGESTION_OPTIMIZATION.md
─  ─  └── EI_JSON_INGESTION_OPTIMIZATION_SUMMARY.md
─  ├── quality/                       # 质量报告
─  ─  ├── code-review-report.md
─  ─  ├── EVTC_TABLE_ASSESSMENT_REPORT.md
─  ─  ├── config_refactor_fastapi_20260504.md
─  ─  ├── database_config_audit_20260504.md
─  ─  ├── evtc_table_audit_report_20260504.md
─  ─  ├── evtc_table_deletion_assessment_20260504.md
─  ─  └── PARSE_ENDPOINT_AUDIT_REPORT_20260504.md
─  ├── testing/                       # 测试报告
─  ─  ├── test-reports-archive.md
─  ─  ├── API_TEST_SUMMARY.md
─  ─  └── api_test_report.html
─  ├── tasks/                         # 任务完成报告
─  ─  ├── task-completion-log.md
─  ─  └── ZEVTC_MIGRATION_REPORT.md
─  └── technical/                     # 技术分构─      ├── COMPREHENSIVE_TECHNICAL_ANALYSIS.md
─      └── FRONTEND_INTEGRATION_GUIDE.md
├── issues/                            # 已解决问题记录─  ├── 前端渲染问题报告.md
─  ├── 前端问题快速通知.md
─  └── UPLOAD_BUG_ANALYSIS.md
├── assets/                            # 临时数据样本
─  ├── sample_skill_rotation_data.json
─  └── 可用玩家标识第json
├── archives/                          # 历史归档
─  └── API说明.md
└── .gitkeep                           # 确保空目录被Git追踪（可选）
```

### 5.2 Git 配置

在项目根目录 `.gitignore` 中添加：

```gitignore
# 内部开发文档（不纳入版本控制）
docs-internal/

# 报告生成产物
*.html
!docs/07-reports/*.html  # 如保留特定HTML，需单独处理
```

> 注意：`docs-internal/` 整体排除，但其中若有需要共享的模板或基准文件，可单独讨论、
### 5.3 文档命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 英文文档 | 全小写，短横线分隔| `code-review-checklist.md` |
| 中文文档 | 保留中文，必要时加前缀 | `需求文档md`、`前端渲染问题报告.md` |
| 日期标记 | YYYYMMDD 后缀，下划线分隔 | `code-audit-report_20260501.md` |
| 目录命名 | 两位数字-主题 | `01-project-guide/`、`02-api-documentation/` |

### 5.4 定期清理机制

| 周期 | 动作 | 责任人|
|------|------|--------|
| 每月 | 检查`docs-internal/issues/` 中已过期的问题记录，确认是否归档 | 文档维护告|
| 每季应| 评估 `docs-internal/reports/` 中报告的有效性，删除已被完全覆盖的内定| 技术负责人 |
| 每次发版 | 将当前版本的阶段性报告归档至 `docs-internal/archives/` | 文档维护告|
| 每年 | 全面审查 `docs/` 下核心文档的时效性，更新过期内容 | 架构常|

### 5.5 备份建议

`docs-internal/` 虽排除在 Git 之外，但建议通过以下方式留存）
1. **团队知识应*：迁移至 Notion / Confluence / 飞书文档等在线协作平变2. **私有仓库**：创建独立的 `gw2-apex-internal` 私有仓库管理（如团队有私有化部署需求）
3. **本地快照**：定期打化`docs-internal/` 一`docs-internal_YYYYMMDD.zip` 存入团队共享网盘

---

## 六、执行清南
| 步骤 | 任务 | 优先级| 说明 |
|------|------|--------|------|
| 1 | 创建 `docs-internal/` 目录结构 | 🔴 高| 按本文档 5.1 节创建子目录 |
| 2 | 迁移第二类文档| 🔴 高| 按第三类清单迁移文件 |
| 3 | 删除重复目录 `02-api/` | 🟡 一| 确认 `02-api-documentation/` 已包含全部内容后删除 |
| 4 | 删除重复目录 `database/` | 🟡 一| 确认 `03-database/` 已包含全部内容后删除 |
| 5 | 移动部署文档自`06-deployment/` | 🟡 一| 件`07-reports/` 移出，建立独立分类|
| 6 | 更新 `.gitignore` | 🔴 高| 添加 `docs-internal/` 排除规则 |
| 7 | 更新 `docs/README.md` | 🟡 一| 反映新的目录结构与分类策留|
| 8 | 团队同步 | 🟢 使| 在团队会议或文档中告知新的文档管理规范|

---

## 附录：当前全部文档速查行
| 路径 | 分类建议 | 处理方式 |
|------|---------|----------|
| `docs/01-project-guide/development-standards.md` | 第一类| 保留 |
| `docs/01-specifications/frontend-backend-conventions.md` | 第一类| 保留 |
| `docs/01-specifications/project-specification.md` | 第一类| 保留 |
| `docs/02-api/*` (4 文件) | 重复 | **删除**（已被02-api-documentation 覆盖）|
| `docs/02-api-documentation/*` (5 文件) | 第一类| 保留 |
| `docs/03-data-analysis/ei-data-format.md` | 第一类| 保留 |
| `docs/03-database/*` (6 文件) | 第一类| 保留 |
| `docs/04-parser/*` (2 文件) | 第一类| 保留 |
| `docs/05-features/*` (5 文件) | 第一类| 保留 |
| `docs/06-testing/test-reports-archive.md` | 第二类| 迁移自docs-internal/reports/testing/ |
| `docs/07-reports/api_test_report.html` | 第二类| 迁移自docs-internal/reports/testing/ |
| `docs/07-reports/API_TEST_SUMMARY.md` | 第二类| 迁移自docs-internal/reports/testing/ |
| `docs/07-reports/code-optimization-report-20260501.md` | 第二类| 迁移自docs-internal/reports/optimization/ |
| `docs/07-reports/code-review-report.md` | 第二类| 迁移自docs-internal/reports/quality/ |
| `docs/07-reports/config_refactor_fastapi_20260504.md` | 第二类| 迁移自docs-internal/reports/quality/ |
| `docs/07-reports/database_config_audit_20260504.md` | 第二类| 迁移自docs-internal/reports/quality/ |
| `docs/07-reports/deploy-debian12.md` | 第一类| 保留（建议移自06-deployment/）|
| `docs/07-reports/deploy-docker-ecs.md` | 第一类| 保留（建议移自06-deployment/）|
| `docs/07-reports/EVTC_TABLE_ASSESSMENT_REPORT.md` | 第二类| 迁移自docs-internal/reports/quality/ |
| `docs/07-reports/evtc_table_audit_report_20260504.md` | 第二类| 迁移自docs-internal/reports/quality/ |
| `docs/07-reports/evtc_table_deletion_assessment_20260504.md` | 第二类| 迁移自docs-internal/reports/quality/ |
| `docs/07-reports/optimization-report.md` | 第二类| 迁移自docs-internal/reports/optimization/ |
| `docs/07-reports/PARSE_ENDPOINT_AUDIT_REPORT_20260504.md` | 第二类| 迁移自docs-internal/reports/quality/ |
| `docs/07-reports/task-completion-log.md` | 第二类| 迁移自docs-internal/reports/tasks/ |
| `docs/07-reports/UPLOAD_BUG_ANALYSIS.md` | 第二类| 迁移自docs-internal/issues/ |
| `docs/07-reports/ZEVTC_MIGRATION_REPORT.md` | 第二类| 迁移自docs-internal/reports/tasks/ |
| `docs/08-assets/field_mapping_reference.csv` | 第二类| 删除（空文件）或迁移自docs-internal/assets/ |
| `docs/08-assets/gw2_wvw_log_schema.sql` | 重复 | **删除**（与 database/ 成03-database/ 重复）|
| `docs/08-assets/sample_skill_rotation_data.json` | 第二类| 迁移自docs-internal/assets/ |
| `docs/08-assets/可用玩家标识第json` | 第二类| 迁移自docs-internal/assets/ |
| `docs/API说明.md` | 第二类| 迁移自docs-internal/archives/ |
| `docs/architecture-guide.md` | 第一类| 保留 |
| `docs/build-library-api-spec.md` | 第一类| 保留 |
| `docs/change-log.md` | 第一类| 保留 |
| `docs/CODE_QUALITY_AUDIT_REPORT_20260504.md` | 第二类| 迁移自docs-internal/audits/ |
| `docs/code-review-checklist.md` | 第一类| 保留 |
| `docs/combat-replay-architecture.md` | 第一类| 保留 |
| `docs/COMPREHENSIVE_TECHNICAL_ANALYSIS.md` | 第二类| 迁移自docs-internal/reports/technical/ |
| `docs/DATA_CONSISTENCY_ANALYSIS.md` | 第二类| 迁移自docs-internal/audits/ |
| `docs/document-classification.md` | 第一类| 保留（更新为本文档） |
| `docs/EI_JSON_INGESTION_OPTIMIZATION.md` | 第二类| 迁移自docs-internal/reports/optimization/ |
| `docs/EI_JSON_INGESTION_OPTIMIZATION_SUMMARY.md` | 第二类| 迁移自docs-internal/reports/optimization/ |
| `docs/evtc_event_audit_report.md` | 第二类| 迁移自docs-internal/audits/ |
| `docs/evtc_event_optimization_plan.md` | 第二类| 迁移自docs-internal/audits/ |
| `docs/EVTC_TABLE_DELETION_ASSESSMENT.md` | 第二类| 迁移自docs-internal/audits/ |
| `docs/EVTC_TABLE_DELETION_FINAL_ASSESSMENT.md` | 第二类| 迁移自docs-internal/audits/ |
| `docs/FRONTEND_INTEGRATION_GUIDE.md` | 第二类| 迁移自docs-internal/reports/technical/ |
| `docs/openapi_schema.json` | 第一类| 保留 |
| `docs/README.md` | 第一类| 保留 |
| `docs/version-log.md` | 第一类| 保留 |
| `docs/ZEVTC_PARSE_ANALYSIS_20260426.md` | 第二类| 迁移自docs-internal/audits/ |
| `docs/前端渲染问题报告.md` | 第二类| 迁移自docs-internal/issues/ |
| `docs/前端问题快速通知.md` | 第二类| 迁移自docs-internal/issues/ |
| `docs/需求文档md` | 第一类| 保留 |
| `docs/database/*` (6 文件) | 重复 | **删除**（已被03-database/ 整合覆盖）|
