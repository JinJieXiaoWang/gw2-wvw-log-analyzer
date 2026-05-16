<template>
  <div class="bg-neutral-card rounded-xl border border-neutral-border overflow-hidden">
    <div class="px-5 py-4 border-b border-neutral-border font-medium text-white">
      基本信息
    </div>
    <div class="p-5">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <FormField
          class="md:col-span-2"
          label="配置标题"
          required
        >
          <BaseInput
            v-model="localForm.title"
            class="w-full"
            placeholder="输入配置标题"
          />
        </FormField>
        <FormField
          label="职业"
          required
        >
          <BaseSelect
            v-model="localForm.profession"
            :options="selectOptions.professionOptions"
            option-label="label"
            option-value="value"
            class="w-full"
            placeholder="选择职业"
          />
        </FormField>
        <FormField label="精英特长">
          <BaseSelect
            v-model="localForm.eliteSpec"
            :options="selectOptions.eliteSpecOptions"
            option-label="label"
            option-value="value"
            class="w-full"
            placeholder="选择精英特长"
            :disabled="loadingDicts"
          />
        </FormField>
        <FormField
          label="角色类型"
          required
        >
          <BaseSelect
            v-model="localForm.role"
            :options="selectOptions.roleOptions"
            option-label="label"
            option-value="value"
            class="w-full"
            placeholder="选择角色类型"
          />
        </FormField>
        <div>
          <label class="block text-sm font-medium mb-1">子角色</label>
          <div class="flex flex-wrap gap-2">
            <BaseButton
              v-for="sr in subRoleOptions"
              :key="sr.value"
              :severity="localForm.subRoles.includes(sr.value) ? 'primary' : 'secondary'"
              :outlined="!localForm.subRoles.includes(sr.value)"
              size="small"
              @click="$emit('toggle-sub-role', sr.value)"
            >
              {{ sr.label }}
            </BaseButton>
          </div>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">护甲类型</label>
          <BaseInput
            v-model="localForm.armorType"
            class="w-full"
            placeholder="如：狂战士、吟游诗人"
          />
        </div>
        <div class="flex items-center gap-3">
          <BaseToggleSwitch
            v-model="localForm.isMeta"
            label="META 配置"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import BaseButton from '@/components/common/ui/input/BaseButton.vue'
import BaseInput from '@/components/common/ui/input/BaseInput.vue'
import BaseSelect from '@/components/common/ui/input/BaseSelect.vue'
import BaseToggleSwitch from '@/components/common/ui/input/BaseToggleSwitch.vue'
import FormField from '@/components/common/ui/input/FormField.vue'
import type { SubRoleType } from '@/composables/build/useBuildEditDialog'
import { SUB_ROLE_OPTIONS } from '@/composables/build/useBuildEditDialog'
import type { BuildCreateDto } from '@/types/buildLibrary'
import { reactive, watch } from 'vue'

/** 下拉选项配置 */
interface SelectOptions {
  /** 职业选项列表 */
  professionOptions: { label: string; value: string }[]
  /** 精英特长选项列表 */
  eliteSpecOptions: { label: string; value: string }[]
  /** 角色类型选项列表 */
  roleOptions: { label: string; value: string }[]
}

const props = defineProps<{
  form: BuildCreateDto
  selectOptions: SelectOptions
  loadingDicts: boolean
}>()

const emit = defineEmits<{
  'toggle-sub-role': [value: SubRoleType]
  'update:form': [form: BuildCreateDto]
}>()

const subRoleOptions = SUB_ROLE_OPTIONS

const localForm = reactive({ ...props.form })

watch(() => props.form, (val) => {
  Object.assign(localForm, val)
}, { deep: true })

watch(localForm, (val) => {
  emit('update:form', { ...val })
}, { deep: true })
</script>
