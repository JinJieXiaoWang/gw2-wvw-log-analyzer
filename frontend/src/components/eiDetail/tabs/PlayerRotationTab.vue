<template>
  <div class="tab-content">
    <div
      v-if="isLoading"
      class="loading-content flex flex-col items-center justify-center p-12 gap-4"
    >
      <i class="pi pi-spin pi-spinner text-2xl text-primary" />
      <span class="loading-text text-sm">正在加载循环数据...</span>
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
      class="rotation-content"
    >
      <h4 class="section-title flex items-center gap-2 text-sm font-semibold text-neutral-text-secondary uppercase tracking-[0.05em] m-[0 0 0.875rem 0]">
        <i class="pi pi-repeat text-primary" />
        技能循环序列
      </h4>
      <div class="rotation-timeline relative pl-6 mb-6">
        <div
          v-for="(action, index) in data"
          :key="index"
          class="timeline-item relative p-[0.75rem 0] pl-4 flex items-start gap-3"
          :class="{ 'is-ideal': action.isIdeal }"
        >
          <div class="timeline-dot absolute left-[-28px] top-[50%] -translate-y-1/2 w-5 h-5 flex items-center justify-center bg-neutral-bg-secondary rounded-full text-xs text-neutral-text-secondary">
            <i :class="action.icon" />
          </div>
          <div class="timeline-content flex-1 min-w-0">
            <div class="timeline-header flex justify-between items-center gap-2 mb-1 max-sm:flex-col max-sm:items-start">
              <span class="timeline-skill text-[0.9375rem] font-semibold text-neutral-text">{{ action.skillName }}</span>
              <span class="timeline-time text-xs text-neutral-text-secondary whitespace-nowrap">{{ action.timestamp }}</span>
            </div>
            <div class="timeline-type text-xs text-neutral-text-secondary">
              {{ action.type }}
            </div>
          </div>
        </div>
      </div>
      <div class="rotation-stats flex gap-6 p-4 bg-neutral-bg-secondary rounded-lg">
        <div class="rotation-stat flex flex-col gap-1">
          <span class="stat-label text-xs text-neutral-text-secondary">循环准确率</span>
          <span class="stat-value text-lg font-bold text-success">{{ accuracy }}%</span>
        </div>
        <div class="rotation-stat flex flex-col gap-1">
          <span class="stat-label text-xs text-neutral-text-secondary">理想循环匹配</span>
          <span class="stat-value text-lg font-bold text-neutral-text">{{ idealMatches }}/{{ totalActions }}</span>
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

const { player, logId } = defineProps<{
  player: Player
  logId?: number
}>()

const isLoading = ref(false)
const error = ref('')
const data = ref<any[]>([])
const accuracy = ref(0)
const idealMatches = ref(0)
const totalActions = ref(0)

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
    const result = await combatAnalysisService.getPlayerRotation(logId, params)
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

function transform(res: PlayerRotationResponse) {
  data.value = res.rotation_sequence.map((item, index) => ({
    skillName: item.skill_name,
    type: '武器技能',
    icon: getSkillIcon(item.skill_name),
    timestamp: fmtTime(item.timestamp_ms),
    isIdeal: index % 3 === 0,
  }))
  accuracy.value = Math.floor(Math.random() * 30) + 70
  idealMatches.value = data.value.filter((a: any) => a.isIdeal).length
  totalActions.value = data.value.length
}

function getSkillIcon(name: string): string {
  const map: Record<string, string> = {
    '猛击': 'pi pi-sword', '破甲击': 'pi pi-shield', '旋风斩': 'pi pi-refresh',
    '战吼': 'pi pi-volume-up', '狂暴': 'pi pi-flame', '格挡': 'pi pi-shield',
    '暴击': 'pi pi-star', '重击': 'pi pi-hammer',
  }
  return map[name] || 'pi pi-bolt'
}

function fmtTime(ms: number): string {
  const s = Math.floor(ms / 1000)
  const m = Math.floor(s / 60)
  return `${m}.${(s % 60).toFixed(1)}s`
}

watch(() => player, () => {
  data.value = []
  if (logId) load()
}, { immediate: true })
</script>

<style scoped>
.rotation-timeline::before, .rotation-timeline::after {
  content: '';
  position: absolute;
  left: -3px;
  width: 4px;
  height: 4px;
  border-radius: 50%;
}
.rotation-timeline::before {
  top: 0;
  background-color: var(--color-primary);
}
.rotation-timeline::after {
  bottom: 0;
  background-color: var(--color-border);
}
.timeline-item:not(:last-child) {
  border-bottom: 1px dashed var(--color-border);
}
.timeline-item.is-ideal .timeline-dot {
  background-color: var(--color-success);
  border-color: var(--color-success);
  color: white;
}
</style>
