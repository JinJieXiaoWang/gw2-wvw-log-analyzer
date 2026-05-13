<template>
  <div class="lg:col-span-2 space-y-6">
    <div class="card">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-semibold text-neutral-text">
          技能循环时间线
        </h3>
        <div class="flex items-center gap-2">
          <Button
            label="实际循环"
            :severity="viewMode === 'actual' ? 'primary' : 'secondary'"
            @click="$emit('update:view-mode', 'actual')"
          />
          <Button
            label="理想循环"
            :severity="viewMode === 'ideal' ? 'primary' : 'secondary'"
            @click="$emit('update:view-mode', 'ideal')"
          />
        </div>
      </div>
      <div class="skill-timeline">
        <div class="flex items-center gap-2">
          <div
            v-for="(skill, index) in currentRotation"
            :key="index"
            class="skill-item"
            :class="{ 'skill-mistake': skill.isMistake }"
          >
            <div class="skill-icon">
              {{ skill.icon || '🛡️' }}
            </div>
            <div class="skill-info">
              <div class="skill-name">
                {{ skill.name }}
              </div>
              <div class="skill-time">
                {{ formatTime(skill.timestamp) }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="card">
      <h3 class="text-lg font-semibold text-neutral-text mb-4">
        技能释放统计
      </h3>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div class="stat-box">
          <div class="stat-value">
            {{ stats.totalCasts }}
          </div>
          <div class="stat-label">
            总释放次数
          </div>
        </div>
        <div class="stat-box">
          <div class="stat-value">
            {{ stats.successRate }}%
          </div>
          <div class="stat-label">
            成功率
          </div>
        </div>
        <div class="stat-box">
          <div class="stat-value">
            {{ stats.mistakes.length }}
          </div>
          <div class="stat-label">
            失误次数
          </div>
        </div>
        <div class="stat-box">
          <div class="stat-value">
            {{ stats.avgCastTime }}s
          </div>
          <div class="stat-label">
            平均释放间隔
          </div>
        </div>
      </div>
    </div>

    <div class="card">
      <h3 class="text-lg font-semibold text-neutral-text mb-4">
        技能使用分布
      </h3>
      <div class="h-64">
        <div class="chart-placeholder flex items-center justify-center h-full text-neutral-text-secondary">
          <i class="pi pi-chart-bar text-4xl mr-2" />
          <span>图表组件待接入</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import Button from 'primevue/button'

defineProps<{
  currentRotation: any[]
  stats: any
  viewMode: 'actual' | 'ideal'
}>()

defineEmits<{
  'update:view-mode': [mode: 'actual' | 'ideal']
}>()

const formatTime = (seconds: number) => {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}
</script>
