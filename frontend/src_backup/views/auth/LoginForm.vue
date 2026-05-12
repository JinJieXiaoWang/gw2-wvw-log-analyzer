<template>
  <form
    class="space-y-5 sm:space-y-6"
    @submit.prevent="emit('submit')"
  >
    <div>
      <label class="block text-gray-300 text-sm font-medium mb-2 sm:mb-3">用户名</label>
      <input
        v-model="form.username"
        type="text"
        placeholder="请输入用户名"
        class="w-full px-4 py-3 sm:px-5 sm:py-3.5 lg:px-6 lg:py-4 bg-slate-700/50 border rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all text-base sm:text-lg"
        :class="errors.username ? 'border-red-500' : 'border-slate-600'"
        :disabled="loading"
        @blur="emit('validateUsername')"
        @input="emit('clearError', 'username')"
      >
      <div
        v-if="errors.username"
        class="mt-2 sm:mt-3"
      >
        <span class="text-red-400 text-sm sm:text-base">{{ errors.username }}</span>
      </div>
      <div
        v-else-if="form.username"
        class="mt-2 sm:mt-3"
      >
        <span class="text-green-400 text-xs sm:text-sm">✓ 用户名格式正确</span>
      </div>
    </div>

    <div>
      <label class="block text-gray-300 text-sm font-medium mb-2 sm:mb-3">密码</label>
      <input
        v-model="form.password"
        type="password"
        placeholder="请输入密码"
        class="w-full px-4 py-3 sm:px-5 sm:py-3.5 lg:px-6 lg:py-4 bg-slate-700/50 border rounded-xl text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all text-base sm:text-lg"
        :class="errors.password ? 'border-red-500' : 'border-slate-600'"
        :disabled="loading"
        @blur="emit('validatePassword')"
        @input="emit('clearError', 'password')"
      >
      <div
        v-if="errors.password"
        class="mt-2 sm:mt-3"
      >
        <span class="text-red-400 text-sm sm:text-base">{{ errors.password }}</span>
      </div>
      <div
        v-else-if="form.password"
        class="mt-2 sm:mt-3"
      >
        <span class="text-green-400 text-xs sm:text-sm">✓ 密码格式正确</span>
      </div>
    </div>

    <div
      v-if="remainingAttempts > 0"
      class="flex items-center gap-2 text-gray-500 text-xs sm:text-sm"
    >
      <i class="pi pi-shield text-blue-400" />
      <span>剩余登录尝试次数: <span class="text-blue-400 font-medium">{{ remainingAttempts }}</span> / 5</span>
    </div>

    <button
      type="submit"
      :disabled="loading || !isValid"
      class="w-full py-3 sm:py-4 px-6 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-500 hover:to-blue-600 disabled:from-slate-600 disabled:to-slate-600 disabled:cursor-not-allowed text-white font-semibold rounded-xl transition-all duration-200 flex items-center justify-center gap-2 text-base sm:text-lg shadow-lg shadow-blue-500/25 hover:shadow-blue-500/40"
    >
      <svg
        v-if="loading"
        class="animate-spin h-5 w-5 sm:h-6 sm:w-6"
        viewBox="0 0 24 24"
      >
        <circle
          class="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          stroke-width="4"
          fill="none"
        />
        <path
          class="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        />
      </svg>
      <span>{{ loading ? '登录中...' : '登 录' }}</span>
    </button>
  </form>
</template>

<script setup lang="ts">
const { form, errors, loading, isValid, remainingAttempts } = defineProps<{
  form: { username: string; password: string }
  errors: { username?: string; password?: string }
  loading: boolean
  isValid: boolean
  remainingAttempts: number
}>()

const emit = defineEmits(['submit', 'validateUsername', 'validatePassword', 'clearError'])
</script>
