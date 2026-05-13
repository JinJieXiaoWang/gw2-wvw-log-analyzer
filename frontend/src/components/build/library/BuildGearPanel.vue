<template>
  <Panel
    header="配装"
    toggleable
  >
    <div class="space-y-3">
      <div class="grid grid-cols-2 gap-3">
        <div>
          <label class="block text-sm font-medium mb-1">Relic</label>
          <InputText
            v-model="localForm.relic"
            class="w-full"
            placeholder="古物名称"
          />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">符文</label>
          <InputText
            v-model="localForm.rune"
            class="w-full"
            placeholder="符文名称"
          />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">食物</label>
          <InputText
            v-model="localForm.food"
            class="w-full"
            placeholder="食物名称"
          />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">扳手</label>
          <InputText
            v-model="localForm.wrench"
            class="w-full"
            placeholder="扳手/保养油"
          />
        </div>
      </div>
      <div>
        <label class="block text-sm font-medium mb-1">灌注</label>
        <InputText
          v-model="localForm.infusion"
          class="w-full"
          placeholder="灌注类型"
        />
      </div>
      <div>
        <div class="flex items-center justify-between mb-2">
          <label class="text-sm font-medium">武器配置</label>
          <BaseButton
            icon="pi pi-plus"
            label="添加武器"
            size="small"
            text
            @click="$emit('add-weapon')"
          />
        </div>
        <div
          v-for="(w, idx) in localForm.weapons"
          :key="idx"
          class="flex items-start gap-2 mb-2"
        >
          <div class="flex-1 grid grid-cols-3 gap-2">
            <InputText
              v-model="w.name"
              placeholder="武器名称"
              class="w-full"
            />
            <InputText
              :model-value="w.sigils.join(',')"
              placeholder="法印（逗号分隔）"
              class="w-full col-span-2"
              @update:model-value="v => w.sigils = (v || '').split(',').map(s => s.trim()).filter(Boolean)"
            />
          </div>
          <BaseButton
            icon="pi pi-trash"
            severity="danger"
            text
            size="small"
            @click="$emit('remove-weapon', idx)"
          />
        </div>
      </div>
    </div>
  </Panel>
</template>

<script setup lang="ts">
import BaseButton from '@/components/common/ui/input/BaseButton.vue';
import type { BuildCreateDto } from '@/types/buildLibrary';
import InputText from 'primevue/inputtext';
import Panel from 'primevue/panel';
import { reactive, watch } from 'vue'

const props = defineProps<{
  form: BuildCreateDto
}>()

const emit = defineEmits<{
  'add-weapon': []
  'remove-weapon': [idx: number]
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
