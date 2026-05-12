<template>
  <div class="mb-8 p-4 rounded-xl border-2 border-dashed border-neutral-border hover:border-primary/50 transition-colors">
    <div class="grid grid-cols-1 md:grid-cols-12 gap-4 items-end">
      <div class="md:col-span-3">
        <label class="block text-xs font-medium text-neutral-text-secondary mb-1.5">评分维度</label>
        <BaseSelect
          v-model="localDimension"
          :options="availableDimensions"
          option-label="label"
          option-value="key"
          placeholder="ѡ择维度"
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
        </BaseSelect>
      </div>
      <div class="md:col-span-2">
        <label class="block text-xs font-medium text-neutral-text-secondary mb-1.5">Ȩ重</label>
        <BaseInputNumber
          v-model="localWeight"
          :min="0"
          :max="100"
          :step="1"
          size="small"
          class="w-full"
        />
      </div>
      <div class="md:col-span-5">
        <label class="block text-xs font-medium text-neutral-text-secondary mb-1.5">描述</label>
        <BaseInput
          v-model="localDesc"
          size="small"
          class="w-full"
          placeholder="输入规则描述..."
        />
      </div>
      <div class="md:col-span-2">
        <BaseButton
          label="添加"
          icon="pi pi-plus"
          severity="success"
          size="small"
          :disabled="!localDimension"
          class="w-full"
          @click="handleAdd"
        />
      </div>
    </div>
  </div>

  <div class="mb-8 p-4 rounded-xl bg-neutral-bg-secondary">
    <h4 class="text-sm font-semibold text-neutral-text mb-4 flex items-center gap-2">
      <i class="pi pi-info-circle text-primary" />评分等级说明
    </h4>
    <div class="grid grid-cols-6 gap-3">
      <div
        v-for="grade in GRADE_LEVELS"
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

  <div class="flex justify-end gap-3 pt-6 border-t border-neutral-border">
    <BaseButton
      label="重置默认"
      icon="pi pi-refresh"
      severity="secondary"
      @click="$emit('reset-default')"
    />
    <BaseButton
      label="ȡ消"
      icon="pi pi-times"
      severity="secondary"
      outlined
      @click="$emit('cancel')"
    />
    <BaseButton
      label="保存更改"
      icon="pi pi-check"
      severity="primary"
      :disabled="!hasChanges"
      @click="$emit('save')"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import BaseInput from '@/components/common/ui/input/BaseInput.vue'
import BaseInputNumber from '@/components/common/ui/input/BaseInputNumber.vue'
import BaseSelect from '@/components/common/ui/input/BaseSelect.vue'
import BaseButton from '@/components/common/ui/input/BaseButton.vue'
import { GRADE_LEVELS } from '@/composables/settings/useScoringRulesSettings'
import type { DimensionInfo } from '@/services/core/scoringRulesService'

const props = defineProps<{
  availableDimensions: DimensionInfo[]
  getDimensionIcon: (key: string) => string
  getDimensionColor: (key: string) => string
  hasChanges: boolean
  newRuleDimension: string
  newRuleWeight: number
  newRuleDesc: string
}>()

const emit = defineEmits<{
  'update:newRuleDimension': [value: string]
  'update:newRuleWeight': [value: number]
  'update:newRuleDesc': [value: string]
  add: []
  'reset-default': []
  cancel: []
  save: []
}>()

const localDimension = ref(props.newRuleDimension)
const localWeight = ref(props.newRuleWeight)
const localDesc = ref(props.newRuleDesc)

watch(() => props.newRuleDimension, v => localDimension.value = v)
watch(() => props.newRuleWeight, v => localWeight.value = v)
watch(() => props.newRuleDesc, v => localDesc.value = v)
watch(localDimension, v => emit('update:newRuleDimension', v))
watch(localWeight, v => emit('update:newRuleWeight', v))
watch(localDesc, v => emit('update:newRuleDesc', v))

function handleAdd() { emit('add') }
</script>
