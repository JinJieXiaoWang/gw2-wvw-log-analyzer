<template>
  <form
    class="space-y-5"
    @submit.prevent="emit('submit')"
  >
    <div>
      <label
        for="username"
        class="block text-sm font-medium text-gray-300 mb-2"
      >
        用户名
      </label>
      <div class="relative">
        <span class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
          <i class="pi pi-user text-gray-400" />
        </span>
        <input
          id="username"
          v-model="username"
          type="text"
          :disabled="submitStatus.loading"
          class="w-full pl-12 pr-4 py-3 bg-slate-700/50 border border-slate-600 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
          :class="{ 'border-red-500 bg-red-900/20': formState.errors.username }"
          placeholder="请输入用户名"
          @blur="emit('validate-username')"
          @input="emit('clear-error', 'username'); updateForm()"
        >
      </div>
      <p
        v-if="formState.errors.username"
        class="mt-2 text-sm text-red-400"
      >
        {{ formState.errors.username }}
      </p>
    </div>

    <div>
      <label
        for="password"
        class="block text-sm font-medium text-gray-300 mb-2"
      >
        密码
      </label>
      <div class="relative">
        <span class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
          <i class="pi pi-lock text-gray-400" />
        </span>
        <input
          id="password"
          v-model="password"
          :type="showPassword ? 'text' : 'password'"
          :disabled="submitStatus.loading"
          class="w-full pl-12 pr-12 py-3 bg-slate-700/50 border border-slate-600 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
          :class="{ 'border-red-500 bg-red-900/20': formState.errors.password }"
          placeholder="请输入密码"
          @blur="emit('validate-password')"
          @input="emit('clear-error', 'password'); updateForm()"
        >
        <button
          type="button"
          class="absolute inset-y-0 right-0 pr-4 flex items-center text-gray-400 hover:text-white transition-colors"
          @click="showPassword = !showPassword"
        >
          <i :class="showPassword ? 'pi pi-eye' : 'pi pi-eye-slash'" />
        </button>
      </div>
      <p
        v-if="formState.errors.password"
        class="mt-2 text-sm text-red-400"
      >
        {{ formState.errors.password }}
      </p>
    </div>

    <!-- <div class="flex items-center justify-between">
      <div class="flex items-center">
        <input
          id="remember-me"
          type="checkbox"
          class="w-4 h-4 rounded border-slate-600 bg-slate-700 text-blue-600 focus:ring-blue-500"
        />
        <label for="remember-me" class="ml-2 block text-sm text-gray-400">
          记住我
        </label>
      </div>
      <a href="#" class="text-sm text-blue-400 hover:text-blue-300 transition-colors">
        忘记密码？
      </a>
    </div> -->

    <button
      type="submit"
      :disabled="submitStatus.loading || !submitStatus.isValid"
      class="w-full py-3 px-4 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-500 hover:to-blue-600 disabled:from-slate-600 disabled:to-slate-700 disabled:cursor-not-allowed text-white font-medium rounded-xl shadow-lg shadow-blue-500/25 transition-all flex items-center justify-center gap-2"
    >
      <i
        v-if="submitStatus.loading"
        class="pi pi-spin pi-spinner"
      />
      <span>{{ submitStatus.loading ? '登录中...' : '登录' }}</span>
    </button>

    <div
      v-if="submitStatus.remainingAttempts > 0"
      class="text-center text-sm text-gray-500"
    >
      剩余登录尝试次数: {{ submitStatus.remainingAttempts }}
    </div>
  </form>
</template>

<script setup lang="ts">
import { ref } from 'vue';

/** 表单状态（含数据和验证错误） */
interface FormState {
  /** 用户名和密码 */
  form: { username: string; password: string }
  /** 字段级验证错误 */
  errors: { username?: string; password?: string }
}

/** 提交状态 */
interface SubmitStatus {
  /** 是否正在提交 */
  loading: boolean
  /** 表单是否有效 */
  isValid: boolean
  /** 剩余登录尝试次数 */
  remainingAttempts: number
}

const props = defineProps<{
  formState: FormState
  submitStatus: SubmitStatus
}>()

const emit = defineEmits<{
  submit: []
  'validate-username': []
  'validate-password': []
  'clear-error': [field: string]
  'update:form': [form: { username: string; password: string }]
}>()

const showPassword = ref(false)
const username = ref(props.formState.form.username)
const password = ref(props.formState.form.password)

function updateForm() {
  emit('update:form', { username: username.value, password: password.value })
}
</script>
