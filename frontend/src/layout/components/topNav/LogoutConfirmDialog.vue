<template>
  <transition name="fade">
    <div v-if="visible" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm" @click.self="$emit('cancel')">
      <div class="bg-neutral-card border border-neutral-border rounded-2xl p-6 w-full max-w-md mx-4 animate-scale-in">
        <div class="text-center">
          <div class="w-16 h-16 bg-status-warning/10 rounded-full flex items-center justify-center mx-auto mb-4">
            <i class="pi pi-sign-out text-status-warning text-3xl" />
          </div>
          <h3 class="text-xl font-bold text-neutral-text mb-2">ȷ认退出登录</h3>
          <p class="text-neutral-text-secondary mb-6">ȷ定要退出当前账号吗？退出后将以游客身份浏览ϵͳ。</p>
          <div class="flex gap-3">
            <button class="flex-1 px-4 py-3 bg-neutral-bg hover:bg-neutral-bg/80 text-neutral-text rounded-xl transition-all font-medium" @click="$emit('cancel')">ȡ消</button>
            <button class="flex-1 px-4 py-3 bg-gradient-to-r from-status-error to-status-error/80 hover:from-status-error/90 hover:to-status-error/70 text-white rounded-xl transition-all font-medium flex items-center justify-center gap-2 logout-confirm-btn" :disabled="isLoggingOut" @click="$emit('confirm')">
              <svg v-if="isLoggingOut" class="animate-spin h-5 w-5" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none" />
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              <span>{{ isLoggingOut ? '退出中...' : 'ȷ认退出' }}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup lang="ts">
defineProps<{
  visible: boolean
  isLoggingOut: boolean
}>()

defineEmits<{
  confirm: []
  cancel: []
}>()
</script>
