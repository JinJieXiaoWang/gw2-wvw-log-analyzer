# AI 模型集成实现方案

> **版本**: v2.0
> **更新日期**: 2026-05-05
> **整合责任人**: 系统文档维护团队
> **变更摘要**: 更新为与实际代码完全一致，标注 analyze_fight / analyze_build 停用状态，补充完整端点与配置项

---

## 一、实现概述

本方案基于激战2 WvW 战场日志系统，集成了 AI 大语言模型能力，实现了：
1. **多模型提供商支持**: OpenAI, DeepSeek, Qwen
2. **智能提示词管理**: 预定义专业的分析模板
3. **响应质量评估**: 自动检查和优化 AI 输出
4. **多级降级策略**: 确保服务稳定性
5. **缓存优化**: 提高响应速度，降低成本

---

## 二、系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                        API 路由层                            │
│         app/routers/ai.py — HTTP 接口                        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                        业务服务层                            │
│    app/services/ai_service.py — AIOrchestrator              │
└────────────────────┬────────────────────────────────────────┘
                     │
    ┌────────────────┼────────────────┐
    ▼                ▼                ▼
┌─────────────┐ ┌───────────┐ ┌─────────────────┐
│ 模型客户端  │ │ 提示词    │ │ 质量评估       │
│ 模块       │ │ 模板      │ │ 降级处理       │
└─────────────┘ └───────────┘ └─────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│                      模型配置层                              │
│           app/config/ai_config.py — 统一配置管理            │
└─────────────────────────────────────────────────────────────┘
```

---

## 三、核心模块说明

### 1. 配置模块 (app/config/ai_config.py)

**功能**:
- 统一管理多提供商配置
- 支持环境变量配置
- 运行时配置检查

**关键配置项**:
```python
AI_ENABLED: bool = True  # AI 功能开关
AI_MODEL_PROVIDER: ModelProvider = ModelProvider.DEEPSEEK  # 默认提供商
AI_REQUEST_TIMEOUT: int = 60  # 超时设置
AI_CACHE_ENABLED: bool = True  # 缓存开关
AI_FALLBACK_ENABLED: bool = True  # 降级开关
```

### 2. 模型客户端 (app/core/ai_model_client.py)

**功能**:
- 支持多个模型提供商的统一接口
- 请求重试机制
- 缓存管理
- 响应包装

**类结构**:
```python
class BaseModelClient:  # 基类
class OpenAIClient(BaseModelClient):  # OpenAI 兼容接口
class DeepSeekClient(BaseModelClient):  # DeepSeek
class QwenClient(BaseModelClient):  # Qwen
class ModelClientFactory:  # 工厂模式创建客户端
class AIModelService:  # AI 服务封装
```

### 3. 提示词模板 (app/core/ai_prompt_templates.py)

**功能**:
- 预定义分析模板
- 响应解析优化
- 智能规则调整

**预定义模板**:
- `fight_analysis_v1`: 战斗分析
- `skill_rotation_v1`: 技能循环分析
- `build_optimization_v1`: Build 配置优化
- `trend_analysis_v1`: 趋势分析

### 4. 质量评估与降级 (app/core/ai_quality_fallback.py)

**功能**:
- 多维度质量评分
- 降级策略管理
- 规则化备用方案

**质量评估维度**:
```python
QualityMetric.ACCURACY: 准确性 (权重 0.3)
QualityMetric.RELEVANCE: 相关性 (权重 0.3)
QualityMetric.COMPLETENESS: 完整性 (权重 0.2)
QualityMetric.CONSISTENCY: 一致性 (权重 0.1)
QualityMetric.RESPONSE_TIME: 响应时间 (权重 0.1)
```

### 5. 业务服务 (app/services/ai_service.py)

**功能**:
- 整合所有 AI 模块
- 提供业务分析功能
- 管理 AI 报告

**核心类**:
```python
class AIOrchestrator:  # AI 编排器
    async def analyze_with_llm()  # 统一分析入口
```

---

## 四、API 端点

`app/routers/ai.py` 中定义的全部端点如下：

| 方法 | 路径 | 功能 | 状态 |
|------|------|------|------|
| GET | `/api/v1/ai/reports` | AI 报告列表 | ✅ 正常 |
| GET | `/api/v1/ai/reports/{report_id}` | 报告详情 | ✅ 正常 |
| DELETE | `/api/v1/ai/reports/{report_id}` | 删除报告 | ✅ 正常 |
| POST | `/api/v1/ai/analyze/fight/{fight_id}` | AI 分析战斗 | ⏸️ 已停用 |
| POST | `/api/v1/ai/analyze/build/{build_id}` | AI 分析 Build | ⏸️ 已停用 |
| GET | `/api/v1/ai/trend` | 趋势分析 | ✅ 正常 |
| GET | `/api/v1/ai/suggestions` | 优化建议 | ✅ 正常 |

> **停用说明**: `analyze_fight` / `analyze_build` 因 Fight / Build 模型变更已停用，但底层 AI 编排器、提示词模板、质量评估、多模型支持均完整保留，可随时恢复。

---

## 五、部署配置

### 环境变量

在 `.env` 文件中配置：

```bash
# 基础开关
AI_ENABLED=True
AI_MODEL_PROVIDER=deepseek

# DeepSeek 配置
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_API_BASE=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_MAX_TOKENS=4000
DEEPSEEK_TEMPERATURE=0.7

# Qwen 配置
QWEN_API_KEY=your_qwen_api_key
QWEN_API_BASE=https://dashscope.aliyuncs.com/api/v1
QWEN_MODEL=qwen-turbo
QWEN_MAX_TOKENS=4000

# OpenAI 配置
OPENAI_API_KEY=your_openai_api_key
OPENAI_API_BASE=https://api.openai.com/v1
OPENAI_MODEL=gpt-4-turbo
OPENAI_MAX_TOKENS=4000

# 高级配置
AI_REQUEST_TIMEOUT=60
AI_MAX_RETRIES=3
AI_CACHE_ENABLED=True
AI_CACHE_TTL=3600
AI_FALLBACK_ENABLED=True
AI_QUALITY_CHECK_ENABLED=True
```

### 安装依赖

```bash
pip install -r requirements.txt
```

新增依赖：
- `httpx>=0.24.0` — 异步 HTTP 客户端
- `openai>=1.0.0` — OpenAI SDK

---

## 六、数据库表

### `ai_reports`

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT PK | 报告 ID |
| report_type | VARCHAR(50) | 报告类型 |
| target_type | VARCHAR(50) | 目标类型 |
| target_id | BIGINT | 目标 ID |
| content | TEXT | 完整报告内容 |
| summary | TEXT | 报告摘要 |
| ai_score | FLOAT | AI 评分 |
| created_by | BIGINT | 创建者用户 ID |
| created_at | DATETIME | 创建时间 |
| is_public | BOOLEAN | 是否公开 |
| is_deleted | BOOLEAN | 是否已删除 |

---

## 七、质量保证机制

### 多级检查流程

```
LLM 响应 → JSON 解析 → 响应优化 → 质量评估 → (通过 / 降级)
```

### 降级链

```
主提供商失败 → 备用提供商 → 缓存 → 规则引擎 → 简化响应
```

### 监控指标

- 响应时间 < 30 秒
- 成功率 > 95%
- 质量评分 > 0.6
- 缓存命中率 > 40%

---

## 八、扩展指南

### 添加新的模型提供商

在 `app/config/ai_config.py` 中：
```python
class ModelProvider(str, Enum):
    # ... 现有 ...
    MY_NEW_PROVIDER = "my_provider"
```

在 `app/core/ai_model_client.py` 中：
```python
class MyNewProviderClient(BaseModelClient):
    async def chat_completion(self, messages, ...):
        # 实现调用逻辑
```

---

## 附录：文件清单

| 文件路径 | 说明 |
|---------|------|
| `app/config/ai_config.py` | AI 配置管理 |
| `app/core/ai_model_client.py` | 模型客户端 |
| `app/core/ai_prompt_templates.py` | 提示词模板 |
| `app/core/ai_quality_fallback.py` | 质量评估与降级 |
| `app/services/ai_service.py` | 业务服务 |
| `app/routers/ai.py` | API 路由 |
| `requirements.txt` | 依赖 |
