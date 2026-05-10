<template>
  <DataTable :value="players" striped-rows :paginator="true" :rows="10" class="w-full" scrollable>
    <Column field="character_name" header="玩家" style="min-width: 140px">
      <template #body="{ data }">
        <div class="flex items-center gap-2">
          <img :src="getProfessionIconUrl(data.profession)" class="w-7 h-7 rounded-full">
          <div>
            <p class="text-sm font-medium">{{ data.character_name || data.account }}</p>
            <p v-if="data.account && data.character_name" class="text-[10px] text-neutral-text-secondary truncate">{{ data.account }}</p>
            <p class="text-[10px] text-neutral-text-secondary">{{ getProfessionName(data.profession) }}</p>
          </div>
        </div>
      </template>
    </Column>
    <Column field="breakbar_damage" header="破甲" style="min-width: 90px"><template #body="{ data }"><span class="text-sm">{{ fmtCompact(data.breakbar_damage) }}</span></template></Column>
    <Column field="flanking_rate" header="侧身率" style="min-width: 80px"><template #body="{ data }"><span class="text-sm">{{ data.flanking_rate.toFixed(1) }}%</span></template></Column>
    <Column field="glance_rate" header="擦过率" style="min-width: 80px"><template #body="{ data }"><span class="text-sm">{{ data.glance_rate.toFixed(1) }}%</span></template></Column>
    <Column field="missed" header="δ命中" style="min-width: 80px" />
    <Column field="interrupts" header="打断" style="min-width: 70px" />
    <Column field="swap_count" header="换武器" style="min-width: 80px" />
    <Column field="blocked_count" header="格挡" style="min-width: 70px" />
    <Column field="evaded_count" header="闪避" style="min-width: 70px" />
    <Column field="dodge_count" header="翻滚" style="min-width: 70px" />
    <Column field="boon_strips" header="剥增益" style="min-width: 85px" />
    <Column field="condition_cleanses" header="清֢" style="min-width: 70px" />
    <Column field="resurrects" header="复活" style="min-width: 70px" />
    <Column field="downed" header="击倒" style="min-width: 70px"><template #body="{ data }"><span class="text-sm font-semibold text-warning">{{ data.downed || 0 }}</span></template></Column>
    <Column field="stun_break" header="解控" style="min-width: 70px"><template #body="{ data }"><span class="text-sm">{{ data.stun_break || 0 }}</span></template></Column>
  </DataTable>
</template>

<script setup lang="ts">
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import { formatCompactNumber as fmtCompact } from '@/utils/core/helpers'
import { getProfessionName, getProfessionIconUrl } from '@/utils/profession/professionUtils'
import type { EiAnalysisPlayer } from '@/services/ei/eiAnalysisService'

defineProps<{
  players: EiAnalysisPlayer[]
}>()
</script>
