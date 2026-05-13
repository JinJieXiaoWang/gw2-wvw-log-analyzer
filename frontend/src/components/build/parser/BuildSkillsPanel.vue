<template>
  <div
    v-if="parsedData"
    class="card"
  >
    <h3 class="text-lg font-semibold text-neutral-text mb-4">
      技能配置
    </h3>
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <!-- 治疗技能 -->
      <div class="text-center">
        <div class="text-sm text-neutral-text-secondary mb-2">
          治疗
        </div>
        <div class="w-20 h-20 mx-auto bg-neutral-800 rounded-lg flex flex-col items-center justify-center p-2">
          <img
            v-if="parsedData.skills.heal?.icon"
            :src="cleanIconUrl(parsedData.skills.heal.icon)"
            :alt="parsedData.skills.heal.name_cn"
            class="w-10 h-10 rounded mb-1"
          >
          <span class="text-xs text-neutral-text">{{ parsedData.skills.heal?.name_cn || '未配置' }}</span>
        </div>
        <p class="text-xs text-neutral-text-secondary mt-2">
          {{ parsedData.skills.heal?.recharge }}s CD
        </p>
      </div>

      <!-- 通用技能 -->
      <div class="col-span-2">
        <div class="text-sm text-neutral-text-secondary mb-2">
          通用
        </div>
        <div class="flex gap-2 justify-center">
          <div
            v-for="(skill, index) in parsedData.skills.utility"
            :key="index"
            class="w-20 h-20 bg-neutral-800 rounded-lg flex flex-col items-center justify-center p-2"
          >
            <img
              v-if="skill.icon"
              :src="cleanIconUrl(skill.icon)"
              :alt="skill.name_cn"
              class="w-10 h-10 rounded mb-1"
            >
            <span class="text-xs text-neutral-text">{{ skill.name_cn }}</span>
          </div>
        </div>
        <div class="flex gap-2 justify-center mt-1">
          <span
            v-for="(skill, index) in parsedData.skills.utility"
            :key="index"
            class="w-20 text-center"
          >
            <span class="text-xs text-neutral-text-secondary">{{ skill.recharge }}s</span>
          </span>
        </div>
      </div>

      <!-- 精英技能 -->
      <div class="text-center">
        <div class="text-sm text-neutral-text-secondary mb-2">
          精英
        </div>
        <div
          class="w-20 h-20 mx-auto bg-neutral-800 rounded-lg flex flex-col items-center justify-center p-2 border border-yellow-500/30"
        >
          <img
            v-if="parsedData.skills.elite?.icon"
            :src="cleanIconUrl(parsedData.skills.elite.icon)"
            :alt="parsedData.skills.elite.name_cn"
            class="w-10 h-10 rounded mb-1"
          >
          <span class="text-xs text-neutral-text">{{ parsedData.skills.elite?.name_cn || '未配置' }}</span>
        </div>
        <p class="text-xs text-neutral-text-secondary mt-2">
          {{ parsedData.skills.elite?.recharge }}s CD
        </p>
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
