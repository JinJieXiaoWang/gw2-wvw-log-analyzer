<template>
  <transition
    name="mobile-menu"
    appear
  >
    <div
      v-if="visible"
      class="fixed inset-0 bg-neutral-bg/95 backdrop-blur-md z-40 lg:hidden pt-20 px-4"
      @click="$emit('close')"
    >
      <div
        class="bg-neutral-card border border-neutral-border rounded-2xl p-4 space-y-2"
        @click.stop
      >
        <router-link
          v-for="item in menuItems"
          :key="item.path"
          :to="item.path"
          class="mobile-nav-item flex items-center gap-3 px-4 py-3 rounded-xl transition-all"
          :class="{ 'mobile-nav-item-active': isActive(item.path) }"
          @click="$emit('close')"
        >
          <div
            class="w-10 h-10 rounded-xl flex items-center justify-center"
            :class="isActive(item.path) ? 'bg-gradient-to-br from-primary to-secondary text-white' : 'bg-neutral-bg text-neutral-text-secondary'"
          >
            <i :class="item.icon" />
          </div>
          <div class="flex-1">
            <span
              class="text-lg font-semibold"
              :class="isActive(item.path) ? 'text-primary' : 'text-neutral-text'"
            >{{ item.label }}</span>
            <p class="text-sm text-neutral-text-disabled">
              {{ item.description }}
            </p>
          </div>
          <i
            v-if="isActive(item.path)"
            class="pi pi-check-circle text-primary text-xl"
          />
        </router-link>
      </div>
    </div>
  </transition>
</template>

<script setup lang="ts">
import type { MenuItem } from '@/composables/core/useTopNav'

defineProps<{
  visible: boolean
  menuItems: MenuItem[]
  isActive: (path: string) => boolean
}>()

defineEmits<{
  close: []
}>()
</script>
