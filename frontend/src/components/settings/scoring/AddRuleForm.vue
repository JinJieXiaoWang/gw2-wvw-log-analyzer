<template>
  <div
    v-if="canWrite"
    class="mt-5"
  >
    <div
      class="bg-surface-100 dark:bg-surface-800 border-2 border-dashed border-surface-300 dark:border-surface-600 rounded-xl p-5 transition-colors hover:border-primary-400 hover:bg-primary-500/5"
    >
      <div class="flex items-center gap-2 mb-4 font-semibold text-color-secondary">
        <i class="pi pi-plus-circle text-primary-500" />
        <span>添加新评分规则</span>
      </div>
      <div class="flex flex-wrap items-start sm:items-center gap-3">
        <Dropdown
          v-model="localDim"
          :options="availableDimensions"
          option-label="label"
          option-value="key"
          placeholder="选择维度"
          class="w-full sm:w-48"
        >
          <template #value="{ value }">
            <div
              v-if="value"
              class="flex items-center gap-2"
            >
              <div
                class="w-6 h-6 rounded flex items-center justify-center text-white text-xs"
                :style="{ background: getDimensionColor(value) }"
              >
                <i :class="getDimensionIcon(value)" />
              </div>
              <span>{{ getDimensionLabel(value) }}</span>
            </div>
            <span
              v-else
              class="text-color-secondary"
            >选择维度</span>
          </template>
          <template #option="{ option }">
            <div class="flex items-center gap-2">
              <div
                class="w-6 h-6 rounded flex items-center justify-center text-white text-xs"
                :style="{ background: getDimensionColor(option.key) }"
              >
                <i :class="getDimensionIcon(option.key)" />
              </div>
              <span>{{ option.label }}</span>
            </div>
          </template>
        </Dropdown>
        <div class="flex items-center gap-2 flex-1 min-w-0">
          <label class="text-sm text-color-secondary whitespace-nowrap">权重</label>
          <InputNumber
            v-model="localWt"
            :min="0"
            :max="10"
            :step="0.01"
            size="small"
            class="w-20"
          />
          <span class="text-xs text-color-secondary">%</span>
          <InputText
            v-model="localDc"
            placeholder="规则描述（可选）"
            class="flex-1 min-w-0"
          />
        </div>
        <Button
          label="添加"
          icon="pi pi-plus"
          severity="success"
          :disabled="!localDim"
          @click="onAdd"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import Dropdown from 'primevue/dropdown'
import InputNumber from 'primevue/inputnumber'
import InputText from 'primevue/inputtext'
import Button from 'primevue/button'
import type { DimensionInfo } from '@/services/core/scoringRulesService'

const props = defineProps<{
  availableDimensions: DimensionInfo[]
  canWrite: boolean
  getDimensionIcon: (key: string) => string
  getDimensionColor: (key: string) => string
  getDimensionLabel: (key: string) => string
  activeRole: string
}>()

const emit = defineEmits<{
  add: [dimension: string, weight: number, desc: string]
}>()

const localDim = ref('')
const localWt = ref(0.1)
const localDc = ref('')

watch(() => props.activeRole, () => {
  localDim.value = ''
  localWt.value = 0.1
  localDc.value = ''
})

const onAdd = () => {
  emit('add', localDim.value, localWt.value, localDc.value)
  localDim.value = ''
  localWt.value = 0.1
  localDc.value = ''
}
</script>
