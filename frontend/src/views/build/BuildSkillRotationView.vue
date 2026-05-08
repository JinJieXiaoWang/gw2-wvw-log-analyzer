<template>
  <div class="skill-rotation-view">
    <!-- 页面头部 -->
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
          label="分析技能循环"
          icon="pi pi-refresh"
          class="btn-game"
          :loading="isAnalyzing"
          @click="handleAnalyze"
        />
      </div>
    </div>

    <!-- 分析结果区域 -->
    <div v-if="analysisResult" class="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6">
      <!-- 左侧：技能循环可视化 -->
      <div class="lg:col-span-2 space-y-6">
        <div class="card">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold text-neutral-text">技能循环时间线</h3>
            <div class="flex items-center gap-2">
              <Button
                label="实际循环"
                :severity="viewMode === 'actual' ? 'primary' : 'secondary'"
                @click="viewMode = 'actual'"
              />
              <Button
                label="理想循环"
                :severity="viewMode === 'ideal' ? 'primary' : 'secondary'"
                @click="viewMode = 'ideal'"
              />
            </div>
          </div>

          <!-- 技能时间线 -->
          <div class="skill-timeline">
            <div class="flex items-center gap-2">
              <div
                v-for="(skill, index) in currentRotation"
                :key="index"
                class="skill-item"
                :class="{ 'skill-mistake': skill.isMistake }"
              >
                <div class="skill-icon">{{ skill.icon || '🛡️'}}</div>
                <div class="skill-info">
                  <div class="skill-name">{{ skill.name }}</div>
                  <div class="skill-time">{{ formatTime(skill.timestamp) }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 技能统计 -->
        <div class="card">
          <h3 class="text-lg font-semibold text-neutral-text mb-4">技能释放统计</h3>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div class="stat-box">
              <div class="stat-value">{{ analysisResult.stats.totalCasts }}</div>
              <div class="stat-label">总释放次数</div>
            </div>
            <div class="stat-box">
              <div class="stat-value">{{ analysisResult.stats.successRate }}%</div>
              <div class="stat-label">成功率</div>
            </div>
            <div class="stat-box">
              <div class="stat-value">{{ analysisResult.stats.mistakes.length }}</div>
              <div class="stat-label">失误次数</div>
            </div>
            <div class="stat-box">
              <div class="stat-value">{{ analysisResult.stats.avgCastTime }}s</div>
              <div class="stat-label">平均释放间隔</div>
            </div>
          </div>
        </div>

        <!-- 技能分布图表 -->
        <div class="card">
          <h3 class="text-lg font-semibold text-neutral-text mb-4">技能使用分布</h3>
          <div class="h-64">
            <!-- 这里可以使用echarts图表占位 -->
            <div class="chart-placeholder flex items-center justify-center h-full text-neutral-text-secondary">
              <i class="pi pi-chart-bar text-4xl mr-2"></i>
              <span>图表组件待接入</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧：失误详情 -->
      <div class="space-y-6">
        <!-- 失误列表 -->
        <div class="card">
          <h3 class="text-lg font-semibold text-neutral-text mb-4">失误详情</h3>
          <div v-if="analysisResult.stats.mistakes.length > 0" class="space-y-3">
            <div
              v-for="(mistake, index) in analysisResult.stats.mistakes"
              :key="index"
              class="mistake-item"
            >
              <div class="flex items-start gap-3">
                <i class="pi pi-exclamation-triangle text-yellow-500 mt-1"></i>
                <div class="flex-1">
                  <div class="mistake-title">{{ mistake.skillName }}</div>
                  <div class="mistake-description">{{ mistake.description }}</div>
                  <div class="mistake-time">{{ formatTime(mistake.timestamp) }}</div>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="text-center py-8 text-neutral-text-secondary">
            <i class="pi pi-check-circle text-3xl text-green-500 mb-2"></i>
            <p>太棒了，没有发现失误！</p>
          </div>
        </div>

        <!-- 优化建议 -->
        <div class="card">
          <h3 class="text-lg font-semibold text-neutral-text mb-4">优化建议</h3>
          <div class="space-y-3">
            <div class="suggestion-item">
              <div class="flex items-start gap-3">
                <i class="pi pi-lightbulb text-yellow-500 mt-1"></i>
                <div>
                  <div class="suggestion-title">优化技能释放顺序</div>
                  <div class="suggestion-description">确保关键技能的CD一好就释放</div>
                </div>
              </div>
            </div>
            <div class="suggestion-item">
              <div class="flex items-start gap-3">
                <i class="pi pi-lightbulb text-yellow-500 mt-1"></i>
                <div>
                  <div class="suggestion-title">关注资源管理</div>
                  <div class="suggestion-description">保持资源（能量/怒气/集中值）的合理分配</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 历史记录 -->
        <div class="card">
          <h3 class="text-lg font-semibold text-neutral-text mb-4">历史分析</h3>
          <div class="space-y-2">
            <div class="text-center py-4 text-neutral-text-secondary">
              暂无历史记录
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else-if="!isAnalyzing && !selectedLogId" class="card text-center py-12 mt-6">
      <i class="pi pi-chart-line text-5xl text-neutral-text-secondary mb-4 opacity-50"></i>
      <h3 class="text-lg font-semibold text-neutral-text mb-2">选择战斗日志开始分析</h3>
      <p class="text-neutral-text-secondary">选择一个战斗日志和玩家，开始分析技能循环</p>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 技能循环分析页面
 * 功能：分析战斗日志中的技能释放情况
 * 作者：帅姐姐
 * 创建日期：2026-05-04
 */

import { ref, computed, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';
import PageHeader from '@/components/common/PageHeader.vue';
import Button from 'primevue/button';
import Dropdown from 'primevue/dropdown';
import skillsApi from '@/api/build/skills';
import logsApi from '@/api/combat/logs';

// Toast 服务
const toast = useToast();

// 状态
const isAnalyzing = ref(false);
const selectedLogId = ref('');
const selectedMemberId = ref('');
const viewMode = ref<'actual' | 'ideal'>('actual');
const analysisResult = ref<any>(null);
const logOptions = ref<any[]>([]);
const memberOptions = ref<any[]>([]);

// 计算属性
const currentRotation = computed(() => {
  if (!analysisResult.value) return [];
  return viewMode.value === 'actual'
    ? analysisResult.value.rotations
    : analysisResult.value.idealRotation;
});

// 方法
const formatTime = (seconds: number) => {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, '0')}`;
};

// 加载日志列表
const loadLogs = async () => {
  try {
    const result = await logsApi.getLogs();
    if (result && result.data) {
      logOptions.value = result.data.map((log: any) => ({
        value: log.id,
        label: log.filename || `Log ${log.id}`
      }));
    }
  } catch (error) {
    console.error('加载日志列表失败:', error);
  }
};

// 日志变化时加载成员列表
const handleLogChange = async () => {
  selectedMemberId.value = '';
  if (!selectedLogId.value) {
    memberOptions.value = [];
    return;
  }

  try {
    const result = await logsApi.getLogDetail(selectedLogId.value);
    if (result && result.data && result.data.members) {
      memberOptions.value = result.data.members.map((member: any) => ({
        id: member.id,
        name: member.name || member.accountName
      }));
    }
  } catch (error) {
    console.error('加载日志详情失败:', error);
  }
};

// 分析技能循环
const handleAnalyze = async () => {
  if (!selectedLogId.value || !selectedMemberId.value) {
    toast.add({
      severity: 'warn',
      summary: '请选择日志和玩家',
      detail: '请先选择一个战斗日志和玩家',
      life: 3000
    });
    return;
  }

  isAnalyzing.value = true;

  try {
    const result = await skillsApi.analyzeSkillRotation(
      selectedLogId.value,
      selectedMemberId.value
    );

    if (result) {
      analysisResult.value = result;
      toast.add({
        severity: 'success',
        summary: '分析完成',
        detail: '技能循环分析完成',
        life: 3000
      });
    }
  } catch (error) {
    console.error('分析技能循环失败:', error);
    toast.add({
      severity: 'error',
      summary: '分析失败',
      detail: error instanceof Error ? error.message : '分析技能循环失败',
      life: 5000
    });
  } finally {
    isAnalyzing.value = false;
  }
};

// 组件挂载时加载数据
onMounted(() => {
  loadLogs();
});
</script>

<style scoped lang="postcss">
.skill-rotation-view {
  min-height: 100vh;
  padding-bottom: 2rem;
}

.card {
  @apply bg-neutral-900 rounded-xl p-6 border border-neutral-800;
}

.skill-timeline {
  @apply overflow-x-auto;
}

.skill-item {
  @apply flex-shrink-0 p-3 bg-neutral-800 rounded-lg border border-neutral-700 hover:border-neutral-600 transition-colors;
}

.skill-item.skill-mistake {
  @apply border-yellow-500/50 bg-yellow-500/10;
}

.skill-icon {
  @apply text-2xl mb-2;
}

.skill-info {
  @apply text-center;
}

.skill-name {
  @apply text-sm font-medium text-neutral-text;
}

.skill-time {
  @apply text-xs text-neutral-text-secondary;
}

.stat-box {
  @apply p-4 bg-neutral-800 rounded-lg text-center;
}

.stat-value {
  @apply text-2xl font-bold text-neutral-text mb-1;
}

.stat-label {
  @apply text-sm text-neutral-text-secondary;
}

.chart-placeholder {
  @apply bg-neutral-800 rounded-lg;
}

.mistake-item {
  @apply p-3 bg-neutral-800 rounded-lg border border-neutral-700;
}

.mistake-title {
  @apply text-sm font-medium text-neutral-text;
}

.mistake-description {
  @apply text-sm text-neutral-text-secondary mt-1;
}

.mistake-time {
  @apply text-xs text-neutral-text-secondary mt-1;
}

.suggestion-item {
  @apply p-3 bg-neutral-800 rounded-lg;
}

.suggestion-title {
  @apply text-sm font-medium text-neutral-text;
}

.suggestion-description {
  @apply text-sm text-neutral-text-secondary mt-1;
}
</style>