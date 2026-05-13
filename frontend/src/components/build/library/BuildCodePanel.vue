<template>
  <Panel
    header="Build 代码"
    toggleable
    :collapsed="false"
  >
    <div>
      <label class="block text-sm font-medium mb-1">BD Code <span class="text-red-400">*</span></label>
      <div class="flex gap-2">
        <Textarea
          v-model="localForm.bdCode"
          class="w-full font-mono flex-1"
          rows="2"
          placeholder="[&...]"
        />
        <BaseButton
          icon="pi pi-bolt"
          label="解析"
          severity="help"
          :loading="parsing"
          :disabled="!localForm.bdCode.trim().startsWith('[&')"
          @click="$emit('parse')"
        />
      </div>
      <p class="text-xs text-surface-500 mt-1">
        输入 BD Code 后点击「解析」可自动填充ְ职业、特性线等数据
      </p>
    </div>
  </Panel>
</template>

<script setup lang="ts">
import BaseButton from '@/components/common/ui/input/BaseButton.vue';
import type { BuildCreateDto } from '@/types/buildLibrary';
import Panel from 'primevue/panel';
import Textarea from 'primevue/textarea';
import { reactive, watch } from 'vue'

const props = defineProps<{
  form: BuildCreateDto
  parsing: boolean
}>()

const emit = defineEmits<{
  parse: []
  'update:form': [form: BuildCreateDto]
}>()

const localForm = reactive({ ...props.form })

watch(() => props.form, (val) => {
  Object.assign(localForm, val)
}, { deep: true })

watch(localForm, (val) => {
  emit('update:form', { ...val })
}, { deep: true })
</script>
