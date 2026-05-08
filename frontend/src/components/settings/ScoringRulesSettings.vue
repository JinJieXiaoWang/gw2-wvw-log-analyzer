<template>
  <div class="card">
    <!-- 卡片头部 -->
    <div class="flex items-center gap-4 mb-8 pb-6 border-b border-neutral-border">
      <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-primary/20 to-secondary/10 flex items-center justify-center border border-primary/20">
        <i class="pi pi-chart-line text-primary text-xl" />
      </div>
      <div>
        <h3 class="text-lg font-bold text-neutral-text">
          评分规则配置
        </h3>
        <p class="text-sm text-neutral-text-secondary mt-0.5">
          为不同角色类型定制评分维度和权重
        </p>
      </div>
    </div>

    <!-- 角色类型选择 -->
    <div class="grid grid-cols-3 gap-4 mb-8">
      <button
        v-for="role in roleTypes"
        :key="role.type"
        class="relative p-4 rounded-xl border-2 transition-all duration-200 text-left"
        :class="[
          activeRole === role.type
            ? 'border-primary bg-primary/5 shadow-lg shadow-primary/10'
            : 'border-neutral-border bg-neutral-bg-secondary hover:border-neutral-border-dark'
        ]"
        @click="switchRole(role.type)"
      >
        <div class="flex items-center gap-3">
          <div
            class="w-10 h-10 rounded-lg flex items-center justify-center text-white text-base"
            :class="roleIconBgClass(role.type)"
          >
            <i :class="role.icon" />
          </div>
          <div>
            <h4 class="font-semibold text-neutral-text text-sm">
              {{ role.label }}
            </h4>
            <p class="text-xs text-neutral-text-secondary">
              {{ role.description }}
            </p>
          </div>
        </div>
        <div
          v-if="hasUnsavedChanges(role.type)"
          class="absolute top-2 right-2"
        >
          <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-warning/20 text-warning">
            已修改
          </span>
        </div>
      </button>
    </div>

    <!-- 权重状态提示 -->
    <div
      class="mb-6 p-4 rounded-xl"
      :class="weightStatusBgClass"
    >
      <div class="flex items-center justify-between mb-2">
        <span
          class="text-sm font-medium"
          :class="weightStatusTextClass"
        >
          权重总和: {{ totalWeight.toFixed(2) }} / 1.00
        </span>
        <span
          v-if="Math.abs(totalWeight - 1.0) > 0.01"
          class="text-xs text-warning flex items-center gap-1"
        >
          <i class="pi pi-exclamation-circle" />
          建议调整为 1.0
        </span>
      </div>
      <div class="h-2 rounded-full bg-neutral-bg-secondary overflow-hidden">
        <div
          class="h-full rounded-full transition-all duration-300"
          :class="weightStatusBarClass"
          :style="{ width: `${Math.min(totalWeight * 100, 100)}%` }"
        />
      </div>
    </div>

    <!-- 规则表格 -->
    <div class="mb-6">
      <DataTable
        :value="editableRules"
        :loading="loading"
        class="w-full"
        :striped-rows="true"
        :row-hover="true"
        :responsive="true"
        :resizable-columns="true"
        scrollable
        scroll-height="auto"
      >
        <!-- 排序列 -->
        <Column
          header="排序"
          style="width: 80px; min-width: 80px;"
        >
          <template #body="{ index }">
            <div class="flex items-center gap-1">
              <Button
                icon="pi pi-chevron-up"
                text
                rounded
                size="small"
                :disabled="index === 0"
                class="p-button-text p-button-secondary"
                @click="moveUp(index)"
              />
              <span class="w-6 text-center text-sm font-medium text-neutral-text">{{ index + 1 }}</span>
              <Button
                icon="pi pi-chevron-down"
                text
                rounded
                size="small"
                :disabled="index === editableRules.length - 1"
                class="p-button-text p-button-secondary"
                @click="moveDown(index)"
              />
            </div>
          </template>
        </Column>

        <!-- 评分维度列 -->
        <Column
          header="评分维度"
          style="width: 150px; min-width: 150px;"
        >
          <template #body="{ data }">
            <div class="flex items-center gap-2">
              <div
                class="w-7 h-7 rounded-md flex items-center justify-center text-white text-xs"
                :style="{ background: getDimensionColor(data.dimension) }"
              >
                <i :class="getDimensionIcon(data.dimension)" />
              </div>
              <span class="text-sm font-medium text-neutral-text">{{ getDimensionLabel(data.dimension) }}</span>
            </div>
          </template>
        </Column>

        <!-- 权重列 -->
        <Column
          header="权重"
          style="width: 280px; min-width: 280px;"
        >
          <template #body="{ index }">
            <div class="flex items-center gap-3">
              <div
                class="flex-1"
                style="min-width: 150px; max-width: 180px;"
              >
                <Slider
                  v-model="editableRules[index].weight"
                  :min="0"
                  :max="1"
                  :step="0.01"
                  class="w-full"
                  @change="markChanged"
                />
              </div>
              <div style="width: 70px; flex-shrink: 0;">
                <InputNumber
                  v-model="editableRules[index].weight"
                  :min="0"
                  :max="1"
                  :step="0.01"
                  :max-fraction-digits="2"
                  size="small"
                  class="w-full"
                  @update:model-value="markChanged"
                />
              </div>
            </div>
          </template>
        </Column>

        <!-- 描述列 -->
        <Column
          header="描述"
          style="flex: 1; min-width: 250px;"
        >
          <template #body="{ index }">
            <InputText
              v-model="editableRules[index].description"
              size="small"
              class="w-full"
              placeholder="输入描述..."
              @update:model-value="markChanged"
            />
          </template>
        </Column>

        <!-- 状态列 -->
        <Column
          header="状态"
          style="width: 120px; min-width: 120px;"
        >
          <template #body="{ data, index }">
            <div class="flex items-center gap-2">
              <ToggleSwitch
                v-model="editableRules[index].is_active"
                @update:model-value="markChanged"
              />
              <span
                class="text-xs font-medium"
                :class="data.is_active ? 'text-success' : 'text-neutral-text-tertiary'"
              >
                {{ data.is_active ? '启用' : '禁用' }}
              </span>
            </div>
          </template>
        </Column>

        <!-- 操作列 -->
        <Column
          header="操作"
          style="width: 60px; min-width: 60px;"
        >
          <template #body="{ index }">
            <Button
              icon="pi pi-trash"
              severity="danger"
              text
              rounded
              size="small"
              @click="removeRule(index)"
            />
          </template>
        </Column>

        <!-- 空状态 -->
        <template #empty>
          <div class="py-12 text-center">
            <i class="pi pi-inbox text-4xl mb-3 opacity-50 text-neutral-text-tertiary" />
            <p class="text-sm text-neutral-text-tertiary">
              暂无评分规则，请添加新规则
            </p>
          </div>
        </template>
      </DataTable>
    </div>

    <!-- 添加规则 -->
    <div class="mb-8 p-4 rounded-xl border-2 border-dashed border-neutral-border hover:border-primary/50 transition-colors">
      <div class="grid grid-cols-1 md:grid-cols-12 gap-4 items-end">
        <div class="md:col-span-3">
          <label class="block text-xs font-medium text-neutral-text-secondary mb-1.5">评分维度</label>
          <Dropdown
            v-model="newRuleDimension"
            :options="availableDimensions"
            option-label="label"
            option-value="key"
            placeholder="选择维度"
            size="small"
            class="w-full"
          >
            <template #option="{ option }">
              <div class="flex items-center gap-2">
                <div
                  class="w-5 h-5 rounded bg-neutral-bg-secondary flex items-center justify-center text-white text-xs"
                  :style="{ background: getDimensionColor(option.key) }"
                >
                  <i :class="getDimensionIcon(option.key)" />
                </div>
                <span>{{ option.label }}</span>
              </div>
            </template>
          </Dropdown>
        </div>
        <div class="md:col-span-2">
          <label class="block text-xs font-medium text-neutral-text-secondary mb-1.5">权重</label>
          <InputNumber
            v-model="newRuleWeight"
            :min="0"
            :max="100"
            :step="1"
            size="small"
            class="w-full"
          />
        </div>
        <div class="md:col-span-5">
          <label class="block text-xs font-medium text-neutral-text-secondary mb-1.5">描述</label>
          <InputText
            v-model="newRuleDesc"
            size="small"
            class="w-full"
            placeholder="输入规则描述..."
          />
        </div>
        <div class="md:col-span-2">
          <Button
            label="添加"
            icon="pi pi-plus"
            severity="success"
            size="small"
            :disabled="!newRuleDimension"
            class="w-full"
            @click="addRule"
          />
        </div>
      </div>
    </div>

    <!-- 评分等级说明 -->
    <div class="mb-8 p-4 rounded-xl bg-neutral-bg-secondary">
      <h4 class="text-sm font-semibold text-neutral-text mb-4 flex items-center gap-2">
        <i class="pi pi-info-circle text-primary" />
        评分等级说明
      </h4>
      <div class="grid grid-cols-6 gap-3">
        <div
          v-for="grade in gradeLevels"
          :key="grade.letter"
          class="text-center p-3 rounded-lg bg-neutral-card"
        >
          <div
            class="text-2xl font-bold mb-1"
            :style="{ background: grade.gradient, WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }"
          >
            {{ grade.letter }}
          </div>
          <div class="text-xs font-medium text-neutral-text">
            {{ grade.range }}
          </div>
          <div class="text-xs text-neutral-text-tertiary">
            {{ grade.desc }}
          </div>
        </div>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div class="flex justify-end gap-3 pt-6 border-t border-neutral-border">
      <Button
        label="重置默认"
        icon="pi pi-refresh"
        severity="secondary"
        @click="confirmReset"
      />
      <Button
        label="取消"
        icon="pi pi-times"
        severity="secondary"
        outlined
        @click="resetChanges"
      />
      <Button
        label="保存更改"
        icon="pi pi-check"
        severity="primary"
        :disabled="!hasUnsavedChanges(activeRole)"
        @click="saveChanges"
      />
    </div>

    <ConfirmDialog />
  </div>
</template>

<script setup lang="ts">
/**
 * 评分规则设置组件
 * 功能：按角色类型（输出/辅助/承伤）管理评分维度和权重
 * 更新日期：2026-05-06
 */

import { ref, computed, onMounted, watch } from 'vue'
import { useConfirm } from 'primevue/useconfirm'
import { useToast } from 'primevue/usetoast'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import Dropdown from 'primevue/dropdown'
import Slider from 'primevue/slider'
import ToggleSwitch from 'primevue/toggleswitch'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import ConfirmDialog from 'primevue/confirmdialog'
import { scoringRulesService, type ScoringRule, type DimensionInfo } from '@/services/scoring/scoringRulesService'

const confirm = useConfirm()
const toast = useToast()

// ============================================
// 角色类型定义
// ============================================
const roleTypes = [
  { type: 'dps', label: '输出', description: '伤害输出职责', icon: 'pi pi-bolt' },
  { type: 'support', label: '辅助', description: '治疗增益职责', icon: 'pi pi-heart' },
  { type: 'tank', label: '承伤', description: '吸收伤害职责', icon: 'pi pi-shield' },
]

const activeRole = ref('dps')

// ============================================
// 数据状态
// ============================================
const loading = ref(false)
const saving = ref(false)

const currentRules = ref<Record<string, ScoringRule[]>>({})
const originalRules = ref<Record<string, ScoringRule[]>>({})
const editableRules = ref<ScoringRule[]>([])
const changedRoles = ref<Set<string>>(new Set())
const allDimensions = ref<DimensionInfo[]>([])

// 新规则表单
const newRuleDimension = ref('')
const newRuleWeight = ref(10)
const newRuleDesc = ref('')

// 评分等级
const gradeLevels = [
  { letter: 'S', range: '≥90分', desc: '表现卓越', gradient: 'linear-gradient(135deg, #FFD700, #FFA500)' },
  { letter: 'A', range: '≥80分', desc: '表现优秀', gradient: 'linear-gradient(135deg, #00D68F, #00B4FF)' },
  { letter: 'B', range: '≥70分', desc: '表现良好', gradient: 'linear-gradient(135deg, #165DFF, #8B5CF6)' },
  { letter: 'C', range: '≥60分', desc: '表现一般', gradient: 'linear-gradient(135deg, #FFAA00, #FFB347)' },
  { letter: 'D', range: '≥40分', desc: '表现较差', gradient: 'linear-gradient(135deg, #FF8A65, #FF5722)' },
  { letter: 'F', range: '<40分', desc: '表现很差', gradient: 'linear-gradient(135deg, #FF4D6A, #D93664)' },
]

// ============================================
// 计算属性
// ============================================
const totalWeight = computed(() =>
  editableRules.value.filter(r => r.is_active).reduce((sum, r) => sum + (r.weight || 0), 0)
)

const availableDimensions = computed(() => {
  const used = new Set(editableRules.value.map(r => r.dimension))
  return allDimensions.value.filter(d => !used.has(d.key))
})

const weightStatusBgClass = computed(() => {
  const diff = Math.abs(totalWeight.value - 1.0)
  if (diff < 0.01) return 'bg-success/10'
  if (diff < 0.1) return 'bg-warning/10'
  return 'bg-error/10'
})

const weightStatusTextClass = computed(() => {
  const diff = Math.abs(totalWeight.value - 1.0)
  if (diff < 0.01) return 'text-success'
  if (diff < 0.1) return 'text-warning'
  return 'text-error'
})

const weightStatusBarClass = computed(() => {
  const diff = Math.abs(totalWeight.value - 1.0)
  if (diff < 0.01) return 'bg-success'
  if (diff < 0.1) return 'bg-warning'
  return 'bg-error'
})

// ============================================
// 方法
// ============================================
function roleIconBgClass(role: string) {
  const map: Record<string, string> = {
    dps: 'bg-gradient-to-br from-error to-orange-500',
    support: 'bg-gradient-to-br from-success to-info',
    tank: 'bg-gradient-to-br from-purple-500 to-primary',
  }
  return map[role] || 'bg-gradient-to-br from-primary to-secondary'
}

function hasUnsavedChanges(role: string) {
  return changedRoles.value.has(role)
}

// 维度信息和图标映射
const dimensionIcons: Record<string, string> = {
  damage: 'pi pi-bolt',
  healing: 'pi pi-heart',
  protection: 'pi pi-shield',
  crowd_control: 'pi pi-lock',
  support: 'pi pi-star',
  survival: 'pi pi-users',
  objective: 'pi pi-flag',
  downstacks: 'pi pi-arrow-down',
}

const dimensionColors: Record<string, string> = {
  damage: '#FF4D6A',
  healing: '#00D68F',
  protection: '#165DFF',
  crowd_control: '#9D4EDD',
  support: '#FFAA00',
  survival: '#00B4FF',
  objective: '#4CAF50',
  downstacks: '#FF5722',
}

function getDimensionIcon(key: string): string {
  return dimensionIcons[key] || 'pi pi-circle'
}

function getDimensionColor(key: string): string {
  return dimensionColors[key] || '#888888'
}

function getDimensionLabel(key: string) {
  return allDimensions.value.find(d => d.key === key)?.label || key
}

// ============================================
// API 调用
// ============================================
async function fetchRules() {
  loading.value = true
  try {
    const data = await scoringRulesService.getRules()
    if (data) {
      for (const key of ['dps', 'support', 'tank']) {
        if (data[key]) {
          currentRules.value[key] = data[key].rules || []
          originalRules.value[key] = JSON.parse(JSON.stringify(data[key].rules || []))
        }
      }
    }
    syncEditableRules()
  } catch (e: any) {
    toast.add({ severity: 'error', summary: '错误', detail: e?.message || '获取评分规则失败', life: 5000 })
  } finally {
    loading.value = false
  }
}

async function fetchDimensions() {
  try {
    allDimensions.value = await scoringRulesService.getDimensions()
  } catch (e) {
    console.error('获取评分维度失败', e)
  }
}

function syncEditableRules() {
  const rules = currentRules.value[activeRole.value] || []
  editableRules.value = rules.map(r => ({ ...r }))
}

// ============================================
// 交互
// ============================================
function switchRole(role: string) {
  activeRole.value = role
  syncEditableRules()
}

function markChanged() {
  changedRoles.value.add(activeRole.value)
}

function moveUp(index: number) {
  if (index === 0) return
  const temp = editableRules.value[index]
  editableRules.value[index] = editableRules.value[index - 1]
  editableRules.value[index - 1] = temp
  markChanged()
}

function moveDown(index: number) {
  if (index === editableRules.value.length - 1) return
  const temp = editableRules.value[index]
  editableRules.value[index] = editableRules.value[index + 1]
  editableRules.value[index + 1] = temp
  markChanged()
}

function removeRule(index: number) {
  confirm.require({
    message: '确定要删除这条评分规则吗？',
    header: '删除确认',
    icon: 'pi pi-exclamation-triangle',
    accept: () => {
      editableRules.value.splice(index, 1)
      markChanged()
      toast.add({ severity: 'success', summary: '成功', detail: '删除成功', life: 3000 })
    }
  })
}

function addRule() {
  if (!newRuleDimension.value) return
  
  const newRule: Partial<ScoringRule> = {
    role_type: activeRole.value,
    dimension: newRuleDimension.value,
    weight: newRuleWeight.value / 100,
    description: newRuleDesc.value,
    is_active: true,
    sort_order: editableRules.value.length + 1,
  }
  
  editableRules.value.push(newRule as ScoringRule)
  markChanged()
  
  // 重置表单
  newRuleDimension.value = ''
  newRuleWeight.value = 10
  newRuleDesc.value = ''
  
  toast.add({ severity: 'success', summary: '成功', detail: '添加成功', life: 3000 })
}

function resetChanges() {
  if (!hasUnsavedChanges(activeRole.value)) return
  
  confirm.require({
    message: '确定要取消所有未保存的更改吗？',
    header: '取消确认',
    icon: 'pi pi-exclamation-triangle',
    accept: () => {
      currentRules.value[activeRole.value] = JSON.parse(JSON.stringify(originalRules.value[activeRole.value] || []))
      changedRoles.value.delete(activeRole.value)
      syncEditableRules()
      toast.add({ severity: 'info', summary: '已取消', detail: '已恢复到上次保存的状态', life: 3000 })
    }
  })
}

async function saveChanges() {
  if (!hasUnsavedChanges(activeRole.value)) return
  
  saving.value = true
  try {
    await scoringRulesService.batchUpdate(activeRole.value, editableRules.value)
    originalRules.value[activeRole.value] = JSON.parse(JSON.stringify(editableRules.value))
    changedRoles.value.delete(activeRole.value)
    toast.add({ severity: 'success', summary: '成功', detail: '保存成功', life: 3000 })
  } catch (e: any) {
    toast.add({ severity: 'error', summary: '错误', detail: e?.message || '保存失败', life: 5000 })
  } finally {
    saving.value = false
  }
}

function confirmReset() {
  confirm.require({
    message: '确定要重置为默认评分规则吗？这将覆盖所有自定义设置。',
    header: '重置确认',
    icon: 'pi pi-exclamation-triangle',
    accept: async () => {
      loading.value = true
      try {
        await scoringRulesService.resetDefault(activeRole.value)
        await fetchRules()
        changedRoles.value.delete(activeRole.value)
        toast.add({ severity: 'success', summary: '成功', detail: '已重置为默认规则', life: 3000 })
      } catch (e: any) {
        toast.add({ severity: 'error', summary: '错误', detail: e?.message || '重置失败', life: 5000 })
      } finally {
        loading.value = false
      }
    }
  })
}

// ============================================
// 生命周期
// ============================================
onMounted(() => {
  fetchRules()
  fetchDimensions()
})

watch(activeRole, () => {
  syncEditableRules()
})
</script>

<style scoped>
/* 自定义滚动条 */
:deep(.p-datatable-scrollable-body) {
  scrollbar-width: thin;
  scrollbar-color: var(--color-neutral-border) transparent;
}

:deep(.p-datatable-scrollable-body::-webkit-scrollbar) {
  width: 6px;
  height: 6px;
}

:deep(.p-datatable-scrollable-body::-webkit-scrollbar-track) {
  background: transparent;
}

:deep(.p-datatable-scrollable-body::-webkit-scrollbar-thumb) {
  background-color: var(--color-neutral-border);
  border-radius: 3px;
}

/* 表格单元格内边距 */
:deep(.p-datatable .p-datatable-tbody > tr > td) {
  padding: 12px 16px;
}

/* 表头样式 */
:deep(.p-datatable .p-datatable-thead > tr > th) {
  padding: 12px 16px;
  background: var(--color-bg-secondary);
  border-bottom: 2px solid var(--color-neutral-border);
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-neutral-text-secondary);
}

/* 行悬停效果 */
:deep(.p-datatable .p-datatable-tbody > tr:hover) {
  background-color: var(--color-bg-secondary);
}

/* 条纹行 */
:deep(.p-datatable .p-datatable-tbody > tr.p-datatable-striped-row) {
  background-color: var(--color-card);
}

:deep(.p-datatable .p-datatable-tbody > tr.p-datatable-striped-row:hover) {
  background-color: var(--color-bg-secondary);
}
</style>