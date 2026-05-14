<template>
  <div>
    <div class="flex items-center gap-3 mb-6">
      <div class="p-2 bg-gradient-to-br from-primary/20 to-indigo-500/20 rounded-xl"><SvgIcon icon="wrench" :size="24" class="text-primary" /></div>
      <h2 class="text-xl font-bold text-white">分析工具</h2>
    </div>
    <div class="space-y-4">
      <div>
        <label class="text-sm text-neutral-text-tertiary mb-2 block">选择战斗</label>
        <select v-model="selectedFight" class="w-full bg-neutral-card-active text-white text-sm px-4 py-2 rounded-lg border border-neutral-border">
          <option value="">请选择战斗</option>
          <option v-for="fight in recentFights" :key="fight.id" :value="fight.id">{{ fight.name }}</option>
        </select>
      </div>
      <div>
        <label class="text-sm text-neutral-text-tertiary mb-2 block">选择玩家</label>
        <select v-model="selectedPlayer" class="w-full bg-neutral-card-active text-white text-sm px-4 py-2 rounded-lg border border-neutral-border">
          <option value="">请选择玩家</option>
          <option v-for="player in recentPlayers" :key="player.id" :value="player.id">{{ player.name }} - {{ player.profession }}</option>
        </select>
      </div>
      <div>
        <label class="text-sm text-neutral-text-tertiary mb-2 block">选择Build</label>
        <select v-model="selectedBuild" class="w-full bg-neutral-card-active text-white text-sm px-4 py-2 rounded-lg border border-neutral-border">
          <option value="">请选择Build</option>
          <option v-for="build in recentBuilds" :key="build.id" :value="build.id">{{ build.name }} - {{ build.profession }}</option>
        </select>
      </div>
      <div class="flex items-center gap-2 pt-2">
        <input type="checkbox" v-model="useCurrentScope" id="scope-current" class="w-4 h-4 rounded border-neutral-border text-primary focus:ring-primary" />
        <label for="scope-current" class="text-sm text-neutral-text-secondary">基于当前选中数据（精准分析）</label>
      </div>
      <button @click="handleAnalyze" :disabled="disabled || !canAnalyze" class="w-full px-5 py-3 bg-gradient-to-r from-primary to-indigo-600 hover:from-primary-light hover:to-indigo-500 disabled:from-neutral-card disabled:to-neutral-card disabled:cursor-not-allowed text-white rounded-xl transition-all font-medium">
        {{ analyzingText }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface FightOption { id: string; name: string }
interface PlayerOption { id: string; name: string; profession: string }
interface BuildOption { id: string; name: string; profession: string }

const props = defineProps<{ recentFights: FightOption[]; recentPlayers: PlayerOption[]; recentBuilds: BuildOption[]; disabled: boolean }>()
const emit = defineEmits<{ analyze: [type: string, id: string] }>()

const selectedFight = ref('')
const selectedPlayer = ref('')
const selectedBuild = ref('')
const useCurrentScope = ref(true)

const canAnalyze = computed(() => selectedFight.value || selectedPlayer.value || selectedBuild.value)
const analyzingText = computed(() => {
  if (!canAnalyze.value) return '请选择分析目标'
  if (selectedFight.value) return '分析战斗'
  if (selectedPlayer.value) return '分析玩家'
  return '分析Build'
})

const handleAnalyze = () => {
  if (selectedFight.value) emit('analyze', 'fight', selectedFight.value)
  else if (selectedPlayer.value) emit('analyze', 'member', selectedPlayer.value)
  else if (selectedBuild.value) emit('analyze', 'build', selectedBuild.value)
}
</script>
