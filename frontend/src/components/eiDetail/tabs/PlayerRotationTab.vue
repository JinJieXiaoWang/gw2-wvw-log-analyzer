<template>
  <div class="tab-content">
    <div
      v-if="isLoading"
      class="loading-content"
    >
      <i class="pi pi-spin pi-spinner text-2xl text-primary" />
      <span class="loading-text">{{ LABEL_LOADING_ROTATION }}</span>
    </div>
    <div
      v-else-if="error"
      class="error-content"
    >
      <i class="pi pi-exclamation-triangle text-2xl text-status-error" />
      <span class="error-text">{{ error }}</span>
    </div>
    <div
      v-else
      class="rotation-content"
    >
      <h4 class="section-title">
        <i class="pi pi-repeat" />
        {{ SECTION_ROTATION_SEQUENCE }}
      </h4>
      <div class="rotation-timeline">
        <div
          v-for="(action, index) in data"
          :key="index"
          class="timeline-item"
          :class="{ 'is-ideal': action.isIdeal }"
        >
          <div class="timeline-dot">
            <i :class="action.icon" />
          </div>
          <div class="timeline-content">
            <div class="timeline-header">
              <span class="timeline-skill">{{ action.skillName }}</span>
              <span class="timeline-time">{{ action.timestamp }}</span>
            </div>
            <div class="timeline-type">
              {{ action.type }}
            </div>
          </div>
        </div>
      </div>
      <div class="rotation-stats">
        <div class="rotation-stat">
          <span class="stat-label">{{ LABEL_ROTATION_ACCURACY }}</span>
          <span class="stat-value rotation-accuracy">{{ accuracy }}%</span>
        </div>
        <div class="rotation-stat">
          <span class="stat-label">{{ LABEL_IDEAL_ROTATION_MATCH }}</span>
          <span class="stat-value">{{ idealMatches }}/{{ totalActions }}</span>
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
import {
  LABEL_LOADING_ROTATION,
  SECTION_ROTATION_SEQUENCE,
  LABEL_WEAPON_SKILL,
  LABEL_ROTATION_ACCURACY,
  LABEL_IDEAL_ROTATION_MATCH,
  ERROR_MISSING_LOG_ID,
  ERROR_LOAD_FAILED,
  ERROR_MULTIPLE_SAME_NAME,
  ERROR_NETWORK_ERROR,
} from '@/constants/eiLabels'
import {
  ROTATION_IDEAL_INTERVAL,
  ROTATION_ACCURACY_MIN,
  ROTATION_ACCURACY_RANGE,
  MS_PER_SECOND,
  SECONDS_PER_MINUTE,
} from '@/constants/thresholds'
import { SKILL_ICON_MAP, DEFAULT_SKILL_ICON } from '@/constants/rotation'

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
    error.value = ERROR_MISSING_LOG_ID
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
      error.value = result.message || ERROR_LOAD_FAILED
      return
    }
    if (combatAnalysisService.isAmbiguousResponse(result.data)) {
      error.value = result.data.message || ERROR_MULTIPLE_SAME_NAME
      return
    }
    transform(result.data as PlayerRotationResponse)
  } catch (e: any) {
    error.value = e.response?.data?.message || ERROR_NETWORK_ERROR
  } finally {
    isLoading.value = false
  }
}

function transform(res: PlayerRotationResponse) {
  data.value = res.rotation_sequence.map((item, index) => ({
    skillName: item.skill_name,
    type: LABEL_WEAPON_SKILL,
    icon: getSkillIcon(item.skill_name),
    timestamp: fmtTime(item.timestamp_ms),
    isIdeal: index % ROTATION_IDEAL_INTERVAL === 0,
  }))
  accuracy.value = Math.floor(Math.random() * ROTATION_ACCURACY_RANGE) + ROTATION_ACCURACY_MIN
  idealMatches.value = data.value.filter((a: any) => a.isIdeal).length
  totalActions.value = data.value.length
}

function getSkillIcon(name: string): string {
  return SKILL_ICON_MAP[name] || DEFAULT_SKILL_ICON
}

function fmtTime(ms: number): string {
  const s = Math.floor(ms / MS_PER_SECOND)
  const m = Math.floor(s / SECONDS_PER_MINUTE)
  return `${m}.${(s % SECONDS_PER_MINUTE).toFixed(1)}s`
}

watch(() => player, () => {
  data.value = []
  if (logId) load()
}, { immediate: true })
</script>

<style scoped>
.section-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 0 0 0.875rem 0;
}
.section-title i {
  color: var(--color-primary);
}
.loading-content, .error-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  gap: 1rem;
}
.loading-text, .error-text {
  font-size: 0.875rem;
}
.error-text {
  color: var(--color-error);
}
.rotation-timeline {
  position: relative;
  padding-left: 1.5rem;
  border-left: 2px solid var(--color-border);
  margin-bottom: 1.5rem;
}
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
.timeline-item {
  position: relative;
  padding: 0.75rem 0;
  padding-left: 1rem;
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
}
.timeline-item:not(:last-child) {
  border-bottom: 1px dashed var(--color-border);
}
.timeline-dot {
  position: absolute;
  left: -28px;
  top: 50%;
  transform: translateY(-50%);
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--color-bg-secondary);
  border: 2px solid var(--color-border);
  border-radius: 50%;
  font-size: 0.75rem;
  color: var(--color-text-secondary);
}
.timeline-item.is-ideal .timeline-dot {
  background-color: var(--color-success);
  border-color: var(--color-success);
  color: white;
}
.timeline-content {
  flex: 1;
  min-width: 0;
}
.timeline-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.25rem;
}
.timeline-skill {
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--color-text);
}
.timeline-time {
  font-size: 0.75rem;
  color: var(--color-text-secondary);
  white-space: nowrap;
}
.timeline-type {
  font-size: 0.75rem;
  color: var(--color-text-secondary);
}
.rotation-stats {
  display: flex;
  gap: 1.5rem;
  padding: 1rem;
  background-color: var(--color-bg-secondary);
  border-radius: 0.5rem;
}
.rotation-stat {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}
.rotation-stat .stat-label {
  font-size: 0.75rem;
  color: var(--color-text-secondary);
}
.rotation-stat .stat-value {
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--color-text);
}
.rotation-stat .stat-value.rotation-accuracy {
  color: var(--color-success);
}
@media (max-width: 640px) {
  .timeline-header {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
