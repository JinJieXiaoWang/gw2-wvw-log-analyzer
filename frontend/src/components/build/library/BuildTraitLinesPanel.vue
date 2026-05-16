<template>
  <Panel
    header="特性线"
    toggleable
  >
    <div class="space-y-2">
      <div
        v-for="(t, idx) in form.traitLines"
        :key="idx"
        class="flex items-center gap-2"
      >
        <InputText
          v-model="t.name"
          placeholder="特性线名称"
          class="flex-1"
        />
        <div class="flex gap-1">
          <BaseSelect
            v-for="cIdx in [0,1,2]"
            :key="cIdx"
            v-model="t.choices[cIdx]"
            :options="[1,2,3]"
            class="w-14"
          />
        </div>
        <BaseButton
          icon="pi pi-trash"
          severity="danger"
          text
          size="small"
          @click="$emit('remove', idx)"
        />
      </div>
      <BaseButton
        icon="pi pi-plus"
        label="添加特性线"
        size="small"
        text
        @click="$emit('add')"
      />
    </div>
  </Panel>
</template>

<script setup lang="ts">
import InputText from 'primevue/inputtext'
import BaseSelect from '@/components/common/ui/input/BaseSelect.vue'
import Panel from 'primevue/panel'
import BaseButton from '@/components/common/ui/input/BaseButton.vue'
import type { BuildCreateDto } from '@/types/buildLibrary'

defineProps<{
  form: BuildCreateDto
}>()

defineEmits<{
  add: []
  remove: [idx: number]
}>()
</script>
