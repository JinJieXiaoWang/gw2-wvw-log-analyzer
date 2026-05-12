<template>
  <div class="skill-rotation-view">
    <PageHeader
      title="技能循环分析"
      subtitle="分析你的技能释放情况，优化你的输出循环"
      icon="pi pi-sync"
      icon-gradient="bg-gradient-to-br from-primary to-secondary"
    />

    <!-- 选择日志区域 -->
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
        <div
          v-if="selectedLogId"
          class="w-full md:w-64"
        >
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
          label="分析技能循环"
          icon="pi pi-refresh"
          class="btn-game"
          :loading="isAnalyzing"
          @click="handleAnalyze"
        />
      </div>
    </div>

    <!-- 分析结果区域 -->
    <div
      v-if="analysisResult"
      class="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6"
    >
      <RotationLeftPanels
        :current-rotation="currentRotation"
        :stats="analysisResult.stats"
        :view-mode="viewMode"
        @update:view-mode="viewMode = $event"
      />
      <RotationRightPanels :mistakes="analysisResult.stats.mistakes" />
    </div>

    <!-- 空状态 -->
    <div
      v-else-if="!isAnalyzing && !selectedLogId"
      class="card text-center py-12 mt-6"
    >
      <i class="pi pi-chart-line text-5xl text-neutral-text-secondary mb-4 opacity-50" />
      <h3 class="text-lg font-semibold text-neutral-text mb-2">
        选择战斗日志开始分析
      </h3>
      <p class="text-neutral-text-secondary">
        选择一个战斗日志和玩家，开始分析技能循环
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import PageHeader from '@/layout/components/PageHeader.vue'
import Button from 'primevue/button'
import Dropdown from 'primevue/dropdown'
import RotationLeftPanels from '@/components/build/rotation/RotationLeftPanels.vue'
import RotationRightPanels from '@/components/build/rotation/RotationRightPanels.vue'
import skillsApi from '@/api/build/skills'
import logsApi from '@/api/combat/logs'

const toast = useToast()

const isAnalyzing = ref(false)
const selectedLogId = ref('')
const selectedMemberId = ref('')
const viewMode = ref<'actual' | 'ideal'>('actual')
const analysisResult = ref<any>(null)
const logOptions = ref<any[]>([])
const memberOptions = ref<any[]>([])

const currentRotation = computed(() => {
  if (!analysisResult.value) return []
  return viewMode.value === 'actual'
    ? analysisResult.value.rotations
    : analysisResult.value.idealRotation
})

const loadLogs = async () => {
  try {
    const result = await logsApi.getLogs()
    if (result && result.data) {
      logOptions.value = result.data.map((log: any) => ({
        value: log.id,
        label: log.filename || `Log ${log.id}`
      }))
    }
  } catch (error) {
    console.error('加载日志列表失败:', error)
  }
}

const handleLogChange = async () => {
  selectedMemberId.value = ''
  if (!selectedLogId.value) {
    memberOptions.value = []
    return
  }
  try {
    const result = await logsApi.getLogDetail(selectedLogId.value)
    if (result && result.data && result.data.members) {
      memberOptions.value = result.data.members.map((member: any) => ({
        id: member.id,
        name: member.name || member.accountName
      }))
    }
  } catch (error) {
    console.error('加载日志详情失败:', error)
  }
}

const handleAnalyze = async () => {
  if (!selectedLogId.value || !selectedMemberId.value) {
    toast.add({ severity: 'warn', summary: '请选择日志和玩家', detail: '请先选择一个战斗日志和玩家', life: 3000 })
    return
  }
  isAnalyzing.value = true
  try {
    const result = await skillsApi.analyzeSkillRotation(selectedLogId.value, selectedMemberId.value)
    if (result) {
      analysisResult.value = result
      toast.add({ severity: 'success', summary: '分析完成', detail: '技能循环分析完成', life: 3000 })
    }
  } catch (error) {
    console.error('分析技能循环失败:', error)
    toast.add({ severity: 'error', summary: '分析失败', detail: error instanceof Error ? error.message : '分析技能循环失败', life: 5000 })
  } finally {
    isAnalyzing.value = false
  }
}

onMounted(() => {
  loadLogs()
})
</script>

<style scoped>@import './BuildSkillRotationView.css';</style>
