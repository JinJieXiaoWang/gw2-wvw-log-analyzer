<template>
  <div class="space-y-4">
    <!-- 未配置提示 -->
    <div v-if="disabled" class="text-center py-8 px-4">
      <div class="inline-flex items-center justify-center p-4 bg-yellow-500/20 rounded-xl mb-4">
        <SvgIcon icon="lock" :size="40" class="text-yellow-400 opacity-80" />
      </div>
      <p class="text-yellow-400 font-medium">请先在配置管理中完成AI配置</p>
      <p class="text-gray-500 text-sm mt-2">配置完成后即可使用智能分析功能</p>
    </div>
    
    <div v-else>
      <!-- 智能推荐提示 -->
      <div class="p-4 bg-gradient-to-r from-blue-900/30 to-purple-900/30 rounded-xl border border-blue-700/30 mb-4">
        <div class="flex items-start gap-3">
          <div class="p-2 bg-blue-500/20 rounded-lg">
            <SvgIcon icon="sparkles" :size="18" class="text-blue-400" />
          </div>
          <div>
            <p class="text-sm font-medium text-blue-300">AI智能推荐</p>
            <p class="text-xs text-gray-400 mt-1">系统会根据您的战斗数据自动推荐分析选项</p>
          </div>
        </div>
      </div>

      <!-- 快速操作按钮 -->
      <div class="space-y-4">
        <!-- 分析战斗 -->
        <div class="group bg-gray-700/40 hover:bg-gray-700/60 rounded-xl p-4 border border-gray-600/50 hover:border-red-500/30 transition-all duration-300">
          <div class="flex items-center justify-between mb-3">
            <h3 class="font-semibold text-white flex items-center gap-2">
              <div class="p-2 bg-gradient-to-br from-red-500/30 to-orange-500/30 rounded-lg">
                <SvgIcon icon="swords" :size="18" class="text-red-400" />
              </div>
              分析战斗
            </h3>
            <button 
              v-if="recentFights?.length"
              @click="autoSelectRecentFight"
              class="text-xs px-2 py-1 bg-blue-600/20 text-blue-400 rounded-lg hover:bg-blue-600/30 transition-colors flex items-center gap-1"
            >
              <SvgIcon icon="zap" :size="12" />
              自动选择最新
            </button>
          </div>
          
          <!-- 选择战斗 -->
          <div class="relative">
            <label class="block text-xs text-gray-400 mb-2">选择战斗</label>
            <div class="relative">
              <select 
                v-model="selectedFightId"
                class="w-full bg-gray-600/80 border border-gray-500 hover:border-gray-400 focus:border-red-500 focus:outline-none rounded-lg px-4 py-2.5 text-sm text-white appearance-none cursor-pointer transition-colors"
              >
                <option value="">选择战斗日志...</option>
                <option v-for="fight in recentFights" :key="fight.id" :value="fight.id">
                  {{ fight.name }}
                  <span class="text-gray-500 ml-2">({{ formatDate(fight.date) }})</span>
                </option>
              </select>
              <div class="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none">
                <SvgIcon icon="chevron-down" :size="16" class="text-gray-400" />
              </div>
            </div>
            
            <!-- 最近战斗快速选择 -->
            <div v-if="recentFights?.length" class="mt-2 flex flex-wrap gap-2">
              <button
                v-for="fight in recentFights.slice(0, 3)"
                :key="fight.id"
                @click="selectedFightId = fight.id"
                class="text-xs px-2 py-1 rounded-lg transition-colors flex items-center gap-1"
                :class="selectedFightId === fight.id ? 'bg-red-500/30 text-red-300' : 'bg-gray-600/50 text-gray-400 hover:bg-gray-600'"
              >
                <SvgIcon icon="clock" :size="12" />
                {{ fight.name.substring(0, 10) }}...
              </button>
            </div>
          </div>
          
          <button 
            @click="handleAnalyzeFight"
            class="w-full mt-4 flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-red-600 to-orange-600 hover:from-red-500 hover:to-orange-500 disabled:from-gray-600 disabled:to-gray-600 disabled:cursor-not-allowed rounded-xl transition-all duration-300 hover:shadow-lg hover:shadow-red-500/20 font-medium"
            :disabled="analyzing || !selectedFightId"
          >
            <svg v-if="analyzing" class="animate-spin h-5 w-5 text-white" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"/>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
            </svg>
            <SvgIcon v-else icon="play" :size="18" class="text-white" />
            <span class="text-white">{{ analyzing ? '分析中...' : '开始分析' }}</span>
          </button>
        </div>
        
        <!-- 分析玩家 -->
        <div class="group bg-gray-700/40 hover:bg-gray-700/60 rounded-xl p-4 border border-gray-600/50 hover:border-green-500/30 transition-all duration-300">
          <div class="flex items-center justify-between mb-3">
            <h3 class="font-semibold text-white flex items-center gap-2">
              <div class="p-2 bg-gradient-to-br from-green-500/30 to-emerald-500/30 rounded-lg">
                <SvgIcon icon="user" :size="18" class="text-green-400" />
              </div>
              分析玩家
            </h3>
            <span class="text-xs text-gray-500">支持名称或ID</span>
          </div>
          
          <div class="relative">
            <label class="block text-xs text-gray-400 mb-2">玩家名称或ID</label>
            <div class="relative">
              <input 
                v-model="localMemberId" 
                type="text" 
                class="w-full bg-gray-600/80 border border-gray-500 hover:border-gray-400 focus:border-green-500 focus:outline-none rounded-lg px-4 py-2.5 text-sm text-white placeholder-gray-500 transition-colors"
                placeholder="输入玩家名称或ID"
                :disabled="analyzing"
                @input="handleMemberInput"
              />
              <div class="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none">
                <SvgIcon icon="search" :size="16" class="text-gray-500" />
              </div>
            </div>
            
            <!-- 玩家建议列表 -->
            <div v-if="memberSuggestions.length && localMemberId.length >= 2" class="mt-2 bg-gray-700/80 rounded-lg overflow-hidden border border-gray-600/50">
              <div class="px-3 py-2 border-b border-gray-600/50">
                <span class="text-xs text-gray-400">找到 {{ memberSuggestions.length }} 个匹配结果</span>
              </div>
              <button
                v-for="member in memberSuggestions"
                :key="member.id"
                @click="selectMember(member)"
                class="w-full px-3 py-2.5 text-left hover:bg-gray-600/50 transition-colors flex items-center gap-3"
              >
                <div class="w-8 h-8 rounded-lg flex items-center justify-center" :class="getProfessionBg(member.profession)">
                  <SvgIcon icon="user" :size="14" :class="getProfessionText(member.profession)" />
                </div>
                <div class="flex-1">
                  <span class="text-sm text-gray-200">{{ member.name }}</span>
                  <span class="text-xs text-gray-500 ml-2">{{ getProfessionName(member.profession) }}</span>
                </div>
                <SvgIcon icon="chevron-right" :size="14" class="text-gray-500" />
              </button>
            </div>
            
            <!-- 快速选择热门玩家 -->
            <div v-if="recentPlayers?.length && localMemberId.length < 2" class="mt-2 flex flex-wrap gap-2">
              <button
                v-for="player in recentPlayers.slice(0, 4)"
                :key="player.id"
                @click="selectMember(player)"
                class="text-xs px-2 py-1.5 rounded-lg transition-colors flex items-center gap-1"
                :class="localMemberId === player.id ? 'bg-green-500/30 text-green-300' : 'bg-gray-600/50 text-gray-400 hover:bg-gray-600'"
              >
                <div class="w-2 h-2 rounded-full" :class="getProfessionColor(player.profession)" />
                {{ player.name.substring(0, 8) }}...
              </button>
            </div>
          </div>
          
          <button 
            @click="handleAnalyzeMember"
            class="w-full mt-4 flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 disabled:from-gray-600 disabled:to-gray-600 disabled:cursor-not-allowed rounded-xl transition-all duration-300 hover:shadow-lg hover:shadow-green-500/20 font-medium"
            :disabled="analyzing || !localMemberId"
          >
            <svg v-if="analyzing" class="animate-spin h-5 w-5 text-white" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"/>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
            </svg>
            <SvgIcon v-else icon="play" :size="18" class="text-white" />
            <span class="text-white">{{ analyzing ? '分析中...' : '开始分析' }}</span>
          </button>
        </div>
        
        <!-- 分析Build -->
        <div class="group bg-gray-700/40 hover:bg-gray-700/60 rounded-xl p-4 border border-gray-600/50 hover:border-blue-500/30 transition-all duration-300">
          <div class="flex items-center justify-between mb-3">
            <h3 class="font-semibold text-white flex items-center gap-2">
              <div class="p-2 bg-gradient-to-br from-blue-500/30 to-indigo-500/30 rounded-lg">
                <SvgIcon icon="code" :size="18" class="text-blue-400" />
              </div>
              分析Build
            </h3>
            <button 
              v-if="recentBuilds?.length"
              @click="autoSelectRecentBuild"
              class="text-xs px-2 py-1 bg-blue-600/20 text-blue-400 rounded-lg hover:bg-blue-600/30 transition-colors flex items-center gap-1"
            >
              <SvgIcon icon="zap" :size="12" />
              自动选择
            </button>
          </div>
          
          <div class="relative">
            <label class="block text-xs text-gray-400 mb-2">Build代码或ID</label>
            <div class="relative">
              <input 
                v-model="localBuildId" 
                type="text" 
                class="w-full bg-gray-600/80 border border-gray-500 hover:border-gray-400 focus:border-blue-500 focus:outline-none rounded-lg px-4 py-2.5 text-sm text-white placeholder-gray-500 transition-colors font-mono"
                placeholder="输入Build代码或ID"
                :disabled="analyzing"
              />
              <div class="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none">
                <SvgIcon icon="code" :size="16" class="text-gray-500" />
              </div>
            </div>
            
            <!-- 最近Build快速选择 -->
            <div v-if="recentBuilds?.length" class="mt-2 flex flex-wrap gap-2">
              <button
                v-for="build in recentBuilds.slice(0, 3)"
                :key="build.id"
                @click="selectBuild(build)"
                class="text-xs px-2 py-1.5 rounded-lg transition-colors flex items-center gap-1"
                :class="localBuildId === build.id ? 'bg-blue-500/30 text-blue-300' : 'bg-gray-600/50 text-gray-400 hover:bg-gray-600'"
              >
                <div class="w-2 h-2 rounded-full" :class="getProfessionColor(build.profession)" />
                {{ build.name }}
              </button>
            </div>
          </div>
          
          <button 
            @click="handleAnalyzeBuild"
            class="w-full mt-4 flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 disabled:from-gray-600 disabled:to-gray-600 disabled:cursor-not-allowed rounded-xl transition-all duration-300 hover:shadow-lg hover:shadow-blue-500/20 font-medium"
            :disabled="analyzing || !localBuildId"
          >
            <svg v-if="analyzing" class="animate-spin h-5 w-5 text-white" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"/>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
            </svg>
            <SvgIcon v-else icon="play" :size="18" class="text-white" />
            <span class="text-white">{{ analyzing ? '分析中...' : '开始分析' }}</span>
          </button>
        </div>
      </div>
      
      <!-- 智能分析模式切换 -->
      <div class="mt-4 p-4 bg-gray-700/30 rounded-xl border border-gray-600/30">
        <div class="flex items-center justify-between mb-3">
          <h4 class="text-sm font-medium text-gray-300 flex items-center gap-2">
            <SvgIcon icon="brain" :size="16" class="text-purple-400" />
            智能分析模式
          </h4>
          <button 
            @click="smartMode = !smartMode"
            class="relative w-12 h-6 rounded-full transition-colors"
            :class="smartMode ? 'bg-purple-600' : 'bg-gray-600'"
          >
            <span 
              class="absolute top-1 w-4 h-4 bg-white rounded-full transition-transform"
              :class="smartMode ? 'translate-x-7' : 'translate-x-1'"
            />
          </button>
        </div>
        <p class="text-xs text-gray-500">
          {{ smartMode ? '已开启：AI将自动关联战斗数据，提供智能推荐和自动化分析' : '已关闭：手动选择分析目标' }}
        </p>
      </div>
      
      <!-- 一键分析按钮 -->
      <button 
        @click="handleAnalyzeAll"
        class="w-full mt-4 flex items-center justify-center gap-2 px-5 py-3.5 bg-gradient-to-r from-purple-600 via-blue-600 to-cyan-600 hover:from-purple-500 hover:via-blue-500 hover:to-cyan-500 disabled:from-gray-600 disabled:via-gray-600 disabled:to-gray-600 disabled:cursor-not-allowed rounded-xl transition-all duration-300 hover:shadow-xl hover:shadow-purple-500/20 text-white font-semibold hover:scale-[1.02]"
        :disabled="analyzing"
      >
        <SvgIcon icon="zap" :size="20" />
        <span>{{ analyzing ? '全面分析中...' : '一键全面分析' }}</span>
        <SvgIcon icon="arrow-right" :size="18" />
      </button>
      
      <!-- 提示信息 -->
      <div class="mt-4 p-4 bg-gray-700/30 rounded-xl border border-gray-600/30">
        <div class="flex items-start gap-3">
          <SvgIcon icon="info" :size="16" class="text-blue-400 flex-shrink-0 mt-0.5" />
          <div>
            <p class="text-sm text-gray-300">AI分析将自动识别战斗中的关键数据，提供个性化优化建议</p>
            <p class="text-xs text-gray-500 mt-1">分析结果包括：伤害输出、技能循环、团队配合、Build优化等</p>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 错误提示 -->
    <Transition name="slide-down">
      <div v-if="errorMessage" class="mt-4 p-4 bg-red-900/40 border border-red-700/50 rounded-xl">
        <div class="flex items-center gap-3">
          <SvgIcon icon="alert-circle" :size="18" class="text-red-400 flex-shrink-0" />
          <p class="text-red-300 text-sm">{{ errorMessage }}</p>
          <button @click="clearError" class="ml-auto">
            <SvgIcon icon="x" :size="16" class="text-red-400/70 hover:text-red-300" />
          </button>
        </div>
      </div>
    </Transition>
    
    <!-- 智能关联提示 -->
    <Transition name="slide-up">
      <div 
        v-if="smartMode && smartSuggestion" 
        class="mt-4 p-4 bg-gradient-to-r from-purple-900/30 to-blue-900/30 border border-purple-700/30 rounded-xl"
      >
        <div class="flex items-start gap-3">
          <div class="p-2 bg-purple-500/20 rounded-lg">
            <SvgIcon icon="lightbulb" :size="16" class="text-purple-400" />
          </div>
          <div class="flex-1">
            <p class="text-sm font-medium text-purple-300">{{ smartSuggestion.title }}</p>
            <p class="text-xs text-gray-400 mt-1">{{ smartSuggestion.message }}</p>
            <button 
              v-if="smartSuggestion.action"
              @click="executeSmartAction"
              class="mt-2 text-xs text-purple-400 hover:text-purple-300 flex items-center gap-1 transition-colors"
            >
              <SvgIcon icon="arrow-right" :size="12" />
              {{ smartSuggestion.action }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { getProfessionName } from '@/services/professionService'
import SvgIcon from '@/components/common/ui/display/SvgIcon.vue'

interface FightOption {
  id: string
  name: string
  date: string
}

interface PlayerOption {
  id: string
  name: string
  profession: string
}

interface BuildOption {
  id: string
  name: string
  profession: string
}

interface SmartSuggestion {
  title: string
  message: string
  action?: string
  actionType?: 'fight' | 'player' | 'build'
  actionId?: string
}

// Props
const props = defineProps<{
  disabled?: boolean
  recentFights?: FightOption[]
  recentPlayers?: PlayerOption[]
  recentBuilds?: BuildOption[]
}>()

// Emits
const emit = defineEmits<{
  'analyze-fight': [fightId: string]
  'analyze-member': [memberId: string]
  'analyze-build': [buildId: string]
  'analyze-all': []
}>()

// 本地状态
const selectedFightId = ref('')
const localMemberId = ref('')
const localBuildId = ref('')
const analyzing = ref(false)
const errorMessage = ref('')
const memberSuggestions = ref<PlayerOption[]>([])
const smartMode = ref(true)
const smartSuggestion = ref<SmartSuggestion | null>(null)

// 清除错误
const clearError = () => {
  errorMessage.value = ''
}

// 格式化日期
const formatDate = (dateString: string): string => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
}

// 获取职业颜色（英文 key → Tailwind class）
const getProfessionColor = (professionKey: string): string => {
  const colors: Record<string, string> = {
    'Warrior': 'bg-red-400', 'Guardian': 'bg-blue-400', 'Ranger': 'bg-green-400',
    'Thief': 'bg-yellow-400', 'Engineer': 'bg-orange-400', 'Elementalist': 'bg-purple-400',
    'Necromancer': 'bg-gray-400', 'Mesmer': 'bg-pink-400', 'Revenant': 'bg-cyan-400',
    'Mechanist': 'bg-teal-400', 'Vindicator': 'bg-amber-400', 'Harbinger': 'bg-indigo-400',
  }
  return colors[professionKey] || 'bg-gray-400'
}

// 获取职业背景色
const getProfessionBg = (professionKey: string): string => {
  const colors: Record<string, string> = {
    'Warrior': 'bg-red-500/20', 'Guardian': 'bg-blue-500/20', 'Ranger': 'bg-green-500/20',
    'Thief': 'bg-yellow-500/20', 'Engineer': 'bg-orange-500/20', 'Elementalist': 'bg-purple-500/20',
    'Necromancer': 'bg-gray-500/20', 'Mesmer': 'bg-pink-500/20', 'Revenant': 'bg-cyan-500/20',
    'Mechanist': 'bg-teal-500/20', 'Vindicator': 'bg-amber-500/20', 'Harbinger': 'bg-indigo-500/20',
  }
  return colors[professionKey] || 'bg-gray-500/20'
}

// 获取职业文字颜色
const getProfessionText = (professionKey: string): string => {
  const colors: Record<string, string> = {
    'Warrior': 'text-red-400', 'Guardian': 'text-blue-400', 'Ranger': 'text-green-400',
    'Thief': 'text-yellow-400', 'Engineer': 'text-orange-400', 'Elementalist': 'text-purple-400',
    'Necromancer': 'text-gray-400', 'Mesmer': 'text-pink-400', 'Revenant': 'text-cyan-400',
    'Mechanist': 'text-teal-400', 'Vindicator': 'text-amber-400', 'Harbinger': 'text-indigo-400',
  }
  return colors[professionKey] || 'text-gray-400'
}

// 自动选择最近战斗
const autoSelectRecentFight = () => {
  if (props.recentFights?.length) {
    selectedFightId.value = props.recentFights[0].id
    updateSmartSuggestion()
  }
}

// 自动选择最近Build
const autoSelectRecentBuild = () => {
  if (props.recentBuilds?.length) {
    selectBuild(props.recentBuilds[0])
    updateSmartSuggestion()
  }
}

// 选择玩家
const selectMember = (member: PlayerOption) => {
  localMemberId.value = member.id
  memberSuggestions.value = []
  updateSmartSuggestion()
}

// 选择Build
const selectBuild = (build: BuildOption) => {
  localBuildId.value = build.id
  updateSmartSuggestion()
}

// 处理玩家输入
const handleMemberInput = () => {
  if (!localMemberId.value || localMemberId.value.length < 2) {
    memberSuggestions.value = []
    return
  }
  
  const query = localMemberId.value.toLowerCase()
  memberSuggestions.value = (props.recentPlayers || []).filter(p => 
    p.name.toLowerCase().includes(query) || p.profession.toLowerCase().includes(query)
  ).slice(0, 5)
}

// 更新智能建议
const updateSmartSuggestion = () => {
  if (!smartMode.value) {
    smartSuggestion.value = null
    return
  }
  
  // 根据已选择的数据生成智能建议
  if (selectedFightId.value && localMemberId.value) {
    smartSuggestion.value = {
      title: '智能分析建议',
      message: '检测到您已选择战斗和玩家，建议一起分析该玩家在这场战斗中的表现',
      action: '立即分析组合',
      actionType: 'fight',
      actionId: selectedFightId.value
    }
  } else if (selectedFightId.value) {
    smartSuggestion.value = {
      title: '智能分析建议',
      message: '系统推荐分析这场战斗中表现最佳的玩家，以获取详细的技能循环分析',
      action: '分析最佳玩家',
      actionType: 'player',
      actionId: ''
    }
  } else if (localMemberId.value) {
    smartSuggestion.value = {
      title: '智能分析建议',
      message: '建议为该玩家选择一场战斗进行深入分析',
      action: '选择战斗',
      actionType: 'fight',
      actionId: ''
    }
  } else {
    smartSuggestion.value = null
  }
}

// 执行智能建议操作
const executeSmartAction = () => {
  if (!smartSuggestion.value) return
  
  switch (smartSuggestion.value.actionType) {
    case 'fight':
      if (smartSuggestion.value.actionId) {
        handleAnalyzeFight()
      } else {
        autoSelectRecentFight()
      }
      break
    case 'player':
      if (props.recentPlayers?.length) {
        selectMember(props.recentPlayers[0])
        handleAnalyzeMember()
      }
      break
    case 'build':
      if (smartSuggestion.value.actionId) {
        localBuildId.value = smartSuggestion.value.actionId
        handleAnalyzeBuild()
      }
      break
  }
  smartSuggestion.value = null
}

// 监听最近玩家变化
watch(() => props.recentPlayers, () => {
  if (localMemberId.value && localMemberId.value.length >= 2) {
    handleMemberInput()
  }
})

// 监听智能模式切换
watch(smartMode, (newVal) => {
  if (newVal) {
    updateSmartSuggestion()
  } else {
    smartSuggestion.value = null
  }
})

// 监听选择变化
watch([selectedFightId, localMemberId, localBuildId], () => {
  if (smartMode.value) {
    updateSmartSuggestion()
  }
})

// 事件处理
const handleAnalyzeFight = () => {
  if (!selectedFightId.value) {
    errorMessage.value = '请先选择战斗日志'
    return
  }
  clearError()
  analyzing.value = true
  smartSuggestion.value = null
  emit('analyze-fight', selectedFightId.value)
}

const handleAnalyzeMember = () => {
  if (!localMemberId.value) {
    errorMessage.value = '请输入玩家名称或ID'
    return
  }
  clearError()
  analyzing.value = true
  smartSuggestion.value = null
  emit('analyze-member', localMemberId.value)
  localMemberId.value = ''
}

const handleAnalyzeBuild = () => {
  if (!localBuildId.value) {
    errorMessage.value = '请输入Build代码或ID'
    return
  }
  clearError()
  analyzing.value = true
  smartSuggestion.value = null
  emit('analyze-build', localBuildId.value)
  localBuildId.value = ''
}

const handleAnalyzeAll = () => {
  clearError()
  analyzing.value = true
  smartSuggestion.value = null
  emit('analyze-all')
}

// 外部重置分析状态
defineExpose({
  resetAnalyzing: () => {
    analyzing.value = false
  },
  triggerSmartSuggestion: () => {
    updateSmartSuggestion()
  }
})
</script>

<style scoped>
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s ease;
}

.slide-down-enter-from,
.slide-down-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.3s ease;
}

.slide-up-enter-from,
.slide-up-leave-to {
  opacity: 0;
  transform: translateY(10px);
}
</style>