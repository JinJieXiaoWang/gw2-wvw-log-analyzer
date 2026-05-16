<template>
  <Dialog
    v-model:visible="localVisible"
    :header="isEdit ? '编辑配置' : '新增配置'"
    :style="{ width: '720px', maxWidth: '95vw' }"
    :modal="true"
    :closable="!submitting"
    :close-on-escape="!submitting"
    @hide="onHide"
  >
    <div class="space-y-4 max-h-[70vh] overflow-y-auto pr-2">
      <BuildBasicInfoPanel
        :form="form"
        :select-options="{ professionOptions, eliteSpecOptions, roleOptions }"
        :loading-dicts="loadingDicts"
        @toggle-sub-role="toggleSubRole"
      />
      <BuildGearPanel
        :form="form"
        @add-weapon="addWeapon"
        @remove-weapon="removeWeapon"
      />
      <BuildCodePanel
        :form="form"
        :parsing="parsing"
        @parse="parseBDCode"
      />
      <BuildTraitLinesPanel
        :form="form"
        @add="addTraitLine"
        @remove="removeTraitLine"
      />
      <BuildExtrasPanel
        :form="form"
        @add-rotation="addRotationCommand"
        @remove-rotation="removeRotationCommand"
        @add-mechanic="addMechanic"
        @remove-mechanic="removeMechanic"
        @add-mechanic-source="addMechanicSource"
        @remove-mechanic-source="removeMechanicSource"
        @add-video="addVideo"
        @remove-video="removeVideo"
        @add-attr="addAttrRequirement"
        @remove-attr="removeAttrRequirement"
      />`
    </div>
    
    <template #footer>
      <div class="flex justify-end gap-3">
        <BaseButton
          label="取消"
          severity="secondary"
          outlined
          :disabled="submitting"
          @click="localVisible = false"
        /><BaseButton
          :label="isEdit ? '保存修改' : '创建配置'"
          severity="primary"
          :loading="submitting"
          :disabled="!isValid"
          @click="onSubmit"
        />
      </div>
    </template>`
  </Dialog>
</template>

<script setup lang="ts">
import Dialog from 'primevue/dialog'
import BaseButton from '@/components/common/ui/input/BaseButton.vue'
import { useBuildEditDialog } from '@/composables/build/useBuildEditDialog'
import type { BuildEntry } from '@/types/buildLibrary'
import BuildBasicInfoPanel from './BuildBasicInfoPanel.vue'
import BuildGearPanel from './BuildGearPanel.vue'
import BuildCodePanel from './BuildCodePanel.vue'
import BuildTraitLinesPanel from './BuildTraitLinesPanel.vue'
import BuildExtrasPanel from './BuildExtrasPanel.vue'

const props = defineProps<{
  visible: boolean
  editingBuild?: BuildEntry | null
}>()

const emit = defineEmits<{
  'update:visible': [value: boolean]
  saved: [build: BuildEntry]
}>()

const {
  form, isEdit, submitting, loadingDicts,
  professionOptions, eliteSpecOptions, roleOptions,
  parsing, isValid, localVisible,
  toggleSubRole, addWeapon, removeWeapon,
  addTraitLine, removeTraitLine,
  addRotationCommand, removeRotationCommand,
  addMechanic, removeMechanic, addMechanicSource, removeMechanicSource,
  addVideo, removeVideo,
  addAttrRequirement, removeAttrRequirement,
  parseBDCode, onSubmit, onHide
} = useBuildEditDialog(props, emit)
</script>
