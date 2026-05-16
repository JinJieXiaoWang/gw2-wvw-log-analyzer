<template>
  <div
    class="card flex items-center gap-3 animate-slide-in-up"
    style="animation-delay: 0.05s"
  >
    <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-primary/30 to-secondary/30 flex items-center justify-center">
      <i class="pi pi-info-circle text-primary" />
    </div>
    <div class="flex-1 min-w-0">
      <p class="text-sm text-neutral-text">
        当前评分基于角色定位评分规则计算
        <Tag
          v-if="ruleVersion > 0"
          :value="'v' + ruleVersion"
          severity="info"
          class="text-[10px] ml-2"
        />
      </p>
      <p class="text-xs text-neutral-text-secondary">
        系统根据玩家职业和定位（输出/辅助/承伤）自动匹配对应的评分维度和权重
      </p>
    </div>
    <BaseButton
      label="评分规则"
      icon="pi pi-chart-line"
      variant="ghost"
      size="small"
      @click="$emit('open-rules')"
    />
  </div>
</template>

<script setup lang="ts">
/**
 * 评分规则提示卡片组件
 * 功能：显示当前评分规则信息
 */

import Tag from 'primevue/tag'
import BaseButton from '@/components/common/ui/input/BaseButton.vue'

defineProps<{
  roleLabel?: string
  ruleVersion: number
}>()

defineEmits<{
  'open-rules': []
}>()
</script>
