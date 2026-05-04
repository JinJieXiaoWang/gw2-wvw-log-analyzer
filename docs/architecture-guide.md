# GW2-APEX 项目架构规范指南

> **版本**: v3.0  
> **更新日期**: 2026-05-05  
> **适用范围**: 本项目全部前端代码（Vue 3 + TypeScript + Vite + Tailwind CSS + PrimeVue Aura）

---

## 版本变更记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v3.0 | 2026-05-05 | 全面更新为当前实际架构：细化技术栈、目录结构、命名规范、状态管理、路由、入口流程；新增约束清单 |
| v2.x | 2026-05-04 | 原架构规范版本（未标注版本号） |

---

## 一、技术栈

| 层级 | 技术 |
|------|------|
| 框架 | Vue 3（Composition API，`<script setup lang="ts">`） |
| 语言 | TypeScript（严格模式） |
| 构建工具 | Vite |
| 样式 | Tailwind CSS（`darkMode: 'class'`）+ 自定义 CSS |
| UI 组件库 | PrimeVue（Aura 预设） |
| 状态管理 | Pinia（Composition API 风格）+ 自定义 AuthStore 类（非 Pinia） |
| 路由 | Vue Router（`createRouter` + `createWebHistory`） |
| HTTP 客户端 | Axios（通过 `ApiFactory` / `HttpClient` 封装于 `services/core/apiService.ts`） |
| 路径别名 | `@/` 指向 `src/` |

---

## 二、核心原则：单一入口

所有模块必须通过唯一、明确的入口进行引用，禁止多入口、分散引用和硬编码。

---

## 三、目录结构

```
src/
├── api/                    # 原始 API 层（按领域分目录：ai, auth, build, combat, data, system）
│   └── index.ts            # Barrel export
├── assets/                 # 静态资源（fonts, images）
├── components/             # 组件（按功能模块分目录）
│   ├── common/             # 基础公共组件（BaseDialog, BaseState, EmptyState, ErrorState, LoadingState, PageHeader, etc.）
│   ├── aiAnalysis/         # AI 分析组件
│   ├── attendance/         # 出勤统计组件
│   ├── build-library/      # Build 图书馆组件
│   ├── buildParser/        # Build 解析组件
│   ├── dashboard/          # 数据看板组件
│   ├── dict/               # 字典组件
│   ├── eiDetail/           # EI 详情页组件
│   ├── logManagement/      # 日志管理组件
│   ├── settings/           # 设置页组件
│   ├── skillRotation/      # 技能循环组件
│   ├── system/             # 系统组件
│   ├── theme/              # 主题组件
│   └── wvwReport/          # WVW 报告组件
├── composables/            # 组合式函数（core/, system/）
├── config/                 # 配置文件（themePreset.ts）
├── constants/              # 常量定义（apiEndpoints.ts, designTokens.ts, themes.ts）
├── data/                   # 静态数据
├── directive/              # 自定义指令（permission.ts）
├── layout/                 # 页面布局
│   ├── MainLayout.vue
│   ├── LoginLayout.vue
│   └── components/
├── models/                 # 领域模型类型（按领域分目录 + index.ts barrel export）
├── router/                 # 路由配置
│   ├── index.ts
│   └── permissionGuard.ts
├── services/               # 业务服务层（core/ + 按领域分目录 + index.ts barrel export）
│   ├── core/               # 核心基础设施（apiService.ts, errorHandler.ts, mockData.ts）
│   ├── index.ts            # Barrel export
│   └── ...                 # 各领域服务目录
├── store/                  # 状态管理
│   ├── index.ts            # Pinia 入口
│   ├── modules.ts          # 模块注册
│   ├── system/settings.ts  # 系统设置（Composition API 风格，localStorage 持久化）
│   ├── eiData.ts           # EI 日志数据状态
│   └── build/buildLibrary.ts # Build 图书馆状态
├── styles/                 # 样式系统
│   ├── index.css           # 唯一 CSS 入口
│   ├── base.css            # Tailwind 指令 + 基础样式
│   ├── variablesUnified.css # 统一 CSS 变量系统（355 行，唯一变量源）
│   ├── components/         # 组件通用样式
│   ├── layouts/            # 布局样式
│   ├── primevue/           # PrimeVue 组件覆盖
│   └── utilities/          # 工具类 + 动画
├── types/                  # TypeScript 全局类型（api.ts, build.ts, eliteInsights.ts, permission.ts + index.ts）
├── utils/                  # 工具函数
│   ├── auth/               # 认证相关
│   ├── core/               # 核心工具
│   ├── error/              # 错误处理
│   ├── mock/               # Mock 数据
│   ├── permission/         # 权限工具
│   ├── profession/         # 职业相关
│   ├── theme/              # 主题工具
│   └── skillIcons.ts       # 技能图标
├── views/                  # 页面组件（按业务模块分组）
│   ├── auth/               # 认证模块
│   ├── build/              # Build 配置模块
│   ├── combat/             # 战斗日志分析模块
│   ├── data/               # 数据统计分析模块
│   ├── error/              # 错误页面
│   ├── system/             # 系统管理模块
│   └── test/               # 测试工具
├── App.vue                 # 根组件
└── main.ts                 # 应用入口
```

> **注意**: `components/` 下子目录命名存在不一致：`build-library`（kebab-case）vs `buildParser`（camelCase）。新增目录建议统一使用 kebab-case。

---

## 四、命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| Vue SFC | PascalCase | `EmptyState.vue`, `BuildLibraryView.vue` |
| TS 模块 | camelCase | `authService.ts`, `apiEndpoints.ts` |
| 组合式函数 | camelCase + `use` 前缀 | `useTheme.ts`, `useAuth.ts` |
| Store | `use` + PascalCase + `Store` | `useSettingsStore.ts` |
| 服务类 | PascalCase + `Service` 后缀 | `AuthService` |
| 服务实例 | camelCase + `Service` 后缀 | `authService` |
| API 类 | PascalCase + `Api` 后缀 | `AuthApi` |
| 页面组件 | PascalCase + `View` 后缀 | `DashboardView.vue`, `LogManagementView.vue` |
| CSS 类名 | kebab-case | `.action-btn`, `.game-card` |
| CSS 变量 | kebab-case | `--color-primary`, `--space-4` |
| 常量 | UPPER_CASE_WITH_UNDERSCORES | `API_ENDPOINTS` |

---

## 五、CSS 样式规范

### 5.1 唯一入口

```
src/main.ts
└── import './styles/index.css'   ← 唯一 CSS 入口
```

**禁止**：
- ❌ 在 Vue 组件中 `import 'xxx.css'`
- ❌ 在 Vue 组件中使用 `<style src="xxx">`
- ❌ 在 `index.html` 中引入本地 CSS 文件
- ❌ 在 CSS 子文件中 `@import` 其他变量文件（变量由入口统一引入）

### 5.2 样式文件结构

```
src/styles/
├── index.css              ← 入口：统合所有子样式
├── variablesUnified.css   ← 统一 CSS 变量系统（355 行，唯一变量源）
├── base.css               ← Tailwind 指令 + 基础样式
├── layouts/               ← 布局样式
├── components/            ← 组件通用样式
├── utilities/             ← 工具类 + 动画
└── primevue/              ← PrimeVue 组件覆盖
```

### 5.3 变量管理

- **唯一变量源**：`variablesUnified.css`
- 所有 CSS 变量必须定义在 `variablesUnified.css` 的 `:root` 中
- 深色/浅色模式通过 `:root.dark` / `:root.light` 管理
- Tailwind 配置 `darkMode: 'class'`
- PrimeVue/Aura 变量桥接：`--p-primary-*`, `--p-surface-*`
- 关键变量：主色调 `#165DFF`、辅助色 `#FF7D00`、AI 专属色 `#00E5C0`、深色游戏风格 `#0D0D0F`
- 自定义阴影：`shadow-glow-primary`, `shadow-glow-ai`
- 自定义动画：`fade-in`, `slide-up`, `pulse-glow`

---

## 六、API 接口规范

### 6.1 单一入口

**业务代码（views / components / composables / stores）只能从以下入口导入 API：**

| 入口 | 用途 | 示例 |
|------|------|------|
| `@/api` | API 数据层（原始 HTTP + DTO 类型） | `import { authApi } from '@/api'` |
| `@/services` | 业务服务层（封装逻辑 + 数据转换） | `import { authService } from '@/services'` |

**禁止**：
- ❌ 直接 `import { apiFactory } from '@/services/core/apiService'`（仅 service 内部可用）
- ❌ 直接 `import { HttpClient } from '@/services/core/apiService'`（仅 api 内部可用）
- ❌ 使用原生 `fetch` 调用业务 API（特殊情况如本地 JSON 配置除外）
- ❌ 硬编码 API URL 字符串

### 6.2 端点定义唯一源

**唯一端点定义文件**：`src/constants/apiEndpoints.ts`

```ts
// ✅ 正确：使用常量
import { API_ENDPOINTS } from '@/constants/apiEndpoints'
apiFactory.get(API_ENDPOINTS.LOGS.LIST)

// ❌ 错误：硬编码
apiFactory.get('/api/v1/logs')
```

### 6.3 API 与 Service 的职责边界

| 层级 | 职责 | 禁止做的事 |
|------|------|-----------|
| `src/api/*` | 原始 HTTP 通信、DTO 类型定义 | 不写业务逻辑、不做数据转换 |
| `src/services/*` | 业务封装、错误处理、数据转换、缓存 | 不硬编码 URL、不直接 `fetch` |

### 6.4 拦截器行为

- **请求拦截器**：自动附加 Bearer Token
- **响应拦截器**：统一错误处理，401 清除 Token 跳转登录页

### 6.5 Barrel Export 完整性

- `src/api/index.ts` 必须导出所有 api 模块
- `src/services/index.ts` 必须导出所有 service 模块和类型
- 新增 api/service 时，必须同步更新对应的 `index.ts`

---

## 七、组件引用规范

### 7.1 引用路径规则

| 场景 | 正确写法 | 错误写法 |
|------|---------|---------|
| view → component | `import X from '@/components/common/X.vue'` | `../../components/common/X.vue` |
| component → component（同目录） | `import X from './X.vue'` | `@/components/...` |
| component → component（跨目录） | `import X from '@/components/dict/X.vue'` | `../../dict/X.vue` |
| router → view | `import X from '@/views/xxx/X.vue'` | 相对路径 |

### 7.2 Barrel Export 优先

对于高频使用的组件目录，优先使用 barrel export：

```ts
// ✅ 推荐：使用 barrel export
import { PageHeader, StatCard, EmptyState } from '@/components/common'

// ⚠️ 可接受：直接引用单个文件
import PageHeader from '@/components/common/PageHeader.vue'
```

**已建立 barrel export 的目录**：
- `src/components/common/`
- `src/components/settings/`
- `src/components/dict/`

> 新增 `common` / `settings` / `dict` 组件时，必须加入对应 `index.ts`。

### 7.3 分层规则

- `views` 可以引用 `components`、`services`、`api`
- `components` 可以引用 `components`（跨目录）、`composables`，禁止引用 `views`
- `models` 禁止引用 `services`（types 层不依赖服务层）
- `services` 可以引用 `api`、`constants`
- `api` 可以引用 `services/core/apiService`（仅限 HttpClient / apiFactory）

---

## 八、路由规范

- `createRouter` + `createWebHistory`
- 所有页面懒加载（`() => import('@/views/xxx/XxxView.vue')`）
- 布局：`MainLayout` / `LoginLayout`
- 权限守卫在 `router/index.ts` 中直接定义
- 路由元信息：`meta.requiresAuth` + `meta.permissions`

---

## 九、状态管理规范

### 9.1 Pinia Store

- `store/system/settings.ts` — 系统设置（Composition API 风格，`ref` + `watch`，localStorage 持久化，主题/语言/水印）
- `store/eiData.ts` — EI 日志数据状态
- `store/build/buildLibrary.ts` — Build 图书馆状态
- Store 命名：`use` + PascalCase + `Store`

### 9.2 自定义权限存储

- `AuthStore` 为自定义类 + 单例（**非 Pinia**）
- 与 Pinia store 并存，负责登录态、Token、权限判断

---

## 十、类型定义规范

### 10.1 类型分层

```
src/types/       ← 全局共享类型（权限、插件、基础 API 类型）
src/models/      ← 领域模型类型（日志、战斗、Build 等）
src/api/*.ts     ← API DTO 类型（与后端接口对应）
src/services/*.ts ← Service 层类型（业务参数、响应包装）
```

### 10.2 禁止反向依赖

- `models` 层禁止从 `services` 层导入类型
- `types` 层禁止从任何业务层导入
- 核心基础设施类型（ApiResponse 等）统一放在 `src/types/api.ts`

---

## 十一、应用入口 `main.ts` 流程

1. import Vue, PrimeVue, ToastService, ConfirmationService
2. import router, pinia, 权限指令, ThemeService, GameThemePreset
3. import `'./styles/index.css'`（唯一 CSS 入口）
4. `ThemeService.initialize()`
5. `createApp(App)`
6. 注册 PrimeVue（GameThemePreset, `darkModeSelector: ':root'`）
7. 注册 ToastService, ConfirmationService, pinia, router
8. 注册 `v-permission` 指令
9. 监听 `auth:logout`
10. mount

---

## 十二、新增模块检查清单

新增任何模块时，必须完成以下检查：

- [ ] CSS：未引入新的 CSS 入口，变量已加入 `variablesUnified.css`
- [ ] API：URL 使用 `API_ENDPOINTS` 常量，未硬编码
- [ ] API：如新增 api 模块，已加入 `src/api/index.ts`
- [ ] Service：如新增 service，已加入 `src/services/index.ts`
- [ ] Component：如新增 common/settings/dict 组件，已加入对应 `index.ts`
- [ ] Import：跨目录引用使用 `@/` 别名，未使用 `../../`
- [ ] HTTP：未使用原生 `fetch` 调用业务 API
- [ ] 命名：Vue SFC 使用 PascalCase，页面组件使用 `View` 后缀，Store 使用 `useXxxStore`

---

## 十三、工具与脚本

### 13.1 检查硬编码 URL

```bash
# 查找硬编码的 /api/v1 路径（排除 constants 和特定文件）
grep -r "'/api/v1" src/ --include="*.ts" --include="*.vue" | grep -v "apiEndpoints.ts" | grep -v "apiService.ts"
```

### 13.2 检查 fetch 绕过

```bash
grep -rn "fetch(" src/ --include="*.ts" --include="*.vue" | grep -v "configManager" | grep -v "node_modules"
```

### 13.3 检查 barrel export 遗漏

```bash
# 检查 components/common 下的组件是否都在 index.ts 中
ls src/components/common/*.vue | xargs -n1 basename | sed 's/.vue//' | while read name; do
  grep -q "$name" src/components/common/index.ts || echo "Missing: $name"
done
```
