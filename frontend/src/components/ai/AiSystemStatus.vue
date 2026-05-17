<template>
  <div>
    <div class="flex items-center gap-3 mb-6">
      <div class="p-2 bg-gradient-to-br from-ai to-emerald-500 rounded-xl">
        <SvgIcon
          icon="activity"
          :size="24"
          class="text-white"
        />
      </div>
      <h2 class="text-xl font-bold text-white">
        系统状态
      </h2>
    </div>
    <div class="space-y-3">
      <div
        class="flex items-center justify-between p-3 bg-neutral-card-active/50 rounded-xl cursor-pointer"
        @click="$emit('test-connection')"
      >
        <div class="flex items-center gap-3">
          <div
            class="w-3 h-3 rounded-full relative"
            :class="config.enabled ? 'bg-ai' : 'bg-error'"
          >
            <div
              v-if="config.enabled"
              class="absolute inset-0 bg-ai rounded-full animate-ping opacity-50"
            />
          </div>
          <span class="text-neutral-text-secondary text-sm">AI服务状态</span>
        </div>
        <div class="flex items-center gap-2">
          <span
            :class="config.enabled ? 'text-ai' : 'text-error'"
            class="text-sm font-semibold"
          >{{ config.enabled ? '在线' : '离线' }}</span>
          <SvgIcon
            icon="chevron-right"
            :size="16"
            class="text-neutral-text-tertiary"
          />
        </div>
      </div>
      <div class="flex items-center justify-between p-3 bg-neutral-card-active/50 rounded-xl">
        <span class="text-neutral-text-tertiary text-sm">提供商</span><span class="text-white text-sm font-medium">{{ config.provider }}</span>
      </div>
      <div class="flex items-center justify-between p-3 bg-neutral-card-active/50 rounded-xl">
        <span class="text-neutral-text-tertiary text-sm">响应延迟</span><span class="text-white text-sm font-medium">{{ stats.response_time }}ms</span>
      </div>
      <div class="flex items-center justify-between p-3 bg-neutral-card-active/50 rounded-xl">
        <span class="text-neutral-text-tertiary text-sm">今日分析</span><span class="text-white text-sm font-medium">{{ stats.today_count }}</span>
      </div>
      <div class="flex items-center justify-between p-3 bg-neutral-card-active/50 rounded-xl">
        <span class="text-neutral-text-tertiary text-sm">缓存条目</span><span class="text-white text-sm font-medium">{{ stats.cache_entries }}</span>
      </div>
    </div>
    <button
      :disabled="testingConnection"
      class="w-full mt-6 flex items-center justify-center gap-2 px-5 py-3 bg-gradient-to-r from-neutral-card-active to-neutral-card hover:from-primary/20 hover:to-primary/10 rounded-xl transition-all font-medium border border-neutral-border"
      @click="$emit('test-connection')"
    >
      <svg
        v-if="testingConnection"
        class="animate-spin h-5 w-5 text-primary"
        viewBox="0 0 24 24"
      ><circle
        class="opacity-25"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        stroke-width="4"
        fill="none"
      /><path
        class="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
      /></svg>
      <SvgIcon
        v-else
        icon="wifi"
        :size="18"
        class="text-primary"
      />
      <span class="text-neutral-text-secondary">{{ testingConnection ? '测试中...' : '测试连接' }}</span>
    </button>
  </div>
</template>

<script setup lang="ts">
import SvgIcon from '@/components/common/ui/display/SvgIcon.vue'

interface AiConfig { enabled: boolean; provider: string; has_api_key: boolean; cache_enabled: boolean; fallback_enabled: boolean }
interface AiStats { cache_hit_rate: number; cache_entries: number; today_count: number; response_time: number }

defineProps<{ config: AiConfig; stats: AiStats; testingConnection: boolean }>()
defineEmits<{ 'test-connection': [] }>()
</script>
