<template>
  <div
    class="card bg-surface-800/50 border border-neutral-border/30 rounded-2xl
           overflow-hidden">
    <div
      class="card-header flex items-center justify-between p-4 border-b
             border-neutral-border/20">
      <div class="flex items-center gap-2">
        <i class="pi pi-users text-primary text-lg" />
        <h3 class="font-semibold text-neutral-text">
          角色统计
        </h3>
        <span class="text-xs px-2 py-0.5 rounded-full bg-primary/20 text-primary">{{ characters.length }} 个角色</span>
      </div>
      <button
        v-if="characters.length > 6"
        type="button"
          class="text-xs text-primary hover:text-primary/80 flex items-center gap-1
                 transition-colors"
        @click="showAll = !showAll"
      >
        <span>{{ showAll ? '收起' : '查看全部' }}</span>
        <i :class="['pi', showAll ? 'pi-chevron-up' : 'pi-chevron-down']" />
      </button>
    </div>
    <div class="card-body p-4">
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <div
          v-for="char in displayCharacters"
          :key="char.character_name"
            class="group p-4 rounded-xl bg-surface-700/50 border border-neutral-border/20
                   hover:border-primary/40 transition-all duration-300 cursor-pointer"
          @click="emit('select', char)"
        >
          <div class="flex items-start gap-3">
            <div
              class="w-12 h-12 rounded-xl flex items-center justify-center text-white font-bold
                     text-lg shrink-0 transition-transform duration-300 group-hover:scale-110"
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
                  <p class="font-bold text-primary">
                    {{ char.attendance_count }}天
                  </p>
                </div>
                <div>
                  <span class="text-neutral-text-secondary">DPS</span>
                  <p class="font-bold text-status-error">
                    {{ formatDps(char.avg_dps) }}
                  </p>
                </div>
                <div>
                  <span class="text-neutral-text-secondary">伤害</span>
                  <p class="font-bold text-status-error">
                    {{ formatNumber(char.total_damage) }}
                  </p>
                </div>
                <div>
                  <span class="text-neutral-text-secondary">评分</span>
                  <span
                    :class="getScoreColor(char.avg_score)"
                    class="font-bold"
                  >{{ char.avg_score }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div
        v-if="!characters.length"
        class="text-center py-8 text-neutral-text-secondary"
      >
        <i class="pi pi-users text-4xl mb-3 opacity-50" />
        <p>暂无角色数据</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { getProfessionColor } from '@/utils/profession/professionUtils'
import { getProfessionLabel, getScoreColor, formatNumber, formatDps } from '@/utils/common/attendanceFormatters'

const { characters } = defineProps<{
  characters: any[]
}>()
const emit = defineEmits(['select'])

const showAll = ref(false)
const displayCharacters = computed(() => showAll.value ? characters : characters.slice(0, 6))

function getProfessionGradient(profession: string) {
  const color = getProfessionColor(profession)
  return `linear-gradient(135deg, ${color}60, ${color}20)`
}
function getProfessionColorVal(profession: string) {
  return getProfessionColor(profession)
}
</script>
