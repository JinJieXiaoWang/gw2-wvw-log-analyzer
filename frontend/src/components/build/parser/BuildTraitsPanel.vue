<template>
  <div
    v-if="parsedData"
    class="card"
  >
    <h3 class="text-lg font-semibold text-neutral-text mb-4">
      特性配置
    </h3>
    <div class="space-y-4">
      <div
        v-for="spec in parsedData.specializations"
        :key="spec.id"
        class="p-4 bg-neutral-800 rounded-lg"
      >
        <div class="flex items-center gap-3 mb-3">
          <img
            v-if="spec.icon"
            :src="cleanIconUrl(spec.icon)"
            :alt="spec.name_cn"
            class="w-8 h-8 rounded"
          >
          <div>
            <span class="text-neutral-text font-medium">{{ spec.name_cn }}</span>
            <span
              v-if="spec.is_elite"
              class="ml-2 text-xs px-2 py-0.5 bg-yellow-500/20 text-yellow-500 rounded"
            >
              精英特长
            </span>
          </div>
        </div>
        <div class="grid grid-cols-3 gap-2">
          <div
            v-for="trait in spec.traits"
            :key="trait.id"
            class="p-3 rounded-lg"
            :class="trait.is_selected ? 'bg-primary/20 border border-primary/50' : 'bg-neutral-700/50'"
          >
            <div class="flex items-center gap-2 mb-1">
              <img
                v-if="trait.icon"
                :src="cleanIconUrl(trait.icon)"
                :alt="trait.name"
                class="w-4 h-4 rounded"
              >
              <span
                class="text-sm font-medium"
                :class="trait.is_selected ? 'text-primary' : 'text-neutral-text-secondary'"
              >
                {{ trait.name }}
              </span>
            </div>
            <p class="text-xs text-neutral-text-secondary line-clamp-2">
              {{ trait.description }}
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { cleanIconUrl } from '@/utils/build/buildParserUtils'

defineProps<{
  parsedData: any
}>()
</script>
