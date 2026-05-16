<template>
  <header class="mb-8">
    <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
      <div class="flex items-center gap-4">
        <div class="p-4 bg-gradient-to-br from-primary via-purple-600 to-indigo-700 rounded-2xl shadow-lg shadow-primary/20">
          <SvgIcon icon="brain" :size="32" class="text-white" />
        </div>
        <div>
          <h1 class="text-3xl lg:text-4xl font-bold text-white tracking-tight">{{ pageTitle }}</h1>
          <p class="text-neutral-text-secondary mt-1.5">{{ pageSubtitle }}</p>
        </div>
      </div>
      <div class="flex items-center gap-3">
        <button @click="$emit('refresh')" :disabled="isRefreshing" class="flex items-center gap-2 px-5 py-2.5 bg-neutral-card hover:bg-neutral-card-hover border border-neutral-border rounded-xl transition-all">
          <SvgIcon v-if="!isRefreshing" icon="refresh-cw" :size="18" class="text-neutral-text-secondary" />
          <span v-else class="animate-spin"><SvgIcon icon="loader" :size="18" /></span>
          <span class="text-neutral-text-secondary">{{ isRefreshing ? btnRefreshing : btnRefresh }}</span>
        </button>
        <button @click="$emit('toggleConfig')" class="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-primary to-indigo-600 hover:from-primary-light hover:to-indigo-500 text-white rounded-xl transition-all font-medium">
          <SvgIcon icon="settings" :size="18" />
          <span>{{ btnConfigManage }}</span>
        </button>
      </div>
    </div>
    <AiStatusBar :config="aiConfig" :stats="aiStats" @test-connection="$emit('testConnection')" />
  </header>
</template>

<script setup lang="ts">
import AiStatusBar from './AiStatusBar.vue'
import SvgIcon from '@/components/common/ui/display/SvgIcon.vue'

interface Props {
  pageTitle: string
  pageSubtitle: string
  isRefreshing: boolean
  btnRefresh: string
  btnRefreshing: string
  btnConfigManage: string
  aiConfig: { enabled: boolean; provider: string; has_api_key: boolean; cache_enabled: boolean; fallback_enabled: boolean }
  aiStats: { cache_hit_rate: number; cache_entries: number; today_count: number; response_time: number }
}

defineProps<Props>()

defineEmits<{
  refresh: []
  toggleConfig: []
  testConnection: []
}>()
</script>

<script lang="ts">
export default { name: 'AiAnalysisPageHeader' }
</script>
