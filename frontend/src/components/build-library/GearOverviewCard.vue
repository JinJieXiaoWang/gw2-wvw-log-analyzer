<template>
  <div class="gear-overview">
    <!-- 护甲类型 -->
    <div class="flex items-center gap-3 mb-4 p-3 rounded-xl bg-neutral-bg border border-neutral-border">
      <i class="pi pi-shield text-status-warning text-lg" />
      <span class="text-base font-semibold text-neutral-text">{{ build.armorType }}</span>
    </div>

    <!-- 武器 -->
    <div v-if="build.weapons && build.weapons.length > 0" class="mb-5">
      <h4 class="text-sm font-bold text-neutral-text-secondary mb-2 uppercase tracking-wider">武器</h4>
      <div class="space-y-2">
        <div
          v-for="weapon in build.weapons"
          :key="weapon.set"
          class="flex items-center gap-3 p-3 rounded-xl bg-neutral-bg border border-neutral-border"
        >
          <span
            class="w-8 h-8 rounded-lg flex items-center justify-center text-xs font-bold text-white flex-shrink-0"
            :style="{ backgroundColor: '#165DFF' }"
          >
            {{ weapon.set }}
          </span>
          <span class="text-base font-medium text-neutral-text flex-1">{{ weapon.name }}</span>
          <div v-if="weapon.sigils && weapon.sigils.length > 0" class="flex gap-2 flex-shrink-0">
            <span
              v-for="sigil in weapon.sigils"
              :key="sigil"
              class="px-2.5 py-1 rounded-md bg-neutral-bg text-xs text-neutral-text-secondary border border-neutral-border"
            >
              {{ sigil }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 消耗品网格 - 2x2 大卡片 -->
    <div class="grid grid-cols-2 gap-3 mb-5">
      <div class="p-4 rounded-xl bg-neutral-bg border border-neutral-border">
        <div class="flex items-center gap-2 mb-2">
          <i class="pi pi-gem text-status-warning" />
          <span class="text-xs font-bold text-neutral-text-secondary uppercase tracking-wide">古物</span>
        </div>
        <div class="text-base font-semibold text-neutral-text">{{ build.relic }}</div>
      </div>
      <div class="p-4 rounded-xl bg-neutral-bg border border-neutral-border">
        <div class="flex items-center gap-2 mb-2">
          <i class="pi pi-sparkles text-rarity-legendary" />
          <span class="text-xs font-bold text-neutral-text-secondary uppercase tracking-wide">符文</span>
        </div>
        <div class="text-base font-semibold text-neutral-text">{{ build.rune }}</div>
      </div>
      <div class="p-4 rounded-xl bg-neutral-bg border border-neutral-border">
        <div class="flex items-center gap-2 mb-2">
          <i class="pi pi-apple text-status-warning" />
          <span class="text-xs font-bold text-neutral-text-secondary uppercase tracking-wide">食物</span>
        </div>
        <div class="text-base font-semibold text-neutral-text">{{ build.food }}</div>
      </div>
      <div class="p-4 rounded-xl bg-neutral-bg border border-neutral-border">
        <div class="flex items-center gap-2 mb-2">
          <i class="pi pi-wrench text-primary" />
          <span class="text-xs font-bold text-neutral-text-secondary uppercase tracking-wide">扳手</span>
        </div>
        <div class="text-base font-semibold text-neutral-text">{{ build.wrench }}</div>
      </div>
    </div>

    <!-- 灌注 -->
    <div class="flex items-center gap-3 p-3 rounded-xl bg-neutral-bg border border-neutral-border mb-5">
      <i class="pi pi-circle-fill text-tech-cyan" />
      <span class="text-sm text-neutral-text-secondary">灌注：</span>
      <span class="text-base font-semibold text-neutral-text">{{ build.infusion }}</span>
    </div>

    <!-- 属性要求 -->
    <div v-if="build.attrRequirements && build.attrRequirements.length > 0" class="space-y-2">
      <div
        v-for="req in build.attrRequirements"
        :key="req"
        class="flex items-center gap-3 p-3 rounded-xl bg-info/8 border border-info/15"
      >
        <i class="pi pi-info-circle text-info" />
        <span class="text-sm text-neutral-text">{{ req }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { BuildEntry } from '@/types/buildLibrary'

interface Props {
  build: BuildEntry
}

defineProps<Props>()
</script>

<style scoped>
.gear-overview {
  padding: 0.25rem;
}
</style>
