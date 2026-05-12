# 前端项目目录规范

> 本规范定义 `frontend/src/` 下所有文件的组织原则与放置规则。
> 核心原则：**按职责分层、按模块分组、同类型同目录。**

---

## 一、目录层级总览

```
src/
├── api/              # API 客户端层（原始 HTTP 请求封装）
├── assets/           # 静态资源（图片、字体、SVG 等）
├── components/       # Vue 组件（按业务模块细分）
├── composables/      # 组合式函数（Vue 3 Composition API 逻辑复用）
├── config/           # 应用配置（端点、主题、存储配置等）
├── layout/           # 布局组件（MainLayout、LoginLayout 等）
├── locales/          # 国际化文案
├── main.ts           # 应用入口文件
├── models/           # 运行时数据模型 / DTO
├── router/           # 路由配置
├── services/         # 业务服务层（比 api 更高层的业务封装）
├── store/            # Pinia 状态管理
├── styles/           # 全局样式与 CSS 工具类（纯 .css 文件）
├── types/            # TypeScript 全局类型定义
├── utils/            # 纯工具函数（无 Vue 依赖的通用逻辑）
├── views/            # 页面级 Vue 组件
├── App.vue           # 根组件
└── vite-env.d.ts     # Vite 环境类型声明
```

---

## 二、文件放置规则

### 2.1 Vue 组件（`.vue`）

| 放置位置 | 说明 | 示例 |
|----------|------|------|
| `views/{module}/` | 页面级组件（对应路由） | `views/combat/CombatLogListView.vue` |
| `components/{module}/` | 可复用业务组件 | `components/combat/PlayerDetailPanel.vue` |
| `components/common/ui/` | 基础 UI 组件 | `components/common/ui/BaseButton.vue` |
| `layout/` | 布局壳组件 | `layout/MainLayout.vue` |

**规范：**
- 组件样式必须内联在 `<style scoped>` 中，禁止在组件目录下创建独立 `.css` 文件
- 若样式过于复杂需抽离，统一放置到 `styles/components/{module}/`

### 2.2 样式文件（`.css`）

**`styles/` 是唯一允许存放独立 `.css` 文件的目录。**

| 子目录 | 用途 | 示例 |
|--------|------|------|
| `styles/components/{module}/` | 复杂组件的抽离样式 | `styles/components/combat/PlayerDetailPanel.css` |
| `styles/layouts/` | 布局相关样式 | `styles/layouts/main.css` |
| `styles/views/{module}/` | 复杂页面的抽离样式 | `styles/views/auth/LoginView.css` |
| `styles/utilities/` | 工具类（动画、工具函数等） | `styles/utilities/animations.css` |
| `styles/primevue/` | PrimeVue 主题覆盖 | `styles/primevue/index.css` |

**规范：**
- `styles/` 目录下**禁止存放 `.ts` 文件**
- 设计 Token 等 TS 常量应放置到 `config/` 或 `utils/theme/`

### 2.3 TypeScript 逻辑文件（`.ts`）

`.ts` 文件**不按文件类型统一扁平化**，而是按**功能职责**分散到对应模块目录。

| 目录 | 职责 | 禁止放置 |
|------|------|----------|
| `api/` | 原始 HTTP 请求封装（axios/fetch 层） | `.vue`、`.css` |
| `services/` | 业务服务层（含状态转换、错误处理） | `.vue`、`.css` |
| `composables/` | Vue 3 组合式函数（含响应式逻辑） | `.vue`、`.css` |
| `utils/` | 纯工具函数（无 Vue 依赖） | `.vue`、`.css` |
| `store/` | Pinia Store 模块 | `.vue`、`.css` |
| `models/` | 运行时数据模型、DTO 定义 | `.vue`、`.css` |
| `types/` | TypeScript 全局类型声明 | `.vue`、`.css`、运行时逻辑 |
| `config/` | 应用配置常量 | `.vue`、`.css` |
| `router/` | 路由配置 | `.vue`、`.css` |
| `locales/` | i18n 文案文件 | `.vue`、`.css` |

**规范：**
- 不允许在 `src/` 根目录下创建新的 `.ts` 文件（除 `main.ts`、`vite-env.d.ts`、`App.vue` 外）
- 不允许在 `components/`、`views/`、`layout/` 下创建独立 `.ts` 文件（barrel export `index.ts` 除外）

### 2.4 静态资源

| 目录 | 用途 |
|------|------|
| `assets/fonts/` | 字体文件 |
| `assets/icons/` | SVG 图标（含 `index.ts` 图标索引） |
| `assets/images/` | 图片资源 |
| `assets/data/` | 静态 JSON 数据 |

**规范：**
- `assets/` 下允许存在 `.ts` 资源索引文件（如 `assets/icons/index.ts`）
- 禁止在 `assets/` 下放置业务逻辑 `.ts` 文件

---

## 三、命名规范

### 3.1 文件命名

| 类型 | 命名规范 | 示例 |
|------|----------|------|
| Vue 页面 | PascalCase + `View` 后缀 | `CombatLogListView.vue` |
| Vue 组件 | PascalCase | `PlayerDetailPanel.vue` |
| Composable | camelCase + `use` 前缀 | `useCombatLogDetail.ts` |
| Service 类 | PascalCase + `Service` 后缀 | `logsService.ts` / `LogsService` |
| Util 函数 | camelCase | `formatCompactNumber.ts` |
| Store | camelCase + `use` 前缀 + `Store` 后缀 | `useSettingsStore.ts` |
| CSS 文件 | PascalCase（与对应组件同名）或 kebab-case | `PlayerDetailPanel.css` |

### 3.2 目录命名

- 使用 **kebab-case** 小写：
  - ✅ `composables/combat/`
  - ✅ `components/common/ui/`
  - ❌ `components/Common/UI/`

---

## 四、单一职责原则

每个目录、每个文件应有且只有一个明确的职责：

- **组件** = 展示 + 交互（逻辑抽离到 composables）
- **Composables** = 可复用的响应式逻辑
- **Services** = 业务封装 + 数据处理
- **API** = 纯 HTTP 请求（不含业务判断）
- **Utils** = 纯函数工具（无副作用、无 Vue 依赖）
- **Store** = 全局状态
- **Models** = 数据结构定义
- **Types** = TypeScript 类型（供编译期使用）

---

## 五、例外与特殊说明

| 文件/目录 | 位置 | 原因 |
|-----------|------|------|
| `components/index.ts` | `components/` 根目录 | Barrel export，行业惯例，用于统一对外导出组件 |
| `assets/icons/index.ts` | `assets/icons/` | 资源索引文件，管理同目录下 SVG 图标 |
| `main.ts` | `src/` 根目录 | 应用入口，Vue 项目标准做法 |
| `vite-env.d.ts` | `src/` 根目录 | Vite 环境类型声明，标准做法 |
| `App.vue` | `src/` 根目录 | 根组件，Vue 项目标准做法 |

---

## 六、禁止事项

1. ❌ 禁止在 `components/`、`views/`、`layout/` 目录下创建独立 `.css` 文件
2. ❌ 禁止在 `styles/` 目录下存放 `.ts` 文件
3. ❌ 禁止在 `src/` 根目录下新增 `.ts` 逻辑文件
4. ❌ 禁止创建单文件目录（如 `directive/` 只放一个文件）
5. ❌ 禁止跨层级引用（如 `views/` 直接引用 `components/` 深层子组件时应使用 `@/` 别名）

---

## 七、目录变更记录

| 日期 | 变更内容 |
|------|----------|
| 2026-05-10 | 将散落在 `components/`、`layout/`、`views/` 下的独立 `.css` 文件统一迁移至 `styles/` |
| 2026-05-10 | 删除微型目录 `constants/`（合并至 `config/` 和 `styles/`） |
| 2026-05-10 | 删除微型目录 `data/`（`builds.json` 移至 `assets/data/`，`mockEiData.ts` 删除） |
| 2026-05-10 | 将 `directive/permission.ts` 合并至 `composables/system/usePermissionDirective.ts` |
| 2026-05-10 | 将 `styles/designTokens.ts` 移至 `config/designTokens.ts` |
| 2026-05-10 | 将散落文件（`useAuthGuard.ts`、`eiData.ts`、`skillIcons.ts`、`useTopNav.ts`）按模块归位 |
