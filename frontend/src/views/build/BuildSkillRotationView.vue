<template>
  <div class="skill-rotation-view">
    <PageHeader
      title="技能循环分析"
      subtitle="基于战斗数据的技能效率与表现分析"
      icon="pi pi-sync"
      icon-gradient="bg-gradient-to-br from-primary to-secondary"
    />

    <!-- 选择区域 -->
    <div class="card mt-6">
      <div class="flex flex-col md:flex-row gap-4 items-start md:items-center justify-between">
        <div class="w-full md:w-96">
          <label class="block text-sm font-medium text-neutral-text mb-2">选择战斗日志</label>
          <Dropdown
            v-model="selectedLogId"
            :options="logOptions"
            option-label="label"
            option-value="value"
            placeholder="选择一个战斗日志"
            class="w-full"
            @change="handleLogChange"
          />
        </div>
        <div v-if="selectedLogId" class="w-full md:w-64">
          <label class="block text-sm font-medium text-neutral-text mb-2">选择玩家</label>
          <Dropdown
            v-model="selectedMemberId"
            :options="memberOptions"
            option-label="name"
            option-value="id"
            placeholder="选择一个玩家"
            class="w-full"
          />
        </div>
        <Button
          v-if="selectedLogId && selectedMemberId"
          label="分析"
          icon="pi pi-refresh"
          class="btn-game"
          :loading="isAnalyzing"
          @click="handleAnalyze"
        />
      </div>
    </div>

    <!-- 分析结果 -->
    <template v-if="analysisResult">
      <!-- 概览卡片 -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mt-6">
        <div class="card text-center">
          <div class="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center mx-auto mb-3">
            <i class="pi pi-file text-primary text-xl" />
          </div>
          <p class="text-2xl font-bold text-neutral-text">{{ analysisResult.fight_count }}</p>
          <p class="text-sm text-neutral-text-secondary mt-1">参与战斗</p>
        </div>
        <div class="card text-center">
          <div class="w-12 h-12 rounded-xl bg-status-error/10 flex items-center justify-center mx-auto mb-3">
            <i class="pi pi-bolt text-status-error text-xl" />
          </div>
          <p class="text-2xl font-bold text-neutral-text">{{ formatNumber(analysisResult.total_damage) }}</p>
          <p class="text-sm text-neutral-text-secondary mt-1">总伤害</p>
        </div>
        <div class="card text-center">
          <div class="w-12 h-12 rounded-xl bg-warning/10 flex items-center justify-center mx-auto mb-3">
            <i class="pi pi-chart-line text-warning text-xl" />
          </div>
          <p class="text-2xl font-bold text-neutral-text">{{ formatNumber(analysisResult.avg_dps) }}</p>
          <p class="text-sm text-neutral-text-secondary mt-1">平均DPS</p>
        </div>
        <div class="card text-center">
          <div class="w-12 h-12 rounded-xl bg-status-success/10 flex items-center justify-center mx-auto mb-3">
            <i class="pi pi-heart text-status-success text-xl" />
          </div>
          <p class="text-2xl font-bold text-neutral-text">{{ formatNumber(analysisResult.total_healing) }}</p>
          <p class="text-sm text-neutral-text-secondary mt-1">总治疗</p>
        </div>
      </div>

      <!-- 技能效率 & Buff -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
        <div class="card">
          <h3 class="text-lg font-semibold text-neutral-text mb-4">技能效率</h3>
          <div class="space-y-3">
            <div>
              <div class="flex justify-between text-sm mb-1">
                <span class="text-neutral-text-secondary">技能施法占比</span>
                <span class="text-neutral-text font-medium">{{ analysisResult.skill_cast_uptime }}%</span>
              </div>
              <ProgressBar :value="analysisResult.skill_cast_uptime" :show-value="false" />
            </div>
          </div>
        </div>
        <div class="card">
          <h3 class="text-lg font-semibold text-neutral-text mb-4">Buff 平均覆盖率</h3>
          <div class="space-y-3">
            <div v-for="(val, key) in analysisResult.buffs" :key="key">
              <div class="flex justify-between text-sm mb-1">
                <span class="text-neutral-text-secondary">{{ buffLabel(key) }}</span>
                <span class="text-neutral-text font-medium">{{ val }}%</span>
              </div>
              <ProgressBar :value="val" :show-value="false" />
            </div>
          </div>
        </div>
      </div>

      <!-- 生存 & 战斗贡献 -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
        <div class="card">
          <h3 class="text-lg font-semibold text-neutral-text mb-4">生存数据</h3>
          <div class="grid grid-cols-2 gap-4">
            <div class="p-3 bg-neutral-800 rounded-lg text-center">
              <p class="text-xl font-bold text-neutral-text">{{ formatNumber(analysisResult.survival.damage_taken) }}</p>
              <p class="text-xs text-neutral-text-secondary mt-1">承受伤害</p>
            </div>
            <div class="p-3 bg-neutral-800 rounded-lg text-center">
              <p class="text-xl font-bold text-neutral-text">{{ analysisResult.survival.deaths }}</p>
              <p class="text-xs text-neutral-text-secondary mt-1">死亡次数</p>
            </div>
            <div class="p-3 bg-neutral-800 rounded-lg text-center">
              <p class="text-xl font-bold text-neutral-text">{{ analysisResult.survival.downs }}</p>
              <p class="text-xs text-neutral-text-secondary mt-1">倒地次数</p>
            </div>
            <div class="p-3 bg-neutral-800 rounded-lg text-center">
              <p class="text-xl font-bold text-neutral-text">{{ analysisResult.survival.dodge_count }}</p>
              <p class="text-xs text-neutral-text-secondary mt-1">翻滚次数</p>
            </div>
          </div>
        </div>
        <div class="card">
          <h3 class="text-lg font-semibold text-neutral-text mb-4">战斗贡献</h3>
          <div class="grid grid-cols-2 gap-4">
            <div class="p-3 bg-neutral-800 rounded-lg text-center">
              <p class="text-xl font-bold text-neutral-text">{{ analysisResult.combat.killed }}</p>
              <p class="text-xs text-neutral-text-secondary mt-1">击杀</p>
            </div>
            <div class="p-3 bg-neutral-800 rounded-lg text-center">
              <p class="text-xl font-bold text-neutral-text">{{ analysisResult.combat.downed }}</p>
              <p class="text-xs text-neutral-text-secondary mt-1">击倒</p>
            </div>
            <div class="p-3 bg-neutral-800 rounded-lg text-center">
              <p class="text-xl font-bold text-neutral-text">{{ analysisResult.combat.boon_strips }}</p>
              <p class="text-xs text-neutral-text-secondary mt-1">削增益</p>
            </div>
            <div class="p-3 bg-neutral-800 rounded-lg text-center">
              <p class="text-xl font-bold text-neutral-text">{{ analysisResult.combat.condition_cleanses }}</p>
              <p class="text-xs text-neutral-text-secondary mt-1">清症状</p>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- 空状态 -->
    <div v-else-if="!isAnalyzing && !selectedLogId" class="card text-center py-12 mt-6">
      <i class="pi pi-chart-line text-5xl text-neutral-text-secondary mb-4 opacity-50" />
      <h3 class="text-lg font-semibold text-neutral-text mb-2">选择战斗日志开始分析</h3>
      <p class="text-neutral-text-secondary">选择一个战斗日志和玩家，查看技能效率与战斗表现</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import PageHeader from '@/layout/components/PageHeader.vue'
import Button from 'primevue/button'
import Dropdown from 'primevue/dropdown'
import ProgressBar from 'primevue/progressbar'
import skillsApi from '@/api/build/skills'
import logsApi from '@/api/combat/logs'

const toast = useToast()

const isAnalyzing = ref(false)
const selectedLogId = ref('')
const selectedMemberId = ref('')
const analysisResult = ref<any>(null)
const logOptions = ref<any[]>([])
const memberOptions = ref<any[]>([])

const BUFF_LABELS: Record<string, string> = {
  might: '力量', fury: '狂怒', quickness: '急速',
  alacrity: '敏捷', protection: '保护', stability: '稳固',
}

const buffLabel = (key: string) => BUFF_LABELS[key] || key

const formatNumber = (num: number): string => {
  if (!num && num !== 0) return '0'
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
  return num.toString()
}

const loadLogs = async () => {
  try {
    const result = await logsApi.getLogs()
    if (result?.data?.items) {
      logOptions.value = result.data.items.map((log: any) => ({
        value: String(log.id),
        label: log.filename || `Log ${log.id}`,
      }))
    }
  } catch (error) {
    console.error('加载日志列表失败:', error)
  }
}

const handleLogChange = async () => {
  selectedMemberId.value = ''
  analysisResult.value = null
  if (!selectedLogId.value) {
    memberOptions.value = []
    return
  }
  try {
    const result = await logsApi.getLogDetail(selectedLogId.value)
    if (result?.data?.members) {
      memberOptions.value = result.data.members.map((member: any) => ({
        id: String(member.id),
        name: member.name || member.accountName || member.account || `Player ${member.id}`,
      }))
    }
  } catch (error) {
    console.error('加载日志详情失败:', error)
  }
}

const handleAnalyze = async () => {
  if (!selectedLogId.value || !selectedMemberId.value) {
    toast.add({ severity: 'warn', summary: '提示', detail: '请先选择日志和玩家', life: 3000 })
    return
  }
  isAnalyzing.value = true
  try {
    const result = await skillsApi.analyzeSkillRotation(selectedLogId.value, selectedMemberId.value)
    if (result) {
      analysisResult.value = result
      toast.add({ severity: 'success', summary: '分析完成', detail: '技能分析数据已加载', life: 3000 })
    } else {
      toast.add({ severity: 'warn', summary: '无数据', detail: '未找到该玩家的战斗数据', life: 3000 })
    }
  } catch (error: any) {
    console.error('分析失败:', error)
    toast.add({ severity: 'error', summary: '分析失败', detail: error?.message || '请求失败', life: 5000 })
  } finally {
    isAnalyzing.value = false
  }
}

onMounted(() => {
  loadLogs()
})
</script>

<style scoped>@import '@/styles/views/build/BuildSkillRotationView.css';</style>
