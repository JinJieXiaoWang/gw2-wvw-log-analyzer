<template>
  <div class="min-h-screen pb-6 sm:pb-10">
    <PageHeader
      title="配置图书馆"
      subtitle="格林特职业学院战场配置百科"
      icon="pi pi-book"
      icon-gradient="bg-gradient-to-br from-primary to-secondary"
    />

    <div
      v-permission="'write'"
      class="flex items-center justify-end gap-3 mt-3 sm:mt-4 mb-2"
    >
      <Button
        icon="pi pi-plus"
        label="新增配置"
        severity="primary"
        class="w-full sm:w-auto"
        @click="openCreateDialog"
      />
    </div>

    <div class="flex flex-col lg:flex-row gap-4 sm:gap-6 lg:gap-8 mt-4 sm:mt-6">
      <aside class="w-full lg:w-80 flex-shrink-0 hidden lg:block">
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

      <div class="lg:hidden w-full mb-4">
        <BaseButton
          icon="pi pi-filter"
          label="筛选"
          severity="secondary"
          outlined
          class="w-full"
          @click="showMobileFilter = true"
        />
      </div>

      <main class="flex-1 min-w-0">
        <div
          v-if="selectedBuildIds.length > 0"
          class="flex flex-wrap items-center gap-3 sm:gap-4 mb-3 sm:mb-4 p-3 rounded-xl bg-primary/5 border border-primary/20"
        >
          <span class="text-sm text-surface-400">已选择 {{ selectedBuildIds.length }} 个配置</span>
          <BaseButton
            icon="pi pi-trash"
            label="批量删除"
            severity="danger"
            size="small"
            @click="batchDelete"
          />
          <BaseButton
            icon="pi pi-times"
            label="取消选择"
            severity="secondary"
            outlined
            size="small"
            @click="selectedBuildIds = []"
          />
        </div>

        <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 mb-3 sm:mb-4">
          <p class="text-sm sm:text-base text-surface-400">
            共 <span class="text-surface-0 font-bold text-sm sm:text-lg">{{ filteredBuilds.length }}</span> 个配置
          </p>
          <div
            v-if="filteredBuilds.length > 0"
            class="flex items-center gap-2"
          >
            <BaseCheckbox
              v-model="selectAllCheckbox"
              @click="toggleSelectAll"
            />
            <span class="text-sm text-surface-400">全选</span>
          </div>
        </div>

        <div
          v-if="filteredBuilds.length > 0"
          class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-2 xl:grid-cols-3 gap-3 sm:gap-4 lg:gap-5"
        >
          <div
            v-for="build in filteredBuilds"
            :key="build.id"
            class="relative"
          >
            <div class="absolute top-2 sm:top-3 left-2 sm:left-3 z-10">
              <BaseCheckbox
                :model-value="selectedBuildIds.includes(build.id)"
                class="bg-surface-900"
                @click="toggleSelectBuild(build.id)"
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

        <div
          v-else
          class="text-center py-12 sm:py-20 rounded-xl border border-surface-700"
        >
          <i class="pi pi-inbox text-4xl sm:text-5xl text-surface-500 mb-3 sm:mb-4" />
          <h3 class="text-base sm:text-lg font-semibold mb-2">
            未找到匹配的配置
          </h3>
          <p class="text-sm sm:text-base text-surface-400 mb-3 sm:mb-4">
            尝试调整筛选条件或搜索关键词
          </p>
          <BaseButton
            label="清除筛选"
            icon="pi pi-filter-slash"
            severity="secondary"
            outlined
            class="w-full sm:w-auto"
            @click="clearFilters"
          />
        </div>
      </main>
    </div>

    <BuildDetailDrawer
      v-model:visible="drawerVisible"
      :build="selectedBuild"
      @copy-code="copyBuildCode"
      @edit="openEditDialog"
      @delete="confirmDelete"
    />

    <BuildEditDialog
      v-model:visible="showEditDialog"
      :editing-build="editingBuild"
      @saved="onDialogSaved"
    />

    <ConfirmDialog />

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
import BuildCard from '@/components/build/library/BuildCard.vue'
import BuildDetailDrawer from '@/components/build/library/BuildDetailDrawer.vue'
import BuildEditDialog from '@/components/build/library/BuildEditDialog.vue'
import BuildFilterSidebar from '@/components/build/library/BuildFilterSidebar.vue'
import BaseButton from '@/components/common/ui/input/BaseButton.vue'
import BaseCheckbox from '@/components/common/ui/input/BaseCheckbox.vue'
import PageHeader from '@/layout/components/PageHeader.vue'
import { useBuildLibraryStore } from '@/store/build/buildLibrary'
import type { BuildEntry, SubRoleFilter } from '@/types/buildLibrary'
import Button from 'primevue/button'
import ConfirmDialog from 'primevue/confirmdialog'
import Drawer from 'primevue/drawer'
import { useConfirm } from 'primevue/useconfirm'
import { useToast } from 'primevue/usetoast'
import { computed, onMounted, ref } from 'vue'

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
  if (updatedBuild) {
    selectedBuild.value = updatedBuild
  } else if (drawerVisible.value && selectedBuild.value) {
    const updated = store.builds.find(b => b.id === selectedBuild.value!.id)
    if (updated) {
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
</script>
