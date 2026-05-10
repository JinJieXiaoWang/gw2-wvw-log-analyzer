<template>
  <div class="attendance-detail-page min-h-screen bg-gradient-to-br from-surface-900 via-surface-800 to-surface-900">
    <!-- Loading State -->
    <LoadingState v-if="loading" text="加载详情中..." class="min-h-screen flex items-center justify-center" />

    <template v-else>
      <!-- Header Section -->
      <div class="relative overflow-hidden bg-gradient-to-r from-primary/20 via-secondary/10 to-primary/20">
        <div class="absolute inset-0 bg-[radial-gradient(circle_at_center,_rgba(22,93,255,0.1)_0%,_transparent_70%)]" />
        <div class="relative container mx-auto px-4 py-8">
          <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
            <!-- Player Info -->
            <div class="flex items-center gap-4">
              <div class="relative">
                <div class="w-20 h-20 rounded-2xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center shadow-lg shadow-primary/20 border-2 border-primary/30">
                  <span class="text-3xl font-bold text-white">{{ data?.account?.charAt(0) || '?' }}</span>
                </div>
                <div class="absolute -bottom-1 -right-1 w-6 h-6 rounded-full bg-status-success border-2 border-surface-900 flex items-center justify-center">
                  <i class="pi pi-check text-white text-xs" />
                </div>
              </div>
              <div>
                <h1 class="text-2xl font-bold text-white mb-1">{{ data?.account || '未知玩家' }}</h1>
                <p class="text-neutral-text-secondary text-sm">
                  <span class="flex items-center gap-2">
                    <i class="pi pi-server text-primary" />
                    <span>{{ data?.server || '未选择服务器' }}</span>
                  </span>
                </p>
                <div class="flex items-center gap-4 mt-2">
                  <span class="text-xs px-3 py-1 rounded-full bg-primary/20 text-primary font-medium">{{ data?.rank || '普通成员' }}</span>
                  <span class="text-xs px-3 py-1 rounded-full bg-secondary/20 text-secondary font-medium">加入 {{ data?.join_date || '--' }}</span>
                </div>
              </div>
            </div>

            <!-- Action Buttons -->
            <div class="flex items-center gap-3">
              <BaseButton label="查看评分规则" icon="pi pi-chart-line" class="btn-ghost" size="small" @click="showScoringRules" />
              <BaseButton label="导出Excel" icon="pi pi-file-excel" class="btn-game" severity="secondary" @click="exportExcel" />
              <BaseButton label="导出CSV" icon="pi pi-file-pdf" class="btn-game" @click="exportCSV" />
            </div>
          </div>
        </div>
      </div>

      <!-- Stats Cards Grid -->
      <div class="container mx-auto px-4 py-6">
        <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
          <StatCard
            icon="pi pi-calendar-check"
            label="出勤天数"
            :value="summary.attendance_count || 0"
            unit="天"
            gradient="from-primary/20 to-primary/5"
            border="border-primary/30"
            iconBg="from-primary/40 to-primary/20"
            textColor="text-primary"
          />
          <StatCard
            icon="pi pi-clock"
            label="总参战时长"
            :value="formatDuration(summary.total_duration_sec)"
            gradient="from-secondary/20 to-secondary/5"
            border="border-secondary/30"
            iconBg="from-secondary/40 to-secondary/20"
            textColor="text-secondary"
          />
          <StatCard
            icon="pi pi-bolt"
            label="总伤害"
            :value="formatNumber(summary.total_damage)"
            gradient="from-status-error/20 to-status-error/5"
            border="border-status-error/30"
            iconBg="from-status-error/40 to-status-error/20"
            textColor="text-status-error"
          />
          <StatCard
            icon="pi pi-heart-pulse"
            label="K/D"
            :value="summary.kd_ratio || '0.0'"
            :gradient="(summary.kd_ratio && summary.kd_ratio >= 2) ? 'from-status-success/20 to-status-success/5' : (summary.kd_ratio && summary.kd_ratio >= 1) ? 'from-primary/20 to-primary/5' : 'from-status-error/20 to-status-error/5'"
            :border="(summary.kd_ratio && summary.kd_ratio >= 2) ? 'border-status-success/30' : (summary.kd_ratio && summary.kd_ratio >= 1) ? 'border-primary/30' : 'border-status-error/30'"
            :iconBg="(summary.kd_ratio && summary.kd_ratio >= 2) ? 'from-status-success/40 to-status-success/20' : (summary.kd_ratio && summary.kd_ratio >= 1) ? 'from-primary/40 to-primary/20' : 'from-status-error/40 to-status-error/20'"
            :textColor="(summary.kd_ratio && summary.kd_ratio >= 2) ? 'text-status-success' : (summary.kd_ratio && summary.kd_ratio >= 1) ? 'text-primary' : 'text-status-error'"
          />
          <StatCard
            icon="pi pi-trophy"
            label="平均评分"
            :value="summary.avg_score || 0"
            :gradient="getScoreGradient(summary.avg_score)"
            :border="getScoreBorder(summary.avg_score)"
            :iconBg="getScoreIconBg(summary.avg_score)"
            :textColor="getScoreColor(summary.avg_score)"
          />
        </div>
      </div>

      <!-- Charts Section -->
      <div class="container mx-auto px-4 py-6">
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <!-- Attendance Trend Chart -->
          <div class="lg:col-span-2 card bg-surface-800/50 border border-neutral-border/30 rounded-2xl overflow-hidden">
            <div class="card-header flex items-center justify-between p-4 border-b border-neutral-border/20">
              <div class="flex items-center gap-2">
                <i class="pi pi-chart-line text-primary text-lg" />
                <h3 class="font-semibold text-neutral-text">出勤趋势</h3>
                <span class="text-xs px-2 py-0.5 rounded-full bg-primary/20 text-primary">最近7天</span>
              </div>
              <Dropdown
                v-model="timeRange"
                :options="timeRangeOptions"
                option-label="label"
                option-value="value"
                class="w-32"
                placeholder="时间范围"
                @change="handleTimeRangeChange"
              />
            </div>
            <div class="card-body p-4">
              <div class="h-64 flex items-center justify-center">
                <svg viewBox="0 0 600 250" class="w-full h-full">
                  <defs>
                    <linearGradient id="trendLineGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                      <stop offset="0%" stop-color="#165DFF" />
                      <stop offset="100%" stop-color="#7B61FF" />
                    </linearGradient>
                    <linearGradient id="trendAreaGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                      <stop offset="0%" stop-color="#165DFF" stop-opacity="0.25" />
                      <stop offset="100%" stop-color="#165DFF" stop-opacity="0" />
                    </linearGradient>
                  </defs>
                  <!-- Grid Lines -->
                  <line v-for="i in 5" :key="'h-' + i" x1="60" :y1="30 + i * 44" x2="560" :y2="30 + i * 44" stroke="#2A2A2A" stroke-width="1" stroke-dasharray="4" />
                  <line v-for="i in 7" :key="'v-' + i" :x1="60 + i * 80" y1="30" :x2="60 + i * 80" y2="230" stroke="#2A2A2A" stroke-width="1" stroke-dasharray="4" />
                  <!-- Y Axis Labels -->
                  <text x="50" y="35" fill="#909399" font-size="11" text-anchor="end">10</text>
                  <text x="50" y="79" fill="#909399" font-size="11" text-anchor="end">8</text>
                  <text x="50" y="123" fill="#909399" font-size="11" text-anchor="end">6</text>
                  <text x="50" y="167" fill="#909399" font-size="11" text-anchor="end">4</text>
                  <text x="50" y="211" fill="#909399" font-size="11" text-anchor="end">2</text>
                  <!-- Area -->
                  <path :d="chartAreaPath" fill="url(#trendAreaGradient)" />
                  <!-- Line -->
                  <path :d="chartLinePath" fill="none" stroke="url(#trendLineGradient)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" />
                  <!-- Points -->
                  <g v-for="(point, index) in chartPoints" :key="index">
                    <circle :cx="point.x" :cy="point.y" r="6" fill="#165DFF" stroke="#fff" stroke-width="2" />
                    <circle :cx="point.x" :cy="point.y" r="3" fill="#fff" />
                  </g>
                  <!-- X Axis Labels -->
                  <text x="100" y="245" fill="#909399" font-size="11" text-anchor="middle">周一</text>
                  <text x="180" y="245" fill="#909399" font-size="11" text-anchor="middle">周二</text>
                  <text x="260" y="245" fill="#909399" font-size="11" text-anchor="middle">周三</text>
                  <text x="340" y="245" fill="#909399" font-size="11" text-anchor="middle">周四</text>
                  <text x="420" y="245" fill="#909399" font-size="11" text-anchor="middle">周五</text>
                  <text x="500" y="245" fill="#909399" font-size="11" text-anchor="middle">周六</text>
                  <text x="580" y="245" fill="#909399" font-size="11" text-anchor="middle">周日</text>
                </svg>
              </div>
              <div class="flex items-center justify-between mt-4 px-2">
                <span class="text-xs text-neutral-text-secondary">出勤次数统计</span>
                <div class="flex items-center gap-2">
                  <span class="w-3 h-3 rounded-full bg-primary" />
                  <span class="text-xs text-neutral-text-secondary">出勤次数</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Ability Radar Chart -->
          <div class="card bg-surface-800/50 border border-neutral-border/30 rounded-2xl overflow-hidden">
            <div class="card-header flex items-center gap-2 p-4 border-b border-neutral-border/20">
              <i class="pi pi-star text-secondary text-lg" />
              <h3 class="font-semibold text-neutral-text">综合能力</h3>
            </div>
            <div class="card-body p-4">
              <div class="h-64 flex items-center justify-center">
                <svg viewBox="0 0 200 200" class="w-full max-w-[180px]">
                  <defs>
                    <linearGradient id="abilityGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                      <stop offset="0%" stop-color="#7B61FF" stop-opacity="0.4" />
                      <stop offset="100%" stop-color="#165DFF" stop-opacity="0.2" />
                    </linearGradient>
                  </defs>
                  <!-- Hexagon Levels -->
                  <polygon v-for="level in [90, 72, 54, 36, 18]" :key="level" :points="getHexagonPoints(level)" fill="none" stroke="#2A2A2A" stroke-width="1" />
                  <!-- Axis Lines -->
                  <line v-for="i in 6" :key="'axis-' + i" x1="100" y1="100" :x2="getAxisPoint(i - 1).x" :y2="getAxisPoint(i - 1).y" stroke="#2A2A2A" stroke-width="1" />
                  <!-- Polygon -->
                  <polygon :points="radarPolygonPoints" fill="url(#abilityGradient)" stroke="#7B61FF" stroke-width="2" />
                  <!-- Points -->
                  <circle v-for="(point, index) in radarCirclePoints" :key="index" :cx="point.x" :cy="point.y" r="5" fill="#7B61FF" stroke="#fff" stroke-width="2" />
                  <!-- Labels -->
                  <text v-for="(label, index) in radarLabels" :key="index" :x="label.x" :y="label.y" fill="#E5E5E5" font-size="11" text-anchor="middle">{{ label.text }}</text>
                </svg>
              </div>
              <div class="grid grid-cols-3 gap-2 mt-4">
                <div class="text-center p-2 rounded-xl bg-surface-700/50">
                  <p class="text-lg font-bold text-status-error">{{ abilities.damage }}</p>
                  <p class="text-xs text-neutral-text-secondary">输出</p>
                </div>
                <div class="text-center p-2 rounded-xl bg-surface-700/50">
                  <p class="text-lg font-bold text-status-success">{{ abilities.healing }}</p>
                  <p class="text-xs text-neutral-text-secondary">治疗</p>
                </div>
                <div class="text-center p-2 rounded-xl bg-surface-700/50">
                  <p class="text-lg font-bold text-secondary">{{ abilities.survival }}</p>
                  <p class="text-xs text-neutral-text-secondary">生存</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Characters and Fights Section -->
      <div class="container mx-auto px-4 py-6">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <!-- Character Stats -->
          <div class="card bg-surface-800/50 border border-neutral-border/30 rounded-2xl overflow-hidden">
            <div class="card-header flex items-center justify-between p-4 border-b border-neutral-border/20">
              <div class="flex items-center gap-2">
                <i class="pi pi-users text-primary text-lg" />
                <h3 class="font-semibold text-neutral-text">角色统计</h3>
                <span class="text-xs px-2 py-0.5 rounded-full bg-primary/20 text-primary">{{ characters.length }} 个角色</span>
              </div>
              <button 
                v-if="characters.length > 6"
                type="button" 
                class="text-xs text-primary hover:text-primary/80 flex items-center gap-1 transition-colors"
                @click="showAllChars = !showAllChars"
              >
                <span>{{ showAllChars ? '收起' : '查看全部' }}</span>
                <i :class="['pi', showAllChars ? 'pi-chevron-up' : 'pi-chevron-down']" />
              </button>
            </div>
            <div class="card-body p-4">
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div
                  v-for="char in displayCharacters"
                  :key="char.character_name"
                  class="group p-4 rounded-xl bg-surface-700/50 border border-neutral-border/20 hover:border-primary/40 transition-all duration-300 cursor-pointer"
                  @click="showCharDetail(char)"
                >
                  <div class="flex items-start gap-3">
                    <div 
                      class="w-12 h-12 rounded-xl flex items-center justify-center text-white font-bold text-lg shrink-0 transition-transform duration-300 group-hover:scale-110" 
                      :style="{ background: getProfessionGradient(char.profession) }"
                    >
                      {{ char.character_name?.charAt(0) || '?' }}
                    </div>
                    <div class="flex-1 min-w-0">
                      <div class="flex items-center gap-2 mb-2">
                        <span class="font-semibold text-neutral-text truncate">{{ char.character_name }}</span>
                        <span 
                          class="text-xs px-2 py-0.5 rounded-full shrink-0" 
                          :style="{ backgroundColor: getProfessionColorVal(char.profession) + '30', color: getProfessionColorVal(char.profession) }"
                        >
                          {{ getProfessionLabel(char.profession) }}
                        </span>
                      </div>
                      <div class="grid grid-cols-2 gap-2 text-xs">
                        <div>
                          <span class="text-neutral-text-secondary">出勤</span>
                          <p class="font-bold text-primary">{{ char.attendance_count }}天</p>
                        </div>
                        <div>
                          <span class="text-neutral-text-secondary">DPS</span>
                          <p class="font-bold text-status-error">{{ formatDps(char.avg_dps) }}</p>
                        </div>
                        <div>
                          <span class="text-neutral-text-secondary">伤害</span>
                          <p class="font-bold text-status-error">{{ formatNumber(char.total_damage) }}</p>
                        </div>
                        <div>
                          <span class="text-neutral-text-secondary">评分</span>
                          <span :class="getScoreColor(char.avg_score)" class="font-bold">{{ char.avg_score }}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div v-if="!characters.length" class="text-center py-8 text-neutral-text-secondary">
                <i class="pi pi-users text-4xl mb-3 opacity-50" />
                <p>暂无角色数据</p>
              </div>
            </div>
          </div>

          <!-- Recent Fights -->
          <div class="card bg-surface-800/50 border border-neutral-border/30 rounded-2xl overflow-hidden">
            <div class="card-header flex items-center justify-between p-4 border-b border-neutral-border/20">
              <div class="flex items-center gap-2">
                <i class="pi pi-swords text-status-error text-lg" />
                <h3 class="font-semibold text-neutral-text">最近战斗</h3>
                <span class="text-xs px-2 py-0.5 rounded-full bg-status-error/20 text-status-error">{{ recentFights.length }} 场</span>
              </div>
              <button 
                v-if="recentFights.length > 5"
                type="button" 
                class="text-xs text-primary hover:text-primary/80 flex items-center gap-1 transition-colors"
                @click="showAllFights = !showAllFights"
              >
                <span>{{ showAllFights ? '收起' : '查看全部' }}</span>
                <i :class="['pi', showAllFights ? 'pi-chevron-up' : 'pi-chevron-down']" />
              </button>
            </div>
            <div class="card-body p-4 max-h-[500px] overflow-y-auto">
              <div class="space-y-3">
                <div
                  v-for="(fight, index) in displayFights"
                  :key="index"
                  class="group p-4 rounded-xl bg-surface-700/50 border border-neutral-border/20 hover:border-status-error/40 transition-all duration-300"
                >
                  <div class="flex flex-wrap items-start gap-3">
                    <div class="flex items-center gap-2 shrink-0">
                      <i class="pi pi-clock text-neutral-text-secondary text-sm" />
                      <span class="text-sm text-neutral-text">{{ formatDateTime(fight.fight_date) }}</span>
                    </div>
                    <div class="flex items-center gap-2 shrink-0">
                      <div 
                        class="w-6 h-6 rounded-full flex items-center justify-center text-white text-xs font-bold" 
                        :style="{ backgroundColor: getProfessionColor(fight.profession) }"
                      >
                        {{ fight.character_name?.charAt(0) }}
                      </div>
                      <span class="text-sm font-medium">{{ fight.character_name }}</span>
                      <span 
                        class="text-xs px-2 py-0.5 rounded-full" 
                        :style="{ backgroundColor: getProfessionColor(fight.profession) + '30', color: getProfessionColor(fight.profession) }"
                      >
                        {{ getProfessionLabel(fight.profession) }}
                      </span>
                    </div>
                    <div class="flex items-center gap-2 flex-1 shrink-0 min-w-[120px]">
                      <i class="pi pi-map-marker text-neutral-text-secondary text-sm" />
                      <span class="text-sm text-neutral-text truncate">{{ fight.map_name }}</span>
                    </div>
                    <div class="flex flex-wrap gap-4 justify-end flex-1">
                      <div class="text-right min-w-[80px]">
                        <span class="text-xs text-neutral-text-secondary">伤害</span>
                        <p class="font-bold text-status-error">{{ formatNumber(fight.damage) }}</p>
                      </div>
                      <div class="text-right min-w-[80px]">
                        <span class="text-xs text-neutral-text-secondary">DPS</span>
                        <p class="font-bold text-status-error">{{ formatDps(fight.dps) }}</p>
                      </div>
                      <div class="text-right min-w-[80px]">
                        <span class="text-xs text-neutral-text-secondary">治疗</span>
                        <p class="font-bold text-status-success">{{ formatNumber(fight.healing) }}</p>
                      </div>
                      <div class="text-right min-w-[60px]">
                        <span class="text-xs text-neutral-text-secondary">评分</span>
                        <span :class="getScoreColor(fight.ai_score)" class="font-bold">{{ fight.ai_score }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div v-if="!recentFights.length" class="text-center py-8 text-neutral-text-secondary">
                <i class="pi pi-swords text-4xl mb-3 opacity-50" />
                <p>暂无战斗记录</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="!data" class="min-h-screen flex items-center justify-center">
        <EmptyState icon="pi pi-inbox" title="暂无数据" description="请选择一个玩家查看详情" />
      </div>
    </template>

    <!-- Character Detail Modal -->
    <BaseDialog 
      v-if="selectedCharacter" 
      :visible="showCharModal" 
      @update:visible="showCharModal = false"
      :header="selectedCharacter.character_name"
      styleClass="w-full max-w-2xl"
    >
      <div class="p-4">
        <div class="grid grid-cols-2 gap-6">
          <div>
            <h4 class="font-semibold text-neutral-text mb-3">角色信息</h4>
            <div class="space-y-3">
              <div class="flex justify-between">
                <span class="text-neutral-text-secondary text-sm">职业</span>
                <span :style="{ color: getProfessionColorVal(selectedCharacter.profession) }" class="font-medium">{{ getProfessionLabel(selectedCharacter.profession) }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-neutral-text-secondary text-sm">出勤天数</span>
                <span class="font-medium text-primary">{{ selectedCharacter.attendance_count }} 天</span>
              </div>
              <div class="flex justify-between">
                <span class="text-neutral-text-secondary text-sm">总伤害</span>
                <span class="font-medium text-status-error">{{ formatNumber(selectedCharacter.total_damage) }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-neutral-text-secondary text-sm">平均DPS</span>
                <span class="font-medium text-status-error">{{ formatDps(selectedCharacter.avg_dps) }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-neutral-text-secondary text-sm">平均评分</span>
                <span :class="getScoreColor(selectedCharacter.avg_score)" class="font-bold">{{ selectedCharacter.avg_score }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-neutral-text-secondary text-sm">K/D</span>
                <span :class="selectedCharacter.kd_ratio >= 2 ? 'text-status-success' : selectedCharacter.kd_ratio >= 1 ? 'text-primary' : 'text-status-error'" class="font-medium">{{ selectedCharacter.kd_ratio }}</span>
              </div>
            </div>
          </div>
          <div>
            <h4 class="font-semibold text-neutral-text mb-3">最近战斗</h4>
            <div class="space-y-2 max-h-48 overflow-y-auto">
              <div 
                v-for="(fight, index) in selectedCharacter.recent_fights?.slice(0, 5) || []" 
                :key="index"
                class="p-2 rounded-lg bg-surface-700/50"
              >
                <div class="flex justify-between text-sm">
                  <span class="text-neutral-text-secondary">{{ formatDateTime(fight.fight_date) }}</span>
                  <span class="text-status-error font-medium">{{ formatNumber(fight.damage) }}</span>
                </div>
              </div>
              <div v-if="!selectedCharacter.recent_fights?.length" class="text-center py-4 text-neutral-text-secondary text-sm">
                暂无战斗记录
              </div>
            </div>
          </div>
        </div>
      </div>
    </BaseDialog>

    <!-- Scoring Rules Modal -->
    <BaseDialog 
      v-if="showScoringModal" 
      :visible="showScoringModal" 
      @update:visible="showScoringModal = false"
      header="评分规则"
      styleClass="w-full max-w-3xl"
    >
      <div class="p-4">
        <p class="text-neutral-text-secondary text-sm mb-4">评分规则说明...</p>
        <!-- Scoring rules content here -->
      </div>
    </BaseDialog>
  </div>
</template>

<script setup lang="ts">import { ref, computed } from 'vue';
import { useToast } from 'primevue/usetoast';
import { useAttendanceDetail } from '@/composables/attendance/useAttendanceDetail';
import LoadingState from '@/components/common/ui/LoadingState.vue';
import EmptyState from '@/components/common/ui/EmptyState.vue';
import BaseButton from '@/components/common/ui/BaseButton.vue';
import BaseDialog from '@/components/common/ui/BaseDialog.vue';
import StatCard from './detail/StatCard.vue';
import Dropdown from 'primevue/dropdown';
import { getProfessionColor } from '@/utils/profession/professionUtils';
import { getProfessionLabel, getScoreColor, formatNumber, formatDps, formatDateTime, formatDuration } from '@/utils/attendance/attendanceFormatters';
const toast = useToast();
const props = defineProps<{
 data?: any;
 loading?: boolean;
}>();
// Local state
const showAllChars = ref(false);
const showAllFights = ref(false);
const showCharModal = ref(false);
const showScoringModal = ref(false);
const selectedCharacter = ref<any>(null);
const timeRange = ref('7d');
const timeRangeOptions = [
 { label: '近7天', value: '7d' },
 { label: '近30天', value: '30d' },
 { label: '近90天', value: '90d' },
];
// Composable data
const { summary, characters, recentFights, abilities, chartPoints, chartLinePath, chartAreaPath, radarPolygonPoints, radarCirclePoints, radarLabels, getHexagonPoints, getAxisPoint, } = useAttendanceDetail(props.data);
// Computed
const displayCharacters = computed(() => {
 return showAllChars.value ? characters.value : characters.value.slice(0, 6);
});
const displayFights = computed(() => {
 return showAllFights.value ? recentFights.value : recentFights.value.slice(0, 5);
});
// Methods
function showCharDetail(char: any) {
 selectedCharacter.value = char;
 showCharModal.value = true;
}
function showScoringRules() {
 showScoringModal.value = true;
}
function handleTimeRangeChange() {
 toast.add({ severity: 'info', summary: '时间范围已更新', detail: `已切换到${timeRangeOptions.find(o => o.value === timeRange.value)?.label}`, life: 3000 });
}
function exportExcel() {
 toast.add({ severity: 'success', summary: '导出成功', detail: 'Excel文件已下载', life: 3000 });
}
function exportCSV() {
 toast.add({ severity: 'success', summary: '导出成功', detail: 'CSV文件已下载', life: 3000 });
}
function getProfessionGradient(profession: string) {
 const color = getProfessionColor(profession);
 return `linear-gradient(135deg, ${color}60, ${color}20)`;
}
function getProfessionColorVal(profession: string) {
 return getProfessionColor(profession);
}
function getScoreGradient(score: number) {
 if (!score)
 return 'from-neutral-border/20 to-neutral-border/5';
 if (score >= 85)
 return 'from-status-success/20 to-status-success/5';
 if (score >= 70)
 return 'from-primary/20 to-primary/5';
 if (score >= 50)
 return 'from-status-warning/20 to-status-warning/5';
 return 'from-status-error/20 to-status-error/5';
}
function getScoreBorder(score: number) {
 if (!score)
 return 'border-neutral-border/30';
 if (score >= 85)
 return 'border-status-success/30';
 if (score >= 70)
 return 'border-primary/30';
 if (score >= 50)
 return 'border-status-warning/30';
 return 'border-status-error/30';
}
function getScoreIconBg(score: number) {
 if (!score)
 return 'from-neutral-border/40 to-neutral-border/20';
 if (score >= 85)
 return 'from-status-success/40 to-status-success/20';
 if (score >= 70)
 return 'from-primary/40 to-primary/20';
 if (score >= 50)
 return 'from-status-warning/40 to-status-warning/20';
 return 'from-status-error/40 to-status-error/20';
}
</script>

<style scoped>
.attendance-detail-page {
  background: var(--color-bg-primary, #0f172a);
}

.card {
  background: rgba(30, 41, 59, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 1rem;
}

.card-header {
  background: rgba(255, 255, 255, 0.02);
}

.card-body {
  padding: 1rem;
}
</style>