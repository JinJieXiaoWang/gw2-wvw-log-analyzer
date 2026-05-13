<template>
  <Panel
    header="基本信息"
    toggleable
    :collapsed="false"
  >
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <FormField
        class="md:col-span-2"
        label="配置标题"
        required
      >
        <InputText
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
          :options="professionOptions"
          option-label="label"
          option-value="value"
          class="w-full"
          placeholder="选择职业"
        />
      </FormField>
      <FormField label="精英特长">
        <BaseSelect
          v-model="localForm.eliteSpec"
          :options="eliteSpecOptions"
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
          :options="roleOptions"
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
        <InputText
          v-model="localForm.armorType"
          class="w-full"
          placeholder="如：狂战士、吟游诗人"
        />
      </div>
      <div class="flex items-center gap-3">
        <label class="text-sm font-medium">META 配置</label>
        <ToggleSwitch v-model="localForm.isMeta" />
      </div>
    </div>
  </Panel>
</template>

<script setup lang="ts">
import BaseButton from '@/components/common/ui/input/BaseButton.vue'
import BaseSelect from '@/components/common/ui/input/BaseSelect.vue'
import FormField from '@/components/common/ui/input/FormField.vue'
import type { SubRoleType } from '@/composables/build/useBuildEditDialog'
import { SUB_ROLE_OPTIONS } from '@/composables/build/useBuildEditDialog'
import type { BuildCreateDto } from '@/types/buildLibrary'
import InputText from 'primevue/inputtext'
import Panel from 'primevue/panel'
import ToggleSwitch from 'primevue/toggleswitch'
import { reactive, watch } from 'vue'

const props = defineProps<{
  form: BuildCreateDto
  professionOptions: { label: string; value: string }[]
  eliteSpecOptions: { label: string; value: string }[]
  roleOptions: { label: string; value: string }[]
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
