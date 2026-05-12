<template>
  <div class="space-y-6">
    <!-- 功能入口卡片 -->
    <div class="card relative overflow-hidden border border-neutral-border">
      <!-- 背景装饰 -->
      <div
        class="absolute top-0 right-0 w-72 h-72 rounded-full -translate-y-1/2 translate-x-1/4 pointer-events-none"
        :style="{ background: `radial-gradient(circle, ${accentColor}08 0%, transparent 70%)` }"
      />
      <div
        class="absolute bottom-0 left-0 w-48 h-48 rounded-full translate-y-1/3 -translate-x-1/4 pointer-events-none"
        :style="{ background: `radial-gradient(circle, ${accentColor}05 0%, transparent 70%)` }"
      />

      <div class="relative">
        <!-- 头部 -->
        <div class="flex items-start gap-5 mb-8">
          <div
            class="w-16 h-16 rounded-2xl flex items-center justify-center flex-shrink-0 shadow-lg"
            :style="{
              backgroundColor: accentColor + '18',
              border: `1px solid ${accentColor}30`,
              boxShadow: `0 0 24px ${accentColor}20`
            }"
          >
            <i
              :class="icon"
              class="text-2xl"
              :style="{ color: accentColor }"
            />
          </div>
          <div class="flex-1 min-w-0">
            <h2 class="text-xl font-bold text-neutral-text mb-1.5">
              {{ title }}
            </h2>
            <p class="text-sm text-neutral-text-secondary leading-relaxed">
              {{ description }}
            </p>
          </div>
          <BaseButton
            :label="buttonLabel"
            :icon="buttonIcon"
            severity="primary"
            size="small"
            class="flex-shrink-0"
            :style="{ backgroundColor: accentColor, borderColor: accentColor }"
            @click="$emit('navigate')"
          />
        </div>

        <!-- 统计信息 -->
        <div
          v-if="stats && stats.length > 0"
          class="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-8"
        >
          <div
            v-for="stat in stats"
            :key="stat.label"
            class="bg-neutral-bg rounded-xl p-4 text-center border border-neutral-border transition-all duration-200 hover:border-neutral-border-light"
            :style="{ boxShadow: `0 0 16px ${accentColor}08` }"
          >
            <div
              class="text-2xl font-bold mb-1"
              :style="{ color: accentColor }"
            >
              {{ stat.value }}
            </div>
            <div class="text-xs text-neutral-text-secondary">
              {{ stat.label }}
            </div>
          </div>
        </div>

        <!-- 快捷操作 -->
        <div v-if="quickActions && quickActions.length > 0">
          <h4 class="text-sm font-semibold text-neutral-text mb-3">
            快捷操作
          </h4>
          <div class="flex flex-wrap gap-3">
            <BaseButton
              v-for="action in quickActions"
              :key="action.label"
              :label="action.label"
              :icon="action.icon"
              :severity="action.severity || 'secondary'"
              outlined
              size="small"
              @click="action.onClick"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- 功能特性列表 -->
    <div
      v-if="features && features.length > 0"
      class="card border border-neutral-border"
    >
      <h3 class="text-lg font-semibold text-neutral-text mb-5">
        功能特性
      </h3>
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div
          v-for="feature in features"
          :key="feature.title"
          class="flex items-start gap-3 p-4 bg-neutral-bg rounded-xl border border-neutral-border transition-all duration-200 hover:border-neutral-border-light group"
        >
          <div
            class="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 transition-all duration-200"
            :style="{ backgroundColor: accentColor + '12' }"
          >
            <i
              :class="feature.icon"
              class="transition-colors duration-200"
              :style="{ color: accentColor }"
            />
          </div>
          <div>
            <h4 class="text-sm font-medium text-neutral-text mb-1">
              {{ feature.title }}
            </h4>
            <p class="text-xs text-neutral-text-secondary leading-relaxed">
              {{ feature.description }}
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 系统功能入口面板
 * 功能：展示系统级功能的入口卡片，包含统计、快捷操作、特性介绍
 * 作者：帅姐姐
 * 创建日期：2026-04-30
 */

import BaseButton from '@/components/common/ui/input/BaseButton.vue'

export interface QuickAction {
  label: string
  icon: string
  severity?: string
  onClick: () => void
}

export interface FeatureItem {
  icon: string
  title: string
  description: string
}

export interface StatItem {
  label: string
  value: string | number
}

interface Props {
  title: string
  description: string
  icon: string
  accentColor: string
  buttonLabel: string
  buttonIcon: string
  stats?: StatItem[]
  quickActions?: QuickAction[]
  features?: FeatureItem[]
}

defineProps<Props>()

defineEmits<{
  navigate: []
}>()
</script>
