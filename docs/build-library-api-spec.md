# Build Library API 规范

> **版本**: v2.0  
> **创建日期**: 2026-05-02  
> **更新日期**: 2026-05-05  
> **状态**: 后端已实现，API 可用

> **更新说明**: 后端 `builds.py` 已实现 5 个核心端点（`GET /`、`GET /{id}`、`POST /`、`PUT /{id}`、`DELETE /{id}`），使用 `ApiResponse` 统一包装。前端已对接真实 API。

---

## 1. 概述

本文档定义了 **配置图书馆 (Build Library)** 模块的标准 API 接口规范。后端已实现完整 CRUD 端点，前端已对接真实 API。

### 1.1 基础信息

| 项目 | 值 |
|------|-----|
| Base URL | `/api/v1/builds` |
| Content-Type | `application/json` |
| 认证方式 | Bearer Token (JWT) |
| 字符编码 | UTF-8 |

### 1.2 通用响应格式

```typescript
interface ApiResponse<T> {
  success: boolean      // 业务是否成功
  code: number          // HTTP 状态码或业务码
  message: string       // 提示信息
  data: T               // 响应数据
  timestamp: string     // ISO 8601 时间戳
}
```

### 1.3 通用错误码

| Code | 含义 | 说明 |
|------|------|------|
| 200 | 成功 | 操作成功完成 |
| 201 | 创建成功 | 资源已创建 |
| 400 | 请求参数错误 | 表单验证失败 |
| 401 | 未授权 | Token 缺失或过期 |
| 403 | 禁止访问 | 权限不足 |
| 404 | 资源不存在 | Build ID 无效 |
| 422 | 验证失败 | 字段级校验错误 |
| 500 | 服务器内部错误 | 系统异常 |

---

## 2. 数据模型

### 2.1 BuildEntry（完整实体）

```typescript
interface BuildEntry {
  id: string                    // 系统生成，UUID 或 Snowflake
  slug: string                  // URL 友好标识，自动生成
  title: string                 // 配置标题，2-100字符
  profession: string            // 职业，枚举值
  professionColor: string       // 职业主题色，HEX格式
  eliteSpec: string | null      // 精英特长，可选
  role: 'dps' | 'support'       // 职责
  subRoles: SubRole[]           // 子职责数组
  armorType: string             // 护甲类型
  weapons: BuildWeapon[]        // 武器配置
  relic: string                 // 古物
  rune: string                  // 符文
  food: string                  // 食物
  wrench: string                // 扳手/通用效果
  infusion: string              // 灌注
  attrRequirements: string[]    // 属性要求
  bdCode: string                // GW2 Build Code
  traitLines: BuildTraitLine[]  // 特性线
  rotationCommands: BuildRotationCommand[]  // 指挥口令
  mechanics: BuildMechanic[]    // 机制来源
  videos: BuildVideo[]          // 参考视频
  author: string                // 作者，1-50字符
  updatedAt: string             // ISO 8601，自动更新
  wordCount: number             // 字数统计（后端计算）
  isMeta: boolean               // 是否为 META 配置（管理员标记）
}
```

### 2.2 子类型定义

```typescript
interface BuildWeapon {
  set: number         // 武器套装编号 (1, 2)
  name: string        // 武器名称
  sigils: string[]    // 法印列表
}

interface BuildTraitLine {
  name: string
  choices: [number, number, number]  // 三行特性选择 (1-3)
}

interface BuildRotationCommand {
  callout: string     // 指挥口令
  action: string      // 对应操作
  note?: string       // 备注
}

interface BuildMechanic {
  name: string
  sources: string[]   // 来源技能/特性
}

interface BuildVideo {
  title: string
  url: string
  author?: string
}

type SubRole = 'boon' | 'heal' | 'tank' | 'cc'
```

### 2.3 创建/更新 DTO

```typescript
// 创建请求（前端表单 → 后端）
interface BuildCreateDto {
  title: string
  profession: string
  eliteSpec: string | null
  role: 'dps' | 'support'
  subRoles: SubRole[]
  armorType: string
  weapons: BuildWeapon[]
  relic: string
  rune: string
  food: string
  wrench: string
  infusion: string
  attrRequirements: string[]
  bdCode: string
  traitLines: BuildTraitLine[]
  rotationCommands: BuildRotationCommand[]
  mechanics: BuildMechanic[]
  videos: BuildVideo[]
  author: string
}

// 更新请求（只发送变更字段）
type BuildUpdateDto = Partial<BuildCreateDto>
```

### 2.4 验证规则

| 字段 | 规则 | 错误码 |
|------|------|--------|
| title | 必填，2-100字符 | TITLE_TOO_SHORT / TITLE_TOO_LONG |
| profession | 必填，必须在职业枚举中 | INVALID_PROFESSION |
| role | 必填，`dps` 或 `support` | INVALID_ROLE |
| bdCode | 必填，正则 `^\[&[A-Za-z0-9+/=]+\]$` | INVALID_BD_CODE |
| author | 必填，1-50字符 | INVALID_AUTHOR |
| armorType | 创建时必填 | ARMOR_TYPE_REQUIRED |

---

## 3. 实体关系图 (ERD)

```
┌─────────────────┐       ┌─────────────────┐
│   BuildEntry    │       │   BuildWeapon   │
├─────────────────┤       ├─────────────────┤
│ PK id           │◄──────┤ FK buildId      │
│    title        │  1:N  │    set          │
│    profession   │       │    name         │
│    role         │       │    sigils[]     │
│    ...          │       └─────────────────┘
└─────────────────┘
         │
         │ 1:N
         ▼
┌─────────────────┐       ┌─────────────────┐
│ BuildTraitLine  │       │BuildRotationCmd │
├─────────────────┤       ├─────────────────┤
│ FK buildId      │       │ FK buildId      │
│    name         │       │    callout      │
│    choices[3]   │       │    action       │
└─────────────────┘       │    note         │
                          └─────────────────┘
         │
         │ 1:N
         ▼
┌─────────────────┐       ┌─────────────────┐
│ BuildMechanic   │       │   BuildVideo    │
├─────────────────┤       ├─────────────────┤
│ FK buildId      │       │ FK buildId      │
│    name         │       │    title        │
│    sources[]    │       │    url          │
└─────────────────┘       │    author       │
                          └─────────────────┘
```

---

## 4. API 端点

### 4.1 获取配置列表

```http
GET /api/v1/builds
```

**Query Parameters：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | number | 否 | 页码，默认 1 |
| pageSize | number | 否 | 每页数量，默认 50，最大 100 |
| profession | string | 否 | 职业过滤 |
| role | string | 否 | 职责过滤 (`dps` / `support`) |
| subRoles | string[] | 否 | 子职责过滤（多选，AND 逻辑） |
| searchQuery | string | 否 | 搜索关键词（标题/职业/作者） |
| sortBy | string | 否 | 排序：`updated` / `profession` / `name` |

**Response (200)：**

```json
{
  "success": true,
  "code": 200,
  "message": "查询成功",
  "data": {
    "items": [...],
    "total": 42,
    "page": 1,
    "pageSize": 50,
    "totalPages": 1
  },
  "timestamp": "2026-05-02T08:00:00.000Z"
}
```

### 4.2 获取单个配置

```http
GET /api/v1/builds/{id}
```

**Response (200)：**

```json
{
  "success": true,
  "code": 200,
  "message": "查询成功",
  "data": { /* BuildEntry */ },
  "timestamp": "2026-05-02T08:00:00.000Z"
}
```

**Response (404)：**

```json
{
  "success": false,
  "code": 404,
  "message": "配置不存在",
  "data": null,
  "timestamp": "2026-05-02T08:00:00.000Z"
}
```

### 4.3 创建配置

```http
POST /api/v1/builds
```

**Request Body：** `BuildCreateDto`

**Response (201)：**

```json
{
  "success": true,
  "code": 201,
  "message": "创建成功",
  "data": { /* BuildEntry */ },
  "timestamp": "2026-05-02T08:00:00.000Z"
}
```

**Response (422)：**

```json
{
  "success": false,
  "code": 422,
  "message": "标题至少需要 2 个字符；请选择有效的职业",
  "data": null,
  "timestamp": "2026-05-02T08:00:00.000Z"
}
```

### 4.4 更新配置

```http
PUT /api/v1/builds/{id}
```

**Request Body：** `BuildUpdateDto`（只包含变更字段）

**Response (200)：**

```json
{
  "success": true,
  "code": 200,
  "message": "更新成功",
  "data": { /* BuildEntry */ },
  "timestamp": "2026-05-02T08:00:00.000Z"
}
```

### 4.5 删除配置

```http
DELETE /api/v1/builds/{id}
```

**Response (200)：**

```json
{
  "success": true,
  "code": 200,
  "message": "删除成功",
  "data": null,
  "timestamp": "2026-05-02T08:00:00.000Z"
}
```

### 4.6 批量删除

```http
DELETE /api/v1/builds/batch
```

**Request Body：**

```json
{
  "ids": ["id1", "id2", "id3"]
}
```

**Response (200)：**

```json
{
  "success": true,
  "code": 200,
  "message": "成功删除 3 个配置",
  "data": {
    "deleted": 3,
    "failed": []
  },
  "timestamp": "2026-05-02T08:00:00.000Z"
}
```

### 4.7 导入配置

```http
POST /api/v1/builds/import
```

**Request Body：**

```json
{
  "mode": "merge",     // "merge" | "replace"
  "builds": [...]      // BuildEntry[]
}
```

---

## 5. 前端 → 后端迁移指南

### 5.1 当前架构（Mock 阶段）

```
BuildLibraryView.vue
    ↓ (调用)
useBuildLibrary.ts (composable)
    ↓ (调用)
buildLibraryService.ts (Mock 服务)
    ↓ (读写)
localStorage (持久化)
```

### 5.2 目标架构（后端接入后）

```
BuildLibraryView.vue
    ↓ (无需改动)
useBuildLibrary.ts (composable)
    ↓ (无需改动)
buildLibraryService.ts (真实 API 服务)
    ↓ (HTTP 请求)
Backend API (/api/v1/builds/*)
    ↓ (读写)
Database (PostgreSQL / MySQL)
```

### 5.3 迁移步骤

1. **替换服务层**：将 `buildLibraryService.ts` 中的 `localStorage` 操作替换为 `axios` HTTP 请求
2. **添加认证头**：在请求中注入 JWT Token
3. **保持接口签名**：`BuildLibraryService` 类的方法签名和返回类型不变
4. **更新错误处理**：适配后端错误码体系
5. **移除 Mock 延迟**：删除 `mockDelay()` 调用

### 5.4 前端无需改动的文件

| 文件 | 说明 |
|------|------|
| `BuildLibraryView.vue` | 完全解耦，只依赖 composable |
| `BuildEditorDialog.vue` | 纯展示组件，只 emit 事件 |
| `BuildDeleteDialog.vue` | 纯展示组件，只 emit 事件 |
| `BuildCard.vue` | 纯展示组件 |
| `useBuildLibrary.ts` | 只调用 service 方法 |
| `types/build-library.ts` | 类型定义即 API 契约 |

---

## 6. 数据管理策略对比

### 方法 A：前端完整 CRUD（已采用）

**适用场景：** 开发阶段无后端、数据量小（<1000 条）、需要快速验证产品概念

**技术实现：**
- 数据持久化：`localStorage`（JSON 序列化）
- 状态管理：Vue 3 Composition API + 自定义 Composable
- 验证逻辑：纯前端同步验证 + 异步服务端校验

**优点：**
- 零后端依赖，开发效率高
- 用户体验完整，可立即验证交互流程
- 数据模型在迭代中快速调整
- localStorage 持久化保证刷新不丢数据

**缺点：**
- 数据仅在单设备可用
- 无法支持多用户协作
- localStorage 有容量限制（~5MB）
- 安全性较低（数据在客户端明文存储）

### 方法 B：纯数据检索系统

**适用场景：** 数据由后端/管理员维护，前端只读展示

**技术实现：**
- 数据存储：静态 JSON 文件或 CDN
- 状态管理：只读 Store，无 mutation
- 筛选逻辑：前端内存计算

**优点：**
- 实现简单，无数据一致性风险
- 适合内容发布型场景
- 可完全静态化部署

**缺点：**
- 无法支持用户自定义内容
- 需要重新部署才能更新数据
- 无法满足社区/UGC 需求

### 最终建议

**采用方法 A（前端完整 CRUD）作为当前阶段方案**，理由：

1. **产品定位**：Build Library 是一个工具型内容库，用户（指挥/团长）需要根据自己的理解创建和调整配置，不是纯内容消费场景
2. **使用模式**：当前 17 个配置远未覆盖所有玩法，社区贡献配置是核心需求
3. **可扩展性**：当后端就绪时，只需替换 `buildLibraryService.ts` 实现，零 UI 改动
4. **开发时间线**：无需等待后端接口，可独立交付完整功能

**未来演进路线：**
- Phase 1（当前）：前端 Mock CRUD + localStorage 持久化
- Phase 2：后端接入，用户配置同步到服务器
- Phase 3：增加用户权限（普通用户/管理员）、审核流程、版本历史
- Phase 4：社区评分、评论、收藏功能
