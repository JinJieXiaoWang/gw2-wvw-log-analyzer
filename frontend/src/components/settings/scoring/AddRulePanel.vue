<template>
  <div class="mt-5">
    <div
      class="bg-surface-100 dark:bg-surface-800 border-2 border-dashed
             border-surface-300 dark:border-surface-600 rounded-xl p-5 transition-colors
             hover:border-primary-400 hover:bg-primary-500/5"
    >
      <div class="flex items-center gap-2 mb-4 font-semibold text-color-secondary">
        <i class="pi pi-plus-circle text-primary-500" /><span>添加新评分规则</span>
      </div>
      <div class="flex flex-wrap items-center gap-4">
        <BaseSelect
          v-model="localDim"
          :options="availableDimensions"
          option-label="label"
          option-value="key"
          placeholder="选择维度"
          class="w-52"
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
        </BaseSelect>
        <div class="flex items-center gap-2">
          <label class="text-sm text-color-secondary whitespace-nowrap">权重</label>
          <BaseInputNumber
            v-model="localWt"
            :min="0"
            :max="1"
            :step="0.01"
            :max-fraction-digits="2"
            size="small"
            class="w-24"
          />
          <span class="text-xs text-color-secondary">(0-1)</span>
        </div>
        <BaseInput
          v-model="localDc"
          placeholder="规则描述（可选）"
          class="flex-1 min-w-[200px]"
        />
        <BaseButton
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
import BaseButton from '@/components/common/ui/input/BaseButton.vue'
import BaseInput from '@/components/common/ui/input/BaseInput.vue'
import BaseInputNumber from '@/components/common/ui/input/BaseInputNumber.vue'
import BaseSelect from '@/components/common/ui/input/BaseSelect.vue'
import type { DimensionInfo } from '@/services/core/scoringRulesService'

const props = defineProps<{
  availableDimensions: DimensionInfo[]
  getDimensionIcon: (key: string) => string
  getDimensionColor: (key: string) => string
  getDimensionLabel: (key: string) => string
  activeRole: string
}>()

const emit = defineEmits<{
  'add-rule': [dimension: string, weight: number, desc: string]
}>()

const localDim = ref('')
const localWt = ref(0.1)
const localDc = ref('')

watch(() => props.activeRole, () => {
  localDim.value = ''
  localWt.value = 0.1
  localDc.value = ''
})

function onAdd() {
  emit('add-rule', localDim.value, localWt.value, localDc.value)
  localDim.value = ''
  localWt.value = 0.1
  localDc.value = ''
}
</script>
