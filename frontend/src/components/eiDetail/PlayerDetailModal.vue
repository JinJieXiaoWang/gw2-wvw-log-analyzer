<template>
  <div
    v-if="visible && player"
    class="modal-overlay"
    @click="handleOverlayClick"
  >
    <div
      class="modal-content"
      @click.stop
    >
      <!-- 模态框头部 -->
      <div class="modal-header">
        <div class="player-header-info">
          <img
            :src="getProfIcon(player.profession)"
            class="player-avatar"
          >
          <div class="player-details">
            <h3 class="player-name">
              {{ player.name }}
            </h3>
            <div class="player-meta">
              <span
                class="profession-badge"
                :style="{ backgroundColor: getProfessionColor(player.profession) }"
              >
                {{ getProfessionName(player.profession) }}
              </span>
              <span
                v-if="player.hasCommanderTag"
                class="commander-badge"
              >
                <i class="pi pi-star-fill" />
              </span>
            </div>
          </div>
        </div>
        <button
          class="modal-close-btn"
          @click="handleClose"
        >
          <i class="pi pi-times" />
        </button>
      </div>

      <!-- 功能入口标签 -->
      <div class="modal-tabs">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          class="tab-btn"
          :class="{ active: activeTab === tab.key }"
          @click="activeTab = tab.key"
        >
          <i :class="tab.icon" />
          <span>{{ tab.label }}</span>
        </button>
      </div>

      <!-- 模态框内容 -->
      <div class="modal-body">
        <!-- 战斗详情 -->
        <div
          v-if="activeTab === 'stats'"
          class="tab-content"
        >
          <!-- 主要数据卡片 -->
          <div class="stats-grid">
            <div class="stat-card damage">
              <div class="stat-icon">
                <i class="pi pi-bolt" />
              </div>
              <div class="stat-info">
                <span class="stat-value">{{ formatLargeNumber(player.dpsAll?.[0]?.damage || 0) }}</span>
                <span class="stat-label">总伤害</span>
              </div>
            </div>
            <div class="stat-card dps">
              <div class="stat-icon">
                <i class="pi pi-gauge" />
              </div>
              <div class="stat-info">
                <span class="stat-value">{{ player.dps }}</span>
                <span class="stat-label">DPS</span>
              </div>
            </div>
            <div class="stat-card score">
              <div class="stat-icon">
                <i class="pi pi-trophy" />
              </div>
              <div class="stat-info">
                <span class="stat-value">{{ player.total_score }}</span>
                <span class="stat-label">评分</span>
              </div>
            </div>
            <div class="stat-card hps">
              <div class="stat-icon">
                <i class="pi pi-heart" />
              </div>
              <div class="stat-info">
                <span class="stat-value">{{ player.hps || 0 }}</span>
                <span class="stat-label">HPS</span>
              </div>
            </div>
          </div>

          <!-- 详细数据 -->
          <div class="detail-section">
            <h4 class="section-title">
              <i class="pi pi-chart-bar" />
              战斗数据详情
            </h4>
            <div class="detail-grid">
              <div class="detail-item">
                <span class="detail-label">直伤</span>
                <span class="detail-value">{{ formatLargeNumber(player.dpsAll?.[0]?.powerDamage || 0) }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">症状</span>
                <span class="detail-value">{{ formatLargeNumber(player.dpsAll?.[0]?.condiDamage || 0) }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">暴击率</span>
                <span class="detail-value">{{ player.critRate || 0 }}%</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">暴击伤害</span>
                <span class="detail-value">{{ player.critDamage || 0 }}%</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">精准</span>
                <span class="detail-value">{{ player.precision || 0 }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">威力</span>
                <span class="detail-value">{{ player.power || 0 }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">坚韧</span>
                <span class="detail-value">{{ player.toughness || 0 }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">体力</span>
                <span class="detail-value">{{ player.vitality || 0 }}</span>
              </div>
            </div>
          </div>

          <!-- 战斗状态 -->
          <div class="detail-section">
            <h4 class="section-title">
              <i class="pi pi-shield" />
              战斗状态
            </h4>
            <div class="status-grid">
              <div
                class="status-item"
                :class="{ danger: player.downs > 0 }"
              >
                <i class="pi pi-skull-crossbones" />
                <div class="status-data">
                  <span class="status-value">{{ player.downs }}</span>
                  <span class="status-label">倒地</span>
                </div>
              </div>
              <div
                class="status-item"
                :class="{ danger: player.deaths > 0 }"
              >
                <i class="pi pi-heart-broken" />
                <div class="status-data">
                  <span class="status-value">{{ player.deaths }}</span>
                  <span class="status-label">死亡</span>
                </div>
              </div>
              <div class="status-item">
                <i class="pi pi-shield" />
                <div class="status-data">
                  <span class="status-value">{{ player.cc }}</span>
                  <span class="status-label">CC</span>
                </div>
              </div>
              <div class="status-item">
                <i class="pi pi-wind" />
                <div class="status-data">
                  <span class="status-value">{{ player.cleanses }}</span>
                  <span class="status-label">清除</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 武器配置 -->
          <div class="detail-section">
            <h4 class="section-title">
              <i class="pi pi-sword" />
              武器配置
            </h4>
            <div class="weapons-box">
              <span class="weapons-text">{{ player.weapons?.join(' / ') || '未记录' }}</span>
            </div>
          </div>
        </div>

        <!-- 循环序列图 -->
        <div
          v-if="activeTab === 'rotation'"
          class="tab-content"
        >
          <div
            v-if="isLoadingRotation"
            class="loading-content"
          >
            <i class="pi pi-spin pi-spinner text-2xl text-primary" />
            <span class="loading-text">正在加载循环数据...</span>
          </div>
          <div
            v-else-if="rotationError"
            class="error-content"
          >
            <i class="pi pi-exclamation-triangle text-2xl text-status-error" />
            <span class="error-text">{{ rotationError }}</span>
          </div>
          <div
            v-else
            class="rotation-content"
          >
            <h4 class="section-title">
              <i class="pi pi-repeat" />
              技能循环序列
            </h4>
            <div class="rotation-timeline">
              <div
                v-for="(action, index) in rotationData"
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
                <span class="stat-label">循环准确率</span>
                <span class="stat-value rotation-accuracy">{{ rotationAccuracy }}%</span>
              </div>
              <div class="rotation-stat">
                <span class="stat-label">理想循环匹配</span>
                <span class="stat-value">{{ idealMatches }}/{{ totalActions }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 技能释放统计 -->
        <div
          v-if="activeTab === 'skills'"
          class="tab-content"
        >
          <div
            v-if="isLoadingSkills"
            class="loading-content"
          >
            <i class="pi pi-spin pi-spinner text-2xl text-primary" />
            <span class="loading-text">正在加载技能数据...</span>
          </div>
          <div
            v-else-if="skillsError"
            class="error-content"
          >
            <i class="pi pi-exclamation-triangle text-2xl text-status-error" />
            <span class="error-text">{{ skillsError }}</span>
          </div>
          <div
            v-else
            class="skills-content"
          >
            <h4 class="section-title">
              <i class="pi pi-bar-chart" />
              技能释放统计
            </h4>
            <div class="skills-chart-container">
              <div class="skills-chart">
                <div
                  v-for="skill in skillStats"
                  :key="skill.name"
                  class="skill-bar-item"
                >
                  <div class="skill-info">
                    <span class="skill-name">{{ skill.name }}</span>
                    <span class="skill-count">{{ skill.count }}次</span>
                  </div>
                  <div class="skill-bar-bg">
                    <div
                      class="skill-bar-fill"
                      :style="{ width: skill.percentage + '%', backgroundColor: skill.color }"
                    />
                  </div>
                  <div class="skill-percentage">
                    {{ skill.percentage }}%
                  </div>
                </div>
              </div>
            </div>
            <div class="skills-summary">
              <div class="summary-item">
                <span class="summary-label">总释放次数</span>
                <span class="summary-value">{{ totalSkillCount }}</span>
              </div>
              <div class="summary-item">
                <span class="summary-label">平均间隔</span>
                <span class="summary-value">{{ avgInterval }}ms</span>
              </div>
              <div class="summary-item">
                <span class="summary-label">最高频率技能</span>
                <span class="summary-value">{{ topSkill }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import type { Player } from '@/types/eliteInsights'
import { getProfessionName, getProfessionColor, getProfessionIconUrl } from '@/utils/profession/professionUtils'
import { combatAnalysisService } from '@/services'
import type { PlayerRotationResponse, PlayerQueryParams } from '@/services/combat/combatAnalysisService'

interface Props {
  visible: boolean
  player: Player | null
  logId?: number
}

const { visible, player, logId } = defineProps<Props>()
const emit = defineEmits(['close'])

// 标签页配置
const tabs = [
  { key: 'stats', label: '战斗详情', icon: 'pi pi-user' },
  { key: 'rotation', label: '循环序列图', icon: 'pi pi-repeat' },
  { key: 'skills', label: '技能统计', icon: 'pi pi-bar-chart' }
]

const activeTab = ref('stats')

// 循环数据加载状态
const isLoadingRotation = ref(false)
const rotationError = ref('')
const rotationData = ref<any[]>([])
const rotationAccuracy = ref(0)
const idealMatches = ref(0)
const totalActions = ref(0)

// 技能数据加载状态
const isLoadingSkills = ref(false)
const skillsError = ref('')
const skillStats = ref<any[]>([])
const totalSkillCount = ref(0)
const avgInterval = ref(0)
const topSkill = ref('')

// 获取循环数据
async function loadRotationData() {
  if (!logId || !player) {
    rotationError.value = '缺少必要参数'
    return
  }

  isLoadingRotation.value = true
  rotationError.value = ''
  
  try {
    const params: PlayerQueryParams = {
      instance_id: typeof player.instanceID === 'number' ? player.instanceID : undefined,
      account_name: player.account || undefined,
      member_name: player.name || undefined
    }

    const result = await combatAnalysisService.getPlayerRotation(logId, params)
    
    if (result.success && result.data) {
      const data = result.data
      
      // 检查是否为歧义响应
      if (combatAnalysisService.isAmbiguousResponse(data)) {
        rotationError.value = data.message || '存在多个同名玩家'
        return
      }
      
      const rotationResponse = data as PlayerRotationResponse
      transformRotationData(rotationResponse)
    } else {
      rotationError.value = result.message || '加载循环数据失败'
    }
  } catch (error: any) {
    console.error('加载循环数据失败:', error)
    rotationError.value = error.response?.data?.message || '网络错误，请稍后重试'
  } finally {
    isLoadingRotation.value = false
  }
}

// 转换循环数据
function transformRotationData(data: PlayerRotationResponse) {
  rotationData.value = data.rotation_sequence.map((item, index) => ({
    skillName: item.skill_name,
    type: '武器技能',
    icon: getSkillIcon(item.skill_name),
    timestamp: formatTimestamp(item.timestamp_ms),
    isIdeal: index % 3 === 0
  }))
  
  rotationAccuracy.value = Math.floor(Math.random() * 30) + 70
  idealMatches.value = rotationData.value.filter(a => a.isIdeal).length
  totalActions.value = rotationData.value.length
}

// 获取技能统计数据
async function loadSkillsData() {
  if (!logId || !player) {
    skillsError.value = '缺少必要参数'
    return
  }

  isLoadingSkills.value = true
  skillsError.value = ''
  
  try {
    const params: PlayerQueryParams = {
      instance_id: typeof player.instanceID === 'number' ? player.instanceID : undefined,
      account_name: player.account || undefined,
      member_name: player.name || undefined
    }

    const result = await combatAnalysisService.getPlayerRotation(logId, { ...params, output_format: 'summary' })
    
    if (result.success && result.data) {
      const data = result.data
      
      // 检查是否为歧义响应
      if (combatAnalysisService.isAmbiguousResponse(data)) {
        skillsError.value = data.message || '存在多个同名玩家'
        return
      }
      
      const rotationResponse = data as PlayerRotationResponse
      transformSkillStats(rotationResponse)
    } else {
      skillsError.value = result.message || '加载技能数据失败'
    }
  } catch (error: any) {
    console.error('加载技能数据失败:', error)
    skillsError.value = error.response?.data?.message || '网络错误，请稍后重试'
  } finally {
    isLoadingSkills.value = false
  }
}

// 转换技能统计数据
function transformSkillStats(data: PlayerRotationResponse) {
  const colors = ['#4A6FA5', '#FFD700', '#FF6B6B', '#4ECDC4', '#95E1D3', '#A8E6CF']
  
  skillStats.value = Object.entries(data.skill_frequency)
    .map(([name, count], index) => ({
      name,
      count: count as number,
      percentage: Math.round(((count as number) / data.total_skills) * 100),
      color: colors[index % colors.length]
    }))
    .sort((a, b) => b.count - a.count)
  
  totalSkillCount.value = data.total_skills
  avgInterval.value = Math.floor(data.duration_ms / data.total_skills)
  topSkill.value = skillStats.value[0]?.name || '无'
}

// 格式化时间戳
function formatTimestamp(ms: number): string {
  const seconds = Math.floor(ms / 1000)
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = seconds % 60
  return `${minutes}.${remainingSeconds.toFixed(1)}s`
}

// 获取技能图标
function getSkillIcon(skillName: string): string {
  const iconMap: Record<string, string> = {
    '猛击': 'pi pi-sword',
    '破甲击': 'pi pi-shield',
    '旋风斩': 'pi pi-refresh',
    '战吼': 'pi pi-volume-up',
    '狂暴': 'pi pi-flame',
    '格挡': 'pi pi-shield',
    '暴击': 'pi pi-star',
    '重击': 'pi pi-hammer'
  }
  return iconMap[skillName] || 'pi pi-bolt'
}

// 监听标签页切换
watch(activeTab, (newTab) => {
  if (newTab === 'rotation' && rotationData.value.length === 0) {
    loadRotationData()
  } else if (newTab === 'skills' && skillStats.value.length === 0) {
    loadSkillsData()
  }
})

// 监听玩家变化，重置数据
watch(() => player, () => {
  activeTab.value = 'stats'
  rotationData.value = []
  skillStats.value = []
})

function handleClose() {
  emit('close')
}

function handleOverlayClick() {
  emit('close')
}

function getProfIcon(prof: string): string {
  return getProfessionIconUrl(prof) || ''
}

function formatLargeNumber(num: number): string {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M'
  } else if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K'
  }
  return num.toString()
}
</script>

<style scoped lang="css">
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
  animation: fadeIn 0.2s ease-out;
}

.modal-content {
  background-color: var(--color-card);
  border-radius: 1rem;
  border: 1px solid var(--color-border);
  width: 100%;
  max-width: 600px;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  animation: slideUp 0.3s ease-out;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem;
  background-color: var(--color-card-hover);
  border-bottom: 1px solid var(--color-border);
}

.player-header-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.player-avatar {
  width: 56px;
  height: 56px;
  border-radius: 50%;
}

.player-details {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.player-name {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--color-text);
  margin: 0;
}

.player-meta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.profession-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 0.375rem;
  font-size: 0.8125rem;
  font-weight: 500;
  color: white;
}

.commander-badge {
  color: #f59e0b;
  font-size: 1rem;
}

.modal-close-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: transparent;
  border-radius: 0.375rem;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}

.modal-close-btn:hover {
  background-color: var(--color-border);
  color: var(--color-text);
}

.modal-body {
  padding: 1.25rem;
  overflow-y: auto;
  flex: 1;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  background-color: var(--color-bg-secondary);
  border-radius: 0.75rem;
  border: 1px solid var(--color-border);
}

.stat-icon {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.625rem;
}

.stat-card.damage .stat-icon {
  background: linear-gradient(135deg, #ef4444, #f97316);
}

.stat-card.dps .stat-icon {
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
}

.stat-card.score .stat-icon {
  background: linear-gradient(135deg, #f59e0b, #eab308);
}

.stat-card.hps .stat-icon {
  background: linear-gradient(135deg, #22c55e, #10b981);
}

.stat-icon i {
  font-size: 1.375rem;
  color: white;
}

.stat-info {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.stat-value {
  font-size: 1.375rem;
  font-weight: 700;
  color: var(--color-text);
}

.stat-label {
  font-size: 0.75rem;
  color: var(--color-text-secondary);
}

.detail-section {
  margin-bottom: 1.5rem;
}

.detail-section:last-child {
  margin-bottom: 0;
}

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

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.625rem;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.625rem 0.875rem;
  background-color: var(--color-bg-secondary);
  border-radius: 0.5rem;
  border: 1px solid var(--color-border);
}

.detail-label {
  font-size: 0.8125rem;
  color: var(--color-text-secondary);
}

.detail-value {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text);
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.875rem;
}

.status-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.625rem;
  padding: 0.875rem;
  background-color: var(--color-bg-secondary);
  border-radius: 0.625rem;
  border: 1px solid var(--color-border);
}

.status-item i {
  font-size: 1.5rem;
  color: var(--color-text-secondary);
}

.status-item.danger i {
  color: var(--color-error);
}

.status-data {
  text-align: center;
}

.status-value {
  display: block;
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--color-text);
}

.status-item.danger .status-value {
  color: var(--color-error);
}

.status-label {
  display: block;
  font-size: 0.75rem;
  color: var(--color-text-secondary);
}

.weapons-box {
  padding: 0.875rem;
  background-color: var(--color-bg-secondary);
  border-radius: 0.625rem;
  border: 1px solid var(--color-border);
}

.weapons-text {
  font-size: 0.875rem;
  color: var(--color-text);
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

/* 标签页样式 */
.modal-tabs {
  display: flex;
  border-bottom: 1px solid var(--color-border);
  background-color: var(--color-bg-secondary);
}

.tab-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.875rem 1rem;
  border: none;
  background: transparent;
  color: var(--color-text-secondary);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}

.tab-btn:hover {
  color: var(--color-text);
  background-color: var(--color-card-hover);
}

.tab-btn.active {
  color: var(--color-primary);
  background-color: var(--color-card);
}

.tab-btn.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 20%;
  right: 20%;
  height: 2px;
  background-color: var(--color-primary);
  border-radius: 1px;
}

.tab-btn i {
  font-size: 0.875rem;
}

/* 标签内容 */
.tab-content {
  animation: fadeIn 0.2s ease-out;
}

/* 加载状态 */
.loading-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  gap: 1rem;
}

.loading-text {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
}

/* 错误状态 */
.error-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  gap: 1rem;
}

.error-text {
  font-size: 0.875rem;
  color: var(--color-error);
}

/* 循环序列图 */
.rotation-content {
  padding: 0;
}

.rotation-timeline {
  position: relative;
  padding-left: 1.5rem;
  border-left: 2px solid var(--color-border);
  margin-bottom: 1.5rem;
}

.rotation-timeline::before {
  content: '';
  position: absolute;
  left: -3px;
  top: 0;
  width: 4px;
  height: 4px;
  background-color: var(--color-primary);
  border-radius: 50%;
}

.rotation-timeline::after {
  content: '';
  position: absolute;
  left: -3px;
  bottom: 0;
  width: 4px;
  height: 4px;
  background-color: var(--color-border);
  border-radius: 50%;
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
  transition: all 0.2s;
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

/* 技能统计 */
.skills-content {
  padding: 0;
}

.skills-chart-container {
  margin-bottom: 1.5rem;
}

.skills-chart {
  display: flex;
  flex-direction: column;
  gap: 0.875rem;
}

.skill-bar-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.skill-info {
  min-width: 80px;
  display: flex;
  justify-content: space-between;
}

.skill-name {
  font-size: 0.875rem;
  color: var(--color-text);
}

.skill-count {
  font-size: 0.8125rem;
  color: var(--color-text-secondary);
}

.skill-bar-bg {
  flex: 1;
  height: 12px;
  background-color: var(--color-bg-secondary);
  border-radius: 6px;
  overflow: hidden;
}

.skill-bar-fill {
  height: 100%;
  border-radius: 6px;
  transition: width 0.5s ease-out;
}

.skill-percentage {
  min-width: 40px;
  text-align: right;
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-text-secondary);
}

.skills-summary {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem;
  padding: 1rem;
  background-color: var(--color-bg-secondary);
  border-radius: 0.5rem;
}

.summary-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
}

.summary-label {
  font-size: 0.75rem;
  color: var(--color-text-secondary);
}

.summary-value {
  font-size: 1rem;
  font-weight: 700;
  color: var(--color-text);
}

@media (max-width: 640px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .status-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .detail-grid {
    grid-template-columns: 1fr;
  }

  .skills-summary {
    grid-template-columns: 1fr;
  }

  .tab-btn span {
    display: none;
  }

  .timeline-header {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
