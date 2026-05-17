<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center gap-3">
        <div class="p-2 bg-gradient-to-br from-warning/20 to-amber-500/20 rounded-xl">
          <SvgIcon
            icon="lightbulb"
            :size="24"
            class="text-warning"
          />
        </div>
        <h2 class="text-xl font-bold text-white">
          AI优化建议
        </h2>
      </div>
      <button
        :disabled="loading"
        class="flex items-center gap-2 px-4 py-2 bg-neutral-card-active/50 hover:bg-neutral-card-active rounded-lg transition-colors"
        @click="$emit('refresh')"
      >
        <SvgIcon
          icon="refresh-cw"
          :size="16"
          :class="{ 'animate-spin': loading }"
          class="text-neutral-text-tertiary"
        />
        <span class="text-sm text-neutral-text-tertiary">刷新</span>
      </button>
    </div>
    <div
      v-if="loading"
      class="space-y-3"
    >
      <div
        v-for="i in 3"
        :key="i"
        class="h-16 bg-neutral-card-active/50 rounded-xl animate-pulse"
      />
    </div>
    <div
      v-else-if="data"
      class="space-y-3"
    >
      <div
        v-for="(suggestion, index) in data.suggestions"
        :key="index"
        class="p-4 bg-neutral-card-active/50 rounded-xl hover:bg-neutral-card-active transition-colors"
      >
        <p class="text-sm text-neutral-text-secondary">
          {{ suggestion }}
        </p>
      </div>
    </div>
    <div
      v-else
      class="text-center py-8"
    >
      <p class="text-neutral-text-tertiary">
        暂无建议数据
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import SvgIcon from '@/components/common/ui/display/SvgIcon.vue'

interface SuggestionsData { suggestions: string[]; high_priority?: string[] }
defineProps<{ data: SuggestionsData | null; loading: boolean }>()
defineEmits<{ refresh: [] }>()
</script>
