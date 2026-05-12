<template>
  <BaseDialog
    v-model:visible="localVisible"
    header="编辑字典分类"
    width="450px"
    confirm-label="保存"
    :loading="saving"
    @confirm="$emit('save')"
  >
    <div class="dialog-form">
      <div class="form-row">
        <label class="form-label">分类名称 *</label>
        <InputText
          v-model="localForm.dict_name"
          placeholder="请输入分类名称"
          class="w-full"
        />
      </div>
      <div class="form-row">
        <label class="form-label">分类编码 *</label>
        <InputText
          v-model="localForm.dict_type"
          placeholder="请输入分类编码"
          :disabled="!!editingType"
          class="w-full"
        />
        <small class="form-hint">编码一旦创建不可修改</small>
      </div>
      <div class="form-row">
        <label class="form-label">排序</label>
        <InputNumber
          v-model="localForm.sort_order"
          :min="0"
          class="w-full"
        />
      </div>
      <div class="form-row">
        <label class="form-label">状态</label>
        <BaseSelect
          v-model="localForm.status"
          :options="statusOptions"
          option-label="label"
          option-value="value"
          class="w-full"
        />
      </div>
      <div class="form-row">
        <label class="form-label">备注</label>
        <Textarea
          v-model="localForm.remark"
          placeholder="请输入备注说明"
          rows="3"
          class="w-full"
        />
      </div>
    </div>
  </BaseDialog>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import Textarea from 'primevue/textarea'
import BaseDialog from '@/components/common/ui/feedback/BaseDialog.vue'
import BaseSelect from '@/components/common/ui/input/BaseSelect.vue'
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
  statusOptions: { label: string; value: number | null }[]
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

<style scoped>
.dialog-form { display: flex; flex-direction: column; gap: 16px; }
.form-row { display: flex; flex-direction: column; gap: 6px; }
.form-label { font-size: 14px; font-weight: 500; color: #e5e5e5; }
.form-hint { font-size: 12px; color: #909399; }
</style>
