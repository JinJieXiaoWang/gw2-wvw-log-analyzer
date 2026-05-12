<template>
  <div class="tab-content">
    <div
      v-if="isLoading"
      class="loading-content flex flex-col items-center justify-center p-12 gap-4"
    >
      <i class="pi pi-spin pi-spinner text-2xl text-primary" />
      <span class="loading-text text-sm">正在加载技能数据...</span>
    </div>
    <div
      v-else-if="error"
      class="error-content flex flex-col items-center justify-center p-12 gap-4"
    >
      <i class="pi pi-exclamation-triangle text-2xl text-status-error" />
      <span class="error-text text-sm text-status-error">{{ error }}</span>
    </div>
    <div
      v-else
      class="skills-content"
    >
      <h4 class="section-title flex items-center gap-2 text-sm font-semibold text-neutral-text-secondary uppercase tracking-[0.05em] m-[0 0 0.875rem 0]">
        <i class="pi pi-bar-chart" />
        技能释放统计
      </h4>
      <div class="skills-chart-container mb-6 flex flex-col gap-3.5">
        <div class="skills-chart flex flex-col gap-3.5">
          <div
            v-for="skill in stats"
            :key="skill.name"
            class="skill-bar-item flex items-center gap-3"
          >
            <div class="skill-info min-w-20 flex justify-between">
              <span class="skill-name text-sm text-neutral-text">{{ skill.name }}</span>
              <span class="skill-count text-[0.8125rem] text-neutral-text-secondary">{{ skill.count }}次</span>
            </div>
            <div class="skill-bar-bg flex-1 h-3 bg-neutral-bg-secondary rounded-[6px] overflow-hidden">
              <div
                class="skill-bar-fill h-full rounded-[6px]"
                :style="{ width: skill.percentage + '%', backgroundColor: skill.color }"
              />
            </div>
            <div class="skill-percentage min-w-10 text-right text-[0.8125rem] font-semibold text-neutral-text-secondary">
              {{ skill.percentage }}%
            </div>
          </div>
        </div>
      </div>
      <div class="skills-summary grid grid-cols-3 max-sm:grid-cols-1 gap-3 p-4 bg-neutral-bg-secondary rounded-lg">
        <div class="summary-item flex flex-col items-center gap-1">
          <span class="summary-label text-xs text-neutral-text-secondary">总释放次数</span>
          <span class="summary-value text-base font-bold text-neutral-text">{{ totalCount }}</span>
        </div>
        <div class="summary-item flex flex-col items-center gap-1">
          <span class="summary-label text-xs text-neutral-text-secondary">平均间隔</span>
          <span class="summary-value text-base font-bold text-neutral-text">{{ avgInterval }}ms</span>
        </div>
        <div class="summary-item flex flex-col items-center gap-1">
          <span class="summary-label text-xs text-neutral-text-secondary">最高频率技能</span>
          <span class="summary-value text-base font-bold text-neutral-text">{{ topSkill }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import type { Player } from '@/types/eliteInsights'
import { combatAnalysisService } from '@/services'
import type { PlayerRotationResponse, PlayerQueryParams } from '@/services/combat/combatAnalysisService'
import { Colors } from '@/config/designTokens'

const { player, logId } = defineProps<{
  player: Player
  logId?: number
}>()

const isLoading = ref(false)
const error = ref('')
const stats = ref<any[]>([])
const totalCount = ref(0)
const avgInterval = ref(0)
const topSkill = ref('')

const colors = [Colors.palette.steelBlue, Colors.palette.gold, Colors.palette.coral, '#4ECDC4', '#95E1D3', '#A8E6CF']

async function load() {
  if (!logId) {
    error.value = '缺少日志ID'
    return
  }
  isLoading.value = true
  error.value = ''
  try {
    const params: PlayerQueryParams = {
      instance_id: typeof player.instanceID === 'number' ? player.instanceID : undefined,
      account_name: player.account || undefined,
      member_name: player.name || undefined,
    }
    const result = await combatAnalysisService.getPlayerRotation(logId, { ...params, output_format: 'summary' })
    if (!result.success || !result.data) {
      error.value = result.message || '加载失败'
      return
    }
    if (combatAnalysisService.isAmbiguousResponse(result.data)) {
      error.value = result.data.message || '存在多个同名玩家'
      return
    }
    transform(result.data as PlayerRotationResponse)
  } catch (e: any) {
    error.value = e.response?.data?.message || '网络错误'
  } finally {
    isLoading.value = false
  }
}

function transform(data: PlayerRotationResponse) {
  stats.value = Object.entries(data.skill_frequency)
    .map(([name, count], index) => ({
      name,
      count: count as number,
      percentage: Math.round(((count as number) / data.total_skills) * 100),
      color: colors[index % colors.length],
    }))
    .sort((a, b) => b.count - a.count)
  totalCount.value = data.total_skills
  avgInterval.value = Math.floor(data.duration_ms / data.total_skills)
  topSkill.value = stats.value[0]?.name || '无'
}

watch(() => player, () => {
  stats.value = []
  if (logId) load()
}, { immediate: true })
</script>

<style scoped>
.section-title i {
  color: var(--color-primary);
}
</style>
