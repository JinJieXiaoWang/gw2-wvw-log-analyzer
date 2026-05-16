<template>
  <Dialog
    :visible="visible"
    :header="title"
    :style="{ width: '400px' }"
    :modal="true"
    :draggable="false"
  >
    <div
      v-if="form"
      class="space-y-4"
    >
      <div>
        <label class="block text-sm text-neutral-text-secondary mb-1">角色定位</label>
        <BaseSelect
          v-model="localForm.role_type"
          :options="roleOptions"
          option-label="label"
          option-value="value"
          placeholder="选择角色定位"
          class="w-full"
        />
      </div>
      <div class="flex items-center gap-2">
        <label class="text-sm text-neutral-text-secondary">状态</label>
        <ToggleSwitch v-model="localForm.is_active" />
        <span class="text-sm text-neutral-text">{{ localForm.is_active ? '启用' : '禁用' }}</span>
      </div>
    </div>
    <template #footer>
      <BaseButton
        label="取消"
        variant="secondary"
        size="small"
        @click="$emit('update:visible', false)"
      />
      <BaseButton
        label="保存"
        icon="pi pi-check"
        variant="primary"
        size="small"
        :loading="loading"
        @click="$emit('save')"
      />
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import Dialog from 'primevue/dialog'
import ToggleSwitch from 'primevue/toggleswitch'
import BaseSelect from '@/components/common/ui/input/BaseSelect.vue'
import BaseButton from '@/components/common/ui/input/BaseButton.vue'
import { reactive, watch } from 'vue'

const props = defineProps<{
  visible: boolean
  title: string
  form: any
  roleOptions: { label: string; value: string }[]
  loading: boolean
}>()

const emit = defineEmits<{
  'update:visible': [boolean]
  'update:form': [form: any]
  save: []
}>()

const localForm = reactive<any>({})

watch(() => props.form, (val) => {
  Object.assign(localForm, val ?? {})
}, { deep: true, immediate: true })

watch(localForm, (val) => {
  emit('update:form', { ...val })
}, { deep: true })
</script>
