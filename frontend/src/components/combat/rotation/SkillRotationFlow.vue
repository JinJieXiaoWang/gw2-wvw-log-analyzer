<template>
  <div class="flex flex-col gap-3">
    <!-- 过滤栏 -->
    <div class="flex flex-wrap items-center gap-3">
      <label class="flex items-center gap-1.5 text-xs text-neutral-text-secondary cursor-pointer select-none">
        <BaseCheckbox
          v-model="showAutoAttacks"
          binary
        />
        <span>{{ FILTER_LABELS.showAuto }}</span>
      </label>
      <label class="flex items-center gap-1.5 text-xs text-neutral-text-secondary cursor-pointer select-none">
        <BaseCheckbox
          v-model="showInstant"
          binary
        />
        <span>{{ FILTER_LABELS.showInstant }}</span>
      </label>
      <label class="flex items-center gap-1.5 text-xs text-neutral-text-secondary cursor-pointer select-none">
        <BaseCheckbox
          v-model="showSwaps"
          binary
        />
        <span>{{ FILTER_LABELS.showSwap }}</span>
      </label>
      <label class="flex items-center gap-1.5 text-xs text-neutral-text-secondary cursor-pointer select-none">
        <BaseCheckbox
          v-model="showTraits"
          binary
        />
        <span>{{ FILTER_LABELS.showTrait }}</span>
      </label>
      <span class="ml-auto text-xs text-neutral-text-secondary">
        {{ filteredEvents.length }} / {{ events.length }}
      </span>
    </div>

    <!-- 技能图标流 -->
    <div
      v-if="filteredEvents.length > 0"
      class="flex flex-wrap gap-1"
    >
      <div
        v-for="(evt, idx) in filteredEvents"
        :key="idx"
        class="group relative"
      >
        <!-- 技能图标 -->
        <div
          class="w-9 h-9 rounded overflow-hidden border-2 transition-transform duration-150 hover:scale-110"
          :class="STATE_BORDER_MAP[evt.state] || STATE_BORDER_MAP.full"
        >
          <img
            v-if="evt.icon"
            :src="evt.icon"
            :alt="evt.name"
            class="w-full h-full object-cover"
            loading="lazy"
          >
          <div
            v-else
            class="w-full h-full flex items-center justify-center text-xs font-bold text-neutral-text-secondary bg-neutral-bg"
          >
            {{ evt.name?.charAt(0) || '?' }}
          </div>
        </div>

        <!-- 悬浮提示 - 完全在 Dialog 内部，absolute 定位 -->
        <div
          class="absolute bottom-full left-1/2 -translate-x-1/2 mb-1.5 hidden group-hover:block z-20 pointer-events-none"
        >
          <div class="px-2.5 py-1.5 rounded-lg bg-neutral-card border border-neutral-border shadow-xl">
            <div class="font-semibold text-xs text-neutral-text whitespace-nowrap">
              {{ evt.name }}
            </div>
            <div class="text-[11px] text-neutral-text-secondary whitespace-nowrap">
              {{ formatTime(evt.castTime) }} · {{ STATE_LABEL_MAP[evt.state] || evt.state }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div
      v-else
      class="flex flex-col items-center justify-center py-12 text-neutral-text-secondary"
    >
      <i class="pi pi-filter-slash text-4xl mb-3 opacity-50" />
      <p class="text-sm">
        当前过滤条件下无技能数据
      </p>
      <p class="text-xs mt-1">
        尝试调整过滤选项
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import BaseCheckbox from '@/components/common/ui/input/BaseCheckbox.vue'
import { formatTime } from '@/utils/combat/rotation'

/** 技能状态边框颜色映射（业务状态专用 token） */
const STATE_BORDER_MAP: Record<string, string> = {
  full: 'border-cyan-400',
  interrupted: 'border-error',
  instant: 'border-primary',
  swap: 'border-purple-500',
  trait: 'border-amber-500',
}

/** 技能状态标签映射 */
const STATE_LABEL_MAP: Record<string, string> = {
  full: '完整释放',
  interrupted: '被打断',
  instant: '瞬发',
  swap: '武器切换',
  trait: '特性触发',
}

/** 过滤选项标签 */
const FILTER_LABELS = {
  showAuto: '显示普攻',
  showInstant: '显示瞬发',
  showSwap: '显示武器切换',
  showTrait: '显示特性触发',
} as const

const props = defineProps<{
  events: any[]
}>()

const showAutoAttacks = ref(false)
const showInstant = ref(true)
const showSwaps = ref(true)
const showTraits = ref(false)

const filteredEvents = computed(() => {
  if (!props.events?.length) return []
  return props.events.filter((evt: any) => {
    if (!showAutoAttacks.value && evt.autoAttack) return false
    if (!showInstant.value && evt.isInstant) return false
    if (!showSwaps.value && evt.isSwap) return false
    if (!showTraits.value && evt.isTraitProc) return false
    return true
  })
})
</script>
