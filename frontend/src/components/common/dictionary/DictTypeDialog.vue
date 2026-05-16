<template>
  <BaseDialog
    v-model:visible="localVisible"
    header="编辑字典分类"
    width="450px"
    confirm-label="保存"
    :loading="saving"
    @confirm="$emit('save')"
  >
    <div class="space-y-4">
      <FormField label="分类名称 *">
        <InputText
          v-model="localForm.dict_name"
          placeholder="请输入分类名称"
          class="w-full"
        />
      </FormField>
      <FormField
        label="分类编码 *"
        hint="编码一旦创建不可修改"
      >
        <InputText
          v-model="localForm.dict_type"
          placeholder="请输入分类编码"
          :disabled="!!editingType"
          class="w-full"
        />
      </FormField>
      <FormField label="排序">
        <InputNumber
          v-model="localForm.sort_order"
          :min="0"
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
import { ref, watch, computed } from 'vue'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import Textarea from 'primevue/textarea'
import BaseDialog from '@/components/common/ui/feedback/BaseDialog.vue'

import FormField from '@/components/common/ui/input/FormField.vue'
import type { DictType } from '@/services/system/dictionaryService'

interface TypeForm {
  dict_name: string
  dict_type: string
  sort_order: number
  status: number
  remark: string
}

const props = defineProps<{
  visible: boolean
  editingType: DictType | null
  saving: boolean
  form: TypeForm

}>()

const emit = defineEmits<{
  'update:visible': [value: boolean]
  'update:form': [value: TypeForm]
  save: []
}>()

const localVisible = computed({
  get: () => props.visible,
  set: v => emit('update:visible', v)
})

const localForm = ref<TypeForm>({ ...props.form })
watch(() => props.form, (v) => { localForm.value = { ...v } }, { deep: true, immediate: true })
watch(localForm, (v) => { emit('update:form', { ...v }) }, { deep: true })
</script>
