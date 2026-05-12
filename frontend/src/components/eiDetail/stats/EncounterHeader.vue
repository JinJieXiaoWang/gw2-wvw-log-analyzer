<template>
  <div class="encounter-header p-[1.25rem 1.5rem]">
    <div class="header-main flex items-center justify-between gap-6">
      <div class="header-left flex items-center gap-4">
        <div class="fight-icon w-12 h-12 flex items-center justify-center bg-[linear-gradient(135deg, var(--color-primary), var(--color-secondary))] rounded-xl">
          <i class="pi pi-sword text-2xl text-white" />
        </div>
        <div class="fight-info flex-1">
          <h1 class="fight-name text-[1.375rem] font-semibold text-neutral-text m-0 mb-1.5">
            {{ fightName }}
          </h1>
          <div class="fight-meta flex items-center gap-2 text-sm text-neutral-text-secondary">
            <span class="meta-item flex items-center gap-1.5">
              <i class="pi pi-clock" />
              <span>{{ formattedDuration }}</span>
            </span>
            <span class="meta-divider border-neutral-border">|</span>
            <span class="meta-item flex items-center gap-1.5">
              <i class="pi pi-user" />
              <span>{{ recorder.name }}</span>
            </span>
          </div>
        </div>
      </div>

      <div class="header-right flex items-center gap-6">
        <div class="version-info flex gap-4">
          <div class="version-item flex flex-col gap-0.5">
            <span class="label text-[0.7rem] uppercase tracking-[0.025em]">Elite Insights:</span>
            <span class="value text-[0.8rem] font-medium">{{ versions.eliteInsights }}</span>
          </div>
          <div class="version-item flex flex-col gap-0.5">
            <span class="label text-[0.7rem] uppercase tracking-[0.025em]">Arc:</span>
            <span class="value text-[0.8rem] font-medium">{{ versions.arc }}</span>
          </div>
          <div class="version-item flex flex-col gap-0.5">
            <span class="label text-[0.7rem] uppercase tracking-[0.025em]">GW2:</span>
            <span class="value text-[0.8rem] font-medium">{{ versions.gw2 }}</span>
          </div>
        </div>

        <div class="theme-toggle flex gap-1 p-1 bg-neutral-card-hover rounded-lg">
          <button
            class="theme-btn w-8 h-8 bg-transparent rounded-md cursor-pointer flex items-center justify-center text-neutral-text-secondary"
            :class="{ active: !lightTheme }"
            title="黑色主题"
            @click="$emit('toggle-theme', false)"
          >
            <i class="pi pi-moon text-base" />
          </button>
          <button
            class="theme-btn w-8 h-8 bg-transparent rounded-md cursor-pointer flex items-center justify-center text-neutral-text-secondary"
            :class="{ active: lightTheme }"
            title="白色主题"
            @click="$emit('toggle-theme', true)"
          >
            <i class="pi pi-sun text-base" />
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 战斗信息头部组件
 * 作者：帅姐姐
 * 创建日期：2024-01-15
 */

import { computed } from 'vue'
import { formatDuration } from '@/types/eliteInsights'

interface Props {
  fightName: string
  duration: number
  recorder: { name: string; account: string }
  versions: { eliteInsights: string; arc: string; gw2: number }
  lightTheme: boolean
}

const props = defineProps<Props>()

defineEmits<{
  (e: 'toggle-theme', isLight: boolean): void
}>()

const formattedDuration = computed(() => formatDuration(props.duration))
</script>

<style scoped lang="css">
.meta-item i {
  color: var(--color-accent);
}
.version-item .label {
  color: var(--color-text-tertiary);
}
.version-item .value {
  color: var(--color-text);
}
.theme-btn:hover {
  background-color: var(--color-border);
  color: var(--color-text);
}
.theme-btn.active {
  background-color: var(--color-accent);
  color: white;
  box-shadow: 0 2px 8px var(--color-shadow);
}
</style>
