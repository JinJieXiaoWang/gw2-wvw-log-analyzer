<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-2xl font-bold text-neutral-text mb-1">
        管理员后台
      </h1>
      <p class="text-neutral-text-secondary text-sm">
        系统配置和账号管理
      </p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
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

      <div class="lg:col-span-3">
        <AdminAccountPanel
          v-if="activeSection === 'account'"
          ref="accountPanelRef"
        />
        <AdminSecurityPanel v-if="activeSection === 'security'" />
        <AdminSystemInfoPanel v-if="activeSection === 'system'" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { authStore } from '@/composables/system/usePermission'
import AdminAccountPanel from '@/components/admin/AdminAccountPanel.vue'
import AdminSecurityPanel from '@/components/admin/AdminSecurityPanel.vue'
import AdminSystemInfoPanel from '@/components/admin/AdminSystemInfoPanel.vue'

const activeSection = ref('account')
const accountPanelRef = ref<InstanceType<typeof AdminAccountPanel> | null>(null)

const adminSections = [
  { id: 'account', label: '账号管理', icon: 'pi pi-user' },
  { id: 'security', label: '安全设置', icon: 'pi pi-shield' },
  { id: 'system', label: '系统信息', icon: 'pi pi-info-circle' }
]

onMounted(() => {
  if (!authStore.isAuthenticated || (authStore.currentRole !== 'super_admin' && authStore.currentRole !== 'operator')) {
    return
  }
  accountPanelRef.value?.reset()
})
</script>
