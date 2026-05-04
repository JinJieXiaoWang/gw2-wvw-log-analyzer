<template>
  <div class="space-y-6">
    <!-- 页面标题 -->
    <div>
      <h1 class="text-2xl font-bold text-neutral-text mb-1">
        管理员后台
      </h1>
      <p class="text-neutral-text-secondary text-sm">
        系统配置和账号管理
      </p>
    </div>

    <!-- 配置内容 -->
    <div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
      <!-- 侧边导航 -->
      <div class="lg:col-span-1">
        <div class="card">
          <div class="space-y-1">
            <button
              v-for="section in adminSections"
              :key="section.id"
              class="w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-colors text-left"
              :class="activeSection === section.id ? 'bg-primary text-white' : 'text-neutral-text-secondary hover:bg-neutral-bg'"
              @click="activeSection = section.id"
            >
              <i :class="section.icon" />
              <span class="text-sm">{{ section.label }}</span>
            </button>
          </div>
        </div>
      </div>

      <!-- 配置详情 -->
      <div class="lg:col-span-3">
        <!-- 账号管理 -->
        <div
          v-if="activeSection === 'account'"
          class="card"
        >
          <div class="flex items-center justify-between mb-6">
            <div>
              <h3 class="text-lg font-semibold text-neutral-text mb-1">
                账号管理
              </h3>
              <p class="text-sm text-neutral-text-secondary">
                修改管理员登录凭据
              </p>
            </div>
          </div>

          <div class="space-y-4 max-w-2xl">
            <div>
              <label class="block text-sm text-neutral-text-secondary mb-2">当前用户名</label>
              <InputText
                v-model="accountForm.username"
                placeholder="请输入用户名"
                class="w-full"
              />
              <small class="text-neutral-text-disabled text-xs">用户名长度至少3个字符</small>
            </div>

            <div>
              <label class="block text-sm text-neutral-text-secondary mb-2">新密码</label>
              <Password
                v-model="accountForm.newPassword"
                placeholder="请输入新密码（留空则不修改）"
                toggle-mask
                class="w-full"
                input-class="w-full"
              />
            </div>

            <div>
              <label class="block text-sm text-neutral-text-secondary mb-2">确认新密码</label>
              <Password
                v-model="accountForm.confirmPassword"
                placeholder="请再次输入新密码"
                toggle-mask
                class="w-full"
                input-class="w-full"
              />
            </div>

            <!-- 密码要求 -->
            <div class="p-4 bg-neutral-bg rounded-lg">
              <h4 class="text-sm font-medium text-neutral-text mb-3">
                密码要求
              </h4>
              <div class="space-y-2">
                <div class="flex items-center gap-2 text-sm">
                  <i
                    class="pi"
                    :class="passwordValidation.hasMinLength ? 'pi-check text-status-success' : 'pi-times text-status-error'"
                  />
                  <span :class="passwordValidation.hasMinLength ? 'text-status-success' : 'text-status-error'">
                    至少8个字符
                  </span>
                </div>
                <div class="flex items-center gap-2 text-sm">
                  <i
                    class="pi"
                    :class="passwordValidation.hasUppercase ? 'pi-check text-status-success' : 'pi-times text-status-error'"
                  />
                  <span :class="passwordValidation.hasUppercase ? 'text-status-success' : 'text-status-error'">
                    包含大写字母
                  </span>
                </div>
                <div class="flex items-center gap-2 text-sm">
                  <i
                    class="pi"
                    :class="passwordValidation.hasLowercase ? 'pi-check text-status-success' : 'pi-times text-status-error'"
                  />
                  <span :class="passwordValidation.hasLowercase ? 'text-status-success' : 'text-status-error'">
                    包含小写字母
                  </span>
                </div>
                <div class="flex items-center gap-2 text-sm">
                  <i
                    class="pi"
                    :class="passwordValidation.hasNumber ? 'pi-check text-status-success' : 'pi-times text-status-error'"
                  />
                  <span :class="passwordValidation.hasNumber ? 'text-status-success' : 'text-status-error'">
                    包含数字
                  </span>
                </div>
                <div class="flex items-center gap-2 text-sm">
                  <i
                    class="pi"
                    :class="passwordValidation.hasSpecialChar ? 'pi-check text-status-success' : 'pi-times text-status-error'"
                  />
                  <span :class="passwordValidation.hasSpecialChar ? 'text-status-success' : 'text-status-error'">
                    包含特殊字符
                  </span>
                </div>
              </div>
            </div>

            <div
              v-if="accountErrors"
              class="p-3 bg-status-error/10 border border-status-error/30 rounded-lg"
            >
              <div class="flex items-center gap-2 text-status-error text-sm">
                <i class="pi pi-exclamation-circle" />
                <span>{{ accountErrors }}</span>
              </div>
            </div>

            <div class="flex gap-3 pt-4">
              <Button
                label="保存修改"
                icon="pi pi-save"
                :loading="isSaving"
                @click="saveAccount"
              />
              <Button
                label="重置"
                severity="secondary"
                icon="pi pi-refresh"
                @click="resetAccountForm"
              />
            </div>
          </div>
        </div>

        <!-- 安全设置 -->
        <div
          v-if="activeSection === 'security'"
          class="card"
        >
          <div class="mb-6">
            <h3 class="text-lg font-semibold text-neutral-text mb-1">
              安全设置
            </h3>
            <p class="text-sm text-neutral-text-secondary">
              配置登录安全策略
            </p>
          </div>

          <div class="space-y-6 max-w-2xl">
            <div class="flex items-center justify-between p-4 bg-neutral-bg rounded-lg">
              <div>
                <h4 class="text-sm font-medium text-neutral-text mb-1">
                  登录失败锁定
                </h4>
                <p class="text-xs text-neutral-text-secondary">
                  连续5次登录失败后锁定账号15分钟
                </p>
              </div>
              <span class="px-3 py-1 bg-status-success/10 text-status-success text-sm rounded-full">
                已启用
              </span>
            </div>

            <div class="flex items-center justify-between p-4 bg-neutral-bg rounded-lg">
              <div>
                <h4 class="text-sm font-medium text-neutral-text mb-1">
                  密码加密存储
                </h4>
                <p class="text-xs text-neutral-text-secondary">
                  使用强哈希算法加密存储密码
                </p>
              </div>
              <span class="px-3 py-1 bg-status-success/10 text-status-success text-sm rounded-full">
                已启用
              </span>
            </div>

            <div class="flex items-center justify-between p-4 bg-neutral-bg rounded-lg">
              <div>
                <h4 class="text-sm font-medium text-neutral-text mb-1">
                  会话超时
                </h4>
                <p class="text-xs text-neutral-text-secondary">
                  设置登录状态保持时间
                </p>
              </div>
              <Dropdown
                v-model="sessionTimeout"
                :options="sessionTimeoutOptions"
                option-label="label"
                option-value="value"
                class="w-40"
              />
            </div>
          </div>
        </div>

        <!-- 系统信息 -->
        <div
          v-if="activeSection === 'system'"
          class="card"
        >
          <div class="mb-6">
            <h3 class="text-lg font-semibold text-neutral-text mb-1">
              系统信息
            </h3>
            <p class="text-sm text-neutral-text-secondary">
              查看系统运行状态
            </p>
          </div>

          <div class="space-y-4">
            <div class="p-4 bg-neutral-bg rounded-lg">
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <p class="text-xs text-neutral-text-secondary mb-1">
                    系统版本
                  </p>
                  <p class="text-sm text-neutral-text font-medium">
                    v1.0.0
                  </p>
                </div>
                <div>
                  <p class="text-xs text-neutral-text-secondary mb-1">
                    构建日期
                  </p>
                  <p class="text-sm text-neutral-text font-medium">
                    2024-01-15
                  </p>
                </div>
                <div>
                  <p class="text-xs text-neutral-text-secondary mb-1">
                    运行环境
                  </p>
                  <p class="text-sm text-neutral-text font-medium">
                    Vue 3.4 + Vite 5.2
                  </p>
                </div>
                <div>
                  <p class="text-xs text-neutral-text-secondary mb-1">
                    最后登录
                  </p>
                  <p class="text-sm text-neutral-text font-medium">
                    {{ lastLoginTime }}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Dropdown from 'primevue/dropdown'
import Button from 'primevue/button'
import { authStore } from '@/composables/system/usePermission'

const toast = useToast()

const activeSection = ref('account')
const isSaving = ref(false)
const accountErrors = ref('')

const adminSections = [
  { id: 'account', label: '账号管理', icon: 'pi pi-user' },
  { id: 'security', label: '安全设置', icon: 'pi pi-shield' },
  { id: 'system', label: '系统信息', icon: 'pi pi-info-circle' }
]

const sessionTimeoutOptions = [
  { label: '30分钟', value: 30 },
  { label: '1小时', value: 60 },
  { label: '6小时', value: 360 },
  { label: '24小时', value: 1440 }
]

const sessionTimeout = ref(60)

const accountForm = reactive({
  username: '',
  newPassword: '',
  confirmPassword: ''
})

const passwordValidation = computed(() => {
  const password = accountForm.newPassword || ''
  return {
    hasMinLength: password.length >= 8,
    hasUppercase: /[A-Z]/.test(password),
    hasLowercase: /[a-z]/.test(password),
    hasNumber: /[0-9]/.test(password),
    hasSpecialChar: /[!@#$%^&*()_+\-=[\]{};':"\\|,.<>/?]/.test(password)
  }
})

const lastLoginTime = computed(() => {
  const user = authStore.currentUser
  if (user?.loginTime) {
    return new Date(user.loginTime).toLocaleString('zh-CN')
  }
  return '未知'
})

const saveAccount = async () => {
  accountErrors.value = ''

  if (!accountForm.username || accountForm.username.length < 3) {
    accountErrors.value = '用户名长度至少3个字符'
    return
  }

  if (accountForm.newPassword) {
    const validation = authStore.validatePassword(accountForm.newPassword)
    if (!validation.valid) {
      accountErrors.value = validation.errors.join('；')
      return
    }

    if (accountForm.newPassword !== accountForm.confirmPassword) {
      accountErrors.value = '两次输入的密码不一致'
      return
    }
  }

  isSaving.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 500))

    if (accountForm.newPassword) {
      const result = authStore.setAdminConfig(accountForm.username, accountForm.newPassword)
      if (!result.success) {
        accountErrors.value = result.message
        return
      }
    } else {
      const currentConfig = authStore.getAdminConfig()
      localStorage.setItem('gw2_wvw_admin_config', JSON.stringify({
        username: accountForm.username,
        password: currentConfig.password
      }))
    }

    toast.add({
      severity: 'success',
      summary: '保存成功',
      detail: '管理员账号配置已更新',
      life: 3000
    })

    accountForm.newPassword = ''
    accountForm.confirmPassword = ''
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: '保存失败',
      detail: '发生错误，请稍后重试',
      life: 3000
    })
  } finally {
    isSaving.value = false
  }
}

const resetAccountForm = () => {
  const config = authStore.getAdminConfig()
  accountForm.username = config.username
  accountForm.newPassword = ''
  accountForm.confirmPassword = ''
  accountErrors.value = ''
}

onMounted(() => {
  if (!authStore.isAuthenticated || (authStore.currentRole !== 'super_admin' && authStore.currentRole !== 'operator')) {
    return
  }
  resetAccountForm()
})
</script>
