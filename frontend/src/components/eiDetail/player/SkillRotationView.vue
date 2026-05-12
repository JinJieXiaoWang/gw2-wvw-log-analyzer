<template>
  <div class="skill-rotation-view space-y-6">
    <!-- 技能释放统计 -->
    <div class="card">
      <h3 class="text-lg font-semibold text-neutral-text mb-4">
        <i class="pi pi-list text-primary mr-2" />
        技能释放统计
      </h3>
      <div class="space-y-4">
        <div
          v-for="player in playersWithData"
          :key="player.instanceID"
          class="p-4 rounded-lg bg-neutral-bg/50"
        >
          <!-- 玩家信息 + 武器配置 -->
          <div class="flex items-center gap-3 mb-3">
            <div
              class="w-10 h-10 rounded-full flex items-center justify-center text-white
                     font-bold shrink-0"
              :style="{ backgroundColor: getProfessionColor(player.profession) }"
            >
              {{ player.name.charAt(0) }}
            </div>
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2">
                <span class="font-medium text-neutral-text">{{ player.name }}</span>
                <span class="text-xs text-neutral-text-secondary">{{ player.profession }}</span>
              </div>
              <!-- 武器配置 -->
              <div
                v-if="player.weapons && player.weapons.length > 0"
                class="flex items-center gap-1 mt-1"
              >
                <span class="text-xs text-neutral-text-secondary">武器:</span>
                <span class="text-xs text-primary font-medium">{{ formatWeapons(player.weapons) }}</span>
              </div>
            </div>
          </div>

          <!-- 技能循环时间线 -->
          <div class="flex items-center gap-2">
            <span class="text-xs text-neutral-text-secondary shrink-0">技能:</span>
            <div class="flex-1 flex flex-wrap gap-1">
              <template v-if="player.rotation && player.rotation.length > 0">
                <div
                  v-for="(cast, idx) in deduplicatedRotation(player.rotation)"
                  :key="idx"
                  class="h-6 px-1.5 rounded text-xs flex items-center justify-center text-white"
                  :style="{ backgroundColor: getSkillColor(cast.skillId) }"
                  :title="`Skill ${cast.skillId} @ ${cast.time}s`"
                >
                  {{ cast.skillId % 1000 }}
                </div>
              </template>
              <span
                v-else
                class="text-xs text-neutral-text-secondary"
              >无技能循环数据</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { getProfessionColor } from '@/utils/profession/professionUtils';
import { Colors } from '@/config/designTokens'

const props = defineProps<{
  players: any[];
}>();

const playersWithData = computed(() => {
  return props.players.filter(p => (p.rotation && p.rotation.length > 0) || (p.weapons && p.weapons.length > 0));
});

interface RotationCast {
  time: number;
  skillId: number;
}

function deduplicatedRotation(rotation: any[]): RotationCast[] {
  const result: RotationCast[] = [];
  let lastTime = -1;
  for (const cast of rotation) {
    const time = Math.round((cast[0] || 0) * 10) / 10; // 保留1位小数
    const skillId = cast[1] || 0;
    // 同一时间只保留一个技能（取第一个）
    if (time !== lastTime) {
      lastTime = time;
      result.push({ time, skillId });
    }
  }
  return result;
}

function formatWeapons(weapons: string[]): string {
  // weapons format: [main1, off1, main2, off2]
  if (!weapons || weapons.length === 0) return '未配置';
  const set1 = weapons.slice(0, 2).filter(w => w).join('+') || '-';
  const set2 = weapons.slice(2, 4).filter(w => w).join('+') || '-';
  return `${set1} / ${set2}`;
}

function getSkillColor(skillId: number): string {
  const colors = [Colors.palette.red, Colors.palette.orange, Colors.palette.amber, Colors.palette.lime, Colors.palette.emerald, Colors.palette.cyan, Colors.palette.blue, Colors.palette.violet, Colors.palette.fuchsia, Colors.palette.crimson];
  return colors[Math.abs(skillId) % colors.length];
}
</script>
