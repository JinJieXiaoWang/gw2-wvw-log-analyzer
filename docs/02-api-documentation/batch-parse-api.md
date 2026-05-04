# GW2日志系统 - 批量解析功能前端对接技术文档

> **版本**: v2.0  
> **更新日期**: 2026-05-05  
> **责任人**: 帅姐姐  
> **整合来源**: 批量解析功能前端对接文档.md（原文件归档至 docs/archive/）

## 版本变更记录

| 版本 | 日期 | 变更内容 | 责任人 |
|------|------|----------|--------|
| v2.0 | 2026-05-05 | 依据代码更新端点列表和机制说明（6 个端点、数据库轮询+限流+指数退避） | 系统 |
| v1.1 | 2026-05-01 | 文档整理归档，内容保持不变 | 帅姐姐 |
| v1.0 | 2026-04-29 | 初始版本 | 技术团队 |

---

## 文档信息

| 项目 | 内容 |
|------|------|
| 文档类型 | 前端对接技术文档 |
| 适用对象 | 前端开发团队 |

---

## 1. 功能概述

### 1.1 功能描述

批量解析功能允许用户一次性选择多个日志文件（最多100个），提交到后台进行异步解析处理。该功能适用于：

- **批量导入场景**：用户上传多个日志文件后，需要统一解析
- **重新解析场景**：解析器升级后，需要对历史日志重新解析
- **大规模数据处理**：同时处理大量日志，提升处理效率

### 1.2 核心特性

- ✅ **异步执行**：后台任务队列异步处理，不阻塞前端
- ✅ **并发控制**：最多3个并发解析任务，确保系统稳定性
- ✅ **实时进度**：支持查询解析进度，实时反馈处理状态
- ✅ **状态跟踪**：每个日志独立状态跟踪，精确掌控处理结果
- ✅ **错误处理**：单个日志失败不影响其他日志，完整错误信息反馈
- ✅ **数据覆盖**：支持覆盖旧数据或跳过已解析日志

### 1.3 数据流程

```
用户选择日志 → 创建批量任务 → 任务入队 → 后台处理
                                      ↓
前端轮询进度 ← 实时状态更新 ← 多线程并发解析
                                      ↓
                                解析结果存储
```

---

## 2. 接口说明

### 2.1 基础信息

| 项目 | 内容 |
|------|------|
| 基础URL | `http://127.0.0.1:8000/api/v1` |
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

**HTTP方法**：`POST`

#### 3.1.1 请求参数

**请求体 (Request Body)**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| task_name | string | 否 | 任务名称，用于标识任务 |
| log_ids | array[integer] | 是 | 需要解析的日志ID列表，最多100个 |
| overwrite | boolean | 否 | 是否覆盖已有数据，默认true |

**请求示例**：

```json
{
  "task_name": "2026-04-29批量解析任务",
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
    "task_name": "2026-04-29批量解析任务",
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
  "message": "日志ID列表不能为空",
  "data": null
}
```

#### 3.1.3 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| id | integer | 任务ID，用于后续查询 |
| status | string | 任务状态：pending/ processing/ completed/ failed/ partial |
| total_count | integer | 总日志数 |
| processed_count | integer | 已处理数 |
| success_count | integer | 成功数 |
| failed_count | integer | 失败数 |

---

### 3.2 获取批量解析任务列表

**功能**：分页获取批量解析任务列表

**接口地址**：`/logs/batch-parse`

**HTTP方法**：`GET`

#### 3.2.1 请求参数

**查询参数 (Query Parameters)**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| page | integer | 否 | 1 | 页码，从1开始 |
| page_size | integer | 否 | 20 | 每页数量，最大100 |
| status | string | 否 | null | 状态筛选：pending/ processing/ completed/ failed/ partial |

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
        "task_name": "2026-04-29批量解析任务",
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

**HTTP方法**：`GET`

#### 3.3.1 请求参数

**路径参数 (Path Parameters)**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| task_id | integer | 是 | 批量任务ID |

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
    "task_name": "2026-04-29批量解析任务",
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

**HTTP方法**：`GET`

#### 3.4.1 请求参数

**路径参数 (Path Parameters)**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| task_id | integer | 是 | 批量任务ID |

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
| current_log_id | integer | 当前处理的日志ID |
| elapsed_seconds | float | 已耗时（秒） |
| estimated_remaining_seconds | float | 预计剩余时间（秒） |

---

### 3.5 获取批量解析任务结果

**功能**：获取任务处理完成后的最终结果

**接口地址**：`/logs/batch-parse/{task_id}/result`

**HTTP方法**：`GET`

#### 3.5.1 请求参数

**路径参数 (Path Parameters)**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| task_id | integer | 是 | 批量任务ID |

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

---

### 3.6 删除批量解析任务

**功能**：删除指定的批量解析任务

**接口地址**：`/logs/batch-parse/{task_id}`

**HTTP方法**：`DELETE`

#### 3.6.1 请求参数

**路径参数 (Path Parameters)**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| task_id | integer | 是 | 批量任务ID |

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

## 4. 错误码说明

### 4.1 HTTP状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 201 | 资源创建成功 |
| 400 | 请求参数错误 |
| 401 | 未授权（token无效或过期） |
| 403 | 禁止访问（权限不足） |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

### 4.2 业务错误码

| 错误码 | 说明 | 解决方案 |
|--------|------|---------|
| 11001 | 无效的令牌 | 重新登录获取token |
| 11002 | 令牌过期 | 重新登录获取token |
| 11003 | 权限不足 | 联系管理员授权 |
| 12001 | 数据验证错误 | 检查请求参数格式 |
| 12002 | 数据不存在 | 检查传入的ID是否正确 |
| 12003 | 数据重复 | 使用新的数据或不传此字段 |
| 12004 | 数据冲突 | 检查数据是否已被占用 |
| 13001 | 日志上传失败 | 重新上传或检查文件格式 |
| 13002 | 日志解析失败 | 检查日志文件是否损坏 |
| 13003 | 日志不存在 | 检查日志ID是否正确 |
| 40001 | 批量任务创建失败 | 检查log_ids是否有效 |
| 40002 | 批量任务不存在 | 检查task_id是否正确 |
| 40003 | 批量任务访问权限不足 | 检查是否有权限访问该任务 |

### 4.3 错误响应格式

```json
{
  "success": false,
  "code": 400,
  "message": "日志ID列表不能为空",
  "data": null
}
```

---

## 5. 对接步骤

### 5.1 前置准备

#### 5.1.1 登录认证

在进行批量解析操作前，用户必须先登录获取token：

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

#### 5.1.2 Token存储

前端需要妥善存储token，并在后续请求中携带：

```javascript
// 存储token
localStorage.setItem('access_token', response.data.access_token);

// 后续请求携带token
const token = localStorage.getItem('access_token');
fetch('/api/v1/logs/batch-parse', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});
```

### 5.2 完整对接流程

#### 步骤1：获取日志列表

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

#### 步骤2：用户选择日志

```javascript
// 用户界面：复选框选择日志
const selectedLogIds = [1, 2, 3, 5]; // 用户选择的日志ID
console.log(`已选择 ${selectedLogIds.length} 个日志`);
```

#### 步骤3：创建批量解析任务

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
  '2026-04-29批量解析',
  true
);

if (createResult.success) {
  const taskId = createResult.data.id;
  console.log(`任务创建成功，任务ID: ${taskId}`);
  startPollingProgress(taskId); // 开始轮询进度
} else {
  console.error('任务创建失败:', createResult.message);
}
```

#### 步骤4：轮询进度

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

          // 更新UI
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

    // 超时处理（5分钟）
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

#### 步骤5：获取最终结果

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

### 5.3 Vue3示例代码

```vue
<template>
  <div class="batch-parse">
    <h2>批量解析日志</h2>

    <!-- 日志选择列表 -->
    <div class="log-list">
      <div v-for="log in logs" :key="log.id" class="log-item">
        <input
          type="checkbox"
          :value="log.id"
          v-model="selectedLogIds"
        />
        <span>{{ log.filename }}</span>
        <span class="status" :class="log.parse_status">
          {{ log.parse_status }}
        </span>
      </div>
    </div>

    <!-- 操作栏 -->
    <div class="actions">
      <button @click="selectAll">全选</button>
      <button @click="clearSelection">清空</button>
      <button @click="startBatchParse" :disabled="selectedLogIds.length === 0">
        开始批量解析 ({{ selectedLogIds.length }})
      </button>
    </div>

    <!-- 进度显示 -->
    <div v-if="currentTask" class="progress-section">
      <h3>任务进度</h3>
      <div class="progress-bar">
        <div
          class="progress-fill"
          :style="{ width: `${progress.percent}%` }"
        ></div>
      </div>
      <div class="progress-info">
        <span>状态: {{ progress.status }}</span>
        <span>{{ progress.percent.toFixed(1) }}%</span>
        <span>成功: {{ progress.successCount }}</span>
        <span>失败: {{ progress.failedCount }}</span>
      </div>
      <div v-if="progress.remaining" class="time-estimate">
        预计剩余时间: {{ formatTime(progress.remaining) }}
      </div>
    </div>

    <!-- 结果显示 -->
    <div v-if="showResult" class="result-section">
      <h3>解析结果</h3>
      <p>任务状态: {{ taskResult.status }}</p>
      <p>成功日志: {{ taskResult.success_log_ids.join(', ') }}</p>
      <div v-if="taskResult.failed_log_ids.length > 0" class="errors">
        <h4>失败详情:</h4>
        <ul>
          <li v-for="logId in taskResult.failed_log_ids" :key="logId">
            日志 {{ logId }}: {{ taskResult.error_details[logId] }}
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';

const logs = ref([]);
const selectedLogIds = ref([]);
const currentTask = ref(null);
const progress = ref({
  status: '',
  percent: 0,
  successCount: 0,
  failedCount: 0,
  remaining: null
});
const showResult = ref(false);
const taskResult = ref(null);
let pollTimer = null;

onMounted(async () => {
  await fetchLogs();
});

async function fetchLogs() {
  const response = await fetch('/api/v1/logs?page=1&page_size=100', {
    headers: { 'Authorization': `Bearer ${getToken()}` }
  });
  const result = await response.json();
  logs.value = result.data.items;
}

function selectAll() {
  selectedLogIds.value = logs.value.map(log => log.id);
}

function clearSelection() {
  selectedLogIds.value = [];
}

async function startBatchParse() {
  if (selectedLogIds.value.length === 0) return;

  // 创建任务
  const createResponse = await fetch('/api/v1/logs/batch-parse', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${getToken()}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      task_name: `批量解析_${Date.now()}`,
      log_ids: selectedLogIds.value,
      overwrite: true
    })
  });

  const createResult = await createResponse.json();

  if (createResult.success) {
    currentTask.value = createResult.data;
    startPolling(createResult.data.id);
  } else {
    alert('创建任务失败: ' + createResult.message);
  }
}

async function pollProgress(taskId) {
  const response = await fetch(`/api/v1/logs/batch-parse/${taskId}/progress`, {
    headers: { 'Authorization': `Bearer ${getToken()}` }
  });
  return await response.json();
}

function startPolling(taskId) {
  pollTimer = setInterval(async () => {
    const result = await pollProgress(taskId);

    if (result.success) {
      const data = result.data;
      progress.value = {
        status: data.status,
        percent: data.progress_percent,
        successCount: data.success_count,
        failedCount: data.failed_count,
        remaining: data.estimated_remaining_seconds
      };

      if (['completed', 'failed', 'partial'].includes(data.status)) {
        clearInterval(pollTimer);
        await fetchResult(taskId);
      }
    }
  }, 2000);
}

async function fetchResult(taskId) {
  const response = await fetch(`/api/v1/logs/batch-parse/${taskId}/result`, {
    headers: { 'Authorization': `Bearer ${getToken()}` }
  });
  const result = await response.json();

  if (result.success) {
    taskResult.value = result.data;
    showResult.value = true;
  }
}

function formatTime(seconds) {
  if (!seconds) return '-';
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}分${secs}秒`;
}

function getToken() {
  return localStorage.getItem('access_token');
}
</script>

<style scoped>
.batch-parse {
  padding: 20px;
}

.log-list {
  max-height: 400px;
  overflow-y: auto;
  border: 1px solid #ddd;
  margin: 10px 0;
}

.log-item {
  padding: 10px;
  display: flex;
  align-items: center;
  gap: 10px;
  border-bottom: 1px solid #eee;
}

.progress-bar {
  height: 20px;
  background: #f0f0f0;
  border-radius: 10px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #4CAF50, #8BC34A);
  transition: width 0.3s;
}

.result-section {
  margin-top: 20px;
  padding: 15px;
  background: #f9f9f9;
  border-radius: 5px;
}
</style>
```

---

## 6. 注意事项

### 6.1 数据校验

- **log_ids数组**：
  - 不能为空
  - 最多100个元素
  - 每个元素必须是有效的整数日志ID

- **task_name**：
  - 最大长度255字符
  - 建议填写有意义的名称便于识别

- **overwrite参数**：
  - `true`：重新解析时覆盖旧数据
  - `false`：跳过已解析的日志（不推荐，可能导致数据不一致）

### 6.2 状态处理

#### 6.2.1 任务状态流转

```
pending → processing → completed
                    → failed
                    → partial
```

#### 6.2.2 日志项状态流转

```
pending → processing → completed
                      → failed
```

#### 6.2.3 状态异常处理

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
    default:
      return '未知状态';
  }
}
```

### 6.3 并发控制

- 后端同时最多处理3个解析任务
- 如果一次提交超过3个日志，会排队处理
- 建议单个批量任务控制在50个以内以获得最佳性能

### 6.4 超时处理

- 轮询间隔建议2-3秒
- 最大轮询时间建议5-10分钟
- 超时后提示用户任务可能仍在执行，可稍后查询结果

### 6.5 网络异常

- 网络断开时停止轮询
- 恢复连接后重新查询进度
- 对于已完成的日志，即使网络中断也不会丢失数据

---

## 7. 性能优化建议

### 7.1 前端优化

#### 7.1.1 请求优化

```javascript
// ❌ 不推荐：频繁请求
setInterval(() => {
  fetchProgress();
}, 500); // 500ms过于频繁

// ✅ 推荐：合理间隔
setInterval(() => {
  fetchProgress();
}, 2000); // 2秒间隔足够
```

#### 7.1.2 防抖处理

```javascript
// 搜索等频繁触发的操作使用防抖
function debounce(fn, delay) {
  let timer = null;
  return function(...args) {
    clearTimeout(timer);
    timer = setTimeout(() => fn.apply(this, args), delay);
  };
}

const debouncedSearch = debounce(searchLogs, 300);
```

#### 7.1.3 缓存策略

```javascript
// 缓存日志列表，减少请求
const logCache = new Map();
const CACHE_TTL = 60000; // 1分钟缓存

function getCachedLogs() {
  const cached = logCache.get('logs');
  if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
    return Promise.resolve(cached.data);
  }

  return fetchLogs().then(data => {
    logCache.set('logs', {
      data,
      timestamp: Date.now()
    });
    return data;
  });
}
```

### 7.2 用户体验优化

#### 7.2.1 进度展示

```javascript
// 显示预估剩余时间
function formatRemainingTime(seconds) {
  if (!seconds) return '计算中...';
  if (seconds < 60) return `${Math.ceil(seconds)}秒`;
  if (seconds < 3600) {
    const mins = Math.floor(seconds / 60);
    const secs = Math.ceil(seconds % 60);
    return `${mins}分${secs}秒`;
  }
  const hours = Math.floor(seconds / 3600);
  const mins = Math.floor((seconds % 3600) / 60);
  return `${hours}小时${mins}分`;
}
```

#### 7.2.2 分批处理大列表

```javascript
// 超过100个日志时分批创建任务
async function batchParseLargeList(logIds) {
  const BATCH_SIZE = 50;
  const results = [];

  for (let i = 0; i < logIds.length; i += BATCH_SIZE) {
    const batch = logIds.slice(i, i + BATCH_SIZE);
    const task = await createBatchParseTask(batch);
    results.push(task);

    // 每批之间暂停，避免请求过于密集
    if (i + BATCH_SIZE < logIds.length) {
      await sleep(1000);
    }
  }

  return results;
}
```

### 7.3 错误处理优化

#### 7.3.1 重试机制

```javascript
async function fetchWithRetry(url, options, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      const response = await fetch(url, options);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      await sleep(1000 * Math.pow(2, i)); // 指数退避
    }
  }
}
```

#### 7.3.2 优雅降级

```javascript
// 进度获取失败时显示最后已知状态
let lastKnownProgress = null;

async function safePollProgress(taskId) {
  try {
    const result = await fetchProgress(taskId);
    lastKnownProgress = result;
    return result;
  } catch (error) {
    console.warn('获取进度失败，使用缓存:', error);
    if (lastKnownProgress) {
      return {
        ...lastKnownProgress,
        status: 'unknown',
        note: '数据可能不是最新的'
      };
    }
    throw error;
  }
}
```

---

## 8. 常见问题解答

### Q1: 批量解析任务创建失败怎么办？

**A**: 常见原因和解决方案：

1. **日志ID无效**
   ```json
   {
     "success": false,
     "message": "没有有效的日志ID"
   }
   ```
   解决：确保所有log_ids都对应真实存在的日志

2. **超过数量限制**
   ```json
   {
     "success": false,
     "message": "最多支持同时解析100个日志文件"
   }
   ```
   解决：分批创建任务，每批不超过100个

3. **未授权**
   ```json
   {
     "success": false,
     "code": 401,
     "message": "无效的令牌"
   }
   ```
   解决：重新登录获取新token

---

### Q2: 轮询进度时有时返回pending状态很久？

**A**: 这是正常现象。任务创建后需要短暂时间进入队列并开始执行。如果pending状态持续超过10秒，可能是后台worker未启动，建议联系运维检查服务器状态。

---

### Q3: 如何判断任务是否真正完成？

**A**: 检查任务状态：

- ✅ **completed**：全部成功，可以获取结果
- ⚠️ **partial**：部分成功，有失败的日志，需要查看error_details
- ❌ **failed**：全部失败，需要检查错误信息
- 🔄 **processing**：仍在处理中，继续轮询

---

### Q4: 任务完成后发现部分日志失败怎么办？

**A**: 可以单独重新解析失败的日志：

```javascript
// 重新解析失败的日志
const failedLogIds = taskResult.failed_log_ids;

for (const logId of failedLogIds) {
  await fetch(`/api/v1/logs/${logId}/parse?overwrite=true`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` }
  });
}
```

---

### Q5: 批量解析和单个解析有什么区别？

**A**: 对比说明：

| 特性 | 单个解析 | 批量解析 |
|------|---------|---------|
| 接口 | `POST /logs/{log_id}/parse` | `POST /logs/batch-parse` |
| 日志数量 | 1个 | 最多100个 |
| 进度跟踪 | 通过progress接口 | 通过progress接口 |
| 并发处理 | 无 | 多线程并发 |
| 适用场景 | 临时解析单个 | 批量导入、重新解析 |

---

### Q6: overwrite=true和false有什么区别？

**A**: 

- **overwrite=true（默认）**：
  - 删除旧的解析数据
  - 重新解析并保存新数据
  - 适用于解析器升级、需要更新结果的场景

- **overwrite=false**：
  - 跳过已解析的日志
  - 只解析未解析过的日志
  - 适用于增量导入、不想覆盖已有结果的场景

⚠️ **注意**：overwrite=false可能导致数据不一致，谨慎使用

---

### Q7: 任务状态一直显示processing怎么办？

**A**: 按以下步骤排查：

1. **检查服务器日志**：查看是否有解析异常
2. **检查文件是否存在**：确保日志文件未被删除
3. **检查数据库连接**：后台任务需要数据库连接
4. **重启服务**：如果是worker线程死锁，重启可以解决

---

### Q8: 如何实现实时推送而不是轮询？

**A**: 当前版本不支持WebSocket实时推送，需要使用轮询方式。如需实时推送，可以：

1. **前端轮询（当前方案）**：2-3秒间隔轮询
2. **Server-Sent Events (SSE)**：需要后端支持，可作为后续优化点
3. **WebSocket**：需要较大改动，可作为长期优化方向

---

### Q9: 批量任务支持取消吗？

**A**: 当前版本不支持直接取消任务。如果需要停止任务，可以：

1. **等待自然完成**：任务会处理完队列中的所有项目
2. **刷新页面**：前端停止轮询，任务仍在后台执行
3. **重启服务器**：可以终止所有后台任务（不推荐）

---

### Q10: 日志文件损坏导致解析失败怎么办？

**A**: 解析失败会自动记录错误信息：

```json
{
  "error_details": {
    "123": "Invalid file format: file is corrupted or not a valid zevtc file"
  }
}
```

**解决方案**：

1. 检查源文件是否损坏
2. 确认文件是有效的EVTC/JSON格式
3. 尝试重新上传文件
4. 如果是解析器bug，联系后端团队

---

## 9. 接口快速参考

### 接口清单

| 序号 | 接口名称 | HTTP方法 | 地址 | 认证 |
|------|---------|---------|------|------|
| 1 | 创建批量任务 | POST | `/logs/batch-parse` | ✅ |
| 2 | 获取任务列表 | GET | `/logs/batch-parse` | ✅ |
| 3 | 获取任务详情 | GET | `/logs/batch-parse/{task_id}` | ✅ |
| 4 | 获取任务进度 | GET | `/logs/batch-parse/{task_id}/progress` | ✅ |
| 5 | 获取任务结果 | GET | `/logs/batch-parse/{task_id}/result` | ✅ |
| 6 | 删除任务 | DELETE | `/logs/batch-parse/{task_id}` | ✅ |

### 快速测试

使用cURL快速测试接口：

```bash
# 1. 登录获取token
curl -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"123456"}'

# 2. 创建批量任务
curl -X POST http://127.0.0.1:8000/api/v1/logs/batch-parse \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {token}" \
  -d '{"log_ids":[1,2,3],"task_name":"测试任务"}'

# 3. 查询进度
curl http://127.0.0.1:8000/api/v1/logs/batch-parse/1/progress \
  -H "Authorization: Bearer {token}"

# 4. 获取结果
curl http://127.0.0.1:8000/api/v1/logs/batch-parse/1/result \
  -H "Authorization: Bearer {token}"
```

---

## 10. 更新日志

| 版本 | 日期 | 更新内容 |
|------|------|---------|
| v1.0 | 2026-04-29 | 初始版本，包含完整接口文档 |

---

**文档结束**
