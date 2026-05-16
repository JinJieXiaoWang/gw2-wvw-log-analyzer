<template>
  <div class="space-y-6">
    <div class="card">
      <h3 class="text-lg font-semibold text-neutral-text mb-4">
        失误详情
      </h3>
      <div
        v-if="mistakes.length > 0"
        class="space-y-3"
      >
        <div
          v-for="(mistake, index) in mistakes"
          :key="index"
          class="mistake-item"
        >
          <div class="flex items-start gap-3">
            <i class="pi pi-exclamation-triangle text-yellow-500 mt-1" />
            <div class="flex-1">
              <div class="mistake-title">
                {{ mistake.skillName }}
              </div>
              <div class="mistake-description">
                {{ mistake.description }}
              </div>
              <div class="mistake-time">
                {{ formatTime(mistake.timestamp) }}
              </div>
            </div>
          </div>
        </div>
      </div>
      <div
        v-else
        class="text-center py-8 text-neutral-text-secondary"
      >
        <i class="pi pi-check-circle text-3xl text-green-500 mb-2" />
        <p>太棒了，没有发现失误！</p>
      </div>
    </div>

    <div class="card">
      <h3 class="text-lg font-semibold text-neutral-text mb-4">
        优化建议
      </h3>
      <div class="space-y-3">
        <div class="suggestion-item">
          <div class="flex items-start gap-3">
            <i class="pi pi-lightbulb text-yellow-500 mt-1" />
            <div>
              <div class="suggestion-title">
                优化技能释放顺序
              </div>
              <div class="suggestion-description">
                确保关键技能的CD一好就释放
              </div>
            </div>
          </div>
        </div>
        <div class="suggestion-item">
          <div class="flex items-start gap-3">
            <i class="pi pi-lightbulb text-yellow-500 mt-1" />
            <div>
              <div class="suggestion-title">
                关注资源管理
              </div>
              <div class="suggestion-description">
                保持资源（能量/怒气/集中值）的合理分配
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="card">
      <h3 class="text-lg font-semibold text-neutral-text mb-4">
        历史分析
      </h3>
      <div class="space-y-2">
        <div class="text-center py-4 text-neutral-text-secondary">
          暂无历史记录
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  mistakes: any[]
}>()

const formatTime = (seconds: number) => {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}
</script>
