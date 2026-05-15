<template>
  <BaseDialog
    v-model:visible="localVisible"
    :header="editingData ? '编辑字典项' : '新增字典项'"
    width="500px"
    :confirm-label="editingData ? '保存' : '新增'"
    :loading="saving"
    @confirm="$emit('save')"
  >
    <div class="space-y-4">
      <FormField label="显示标签 *">
        <InputText
          v-model="localForm.dict_label"
          placeholder="请输入显示标签"
          class="w-full"
        />
      </FormField>
      <FormField label="存储值 *">
        <InputText
          v-model="localForm.dict_value"
          placeholder="请输入存储值"
          class="w-full"
        />
      </FormField>
      <FormField label="排序">
        <InputNumber
          v-model="localForm.dict_sort"
          :min="0"
          class="w-full"
        />
      </FormField>
      <FormField label="CSS类">
        <ColorPickerInput v-model="localForm.css_class" />
      </FormField>
      <FormField label="列表类">
        <InputText
          v-model="localForm.list_class"
          placeholder="如: primary, secondary"
          class="w-full"
        />
      </FormField>
      <FormField label="状态">
        <DictSelect
          v-model="localForm.status"
          dict-type="sys_normal_disable"
          class="w-full"
        />
      </FormField>
      <FormField label="备注">
        <Textarea
          v-model="localForm.remark"
          placeholder="请输入备注说明"
          rows="3"
          class="w-full"
        />
      </FormField>
    </div>
  </BaseDialog>
</template>

<script setup lang="ts">
import BaseDialog from '@/components/common/ui/feedback/BaseDialog.vue'

import ColorPickerInput from '@/components/common/ui/input/ColorPickerInput.vue'
import FormField from '@/components/common/ui/input/FormField.vue'
import type { DictData } from '@/services/system/dictionaryService'
import InputNumber from 'primevue/inputnumber'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'
import { computed, ref, watch } from 'vue'

interface DataForm {
  dict_label: string
  dict_value: string
  dict_sort: number
  css_class: string
  list_class: string
  status: number
  remark: string
}

const visible = defineModel<boolean>('visible', { default: false })
const form = defineModel<DataForm>('form', {
  default: () => ({ dict_label: '', dict_value: '', dict_sort: 0, css_class: '', list_class: '', status: 0, remark: '' })
})

const props = defineProps<{
  editingData: DictData | null
  saving: boolean

}>()

const emit = defineEmits<{
  save: []
}>()

const localVisible = computed({
  get: () => visible.value,
  set: v => visible.value = v
})

const localForm = ref<DataForm>({ ...form.value })
watch(() => form.value, (v) => { localForm.value = { ...v } }, { deep: true, immediate: true })
watch(localForm, (v) => { form.value = { ...v } }, { deep: true })
</script>
