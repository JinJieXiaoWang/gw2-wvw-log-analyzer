<template>
  <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
    <div
      v-for="role in roles"
      :key="role.type"
      class="relative rounded-xl p-5 cursor-pointer transition-all duration-300 overflow-hidden border"
      :class="activeRole === role.type ? 'border-primary-500 shadow-lg shadow-primary-500/20 -translate-y-1' : 'border-surface-200 dark:border-surface-700 hover:border-primary-300 hover:-translate-y-1 hover:shadow-xl'"
      :style="{ '--accent': colors[role.type] }"
      @click="emit('switch', role.type)"
    >
      <div
        class="absolute top-0 left-0 right-0 h-[3px] transition-opacity duration-300"
        :class="activeRole === role.type ? 'opacity-100' : 'opacity-0'"
        :style="{ background: colors[role.type] }"
      />
      <div
        class="absolute -top-1/2 -left-1/2 w-[200%] h-[200%] rounded-full pointer-events-none transition-opacity duration-500"
        :class="activeRole === role.type ? 'opacity-[0.05]' : 'opacity-0'"
        :style="{ background: `radial-gradient(circle, ${colors[role.type]} 0%, transparent 70%)` }"
      />
      <div class="relative z-10 flex flex-col gap-3">
        <div class="flex items-center gap-4">
          <div
            class="w-14 h-14 rounded-lg flex items-center justify-center text-2xl text-white shrink-0 shadow-lg"
            :style="{ background: `linear-gradient(135deg, ${colors[role.type]}, ${gradients[role.type]})`, boxShadow: `0 8px 24px -8px ${colors[role.type]}` }"
          >
            <i :class="role.icon" />
          </div>
          <div class="flex-1 min-w-0">
            <h3 class="text-xl font-semibold text-color">
              {{ role.label }}
            </h3>
            <p class="text-sm text-color-secondary">
              {{ role.description }}
            </p>
          </div>
        </div>
        <div class="flex items-center justify-between mt-1">
          <span class="text-xs text-color-secondary px-2 py-1 rounded-full bg-surface-100 dark:bg-surface-800">{{ ruleCounts[role.type] || 0 }} 维度</span>
          <Tag
            v-if="unsavedRoles.has(role.type)"
            value="待保存"
            severity="warning"
            class="text-xs"
          />
        </div>
      </div>
      <div class="absolute bottom-0 left-0 right-0 h-1 bg-surface-200 dark:bg-surface-700">
        <div
          class="h-full transition-all duration-300"
          :style="{ width: `${progress[role.type] || 0}%`, background: colors[role.type] }"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import Tag from 'primevue/tag'

const { roles, activeRole, colors, gradients, ruleCounts, unsavedRoles, progress } = defineProps<{
  roles: { type: string; label: string; description: string; icon: string; color: string }[]
  activeRole: string
  colors: Record<string, string>
  gradients: Record<string, string>
  ruleCounts: Record<string, number>
  unsavedRoles: Set<string>
  progress: Record<string, number>
}>()
const emit = defineEmits(['switch'])
</script>
