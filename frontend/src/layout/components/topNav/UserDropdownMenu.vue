<template>
  <transition
    name="dropdown"
    appear
  >
    <div
      v-if="visible"
      class="user-dropdown absolute top-full mt-2 right-0 w-64 bg-neutral-card border border-neutral-border rounded-xl shadow-2xl shadow-neutral-shadow/50 overflow-hidden z-50"
    >
      <div v-if="isAuthenticated">
        <div class="px-4 py-3 border-b border-neutral-border bg-gradient-to-r from-primary/5 to-secondary/5">
          <div class="flex items-center gap-3">
            <div class="w-12 h-12 bg-gradient-to-br from-primary to-secondary rounded-xl flex items-center justify-center shadow-lg">
              <span class="text-white font-bold text-lg">{{ userInitial }}</span>
            </div>
            <div>
              <p class="text-base font-bold text-neutral-text">
                {{ user?.username }}
              </p>
              <p class="text-sm text-neutral-text-secondary">
                系统操作员
              </p>
            </div>
          </div>
        </div>
        <div class="p-2">
          <router-link
            v-if="canWrite"
            to="/settings"
            class="flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-neutral-bg transition-colors group"
            @click="emit('close')"
          >
            <div class="w-8 h-8 bg-primary/10 rounded-lg flex items-center justify-center group-hover:bg-primary/20 transition-colors">
              <i class="pi pi-cog text-primary text-base" />
            </div>
            <div>
              <p class="text-base font-medium text-neutral-text">
                系统设置
              </p>
              <p class="text-sm text-neutral-text-disabled">
                配置管理
              </p>
            </div>
          </router-link>
        </div>
        <div class="px-4 py-3 border-t border-neutral-border bg-neutral-bg/50">
          <button
            class="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-gradient-to-r from-status-error/10 to-status-error/5 hover:from-status-error/20 hover:to-status-error/10 text-status-error rounded-lg transition-all group logout-btn"
            @click="emit('logout')"
          >
            <i class="pi pi-sign-out group-hover:translate-x-0.5 transition-transform" />
            <span class="text-base font-medium">退出登录</span>
          </button>
        </div>
      </div>
      <div v-else>
        <div class="px-4 py-6 text-center border-b border-neutral-border">
          <div class="w-16 h-16 bg-neutral-bg rounded-full flex items-center justify-center mx-auto mb-3">
            <i class="pi pi-user text-3xl text-neutral-text-disabled" />
          </div>
          <p class="text-base text-neutral-text-secondary mb-4">
            登录后可上传日志和管理系统
          </p>
          <router-link
            to="/login"
            class="inline-flex items-center gap-2 px-6 py-2.5 bg-gradient-to-r from-primary to-secondary text-white rounded-lg hover:opacity-90 transition-opacity shadow-lg shadow-primary/30"
            @click="emit('close')"
          >
            <i class="pi pi-sign-in" />
            <span class="text-base font-medium">操作员登录</span>
          </router-link>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup lang="ts">
const { visible, isAuthenticated, user, userInitial, canWrite } = defineProps<{
  visible: boolean
  isAuthenticated: boolean
  user: any
  userInitial: string
  canWrite: boolean
}>()

const emit = defineEmits(['close', 'logout'])
</script>

<style scoped>@import './topNav.css';</style>
