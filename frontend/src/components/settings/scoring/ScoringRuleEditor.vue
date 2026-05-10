<template>
  <div class="bg-surface-0 dark:bg-surface-900 border border-surface-200 dark:border-surface-700 rounded-2xl p-6 shadow-lg">
    <!-- Header -->
    <div class="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4 mb-5">
      <div class="flex items-center gap-4">
        <div class="w-12 h-12 rounded-lg flex items-center justify-center text-xl text-white shadow-lg shrink-0" :style="{ background: `linear-gradient(135deg, ${data.roleColor}, ${data.roleGradient})`, boxShadow: `0 8px 24px -8px ${data.roleColor}` }">
          <i :class="data.activeRoleIcon" />
        </div>
        <div>
          <h3 class="text-xl font-semibold text-color">{{ data.activeRoleLabel }}评分规则<span v-if="data.ruleScope === 'profession' && data.selectedProfession" class="text-sm font-normal text-color-secondary ml-2">鈥?{{ data.selectedProfession }}</span></h3>
          <div class="flex items-center gap-3 mt-1 flex-wrap">
            <span class="text-sm text-color-secondary">Ȩ重总和</span>
            <div class="flex items-baseline gap-1 px-3 py-0.5 rounded-full text-sm font-bold transition-colors" :class="data.weightStatusClass === 'optimal' ? 'bg-green-500/10 text-green-500' : data.weightStatusClass === 'warning' ? 'bg-orange-500/10 text-orange-500' : 'bg-red-500/10 text-red-500'">
              <span class="text-base">{{ data.totalWeight.toFixed(2) }}</span><span class="text-xs font-normal opacity-60">/ 1.00</span>
            </div>
            <span v-if="data.weightStatusClass !== 'optimal'" class="flex items-center gap-1 text-xs text-orange-500"><i class="pi pi-exclamation-circle" />建议调整涓?1.0</span>
          </div>
        </div>
      </div>
      <div class="flex flex-wrap gap-2">
        <BaseButton v-if="data.ruleScope === 'generic'" label="应用到历史数鎹? icon="pi pi-history" severity="info" outlined :loading="data.recalculating" :disabled="!data.canRecalculate" @click="emit('recalculate')" />
        <BaseButton v-if="data.ruleScope === 'profession'" label="ɾ除职业规则" icon="pi pi-trash" severity="danger" outlined :loading="data.deletingProfession" :disabled="!data.currentProfessionHasRules" @click="emit('delete-profession')" />
        <BaseButton label="重置默认" icon="pi pi-refresh" severity="secondary" outlined :loading="data.resetting" @click="emit('reset')" />
        <BaseButton label="保存更改" icon="pi pi-save" severity="primary" :loading="data.saving" :disabled="!data.hasUnsavedChanges" @click="emit('save')" />
      </div>
    </div>

    <!-- 权重鏉?-->
    <div class="relative h-2 bg-surface-200 dark:bg-surface-700 rounded-full mb-5 overflow-hidden">
      <div class="h-full rounded-full transition-all duration-300" :class="data.weightStatusClass === 'optimal' ? 'bg-green-500' : data.weightStatusClass === 'warning' ? 'bg-orange-500' : 'bg-red-500'" :style="{ width: `${Math.min(data.totalWeight * 100, 100)}%` }" />
      <div class="absolute top-0 bottom-0 w-0.5 bg-white/50" style="left: 100%" />
    </div>

    <!-- 规则琛ㄦ牸 -->
    <div class="rounded-lg overflow-hidden border border-surface-200 dark:border-surface-700">
      <DataTable :value="data.editableRules" :loading="data.loading" striped-rows row-hover class="text-sm">
        <template #empty>
          <EmptyState icon="pi pi-inbox" title="暂无评分规则" description="请添加新规则" />
        </template>
        <Column field="sort_order" header="排序" style="width: 80px">
          <template #body="{ index }">
            <div class="flex items-center gap-1">
              <BaseButton icon="pi pi-chevron-up" text rounded size="small" class="w-7 h-7" :disabled="index === 0" @click="emit('move-up', index)" />
              <span class="w-6 text-center text-sm font-semibold">{{ index + 1 }}</span>
              <BaseButton icon="pi pi-chevron-down" text rounded size="small" class="w-7 h-7" :disabled="index === data.editableRules.length - 1" @click="emit('move-down', index)" />
            </div>
          </template>
        </Column>
        <Column field="dimension" header="评分维度" style="width: 150px">
          <template #body="{ data }">
            <div class="flex items-center gap-3">
              <div class="w-9 h-9 rounded-md flex items-center justify-center text-white text-sm shrink-0" :style="{ background: data.getDimensionColor(data.dimension) }"><i :class="data.getDimensionIcon(data.dimension)" /></div>
              <span class="font-medium">{{ data.getDimensionLabel(data.dimension) }}</span>
            </div>
          </template>
        </Column>
        <Column field="weight" header="Ȩ重分配" style="min-width: 280px">
          <template #body="{ index }">
            <div class="flex items-center gap-3 relative">
              <Slider v-model="data.editableRules[index].weight" :min="0" :max="1" :step="0.01" class="flex-1" :disabled="!data.canWrite" @change="emit('mark-changed')" />
              <div class="flex items-center gap-1 bg-surface-100 dark:bg-surface-800 px-2 py-1 rounded-md border border-surface-200 dark:border-surface-700">
                <InputNumber v-model="data.editableRules[index].weight" :min="0" :max="1" :step="0.01" :max-fraction-digits="2" size="small" class="w-16" :disabled="!data.canWrite" @update:model-value="emit('mark-changed')" />
                <span class="text-xs text-color-secondary">(0-1)</span>
              </div>
              <div class="absolute bottom-0 left-0 h-0.5 bg-primary-500 opacity-30 transition-all" :style="{ width: `${data.editableRules[index].weight * 100}%` }" />
            </div>
          </template>
        </Column>
        <Column field="description" header="规则描述">
          <template #body="{ index }">
            <InputText v-model="data.editableRules[index].description" size="small" class="w-full" placeholder="输入规则描述..." :disabled="!data.canWrite" @update:model-value="emit('mark-changed')" />
          </template>
        </Column>
        <Column field="is_active" header="״漼? style="width: 100px">
          <template #body="{ index }">
            <div class="flex items-center gap-2">
              <ToggleSwitch v-model="data.editableRules[index].is_active" :disabled="!data.canWrite" @update:model-value="emit('mark-changed')" />
              <span class="text-xs font-medium" :class="data.editableRules[index].is_active ? 'text-green-500' : 'text-color-secondary'">{{ data.editableRules[index].is_active ? '启用' : '禁用' }}</span>
            </div>
          </template>
        </Column>
        <Column header="操作" style="width: 80px">
          <template #body="{ index }">
            <BaseButton v-if="data.canWrite" icon="pi pi-trash" severity="danger" text rounded size="small" class="w-9 h-9 text-color-secondary hover:text-red-500" @click="emit('remove-rule', index)" />
          </template>
        </Column>
      </DataTable>
    </div>

    <!-- 添加规则 -->
    <div v-if="data.canWrite" class="mt-5">
      <div class="bg-surface-100 dark:bg-surface-800 border-2 border-dashed border-surface-300 dark:border-surface-600 rounded-xl p-5 transition-colors hover:border-primary-400 hover:bg-primary-500/5">
        <div class="flex items-center gap-2 mb-4 font-semibold text-color-secondary"><i class="pi pi-plus-circle text-primary-500" /><span>添加新评分规鍒?/span></div>
        <div class="flex flex-wrap items-center gap-4">
          <BaseSelect v-model="newRuleDim" :options="data.availableDimensions" option-label="label" option-value="key" placeholder="ѡ择维度" class="w-52">
            <template #value="{ value }">
              <div v-if="value" class="flex items-center gap-2">
                <div class="w-6 h-6 rounded flex items-center justify-center text-white text-xs" :style="{ background: data.getDimensionColor(value) }"><i :class="data.getDimensionIcon(value)" /></div>
                <span>{{ data.getDimensionLabel(value) }}</span>
              </div>
              <span v-else class="text-color-secondary">ѡ择维度</span>
            </template>
            <template #option="{ option }">
              <div class="flex items-center gap-2">
                <div class="w-6 h-6 rounded flex items-center justify-center text-white text-xs" :style="{ background: data.getDimensionColor(option.key) }"><i :class="data.getDimensionIcon(option.key)" /></div>
                <span>{{ option.label }}</span>
              </div>
            </template>
          </BaseSelect>
          <div class="flex items-center gap-2">
            <label class="text-sm text-color-secondary whitespace-nowrap">Ȩ重</label>
            <InputNumber v-model="newRuleWt" :min="0" :max="1" :step="0.01" :max-fraction-digits="2" size="small" class="w-24" />
            <span class="text-xs text-color-secondary">(0-1)</span>
          </div>
          <InputText v-model="newRuleDc" placeholder="规则描述锛堝彲閫夛級" class="flex-1 min-w-[200px]" />
          <BaseButton label="添加" icon="pi pi-plus" severity="success" :disabled="!newRuleDim" @click="onAdd" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import BaseButton from '@/components/common/ui/BaseButton.vue'
import EmptyState from '@/components/common/ui/EmptyState.vue'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import InputNumber from 'primevue/inputnumber'
import InputText from 'primevue/inputtext'
import BaseSelect from '@/components/common/ui/BaseSelect.vue'
import Slider from 'primevue/slider'
import ToggleSwitch from 'primevue/toggleswitch'
import type { ScoringRule, DimensionInfo } from '@/services/scoring/scoringRulesService'

interface RuleEditorData {
  activeRole: string
  activeRoleLabel: string
  activeRoleIcon: string
  roleColor: string
  roleGradient: string
  editableRules: ScoringRule[]
  allDimensions: DimensionInfo[]
  loading: boolean
  saving: boolean
  resetting: boolean
  deletingProfession: boolean
  recalculating: boolean
  canWrite: boolean
  weightStatusClass: string
  totalWeight: number
  ruleScope: string
  selectedProfession: string
  canRecalculate: boolean
  currentProfessionHasRules: boolean
  hasUnsavedChanges: boolean
  availableDimensions: DimensionInfo[]
  getDimensionIcon: (key: string) => string
  getDimensionColor: (key: string) => string
  getDimensionLabel: (key: string) => string
}

const props = defineProps<{ data: RuleEditorData }>()
const emit = defineEmits<{
  save: []
  reset: []
  recalculate: []
  'delete-profession': []
  'add-rule': [dimension: string, weight: number, desc: string]
  'remove-rule': [index: number]
  'move-up': [index: number]
  'move-down': [index: number]
  'mark-changed': []
}>()

const newRuleDim = ref('')
const newRuleWt = ref(10)
const newRuleDc = ref('')

watch(() => props.data.activeRole, () => {
  newRuleDim.value = ''
  newRuleWt.value = 10
  newRuleDc.value = ''
})

function onAdd() {
  emit('add-rule', newRuleDim.value, newRuleWt.value, newRuleDc.value)
  newRuleDim.value = ''
  newRuleWt.value = 10
  newRuleDc.value = ''
}
</script>

<style scoped>
:deep(.p-slider) { background: var(--color-bg-secondary); height: 6px; border-radius: var(--radius-full); }
:deep(.p-slider .p-slider-range) { background: linear-gradient(90deg, var(--color-primary), var(--color-ai)); border-radius: var(--radius-full); }
:deep(.p-slider .p-slider-handle) { width: 18px; height: 18px; background: white; border: 3px solid var(--color-primary); box-shadow: 0 2px 8px rgba(22,93,255,0.4); transition: all var(--transition-fast); }
:deep(.p-slider .p-slider-handle:hover) { transform: scale(1.2); box-shadow: 0 4px 12px rgba(22,93,255,0.5); }
:deep(.p-inputnumber-input) { text-align: center; font-weight: 600; background: transparent; border: none; color: var(--color-text); }
:deep(.p-toggleswitch.p-toggleswitch-checked .p-toggleswitch-slider) { background: linear-gradient(90deg, var(--color-success), #33E0A5); }
</style>
