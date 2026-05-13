<template>
  <div class="space-y-6">
    <PageHeader
      title="职业管理"
      subtitle="管理游戏中所有的职业、精英特长和角色定位数据"
      icon="pi pi-users"
      icon-gradient="bg-gradient-to-br from-primary to-secondary"
    />

    <div class="card p-0 overflow-hidden">
      <TabMenu
        v-model:active-index="activeTabIndex"
        :model="tabItems"
      />

      <div class="p-5">
        <div
          v-if="loading"
          class="flex items-center justify-center py-16"
        >
          <ProgressSpinner style="width: 40px; height: 40px" />
          <span class="ml-3 text-neutral-text-secondary text-sm">加载数据中...</span>
        </div>

        <ProfessionListPanel
          v-else-if="activeTabIndex === 0"
          :professions="professions"
          :can-edit="canEdit"
          :get-role-name="getRoleName"
          @refresh="loadData"
          @edit="openEdit"
        />

        <EliteSpecListPanel
          v-else-if="activeTabIndex === 1"
          :elite-specs="eliteSpecs"
          :can-edit="canEdit"
          :get-role-name="getRoleName"
          :get-profession-name="getProfessionName"
          @refresh="loadData"
          @edit="openEdit"
        />

        <RoleTypeListPanel
          v-else-if="activeTabIndex === 2"
          :role-types="roleTypes"
          @refresh="loadData"
        />
      </div>
    </div>

    <div
      v-if="statistics"
      class="card p-5"
    >
      <div class="flex flex-wrap items-center gap-6">
        <div
          v-for="s in statList"
          :key="s.key"
          class="flex items-center gap-3"
        >
          <div
            class="p-2 rounded-lg"
            :class="s.bgClass"
          >
            <i :class="s.icon + ' ' + s.iconColor" />
          </div>
          <div>
            <p class="text-2xl font-bold text-neutral-text">
              {{ statistics[s.key] }}
            </p>
            <p class="text-xs text-neutral-text-secondary">
              {{ s.label }}
            </p>
          </div>
        </div>
      </div>
    </div>

    <ProfessionEditDialog
      v-model:visible="editVisible"
      :title="editTitle"
      :form="editForm"
      :role-options="roleTypeOptions"
      :loading="saving"
      @save="saveEdit"
    />
  </div>
</template>

<script setup lang="ts">
import EliteSpecListPanel from '@/components/profession/EliteSpecListPanel.vue'
import ProfessionEditDialog from '@/components/profession/ProfessionEditDialog.vue'
import ProfessionListPanel from '@/components/profession/ProfessionListPanel.vue'
import RoleTypeListPanel from '@/components/profession/RoleTypeListPanel.vue'
import { usePermission } from '@/composables/system/usePermission'
import PageHeader from '@/layout/components/PageHeader.vue'
import ProgressSpinner from 'primevue/progressspinner'
import TabMenu from 'primevue/tabmenu'
import { useToast } from 'primevue/usetoast'
import { computed, onMounted, ref } from 'vue'

const toast = useToast()
const { can } = usePermission()
const canEdit = computed(() => can('write'))

const activeTabIndex = ref(0)
const loading = ref(false)
const professions = ref<any[]>([])
const eliteSpecs = ref<any[]>([])
const roleTypes = ref<any[]>([])
const statistics = ref<any>(null)

const tabItems = [
  { label: '职业管理', icon: 'pi pi-sitemap' },
  { label: '精英特长', icon: 'pi pi-star' },
  { label: '角色定位', icon: 'pi pi-bullseye' },
]

const statList = [
  { key: 'professions_count', label: '职业', icon: 'pi pi-sitemap', bgClass: 'bg-primary/10', iconColor: 'text-primary' },
  { key: 'elite_specs_count', label: '精英特长', icon: 'pi pi-star', bgClass: 'bg-secondary/10', iconColor: 'text-secondary' },
  { key: 'role_types_count', label: '角色定位', icon: 'pi pi-bullseye', bgClass: 'bg-ai/10', iconColor: 'text-ai' },
]

const loadData = async () => {
  loading.value = true
  try {
    const [profRes, specsRes, rolesRes, statsRes] = await Promise.all([
      fetch('/api/v1/professions?include_specs=true'),
      fetch('/api/v1/professions/elite-specs'),
      fetch('/api/v1/professions/role-types'),
      fetch('/api/v1/professions/statistics'),
    ])
    const [profData, specsData, rolesData, statsData] = await Promise.all([
      profRes.json(), specsRes.json(), rolesRes.json(), statsRes.json(),
    ])
    professions.value = profData.data?.professions || []
    eliteSpecs.value = specsData.data?.elite_specs || []
    roleTypes.value = rolesData.data || []
    statistics.value = statsData.data
  } catch (error) {
    console.error('加载数据失败:', error)
  } finally {
    loading.value = false
  }
}

const getRoleName = (roleKey: string) => {
  const role = roleTypes.value.find(r => r.role_key === roleKey)
  return role?.role_name || roleKey
}

const getProfessionName = (profKey: string) => {
  const prof = professions.value.find(p => p.profession_key === profKey)
  return prof?.profession_name || profKey
}

const editVisible = ref(false)
const editType = ref<'profession' | 'spec'>('profession')
const editForm = ref<any>(null)
const saving = ref(false)

const editTitle = computed(() => editType.value === 'profession' ? '编辑职业' : '编辑精英特长')
const roleTypeOptions = computed(() => roleTypes.value.map(r => ({ label: r.role_name, value: r.role_key })))

const openEdit = (type: 'profession' | 'spec', item: any) => {
  editType.value = type
  editForm.value = {
    key: type === 'profession' ? item.profession_key : item.spec_key,
    default_role: item.default_role,
    is_active: !!item.is_active,
  }
  editVisible.value = true
}

const saveEdit = async () => {
  if (!editForm.value) return
  saving.value = true
  try {
    const endpoint = editType.value === 'profession'
      ? `/api/v1/professions/profession/${editForm.value.key}/role?role_key=${editForm.value.default_role}`
      : `/api/v1/professions/elite-spec/${editForm.value.key}/role?role_key=${editForm.value.default_role}`
    const res = await fetch(endpoint, { method: 'PUT' })
    const data = await res.json()
    if (data.success) {
      toast.add({ severity: 'success', summary: '保存成功', life: 3000 })
      editVisible.value = false
      loadData()
    } else {
      toast.add({ severity: 'error', summary: '保存失败', detail: data.message, life: 3000 })
    }
  } catch (e) {
    toast.add({ severity: 'error', summary: '保存失败', detail: String(e), life: 3000 })
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>
