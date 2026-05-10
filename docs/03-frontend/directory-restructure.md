# 前端项目目录结构整理说明

> 整理日期：2026-05-10
> 范围：`frontend/src/` 下所有散落文件及微型目录
> 原则：最小侵入、功能不变、引用安全

---

## 一、背景与目标

在第二轮细分审查完成后，对 `frontend/src/` 进行了全面梳理，发现以下结构性问题：

1. **根目录散落文件**：`update-references.ps1` 脚本直接放在 `src/` 根下
2. **微型目录冗余**：`constants/`（3个文件）、`data/`（2个文件）职责与其他目录重叠
3. **文件未按模块归类**：composable、store、utils 文件散落在父目录根级
4. **命名不规范**：`utils/attendance/formatters.ts` 命名过于泛化
5. **职责混淆**：`layout/components/topNav/useTopNav.ts` 是 composable 却放在组件目录内
6. **疑似死代码**：`data/mockEiData.ts`、`composables/useAuthGuard.ts`、`store/eiData.ts` 无外部引用

本次整理旨在消除上述问题，建立清晰、一致的目录层级结构。

---

## 二、新旧目录对比

### 2.1 src/ 根目录变化

```diff
  frontend/src/
+ ├── composables/core/
+ ├── composables/layout/
+ ├── store/ei/
- ├── constants/
- ├── data/
- ├── update-references.ps1
- ├── composables/useAuthGuard.ts
- ├── store/eiData.ts
- ├── utils/skillIcons.ts
```

### 2.2 核心迁移记录

| 原路径 | 新路径 | 操作类型 | 引用影响 |
|--------|--------|----------|----------|
| `src/update-references.ps1` | `frontend/scripts/update-references.ps1` | 移动 | 无 |
| `src/constants/apiEndpoints.ts` | `src/config/apiEndpoints.ts` | 移动 | 28 个文件更新 |
| `src/constants/themes.ts` | `src/config/themes.ts` | 移动 | 5 个文件更新 |
| `src/constants/designTokens.ts` | `src/styles/designTokens.ts` | 移动 | 无引用 |
| `src/data/builds.json` | `src/assets/data/builds.json` | 移动 | 无引用 |
| `src/data/mockEiData.ts` | — | **删除** | 无引用 |
| `src/composables/useAuthGuard.ts` | `src/composables/core/useAuthGuard.ts` | 移动 | 无引用 |
| `src/store/eiData.ts` | `src/store/ei/eiData.ts` | 移动 | `store/modules.ts` 更新 |
| `src/utils/skillIcons.ts` | `src/utils/profession/skillIcons.ts` | 移动 | 1 个文件更新 |
| `src/layout/components/topNav/useTopNav.ts` | `src/composables/layout/useTopNav.ts` | 移动 | 2 个文件更新 |
| `src/utils/attendance/formatters.ts` | 合并至 `attendanceFormatters.ts` | **删除** | 3 个文件更新 |

---

## 三、引用路径更新清单

### 3.1 批量替换（PowerShell 全局替换）

| 旧路径 | 新路径 | 受影响文件数 |
|--------|--------|-------------|
| `@/constants/apiEndpoints` | `@/config/apiEndpoints` | 28 |
| `@/constants/themes` | `@/config/themes` | 5 |
| `@/utils/skillIcons` | `@/utils/profession/skillIcons` | 1 |

### 3.2 手动更新

| 文件 | 旧引用 | 新引用 |
|------|--------|--------|
| `store/modules.ts` | `./eiData` | `./ei/eiData` |
| `layout/components/topNav/index.vue` | `./useTopNav` | `@/composables/layout/useTopNav` |
| `layout/components/topNav/MobileMenu.vue` | `./useTopNav` | `@/composables/layout/useTopNav` |
| `composables/attendance/useDataAttendance.ts` | `@/utils/attendance/formatters` | `@/utils/attendance/attendanceFormatters` |
| `components/attendance/AttendanceTable.vue` | `@/utils/attendance/formatters` | `@/utils/attendance/attendanceFormatters` |
| `components/attendance/AttendanceStatCards.vue` | `@/utils/attendance/formatters` | `@/utils/attendance/attendanceFormatters` |

---

## 四、代码去重

### `utils/attendance/formatters.ts` 合并说明

原 `utils/attendance/` 下存在两个高度重叠的格式化文件：

- **`attendanceFormatters.ts`**：`formatDateTime`、`formatNumber`、`formatDps`、`formatDuration`、`getProfessionLabel`、`getScoreColor`
- **`formatters.ts`**：`formatDateParam`、`formatDate`、`formatNumber`、`formatDuration`

**处理方案**：
1. 将 `formatters.ts` 独有的 `formatDateParam`、`formatDate` 合并到 `attendanceFormatters.ts`
2. `formatNumber`、`formatDuration` 两者实现完全一致，保留 `attendanceFormatters.ts` 中的版本
3. 删除 `formatters.ts`

---

## 五、清理的空目录

- `frontend/src/constants/` — 所有文件已迁移至 `config/` 和 `styles/`
- `frontend/src/data/` — `builds.json` 移至 `assets/data/`，`mockEiData.ts` 删除

---

## 六、验证结果

### 6.1 残留引用扫描

对以下旧路径进行全局扫描，确认 **零残留**：

- `@/constants/` ✅ 0 处
- `@/data/` ✅ 0 处
- `@/utils/skillIcons` ✅ 0 处
- `./useTopNav`（相对路径）✅ 0 处
- `@/utils/attendance/formatters` ✅ 0 处

### 6.2 模块解析验证

运行 `npx vue-tsc --noEmit` 检查模块解析：
- **无新增** `Cannot find module` 或 `TS2307` 错误 ✅
- 项目中存在的类型错误为**整理前已存在**，与本次目录调整无关

### 6.3 构建验证

运行 `npm run build`：
- 无新增模块找不到错误 ✅
- 构建报错均为整理前已存在的类型问题（`Unterminated string literal` 等）

---

## 七、整理后目录结构（src 根级）

```
frontend/src/
├── api/              # API 请求层（按模块）
├── App.vue           # 根组件
├── assets/           # 静态资源
│   ├── data/         # 静态 JSON 数据（新增）
│   ├── fonts/
│   ├── icons/
│   └── images/
├── components/       # 组件（按模块）
│   ├── ai/
│   ├── attendance/
│   ├── build/
│   ├── combat/
│   ├── common/
│   ├── dashboard/
│   ├── log/
│   ├── settings/
│   ├── system/
│   ├── test/
│   └── index.ts
├── composables/      # 组合式函数（按模块）
│   ├── attendance/
│   ├── auth/
│   ├── build/
│   ├── combat/
│   ├── common/
│   ├── core/         # 通用守卫等
│   ├── data/
│   ├── layout/       # 布局相关 composable
│   ├── log/
│   ├── settings/
│   ├── system/
│   └── test/
├── config/           # 配置文件（新增 apiEndpoints.ts、themes.ts）
│   ├── app.config.ts
│   ├── apiEndpoints.ts
│   ├── storage.config.ts
│   ├── themePreset.ts
│   └── themes.ts
├── directive/        # 自定义指令
├── layout/           # 布局组件
├── locales/          # 国际化
├── main.ts           # 入口
├── models/           # 数据模型
├── router/           # 路由
├── services/         # 业务服务层
├── store/            # 状态管理
│   ├── build/
│   ├── ei/           # 新增
│   ├── system/
│   ├── index.ts
│   └── modules.ts
├── styles/           # 全局样式（新增 designTokens.ts）
├── types/            # 全局类型定义
├── utils/            # 工具函数
│   ├── attendance/
│   ├── auth/
│   ├── build/
│   ├── cache/
│   ├── combat/
│   ├── core/
│   ├── error/
│   ├── events/
│   ├── log/
│   ├── mock/
│   ├── permission/
│   ├── profession/   # 新增 skillIcons.ts
│   ├── theme/
│   └── timer/
├── views/            # 页面视图
└── vite-env.d.ts
```

---

## 八、补充整理（CSS 归位与 designTokens 迁移）

在首轮整理完成后，进一步审查发现以下问题并修复：

### 8.1 `styles/` 目录中的 `.ts` 混放

`styles/designTokens.ts` 是一个 TypeScript 常量文件，不应放在纯 CSS 目录中。

| 原路径 | 新路径 |
|--------|--------|
| `styles/designTokens.ts` | `config/designTokens.ts` |

### 8.2 散落在组件/布局/视图目录中的 `.css` 文件

以下独立 CSS 文件被迁移至 `styles/` 下对应模块目录：

| 原路径 | 新路径 |
|--------|--------|
| `components/build/library/BuildFilterSidebar.css` | `styles/components/build/BuildFilterSidebar.css` |
| `components/combat/PlayerDetailPanel.css` | `styles/components/combat/PlayerDetailPanel.css` |
| `components/combat/SkillRotationTimeline.css` | `styles/components/combat/SkillRotationTimeline.css` |
| `components/common/dictionary/DictionaryManagementWrapper.css` | `styles/components/common/dictionary/DictionaryManagementWrapper.css` |
| `layout/components/topNav/topNav.css` | `styles/layouts/topNav.css` |
| `views/auth/LoginView.css` | `styles/views/auth/LoginView.css` |
| `views/build/BuildSkillRotationView.css` | `styles/views/build/BuildSkillRotationView.css` |

### 8.3 单文件目录 `directive/` 合并

`directive/permission.ts` 仅含一个文件，不符合"单一职责目录"原则，迁移至 `composables/system/usePermissionDirective.ts`。

---

## 九、当前目录纯度验证

| 目录 | 主要类型 | 混放检查 |
|------|----------|----------|
| `api/` | `.ts` | ✅ 纯净 |
| `assets/` | `.png/.svg/.json` + `icons/index.ts` | ✅ 资源索引例外 |
| `components/` | `.vue` + `index.ts` | ✅ barrel export 例外 |
| `composables/` | `.ts` | ✅ 纯净 |
| `config/` | `.ts` | ✅ 纯净 |
| `layout/` | `.vue` | ✅ 纯净 |
| `locales/` | `.ts` | ✅ 纯净 |
| `models/` | `.ts` | ✅ 纯净 |
| `router/` | `.ts` | ✅ 纯净 |
| `services/` | `.ts` | ✅ 纯净 |
| `store/` | `.ts` | ✅ 纯净 |
| `styles/` | `.css` | ✅ 纯净 |
| `types/` | `.ts` | ✅ 纯净 |
| `utils/` | `.ts` | ✅ 纯净 |
| `views/` | `.vue` | ✅ 纯净 |

---

## 十、后续建议

1. **修复预存在类型错误**：`api/build/skills.ts`、`composables/combat/useCombatLogDetail.ts` 等文件中存在字符串未闭合等语法错误，建议优先修复
2. **统一命名规范**：建议所有 barrel export 文件统一使用 `index.ts` 命名，并确保各模块目录下都有清晰的 `index.ts`
3. **持续监控**：后续新增文件时应遵循 `src/README.md` 中的目录规范，避免再次产生散落文件
