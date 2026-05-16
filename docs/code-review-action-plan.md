# 代码审查整改行动计划

> **审查日期**: 2026-05-12
> **依据文档**: `docs/项目规则.md`、`docs/01-project-guide/development-standards.md`、`docs/01-specifications/frontend-backend-conventions.md`、`docs/03-frontend/directory-restructure.md`、`docs/COMPONENTS_GUIDE.md`
> **审查范围**: 全项目前后端代码库

---

## 一、问题总览

| 优先级 | 问题类别 | 涉及文件数 | 风险等级 |
|--------|---------|-----------|---------|
| **P0** | 编译阻断/系统稳定性 | 15+ | 🔴 致命 |
| **P1** | 架构违规/安全缺陷 | 60+ | 🟠 严重 |
| **P2** | 规范偏差/质量债务 | 80+ | 🟡 中等 |
| **P3** | 优化改进/风格统一 | 50+ | 🟢 轻微 |

---

## 二、P0 级整改 — 立即执行（1-2 天）

> **判定标准**: 导致编译失败、运行时崩溃、数据不一致或安全漏洞，必须立即修复。

### 2.1 前端类型系统断裂（编译阻断）

| 模块 | 问题描述 | 影响 | 实施复杂度 |
|------|---------|------|-----------|
| `src/types/permission.ts` | `AuthState` 接口缺少 `menus: MenuItem[]`、`currentRole`、`currentUser` 等字段 | 10+ 文件编译失败 | 低 |
| `src/composables/system/usePermission.ts` | 返回值未暴露 `isAdmin`、`isOperator`、`isSuperAdmin`，但大量调用方解构使用 | 权限系统失效 | 低 |
| `src/composables/layout/useTopNav.ts` | `MenuItem` 类型仅在此文件定义，未被全局导出 | 类型引用失败 | 低 |
| `src/services/professionService.ts` | API 响应类型为 `{}`，访问 `data` 字段报错 | 职业管理功能异常 | 低 |

**整改方案**:
1. 在 `src/types/permission.ts` 中补全 `AuthState` 接口定义
2. 在 `src/types/layout.ts` 中全局定义 `MenuItem` 类型
3. 在 `usePermission()` 中暴露缺失的计算属性
4. 修正 `professionService.ts` 的 API 响应类型为 `ApiResponse<T>`

### 2.2 前端语法错误

| 文件 | 问题描述 | 影响 |
|------|---------|------|
| `src/api/build/skills.ts` | 字符串未闭合 | 构建失败 |
| `src/composables/combat/useCombatLogDetail.ts` | 字符串未闭合等语法错误 | 构建失败 |

**整改方案**: 逐行修复字符串引号闭合问题，运行 `npx vue-tsc --noEmit` 验证。

### 2.3 后端 SyntaxWarning

| 文件 | 问题描述 | 影响 |
|------|---------|------|
| `scripts/import_gw2_txt_builds.py:12` | 非法转义序列 `\C` | 运行时警告 |
| `scripts/test_json_initializer.py:7` | 非法转义序列 `\C` | 运行时警告 |

**整改方案**: 路径字符串前加 `r` 前缀（如 `r"D:\Code\..."`）。

### 2.4 样式系统违规（重复导入）

| 文件 | 问题描述 | 影响 |
|------|---------|------|
| `frontend/src/styles/components/buttons.css` | 重复 `@import '../variablesUnified.css'` | CSS变量重复定义，潜在冲突 |
| `frontend/src/styles/components/cards.css` | 同上 | 同上 |
| `frontend/src/styles/components/forms.css` | 同上 | 同上 |
| `frontend/src/styles/components/gameMenu.css` | 同上 + 存在 UTF-8 乱码 `样�?` | 同上 + 乱码 |
| `frontend/src/main.ts` | 存在 3 个 CSS/样式导入，非唯一入口 | 违反样式入口唯一性 |
| `frontend/index.html` | 引入外部 Google Fonts CSS | 违反样式入口唯一性 |

**整改方案**:
1. 删除 4 个 CSS 子文件中的 `@import '../variablesUnified.css'`
2. 修复 `gameMenu.css` 中的乱码字符
3. 将 `main.ts` 中的 `@primeuix/themes/aura` 和 `primeicons/primeicons.css` 通过 `index.css` 统一聚合引入
4. 将 Google Fonts 移至 `base.css` 中以 `@import` 或 `@font-face` 方式本地化管理

### 2.5 重复/残留文件（导致维护混乱）

| 重复/残留文件 | 保留文件 | 操作 |
|--------------|---------|------|
| `src/constants/apiEndpoints.ts` | `src/config/apiEndpoints.ts` | 删除 constants 版本，批量更新 25+ 个引用 |
| `src/constants/designTokens.ts` | `src/config/designTokens.ts` | 删除 constants 版本 |
| `src/constants/themes.ts` | `src/config/themes.ts` | 删除 constants 版本 |
| `src/constants/combatConstants.ts` | — | 删除（零引用） |
| `src/constants/scoringConstants.ts` | — | 删除（零引用） |
| `src/data/mockEiData.ts` | `src/utils/mock/mockEiData.ts` | 删除 data 版本 |
| `src/data/builds.json` | — | 确认是否已迁移至 `assets/data/`，删除残留 |
| `src/composables/useAuthGuard.ts` | `src/composables/core/useAuthGuard.ts` | 删除根目录版本 |
| `src/store/eiData.ts` | `src/store/ei/eiData.ts` | 删除旧版本，更新 `store/modules.ts` 引用 |

**整改方案**: 先确认保留版本功能完整，然后删除重复/残留文件，批量更新引用路径。

---

## 三、P1 级整改 — 高优先级（第 1 周）

> **判定标准**: 严重违反架构分层、安全规范或导致可维护性急剧下降，但不阻断编译。

### 3.1 后端路由层写业务逻辑（最严重架构违规）

| 文件 | 行数 | 违规内容 | 风险等级 |
|------|------|---------|---------|
| `app/routers/logs.py` | **633行** | 含 `_ProgressStore`、`_do_parse_log`（83行）、文件操作、CSV导出、DB操作 | 🔴 |
| `app/routers/users.py` | **354行** | 用户CRUD、密码哈希、权限判断、DB操作 | 🔴 |
| `app/routers/professions.py` | **460行** | 完整业务逻辑、裸参数 `Dict[str, Any]` | 🔴 |
| `app/routers/dict_data.py` | **277行** | 级联查询直接DB操作 | 🟠 |
| `app/routers/scoring_rules.py` | **391行** | 硬编码业务数据、版本管理逻辑 | 🟠 |
| `app/routers/auth.py` | **193行** | `change_password` 直接DB操作、Service实例化 | 🟠 |
| `app/routers/batch_parse.py` | **182行** | DB查询直接写在路由 | 🟠 |
| `app/routers/storage.py` | **222行** | 内嵌 `run_cleanup()` 含 `SessionLocal()` | 🟠 |

**整改方案**:
1. **`logs.py` 拆分**（最紧急）:
   - 拆分为 `logs_upload.py`、`logs_parse.py`、`logs_export.py`
   - `_ProgressStore` → `app/services/zevtc/parse_progress_service.py`
   - `_do_parse_log` → `app/services/zevtc/log_service.py`，拆分为子函数
   - 所有 `db.query()`/`db.commit()` 下沉至 `LogService`
   - 文件操作下沉至 `FileService`
2. **`users.py` 拆分**:
   - 拆分为 `users_admin.py`、`users_profile.py`
   - 所有CRUD下沉至 `UserService`
   - 密码哈希移至 `auth_service`
3. **`professions.py` 拆分**:
   - 拆分为查询和写操作路由
   - 裸参数 `Dict[str, Any]` 改为 Pydantic 模型
4. 其他文件：同理将DB操作和业务逻辑下沉至对应 Service

### 3.2 后端路由文件超标

| 文件 | 行数 | 超标倍数 | 拆分建议 |
|------|------|---------|---------|
| `app/routers/logs.py` | 633 | 3.2x | `logs_upload.py` + `logs_parse.py` + `logs_export.py` |
| `app/routers/professions.py` | 460 | 2.3x | `professions_query.py` + `professions_admin.py` |
| `app/routers/scoring_rules.py` | 391 | 2.0x | `scoring_rules_crud.py` + `scoring_rules_version.py` |
| `app/routers/users.py` | 354 | 1.8x | `users_admin.py` + `users_profile.py` |
| `app/routers/dashboard.py` | 270 | 1.4x | 按模块拆分 |
| `app/routers/attendance.py` | 250 | 1.3x | `attendance_accounts.py` + `attendance_filters.py` |
| `app/routers/menus.py` | 249 | 1.2x | 拆分菜单CRUD和树形查询 |
| `app/routers/scoring.py` | 241 | 1.2x | 拆分实时评分与重算任务 |
| `app/routers/storage.py` | 222 | 1.1x | `storage_monitor.py` + `storage_cleanup.py` |
| `app/routers/test_dps_report.py` | 201 | 1.0x | `test_dps_upload.py` + `test_dps_parse.py` |

### 3.3 前端超大 Vue 文件（页面 >350 / 组件 >250）

| 文件 | 行数 | 类型 | 拆分建议 |
|------|------|------|---------|
| `views/combat/CombatLogDetailView.vue` | **2304** | 页面 | 拆分为 8-10 个组件 |
| `views/settings/ScoringRulesView.vue` | **1488** | 页面 | 拆分为 5-6 个组件 |
| `components/eiDetail/PlayerDetailModal.vue` | **1194** | 业务组件 | 拆分为 4 个标签页组件 |
| `views/data/AttendanceDetailView.vue` | **992** | 页面 | 拆分为 5-6 个组件 |
| `layout/components/topNav/index.vue` | **901** | 布局组件 | 拆分为 NavLogo/Search/Notification/UserMenu |
| `components/attendance/AttendanceDetail.vue` | **873** | 业务组件 | 拆分为 Header/Calendar/Table/Grid |
| `components/eiDetail/StatsView.vue` | **847** | 业务组件 | 拆分为 ChartSection/TableSection |
| `components/settings/ScoringRulesSettings.vue` | **727** | 业务组件 | 拆分为 List/Form/Preview |
| `components/settings/SystemParamsSettings.vue` | **706** | 业务组件 | 按参数类别拆分 |
| `components/eiDetail/HealingExtension.vue` | **699** | 业务组件 | 拆分为 Overview/Table/Chart |

**整改方案**:
1. 对超过 **800 行**的 7 个文件优先拆分
2. 按"语义拆分"原则，<50 行 UI 不单独拆组件
3. 页面私有子组件控制在 3-5 个以内
4. 组件嵌套最多 2 层
5. 拆分后原文件仅做组装逻辑

### 3.4 前端 Template 严重违规

| 违规类型 | 涉及文件数 | 严重程度 |
|---------|-----------|---------|
| 标签嵌套 >3 层 | **28/28** 超大文件 | 🔴 所有审查文件均超标 |
| 行内样式 `style="..."` | 22/28 | 🟠 |
| class >80 字符未换行 | 18/28 | 🟡 |
| 直接使用 PrimeVue 原生标签 | 15/28 | 🟡 |

**整改方案**:
1. 标签嵌套：通过拆分组件降低嵌套深度
2. 行内样式：全部改为 Tailwind 原子类或 CSS 变量
3. class过长：超过80字符必须换行；重复组合抽取为常量或子组件
4. PrimeVue原生标签：替换为已二次封装的 BaseButton/BaseDialog/BaseSelect/BaseTag 等

### 3.5 main.py Router 注册问题

| 问题 | 文件 | 影响 |
|------|------|------|
| `database_management.py` 未注册 | `main.py` | 接口完全不可访问 |
| `memory_monitor` 未加 `API_PREFIX` | `main.py:190` | 路径不一致 |
| `monitoring` prefix 重复 | `app/routers/monitoring.py` | 实际路径 `/api/v1/api/v1/monitoring/` |

**整改方案**:
1. 在 `main.py` 中注册 `database_management` router
2. 统一 `memory_monitor` 的 prefix 处理
3. 移除 `monitoring.py` 中的硬编码 `/api/v1` prefix

---

## 四、P2 级整改 — 中优先级（第 2-3 周）

> **判定标准**: 违反编码规范、影响代码质量，但不影响功能运行。

### 4.1 硬编码配置（安全/维护风险）

| 文件 | 硬编码内容 | 整改方式 |
|------|-----------|---------|
| `app/routers/logs.py:64` | `UPLOAD_DIR = "./uploads"` | 移至 `settings.py` |
| `app/routers/logs.py:17` | `MAX_CONCURRENT_PARSE = 3` | 移至 `settings.py` |
| `app/routers/test_dps_report.py:20-21` | `DPS_REPORT_UPLOAD_URL` / `DPS_REPORT_JSON_URL` | 移至 `settings.py` |
| `app/routers/settings.py` | 三套默认设置重复定义 | 统一使用 `DEFAULT_SETTINGS` 常量 |
| `app/routers/scoring_rules.py` | `ROLE_DESCRIPTIONS`、评分维度硬编码 | 移至 service 或配置 |
| `app/routers/users.py` | 角色列表硬编码 | 从数据库或配置读取 |
| `app/routers/config.py` | `supported_formats`、`theme_default` | 从 `settings.py` 读取 |
| `src/services/professionService.ts:68` | `API_PREFIX = '/professions'` | 统一收拢到 `config/apiEndpoints.ts` |

### 4.2 后端业务文件超标（>400行）

| 文件 | 行数 | 拆分建议 |
|------|------|---------|
| `app/services/zevtc/log_import_service.py` | **1042** | 拆分为 parser/player/fight 子模块 |
| `app/services/menu_service.py` | **885** | 拆分为 tree/crud 子模块 |
| `app/services/zevtc/attendance_service.py` | **830** | 拆分为 query/account/score 子模块 |
| `app/services/zevtc/batch_parse_service.py` | **752** | 拆分为 task/item/scheduler 子模块 |
| `app/services/game_data/game_data_service.py` | **714** | 按数据类别拆分 |
| `app/services/system/dictionary_service.py` | **699** | 拆分接口/缓存/CRUD |
| `app/services/system/dashboard_service.py` | **577** | 按 KPI/趋势/分布拆分 |
| `app/services/game_data/bdcode_service.py` | **525** | 拆分数据加载/查询 |
| `app/services/zevtc/parser_service.py` | **525** | 拆分解析/转换 |
| `app/services/ei/unified_service.py` | **507** | 拆分构建/同步 |
| `app/services/scoring_rule_service.py` | **500** | 拆分CRUD/版本/计算 |
| `app/services/wvw/scoring_service.py` | **491** | 拆分计算/重算/查询 |
| `app/services/ei/report_service.py` | **481** | 拆分摘要/导入/导出 |

### 4.3 后端超大函数（>80行）

| 文件 | 函数 | 行数 | 整改 |
|------|------|------|------|
| `menu_service.py:565` | `init_default_menus` | **322** | 提取菜单数据为配置/JSON |
| `attendance_service.py:140` | `get_account_detail` | **247** | 拆分为查询/统计/聚合 |
| `database.py:452` | `_sync_table_columns` | **222** | 拆分 |
| `log_import_service.py:495` | `_insert_players` | **215** | 拆分 |
| `log_import_service.py:134` | `import_log` | **142** | 拆分 |
| `fight_service.py:94` | `get_log_player_stats` | **144** | 拆分 |
| `ei/unified_service.py:246` | `_build_ei_player` | **155** | 拆分 |

### 4.4 前端死代码清理

| 代码 | 状态 | 操作 |
|------|------|------|
| `src/models/` 目录（594行，50+接口） | 零引用 | 整体删除，或迁移 services/ 中的接口定义至此 |
| `src/utils/core/helpers.ts` 中 12 个函数 | 零引用 | 删除未使用函数 |
| `src/constants/combatConstants.ts` | 零引用 | 删除 |
| `src/constants/scoringConstants.ts` | 零引用 | 删除 |
| `src/store/eiData.ts:164` | 废弃注释 | 删除 |

### 4.5 响应格式不统一

| 文件 | 问题 | 整改 |
|------|------|------|
| `app/routers/memory_monitor.py` | 全部返回 bare dict | 统一使用 `ApiResponse` |
| `app/routers/config.py` | 返回 bare dict | 统一使用 `ApiResponse.success_response()` |
| `app/routers/bdcode.py` | 使用 `HTTPException` | 改用自定义异常 |

### 4.6 Pydantic 模型位置违规

| 文件 | 模型 | 应移至 |
|------|------|--------|
| `app/routers/ei_analysis.py` | `SkillMapItem`、`PlayerRotationResponse` | `app/schemas/combat_analysis.py` |
| `app/routers/settings.py` | `SettingsUpdateRequest`、`SettingsItem` | `app/schemas/settings.py` |
| `app/routers/test_dps_report.py` | `DpsReportTestResponse` | `app/schemas/test_tools.py` |
| `app/routers/monitoring.py` | `BenchmarkRequest`、`BenchmarkResult` | 删除或补全接口 |

### 4.7 前端 any 类型滥用

| 文件 | 问题 | 整改 |
|------|------|------|
| `src/composables/combat/useCombatLogDetail.ts` | `(a: any, b: any)`、`events: any[]` 等 | 补充具体类型 |
| `src/services/combat/combatAnalysisService.ts` | `convertKeysToCamelCase(obj: any): any` | 使用泛型 |
| `src/services/combat/wvwReportService.ts` | `convertObjectKeys(obj: any): any` | 使用泛型 |
| `src/utils/core/performance.ts` | `(...args: any[]) => any` | 使用泛型 |
| `src/api/build/skills.ts` | `Promise<any \| null>` | 补充响应类型 |

---

## 五、P3 级整改 — 低优先级（第 3-4 周及以后）

> **判定标准**: 风格不一致、轻微优化，可逐步推进。

### 5.1 代码风格统一

| 文件 | 问题 | 整改 |
|------|------|------|
| `src/utils/core/helpers.ts` | 77个分号，4空格缩进 | 统一为2空格、无分号 |
| `src/store/eiData.ts` | 大量分号 | 统一风格 |
| `src/utils/core/performance.ts` | 大量分号 | 统一风格 |
| `src/services/core/apiService.ts` | 大量分号 | 统一风格 |

### 5.2 ESLint 配置升级

| 问题 | 整改 |
|------|------|
| 使用 `.eslintrc.json` 传统配置 | 迁移至 `eslint.config.js` 扁平配置 |

### 5.3 主题系统完善

| 问题 | 整改 |
|------|------|
| Tailwind `darkMode: 'class'` 与 PrimeVue `:root` 机制不一致 | 统一暗色模式切换机制 |
| `themes.ts` 定义多主题但 `main.ts` 硬编码单主题 | 完成多主题切换功能，或移除未使用的主题配置 |

### 5.4 未使用导入清理

| 范围 | 数量 |
|------|------|
| 后端 routers/ 文件 | 18 个文件存在未使用导入 |
| 前端 services/、composables/ 文件 | 抽样发现 10+ 个文件 |

**整改方案**: 使用 ESLint `no-unused-vars` 规则自动检测并清理。

### 5.5 前端 defineModel 迁移

| 文件 | 当前写法 | 目标写法 |
|------|---------|---------|
| `components/eiDetail/StatsView.vue` | `emit('update:xxx')` | `defineModel<T>()` |
| 其他少量文件 | `props + emit` | `defineModel<T>()` |

### 5.6 前端 Props 数量控制

| 文件 | Props数量 | 整改 |
|------|----------|------|
| `components/eiDetail/StatsView.vue` | 7个 | 合并或拆分至 ≤6 |

### 5.7 分层污染整改

| 问题 | 整改 |
|------|------|
| `services/` 下内联定义 155+ 个接口 | 逐步迁移至 `api/` 或 `models/` |
| `api/system/dictionary.ts` 是 re-export 而非 API 层 | 补充真实 API 调用或删除 |
| `utils/profession/dictMapping.ts` 混入业务逻辑 | 评估是否应移至 composables/ |
| `utils/theme/imageColorUtils.ts` 混入主题业务逻辑 | 评估是否应移至 services/ |

---

## 六、实施顺序建议

### 阶段一：止血（Day 1-2）
1. ✅ 修复前端类型系统断裂（P0）
2. ✅ 修复前端语法错误（P0）
3. ✅ 修复后端 SyntaxWarning（P0）
4. ✅ 清理重复/残留文件（P0）
5. ✅ 修复样式系统重复导入和乱码（P0）
6. ✅ 运行前后端构建验证

### 阶段二：架构整改（Week 1）
1. 🔧 后端：`logs.py` 业务逻辑下沉至 service 层（P1最高优先级）
2. 🔧 后端：`users.py`、`professions.py` 业务逻辑下沉（P1）
3. 🔧 后端：拆分超标路由文件（P1）
4. 🔧 前端：拆分超过 800 行的 7 个超大文件（P1）
5. 🔧 前后端：统一响应格式、修复裸响应（P1/P2）
6. 🔧 修复 `main.py` router 注册缺失（P1）

### 阶段三：规范落地（Week 2-3）
1. 📐 前端：修复行内样式、class过长、标签嵌套（P1/P2）
2. 📐 后端：迁移 Pydantic 模型至 schemas/（P2）
3. 📐 后端：硬编码配置集中化（P2）
4. 📐 后端：拆分超标业务文件（P2）
5. 📐 后端：拆分超大函数（P2）
6. 📐 前端：清理死代码（models/、helpers.ts零引用函数）（P2）
7. 📐 前端：限制 any 类型使用（P2）

### 阶段四：质量优化（Week 3-4及以后）
1. 🎨 统一代码风格（2空格、无分号）（P3）
2. 🎨 升级 ESLint 至扁平配置（P3）
3. 🎨 统一主题切换机制（P3）
4. 🎨 迁移 `emit('update:xxx')` 至 `defineModel<T>()`（P3）
5. 🎨 清理未使用导入（P3）
6. 🎨 分层净化（services/接口迁移）（P3）

---

## 七、验收标准

| 阶段 | 验收检查项 |
|------|-----------|
| P0 | `npm run build` 无新增错误，`npx vue-tsc --noEmit` 无新增类型错误，`python -m py_compile` 无警告 |
| P1 | 所有路由文件 ≤200行，页面vue ≤350行，业务组件 ≤250行，路由层无DB操作 |
| P2 | 硬编码清零，Pydantic模型全部在schemas/，any类型减少80% |
| P3 | ESLint `no-unused-vars` 零报错，代码风格100%统一 |

---

## 八、风险与注意事项

1. **业务逻辑不变原则**: 所有整改仅做分层、规范、格式化，不改动原有业务逻辑与交互
2. **渐进式拆分**: 超大文件拆分优先按语义拆分，避免过度拆分导致文件泛滥
3. **测试保障**: 每个阶段整改后必须执行构建验证，关键业务逻辑需人工回归测试
4. **存量代码温和处理**: 对历史遗留的不规范代码采取温和规整，不做破坏性重构
5. **并行实施**: P0必须串行优先完成，P1/P2/P3可在多个开发者间并行推进
