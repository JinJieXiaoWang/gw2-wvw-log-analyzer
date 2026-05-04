# GW2 WVW 日志解析管理系统 - 认证接口文档

> **版本**: v3.0  
> **更新日期**: 2026-05-05  
> **责任人**: 帅姐姐  
> **整合来源**: AUTH_API_DOC.md, 登录接口优化方案.md

## 版本变更记录

| 版本 | 日期 | 变更内容 | 责任人 |
|------|------|----------|--------|
| v3.0 | 2026-05-05 | 补充 change-password 端点，与实际代码对齐 | 系统 |
| v2.0 | 2026-05-01 | 整合登录接口文档与优化方案，精简为统一认证接口规范 | 帅姐姐 |
| v1.0 | 2026-04-28 | 初始版本 | 技术团队 |

---

## 一、接口概述

本文档描述 GW2 WVW 日志系统的认证相关 API 接口。根据优化方案，认证接口已精简为仅保留核心的操作员登录、登出、状态查询和用户信息接口。

### 业务场景

| 角色 | 需求描述 | 访问权限 |
|------|----------|----------|
| **普通公会成员** | 查看日志、出勤统计、技能分析等内容 | 无需登录，公开访问 |
| **系统操作员** | 上传日志、解析日志、系统维护 | 需要认证 |

### 精简后的接口列表

| 接口 | 方法 | 功能说明 | 认证要求 |
|------|------|----------|----------|
| `/api/v1/auth/login` | POST | 操作员登录 | 无需认证 |
| `/api/v1/auth/logout` | POST | 操作员登出 | 需要认证 |
| `/api/v1/auth/status` | GET | 获取登录状态 | 可选认证 |
| `/api/v1/auth/profile` | GET | 获取用户信息 | 需要认证 |
| `/api/v1/auth/change-password` | POST | 修改当前用户密码 | 需要认证 |

---

## 二、认证方式

系统采用 **JWT (JSON Web Token)** 进行认证，登录成功后返回访问令牌，后续请求需在 `Authorization` 请求头中携带该令牌。

**令牌格式**：
```
Authorization: Bearer <access_token>
```

**令牌有效期**：2 小时

---

## 三、统一响应格式

### 成功响应
```json
{
  "success": true,
  "message": "操作成功",
  "data": {},
  "error_code": null,
  "timestamp": "2026-04-28T12:00:00Z"
}
```

### 失败响应
```json
{
  "success": false,
  "message": "错误描述",
  "data": null,
  "error_code": "ERROR_CODE",
  "timestamp": "2026-04-28T12:00:00Z"
}
```

---

## 四、接口详情

### 4.1 操作员登录

**接口地址**：`POST /api/v1/auth/login`

**功能描述**：操作员登录，成功后返回 JWT 访问令牌

**请求头**：
```
Content-Type: application/json
```

**请求体**：
```json
{
  "username": "operator",
  "password": "password"
}
```

**请求参数**：

| 参数名 | 类型 | 必填 | 长度限制 | 说明 |
|--------|------|------|----------|------|
| username | string | 是 | 3-50 字符 | 操作员用户名 |
| password | string | 是 | 6-128 字符 | 操作员密码 |

**成功响应**：
```json
{
  "success": true,
  "message": "登录成功",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 7200,
    "user": {
      "id": 1,
      "username": "operator",
      "role": "operator",
      "is_active": true
    },
    "permissions": ["read", "write", "upload", "delete"]
  },
  "error_code": null,
  "timestamp": "2026-04-28T12:00:00Z"
}
```

**失败响应**：
```json
{
  "success": false,
  "message": "用户名或密码错误",
  "data": null,
  "error_code": "INVALID_CREDENTIALS",
  "timestamp": "2026-04-28T12:00:00Z"
}
```

**登录限流机制**：
- 同一账户+IP 在 5 分钟内最多尝试 5 次登录
- 超过次数后账户锁定 15 分钟

---

### 4.2 操作员登出

**接口地址**：`POST /api/v1/auth/logout`

**功能描述**：操作员登出

**认证要求**：需要有效的 JWT 令牌

**请求头**：
```
Content-Type: application/json
Authorization: Bearer <access_token>
```

**请求参数**：无

**成功响应**：
```json
{
  "success": true,
  "message": "登出成功",
  "data": null,
  "error_code": null,
  "timestamp": "2026-04-28T12:00:00Z"
}
```

> 前端应在调用此接口后清除本地存储的 token。

---

### 4.3 获取登录状态

**接口地址**：`GET /api/v1/auth/status`

**功能描述**：获取当前登录状态，无需认证也可访问

**请求头**：
```
Content-Type: application/json
```

**可选请求头（已登录时）**：
```
Authorization: Bearer <access_token>
```

**成功响应（未登录）**：
```json
{
  "success": true,
  "message": "获取状态成功",
  "data": {
    "is_logged_in": false,
    "user": null,
    "permissions": ["read"]
  }
}
```

**成功响应（已登录）**：
```json
{
  "success": true,
  "message": "获取状态成功",
  "data": {
    "is_logged_in": true,
    "user": {
      "id": 1,
      "username": "operator",
      "role": "operator"
    },
    "permissions": ["read", "write", "upload", "delete"]
  }
}
```

---

### 4.4 获取用户信息

**接口地址**：`GET /api/v1/auth/profile`

**功能描述**：获取当前登录操作员的详细信息

**认证要求**：需要有效的 JWT 令牌

**成功响应**：
```json
{
  "success": true,
  "message": "获取用户信息成功",
  "data": {
    "user": {
      "id": 1,
      "username": "operator",
      "role": "operator",
      "is_active": true
    },
    "permissions": ["read", "write", "upload", "delete"]
  }
}
```

---

## 五、权限控制策略

### 5.1 权限分级

| 权限级别 | 角色 | 访问范围 | API 路径示例 |
|----------|------|----------|--------------|
| **公开访问** | 普通成员 | 查看日志列表、统计数据、战斗详情 | `/api/v1/logs`, `/api/v1/members`, `/api/v1/fights` |
| **操作员** | 系统操作员 | 上传日志、解析日志、删除日志 | `/api/v1/logs` (POST), `/api/v1/logs/{id}/parse` |

### 5.2 权限列表

| 权限 | 说明 |
|------|------|
| read | 读取数据权限 |
| write | 写入数据权限 |
| upload | 上传文件权限 |
| delete | 删除数据权限 |

### 5.3 接口权限矩阵

| 接口路径 | 公开访问 | 操作员 |
|----------|:--------:|:------:|
| `GET /api/v1/logs` | ✅ | ✅ |
| `POST /api/v1/logs` | ❌ | ✅ |
| `GET /api/v1/logs/{id}` | ✅ | ✅ |
| `DELETE /api/v1/logs/{id}` | ❌ | ✅ |
| `POST /api/v1/logs/{id}/parse` | ❌ | ✅ |
| `GET /api/v1/members` | ✅ | ✅ |
| `GET /api/v1/fights` | ✅ | ✅ |
| `GET /api/v1/skills` | ✅ | ✅ |

---

## 六、HTTP 状态码

| 状态码 | 含义 | 说明 |
|--------|------|------|
| 200 | 请求成功 | 操作成功完成 |
| 400 | 请求参数错误 | 参数校验失败或业务逻辑错误 |
| 401 | 未授权 | 未提供令牌或令牌无效/过期 |
| 500 | 服务器内部错误 | 服务端处理异常 |

---

## 七、安全考量

### 7.1 登录限流

- **限制策略**：同一 IP/账户 5 分钟内最多尝试 5 次
- **触发锁定**：超过次数后锁定 15 分钟
- **解锁方式**：自动解锁

### 7.2 Token 安全

- **Access Token 有效期**：2 小时
- **Token 存储**：建议前端使用 HttpOnly Cookie 存储

### 7.3 安全风险评估

| 风险项 | 风险等级 | 建议措施 |
|--------|----------|----------|
| Token 泄露 | 中 | 使用 HttpOnly Cookie 存储 |
| 暴力破解 | 高 | 已实现登录失败次数限制 |
| 会话劫持 | 中 | 短 Token + 刷新机制 |
| 权限绕过 | 高 | 后端严格权限校验 |

---

## 八、前端适配建议

```typescript
// 权限判断示例
const showUploadButton = permissions.includes('upload')
const showDeleteButton = permissions.includes('delete')

// 根据登录状态控制功能显示
const isLoggedIn = authStatus.is_logged_in
const userRole = authStatus.user?.role
```

### 4.5 修改密码

**接口**: `POST /api/v1/auth/change-password`

**认证要求**: 需要 Bearer Token

**请求体**:
```json
{
  "old_password": "string",
  "new_password": "string"
}
```

**成功响应**:
```json
{
  "success": true,
  "code": 200,
  "message": "密码修改成功",
  "data": null
}
```

**错误响应**:
- `400`: 请求参数错误
- `401`: 未授权或旧密码不正确
- `500`: 服务器内部错误

**说明**:
- 修改密码后会更新 `sys_user.token_version`，使旧 JWT 失效
- 前端修改成功后需清除当前 Token 并重新登录

---

*本文档整合了登录接口对接文档与登录接口优化方案。原始详细内容请参阅 `docs/archive/` 目录。*
