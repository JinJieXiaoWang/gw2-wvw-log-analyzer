# 代码审查检查清单

> **版本**: v2.0  
> **更新日期**: 2026-05-05  
> **适用范围**: 本项目全部前端代码（Vue 3 + TypeScript + Tailwind CSS + PrimeVue Aura）

---

## 版本变更记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v2.0 | 2026-05-05 | 补充目录命名一致性、View 后缀、主题初始化、PrimeVue Aura 等检查项 |
| v1.0 | 2026-05-01 | 初始版本 |

---

## A. API 与网络层

- [ ] **无硬编码 URL**：所有 API 调用使用 `API_ENDPOINTS` 常量（`src/constants/apiEndpoints.ts`）
- [ ] **无 fetch 绕过**：业务 API 调用统一通过 `apiFactory` / `HttpClient`，不使用原生 `fetch`
- [ ] **单一入口**：业务代码从 `@/api` 或 `@/services` 导入，不从深层路径直接导入 `apiFactory`
- [ ] **Barrel Export**：新增 api / service 模块已加入对应 `index.ts`
- [ ] **Token 管理**：认证相关操作通过 `apiService` 拦截器处理，不手动拼接 `Authorization` header

## B. 组件与引用

- [ ] **路径规范**：跨目录引用使用 `@/` 别名（如 `@/components/common/PageHeader`），不使用 `../../`
- [ ] **Barrel Export**：新增 `common` / `settings` / `dict` 组件已加入对应目录的 `index.ts`
- [ ] **无循环引用**：组件间不存在循环 import
- [ ] **分层合规**：`components` 不引用 `views`，`models` 不引用 `services`
- [ ] **View 后缀合规**：新增页面级组件必须以 `View` 结尾（如 `CombatLogListView.vue`）
- [ ] **目录命名一致性**：新增组件目录优先使用 **camelCase**（与现有 `buildParser/`, `eiDetail/` 保持一致），避免混用 kebab-case

## C. 样式与 CSS

- [ ] **单一入口**：未新增 CSS 文件入口（如 `import 'xxx.css'` 或 `<style src="xxx">`）
- [ ] **变量统一**：新增 CSS 变量已加入 `src/styles/variablesUnified.css`
- [ ] **Tailwind 合规**：未在 PrimeVue 覆盖样式中重复添加 `@tailwind` 指令
- [ ] **主题合规**：组件颜色使用 CSS 变量（`var(--primary-500)`），不硬编码色值

## D. 类型与分层

- [ ] **类型位置正确**：DTO 类型放在 `api` 或 `models`，全局类型放在 `src/types`
- [ ] **无反向依赖**：`types` / `models` 层未从 `services` / `api` 层导入
- [ ] **核心类型统一**：`ApiResponse` / `ApiError` 等基础设施类型从 `@/types/api` 导入

## E. 主题与 PrimeVue

- [ ] **预设一致**：PrimeVue 组件使用 `GameThemePreset`（Aura 游戏主题预设）
- [ ] **darkModeSelector**：PrimeVue 配置使用 `darkModeSelector: ':root'`（与 CSS 变量系统一致）
- [ ] **主题初始化**：如需在应用创建前初始化主题，使用 `ThemeService.initialize()`

## F. 状态管理

- [ ] **Pinia 风格**：新增 Store 使用 Composition API 风格（`defineStore('id', () => { ... })`）
- [ ] **持久化规范**：需持久化的状态使用 `ref` + `watch` + `localStorage`，不直接操作 Storage
- [ ] **权限状态**：权限检查使用 `usePermission()` 组合式函数或 `authStore` 单例，不直接读取 localStorage

## G. 安全与错误处理

- [ ] **错误处理**：API 调用有适当的错误捕获和提示
- [ ] **401 处理**：不手动处理 401 跳转，由 `apiService` 响应拦截器统一处理

## H. 构建验证

- [ ] **构建通过**：执行 `npm run build` 或 `npx vite build` 无错误
- [ ] **类型检查**：执行 `npx vue-tsc --noEmit` 无类型错误

---

## 审查流程

1. 提交者对照本清单逐项自检，全部勾选后方可提交
2. 审查者重点检查 **A（API）**、**B（组件引用）** 和 **C（样式）** 类项目
3. 发现违规项时，在 PR 评论中引用本清单对应条目编号
