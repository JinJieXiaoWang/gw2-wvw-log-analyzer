<template>
  <div
    class="bg-surface-0 dark:bg-surface-900 border border-surface-200 dark:border-surface-700 rounded-2xl p-5 shadow-sm"
  >
    <div class="flex items-center gap-3 mb-4">
      <div class="w-10 h-10 rounded-lg bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center">
        <i class="pi pi-upload text-white" />
      </div>
      <div>
        <h4 class="font-semibold text-color">
          上传与解析
        </h4>
        <span class="text-xs text-color-secondary">文件上传与战斗解析限制</span>
      </div>
    </div>
    <div class="space-y-4">
      <div class="flex items-center gap-3 p-3 bg-surface-50 dark:bg-surface-800 rounded-lg flex-wrap sm:flex-nowrap">
        <div class="flex items-center gap-3 flex-1 min-w-0">
          <div class="w-8 h-8 rounded flex items-center justify-center bg-violet-100 dark:bg-violet-900/30">
            <i class="pi pi-file text-violet-600 dark:text-violet-400" />
          </div>
          <div>
            <label class="text-sm font-medium text-color">最大上传文件大小</label>
            <p class="text-xs text-color-secondary">
              允许上传的单个文件最大容量
            </p>
          </div>
        </div>
        <BaseInputNumber
          v-model="localConfigs.upload_max_file_size"
          :min="1"
          :max="500"
          suffix=" MB"
          class="w-full sm:w-32 max-w-full"
          @blur="markChanged('upload_max_file_size')"
        />
      </div>
      <div class="flex items-center gap-3 p-3 bg-surface-50 dark:bg-surface-800 rounded-lg flex-wrap sm:flex-nowrap">
        <div class="flex items-center gap-3 flex-1 min-w-0">
          <div class="w-8 h-8 rounded flex items-center justify-center bg-violet-100 dark:bg-violet-900/30">
            <i class="pi pi-code text-violet-600 dark:text-violet-400" />
          </div>
          <div>
            <label class="text-sm font-medium text-color">允许的文件扩展名</label>
            <p class="text-xs text-color-secondary">
              JSON数组格式，如 [&quot;.zevtc&quot;, &quot;.evtc&quot;]
            </p>
          </div>
        </div>
        <BaseInput
          v-model="localConfigs.upload_allowed_extensions"
          class="w-full sm:w-56 max-w-full"
          @input="markChanged('upload_allowed_extensions')"
        />
      </div>
      <div class="flex items-center gap-3 p-3 bg-surface-50 dark:bg-surface-800 rounded-lg flex-wrap sm:flex-nowrap">
        <div class="flex items-center gap-3 flex-1 min-w-0">
          <div class="w-8 h-8 rounded flex items-center justify-center bg-violet-100 dark:bg-violet-900/30">
            <i class="pi pi-clock text-violet-600 dark:text-violet-400" />
          </div>
          <div>
            <label class="text-sm font-medium text-color">最大战斗时长</label>
            <p class="text-xs text-color-secondary">
              超过此时长的战斗将被截断分析
            </p>
          </div>
        </div>
        <BaseInputNumber
          v-model="localConfigs.analysis_max_fight_duration"
          :min="60"
          :max="7200"
          suffix=" 秒"
          class="w-full sm:w-32 max-w-full"
          @blur="markChanged('analysis_max_fight_duration')"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import BaseInputNumber from '@/components/common/ui/input/BaseInputNumber.vue'
import BaseInput from '@/components/common/ui/input/BaseInput.vue'
import { reactive, watch } from 'vue'

const props = defineProps<{
  configs: Record<string, any>
}>()

const emit = defineEmits<{
  markChanged: [key: string]
  'update:configs': [configs: Record<string, any>]
}>()

const localConfigs = reactive({ ...props.configs })

watch(() => props.configs, (val) => {
  Object.assign(localConfigs, val)
}, { deep: true })

watch(localConfigs, (val) => {
  emit('update:configs', { ...val })
}, { deep: true })

const markChanged = (key: string) => emit('markChanged', key)
</script>
