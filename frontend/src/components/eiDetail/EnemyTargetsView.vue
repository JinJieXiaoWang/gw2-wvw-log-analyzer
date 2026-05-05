<template>
  <div class="enemy-targets-view space-y-6">
    <!-- 目标统计 -->
    <div class="card">
      <h3 class="text-lg font-semibold text-neutral-text mb-4">
        <i class="pi pi-exclamation-circle text-status-error mr-2" />
        敌方目标统计
      </h3>
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
        <div class="p-4 rounded-lg bg-neutral-bg/50 text-center">
          <p class="text-3xl font-bold text-status-error">
            {{ targets.length }}
          </p>
          <p class="text-sm text-neutral-text-secondary mt-1">
            总目标数
          </p>
        </div>
        <div class="p-4 rounded-lg bg-neutral-bg/50 text-center">
          <p class="text-3xl font-bold text-primary">
            {{ enemyPlayerCount }}
          </p>
          <p class="text-sm text-neutral-text-secondary mt-1">
            敌方玩家
          </p>
        </div>
        <div class="p-4 rounded-lg bg-neutral-bg/50 text-center">
          <p class="text-3xl font-bold text-secondary">
            {{ npcCount }}
          </p>
          <p class="text-sm text-neutral-text-secondary mt-1">
            NPC
          </p>
        </div>
        <div class="p-4 rounded-lg bg-neutral-bg/50 text-center">
          <p class="text-3xl font-bold text-status-warning">
            {{ professionCounts.length }}
          </p>
          <p class="text-sm text-neutral-text-secondary mt-1">
            职业种类
          </p>
        </div>
      </div>

      <!-- 敌方玩家列表 -->
      <div
        v-if="enemyPlayers.length > 0"
        class="mb-6"
      >
        <h4 class="text-base font-medium text-neutral-text mb-3">
          <i class="pi pi-users text-status-error mr-1" />
          敌方玩家 ({{ enemyPlayers.length }})
        </h4>
        <div class="flex flex-wrap gap-2">
          <div
            v-for="target in enemyPlayers"
            :key="target.instanceID"
            class="flex items-center gap-2 px-3 py-2 rounded-lg bg-neutral-bg border border-neutral-border"
          >
            <img
              v-if="target.icon"
              :src="target.icon"
              class="w-6 h-6 rounded"
              :alt="target.name"
              @error="handleImgError"
            >
            <i
              v-else
              class="pi pi-user text-status-error"
            />
            <span class="text-sm text-neutral-text">{{ target.name || '未知' }}</span>
            <Tag
              v-if="target.enemyPlayer"
              value="玩家"
              severity="danger"
              class="text-xs"
            />
          </div>
        </div>
      </div>

      <!-- 职业分布 -->
      <div v-if="professionCounts.length > 0">
        <h4 class="text-base font-medium text-neutral-text mb-3">
          <i class="pi pi-chart-pie text-primary mr-1" />
          职业分布
        </h4>
        <div class="flex flex-wrap gap-2">
          <div
            v-for="pc in professionCounts"
            :key="pc.profession"
            class="flex items-center gap-2 px-3 py-2 rounded-lg bg-neutral-bg"
          >
            <span
              class="w-3 h-3 rounded-full"
              :style="{ backgroundColor: getProfessionColor(pc.profession) }"
            />
            <span class="text-sm text-neutral-text">{{ pc.profession }}</span>
            <span class="text-sm font-semibold text-primary">{{ pc.count }}</span>
          </div>
        </div>
      </div>

      <div
        v-if="targets.length === 0"
        class="text-center py-8 text-neutral-text-secondary"
      >
        <i class="pi pi-inbox text-4xl mb-2" />
        <p>暂无敌方目标数据</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import Tag from 'primevue/tag';
import { getProfessionColor } from '@/utils/profession/professionUtils';

const props = defineProps<{
  targets: any[];
}>();

const enemyPlayers = computed(() => props.targets.filter(t => t.enemyPlayer));
const npcs = computed(() => props.targets.filter(t => !t.enemyPlayer));
const enemyPlayerCount = computed(() => enemyPlayers.value.length);
const npcCount = computed(() => npcs.value.length);

const professionCounts = computed(() => {
  const counts: Record<string, number> = {};
  enemyPlayers.value.forEach(t => {
    const prof = t.profession || 'Unknown';
    counts[prof] = (counts[prof] || 0) + 1;
  });
  return Object.entries(counts)
    .map(([profession, count]) => ({ profession, count }))
    .sort((a, b) => b.count - a.count);
});

function handleImgError(e: Event) {
  const img = e.target as HTMLImageElement;
  if (img) img.style.display = 'none';
}
</script>
