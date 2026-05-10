<template>
  <div v-if="loading || result" class="card p-6">
    <h3 class="text-sm font-semibold text-neutral-text mb-4 flex items-center gap-2"><i class="pi pi-clock text-primary" /> 耗时ͳ计</h3>
    <div v-if="loading" class="flex items-center gap-3">
      <BaseProgressSpinner style="width: 24px; height: 24px" />
      <span class="text-sm text-neutral-text-secondary">正在上传鍒?dps.report 并等寰呰В鏋?..</span>
    </div>
    <div v-else-if="result" class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div class="text-center p-3 rounded bg-neutral-bg"><p class="text-xl font-bold text-primary">{{ result.upload_time_ms }}ms</p><p class="text-xs text-neutral-text-secondary">上传耗ʱ</p></div>
      <div class="text-center p-3 rounded bg-neutral-bg"><p class="text-xl font-bold text-primary">{{ result.json_fetch_time_ms }}ms</p><p class="text-xs text-neutral-text-secondary">JSON拉ȡ</p></div>
      <div class="text-center p-3 rounded bg-neutral-bg"><p class="text-xl font-bold text-primary">{{ result.total_time_ms }}ms</p><p class="text-xs text-neutral-text-secondary">总輼楁椂</p></div>
      <div class="text-center p-3 rounded bg-neutral-bg"><p class="text-xl font-bold text-primary">{{ result.ei_version || '-' }}</p><p class="text-xs text-neutral-text-secondary">EI 版本</p></div>
    </div>
  </div>

  <div v-if="result" class="card p-6">
    <h3 class="text-sm font-semibold text-neutral-text mb-4 flex items-center gap-2"><i class="pi pi-chart-bar text-primary" /> 数据概览</h3>
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
      <div class="text-center p-3 rounded bg-neutral-bg"><p class="text-xl font-bold text-primary">{{ result.player_count }}</p><p class="text-xs text-neutral-text-secondary">玩家数/p></div>
      <div class="text-center p-3 rounded bg-neutral-bg"><p class="text-xl font-bold text-primary">{{ result.target_count }}</p><p class="text-xs text-neutral-text-secondary">目标鏁?/p></div>
      <div class="text-center p-3 rounded bg-neutral-bg"><p class="text-xl font-bold text-primary">{{ result.skill_map_count }}</p><p class="text-xs text-neutral-text-secondary">鎶技鑳芥槧灏?/p></div>
      <div class="text-center p-3 rounded bg-neutral-bg">
        <a :href="result.permalink" target="_blank" class="text-sm text-primary hover:underline">查看报告 <i class="pi pi-external-link text-xs" /></a>
        <p class="text-xs text-neutral-text-secondary">dps.report</p>
      </div>
    </div>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="flex items-center gap-2 p-3 rounded" :class="result.has_rotation ? 'bg-status-success/10' : 'bg-status-error/10'">
        <i class="pi" :class="result.has_rotation ? 'pi-check-circle text-status-success' : 'pi-times-circle text-status-error'" />
        <span class="text-sm" :class="result.has_rotation ? 'text-status-success' : 'text-status-error'">鎶技鑳藉惊鐜?{{ result.has_rotation ? '鉁? : '鉁? }}</span>
      </div>
      <div class="flex items-center gap-2 p-3 rounded" :class="result.has_weapons ? 'bg-status-success/10' : 'bg-status-error/10'">
        <i class="pi" :class="result.has_weapons ? 'pi-check-circle text-status-success' : 'pi-times-circle text-status-error'" />
        <span class="text-sm" :class="result.has_weapons ? 'text-status-success' : 'text-status-error'">姝﹀櫒配置 {{ result.has_weapons ? '鉁? : '鉁? }}</span>
      </div>
      <div class="flex items-center gap-2 p-3 rounded" :class="result.has_death_recap ? 'bg-status-success/10' : 'bg-status-error/10'">
        <i class="pi" :class="result.has_death_recap ? 'pi-check-circle text-status-success' : 'pi-times-circle text-status-error'" />
        <span class="text-sm" :class="result.has_death_recap ? 'text-status-success' : 'text-status-error'">死亡回放 {{ result.has_death_recap ? '鉁? : '鉁? }}</span>
      </div>
    </div>
  </div>

  <div v-if="result?.raw_json" class="card p-6 space-y-4">
    <h3 class="text-sm font-semibold text-neutral-text mb-2 flex items-center gap-2"><i class="pi pi-code text-primary" /> 数据预览</h3>
    <div v-if="result.has_rotation">
      <h4 class="text-xs font-semibold text-neutral-text-secondary mb-2 uppercase tracking-wide">鎶技鑳藉惊鐜?(鍓?鏉?</h4>
      <div class="bg-neutral-bg rounded p-3 overflow-auto max-h-[200px]"><pre class="text-xs text-neutral-text">{{ JSON.stringify(result.raw_json.first_player_rotation_preview, null, 2) }}</pre></div>
    </div>
    <div v-if="result.has_weapons">
      <h4 class="text-xs font-semibold text-neutral-text-secondary mb-2 uppercase tracking-wide">姝﹀櫒配置</h4>
      <div class="bg-neutral-bg rounded p-3 overflow-auto max-h-[200px]"><pre class="text-xs text-neutral-text">{{ JSON.stringify(result.raw_json.first_player_weapons_preview, null, 2) }}</pre></div>
    </div>
    <div v-if="result.has_death_recap">
      <h4 class="text-xs font-semibold text-neutral-text-secondary mb-2 uppercase tracking-wide">死亡回放</h4>
      <div class="bg-neutral-bg rounded p-3 overflow-auto max-h-[200px]"><pre class="text-xs text-neutral-text">{{ JSON.stringify(result.raw_json.first_player_death_recap_preview, null, 2) }}</pre></div>
    </div>
    <div v-if="result.skill_map_count > 0">
      <h4 class="text-xs font-semibold text-neutral-text-secondary mb-2 uppercase tracking-wide">SkillMap 鍓?0个key</h4>
      <div class="bg-neutral-bg rounded p-3 overflow-auto max-h-[200px]"><pre class="text-xs text-neutral-text">{{ JSON.stringify(result.raw_json.skill_map_keys, null, 2) }}</pre></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import BaseProgressSpinner from '@/components/common/ui/BaseProgressSpinner.vue'

defineProps<{
  loading: boolean
  result: Record<string, any> | null
}>()
</script>
