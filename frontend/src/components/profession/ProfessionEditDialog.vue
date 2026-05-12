<template>
  <Dialog
    v-model:visible="visible"
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
        <label class="block text-sm text-neutral-text-secondary mb-1">默认角色</label>
        <BaseSelect
          v-model="form.default_role"
          :options="roleOptions"
          option-label="label"
          option-value="value"
          placeholder="选择角色定位"
          class="w-full"
        />
      </div>
      <div class="flex items-center gap-2">
        <label class="text-sm text-neutral-text-secondary">状态</label>
        <ToggleSwitch v-model="form.is_active" />
        <span class="text-sm text-neutral-text">{{ form.is_active ? '启用' : '禁用' }}</span>
      </div>
    </div>
    <template #footer>
      <BaseButton
        label="取消"
        variant="secondary"
        size="small"
        @click="visible = false"
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

const visible = defineModel<boolean>('visible', { required: true })

defineProps<{
  title: string
  form: any
  roleOptions: { label: string; value: string }[]
  loading: boolean
}>()

defineEmits<{
  save: []
}>()
</script>
