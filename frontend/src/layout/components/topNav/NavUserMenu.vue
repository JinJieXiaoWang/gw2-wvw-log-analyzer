<template>
  <div class="relative">
    <button class="flex items-center gap-2 p-1.5 pr-3 hover:bg-neutral-bg rounded-xl transition-all hover:scale-[1.02] user-menu-trigger" @click="showUserMenu = !showUserMenu">
      <div class="relative">
        <div class="w-10 h-10 bg-gradient-to-br from-primary to-secondary rounded-xl flex items-center justify-center shadow-md shadow-primary/20 overflow-hidden ring-2 ring-primary/20">
          <span class="text-white font-bold text-base">{{ userInitial }}</span>
        </div>
        <div class="absolute -bottom-0.5 -right-0.5 w-3.5 h-3.5 bg-status-success rounded-full border-2 border-neutral-card" />
      </div>
      <div class="hidden sm:block text-left">
        <p class="text-base font-semibold text-neutral-text leading-tight">{{ isAuthenticated ? (user?.username || '操作Ա') : '游客' }}</p>
        <div class="flex items-center gap-1">
          <span :class="isAuthenticated ? 'text-primary' : 'text-neutral-text-disabled'" class="text-sm">{{ isAuthenticated ? '操作Ա' : '浏览ģʽ' }}</span>
        </div>
      </div>
      <i class="pi pi-chevron-down text-sm text-neutral-text-disabled hidden sm:block" />
    </button>
    <transition name="dropdown" appear>
      <div v-if="showUserMenu" class="user-dropdown absolute top-full mt-2 right-0 w-64 bg-neutral-card border border-neutral-border rounded-xl shadow-2xl shadow-neutral-shadow/50 overflow-hidden z-50">
        <div v-if="isAuthenticated">
          <div class="px-4 py-3 border-b border-neutral-border bg-gradient-to-r from-primary/5 to-secondary/5">
            <div class="flex items-center gap-3">
              <div class="w-12 h-12 bg-gradient-to-br from-primary to-secondary rounded-xl flex items-center justify-center shadow-lg">
                <span class="text-white font-bold text-lg">{{ userInitial }}</span>
              </div>
              <div>
                <p class="text-base font-bold text-neutral-text">{{ user?.username }}</p>
                <p class="text-sm text-neutral-text-secondary">ϵͳ操作员</p>
              </div>
            </div>
          </div>
          <div class="p-2">
            <router-link v-if="canWrite" to="/settings" class="flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-neutral-bg transition-colors group" @click="showUserMenu = false">
              <div class="w-8 h-8 bg-primary/10 rounded-lg flex items-center justify-center group-hover:bg-primary/20 transition-colors">
                <i class="pi pi-cog text-primary text-base" />
              </div>
              <div>
                <p class="text-base font-medium text-neutral-text">ϵͳ设置</p>
                <p class="text-sm text-neutral-text-disabled">配置管理</p>
              </div>
            </router-link>
          </div>
          <div class="px-4 py-3 border-t border-neutral-border bg-neutral-bg/50">
            <button class="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-gradient-to-r from-status-error/10 to-status-error/5 hover:from-status-error/20 hover:to-status-error/10 text-status-error rounded-lg transition-all group logout-btn" @click="$emit('logout')">
              <i class="pi pi-sign-out group-hover:translate-x-0.5 transition-transform" />
              <span class="text-base font-medium">退出登¼</span>
            </button>
          </div>
        </div>
        <div v-else>
          <div class="px-4 py-6 text-center border-b border-neutral-border">
            <div class="w-16 h-16 bg-neutral-bg rounded-full flex items-center justify-center mx-auto mb-3">
              <i class="pi pi-user text-3xl text-neutral-text-disabled" />
            </div>
            <p class="text-base text-neutral-text-secondary mb-4">登录后可上传日志和管理ϵͳ</p>
            <router-link to="/login" class="inline-flex items-center gap-2 px-6 py-2.5 bg-gradient-to-r from-primary to-secondary text-white rounded-lg hover:opacity-90 transition-opacity shadow-lg shadow-primary/30" @click="showUserMenu = false">
              <i class="pi pi-sign-in" />
              <span class="text-base font-medium">操作员登¼</span>
            </router-link>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { authStore, usePermission } from '@/composables/system/usePermission'

const { can } = usePermission()
const showUserMenu = ref(false)

const isAuthenticated = computed(() => authStore.isAuthenticated)
const user = computed(() => authStore.currentUser)
const userInitial = computed(() => user.value?.username?.charAt(0).toUpperCase() || 'A')
const canWrite = computed(() => can('write'))

defineEmits<{
  logout: []
}>()
</script>
