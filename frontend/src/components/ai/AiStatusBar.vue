<template>
  <div class="mt-6 flex flex-wrap items-center gap-3">
    <div class="flex items-center gap-2 px-4 py-2.5 bg-neutral-card/80 backdrop-blur-sm rounded-xl border border-neutral-border hover:border-ai/50 transition-all">
      <div
        class="w-2.5 h-2.5 rounded-full relative"
        :class="config.enabled ? 'bg-ai' : 'bg-error'"
      >
        <div
          v-if="config.enabled"
          class="absolute inset-0 bg-ai rounded-full animate-ping opacity-50"
        />
      </div>
      <span
        class="text-sm font-medium"
        :class="config.enabled ? 'text-ai' : 'text-error'"
      >
        {{ config.enabled ? 'AI服务已启用' : 'AI服务未配置' }}
      </span>
    </div>
    <div class="flex items-center gap-2 px-4 py-2.5 bg-neutral-card/80 backdrop-blur-sm rounded-xl border border-neutral-border">
      <SvgIcon
        icon="hard-drive"
        :size="16"
        class="text-primary"
      />
      <span class="text-sm text-neutral-text-secondary">缓存命中: <span class="text-primary font-semibold">{{ stats.cache_hit_rate }}%</span></span>
    </div>
    <div class="flex items-center gap-2 px-4 py-2.5 bg-neutral-card/80 backdrop-blur-sm rounded-xl border border-neutral-border">
      <SvgIcon
        icon="file-text"
        :size="16"
        class="text-secondary"
      />
      <span class="text-sm text-neutral-text-secondary">已分析 <span class="text-secondary font-semibold">{{ stats.today_count }}</span> 份报告</span>
    </div>
    <div class="flex items-center gap-2 px-4 py-2.5 bg-neutral-card/80 backdrop-blur-sm rounded-xl border border-neutral-border">
      <SvgIcon
        icon="zap"
        :size="16"
        class="text-ai"
      />
      <span class="text-sm text-neutral-text-secondary">响应延迟: <span class="text-ai font-semibold">{{ stats.response_time }}ms</span></span>
    </div>
  </div>
</template>

<script setup lang="ts">
import SvgIcon from '@/components/common/ui/display/SvgIcon.vue'

interface AiConfig { enabled: boolean; provider: string; has_api_key: boolean; cache_enabled: boolean; fallback_enabled: boolean }
interface AiStats { cache_hit_rate: number; cache_entries: number; today_count: number; response_time: number }

defineProps<{ config: AiConfig; stats: AiStats }>()
defineEmits<{ 'test-connection': [] }>()
</script>
