# PrimeVue 组件使用指南

## 概述
本文档用于规范项目中 PrimeVue 组件的使用方式，包括二次封装组件的使用说明和最佳实践。

## 通用二次封装组件

### BaseButton - 基础按钮组件
**路径**: `@/components/common/ui/BaseButton.vue`

**功能**: 对 PrimeVue Button 的封装，提供项目统一的按钮样式和交互
**使用方式**:
```vue
<template>
  <BaseButton label="提交" severity="primary" @click="handleSubmit" />
</template>

<script setup lang="ts">
import { BaseButton } from '@/components'
</script>
```

### BaseDialog - 基础对话框组件
**路径**: `@/components/common/ui/BaseDialog.vue`

**功能**: 对 PrimeVue Dialog 的封装，提供项目统一的对话框样式和操作流程
**使用方式**:
```vue
<template>
  <BaseDialog
    v-model:visible="showDialog"
    header="示例对话框"
    confirm-label="保存"
    @confirm="handleSave"
  >
    <div>对话框内容</div>
  </BaseDialog>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { BaseDialog } from '@/components'

const showDialog = ref(false)
</script>
```

### BaseSelect - 基础选择器组件
**路径**: `@/components/common/ui/BaseSelect.vue`

**功能**: 对 PrimeVue Select 的封装，提供项目统一的选择器样式
**使用方式**:
```vue
<template>
  <BaseSelect v-model="selectedItem" :options="options" option-label="name" option-value="id" />
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { BaseSelect } from '@/components'

const selectedItem = ref('')
const options = [
  { id: '1', name: '选项1' },
  { id: '2', name: '选项2' }
]
</script>
```

### BaseTag - 基础标签组件
**路径**: `@/components/common/ui/BaseTag.vue`

**功能**: 对 PrimeVue Tag 的封装，提供项目统一的标签样式
**使用方式**:
```vue
<template>
  <BaseTag value="已完成" severity="success" />
</template>

<script setup lang="ts">
import { BaseTag } from '@/components'
</script>
```

## PrimeVue 原生组件使用建议

### 按钮样式类
项目中已定义的按钮样式类（在 `tailwind.config.js` 或 CSS 文件中）：
- `btn-game` - 游戏风格的主按钮
- `btn-secondary` - 次要按钮
- `btn-ghost` - 幽灵按钮
- `btn-success` - 成功按钮
- `btn-danger` - 危险按钮
- `btn-warning` - 警告按钮

### 常用组件列表

| 组件名 | PrimeVue 导入 | 说明 |
|-------|-------------|------|
| Toast | `import Toast from 'primevue/toast'; import { useToast } from 'primevue/usetoast';` | 提示信息 |
| ConfirmDialog | `import ConfirmDialog from 'primevue/confirmdialog'; import { useConfirm } from 'primevue/useconfirm';` | 确认对话框 |
| Button | `import Button from 'primevue/button';` | 按钮 |
| Dialog | `import Dialog from 'primevue/dialog';` | 对话框 |
| Select | `import Select from 'primevue/select';` | 选择器 |
| Dropdown | `import Dropdown from 'primevue/dropdown';` | 下拉选择 |
| InputText | `import InputText from 'primevue/inputtext';` | 文本输入 |
| InputNumber | `import InputNumber from 'primevue/inputnumber';` | 数字输入 |
| Textarea | `import Textarea from 'primevue/textarea';` | 多行文本输入 |
| Checkbox | `import Checkbox from 'primevue/checkbox';` | 复选框 |
| RadioButton | `import RadioButton from 'primevue/radiobutton';` | 单选按钮 |
| DataTable | `import DataTable from 'primevue/datatable';` | 数据表格 |
| Column | `import Column from 'primevue/column';` | 表格列 |
| Tag | `import Tag from 'primevue/tag';` | 标签 |
| ProgressSpinner | `import ProgressSpinner from 'primevue/progressspinner';` | 加载中 |
| ProgressBar | `import ProgressBar from 'primevue/progressbar';` | 进度条 |
| Drawer | `import Drawer from 'primevue/drawer';` | 抽屉 |
| OverlayPanel | `import OverlayPanel from 'primevue/overlaypanel';` | 悬浮面板 |
| Panel | `import Panel from 'primevue/panel';` | 面板 |
| TabView | `import TabView from 'primevue/tabview';` | 标签页容器 |
| TabPanel | `import TabPanel from 'primevue/tabpanel';` | 标签页项 |
| Menu | `import Menu from 'primevue/menu';` | 菜单 |
| Tooltip | `import Tooltip from 'primevue/tooltip';` | 提示框 |

## 导入方式

### 从主组件索引导入（推荐）
```typescript
import { BaseButton, BaseDialog, PageHeader } from '@/components'
```

### 直接导入 PrimeVue 组件
```typescript
import Button from 'primevue/button'
import { useToast } from 'primevue/usetoast'
```

## 最佳实践

1. **优先使用二次封装组件**：对于基础 UI 组件（Button, Dialog, Select, Tag），优先使用项目中的封装版本
2. **保持样式一致性**：使用项目定义的样式类（如 `btn-game` 等）
3. **正确使用 Toast 和 Confirmation**：在 `main.ts` 中已全局注册 ToastService 和 ConfirmationService，可直接在组件中使用
4. **响应式设计**：确保组件在不同屏幕尺寸下能正常显示
5. **国际化**：用户可见文本应考虑未来的国际化需求

## 主题配置

项目使用自定义的游戏主题配置（`GameThemePreset`），主题在 `@/config/themePreset.ts` 中定义。所有 PrimeVue 组件将自动适配项目主题。
