<template>
  <div
    class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4
           bg-surface-0 dark:bg-surface-900 border border-surface-200
           dark:border-surface-700 rounded-xl p-4">
    <div class="flex bg-surface-100 dark:bg-surface-800 rounded-lg p-1">
      <button
        class="px-4 py-2 rounded-md text-sm font-medium transition-all duration-200 flex
               items-center gap-2"
        :class="scope === 'generic'
          ? 'bg-primary-500 text-white shadow-sm'
          : 'text-color-secondary hover:text-color'"
        @click="emit('change-scope', 'generic')"
      >
        <i class="pi pi-globe" />
        通用规则
      </button>
      <button
        class="px-4 py-2 rounded-md text-sm font-medium transition-all duration-200 flex
               items-center gap-2"
        :class="scope === 'profession'
          ? 'bg-primary-500 text-white shadow-sm'
          : 'text-color-secondary hover:text-color'"
        @click="emit('change-scope', 'profession')"
      >
        <i class="pi pi-id-card" />
        职业特定规则
      </button>
    </div>

    <div
      v-if="scope === 'profession'"
      class="flex flex-col sm:flex-row gap-3 w-full sm:w-auto"
    >
      <BaseSelect
        v-model="selectedBaseProfession"
        :options="cascadeProfessions"
        option-label="label"
        option-value="value"
        placeholder="选择职业"
        class="w-full sm:w-48"
        @change="onBaseProfessionChange"
      >
        <template #value="slotProps">
          <div
            v-if="slotProps.value"
            class="flex items-center gap-2"
          >
            <div
              class="w-3 h-3 rounded-full"
              :style="{ background: getProfessionColor(slotProps.value) }"
            />
            <span>{{ getProfessionLabel(slotProps.value) }}</span>
          </div>
          <span
            v-else
            class="text-color-secondary"
          >选择职业</span>
        </template>
        <template #option="slotProps">
          <div class="flex items-center gap-2">
            <div
              class="w-3 h-3 rounded-full"
              :style="{ background: slotProps.option.color }"
            />
            <span>{{ slotProps.option.label }}</span>
          </div>
        </template>
      </BaseSelect>

      <BaseSelect
        v-model="selectedProfession"
        :options="filteredEliteSpecs"
        option-label="label"
        option-value="value"
        placeholder="选择精英特长"
        class="w-full sm:w-56"
        :disabled="!selectedBaseProfession"
        @change="onProfessionChange"
      >
        <template #value="slotProps">
          <div
            v-if="slotProps.value"
            class="flex items-center gap-2"
          >
            <div
              class="w-3 h-3 rounded-full"
              :style="{ background: getSpecColor(slotProps.value) }"
            />
            <span>{{ getSpecLabel(slotProps.value) }}</span>
          </div>
          <span
            v-else
            class="text-color-secondary"
          >选择精英特长</span>
        </template>
        <template #option="slotProps">
          <div class="flex items-center gap-2">
            <div
              class="w-3 h-3 rounded-full"
              :style="{ background: slotProps.option.color }"
            />
            <span>{{ slotProps.option.label }}</span>
          </div>
        </template>
      </BaseSelect>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import BaseSelect from '@/components/common/ui/input/BaseSelect.vue'
import type { ProfessionCascade } from '@/services/system/dictionaryService'
import { Colors } from '@/config/designTokens'

interface Props {
  scope: 'generic' | 'profession'
  cascadeProfessions: ProfessionCascade[]
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'change-scope': [scope: 'generic' | 'profession']
  'base-profession-change': []
  'profession-change': []
}>()

const selectedBaseProfession = defineModel<string>('selectedBaseProfession', { default: '' })
const selectedProfession = defineModel<string>('selectedProfession', { default: '' })

const filteredEliteSpecs = computed(() => {
  const prof = props.cascadeProfessions.find(p => p.value === selectedBaseProfession.value)
  return prof?.elite_specs || []
})

function getProfessionColor(value: string): string {
  const prof = props.cascadeProfessions.find(p => p.value === value)
  return prof?.color || Colors.palette.gray
}

function getProfessionLabel(value: string): string {
  const prof = props.cascadeProfessions.find(p => p.value === value)
  return prof?.label || value
}

function getSpecColor(value: string): string {
  for (const prof of props.cascadeProfessions) {
    const spec = prof.elite_specs.find(s => s.value === value)
    if (spec) return spec.color
  }
  return Colors.palette.gray
}

function getSpecLabel(value: string): string {
  for (const prof of props.cascadeProfessions) {
    const spec = prof.elite_specs.find(s => s.value === value)
    if (spec) return spec.label
  }
  return value
}

function onBaseProfessionChange() {
  emit('base-profession-change')
}

function onProfessionChange() {
  emit('profession-change')
}
</script>

<script lang="ts">
export default {
  name: 'RuleScopeSelector',
}
</script>
