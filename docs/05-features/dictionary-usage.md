# 字典功能使用指南

> **版本**: v3.1.0  
> **更新日期**: 2026-05-07  
> **设计理念**: 借鉴若依(RuoYi)字典管理，实现"配置一次，全局复用"

---

## 一、概述

字典功能是系统的核心基础设施，用于统一管理所有枚举类配置数据（如职业、角色、状态、类型等）。通过将硬编码的枚举值抽离到数据库中管理，实现：

- **零代码扩展**：新增枚举值只需在管理页面配置，无需改代码
- **动态启用禁用**：通过 `status` 字段控制哪些枚举值生效
- **统一翻译**：前端自动将 `value` 翻译为 `label`，无需手写映射表
- **颜色标记**：每个字典项可配置 `css_class` 颜色，用于 UI 高亮

---

## 二、数据结构

### 2.1 字典类型（sys_dict_type）

| 字段 | 说明 |
|-----|------|
| `dict_type` | 字典编码（唯一），如 `profession`、`role` |
| `dict_name` | 字典名称，如 "职业"、"角色定位" |
| `status` | 0=启用，1=禁用（控制整个字典类型的可用性） |
| `sort_order` | 排序顺序 |
| `is_system` | 是否系统预置（1=预置，不可删除） |

### 2.2 字典数据（sys_dict_data）

| 字段 | 说明 |
|-----|------|
| `dict_type` | 所属字典类型编码 |
| `dict_value` | 字典值（代码中使用），如 `Guardian`、`dps` |
| `dict_label` | 字典标签（展示给用户），如 "守护者"、"输出" |
| `css_class` | CSS 颜色值或样式类，如 `#0078D4`、`text-primary` |
| `status` | 0=启用，1=禁用（控制单条数据的可用性） |
| `dict_sort` | 排序顺序 |

### 2.3 启用/禁用机制

这是字典功能的核心设计：

- **字典类型禁用**（`sys_dict_type.status = 1`）：整个字典类型不可用，所有查询返回空
- **字典数据禁用**（`sys_dict_data.status = 1`）：单条数据不可用，查询时自动过滤

**典型应用场景**：

```
role 字典中有 7 个角色：
  dps（输出）        status=0  启用 ✓
  support（辅助）    status=0  启用 ✓
  tank（承伤）       status=0  启用 ✓
  condition（症状）  status=1  禁用 ✗
  healing（治疗）    status=1  禁用 ✗
  control（控制）    status=1  禁用 ✗
  utility（功能）    status=1  禁用 ✗

评分系统只渲染启用的 3 个角色卡片，
后续想启用 condition 时，只需在字典管理页将其 status 改为 0，
无需任何代码改动。
```

---

## 三、后端接口

### 3.1 公开接口（无需认证）

| 接口 | 说明 |
|-----|------|
| `GET /api/v1/dictionary/options/{dict_type}` | 获取下拉选项（已过滤 status=0） |
| `GET /api/v1/dictionary/cascade/profession-specs` | 获取职业-精英特长级联数据 |

### 3.2 管理接口（需管理员权限）

| 接口 | 说明 |
|-----|------|
| `GET /api/v1/dictionary/types` | 字典类型列表（分页） |
| `GET /api/v1/dictionary/types/all` | 所有启用的字典类型 |
| `POST /api/v1/dictionary/types` | 创建字典类型 |
| `PUT /api/v1/dictionary/types/{dict_id}` | 更新字典类型 |
| `DELETE /api/v1/dictionary/types/{dict_id}` | 删除字典类型 |
| `GET /api/v1/dictionary/data` | 字典数据列表（分页） |
| `POST /api/v1/dictionary/data` | 创建字典项 |
| `PUT /api/v1/dictionary/data/{dict_code}` | 更新字典项 |
| `DELETE /api/v1/dictionary/data/{dict_code}` | 删除字典项 |
| `POST /api/v1/dictionary/reload-cache` | 刷新字典缓存 |
| `POST /api/v1/dictionary/init` | 初始化系统预置字典 |

### 3.3 后端服务层

```python
from app.services.system.dictionary_service import DictionaryService
from app.utils.dict_utils import get_dict_options, get_dict_label

# 服务层用法（带 db session）
service = DictionaryService(db)
options = service.get_dict_options("role")

# 工具函数（自动获取 session）
label = get_dict_label("profession", "Guardian")  # -> "守护者"
```

**后端多级缓存机制**：

```
内存缓存（5分钟） → 持久化缓存文件（1小时） → 数据库查询
```

---

## 四、前端使用方式

### 4.1 Pinia Store（全局缓存）

登录后自动预加载常用字典到全局 Store，组件内直接读取。

```typescript
import { useDictStore } from '@/store/system/dict'

const dictStore = useDictStore()

// 获取字典数据
const roles = dictStore.getDict('role')

// 获取标签
const label = dictStore.getDictLabel('profession', 'Guardian')  // '守护者'

// 获取颜色
const color = dictStore.getDictColor('role', 'dps')  // '#FF6B35'

// 获取完整字典项
const item = dictStore.getDictItem('role', 'support')
// { label: '辅助', value: 'support', css_class: '#35B0FF', is_default: 0 }

// 强制刷新指定字典
await dictStore.refreshDict('profession')

// 清空所有缓存
dictStore.cleanDict()
```

### 4.2 useDict Composable（批量加载）

一次性加载多个字典，自动并行请求 + Store 缓存。

```typescript
import { useDict } from '@/composables/core/useDict'

// 同时加载 profession 和 role 两个字典
const { profession, role, dictLoading, dictReady } = useDict('profession', 'role')

// profession.value -> [{label:'守护者', value:'Guardian', css_class:'#0078D4'}, ...]
// dictLoading.value -> true/false
// dictReady.value -> true（全部加载完成）
```

**异步版（需要等待加载完成）**：

```typescript
import { useDictAsync } from '@/composables/core/useDict'

const { profession } = await useDictAsync('profession', 'role')
// 此时 profession.value 已有数据
```

### 4.3 DictTag 组件（标签翻译 + 颜色）

自动将字典值翻译为标签文本，并根据 `css_class` 显示颜色。

```vue
<!-- 基础用法：圆角标签（默认） -->
<DictTag dict-type="role" value="dps" />
<!-- 显示：红色圆角标签 "输出" -->

<!-- PrimeVue Tag 样式 -->
<DictTag dict-type="profession" value="Guardian" variant="tag" />

<!-- PrimeVue Badge 样式 -->
<DictTag dict-type="role" value="support" variant="badge" />

<!-- 纯文本（带颜色圆点） -->
<DictTag dict-type="role" value="tank" variant="text" show-dot />

<!-- 自定义占位文本 -->
<DictTag dict-type="role" :value="null" placeholder="未设置" />
```

### 4.4 DictSelect 组件（下拉选择）

自动从 Store 缓存读取选项，支持颜色预览。

```vue
<DictSelect
  v-model="selectedRole"
  dict-type="role"
  placeholder="选择角色"
  show-color
/>
```

**特性**：
- 优先从 Pinia Store 读取，避免重复请求
- Store 中没有时自动请求 API 并存入缓存
- 支持颜色圆点预览
- 支持搜索过滤

### 4.5 在 Table 列中使用

```vue
<Column field="profession" header="职业">
  <template #body="{ data }">
    <DictTag dict-type="profession" :value="data.profession" />
  </template>
</Column>

<Column field="role_type" header="角色">
  <template #body="{ data }">
    <DictTag dict-type="role" :value="data.role_type" variant="badge" />
  </template>
</Column>
```

---

## 五、常见使用场景

### 场景 1：表单下拉框

```vue
<template>
  <div class="form">
    <!-- 方式1：使用 DictSelect 组件（推荐） -->
    <DictSelect v-model="form.profession" dict-type="profession" />
    <DictSelect v-model="form.role" dict-type="role" />

    <!-- 方式2：手动使用 Store -->
    <Dropdown
      v-model="form.profession"
      :options="professionOptions"
      option-label="label"
      option-value="value"
    />
  </div>
</template>

<script setup>
import { useDict } from '@/composables/core/useDict'
const { profession: professionOptions } = useDict('profession')
</script>
```

### 场景 2：列表翻译

```vue
<template>
  <DataTable :value="players">
    <Column field="profession" header="职业">
      <template #body="{ data }">
        <div class="flex items-center gap-2">
          <div class="w-3 h-3 rounded-full" :style="{background: getColor(data.profession)}" />
          <span>{{ getLabel(data.profession) }}</span>
        </div>
      </template>
    </Column>
  </DataTable>
</template>

<script setup>
import { useDictStore } from '@/store/system/dict'
const dictStore = useDictStore()

const getLabel = (val) => dictStore.getDictLabel('profession', val)
const getColor = (val) => dictStore.getDictColor('profession', val)
</script>
```

### 场景 3：级联选择

```vue
<template>
  <div class="flex gap-3">
    <Dropdown v-model="selectedProfession" :options="professions" @change="onProfChange" />
    <Dropdown v-model="selectedSpec" :options="filteredSpecs" />
  </div>
</template>

<script setup>
import { useDict } from '@/composables/core/useDict'
import { dictionaryService } from '@/services/system/dictionaryService'

const { profession: professions } = useDict('profession')

const selectedProfession = ref('')
const selectedSpec = ref('')
const filteredSpecs = ref([])

async function onProfChange() {
  const cascade = await dictionaryService.getProfessionSpecsCascade()
  const prof = cascade?.professions?.find(p => p.value === selectedProfession.value)
  filteredSpecs.value = prof?.elite_specs || []
}
</script>
```

### 场景 4：后端动态渲染评分角色

```typescript
// ScoringRulesView.vue
const roleTypes = ref([])

async function fetchRoleTypes() {
  const data = await scoringRulesService.getRoleTypes()
  // 后端返回的是字典表中 status=0 的角色
  roleTypes.value = data.map(r => ({
    type: r.type,
    label: r.label,
    description: r.description,
    color: r.color,
  }))
}
```

---

## 六、最佳实践

### 6.1 字典命名规范

| 类型 | 命名规范 | 示例 |
|-----|---------|------|
| 字典类型编码 | 小写下划线 | `profession`, `scoring_dimension` |
| 字典值 | 英文小写/驼峰 | `Guardian`, `dps`, `damage` |
| 字典标签 | 中文 | `守护者`, `输出`, `伤害` |
| css_class | Hex 颜色值 | `#0078D4`, `#FF6B35` |

### 6.2 新增字典的标准流程

1. **确认是否需要**：先检查现有字典中是否有类似类型
2. **创建字典类型**：在字典管理页创建 `dict_type` 和 `dict_name`
3. **添加字典数据**：逐条添加 `dict_value`、`dict_label`、`css_class`
4. **后端消费**：在 `dict_init.py` 中添加初始化代码（保证新环境自动创建）
5. **前端消费**：使用 `useDict('your_type')` 或 `<DictTag dict-type="your_type" />`
6. **测试验证**：确认禁用/启用状态生效

### 6.3 性能优化建议

| 建议 | 说明 |
|-----|------|
| 优先使用 Pinia Store | 避免每个组件独立请求，减少 API 调用 |
| 批量加载 | `useDict('a', 'b', 'c')` 比分别调用 3 次更高效 |
| 登录预加载 | 系统已在登录成功后自动预加载常用字典 |
| 及时清理 | 字典数据变更后，Store 会自动清空对应缓存 |

### 6.4 避免踩坑

| 坑 | 解决方案 |
|---|---------|
| 字典值改了，前端还显示旧标签 | 字典管理页操作后，Store 会自动刷新；如仍有问题，点击"刷新字典缓存"按钮 |
| 新增角色后评分系统不显示 | 检查 `role` 字典中该角色的 `status` 是否为 `0` |
| 颜色不生效 | 确认 `css_class` 是有效的 Hex 颜色值（如 `#0078D4`） |
| 多个组件同时加载同一个字典 | 不用担心，Store 会合并请求，只发一次 API |

---

## 七、系统预置字典

以下字典类型在系统初始化时自动创建（`is_system = 1`），**不可删除**：

| 字典类型 | 说明 | 典型用途 |
|---------|------|---------|
| `profession` | 职业 | 玩家职业选择、级联查询 |
| `specialization` | 精英特长 | 职业级联、Build 配置 |
| `role` | 角色定位 | 评分系统角色卡片、规则配置 |
| `scoring_dimension` | 评分维度 | 评分规则权重配置 |
| `game_mode` | 游戏模式 | 日志分类、统计筛选 |
| `buff_id` | 增益ID | Buff 名称映射 |

---

## 八、架构图

```
┌─────────────────────────────────────────────────────────────┐
│                        前端层 (Vue 3)                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │ DictSelect  │  │  DictTag    │  │   useDict()         │ │
│  │ 下拉选择    │  │  标签翻译   │  │   批量加载          │ │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘ │
│         │                │                    │            │
│  ┌──────▼────────────────▼────────────────────▼──────────┐ │
│  │              Pinia Store (useDictStore)               │ │
│  │  - 全局缓存 Map<dictType, DictItem[]>                 │ │
│  │  - getDictLabel / getDictColor / getDictItem          │ │
│  │  - loadDict / loadDicts / preloadCommonDicts          │ │
│  └──────┬────────────────────────────────────────────────┘ │
│         │ 缓存命中直接返回                                 │
│         │ 缓存未命中发 API 请求                            │
└─────────┼──────────────────────────────────────────────────┘
          │
┌─────────▼──────────────────────────────────────────────────┐
│                    API 层 (FastAPI)                         │
│  GET /dictionary/options/{dict_type}  ← 公开接口            │
│  GET /dictionary/cascade/profession-specs  ← 级联数据       │
│  POST /dictionary/reload-cache  ← 刷新缓存                  │
└─────────┬──────────────────────────────────────────────────┘
          │
┌─────────▼──────────────────────────────────────────────────┐
│                 服务层 (DictionaryService)                  │
│  - get_dict_options()  → 查缓存 → 查数据库                  │
│  - get_dict_label()    → 查缓存 → 查数据库                  │
└─────────┬──────────────────────────────────────────────────┘
          │
┌─────────▼──────────────────────────────────────────────────┐
│                多级缓存 (dict_utils.py)                     │
│  内存缓存 (5分钟) → 持久化缓存文件 (1小时) → 数据库查询      │
└─────────────────────────────────────────────────────────────┘
```

---

## 九、变更日志

| 日期 | 版本 | 变更 |
|------|------|------|
| 2026-04-29 | v1.0 | 字典管理模块初版 |
| 2026-05-02 | v2.0 | 新增 Pinia Store 全局缓存、useDict Composable、DictTag 组件 |
| 2026-05-04 | v2.1 | DictSelect 集成 Store 缓存、字典管理页操作后自动刷新前端缓存 |
| 2026-05-05 | v3.0 | 评分系统角色类型改为字典驱动，支持动态启用/禁用 |
| 2026-05-07 | v3.1 | 新增职业-精英特长级联接口、登录后自动预加载常用字典 |
