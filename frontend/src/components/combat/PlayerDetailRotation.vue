<template>
  <div class="space-y-5">
    <Card v-if="rotation.weapons?.length" class="border-none bg-surface-100/50">
      <template #header>
        <div class="flex items-center gap-2"><i class="pi pi-wrench text-primary" /><span class="font-semibold">姝﹀櫒配置</span></div>
      </template>
      <template #content>
        <div class="flex flex-wrap gap-2">
          <Chip v-for="(w, idx) in validWeapons" :key="idx" :label="weaponNameMap[w] || w" class="bg-primary/10 text-primary border-primary/30" />
        </div>
      </template>
    </Card>

    <Card v-if="hasConsumables" class="border-none bg-surface-100/50">
      <template #header>
        <div class="flex items-center gap-2"><i class="pi pi-sparkles text-success" /><span class="font-semibold">ʳ物 / 扳手</span></div>
      </template>
      <template #content>
        <div class="flex flex-wrap gap-2">
          <div v-for="(f, idx) in rotation.consumables?.food || []" :key="`food-${idx}`" class="flex items-center gap-2 px-3 py-1.5 rounded-full bg-success/10 text-success border border-success/30 text-sm">
            <img v-if="f.icon" :src="f.icon" class="w-4 h-4 rounded" /><span>{{ f.name || 'δ֪ʳ物' }}</span>
          </div>
          <div v-for="(u, idx) in rotation.consumables?.utility || []" :key="`util-${idx}`" class="flex items-center gap-2 px-3 py-1.5 rounded-full bg-primary/10 text-primary border border-primary/30 text-sm">
            <img v-if="u.icon" :src="u.icon" class="w-4 h-4 rounded" /><span>{{ u.name || 'δ֪扳手' }}</span>
          </div>
        </div>
      </template>
    </Card>

    <div v-if="!hasDetailData" class="text-center py-8">
      <div class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-surface-200/50 mb-4"><i class="pi pi-info-circle text-2xl text-neutral-text-secondary" /></div>
      <p class="text-neutral-text-secondary">暂无璇︾粏战斗数据</p>
      <p class="text-xs text-neutral-text-muted mt-1">当前解析器暂未提供技能循环、武器配置等详细信息</p>
    </div>

    <Card v-else-if="events.length > 0" class="border-none bg-surface-100/50">
      <template #header>
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2"><i class="pi pi-clock text-primary" /><span class="font-semibold">鎶技鑳藉惊鐜?/span></div>
          <BaseButton icon="pi pi-refresh" size="small" @click="$emit('refresh')" :disabled="loading" />
        </div>
      </template>
      <template #content>
        <SkillRotationViewer :events="events" :fight-duration="fightDuration" />
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import Card from 'primevue/card'
import BaseButton from '@/components/common/ui/BaseButton.vue'
import Chip from 'primevue/chip'
import SkillRotationViewer from './SkillRotationViewer.vue'
import { weaponNameMap } from '@/utils/combat/playerDetailHelpers'
import type { PlayerRotationData } from '@/services/ei/eiAnalysisService'

const props = defineProps<{
  rotation: PlayerRotationData
  events: any[]
  fightDuration: number
  loading: boolean
}>()

defineEmits<{ (e: 'refresh'): void }>()

const validWeapons = computed(() => props.rotation.weapons?.filter((w: string) => w && w !== 'Unknown').slice(0, 4) || [])

const hasConsumables = computed(() => {
  const c = props.rotation.consumables
  return (c?.food?.length || 0) > 0 || (c?.utility?.length || 0) > 0
})

const hasDetailData = computed(() => validWeapons.value.length > 0 || props.events.length > 0 || hasConsumables.value)
</script>
