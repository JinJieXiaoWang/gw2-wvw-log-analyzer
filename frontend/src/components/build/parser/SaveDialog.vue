<template>
  <BaseDialog
    :visible="visible"
    header="保存Build配置"
    width="500"
    :modal="true"
    confirm-label="保存"
    :loading="isSaving"
    @update:visible="emit('update:visible', $event)"
    @confirm="handleSubmit(() => emit('save', formData))"
  >
    <form
      class="space-y-4"
      @submit.prevent="handleSubmit(() => emit('save', formData))"
    >
      <FormField
        label="Build名称"
        required
        :error="errors.title"
      >
        <InputText
          v-model="formData.title"
          class="w-full"
          placeholder="输入Build名称"
          :class="{ 'p-invalid': errors.title }"
        />
      </FormField>
      <FormField
        label="ְҵ"
        required
        :error="errors.profession"
      >
        <BaseSelect
          v-model="formData.profession"
          :options="professionOptions"
          option-label="label"
          option-value="value"
          class="w-full"
          placeholder="选择职业"
          :class="{ 'p-invalid': errors.profession }"
        />
      </FormField>
      <FormField
        label="职责"
        required
        :error="errors.role"
      >
        <BaseSelect
          v-model="formData.role"
          :options="roleOptions"
          option-label="label"
          option-value="value"
          class="w-full"
          placeholder="选择职责"
          :class="{ 'p-invalid': errors.role }"
        />
      </FormField>
      <FormField label="备注">
        <Textarea
          v-model="formData.notes"
          class="w-full"
          placeholder="添加备注说明"
          rows="3"
        />
      </FormField>
      <div class="flex items-center gap-2">
        <Checkbox
          v-model="formData.isMeta"
          input-id="isMeta"
        />
        <label
          for="isMeta"
          class="text-sm text-neutral-text"
        >标记为Meta Build</label>
      </div>
    </form>
  </BaseDialog>
</template>

<script setup lang="ts">
import { toRef } from 'vue'
import BaseDialog from '@/components/common/ui/feedback/BaseDialog.vue'
import InputText from 'primevue/inputtext'
import BaseSelect from '@/components/common/ui/input/BaseSelect.vue'
import Textarea from 'primevue/textarea'
import Checkbox from 'primevue/checkbox'
import FormField from '@/components/common/ui/input/FormField.vue'
import { useSaveDialog } from '@/composables/build/useSaveDialog'

const props = defineProps<{
  visible: boolean
  parsedData?: any
  buildCode?: string
}>()

const emit = defineEmits<{
  'update:visible': [value: boolean]
  'save': [data: any]
}>()

const { isSaving, formData, errors, professionOptions, roleOptions, handleSubmit } = useSaveDialog(toRef(() => props.visible), props.parsedData, props.buildCode)
</script>
