# 前后端对接方式约定

> **版本**: v2.0.0  
> **更新日期**: 2026-05-05  
> **整合责任人**: 系统文档维护团队  
> **变更摘要**: 与实际代码对齐：补充角色体系、JWT 有效期、前端 API 架构、已知问题与注意事项

---

## 历史版本

| 版本 | 日期 | 变更内容 | 责任人 |
|------|------|----------|--------|
| v2.0.0 | 2026-05-05 | 与实际代码对齐：更新角色、JWT、API 架构、已知问题 | 系统 |
| v1.1.0 | 2026-05-01 | 归档至规范目录，添加版本头 | 系统 |
| v1.0.0 | 2026-04-27 | 初始版本 | 帅妹妹丶.8297 |

---

# 前后端对接方式约定

## 1. API 请求方式使用场景

| 请求方式 | 使用场景 | 示例 |
|---------|---------|------|
| GET | 获取资源，无副作用 | `/api/v1/logs` - 获取日志列表 |
| POST | 创建资源或执行操作 | `/api/v1/logs` - 上传日志文件 |
| PUT | 更新资源 | `/api/v1/logs/{log_id}` - 更新日志信息 |
| DELETE | 删除资源 | `/api/v1/logs/{log_id}` - 删除日志 |
| PATCH | 部分更新资源 | `/api/v1/users/{user_id}` - 更新用户部分信息 |

## 2. 请求参数传递方式

### 2.1 路径参数
- 用于资源标识，如 `/api/v1/logs/{log_id}`
- 路径参数必须在 URL 中明确指定
- 适用于获取单个资源的场景

### 2.2 查询参数
- 用于过滤、排序、分页等，如 `/api/v1/logs?page=1&page_size=20`
- 查询参数是可选的，附加在 URL 后面
- 适用于列表查询、搜索等场景

### 2.3 请求体
- 用于传递复杂数据，如创建或更新资源时
- 使用 JSON 格式
- 适用于 POST、PUT、PATCH 请求

## 3. 认证与授权方式

### 3.1 认证方式
- 使用 JWT（JSON Web Token）进行认证
- Token 有效期为 **2 小时**（`ACCESS_TOKEN_EXPIRE_HOURS = 2`）
- 登录成功后，后端返回 token
- 前端在后续请求的 Authorization 头中携带 token
- 格式：`Authorization: Bearer {token}`
- 前端 `apiService` 拦截器自动附加 Token，业务代码不手动拼接

### 3.2 授权方式
- 基于角色的访问控制（RBAC）
- 角色包括：
  - `super_admin` — 超级管理员
  - `operator` — 操作员
  - `user` — 普通用户
  - `guest` — 访客
- 敏感操作（如 `/settings`、`/dictionary`）需要 `write` 权限
- 前端路由守卫检查 `meta.requiresAuth` 和 `meta.permissions`
- 无权限时重定向到 `/forbidden`

### 3.3 Token 失效机制
- `sys_user.token_version` 字段用于密码修改后使旧 JWT 失效
- 前端 401 响应时由拦截器统一清除 Token 并跳转登录页

## 4. 接口版本控制策略

- 使用 URL 路径进行版本控制，如 `/api/v1/logs`
- 全局前缀由 `settings.API_PREFIX = "/api/v1"` 控制
- 不同版本的接口可以并行存在
- 版本升级时保持向后兼容

## 5. 数据格式与编码方式

### 5.1 请求数据格式
- 优先使用 JSON 格式
- 对于文件上传，使用 `multipart/form-data` 格式

### 5.2 响应数据格式
- **大部分模块**统一使用 `ApiResponse` 结构：
  ```json
  {
    "success": true,
    "code": 200,
    "message": "操作成功",
    "data": {}
  }
  ```
- **例外模块**：`ei_report`、`wvw_report`、`bdcode` 使用自己的独立响应模型（见下方「已知问题」）

### 5.3 编码方式
- 统一使用 UTF-8 编码
- 响应头中设置 `Content-Type: application/json; charset=utf-8`

## 6. 错误处理与异常反馈机制

### 6.1 错误响应格式
- 统一使用 `ApiResponse` 结构，`success` 为 `false`
- 包含错误代码和错误信息
  ```json
  {
    "success": false,
    "code": 400,
    "message": "请求参数错误",
    "data": null
  }
  ```

### 6.2 常见 HTTP 状态码

| 状态码 | 含义 |
|--------|------|
| 200 | 请求成功 |
| 201 | 资源创建成功 |
| 204 | 无内容 |
| 400 | 请求参数错误 |
| 401 | 未授权（Token 过期或无效）|
| 403 | 禁止访问（权限不足）|
| 404 | 资源不存在 |
| 405 | 请求方法不允许 |
| 429 | 请求过于频繁 |
| 500 | 服务器内部错误 |
| 502 | 网关错误 |
| 503 | 服务不可用 |
| 504 | 网关超时 |

### 6.3 前端错误处理
- 由 `apiService` 响应拦截器统一处理错误
- **401**：自动清除 Token，跳转 `/login`
- **403**：跳转 `/forbidden`
- **429**：显示请求过于频繁提示
- **500/502/503/504**：显示通用服务器错误提示
- 业务逻辑错误显示后端返回的 `message`

## 7. 分页参数规范

### 7.1 分页参数
- `page`: 页码，从 1 开始
- `page_size`: 每页数量，默认 20，最大 100

### 7.2 分页响应格式
```json
{
  "success": true,
  "code": 200,
  "message": "获取成功",
  "data": {
    "items": [],
    "total": 100,
    "page": 1,
    "page_size": 20,
    "total_pages": 5
  }
}
```

## 8. 时间格式规范

- 日期时间格式：ISO 8601 格式，如 `2026-04-27T12:00:00Z`
- 日期格式：`YYYY-MM-DD`，如 `2026-04-27`
- 时间格式：`HH:MM:SS`，如 `12:00:00`

## 9. 命名规范

### 9.1 URL 命名
- 使用小写字母
- 单词之间用连字符（-）分隔
- 复数形式表示资源集合，如 `/api/v1/logs`

### 9.2 参数命名
- 路径参数：使用小写字母，单词之间用连字符（-）分隔
- 查询参数：使用小驼峰命名法，如 `pageSize`
- 请求体参数：使用小驼峰命名法

### 9.3 响应字段命名
- 使用小驼峰命名法，如 `accountName`
- 保持与请求参数命名一致

## 10. 前端 API 调用架构

前端采用三层 API 架构：

```
views/              # 页面组件（调用 Service）
  ↓
services/           # 业务服务层（调用 API 实例）
  ├── core/
  │   └── apiService.ts   # Axios 封装（ApiFactory / HttpClient）
  ├── ai/, auth/, build/, combat/, data/, ei/, skills/, system/
  └── index.ts            # Barrel export
  ↓
api/                # 原始 API 层（调用 HttpClient）
  ├── ai/, auth/, build/, combat/, data/, system/
  └── index.ts            # Barrel export
  ↓
constants/
  └── apiEndpoints.ts     # 所有端点路径常量
```

- **api/**：原始接口封装，每个文件是一个「类 + 单例实例」
- **services/**：业务逻辑封装，可进行数据转换和缓存
- **views/**：仅调用 Service，不直接调用 API 层

## 11. 已知问题与注意事项

> 以下问题已在代码中存在，前端对接时需注意。

### 11.1 响应模型不统一
- `ei_report`、`wvw_report`、`bdcode` 三个模块使用了自己的独立响应模型
- 其余模块均使用 `ApiResponse` 统一包装
- 前端调用这三个模块时，需直接读取响应体而非 `response.data`

### 11.2 `monitoring` 前缀重复
- `monitoring.py` 的 router prefix 已经是 `/api/v1/monitoring`
- `main.py` 注册时又加了 `prefix=settings.API_PREFIX`（`/api/v1`）
- **实际路径为 `/api/v1/api/v1/monitoring/...`**
- 前端调用时请以实际 `/docs` 中展示的路径为准

### 11.3 `bdcode` 特殊前缀
- `bdcode` 是唯一在 `main.py` 中注册时**不带** `settings.API_PREFIX` 的 router
- 其内部已硬编码前缀 `/api/bdcode`
- 实际路径为 `/api/bdcode/...`，而非 `/api/v1/bdcode/...`

### 11.4 `database_management.py` 未注册
- 该文件存在于 `routers` 目录但 `main.py` 未导入注册
- 当前不可访问，请勿对接

## 12. 性能优化建议

### 12.1 前端优化
- 使用缓存减少重复请求
- 实现分页加载，避免一次性加载大量数据
- 合理使用防抖和节流
- 减少请求次数，合并相关请求

### 12.2 后端优化
- 使用数据库索引
- 实现数据缓存
- 优化查询语句
- 使用异步处理

## 13. 调试与测试

### 13.1 调试工具
- 使用 Postman 或浏览器 DevTools 进行 API 测试
- FastAPI 自动 Swagger 文档：`/docs`

### 13.2 环境
- 开发环境：`localhost:8000`
- API 文档：`http://localhost:8000/docs`

## 14. 接口文档

- 使用 FastAPI 自动生成的 Swagger 文档
- 访问 `/docs` 查看完整的 API 文档
- 文档包含接口说明、参数描述、返回值等信息
- 离线文档参考 `docs/openapi_schema.json`
