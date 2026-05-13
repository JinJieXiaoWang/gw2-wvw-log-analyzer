<template>
  <Panel
    header="ָ挥口令"
    toggleable
  >
    <div class="space-y-2">
      <div
        v-for="(c, idx) in localForm.rotationCommands"
        :key="idx"
        class="grid grid-cols-[1fr_2fr_auto] gap-2 items-center"
      >
        <InputText
          v-model="c.callout"
          placeholder="口令"
        />
        <InputText
          v-model="c.action"
          placeholder="操作说明"
        />
        <BaseButton
          icon="pi pi-trash"
          severity="danger"
          text
          size="small"
          @click="$emit('remove-rotation', idx)"
        />
      </div>
      <BaseButton
        icon="pi pi-plus"
        label="添加口令"
        size="small"
        text
        @click="$emit('add-rotation')"
      />
    </div>
  </Panel>

  <Panel
    header="关键机制"
    toggleable
  >
    <div class="space-y-2">
      <div
        v-for="(m, idx) in localForm.mechanics"
        :key="idx"
        class="space-y-2 p-3 rounded-lg bg-surface-900 border border-surface-700"
      >
        <div class="flex items-center gap-2">
          <InputText
            v-model="m.name"
            placeholder="机制名称"
            class="flex-1"
          />
          <BaseButton
            icon="pi pi-trash"
            severity="danger"
            text
            size="small"
            @click="$emit('remove-mechanic', idx)"
          />
        </div>
        <div
          v-for="(_, sIdx) in m.sources"
          :key="sIdx"
          class="flex items-center gap-2"
        >
          <InputText
            v-model="m.sources[sIdx]"
            placeholder="来源说明"
            class="flex-1"
          />
          <BaseButton
            icon="pi pi-trash"
            severity="danger"
            text
            size="small"
            @click="$emit('remove-mechanic-source', idx, sIdx)"
          />
        </div>
        <BaseButton
          icon="pi pi-plus"
          label="添加来源"
          size="small"
          text
          @click="$emit('add-mechanic-source', idx)"
        />
      </div>
      <BaseButton
        icon="pi pi-plus"
        label="添加机制"
        size="small"
        text
        @click="$emit('add-mechanic')"
      />
    </div>
  </Panel>

  <Panel
    header="参考视频"
    toggleable
  >
    <div class="space-y-2">
      <div
        v-for="(v, idx) in localForm.videos"
        :key="idx"
        class="grid grid-cols-[1fr_1fr_auto] gap-2 items-center"
      >
        <InputText
          v-model="v.title"
          placeholder="视频标题"
        />
        <InputText
          v-model="v.url"
          placeholder="视频链接"
        />
        <BaseButton
          icon="pi pi-trash"
          severity="danger"
          text
          size="small"
          @click="$emit('remove-video', idx)"
        />
      </div>
      <BaseButton
        icon="pi pi-plus"
        label="添加视频"
        size="small"
        text
        @click="$emit('add-video')"
      />
    </div>
  </Panel>

  <Panel
    header="属性要求"
    toggleable
  >
    <div class="space-y-2">
      <div
        v-for="(_, idx) in localForm.attrRequirements"
        :key="idx"
        class="flex items-center gap-2"
      >
        <InputText
          v-model="localForm.attrRequirements[idx]"
          placeholder="属性要求说明"
          class="flex-1"
        />
        <BaseButton
          icon="pi pi-trash"
          severity="danger"
          text
          size="small"
          @click="$emit('remove-attr', idx)"
        />
      </div>
      <BaseButton
        icon="pi pi-plus"
        label="添加要求"
        size="small"
        text
        @click="$emit('add-attr')"
      />
    </div>
  </Panel>
</template>

<script setup lang="ts">
import InputText from 'primevue/inputtext'
import Panel from 'primevue/panel'
import BaseButton from '@/components/common/ui/input/BaseButton.vue'
import type { BuildCreateDto } from '@/types/buildLibrary'
import { reactive, watch } from 'vue'

const props = defineProps<{
  form: BuildCreateDto
}>()

const emit = defineEmits<{
  'add-rotation': []
  'remove-rotation': [idx: number]
  'add-mechanic': []
  'remove-mechanic': [idx: number]
  'add-mechanic-source': [mechIdx: number]
  'remove-mechanic-source': [mechIdx: number, srcIdx: number]
  'add-video': []
  'remove-video': [idx: number]
  'add-attr': []
  'remove-attr': [idx: number]
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
