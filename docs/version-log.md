# 文档体系全局版本变更日志

> **版本**: v3.0.0  
> **更新日期**: 2026-05-05  
> **维护责任人*: 系统文档维护团队

---

## v3.0.0 - 2026-05-05

**变更类型**: 依据代码全面更新  
**责任人*: 系统文档维护团队

### 主要变更

1. **依据代码全面更新**: 所有核心文档依据当前系统实际代码进行校对和更新
2. **数据库文档*: 更新 `schema-design.md`/`database-guide.md`/`storage-strategy.md`/`zevtc-complete-schema-design.md`，明确ZEVTC 原始数据体系已废弃，仅保留EI JSON 同步模型
3. **前端架构文档**: 更新 `architecture-guide.md`/`development-standards.md`，反映实际技术栈（Vite + PrimeVue Aura + Tailwind + Pinia）和命名规范
4. **API 文档**: 更新 `api-interface-documentation.md` 及子文档，端点总数件162 修正一112，补充已知问题（monitoring 前缀重复、响应模型不统一等）
5. **部署文档**: 更新 `deploy-debian12.md`/`deploy-docker-ecs.md`，与 `install.sh`/`docker-compose.yml`/`Dockerfile` 实际配置对齐
6. **功能模块文档**: 更新 `ai-integration.md`/`batch-parse.md`/`skill-rotation.md`/`ei-report-api-design.md`/`data-storage-strategy.md`，反映当前实现状性7. **解析器文档*: 更新 `parser-specification.md`/`parser-troubleshooting.md`，反映双解析路径（dps.report API + 本地 EnhancedZevtcParser（8. **OpenAPI Schema**: 重新生成 `openapi_schema.json`（12 个路径9. **分类规范**: 新增 `document-classification-v2.md`，建立docs-internal/ 目录管理内部文档

### 受影响文档清南
| 文档 | 变更类型 |
|------|---------|
| `architecture-guide.md` | 全面重写 |
| `code-review-checklist.md` | 补充检查项 |
| `development-standards.md` | 全面重写 |
| `frontend-backend-conventions.md` | 补充角色、JWT、已知问题|
| `api-interface-documentation.md` | 全面重写（12 端点）|
| `auth-api.md` | 补充 change-password |
| `build-library-api-spec.md` | 更新状态为已实现|
| `combat-replay-architecture.md` | 更新后端仅透传说明 |
| `schema-design.md` | 全面重写（6 张表）|
| `database-guide.md` | 待更文|
| `storage-strategy.md` | 待更文|
| `zevtc-complete-schema-design.md` | 待更文|
| `parser-specification.md` | 待更文|
| `parser-troubleshooting.md` | 待更文|
| `ai-integration.md` | 待更文|
| `batch-parse.md` | 待更文|
| `skill-rotation.md` | 待更文|
| `ei-report-api-design.md` | 待更文|
| `data-storage-strategy.md` | 待更文|
| `deploy-debian12.md` | 待更文|
| `deploy-docker-ecs.md` | 待更文|
| `document-classification-v2.md` | 新增 |
| `openapi_schema.json` | 重新生成 |

---

## v2.0.0 - 2026-05-01

**变更类型**: 重大重构  
**责任人*: 系统文档维护团队

### 主要变更

1. **目录重构**：将平铺的64 个文档重组为 8 个主题分类目录2. **文档合并**：合并主题相关、内容重复的文档一18 个核心文档3. **去重清理**：删除5 组以上完全重复或高度相似的文档4. **命名规范**：修复乱码文件名，统一采用小写短横线命名法
5. **版本头标准化**：为每个文档添加包含版本号、更新日期、责任人、变更摘要的标准头部
6. **历史版本行*：为每个文档添加历史版本记录表格

### 合并映射详情

| 新文档| 合并来源（原文件名） |
|--------|---------------------|
| `01-specifications/project-specification.md` | `SPEC.md` + `DEV_PLAN.md` |
| `02-api/auth-api.md` | `AUTH_API_DOC.md` + `登录接口优化方案.md` |
| `02-api/combat-analysis-api.md` | `COMBAT_ANALYSIS_API.md` + `COMBAT_ANALYSIS_API_INTEGRATION_REPORT.md` + `BACKEND_ISSUE_ASSESSMENT_REPORT.md` + `COMBAT_ANALYSIS_API_EVALUATION_REPORT.md` + `FRONTEND_COMMUNICATION_GUIDE.md` |
| `02-api/dictionary-api.md` | `dictionary_api_usage.md` + `字典功能使用指南.md` + `字典功能前端开发指南md` + `COLOR_FIX_REPORT.md` |
| `02-api/game-data-api.md` | `GAME_DATA_SERVICE.md` + `GAME_DATA_IMPLEMENTATION_SUMMARY.md` + `PROFESSION_BUFF_SKILL_ANALYSIS.md` |
| `03-database/schema-design.md` | `DATABASE_SCHEMA_DESIGN.md` + `ZEVTC_SCHEMA_COMPATIBILITY_REPORT.md` + `ZEVTC_ADMINS_SQL_COMPATIBILITY_REPORT.md` + `DATABASE_IMPROVEMENT_REPORT.md` |
| `03-database/database-guide.md` | `DATABASE_TEST_PLAN.md` + `MYSQL_TEST_GUIDE.md` + `database_reset_guide.md` + `database_upgrade_guide.md` + `BUGFIX_DB_TYPE_CASE.md` |
| `03-database/storage-strategy.md` | `STORAGE_CAPACITY_ANALYSIS.md` + `PARSE_AND_CLEAN_STRATEGY.md` + `重复解析处理策略分析.md` |
| `04-parser/parser-specification.md` | `PARSER_UPGRADE_REPORT.md` + `DATA_JSON_FIELDS.md` + `Elite Insights解析器能力分析与API设计方案.md` + `PERFORMANCE_OPTIMIZATIONS.md` |
| `04-parser/parser-troubleshooting.md` | `PARSER_FIX_REPORT.md` + `DAMAGE_FIX_REPORT.md` + `UPLOAD_FIX_REPORT.md` + `PROJECT_UPDATE_SUMMARY.md` |
| `05-features/skill-rotation.md` | `SKILL_ROTATION_ISSUE_SOLUTION.md` + `skill_rotation_issue_report.md` + `skill_rotation_final_analysis.md` + `complete_skill_rotation_verification_report.md` + `技能循环系统验证完成报告md` + `玩家查询问题诊断报告.md` + `skill_rotation_api_test_report.md` |
| `05-features/batch-parse.md` | `批量解析功能前端对接文档.md` |
| `05-features/ai-integration.md` | `AI_INTEGRATION_GUIDE.md` |
| `06-testing/test-reports-archive.md` | `COMBAT_ANALYSIS_TEST_REPORT.md` + `COMBAT_ANALYSIS_TEST_REPORT_V2.md` + `完整战斗分析系统测试报告.md` + `SERVICE_LAYER_TEST_REPORT.md` + `SIMPLE_TEST_REPORT.md` + `INTEGRATION_TEST_REPORT.md` + `dictionary_business_rules_test_report.md` + `测试报告模板指南.md` |
| `07-reports/optimization-report.md` | `OPTIMIZATION_REPORT.md` + `OPTIMIZATION_DESIGN_DOC.md` + `FRONTEND_BACKEND_OPTIMIZATION_REPORT.md` |
| `07-reports/code-review-report.md` | `code_review_cleanup_report.md` + `GARBLED_FIX_REPORT.md` |
| `07-reports/task-completion-log.md` | `TASK_COMPLETE_REPORT.md` |

### 删除清单

| 删除文件 | 删除原因 |
|---------|---------|
| `ZEVTC_ADMINS_SQL_COMPATIBILITY_REPORT copy.md` | 一`ZEVTC_ADMINS_SQL_COMPATIBILITY_REPORT.md` 内容完全一自|
| `FRONTEND_COMMUNICATION_GUIDE.md` | 一`COMBAT_ANALYSIS_API_EVALUATION_REPORT.md` 内容重复，已合并 |
| `skill_rotation_data_analysis.txt` | 一次性数据分析，无长期保存价值|
| `skill_rotation_data_documentation.md` | 内容已合并至 `skill-rotation.md` |

---

## v1.0.0 - 2026-04-27 ~ 2026-05-01

**变更类型**: 初始积累  
**责任人*: 帅妹妹丶.8297、技术团队、系统优化团队
### 说明

此阶段为项目文档的原始积累期，各模块文档独立创建，无统一目录结构和命名规范。共产生级64 一Markdown/文本文件，平铺存放于 `docs/` 根目录、
主要文档按时间线产生）- **2026-04-27**: SPEC.md、DEV_PLAN.md、FRONTEND_BACKEND_CONVENTIONS.md、Elite Insights解析器能力分析与API设计方案.md 等- **2026-04-28**: AUTH_API_DOC.md、DATA_JSON_FIELDS.md、GAME_DATA_SERVICE.md、OPTIMIZATION_REPORT.md 等- **2026-04-29**: COMBAT_ANALYSIS_API.md、COMBAT_ANALYSIS_API_INTEGRATION_REPORT.md、INTEGRATION_TEST_REPORT.md、PARSER_UPGRADE_REPORT.md 等- **2026-04-30**: BACKEND_ISSUE_ASSESSMENT_REPORT.md、COLOR_FIX_REPORT.md、FRONTEND_COMMUNICATION_GUIDE.md、DATABASE_IMPROVEMENT_REPORT.md 等- **2026-05-01**: AI_INTEGRATION_GUIDE.md、DATABASE_SCHEMA_DESIGN.md、STORAGE_CAPACITY_ANALYSIS.md、ZEVTC_SCHEMA_COMPATIBILITY_REPORT.md 等