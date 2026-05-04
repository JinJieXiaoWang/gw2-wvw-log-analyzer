# GW2 WVW 日志解析管理系统 - 文档中心

> **文档版本**: v2.1  
> **更新日期**: 2026-05-05  
> **责任人**: 帅姐姐

---

## 📋 文档体系说明

本文档中心采用分类目录结构，将项目文档按 **功能领域** 组织为编号主题目录。所有文档已按 [文档分类规范](./document-classification-v2.md) 划分为**核心文档**（纳入 Git）与**内部文档**（不纳入 Git）。

### 文档分类

| 类别 | 位置 | 说明 | Git 策略 |
|------|------|------|----------|
| 核心文档 | `docs/` 根目录及编号子目录 | 面向用户/运维/API消费者/开发团队的长期维护文档 | ✅ 纳入 Git |
| 内部文档 | `docs-internal/` 目录 | 开发阶段专用的审计、测试、问题排查、历史归档 | ❌ 不纳入 Git |

> 内部文档存放于项目根目录的 `docs-internal/` 文件夹，包含 `audits/`、`reports/`、`issues/`、`assets/`、`archives/` 子目录。详见 [document-classification-v2.md](./document-classification-v2.md)。

---

## 📚 文档目录

### 一、项目指南与规范

| 文档 | 说明 | 版本 |
|------|------|------|
| [architecture-guide.md](./architecture-guide.md) | 前端架构规范与分层设计 | v2.0 |
| [code-review-checklist.md](./code-review-checklist.md) | 代码审查检查清单 | v1.0 |
| [01-project-guide/development-standards.md](./01-project-guide/development-standards.md) | 编码规范、CSS管理、组件指南、主题系统 | v2.0 |
| [01-specifications/project-specification.md](./01-specifications/project-specification.md) | 技术规范与开发计划 | v2.0 |
| [01-specifications/frontend-backend-conventions.md](./01-specifications/frontend-backend-conventions.md) | 前后端对接方式约定 | v1.1 |

### 二、API 文档

| 文档 | 说明 | 版本 |
|------|------|------|
| [02-api-documentation/api-interface-documentation.md](./02-api-documentation/api-interface-documentation.md) | 完整 API 接口文档（162 端点） | v2.0 |
| [02-api-documentation/auth-api.md](./02-api-documentation/auth-api.md) | 认证接口文档（登录/登出/状态/权限） | v2.0 |
| [02-api-documentation/combat-analysis-api.md](./02-api-documentation/combat-analysis-api.md) | 战斗分析 API 与对接问题记录 | v2.0 |
| [02-api-documentation/dictionary-api.md](./02-api-documentation/dictionary-api.md) | 字典功能 API 与前端对接指南 | v2.0 |
| [02-api-documentation/batch-parse-api.md](./02-api-documentation/batch-parse-api.md) | 批量解析功能前端对接文档 | v1.1 |
| [build-library-api-spec.md](./build-library-api-spec.md) | Build 图书馆 API 规范 | v1.0 |
| [openapi_schema.json](./openapi_schema.json) | FastAPI 原生 OpenAPI 规格 | - |

### 三、数据分析

| 文档 | 说明 | 版本 |
|------|------|------|
| [03-data-analysis/ei-data-format.md](./03-data-analysis/ei-data-format.md) | Elite Insights 数据格式规范与解析器能力分析 | v2.0 |

### 四、数据库设计

| 文档 | 说明 | 版本 |
|------|------|------|
| [03-database/database-guide.md](./03-database/database-guide.md) | 数据库操作与测试指南 | v2.0 |
| [03-database/schema-design.md](./03-database/schema-design.md) | 数据库表结构设计说明 | v2.0 |
| [03-database/storage-strategy.md](./03-database/storage-strategy.md) | 存储策略与容量分析 | v2.0 |
| [03-database/zevtc-complete-schema-design.md](./03-database/zevtc-complete-schema-design.md) | ZEVTC 完整 Schema 设计 | v1.0 |
| [03-database/zevtc_complete_schema.sql](./03-database/zevtc_complete_schema.sql) | ZEVTC 完整 Schema SQL 脚本 | - |

### 五、解析器文档

| 文档 | 说明 | 版本 |
|------|------|------|
| [04-parser/parser-specification.md](./04-parser/parser-specification.md) | 解析器规范与设计文档 | v2.0 |
| [04-parser/parser-troubleshooting.md](./04-parser/parser-troubleshooting.md) | 解析器问题排查手册 | v2.0 |

### 六、功能模块设计

| 文档 | 说明 | 版本 |
|------|------|------|
| [05-features/skill-rotation.md](./05-features/skill-rotation.md) | 技能循环功能与问题排查手册 | v3.0 |
| [05-features/ai-integration.md](./05-features/ai-integration.md) | AI 模型集成实现方案 | v1.1 |
| [05-features/batch-parse.md](./05-features/batch-parse.md) | 批量解析功能设计文档 | v1.1 |
| [05-features/ei-report-api-design.md](./05-features/ei-report-api-design.md) | EI 完整报告 API 设计 | v1.0 |
| [05-features/data-storage-strategy.md](./05-features/data-storage-strategy.md) | ZEVTC 多表数据存储策略 | v1.0 |

### 七、部署指南

| 文档 | 说明 | 版本 |
|------|------|------|
| [06-deployment/deploy-debian12.md](./06-deployment/deploy-debian12.md) | Debian 12 裸机部署指南 | v1.0 |
| [06-deployment/deploy-docker-ecs.md](./06-deployment/deploy-docker-ecs.md) | Docker/ECS 部署指南 | v1.0 |

### 八、产品需求

| 文档 | 说明 | 版本 |
|------|------|------|
| [requirements.md](./requirements.md) | 完整产品需求文档（含AI模块） | v1.0 |

---

## 📝 变更日志

- **文档体系版本**: 详见 [version-log.md](./version-log.md)
- **系统版本变更**: 详见 [change-log.md](./change-log.md)

---

## 🔗 快速导航

- **新成员入门**: 从 [architecture-guide.md](./architecture-guide.md) 开始
- **前端开发**: 参考 [development-standards.md](./01-project-guide/development-standards.md)
- **API 对接**: 阅读 [api-interface-documentation.md](./02-api-documentation/api-interface-documentation.md)
- **认证接口**: 查看 [auth-api.md](./02-api-documentation/auth-api.md)
- **战斗数据**: 参考 [combat-analysis-api.md](./02-api-documentation/combat-analysis-api.md)
- **数据库运维**: 参考 [03-database/database-guide.md](./03-database/database-guide.md)
- **部署上线**: 参考 [06-deployment/deploy-debian12.md](./06-deployment/deploy-debian12.md)
