<template>
  <transition name="fade">
    <div
      v-if="visible"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm"
    >
      <div class="text-center">
        <div class="relative w-32 h-32 mx-auto mb-6">
          <svg
            class="w-full h-full -rotate-90"
            viewBox="0 0 100 100"
          >
            <circle
              cx="50"
              cy="50"
              r="45"
              fill="none"
              stroke="rgba(59, 130, 246, 0.2)"
              stroke-width="8"
            />
            <circle
              cx="50"
              cy="50"
              r="45"
              fill="none"
              stroke="url(#gradient)"
              stroke-width="8"
              stroke-linecap="round"
              :stroke-dasharray="283"
              :stroke-dashoffset="283 - (283 * progress) / 100"
              class="transition-all duration-300"
            />
            <defs>
              <linearGradient
                id="gradient"
                x1="0%"
                y1="0%"
                x2="100%"
                y2="100%"
              >
                <stop
                  offset="0%"
                  stop-color="#3B82F6"
                />
                <stop
                  offset="100%"
                  stop-color="#8B5CF6"
                />
              </linearGradient>
            </defs>
          </svg>
          <div class="absolute inset-0 flex items-center justify-center">
            <i
              v-if="isLoading"
              class="pi pi-spin pi-spinner text-blue-400 text-3xl"
            />
            <i
              v-else
              class="pi pi-check text-green-400 text-4xl"
            />
          </div>
        </div>
        <p class="text-white text-lg font-medium">
          {{ isLoading ? '正在验证身份...' : '验证完成' }}
        </p>
        <p class="text-gray-400 text-sm mt-2">
          {{ progress }}%
        </p>
      </div>
    </div>
  </transition>
</template>

<script setup lang="ts">
defineProps<{
  visible: boolean
  isLoading: boolean
  progress: number
}>()
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
