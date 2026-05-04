# 批量解析功能前端对接文档

> **版本**: v2.0
> **更新日期**: 2026-05-05
> **整合责任人**: 系统文档维护团队
> **变更摘要**: 更新为与实际代码完全一致，修正后端机制为数据库轮询+单线程+限流+指数退避，补充 retrying 状态与数据库表结构

---

## 文档信息

| 项目 | 内容 |
|------|------|
| 版本 | v2.0 |
| 创建日期 | 2026-04-29 |
| 更新日期 | 2026-05-05 |
| 文档类型 | 前端对接技术文档 |
| 适用对象 | 前端开发团队 |

---

## 1. 功能概述

### 1.1 功能描述

批量解析功能允许用户一次性选择多个日志文件（最多 100 个），提交到后台进行异步解析处理。该功能适用于：

- **批量导入场景**：用户上传多个日志文件后，需要统一解析
- **重新解析场景**：解析器升级后，需要对历史日志重新解析
- **大规模数据处理**：同时处理大量日志，提升处理效率

### 1.2 核心特性

- ✅ **异步执行**：后台任务队列异步处理，不阻塞前端
- ✅ **单线程处理**：后端采用单线程执行，配合限流与指数退避策略
- ✅ **实时进度**：支持查询解析进度，实时反馈处理状态
- ✅ **状态跟踪**：每个日志独立状态跟踪，精确掌控处理结果
- ✅ **错误处理**：单个日志失败不影响其他日志，完整错误信息反馈
- ✅ **数据覆盖**：支持覆盖旧数据或跳过已解析日志

### 1.3 数据流程

```
用户选择日志 → 创建批量任务 → 任务入队 → 后台处理
                                      ↓
前端轮询进度 ← 实时状态更新 ← 数据库轮询 + 单线程 + 限流 + 指数退避
                                      ↓
                                解析结果存储
```

### 1.4 后端处理机制

| 机制项 | 说明 |
|--------|------|
| 调度方式 | 数据库轮询 |
| 执行线程 | 单线程 |
| 流量控制 | 限流 |
| 重试策略 | 指数退避 |

---

## 2. 接口说明

### 2.1 基础信息

| 项目 | 内容 |
|------|------|
| 基础 URL | `http://127.0.0.1:8000/api/v1` |
| 数据格式 | JSON |
| 编码格式 | UTF-8 |
| 认证方式 | Bearer Token (JWT) |

### 2.2 通用请求头

所有接口都需要携带以下请求头：

```http
Content-Type: application/json; charset=utf-8
Authorization: Bearer {access_token}
```

---

## 3. 接口详情

### 3.1 创建批量解析任务

**功能**：创建批量解析任务并立即开始执行

**接口地址**：`/logs/batch-parse`

**HTTP 方法**：`POST`

#### 3.1.1 请求参数

**请求体 (Request Body)**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| task_name | string | 否 | 任务名称，用于标识任务 |
| log_ids | array[integer] | 是 | 需要解析的日志 ID 列表，最多 100 个 |
| overwrite | boolean | 否 | 是否覆盖已有数据，默认 true |

**请求示例**：

```json
{
  "task_name": "2026-04-29 批量解析任务",
  "log_ids": [1, 2, 3, 4, 5],
  "overwrite": true
}
```

#### 3.1.2 响应参数

**成功响应 (HTTP 200)**：

```json
{
  "success": true,
  "code": 200,
  "message": "批量解析任务创建成功",
  "data": {
    "id": 1,
    "task_name": "2026-04-29 批量解析任务",
    "status": "pending",
    "total_count": 5,
    "processed_count": 0,
    "success_count": 0,
    "failed_count": 0,
    "created_at": "2026-04-29T12:00:00Z",
    "started_at": null,
    "completed_at": null,
    "created_by": 1,
    "error_message": null,
    "log_ids": [1, 2, 3, 4, 5]
  }
}
```

**失败响应 (HTTP 400)**：

```json
{
  "success": false,
  "code": 400,
  "message": "日志 ID 列表不能为空",
  "data": null
}
```

#### 3.1.3 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| id | integer | 任务 ID，用于后续查询 |
| status | string | 任务状态：pending / processing / completed / failed / partial / retrying |
| total_count | integer | 总日志数 |
| processed_count | integer | 已处理数 |
| success_count | integer | 成功数 |
| failed_count | integer | 失败数 |

---

### 3.2 获取批量解析任务列表

**功能**：分页获取批量解析任务列表

**接口地址**：`/logs/batch-parse`

**HTTP 方法**：`GET`

#### 3.2.1 请求参数

**查询参数 (Query Parameters)**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| page | integer | 否 | 1 | 页码，从 1 开始 |
| page_size | integer | 否 | 20 | 每页数量，最大 100 |
| status | string | 否 | null | 状态筛选：pending / processing / completed / failed / partial / retrying |

**请求示例**：

```
GET /api/v1/logs/batch-parse?page=1&page_size=20
GET /api/v1/logs/batch-parse?status=completed&page=1&page_size=10
```

#### 3.2.2 响应参数

**成功响应 (HTTP 200)**：

```json
{
  "success": true,
  "code": 200,
  "message": "获取批量解析任务列表成功",
  "data": {
    "items": [
      {
        "id": 1,
        "task_name": "2026-04-29 批量解析任务",
        "status": "completed",
        "total_count": 5,
        "processed_count": 5,
        "success_count": 4,
        "failed_count": 1,
        "created_at": "2026-04-29T12:00:00Z",
        "started_at": "2026-04-29T12:00:05Z",
        "completed_at": "2026-04-29T12:05:30Z",
        "created_by": 1,
        "error_message": null,
        "log_ids": [1, 2, 3, 4, 5]
      }
    ],
    "total": 1,
    "page": 1,
    "page_size": 20
  }
}
```

---

### 3.3 获取批量解析任务详情

**功能**：获取指定任务的详细信息

**接口地址**：`/logs/batch-parse/{task_id}`

**HTTP 方法**：`GET`

#### 3.3.1 请求参数

**路径参数 (Path Parameters)**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| task_id | integer | 是 | 批量任务 ID |

**请求示例**：

```
GET /api/v1/logs/batch-parse/1
```

#### 3.3.2 响应参数

**成功响应 (HTTP 200)**：

```json
{
  "success": true,
  "code": 200,
  "message": "获取批量解析任务详情成功",
  "data": {
    "id": 1,
    "task_name": "2026-04-29 批量解析任务",
    "status": "completed",
    "total_count": 5,
    "processed_count": 5,
    "success_count": 4,
    "failed_count": 1,
    "created_at": "2026-04-29T12:00:00Z",
    "started_at": "2026-04-29T12:00:05Z",
    "completed_at": "2026-04-29T12:05:30Z",
    "created_by": 1,
    "error_message": null,
    "log_ids": [1, 2, 3, 4, 5],
    "items": [
      {
        "id": 1,
        "task_id": 1,
        "log_id": 1,
        "status": "completed",
        "started_at": "2026-04-29T12:00:06Z",
        "completed_at": "2026-04-29T12:01:15Z",
        "error_message": null
      },
      {
        "id": 2,
        "task_id": 1,
        "log_id": 2,
        "status": "failed",
        "started_at": "2026-04-29T12:00:06Z",
        "completed_at": "2026-04-29T12:00:45Z",
        "error_message": "Invalid file format"
      }
    ]
  }
}
```

---

### 3.4 获取批量解析任务进度

**功能**：实时获取任务处理进度

**接口地址**：`/logs/batch-parse/{task_id}/progress`

**HTTP 方法**：`GET`

#### 3.4.1 请求参数

**路径参数 (Path Parameters)**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| task_id | integer | 是 | 批量任务 ID |

**请求示例**：

```
GET /api/v1/logs/batch-parse/1/progress
```

#### 3.4.2 响应参数

**成功响应 (HTTP 200)**：

```json
{
  "success": true,
  "code": 200,
  "message": "获取批量解析任务进度成功",
  "data": {
    "task_id": 1,
    "status": "processing",
    "total_count": 5,
    "processed_count": 3,
    "success_count": 2,
    "failed_count": 1,
    "progress_percent": 60.0,
    "current_log_id": 4,
    "elapsed_seconds": 120.5,
    "estimated_remaining_seconds": 80.3,
    "items": [
      {
        "log_id": 1,
        "status": "completed",
        "error_message": null
      },
      {
        "log_id": 2,
        "status": "completed",
        "error_message": null
      },
      {
        "log_id": 3,
        "status": "failed",
        "error_message": "Invalid file format"
      },
      {
        "log_id": 4,
        "status": "processing",
        "error_message": null
      },
      {
        "log_id": 5,
        "status": "pending",
        "error_message": null
      }
    ]
  }
}
```

#### 3.4.3 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| progress_percent | float | 完成百分比 (0-100) |
| current_log_id | integer | 当前处理的日志 ID |
| elapsed_seconds | float | 已耗时（秒） |
| estimated_remaining_seconds | float | 预计剩余时间（秒） |

---

### 3.5 获取批量解析任务结果

**功能**：获取任务处理完成后的最终结果

**接口地址**：`/logs/batch-parse/{task_id}/result`

**HTTP 方法**：`GET`

#### 3.5.1 请求参数

**路径参数 (Path Parameters)**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| task_id | integer | 是 | 批量任务 ID |

**请求示例**：

```
GET /api/v1/logs/batch-parse/1/result
```

#### 3.5.2 响应参数

**成功响应 (HTTP 200)**：

```json
{
  "success": true,
  "code": 200,
  "message": "获取批量解析任务结果成功",
  "data": {
    "task_id": 1,
    "status": "completed",
    "total_count": 5,
    "success_count": 4,
    "failed_count": 1,
    "success_log_ids": [1, 2, 4, 5],
    "failed_log_ids": [3],
    "error_details": {
      "3": "Invalid file format: file is corrupted or not a valid zevtc file"
    }
  }
}
```

#### 3.5.3 任务状态说明

| 状态 | 说明 |
|------|------|
| pending | 任务等待中，尚未开始 |
| processing | 任务正在处理中 |
| completed | 任务全部完成，全部成功 |
| failed | 任务全部失败 |
| partial | 任务部分成功，部分失败 |
| retrying | 任务重试中（指数退避） |

---

### 3.6 删除批量解析任务

**功能**：删除指定的批量解析任务

**接口地址**：`/logs/batch-parse/{task_id}`

**HTTP 方法**：`DELETE`

#### 3.6.1 请求参数

**路径参数 (Path Parameters)**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| task_id | integer | 是 | 批量任务 ID |

**请求示例**：

```
DELETE /api/v1/logs/batch-parse/1
```

#### 3.6.2 响应参数

**成功响应 (HTTP 200)**：

```json
{
  "success": true,
  "code": 200,
  "message": "删除批量解析任务成功",
  "data": null
}
```

**失败响应 (HTTP 403)**：

```json
{
  "success": false,
  "code": 403,
  "message": "无权删除此任务",
  "data": null
}
```

---

## 4. 数据库表结构

### `batch_parse_tasks`

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT PK | 任务 ID |
| task_name | VARCHAR(255) | 任务名称 |
| status | VARCHAR(20) | 任务状态 |
| total_count | INT | 总日志数 |
| processed_count | INT | 已处理数 |
| success_count | INT | 成功数 |
| failed_count | INT | 失败数 |
| created_by | BIGINT | 创建者用户 ID |
| created_at | DATETIME | 创建时间 |
| started_at | DATETIME | 开始时间 |
| completed_at | DATETIME | 完成时间 |
| error_message | TEXT | 错误信息 |

### `batch_parse_task_items`

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT PK | 子任务 ID |
| task_id | BIGINT FK | 所属任务 ID |
| log_id | BIGINT | 日志 ID |
| status | VARCHAR(20) | 子任务状态 |
| started_at | DATETIME | 开始时间 |
| completed_at | DATETIME | 完成时间 |
| error_message | TEXT | 错误信息 |

---

## 5. 状态流转

### 5.1 任务状态流转

```
pending → processing → completed
                    → failed
                    → partial
                    → retrying → processing
```

### 5.2 日志项状态流转

```
pending → processing → completed
                      → failed
                      → retrying → processing
```

---

## 6. 错误码说明

### 6.1 HTTP 状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 201 | 资源创建成功 |
| 400 | 请求参数错误 |
| 401 | 未授权（token 无效或过期） |
| 403 | 禁止访问（权限不足） |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

### 6.2 业务错误码

| 错误码 | 说明 | 解决方案 |
|--------|------|---------|
| 11001 | 无效的令牌 | 重新登录获取 token |
| 11002 | 令牌过期 | 重新登录获取 token |
| 11003 | 权限不足 | 联系管理员授权 |
| 12001 | 数据验证错误 | 检查请求参数格式 |
| 12002 | 数据不存在 | 检查传入的 ID 是否正确 |
| 12003 | 数据重复 | 使用新的数据或不传此字段 |
| 12004 | 数据冲突 | 检查数据是否已被占用 |
| 13001 | 日志上传失败 | 重新上传或检查文件格式 |
| 13002 | 日志解析失败 | 检查日志文件是否损坏 |
| 13003 | 日志不存在 | 检查日志 ID 是否正确 |
| 40001 | 批量任务创建失败 | 检查 log_ids 是否有效 |
| 40002 | 批量任务不存在 | 检查 task_id 是否正确 |
| 40003 | 批量任务访问权限不足 | 检查是否有权限访问该任务 |

---

## 7. 对接步骤

### 7.1 前置准备

#### 7.1.1 登录认证

在进行批量解析操作前，用户必须先登录获取 token：

```javascript
// 登录请求
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "123456"
}

// 响应
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer",
    "expires_in": 86400
  }
}
```

#### 7.1.2 Token 存储

前端需要妥善存储 token，并在后续请求中携带：

```javascript
// 存储 token
localStorage.setItem('access_token', response.data.access_token);

// 后续请求携带 token
const token = localStorage.getItem('access_token');
fetch('/api/v1/logs/batch-parse', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});
```

### 7.2 完整对接流程

#### 步骤 1：获取日志列表

```javascript
// 获取日志列表
async function getLogs() {
  const response = await fetch('/api/v1/logs?page=1&page_size=100', {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  const result = await response.json();
  return result.data.items;
}

// 显示日志列表供用户选择
const logs = await getLogs();
console.log(logs);
// [{id: 1, filename: "log1.zevtc", ...}, ...]
```

#### 步骤 2：用户选择日志

```javascript
// 用户界面：复选框选择日志
const selectedLogIds = [1, 2, 3, 5]; // 用户选择的日志 ID
console.log(`已选择 ${selectedLogIds.length} 个日志`);
```

#### 步骤 3：创建批量解析任务

```javascript
// 创建批量解析任务
async function createBatchParseTask(logIds, taskName, overwrite = true) {
  const response = await fetch('/api/v1/logs/batch-parse', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      task_name: taskName,
      log_ids: logIds,
      overwrite: overwrite
    })
  });
  return await response.json();
}

// 创建任务
const createResult = await createBatchParseTask(
  selectedLogIds,
  '2026-04-29 批量解析',
  true
);

if (createResult.success) {
  const taskId = createResult.data.id;
  console.log(`任务创建成功，任务 ID: ${taskId}`);
  startPollingProgress(taskId); // 开始轮询进度
} else {
  console.error('任务创建失败:', createResult.message);
}
```

#### 步骤 4：轮询进度

```javascript
// 轮询进度
async function pollProgress(taskId, interval = 2000) {
  return new Promise((resolve, reject) => {
    const timer = setInterval(async () => {
      try {
        const response = await fetch(`/api/v1/logs/batch-parse/${taskId}/progress`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        const result = await response.json();

        if (result.success) {
          const progress = result.data;

          // 更新 UI
          updateProgressUI({
            status: progress.status,
            percent: progress.progress_percent,
            successCount: progress.success_count,
            failedCount: progress.failed_count,
            currentLogId: progress.current_log_id,
            elapsed: progress.elapsed_seconds,
            remaining: progress.estimated_remaining_seconds
          });

          // 检查是否完成
          if (['completed', 'failed', 'partial'].includes(progress.status)) {
            clearInterval(timer);
            resolve(progress);
          }
        }
      } catch (error) {
        console.error('获取进度失败:', error);
      }
    }, interval);

    // 超时处理（5 分钟）
    setTimeout(() => {
      clearInterval(timer);
      reject(new Error('进度查询超时'));
    }, 300000);
  });
}

// 开始轮询
async function startPollingProgress(taskId) {
  try {
    const finalResult = await pollProgress(taskId);
    console.log('任务完成:', finalResult.status);
    showResult(finalResult);
  } catch (error) {
    console.error('轮询异常:', error);
    showError(error.message);
  }
}
```

#### 步骤 5：获取最终结果

```javascript
// 获取最终结果
async function getTaskResult(taskId) {
  const response = await fetch(`/api/v1/logs/batch-parse/${taskId}/result`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  const result = await response.json();
  return result.data;
}

// 显示结果
async function showResult(result) {
  console.log('=== 批量解析结果 ===');
  console.log(`状态: ${result.status}`);
  console.log(`总数: ${result.total_count}`);
  console.log(`成功: ${result.success_count}`);
  console.log(`失败: ${result.failed_count}`);

  if (result.failed_log_ids.length > 0) {
    console.log('失败详情:', result.error_details);
  }
}
```

---

## 8. 注意事项

### 8.1 数据校验

- **log_ids 数组**：
  - 不能为空
  - 最多 100 个元素
  - 每个元素必须是有效的整数日志 ID

- **task_name**：
  - 最大长度 255 字符
  - 建议填写有意义的名称便于识别

- **overwrite 参数**：
  - `true`：重新解析时覆盖旧数据
  - `false`：跳过已解析的日志（不推荐，可能导致数据不一致）

### 8.2 状态异常处理

```javascript
// 异常状态处理示例
function handleTaskStatus(status) {
  switch (status) {
    case 'pending':
      return '等待处理';
    case 'processing':
      return '处理中';
    case 'completed':
      return '全部成功';
    case 'failed':
      return '全部失败';
    case 'partial':
      return '部分成功';
    case 'retrying':
      return '重试中';
    default:
      return '未知状态';
  }
}
```

---

## 附录：文件清单

| 文件路径 | 说明 |
|---------|------|
| `app/routers/logs.py` | 批量解析 API 路由 |
| `app/services/batch_parse_service.py` | 批量解析业务服务 |
