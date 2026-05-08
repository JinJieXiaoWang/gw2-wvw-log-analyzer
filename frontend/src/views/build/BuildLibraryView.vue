<template>
  <div class="min-h-screen pb-10">
    <PageHeader
      title="配置图书馆"
      subtitle="格林特职业学院战场配置百科"
      icon="pi pi-book"
      icon-gradient="bg-gradient-to-br from-primary to-secondary"
    />

    <div class="flex items-center justify-end gap-3 mt-4 mb-2" v-permission="'write'">
      <Button icon="pi pi-plus" label="新增配置" severity="primary" @click="openCreateDialog" />
    </div>

    <div class="flex gap-8 mt-6">
      <!-- 左侧筛选栏 -->
      <aside class="w-80 flex-shrink-0 hidden lg:block">
        <div class="sticky top-20">
          <BuildFilterSidebar
            :professions="professions"
            :professions-dict="professionsDict"
            :active-profession="filters.profession"
            :active-role="filters.role"
            :active-sub-roles="filters.subRoles"
            :search-query="filters.searchQuery"
            :sort-by="filters.sortBy"
            :role-counts="roleCounts"
            :sub-role-counts="subRoleCounts"
            :profession-counts="professionCounts"
            @select-profession="store.setFilter('profession', $event)"
            @select-role="store.setFilter('role', $event)"
            @toggle-sub-role="toggleSubRole"
            @update-search="store.setFilter('searchQuery', $event)"
            @update-sort="store.setFilter('sortBy', $event as 'updated' | 'profession' | 'name')"
            @clear-filters="clearFilters"
          />
        </div>
      </aside>

      <!-- 移动端筛选 -->
      <div class="lg:hidden w-full mb-4">
        <Button icon="pi pi-filter" label="筛选" severity="secondary" outlined @click="showMobileFilter = true" />
      </div>

      <!-- 主内容区 -->
      <main class="flex-1 min-w-0">
        <!-- 批量操作栏 -->
        <div v-if="selectedBuildIds.length > 0" class="flex items-center gap-4 mb-4 p-3 rounded-xl bg-primary/5 border border-primary/20">
          <span class="text-sm text-surface-400">已选择 {{ selectedBuildIds.length }} 个配置</span>
          <Button icon="pi pi-trash" label="批量删除" severity="danger" size="small" @click="batchDelete" />
          <Button icon="pi pi-times" label="取消选择" severity="secondary" outlined size="small" @click="selectedBuildIds = []" />
        </div>

        <div class="flex items-center justify-between mb-4">
          <p class="text-base text-surface-400">
            共 <span class="text-surface-0 font-bold text-lg">{{ filteredBuilds.length }}</span> 个配置
          </p>
          <div v-if="filteredBuilds.length > 0" class="flex items-center gap-2">
            <Checkbox v-model="selectAllCheckbox" @click="toggleSelectAll" />
            <span class="text-sm text-surface-400">全选</span>
          </div>
        </div>

        <div v-if="filteredBuilds.length > 0" class="grid grid-cols-1 md:grid-cols-2 gap-5">
          <div v-for="build in filteredBuilds" :key="build.id" class="relative">
            <div class="absolute top-3 left-3 z-10">
              <Checkbox 
                :model-value="selectedBuildIds.includes(build.id)" 
                @click="toggleSelectBuild(build.id)"
                class="bg-surface-900"
              />
            </div>
            <BuildCard
              :build="build"
              @select="openDetail"
              @edit="openEditDialogFromCard"
              @copy-code="copyBuildCode"
            />
          </div>
        </div>

        <div v-else class="text-center py-20 rounded-xl border border-surface-700">
          <i class="pi pi-inbox text-5xl text-surface-500 mb-4" />
          <h3 class="text-lg font-semibold mb-2">未找到匹配的配置</h3>
          <p class="text-base text-surface-400 mb-4">尝试调整筛选条件或搜索关键词</p>
          <Button label="清除筛选" icon="pi pi-filter-slash" severity="secondary" outlined @click="clearFilters" />
        </div>
      </main>
    </div>

    <!-- 详情抽屉 -->
    <Drawer
      v-model:visible="drawerVisible"
      position="right"
      :modal="true"
      :dismissable="true"
      :pt="{ root: { style: { width: '920px' } } }"
    >
      <template v-if="selectedBuild">
        <!-- 头部 -->
        <div class="flex items-start gap-5 mb-6">
          <div
            class="w-16 h-16 rounded-2xl flex items-center justify-center text-white font-bold text-xl flex-shrink-0 shadow-lg"
            :style="{ backgroundColor: selectedBuild.professionColor }"
          >
            {{ professionInitial(selectedBuild.profession) }}
          </div>
          <div class="flex-1 min-w-0">
            <h2 class="text-xl font-bold leading-snug">{{ selectedBuild.title }}</h2>
            <p class="text-sm text-surface-400 mt-1">
              {{ selectedBuild.role === 'dps' ? '输出' : '辅助' }} · 
              {{ selectedBuild.eliteSpec ? getProfessionName(selectedBuild.eliteSpec) : '核心职业' }}
            </p>
            <div class="flex flex-wrap gap-2 mt-3">
              <Tag
                :value="selectedBuild.role === 'dps' ? '输出' : '辅助'"
                :severity="selectedBuild.role === 'dps' ? 'danger' : 'success'"
                class="text-sm font-semibold"
              />
              <Tag
                v-for="sub in selectedBuild.subRoles"
                :key="sub"
                :value="subRoleLabel(sub)"
                severity="info"
                class="text-sm"
              />
              <Tag v-if="selectedBuild.isMeta" value="META" severity="success" class="text-sm font-bold" />
            </div>
          </div>
        </div>

        <Divider />

        <Panel header="配装" class="mb-4" toggleable>
          <template #icons><i class="pi pi-shield text-primary" /></template>
          <GearOverviewCard :build="selectedBuild" />
        </Panel>

        <Panel header="Build 代码" class="mb-4" toggleable>
          <template #icons><i class="pi pi-code text-primary" /></template>
          <div class="p-4 rounded-lg bg-surface-900 font-mono text-sm break-all mb-4 leading-relaxed border border-surface-700">
            {{ selectedBuild.bdCode }}
          </div>
          <div class="flex gap-3">
            <Button icon="pi pi-copy" label="复制代码" size="small" @click="copyBuildCode(selectedBuild)" />
            <router-link :to="{ path: '/build-parser', query: { code: selectedBuild.bdCode } }" class="no-underline">
              <Button icon="pi pi-external-link" label="在解析器中打开" size="small" outlined />
            </router-link>
          </div>
        </Panel>

        <Panel v-if="selectedBuild.traitLines?.length" header="特性" class="mb-4" toggleable>
          <template #icons><i class="pi pi-sitemap text-rarity-legendary" /></template>
          <div class="space-y-3">
            <div
              v-for="(line, idx) in selectedBuild.traitLines"
              :key="idx"
              class="flex items-center gap-4 p-3 rounded-lg bg-surface-900 border border-surface-700"
            >
              <span class="text-base font-semibold min-w-[100px]">{{ line.name }}</span>
              <div class="flex gap-2">
                <Tag
                  v-for="(choice, cIdx) in line.choices"
                  :key="cIdx"
                  :value="String(choice)"
                  :severity="['danger', 'warning', 'success'][cIdx]"
                  class="text-sm font-bold w-9 h-9 flex items-center justify-center"
                />
              </div>
            </div>
          </div>
        </Panel>

        <Panel header="指挥口令速查" class="mb-4" toggleable>
          <template #icons><i class="pi pi-microphone text-secondary" /></template>
          <CommanderCheatsheet :commands="selectedBuild.rotationCommands" />
        </Panel>

        <Panel v-if="selectedBuild.mechanics?.length" header="关键机制" class="mb-4" toggleable>
          <template #icons><i class="pi pi-cog text-tech-cyan" /></template>
          <div class="space-y-3">
            <div
              v-for="mech in selectedBuild.mechanics"
              :key="mech.name"
              class="p-4 rounded-lg bg-surface-900 border border-surface-700"
            >
              <div class="text-base font-semibold mb-2">{{ mech.name }}</div>
              <ul class="list-disc list-inside text-sm text-surface-400 space-y-1">
                <li v-for="source in mech.sources" :key="source">{{ source }}</li>
              </ul>
            </div>
          </div>
        </Panel>

        <Panel v-if="selectedBuild.videos?.length" header="参考视频" class="mb-4" toggleable>
          <template #icons><i class="pi pi-video text-red-400" /></template>
          <div class="space-y-3">
            <a
              v-for="video in selectedBuild.videos"
              :key="video.title"
              :href="video.url || '#'"
              class="flex items-center gap-4 p-4 rounded-lg bg-surface-900 border border-surface-700 hover:border-primary transition-colors group no-underline"
              target="_blank"
              rel="noopener noreferrer"
            >
              <div class="w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0 bg-red-500/10">
                <i class="pi pi-play text-red-400" />
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-base font-medium truncate group-hover:text-primary transition-colors">{{ video.title }}</p>
                <p v-if="video.author" class="text-sm text-surface-400 mt-0.5">{{ video.author }}</p>
              </div>
              <i class="pi pi-external-link text-surface-500" />
            </a>
          </div>
        </Panel>

        <Divider />

        <div class="text-sm text-surface-400 space-y-1">
          <p>作者：{{ selectedBuild.author || '未知' }}</p>
          <p>更新：{{ formatFullDate(selectedBuild.updatedAt) }}</p>
          <p>字数：{{ selectedBuild.wordCount }}</p>
        </div>

        <!-- 管理操作（需 write 权限） -->
        <div v-permission="'write'" class="flex gap-3 mt-6 pt-4 border-t border-surface-700">
          <Button icon="pi pi-pencil" label="编辑配置" severity="primary" outlined @click="openEditDialog" />
          <Button icon="pi pi-trash" label="删除配置" severity="danger" outlined @click="confirmDelete" />
        </div>
      </template>
    </Drawer>

    <!-- 新增/编辑对话框 -->
    <BuildEditDialog
      v-model:visible="showEditDialog"
      :editing-build="editingBuild"
      @saved="onDialogSaved"
    />

    <ConfirmDialog />

    <!-- 移动端筛选抽屉 -->
    <Drawer
      v-model:visible="showMobileFilter"
      position="left"
      :pt="{ root: { style: { width: '360px' } } }"
    >
      <BuildFilterSidebar
        :professions="professions"
        :professions-dict="professionsDict"
        :active-profession="filters.profession"
        :active-role="filters.role"
        :active-sub-roles="filters.subRoles"
        :search-query="filters.searchQuery"
        :sort-by="filters.sortBy"
        :role-counts="roleCounts"
        :sub-role-counts="subRoleCounts"
        :profession-counts="professionCounts"
        @select-profession="store.setFilter('profession', $event)"
        @select-role="store.setFilter('role', $event)"
        @toggle-sub-role="toggleSubRole"
        @update-search="store.setFilter('searchQuery', $event)"
        @update-sort="store.setFilter('sortBy', $event as 'updated' | 'profession' | 'name')"
        @clear-filters="clearFilters"
      />
    </Drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'
import PageHeader from '@/components/common/PageHeader.vue'
import BuildFilterSidebar from '@/components/build-library/BuildFilterSidebar.vue'
import BuildCard from '@/components/build-library/BuildCard.vue'
import GearOverviewCard from '@/components/build-library/GearOverviewCard.vue'
import CommanderCheatsheet from '@/components/build-library/CommanderCheatsheet.vue'
import BuildEditDialog from '@/components/build-library/BuildEditDialog.vue'
import Drawer from 'primevue/drawer'
import Button from 'primevue/button'
import Tag from 'primevue/tag'
import Panel from 'primevue/panel'
import Divider from 'primevue/divider'
import ConfirmDialog from 'primevue/confirmdialog'
import Checkbox from 'primevue/checkbox'
import { useBuildLibraryStore } from '@/store/build/buildLibrary'
import type { BuildEntry, SubRoleFilter } from '@/types/buildLibrary'
import { getProfessionName } from '@/utils/profession/professionUtils'

const toast = useToast()
const confirm = useConfirm()
const store = useBuildLibraryStore()

const filters = computed(() => store.filters)
const professions = computed(() => store.professions)
const professionsDict = computed(() => store.professionsDict)
const roleCounts = computed(() => store.roleCounts)
const subRoleCounts = computed(() => store.subRoleCounts)
const professionCounts = computed(() => store.professionCounts)
const filteredBuilds = computed(() => store.filteredBuilds)

const drawerVisible = ref(false)
const showMobileFilter = ref(false)
const selectedBuild = ref<BuildEntry | null>(null)
const showEditDialog = ref(false)
const editingBuild = ref<BuildEntry | null>(null)

// 批量选择相关
const selectedBuildIds = ref<string[]>([])
const selectAllCheckbox = ref(false)

const toggleSubRole = (subRole: SubRoleFilter) => {
  if (subRole === 'all') return
  store.toggleSubRole(subRole)
}

const clearFilters = () => {
  store.clearFilters()
}

onMounted(() => {
  store.fetchBuilds()
})

const openDetail = (build: BuildEntry) => {
  selectedBuild.value = build
  drawerVisible.value = true
}

const openCreateDialog = () => {
  editingBuild.value = null
  showEditDialog.value = true
}

const openEditDialog = () => {
  if (selectedBuild.value) {
    editingBuild.value = selectedBuild.value
    showEditDialog.value = true
  }
}

const openEditDialogFromCard = (build: BuildEntry) => {
  editingBuild.value = build
  showEditDialog.value = true
}

const confirmDelete = () => {
  if (!selectedBuild.value) return
  const build = selectedBuild.value
  confirm.require({
    message: `确定要删除配置「${build.title}」吗？此操作不可恢复。`,
    header: '确认删除',
    icon: 'pi pi-exclamation-triangle',
    acceptLabel: '删除',
    rejectLabel: '取消',
    acceptClass: 'p-button-danger',
    accept: async () => {
      const result = await store.deleteBuild(build.id)
      if (result.success) {
        toast.add({ severity: 'success', summary: '删除成功', detail: `配置「${build.title}」已删除`, life: 3000 })
        drawerVisible.value = false
        selectedBuild.value = null
      } else {
        toast.add({ severity: 'error', summary: '删除失败', detail: result.error || '未知错误', life: 5000 })
      }
    }
  })
}

const onDialogSaved = (updatedBuild?: BuildEntry) => {
  // 编辑完成后刷新数据
  if (updatedBuild) {
    // 如果有返回的更新数据，直接更新选中项
    selectedBuild.value = updatedBuild
  } else if (drawerVisible.value && selectedBuild.value) {
    // 否则从store中查找更新后的build
    const updated = store.builds.find(b => b.id === selectedBuild.value!.id)
    if (updated) {
      // 使用展开操作强制触发响应式更新
      selectedBuild.value = { ...updated }
    }
  }
}

const copyBuildCode = async (build: BuildEntry) => {
  if (!build.bdCode) return
  try {
    await navigator.clipboard.writeText(build.bdCode)
    toast.add({ severity: 'success', summary: '复制成功', detail: 'Build代码已复制到剪贴板', life: 2000 })
  } catch {
    toast.add({ severity: 'error', summary: '复制失败', detail: '无法复制到剪贴板', life: 3000 })
  }
}

const professionInitial = (prof: string): string => {
  const map: Record<string, string> = {
    Elementalist: '元', Engineer: '工', Guardian: '守', Mesmer: '幻',
    Necromancer: '死', Ranger: '游', Revenant: '魂', Warrior: '战'
  }
  return map[prof] || prof.charAt(0)
}

const subRoleLabel = (sub: string): string => {
  const map: Record<string, string> = { boon: '增益', heal: '治疗', tank: '承伤', cc: '削控' }
  return map[sub] || sub
}

// 批量选择方法
const toggleSelectBuild = (buildId: string) => {
  const index = selectedBuildIds.value.indexOf(buildId)
  if (index > -1) {
    selectedBuildIds.value.splice(index, 1)
  } else {
    selectedBuildIds.value.push(buildId)
  }
  updateSelectAllCheckbox()
}

const updateSelectAllCheckbox = () => {
  selectAllCheckbox.value = filteredBuilds.value.length > 0 && 
    selectedBuildIds.value.length === filteredBuilds.value.length
}

const toggleSelectAll = () => {
  if (selectAllCheckbox.value) {
    selectedBuildIds.value = filteredBuilds.value.map(b => b.id)
  } else {
    selectedBuildIds.value = []
  }
}

const batchDelete = () => {
  if (selectedBuildIds.value.length === 0) return
  const count = selectedBuildIds.value.length
  confirm.require({
    message: `确定要删除选中的 ${count} 个配置吗？此操作不可恢复。`,
    header: '确认批量删除',
    icon: 'pi pi-exclamation-triangle',
    acceptLabel: '删除',
    rejectLabel: '取消',
    acceptClass: 'p-button-danger',
    accept: async () => {
      const results = await Promise.all(
        selectedBuildIds.value.map(id => store.deleteBuild(id))
      )
      const successCount = results.filter(r => r.success).length
      if (successCount === count) {
        toast.add({ severity: 'success', summary: '批量删除成功', detail: `已删除 ${count} 个配置`, life: 3000 })
      } else if (successCount > 0) {
        toast.add({ severity: 'warn', summary: '部分删除成功', detail: `成功删除 ${successCount}/${count} 个配置`, life: 5000 })
      } else {
        toast.add({ severity: 'error', summary: '批量删除失败', detail: '删除操作失败', life: 5000 })
      }
      selectedBuildIds.value = []
      selectAllCheckbox.value = false
    }
  })
}

const formatFullDate = (dateStr: string): string => {
  return new Date(dateStr).toLocaleDateString('zh-CN', {
    year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit'
  })
}
</script>
