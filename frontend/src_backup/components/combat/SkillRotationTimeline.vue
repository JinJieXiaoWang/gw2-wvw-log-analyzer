<template>
  <div class="skill-rotation-timeline">
    <RotationViewModeBar
      v-model:view-mode="viewMode"
      v-model:show-auto-attacks="showAutoAttacks"
      v-model:show-instant-cast="showInstantCast"
    />
    <SimpleRotationView
      v-if="viewMode === 'simple'"
      :cycles="simpleCycles"
      :format-time="formatTime"
      :format-duration="formatDuration"
    />
    <AdvancedRotationView
      v-else
      :skill-rows="advancedSkillRows"
      :time-ticks="advancedTimeTicks"
      :content-style="advancedContentStyle"
      :scroll-left="advancedScrollLeft"
      :format-time="formatTime"
      @scroll="handleAdvancedScroll"
    />
    <RotationTimelineLegend />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useSkillRotationTimeline, type RotationEvent } from '@/composables/combat/useSkillRotationTimeline'
import RotationViewModeBar from './rotation/RotationViewModeBar.vue'
import SimpleRotationView from './rotation/SimpleRotationView.vue'
import AdvancedRotationView from './rotation/AdvancedRotationView.vue'
import RotationTimelineLegend from './rotation/RotationTimelineLegend.vue'

const props = defineProps<{
  events: RotationEvent[]
  fightDuration?: number
}>()

const {
  viewMode, showAutoAttacks, showInstantCast,
  advancedScrollLeft, advancedContentStyle,
  simpleCycles, advancedSkillRows, advancedTimeTicks,
  formatTime, formatDuration, handleAdvancedScroll
} = useSkillRotationTimeline(props)

onMounted(() => {
  // scrollLeft initialized in composable ref
})
</script>

<style scoped src="@/styles/components/combat/SkillRotationTimeline.css"></style>
