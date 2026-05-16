<template>
  <div class="squad-composition-view space-y-6">
    <!-- 指挥官列表 -->
    <div class="card">
      <h3 class="text-lg font-semibold text-neutral-text mb-4">
        <i class="pi pi-star-fill text-yellow-500 mr-2" />
        指挥官
      </h3>
      <div class="flex flex-wrap gap-3">
        <div
          v-for="cmd in commanders"
          :key="cmd.instanceID"
          class="flex items-center gap-3 px-4 py-3 rounded-lg bg-yellow-500/10 border border-yellow-500/30"
        >
          <div
            class="w-10 h-10 rounded-full flex items-center justify-center text-white font-bold"
            :style="{ backgroundColor: getProfessionColor(cmd.profession) }"
          >
            {{ cmd.name.charAt(0) }}
          </div>
          <div>
            <p class="font-medium text-neutral-text">
              {{ cmd.name }}
            </p>
            <p class="text-xs text-neutral-text-secondary">
              {{ getProfessionName(cmd.profession) }}
            </p>
          </div>
        </div>
        <div
          v-if="commanders.length === 0"
          class="text-neutral-text-secondary text-sm"
        >
          未检测到指挥官标记
        </div>
      </div>
    </div>

    <!-- 小队编制 -->
    <div class="card">
      <h3 class="text-lg font-semibold text-neutral-text mb-4">
        <i class="pi pi-sitemap text-primary mr-2" />
        小队编制
      </h3>
      <div class="space-y-4">
        <div
          v-for="group in groups"
          :key="group.id"
          class="rounded-lg border-2 p-3"
          :style="{ borderColor: getGroupColor(group.id), backgroundColor: getGroupColor(group.id) + '10' }"
        >
          <!-- 小队标题 -->
          <div
            class="flex items-center justify-between mb-3 pb-2 border-b"
            :style="{ borderColor: getGroupColor(group.id) + '40' }"
          >
            <div class="flex items-center gap-2">
              <span
                class="w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold text-white"
                :style="{ backgroundColor: getGroupColor(group.id) }"
              >
                {{ group.id }}
              </span>
              <span class="font-semibold text-neutral-text">小队 {{ group.id }}</span>
            </div>
            <span
              class="text-xs px-2 py-0.5 rounded-full font-medium"
              :style="{ backgroundColor: getGroupColor(group.id) + '30', color: getGroupColor(group.id) }"
            >
              {{ group.players.length }}人
            </span>
          </div>
          <!-- 小队成员 — 横着排，一排5人 -->
          <div class="grid grid-cols-5 gap-2">
            <div
              v-for="player in group.players"
              :key="player.instanceID"
              class="flex flex-col items-center gap-1 p-2 rounded cursor-pointer transition-colors"
              :class="player.hasCommanderTag ? 'bg-yellow-500/10 hover:bg-yellow-500/20' : 'bg-white/5 hover:bg-white/10'"
              @click="$emit('select-player', player.instanceID)"
            >
              <div
                class="w-10 h-10 rounded-full flex items-center justify-center text-white text-sm font-bold"
                :style="{ backgroundColor: getProfessionColor(player.profession) }"
              >
                {{ player.name.charAt(0) }}
              </div>
              <div class="text-center w-full">
                <div class="flex items-center justify-center gap-0.5">
                  <span class="text-xs text-neutral-text truncate max-w-[80px]">{{ player.name }}</span>
                  <i
                    v-if="player.hasCommanderTag"
                    class="pi pi-star-fill text-yellow-500 text-[10px]"
                    title="指挥官"
                  />
                </div>
                <span class="text-[10px] text-neutral-text-secondary">{{ getProfessionName(player.profession) }}</span>
              </div>
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
import { getProfessionName } from '@/services/professionService';

const props = defineProps<{
  players: any[];
}>();

defineEmits(['select-player']);

interface GroupData {
  id: number | string;
  players: any[];
}

const groups = computed<GroupData[]>(() => {
  const maxGroup = 10;
  const result: GroupData[] = [];
  for (let i = 1; i <= maxGroup; i++) {
    const groupPlayers = props.players.filter(p => (p.group || 0) === i);
    if (groupPlayers.length > 0) {
      result.push({ id: i, players: groupPlayers });
    }
  }
  // 未分组玩家
  const ungrouped = props.players.filter(p => !p.group || p.group === 0);
  if (ungrouped.length > 0) {
    result.push({ id: '-', players: ungrouped });
  }
  return result;
});

const commanders = computed(() => props.players.filter(p => p.hasCommanderTag));

function getGroupColor(id: number | string): string {
  const colors: Record<string, string> = {
    '1': '#ef4444', '2': '#f97316', '3': '#eab308', '4': '#84cc16',
    '5': '#22c55e', '6': '#06b6d4', '7': '#3b82f6', '8': '#8b5cf6',
    '9': '#d946ef', '10': '#f43f5e', '-': '#6b7280',
  };
  return colors[String(id)] || '#6b7280';
}
</script>
