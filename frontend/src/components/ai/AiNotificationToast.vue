<template>
  <Transition name="slide-up">
    <div v-if="show" :class="notificationClass" class="fixed bottom-8 right-8 px-6 py-4 rounded-2xl shadow-2xl z-50 flex items-center gap-4 min-w-[280px]">
      <SvgIcon :icon="notificationIcon" :size="24" class="text-white flex-shrink-0" />
      <div>
        <p class="text-white font-medium">{{ title }}</p>
        <p class="text-white/80 text-sm">{{ message }}</p>
      </div>
      <button @click="$emit('close')" class="ml-auto">
        <SvgIcon icon="x" :size="18" class="text-white/80 hover:text-white" />
      </button>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import SvgIcon from '@/components/common/ui/display/SvgIcon.vue'
import { computed } from 'vue'

interface Props {
  show: boolean
  title: string
  message: string
  type: 'success' | 'error' | 'warning'
}

const props = defineProps<Props>()

defineEmits<{
  close: []
}>()

const notificationClass = computed(() => {
  if (props.type === 'success') return 'bg-gradient-to-r from-status-success to-emerald-600'
  if (props.type === 'warning') return 'bg-gradient-to-r from-warning to-secondary'
  return 'bg-gradient-to-r from-error to-red-600'
})

const notificationIcon = computed(() => props.type === 'success' ? 'check-circle' : props.type === 'warning' ? 'alert-circle' : 'x-circle')
</script>

<style scoped>
.slide-up-enter-active, .slide-up-leave-active { transition: all 0.3s ease; }
.slide-up-enter-from, .slide-up-leave-to { opacity: 0; transform: translateY(20px); }
</style>
