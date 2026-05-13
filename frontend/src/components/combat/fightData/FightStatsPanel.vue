<template>
  <div
    v-if="stats"
    class="bg-gray-800 rounded-lg p-4"
  >
    <h2 class="text-xl font-semibold mb-4">
      战斗统计数据
    </h2>
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      <div class="bg-gray-700 rounded p-3 text-center">
        <p class="text-sm text-gray-400">
          总伤害
        </p>
        <p class="text-lg font-semibold">
          {{ stats.totalDamage.toLocaleString() }}
        </p>
      </div>
      <div class="bg-gray-700 rounded p-3 text-center">
        <p class="text-sm text-gray-400">
          总承伤
        </p>
        <p class="text-lg font-semibold">
          {{ stats.totalDamageTaken.toLocaleString() }}
        </p>
      </div>
      <div class="bg-gray-700 rounded p-3 text-center">
        <p class="text-sm text-gray-400">
          总击杀
        </p>
        <p class="text-lg font-semibold">
          {{ stats.totalKills }}
        </p>
      </div>
      <div class="bg-gray-700 rounded p-3 text-center">
        <p class="text-sm text-gray-400">
          总死亡
        </p>
        <p class="text-lg font-semibold">
          {{ stats.totalDeaths }}
        </p>
      </div>
    </div>

    <h3 class="font-medium mb-2">
      玩家统计
    </h3>
    <div class="overflow-x-auto">
      <table class="w-full">
        <thead>
          <tr class="border-b border-gray-700">
            <th class="text-left py-3 px-4">
              玩家
            </th>
            <th class="text-left py-3 px-4">
              职业
            </th>
            <th class="text-left py-3 px-4">
              伤害
            </th>
            <th class="text-left py-3 px-4">
              承伤
            </th>
            <th class="text-left py-3 px-4">
              击杀
            </th>
            <th class="text-left py-3 px-4">
              死亡
            </th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(p, i) in stats.playerStats"
            :key="i"
            class="border-b border-gray-700 hover:bg-gray-700 transition-colors"
          >
            <td class="py-3 px-4">
              {{ p.accountName }}
            </td>
            <td class="py-3 px-4">
              {{ p.profession }}
            </td>
            <td class="py-3 px-4">
              {{ p.damage.toLocaleString() }}
            </td>
            <td class="py-3 px-4">
              {{ p.damageTaken.toLocaleString() }}
            </td>
            <td class="py-3 px-4">
              {{ p.kills }}
            </td>
            <td class="py-3 px-4">
              {{ p.deaths }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { FightStats } from '@/services/combat/fightsService';

defineProps<{
  stats: FightStats | null
}>()
</script>
