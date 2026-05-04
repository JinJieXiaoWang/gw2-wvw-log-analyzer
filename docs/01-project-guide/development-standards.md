# GW2 WVW 日志解析管理系统 - 开发规范指南
> **版本**: v3.0  
> **更新日期**: 2026-05-05  
> **责任人*: 帅姐姐 
> **整合来源**: CODING_STANDARDS.md, CSS_MANAGEMENT.md, Component-Guide.md, THEME_SYSTEM_GUIDE.md, architecture-guide.md

## 版本变更记录

| 版本 | 日期 | 变更内容 | 责任人|
|------|------|----------|--------|
| v3.0 | 2026-05-05 | 同步实际代码架构：更新技术栈（PrimeVue Aura、Axios 封装层）、目录结构（新增 api/、models/、directive/ 等）、命名规范（View 后缀、Store 命名、API 类命名）、CSS 唯一变量源（variablesUnified.css）、入口流程、约束清单；记录目录命名不一致问题| 帅姐姐|
| v2.0 | 2026-05-01 | 整合编码规范、CSS 管理、组件指南、主题系统为统一开发规范| 帅姐姐|

---

## 目录

1. [编码规范](#一编码规范)
2. [CSS 管理](#二css-管理)
3. [主题系统](#三主题系组
4. [组件指南](#四组件指南
5. [最佳实践总结](#五最佳实践总结)
6. [版本历史](#六版本历变

---

## 一、编码规范
### 1. 项目概览与技术栈

本项目是一个基于Vue 3 + TypeScript + Vite + Tailwind CSS + PrimeVue（Aura 预设）的前端应用，用于管理和分析激成 (GW2) WVW 战场日志数据、
- **框架**: Vue 3 (Composition API，`<script setup lang="ts">`)
- **语言**: TypeScript（严格模式）
- **构建工具**: Vite
- **样式**: Tailwind CSS (`darkMode: 'class'`) + 自定义CSS
- **UI 组件应*: PrimeVue（Aura 预设）- **状态管理*: Pinia（Composition API 风格（ 自定义AuthStore 类（面Pinia）- **路由**: Vue Router（`createRouter` + `createWebHistory`）- **HTTP 客户立*: Axios（通过 `ApiFactory` / `HttpClient` 封装于`services/core/apiService.ts`）- **路径别名**: `@/` 指向 `src/`

### 2. TypeScript 规范

#### 2.1 类型定义
- 使用 `interface` 定义对象类型
- 使用 `type` 定义联合类型、交叉类型等
- 为所本API 响应和核心数据结构创建类型定义- 避免使用 `any` 类型，使用更具体的类型或泛型

#### 2.2 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 变量/函数 | camelCase | `getUserList`, `isLoading` |
| 接口 | PascalCase | `UserProfile`, `ApiResponse` |
| 类型别名 | PascalCase | `ThemeId`, `LogFilter` |
| 常量 | UPPER_CASE_WITH_UNDERSCORES | `API_ENDPOINTS`, `MAX_PAGE_SIZE` |
| 枚举 | PascalCase（枚举值全大写）| `enum Status { ACTIVE = 'active' }` |
| Vue SFC | PascalCase | `EmptyState.vue`, `DashboardView.vue` |
| 组合式函数| camelCase + `use` 前缀 | `useTheme.ts`, `useAuth.ts` |
| Store 文件 | `use` + PascalCase + `Store` | `useSettingsStore.ts` |
| 服务类| PascalCase + `Service` 后缀 | `AuthService` |
| 服务实例 | camelCase + `Service` 后缀 | `authService` |
| API 类| PascalCase + `Api` 后缀 | `AuthApi` |
| 页面组件 | PascalCase + `View` 后缀 | `DashboardView.vue`, `LogManagementView.vue` |
| CSS 类名 | kebab-case | `.action-btn`, `.game-card` |
| CSS 变量 | kebab-case | `--color-primary`, `--space-4` |

#### 2.3 代码风格
- 缩进: 2 个空格（一Vue 3 官方规范一致）
- 分号: 不使用分号（一TypeScript 官方推荐一致）
- 引号: 单引变(`'`)
- 大括变 与语句在同一行- 行长应 每行不超迁120 个字第
### 3. Vue 组件规范

#### 3.1 组件结构
- **文件命名**: PascalCase (`.vue`)
- **组件命名**: PascalCase
- **脚本设置**: 使用 `<script setup lang="ts">`
- **模板**: 使用 HTML 风格的标签（小写+连字符）

#### 3.2 组件组织
- **组件拆分**: 按功能拆分组件，保持单个组件职责单一
- **Props 定义**: 使用 TypeScript 类型定义 Props
- **Emits 定义**: 使用 TypeScript 类型定义事件
- **组件注释**: 为组件添加功能、Props、Emits 说明

#### 3.3 组合弃API 使用
- **导入顺序**: 按`vue` 内置 API、第三方库、本地文件顺序导充- **响应式变重*: 使用 `ref()` 和`reactive()` 合理管理状性- **计算属性*: 使用 `computed()` 处理派生状性- **生命周期**: 优先使用 `onMounted()` 等组合式 API 钩子

### 4. 代码结构规范

#### 4.1 目录结构

```
src/
├── api/                  # 原始 API 层（按领域分目录：ai, auth, build, combat, data, system（─  └── index.ts          # Barrel export
├── assets/               # 静态资源（fonts, images（├── components/           # 组件（按功能模块分目录）
─  ├── common/           # 基础公共组件（BaseDialog, BaseState, EmptyState, ErrorState, LoadingState, PageHeader, etc.（─  ├── aiAnalysis/       # AI 分析组件
─  ├── attendance/       # 出勤统计组件
─  ├── build-library/    # Build 图书馆组件（kebab-case（─  ├── buildParser/      # Build 解析组件（camelCase）⚠️命名不一自─  ├── dashboard/        # 数据看板组件
─  ├── dict/             # 字典组件
─  ├── eiDetail/         # EI 详情页组件─  ├── logManagement/    # 日志管理组件
─  ├── settings/         # 设置页组件─  ├── skillRotation/    # 技能循环组件─  ├── system/           # 系统组件
─  ├── theme/            # 主题组件
─  └── wvwReport/        # WVW 报告组件
├── composables/          # 组合式函数（core/, system/（├── config/               # 配置文件（themePreset.ts（├── constants/            # 常量定义（apiEndpoints.ts, designTokens.ts, themes.ts（├── data/                 # 静态数据├── directive/            # 自定义指令（permission.ts（├── layout/               # 页面布局（MainLayout / LoginLayout / components/（├── models/               # 领域模型类型（按领域分目录+ index.ts barrel export（├── router/               # 路由配置（index.ts + permissionGuard.ts（├── services/             # 业务服务层（core/ + 按领域分目录 + index.ts barrel export（─  ├── core/             # 核心基础设施（apiService.ts, errorHandler.ts, mockData.ts（─  └── index.ts          # Barrel export
├── store/                # Pinia 状态管理─  ├── index.ts          # Pinia 入口
─  ├── modules.ts        # 模块注册
─  ├── system/settings.ts # 系统设置（Composition API 风格，localStorage 持久化）
─  ├── eiData.ts         # EI 日志数据状性─  └── build/buildLibrary.ts # Build 图书馆状性├── styles/               # 样式系统
─  ├── index.css         # 唯一 CSS 入口
─  ├── base.css          # Tailwind 指令 + 基础样式
─  ├── variablesUnified.css # 统一 CSS 变量系统（55 行，唯一变量源）
─  ├── components/       # 组件通用样式
─  ├── layouts/          # 布局样式
─  ├── primevue/         # PrimeVue 组件覆盖
─  └── utilities/        # 工具类+ 动画
├── types/                # TypeScript 全局类型（api.ts, build.ts, eliteInsights.ts, permission.ts + index.ts（├── utils/                # 工具函数
─  ├── auth/             # 认证相关
─  ├── core/             # 核心工具
─  ├── error/            # 错误处理
─  ├── mock/             # Mock 数据
─  ├── permission/       # 权限工具
─  ├── profession/       # 职业相关
─  ├── theme/            # 主题工具
─  └── skillIcons.ts     # 技能图样├── views/                # 页面组件（按业务模块分组（─  ├── auth/             # 认证模块
─  ├── build/            # Build 配置模块
─  ├── combat/           # 战斗日志分析模块
─  ├── data/             # 数据统计分析模块
─  ├── error/            # 错误页面
─  ├── system/           # 系统管理模块
─  └── test/             # 测试工具
├── App.vue               # 根组件└── main.ts               # 应用入口
```

> **注意**: `components/` 下子目录命名存在不一致：`build-library`（kebab-case）vs `buildParser`（camelCase）。新增目录建议统一使用 kebab-case、
#### 4.2 文件组织
- **API 服务**: 按功能模块拆分API 调用
- **组件**: 按功能和复用性组织组件- **类型定义**: 集中管理核心数据类型
- **工具函数**: 按功能分类组织工具函数
### 5. 注释规范

#### 5.1 文件头部注释
```typescript
/**
 * 组件/模块名称
 * 功能：详细描述组件模块的功能 * 作者：作者姓名 * 创建日期：YYYY-MM-DD
 * 更新日期：YYYY-MM-DD
 */
```

#### 5.2 函数注释
```typescript
/**
 * 函数名称
 * 功能：详细描述函数功能 * 参数：参数名1 - 类型 - 描述；参数名2 - 类型 - 描述
 * 返回：返回值类型- 描述
 * 异常：可能抛出的异常
 */
```

#### 5.3 代码注释
- 复杂逻辑添加行内注释
- 关键业务逻辑添加块注重- 注释使用中文，保持简洁明了
### 6. 样式规范（基础）
#### 6.1 Tailwind CSS 使用
- 优先使用 Tailwind 内置类- 合理使用自定义工具类
- 避免过度嵌套和复杂类名
#### 6.2 自定义样弃- 按功能模块组织自定义样式
- 使用 `@layer` 组织样式层级
- 避免使用 `!important`
- 使用 CSS 变量管理颜色和尺对
#### 6.3 命名规范
- **类名**: 使用 kebab-case
- **变量名*: 使用 kebab-case
- **选择器*: 避免使用 ID 选择器- **BEM 规范**: 对于复杂组件，使用BEM 命名注
> 详见第二立[CSS 管理](#二css-管理) 了解完整的样式目录结构、设计令牌管理和实施步骤、
### 7. 工具配置

#### 7.1 ESLint 配置
- 遵循 Vue 3 官方推荐的ESLint 配置
- 使用 TypeScript ESLint 插件
- 配置合理的规则集

#### 7.2 Prettier 配置
- 使用 Prettier 自动格式化代码- 一ESLint 配置保持一自- 配置合理的格式化规则

#### 7.3 TypeScript 配置
- 启用严格模式 (`strict: true`)
- 配置合理的编译选项
- 定义自定义类型路径别名
### 8. 版本控制

#### 8.1 Git 规范
- 使用语义化版本号
- 提交信息遵循约定式提交规范- 分支管理遵循 Git Flow 工作测- 定期进行代码审查

#### 8.2 提交信息格式
```
<type>(<scope>): <subject>

<body>

<footer>
```

**类型**:
- `feat`: 新功能- `fix`: 修复 bug
- `docs`: 文档更新
- `style`: 代码风格调整
- `refactor`: 代码重构
- `test`: 测试代码
- `chore`: 构建过程或辅助工具的变动

### 9. 团队协作

#### 9.1 代码审查
- 定期进行代码审查
- 关注代码质量和安全性- 提供建设性的反馈
- 确保代码符合规范

#### 9.2 文档维护
- 及时更新文档
- 保持文档与代码同步- 编写清晰的API 文档
- 提供使用示例

#### 9.3 知识共享
- 定期进行技术分享- 建立技术知识库
- 记录常见问题和解决方档- 分享最佳实路
---

## 二、CSS 管理

### 1. 核心策略

- **唯一入口**: `src/main.ts` 一`import './styles/index.css'` 为唯一 CSS 入口
- **唯一变量源*: `styles/variablesUnified.css`（55 行）为唯一 CSS 变量源- **Tailwind 优先**: 优先使用 Tailwind CSS 内置类- **自定义样式模块化**: 将自定义样式按功能拆分- **设计令牌集中管理**: 集中管理颜色、尺寸等设计令牌
- **组件样式隔离**: 组件级样式使用scoped 成CSS Modules
- **PrimeVue 样式统一管理**: 统一管理 PrimeVue 组件样式覆盖

**禁止**：- ❌在Vue 组件一`import 'xxx.css'` 或使用`<style src="xxx">`
- ❌在`index.html` 中引入本在CSS 文件
- ❌在CSS 子文件中 `@import` 其他变量文件

### 2. 目录结构设计

```
src/
├── styles/
─  ├── index.css          # 唯一样式入口文件
─  ├── variablesUnified.css # 统一 CSS 变量系统（唯一变量源，355 行）
─  ├── base.css           # 基础样式（Tailwind 指令（─  ├── components/        # 组件样式
─  ├── layouts/           # 布局样式
─  ├── utilities/         # 工具类+ 动画
─  └── primevue/          # PrimeVue 样式覆盖
└── ...
```

### 3. 样式组织方式

#### 3.1 设计令牌管理

**`styles/variablesUnified.css`**（唯一变量源）:

- 主色调：`#165DFF`
- 辅助色：`#FF7D00`
- AI 专属色：`#00E5C0`
- 深色游戏风格背景：`#0D0D0F`
- PrimeVue/Aura 变量桥接：`--p-primary-*`, `--p-surface-*`
- 支持 `:root.dark` / `:root.light` 主题切换
- 自定义阴影：`shadow-glow-primary`, `shadow-glow-ai`
- 自定义动画：`fade-in`, `slide-up`, `pulse-glow`

所有新增CSS 变量必须定义在`variablesUnified.css` 的`:root` 中，并在 `tailwind.config.js` 中同步、
#### 3.2 基础样式

**`styles/base.css`**:
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }
  
  body {
    font-family: var(--font-family);
    background: var(--color-bg);
    color: var(--color-text);
    line-height: 1.5;
    min-height: 100vh;
  }
  
  /* 其他基础样式 */
}
```

#### 3.3 组件样式

**`styles/components/*.css`**:
```css
@layer components {
  .btn {
    @apply relative inline-flex items-center justify-center gap-2 font-medium rounded-lg;
    @apply px-5 py-2.5 text-sm;
    @apply transition-all duration-200 ease-out;
  }
  
  .btn-primary {
    @apply btn bg-primary text-white shadow-sm;
    box-shadow: 0 0 20px rgba(22, 93, 255, 0.3);
  }
  
  .btn-secondary {
    @apply btn bg-secondary text-white shadow-sm;
    box-shadow: 0 0 20px rgba(255, 125, 0, 0.3);
  }
  
  /* 其他按钮样式 */
}
```

#### 3.4 布局样式

**`styles/layouts/*.css`**:
```css
.main-layout {
  @apply min-h-screen flex flex-col;
}

.main-content {
  @apply flex-1 p-6;
}

/* 其他布局样式 */
```

#### 3.5 工具类
**`styles/utilities/*.css`**:
```css
@keyframes slideInUp {
  from {
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.animate-slide-in-up {
  animation: slideInUp 0.4s ease-out;
}

/* 其他动画 */
```

#### 3.6 PrimeVue 样式覆盖

**`styles/primevue/*.css`**:
```css
.p-dialog {
  @apply rounded-xl border border-neutral-border;
  background: var(--color-card);
  box-shadow: var(--shadow-xl);
}

.p-dialog .p-dialog-header {
  @apply bg-neutral-card border-b border-neutral-border;
  @apply text-neutral-text;
}

/* 其他 PrimeVue 组件样式覆盖 */
```

#### 3.7 样式入口文件

**`styles/index.css`**:
```css
/* 统一变量系统（唯一变量源） */
@import './variablesUnified.css';

/* 基础样式 */
@import './base.css';

/* 布局样式 */
@import './layouts/main.css';
@import './layouts/page.css';

/* 组件样式 */
@import './components/buttons.css';
@import './components/cards.css';
@import './components/tables.css';
@import './components/forms.css';

/* 工具类*/
@import './utilities/animations.css';
@import './utilities/typography.css';
@import './utilities/layout.css';

/* PrimeVue 样式覆盖 */
@import './primevue/index.css';
```

### 4. 命名规范

#### 4.1 类名命名

- **BEM 规范**: 对于复杂组件，使用BEM 命名注  ```css
  .block {
    /* 块*/
  }
  
  .block__element {
    /* 元素 */
  }
  
  .block--modifier {
    /* 修饰第*/
  }
  ```

- **kebab-case**: 类名使用小写字母和连字符
  ```css
  .btn-primary {}
  .card-legendary {}
  .nav-link-active {}
  ```

- **语义化命名*: 类名应反映其功能，而不是样弃  ```css
  /* 好的命名 */
  .btn-primary {}
  .card-interactive {}
  
  /* 不好的命名*/
  .red-button {}
  .big-card {}
  ```

#### 4.2 CSS 变量命名

- **kebab-case**: 变量名使用小写字母和连字第  ```css
  --color-primary: #165DFF;
  --space-4: 1rem;
  --radius-lg: 0.75rem;
  ```

- **分类命名**: 按功能分类命名变重  ```css
  /* 颜色 */
  --color-primary: #165DFF;
  
  /* 间距 */
  --space-4: 1rem;
  
  /* 圆角 */
  --radius-lg: 0.75rem;
  ```

### 5. 实施步骤

#### 5.1 准备阶段

1. **创建样式目录结构**
   - 创建 `src/styles` 目录
   - 创建子目录：`components`, `layouts`, `utilities`, `primevue`

2. **拆分现有样式**
   - 将样式按功能拆分到对应文件   - 提取设计令牌分`variablesUnified.css`
   - 拆分基础样式分`base.css`
   - 拆分组件样式分`components/` 目录
   - 拆分布局样式分`layouts/` 目录
   - 拆分工具类到 `utilities/` 目录
   - 拆分 PrimeVue 样式覆盖分`primevue/` 目录

3. **创建样式入口文件**
   - 创建 `styles/index.css`
   - 按顺序导入所有样式文件
#### 5.2 迁移阶段

1. **更新主入口文件*
   - 修改 `main.ts` 中的样式导入一`import './styles/index.css'`

2. **清理组件样式**
   - 移除组件中的重复样式
   - 对于需要组件级样式的组件，使用 `scoped` 成CSS Modules
   - 优先使用 Tailwind 类和全局组件样式

3. **测试样式效果**
   - 确保所有页面样式正常显示   - 确保响应式布局正常工作
   - 确保动画效果正常

#### 5.3 优化阶段

1. **性能优化**
   - 移除未使用的样式
   - 优化 CSS 选择器   - 减少样式文件大小

2. **可维护性优化*
   - 添加样式文档
   - 优化样式组织
   - 统一命名规范

3. **最佳实践应用*
   - 应用 CSS 最佳实路   - 确保样式一致性   - 提高样式可扩展性
### 6. 最佳实路
#### 6.1 Tailwind CSS 使用

- **优先使用 Tailwind 内置类*
  ```vue
  <!-- 好的做法 -->
  <div class="flex items-center justify-between p-4 bg-neutral-card rounded-lg">
    <!-- 内容 -->
  </div>
  
  <!-- 不好的做注-->
  <div class="card-header">
    <!-- 内容 -->
  </div>
  <style scoped>
  .card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem;
    background: var(--color-card);
    border-radius: 0.75rem;
  }
  </style>
  ```

- **合理使用自定义工具类**
  ```css
  @layer utilities {
    .text-gradient-primary {
      background: linear-gradient(135deg, var(--color-primary), var(--color-primary-light));
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }
  }
  ```

#### 6.2 组件样式隔离

- **使用 scoped 样式**
  ```vue
  <template>
    <div class="custom-component">
      <!-- 内容 -->
    </div>
  </template>
  
  <style scoped>
  .custom-component {
    /* 组件级样弃*/
  }
  </style>
  ```

- **使用 CSS Modules**（可选）
  ```vue
  <template>
    <div :class="styles.customComponent">
      <!-- 内容 -->
    </div>
  </template>
  
  <script setup lang="ts">
  import styles from './CustomComponent.module.css'
  </script>
  ```

#### 6.3 样式组织

- **按功能组织样弃*
  - 将相关样式放在同一文件一  - 使用清晰的文件命名  - 保持样式文件大小合理

- **使用 @layer 组织样式**
  ```css
  @layer base {
    /* 基础样式 */
  }
  
  @layer components {
    /* 组件样式 */
  }
  
  @layer utilities {
    /* 工具类*/
  }
  ```

#### 6.4 响应式设计
- **使用 Tailwind 响应式类**
  ```vue
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
    <!-- 内容 -->
  </div>
  ```

- **合理使用媒体查询**
  ```css
  @media (max-width: 640px) {
    .sm\:hidden {
      display: none;
    }
  }
  ```

#### 6.5 性能优化

- **避免过度嵌套**
  ```css
  /* 好的做法 */
  .btn-primary {}
  .btn-primary:hover {}
  
  /* 不好的做注*/
  .btn {
    &-primary {
      &:hover {
        /* 样式 */
      }
    }
  }
  ```

- **使用 CSS 变量**
  ```css
  /* 好的做法 */
  .btn-primary {
    background: var(--color-primary);
  }
  
  /* 不好的做注*/
  .btn-primary {
    background: #165DFF;
  }
  ```

- **减少使用 !important**
  ```css
  /* 避免使用 */
  .btn-primary {
    background: #165DFF !important;
  }
  ```

---

## 三、主题系组
### 1. 核心架构

```
┌───────────────────────────────────────────────────────────────                     表现局(Vue 组件)                     ──             使用 Tailwind 工具类+ PrimeVue            ─└──────────────────────┬──────────────────────────────────────                       ─┌──────────────────────▼───────────────────────────────────────                  CSS 变量桥接局                   ──         统一变量系统: 游戏风格 →PrimeVue Aura    ──             variablesUnified.css (唯一变量源       ─└──────────────────────┬──────────────────────────────────────                       ─┌──────────────────────▼───────────────────────────────────────                  主题配置局                        ──        ThemeService + GameThemes 常量配置        ─└──────────────────────────────────────────────────────────────```

### 2. 快速开姐
#### 2.1 在Vue 组件中使用主题
```vue
<template>
  <!-- 使用 Tailwind 工具类- 自动响应主题切换 -->
  <div class="game-card p-6">
    <h1 class="text-2xl font-bold text-neutral-text">欢迎</h1>
    <p class="text-neutral-text-secondary">游戏风格主题已启用/p>
    
    <!-- PrimeVue 组件 - 自动应用主题 -->
    <Button class="mt-4" @click="doSomething">
      点击成    </Button>
  </div>
</template>

<script setup lang="ts">
import { Button } from 'primevue/button';

function doSomething() {
  console.log('主题系统正常工作!');
}
</script>
```

#### 2.2 编程式切换主题
```vue
<template>
  <div class="flex gap-3">
    <Button 
      v-for="theme in allThemes" 
      :key="theme.id"
      :label="theme.name"
      @click="changeTheme(theme.id)"
    />
  </div>
</template>

<script setup lang="ts">
import { ThemeService } from '@/services/themeService';
import { GameThemes } from '@/constants/themes';

const allThemes = GameThemes;

async function changeTheme(themeId: string) {
  await ThemeService.applyTheme(themeId);
}
</script>
```

### 3. 色彩系统

#### 3.1 主色调
- `--color-primary` / `primary`: 电竞蓝(#165DFF)
- `--color-primary-light`: 亮蓝
- `--color-primary-dark`: 深蓝

#### 3.2 辅助色
- `--color-secondary` / `secondary`: 橙红 (#FF7D00)

#### 3.3 中性色

- `--color-bg`: 背景色(#0D0D0F)
- `--color-card`: 卡片色(#1A1A1F)
- `--color-border`: 边框色(#2D2D35)
- `--color-text`: 文本色(#F0F0F5)

#### 3.4 状态色

- `success`: 绿色
- `warning`: 黄色
- `error`: 红色
- `info`: 蓝色
- `ai`: 科技面(#00E5C0)

### 4. Tailwind 工具类
#### 4.1 游戏风格工具类
```css
.game-card           /* 游戏风格卡片 */
.game-btn-primary    /* 主按钮*/
.game-btn-secondary  /* 次要按钮 */
.game-input          /* 输入档*/
.game-tag            /* 标签 */
.game-glow           /* 发光效果 */
.game-lift           /* 悬浮提升 */
```

#### 4.2 主题响应工具类
```html
<!-- 使用CSS变量的工具类 - 自动响应主题切换 -->
<div class="bg-neutral-card text-neutral-text border border-neutral-border">
  自动响应主题的内定</div>
```

### 5. PrimeVue 组件集成

所本PrimeVue 组件都已通过 `src/styles/primevue/index.css` 进行了游戏风格覆盖，无需额外配置即可使用、
### 6. 添加新主题
#### 6.1 在constants/themes.ts 中添加配置
```typescript
{
  id: 'dark-void',
  name: '虚空暗黑',
  description: '深邃的太空主题,
  icon: 'pi-star',
  previewGradient: 'linear-gradient(135deg, #0a0a15 0%, #151530 50%, #0f0f20 100%)',
  preset: 'aura',
  colors: {
    primary: '#6366f1',
    primaryLight: '#818cf8',
    primaryDark: '#4f46e5',
    secondary: '#f59e0b',
    secondaryLight: '#fbbf24',
    secondaryDark: '#d97706',
    bg: '#0a0a15',
    bgSecondary: '#0f0f20',
    card: '#151530',
    cardHover: '#1a1a40',
    border: '#2a2a50',
    borderLight: '#3a3a60',
    text: '#e0e0ff',
    textSecondary: '#a0a0c0',
    textDisabled: '#606080',
    textInverse: '#0a0a15',
    success: '#10b981',
    warning: '#f59e0b',
    error: '#ef4444',
    info: '#3b82f6',
    ai: '#06b6d4'
  }
}
```

### 7. 性能优化

#### 7.1 主题切换优化

- 使用 CSS 变量而非 DOM 操作
- 批量更新变量值- 添加防抖动机分- 使用硬件加速的过渡动画

#### 7.2 滚动性能

```css
.game-scrollbar {
  /* 优化滚动条性能 */
}
```

---

## 四、组件指南
### 1. EmptyState - 空状态组件
展示数据为空时的界面状态，提供友好的提示信息和可能的操作、
#### 1.1 基本使用

```vue
<template>
  <EmptyState
    icon="pi pi-inbox"
    title="暂无数据"
    description="请上传日志文件开始分构
    :show-action="true"
    action-text="上传文件"
    @action="handleUpload"
  />
</template>

<script setup>
import EmptyState from '@/components/common/EmptyState.vue'

const handleUpload = () => {
  // 处理上传操作
}
</script>
```

#### 1.2 属性(Props)

| 属性| 类型 | 默认值| 说明 |
|------|------|--------|------|
| icon | string | 'pi pi-inbox' | 显示的图标类名|
| title | string | '暂无数据' | 标题文本 |
| description | string | '' | 描述文本 |
| showAction | boolean | false | 是否显示操作按钮 |
| actionText | string | '添加数据' | 操作按钮文本 |

#### 1.3 事件 (Events)

| 事件名| 参数 | 说明 |
|--------|------|------|
| action | - | 点击操作按钮时触变|

#### 1.4 插槽 (Slots)

| 插槽名| 说明 |
|--------|------|
| actions | 自定义操作按钮区基|

#### 1.5 高级用法

```vue
<template>
  <EmptyState
    title="没有找到匹配的日志
    description="尝试调整筛选条件或清除搜索"
  >
    <template #actions>
      <Button label="清除筛通 class="btn-game" outlined @click="clearFilters" />
      <Button label="重新搜索" class="btn-game" @click="reSearch" />
    </template>
  </EmptyState>
</template>
```

---

### 2. ErrorState - 错误状态组件
展示错误信息的组件，提供重试和返回首页等操作、
#### 2.1 基本使用

```vue
<template>
  <ErrorState
    title="加载失败"
    message="网络连接异常，请检查网络后重试"
    :show-retry="true"
    :show-home="true"
    @retry="handleRetry"
    @home="goHome"
  />
</template>

<script setup>
import ErrorState from '@/components/common/ErrorState.vue'
</script>
```

#### 2.2 属性(Props)

| 属性| 类型 | 默认值| 说明 |
|------|------|--------|------|
| title | string | '加载失败' | 错误标题 |
| message | string | '发生错误，请稍后重试' | 错误信息 |
| showRetry | boolean | true | 是否显示重试按钮 |
| showHome | boolean | true | 是否显示返回首页按钮 |
| retryText | string | '重试' | 重试按钮文本 |
| homeText | string | '返回首页' | 返回首页按钮文本 |

#### 2.3 事件 (Events)

| 事件名| 参数 | 说明 |
|--------|------|------|
| retry | - | 点击重试按钮时触变|
| home | - | 点击返回首页按钮时触变|

---

### 3. LoadingState - 加载状态组件
展示数据加载中的状态、
#### 3.1 基本使用

```vue
<template>
  <LoadingState text="正在加载数据..." :size="40" />
</template>

<script setup>
import LoadingState from '@/components/common/LoadingState.vue'
</script>
```

#### 3.2 属性(Props)

| 属性| 类型 | 默认值| 说明 |
|------|------|--------|------|
| text | string | '' | 加载提示文本 |
| size | number | 32 | 加载图标大小（像素） |

---

### 4. 操作列按钮样弃
操作列是数据表格中的重要组成部分，用于提供对每行数据的查看、编辑、删除等操作。本规范定义了操作列按钮的样式标准和使用方法、
#### 4.1 样式定义

**基础按钮类*:
```css
.action-btn {
  @apply relative inline-flex items-center justify-center;
  @apply w-8 h-8 rounded-lg text-neutral-text-secondary;
  @apply transition-all duration-200 ease-out;
  @apply hover:text-neutral-text;
}
```

**按钮变体**:
```css
/* 查看按钮 */
.action-btn-view:hover {
  @apply bg-primary/15 text-primary;
}

/* 编辑/修改按钮 */
.action-btn-edit:hover {
  @apply bg-secondary/15 text-secondary;
}

/* 下载按钮 */
.action-btn-download:hover {
  @apply bg-status-success/15 text-status-success;
}

/* 解析按钮 */
.action-btn-parse:hover {
  @apply bg-secondary/15 text-secondary;
}

/* 删除按钮 */
.action-btn-delete:hover {
  @apply bg-status-error/15 text-status-error;
}
```

**尺寸变体**:
```css
/* 小型按钮 */
.action-btn-sm {
  @apply w-7 h-7 text-sm;
}

/* 大型按钮 */
.action-btn-lg {
  @apply w-10 h-10 text-base;
}
```

**操作列容器*:
```css
.table-actions {
  @apply flex items-center gap-3;
}
```

#### 4.2 类名说明

| 类名 | 说明 | Hover 效果 |
|------|------|-----------|
| `.action-btn` | 基础按钮类| 文本颜色变为 `neutral-text` |
| `.action-btn-view` | 查看按钮 | 背景 `primary/15`，文存`primary` |
| `.action-btn-edit` | 编辑按钮 | 背景 `secondary/15`，文存`secondary` |
| `.action-btn-download` | 下载按钮 | 背景 `status-success/15`，文存`status-success` |
| `.action-btn-parse` | 解析按钮 | 背景 `secondary/15`，文存`secondary` |
| `.action-btn-delete` | 删除按钮 | 背景 `status-error/15`，文存`status-error` |

#### 4.3 使用方法

```vue
<template>
  <Column header="操作" style="min-width: 200px">
    <template #body="{ data }">
      <div class="table-actions flex items-center gap-3">
        <Button
          v-tooltip.top="'查看'"
          icon="pi pi-eye"
          size="small"
          text
          class="action-btn action-btn-view"
          @click="viewItem(data)"
        />
        <Button
          v-tooltip.top="'编辑'"
          icon="pi pi-pencil"
          size="small"
          text
          class="action-btn action-btn-edit"
          @click="editItem(data)"
        />
        <Button
          v-tooltip.top="'删除'"
          icon="pi pi-trash"
          size="small"
          text
          class="action-btn action-btn-delete"
          @click="deleteItem(data)"
        />
      </div>
    </template>
  </Column>
</template>
```

#### 4.4 尺寸变体

```vue
<Button class="action-btn action-btn-sm" /> <!-- 小型 -->
<Button class="action-btn" /> <!-- 默认 -->
<Button class="action-btn action-btn-lg" /> <!-- 大型 -->
```

#### 4.5 禁用状性
```vue
<Button 
  class="action-btn action-btn-view" 
  :disabled="!canView"
/>
```

#### 4.6 PrimeVue 组件适配

```css
.p-datatable .p-button {
  @apply border-none;
}

.p-datatable .p-button.p-button-text {
  @apply text-neutral-text-secondary hover:text-neutral-text;
}

.p-datatable .p-button.p-button-text:hover {
  @apply bg-neutral-card;
}
```

复选框样式:
```css
.p-datatable .p-checkbox {
  @apply border-neutral-border bg-neutral-bg;
}

.p-datatable .p-checkbox.p-highlight {
  @apply border-primary bg-primary;
}

.p-datatable .p-checkbox .p-checkbox-icon {
  @apply text-white;
}
```

#### 4.7 响应式考虑

操作列应保证在不同屏幕尺寸下的良好显示效果：

```vue
<Column header="操作" style="min-width: 200px">
  <template #body="{ data }">
    <div class="table-actions flex items-center gap-2 sm:gap-3">
      <!-- 按钮 -->
    </div>
  </template>
</Column>
```

#### 4.8 可访问性
- 使用合适的图标和tooltip 提示
- 确保按钮有适当的contrast ratio
- 使用语义化的标签和描迁
```vue
<Button
  v-tooltip.top="'删除记录'"
  aria-label="删除记录"
  icon="pi pi-trash"
  class="action-btn action-btn-delete"
/>
```

---

### 5. 游戏风格按钮 (.btn-game)

项目中所有主要按钮都应该使用 `.btn-game` 类，以保持一致的游戏风格外观、
```vue
<template>
  <!-- 默认按钮 -->
  <Button class="btn-game" label="提交" />
  
  <!-- 次要按钮 -->
  <Button class="btn-game" outlined label="取消" />
  
  <!-- 带图标的按钮 -->
  <Button class="btn-game" icon="pi pi-upload" label="上传" />
  
  <!-- 仅图标按钮-->
  <Button class="btn-game" icon="pi pi-refresh" />
</template>
```

---

### 6. PrimeVue DataTable 配置

推荐的DataTable 配置）
```vue
<template>
  <DataTable
    v-model:selection="selectedItems"
    :value="data"
    :loading="loading"
    data-key="id"
    :paginator="true"
    :rows="10"
    :rows-per-page-options="[10, 20, 50]"
    striped-rows
    removable-sort
    class="w-full"
  >
    <!-- 复选框分-->
    <Column selection-mode="multiple" header-style="width: 3rem" />
    
    <!-- 数据分-->
    <Column field="name" header="名称" sortable />
    
    <!-- 操作分-->
    <Column
      header="操作"
      style="min-width: 200px"
      header-style="width: 200px"
    >
      <template #body="{ data }">
        <div class="table-actions flex items-center gap-3">
          <!-- 操作按钮 -->
        </div>
      </template>
    </Column>
    
    <!-- 空状性-->
    <template #empty>
      <EmptyState description="暂无数据" />
    </template>
  </DataTable>
</template>
```

---

### 7. 完整页面示例

#### 7.1 数据管理页面模板

```vue
<template>
  <div class="container px-4 py-6">
    <!-- 页面标题和操使-->
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold text-neutral-text">数据管理</h1>
      <div class="flex items-center gap-3">
        <Button class="btn-game" icon="pi pi-refresh" @click="refreshData" />
        <Button class="btn-game" icon="pi pi-plus" label="添加" @click="addItem" />
      </div>
    </div>

    <!-- 数据表格 -->
    <DataTable
      v-model:selection="selectedItems"
      :value="data"
      :loading="loading"
      data-key="id"
      :paginator="true"
      :rows="10"
      :rows-per-page-options="[10, 20, 50]"
      striped-rows
      removable-sort
      class="w-full"
    >
      <Column selection-mode="multiple" header-style="width: 3rem" />
      
      <Column field="name" header="名称" sortable />
      <Column field="status" header="状性 sortable>
        <template #body="{ data }">
          <span class="game-badge" :class="getStatusClass(data.status)">
            {{ data.statusText }}
          </span>
        </template>
      </Column>
      <Column field="createdAt" header="创建时间" sortable />
      
      <Column
        header="操作"
        style="min-width: 200px"
        header-style="width: 200px"
      >
        <template #body="{ data }">
          <div class="table-actions flex items-center gap-3">
            <Button
              v-tooltip.top="'查看'"
              icon="pi pi-eye"
              size="small"
              text
              class="action-btn action-btn-view"
              @click="viewItem(data)"
            />
            <Button
              v-tooltip.top="'编辑'"
              icon="pi pi-pencil"
              size="small"
              text
              class="action-btn action-btn-edit"
              @click="editItem(data)"
            />
            <Button
              v-tooltip.top="'删除'"
              icon="pi pi-trash"
              size="small"
              text
              class="action-btn action-btn-delete"
              @click="deleteItem(data)"
            />
          </div>
        </template>
      </Column>
      
      <template #empty>
        <EmptyState
          title="暂无数据"
          description="添加新的数据开始使用
          :show-action="true"
          action-text="添加数据"
          @action="addItem"
        />
      </template>
    </DataTable>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import EmptyState from '@/components/common/EmptyState.vue'

const data = ref<any[]>([])
const selectedItems = ref<any[]>([])
const loading = ref(false)

const refreshData = async () => {
  loading.value = true
  try {
    // 加载数据
  } finally {
    loading.value = false
  }
}

const addItem = () => {
  // 添加新项
}

const viewItem = (item: any) => {
  // 查看详情
}

const editItem = (item: any) => {
  // 编辑项}

const deleteItem = (item: any) => {
  // 删除项}

const getStatusClass = (status: string) => {
  return status === 'active' ? 'game-badge-success' : 'game-badge-warning'
}

onMounted(() => {
  refreshData()
})
</script>
```

---

### 8. 常见问题

#### Q: 如何自定义操作按钮的颜色：A: 使用 `.action-btn-*` 变体类，如果需要自定义颜色，创建新的变体类并在 `buttons.css` 中添加样式、
#### Q: 如何在不同主题间切换：A: 使用 `ThemeService` 成`ThemeSwitcher` 组件，项目已内置主题系统。详见第三章 [主题系统](#三主题系组、
#### Q: 状态组件如何与路由结合使用：A: 在页面组件中通过条件渲染显示不同的状态组件，根据数据加载状态动态切换、
#### Q: 游戏徽章和标准徽章有什么区别？
A: 游戏徽章 (`.game-badge-*`) 具有渐变背景、光泽效果和脉冲动画，更符合游戏数据工具的视觉风格；标准徽章 (`.badge-*`) 更简洁，适合常规应用场景。推荐使用游戏徽章、
#### Q: 如何创建自定义的徽章变体：A: 在`badges.css` 中添加新的徽章类，遵循现有的命名约定和样式模式，确保与主题变量保持一致、
---

## 五、最佳实践总结

本章节汇总了来自编码规范、CSS 管理、主题系统和组件指南的最佳实践，供开发者在日常工作中快速参考、
### 1. 性能优化

#### Vue 性能
- 使用 `v-memo` 缓存计算结果
- 合理使用 `v-for` 的`key` 属性- 避免在模板中进行复杂计算
- 使用 `defineAsyncComponent` 懒加载组件- 按需加载大型组件，使用动态导充- 合理使用 `v-if` 和`v-show`，避免过度重组- 对于长列表使用虚拟滚动（PrimeVue 支持）- 处理用户输入时使用防报节流

#### CSS 性能
- 避免过度嵌套 CSS 选择器- 使用 CSS 变量管理颜色，避免硬编码
- 减少使用 `!important`
- 移除未使用的样式，优化选择器- 减少样式文件大小

#### 主题切换性能
- 使用 CSS 变量而非 DOM 操作实现主题切换
- 批量更新变量值- 添加防抖动机分- 使用硬件加速的过渡动画

### 2. 可维护性
- 保持组件职责单一
- 使用组合式函数复用逻辑
- 合理使用 Pinia 管理全局状性- 统一错误处理机制
- 按功能模块拆分API 调用和样式文件- 使用 `@layer` 组织样式层级
- 保持样式文件大小合理，清晰的文件命名

### 3. 代码质量

- 定期运行 `npm run lint` 检查代码规范- 定期运行 `npm run type-check` 检查类型错说- 编写清晰的单元测说- 保持代码风格一自- 为组件和函数编写清晰的注重- 及时更新文档，保持文档与代码同步

### 4. 安全性
- 避免 XSS 攻击，使用`v-html` 时要谨慎
- 对用户输入进行验说- 合理使用 HTTPS
- 保护敏感信息

### 5. CSS / Tailwind 最佳实路
- **优先使用 Tailwind 内置类*，减少自定义 CSS
- 按功能模块组织自定义样式
- 使用 CSS 变量管理颜色和尺对- 类名使用 kebab-case，语义化命名
- 复杂组件使用 BEM 命名注- 避免使用 ID 选择器- 组件级样式使用`scoped` 成CSS Modules
- 使用 Tailwind 响应式类处理适配

### 6. 主题系统最佳实路
- **优先使用 CSS 变量**：不要硬编码颜色值- **使用 Tailwind 工具类*：减少自定义 CSS
- **PrimeVue 组件优先**：利用已覆盖的组件- **保持主题切换流畅**：避免在主题切换时进行繁重计管- **使用渐变透明应*：通过 `primary-alpha-10` 等类实现

### 7. 组件使用原则

- **复用通用组件**：优先使用EmptyState、ErrorState、LoadingState 等通用组件
- **保持一致性*：同一类型的功能使用相同的组件和样弃- **语义化*：使用合适的组件表达正确的UI 状性- **响应弃*：确保组件在不同屏幕尺寸下正常显示- **统一组件样式**：使用项目预定义的组件类（如 `.btn-game`, `.action-btn`）- **避免内联样式**：除非必要，不使用内联样弃- **使用主题变量**：通过 CSS 变量访问主题颜色

### 8. 版本控制与协使
- 提交信息遵循约定式提交规范- 分支管理遵循 Git Flow 工作测- 定期进行代码审查
- 提供建设性的反馈
- 建立技术知识库，记录常见问题和解决方案
- 定期进行技术分享
---

## 六、版本历变
### 整合前版本记录
| 版本 | 日期 | 来源文档 | 变更内容 | 责任人|
|------|------|----------|----------|--------|
| v1.2 | 2026-04-29 | CSS_MANAGEMENT.md | 新增徽章样式系统、操作列按钮样式规范 | 帅姐姐|
| v1.1 | 2026-04-29 | CODING_STANDARDS.md | 编码标准文档更新 | 帅姐姐|
| v1.1 | 2026-04-29 | Component-Guide.md | 初始版本，包含状态组件和操作按钮样式指南 | 帅姐姐|
| v1.1 | 2026-04-25 | CSS_MANAGEMENT.md | 添加操作列按钮样式规范章节| 帅姐姐|
| v1.0 | 2026-04-15 | CSS_MANAGEMENT.md | 初始版本，CSS 管理系统实施方案 | 帅姐姐|

### 整合后版本记录
| 版本 | 日期 | 变更内容 | 责任人|
|------|------|----------|--------|
| v3.0 | 2026-05-05 | 同步实际代码架构：更新技术栈、目录结构、命名规范（View 后缀、Store 命名、API 类命名）、CSS 唯一变量源（variablesUnified.css）、入口流程、约束清单；记录目录命名不一致问题| 帅姐姐|
| v2.0 | 2026-05-01 | 整合编码规范、CSS 管理、组件指南、主题系统为统一开发规范文档| 帅姐姐|
