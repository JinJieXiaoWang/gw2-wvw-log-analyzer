<template>
  <div class="space-y-4">
    <AiAnalysisDisabled v-if="disabled" />

    <template v-else>
      <AiAnalysisHeader />

      <div class="space-y-4">
        <AiAnalysisFight
          v-model="selectedFightId"
          :recent-fights="recentFights"
          :disabled="analyzing"
          @analyze="handleAnalyzeFight"
        />
        <AiAnalysisPlayer
          v-model="localMemberId"
          :recent-players="recentPlayers"
          :disabled="analyzing"
          @analyze="handleAnalyzeMember"
        />
        <AiAnalysisBuild
          v-model="localBuildId"
          :recent-builds="recentBuilds"
          :disabled="analyzing"
          @analyze="handleAnalyzeBuild"
        />
      </div>

      <AiAnalysisSmartPanel
        v-model:smart-mode="smartMode"
        :analyzing="analyzing"
        :error-message="errorMessage"
        :smart-suggestion="smartSuggestion"
        @analyze-all="handleAnalyzeAll"
        @clear-error="clearError"
        @execute-smart-action="executeSmartAction"
      />
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import AiAnalysisDisabled from './AiAnalysisDisabled.vue'
import AiAnalysisHeader from './AiAnalysisHeader.vue'
import AiAnalysisFight from './AiAnalysisFight.vue'
import AiAnalysisPlayer from './AiAnalysisPlayer.vue'
import AiAnalysisBuild from './AiAnalysisBuild.vue'
import AiAnalysisSmartPanel from './AiAnalysisSmartPanel.vue'
import {
  TOOLS_ERROR_SELECT_FIGHT,
  TOOLS_ERROR_ENTER_PLAYER,
  TOOLS_ERROR_ENTER_BUILD,
  SMART_SUGGESTION_TITLE,
  SMART_SUGGESTION_COMBO_MSG,
  SMART_SUGGESTION_COMBO_ACTION,
  SMART_SUGGESTION_FIGHT_MSG,
  SMART_SUGGESTION_FIGHT_ACTION,
  SMART_SUGGESTION_PLAYER_MSG,
  SMART_SUGGESTION_PLAYER_ACTION,
} from '@/constants/aiAnalysis'

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

const props = defineProps<{
  disabled?: boolean
  recentFights?: FightOption[]
  recentPlayers?: PlayerOption[]
  recentBuilds?: BuildOption[]
}>()

const emit = defineEmits<{
  'analyze-fight': [fightId: string]
  'analyze-member': [memberId: string]
  'analyze-build': [buildId: string]
  'analyze-all': []
}>()

const selectedFightId = ref('')
const localMemberId = ref('')
const localBuildId = ref('')
const analyzing = ref(false)
const errorMessage = ref('')
const smartMode = ref(true)
const smartSuggestion = ref<SmartSuggestion | null>(null)

const clearError = () => {
  errorMessage.value = ''
}

const updateSmartSuggestion = () => {
  if (!smartMode.value) {
    smartSuggestion.value = null
    return
  }

  if (selectedFightId.value && localMemberId.value) {
    smartSuggestion.value = {
      title: SMART_SUGGESTION_TITLE,
      message: SMART_SUGGESTION_COMBO_MSG,
      action: SMART_SUGGESTION_COMBO_ACTION,
      actionType: 'fight',
      actionId: selectedFightId.value,
    }
  } else if (selectedFightId.value) {
    smartSuggestion.value = {
      title: SMART_SUGGESTION_TITLE,
      message: SMART_SUGGESTION_FIGHT_MSG,
      action: SMART_SUGGESTION_FIGHT_ACTION,
      actionType: 'player',
      actionId: '',
    }
  } else if (localMemberId.value) {
    smartSuggestion.value = {
      title: SMART_SUGGESTION_TITLE,
      message: SMART_SUGGESTION_PLAYER_MSG,
      action: SMART_SUGGESTION_PLAYER_ACTION,
      actionType: 'fight',
      actionId: '',
    }
  } else {
    smartSuggestion.value = null
  }
}

const executeSmartAction = () => {
  if (!smartSuggestion.value) return

  switch (smartSuggestion.value.actionType) {
    case 'fight':
      if (smartSuggestion.value.actionId) {
        handleAnalyzeFight()
      } else if (props.recentFights?.length) {
        selectedFightId.value = props.recentFights[0].id
        handleAnalyzeFight()
      }
      break
    case 'player':
      if (props.recentPlayers?.length) {
        localMemberId.value = props.recentPlayers[0].id
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

watch(smartMode, (newVal) => {
  if (newVal) {
    updateSmartSuggestion()
  } else {
    smartSuggestion.value = null
  }
})

watch([selectedFightId, localMemberId, localBuildId], () => {
  if (smartMode.value) {
    updateSmartSuggestion()
  }
})

const handleAnalyzeFight = () => {
  if (!selectedFightId.value) {
    errorMessage.value = TOOLS_ERROR_SELECT_FIGHT
    return
  }
  clearError()
  analyzing.value = true
  smartSuggestion.value = null
  emit('analyze-fight', selectedFightId.value)
}

const handleAnalyzeMember = () => {
  if (!localMemberId.value) {
    errorMessage.value = TOOLS_ERROR_ENTER_PLAYER
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
    errorMessage.value = TOOLS_ERROR_ENTER_BUILD
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

defineExpose({
  resetAnalyzing: () => {
    analyzing.value = false
  },
  triggerSmartSuggestion: () => {
    updateSmartSuggestion()
  },
})
</script>
