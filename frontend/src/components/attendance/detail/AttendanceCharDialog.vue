<template>
  <BaseDialog
    v-if="character"
    :visible="visible"
    :header="character.character_name"
    style-class="w-full max-w-2xl"
    @update:visible="visible = $event"
  >
    <div class="p-4">
      <div class="grid grid-cols-2 gap-6">
        <div>
          <h4 class="font-semibold text-neutral-text mb-3">
            角色信息
          </h4>
          <div class="space-y-3">
            <div class="flex justify-between">
              <span class="text-neutral-text-secondary text-sm">职业</span>
              <!-- 动态值，无法使用 Tailwind 静态类 -->
              <span
                :style="{ color: getProfessionColorVal(character.profession) }"
                class="font-medium"
              >{{ getProfessionLabel(character.profession) }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-neutral-text-secondary text-sm">出勤天数</span>
              <span class="font-medium text-primary">{{ character.attendance_count }} 天</span>
            </div>
            <div class="flex justify-between">
              <span class="text-neutral-text-secondary text-sm">总伤害</span>
              <span class="font-medium text-status-error">{{ formatNumber(character.total_damage) }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-neutral-text-secondary text-sm">平均DPS</span>
              <span class="font-medium text-status-error">{{ formatDps(character.avg_dps) }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-neutral-text-secondary text-sm">平均评分</span>
              <span
                :class="getScoreColor(character.avg_score)"
                class="font-bold"
              >{{ character.avg_score }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-neutral-text-secondary text-sm">K/D</span>
              <span
                :class="character.kd_ratio >= 2 ? 'text-status-success' : character.kd_ratio >= 1 ? 'text-primary' : 'text-status-error'"
                class="font-medium"
              >{{ character.kd_ratio }}</span>
            </div>
          </div>
        </div>
        <div>
          <h4 class="font-semibold text-neutral-text mb-3">
            角色战斗记录
          </h4>
          <div class="space-y-2">
            <div
              v-for="(fight, index) in fights"
              :key="index"
              class="p-2 rounded-lg bg-surface-700/50"
            >
              <div class="flex justify-between text-sm">
                <span class="text-neutral-text-secondary">{{ formatDateTime(fight.fight_date) }}</span>
                <span class="text-status-error font-medium">{{ formatNumber(fight.damage) }}</span>
              </div>
            </div>
            <div
              v-if="!fights.length"
              class="text-center py-4 text-neutral-text-secondary text-sm"
            >
              暂无战斗记录
            </div>
          </div>
        </div>
      </div>
    </div>
  </BaseDialog>
</template>

<script setup lang="ts">
import BaseDialog from '@/components/common/ui/feedback/BaseDialog.vue'
import { getProfessionColor } from '@/utils/profession/professionUtils'
import { getProfessionLabel, getScoreColor, formatNumber, formatDps, formatDateTime } from '@/utils/common/attendanceFormatters'

const { character, fights } = defineProps<{
  character: any
  fights: any[]
}>()

const visible = defineModel<boolean>('visible', { default: false })

function getProfessionColorVal(profession: string) {
  return getProfessionColor(profession)
}
</script>
