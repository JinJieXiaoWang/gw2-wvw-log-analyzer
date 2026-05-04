<template>
  <div class="build-filter-sidebar p-6">
    <!-- 搜索 -->
    <div class="mb-6">
      <div class="relative">
        <InputText
          v-model="localSearch"
          class="w-full pl-10 text-base h-11"
          placeholder="搜索 Build 名称、职业..."
          @input="onSearchInput"
        />
        <i class="pi pi-search absolute left-3.5 top-1/2 -translate-y-1/2 text-neutral-text-disabled" />
      </div>
    </div>

    <!-- 职业筛选 -->
    <div class="mb-6">
      <h4 class="text-sm font-bold text-neutral-text-secondary mb-3 uppercase tracking-wider">职业</h4>
      <div class="grid grid-cols-1 gap-2">
        <button
          v-for="prof in professionList"
          :key="prof.key"
          class="profession-btn flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200 text-left"
          :class="{ 'profession-btn-active': activeProfession === prof.key }"
          :style="
            activeProfession === prof.key
              ? { backgroundColor: prof.color + '18', borderColor: prof.color }
              : {}
          "
          @click="selectProfession(prof.key)"
        >
          <div
            class="w-9 h-9 rounded-lg flex items-center justify-center text-white font-bold text-sm flex-shrink-0"
            :style="{ backgroundColor: prof.color }"
          >
            {{ prof.initial }}
          </div>
          <div class="flex-1 min-w-0">
            <div class="text-sm font-semibold text-neutral-text truncate leading-tight">
              {{ prof.label }}
            </div>
            <div class="text-xs text-neutral-text-secondary mt-0.5">{{ prof.count }} 个配置</div>
          </div>
        </button>
      </div>
    </div>

    <!-- 职责筛选 -->
    <div class="mb-6">
      <h4 class="text-sm font-bold text-neutral-text-secondary mb-3 uppercase tracking-wider">职责</h4>
      <div class="flex gap-2">
        <button
          v-for="role in roleOptions"
          :key="role.value"
          class="role-btn flex-1 py-2.5 px-3 rounded-xl text-sm font-semibold transition-all duration-200 text-center"
          :class="{ 'role-btn-active': activeRole === role.value }"
          @click="selectRole(role.value)"
        >
          <span class="block">{{ role.label }}</span>
          <span class="text-xs opacity-60">{{ roleCounts[role.value] || 0 }}</span>
        </button>
      </div>
    </div>

    <!-- 子职责筛选 -->
    <div class="mb-6">
      <h4 class="text-sm font-bold text-neutral-text-secondary mb-3 uppercase tracking-wider">细分职责</h4>
      <div class="flex flex-wrap gap-2">
        <button
          v-for="sub in subRoleOptions"
          :key="sub.value"
          class="subrole-chip px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 border"
          :class="activeSubRoles.includes(sub.value) ? 'subrole-chip-active' : 'subrole-chip-inactive'"
          @click="toggleSubRole(sub.value)"
        >
          {{ sub.label }}
          <span v-if="(subRoleCounts[sub.value] || 0) > 0" class="opacity-50 ml-1 text-xs">
            ({{ subRoleCounts[sub.value] }})
          </span>
        </button>
      </div>
    </div>

    <!-- 排序 -->
    <div class="mb-6">
      <h4 class="text-sm font-bold text-neutral-text-secondary mb-3 uppercase tracking-wider">排序</h4>
      <Dropdown
        v-model="localSort"
        :options="sortOptions"
        option-label="label"
        option-value="value"
        class="w-full"
        @change="onSortChange"
      />
    </div>

    <!-- 清除筛选 -->
    <button
      v-if="hasActiveFilters"
      class="w-full py-2.5 rounded-xl text-sm font-semibold transition-all duration-200 flex items-center justify-center gap-2 clear-btn"
      @click="clearFilters"
    >
      <i class="pi pi-filter-slash" />
      清除筛选
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import InputText from 'primevue/inputtext'
import Dropdown from 'primevue/dropdown'
import type { RoleFilter, SubRoleFilter } from '@/types/buildLibrary'

interface Props {
  professions: string[]
  activeProfession: string
  activeRole: RoleFilter
  activeSubRoles: SubRoleFilter[]
  searchQuery: string
  sortBy: string
  roleCounts: Record<string, number>
  subRoleCounts: Record<string, number>
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'select-profession': [profession: string]
  'select-role': [role: RoleFilter]
  'toggle-sub-role': [subRole: SubRoleFilter]
  'update-search': [query: string]
  'update-sort': [sort: string]
  'clear-filters': []
}>()

const localSearch = ref(props.searchQuery)
const localSort = ref(props.sortBy)

watch(
  () => props.searchQuery,
  (val) => {
    localSearch.value = val
  }
)
watch(
  () => props.sortBy,
  (val) => {
    localSort.value = val
  }
)

let searchTimeout: ReturnType<typeof setTimeout>
const onSearchInput = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => emit('update-search', localSearch.value), 300)
}

const onSortChange = () => emit('update-sort', localSort.value)

const professionData: Record<string, { label: string; initial: string; color: string }> = {
  Elementalist: { label: '元素使', initial: '元', color: '#F18E38' },
  Engineer: { label: '工程师', initial: '工', color: '#D09C59' },
  Guardian: { label: '守护者', initial: '守', color: '#5C9AD6' },
  Mesmer: { label: '幻术师', initial: '幻', color: '#B679D5' },
  Necromancer: { label: '唤灵师', initial: '死', color: '#2A9D8F' },
  Ranger: { label: '游侠', initial: '游', color: '#8BC53F' },
  Revenant: { label: '魂武者', initial: '魂', color: '#C0363D' },
  Warrior: { label: '战士', initial: '战', color: '#FFD166' }
}

const professionList = computed(() => {
  return props.professions.map((key) => ({
    key,
    ...professionData[key],
    count: props.roleCounts[key] || 0
  }))
})

const roleOptions = [
  { label: '全部', value: 'all' as RoleFilter },
  { label: '输出', value: 'dps' as RoleFilter },
  { label: '辅助', value: 'support' as RoleFilter }
]

const subRoleOptions = [
  { label: '增益', value: 'boon' as SubRoleFilter },
  { label: '治疗', value: 'heal' as SubRoleFilter },
  { label: '承伤', value: 'tank' as SubRoleFilter },
  { label: '削控', value: 'cc' as SubRoleFilter }
]

const sortOptions = [
  { label: '最新更新', value: 'updated' },
  { label: '最旧更新', value: 'updated-asc' },
  { label: '职业排序', value: 'profession' }
]

const selectProfession = (prof: string) => {
  emit('select-profession', props.activeProfession === prof ? 'all' : prof)
}

const selectRole = (role: RoleFilter) => emit('select-role', role)
const toggleSubRole = (subRole: SubRoleFilter) => emit('toggle-sub-role', subRole)

const hasActiveFilters = computed(
  () =>
    props.activeProfession !== 'all' ||
    props.activeRole !== 'all' ||
    props.activeSubRoles.length > 0 ||
    props.searchQuery !== ''
)

const clearFilters = () => {
  localSearch.value = ''
  emit('clear-filters')
}
</script>

<style scoped>
.profession-btn {
  border: 1.5px solid transparent;
  background: var(--color-bg-alpha-60, rgba(30, 30, 30, 0.5));
}
.profession-btn:hover {
  background: var(--color-bg-hover, rgba(42, 42, 42, 0.8));
  border-color: var(--color-border);
}
.profession-btn-active {
  border-width: 1.5px;
}

.role-btn {
  background: var(--color-bg-alpha-60, rgba(30, 30, 30, 0.5));
  color: var(--neutral-text-secondary);
  border: 1.5px solid transparent;
}
.role-btn:hover {
  background: var(--color-bg);
  border-color: var(--color-border);
}
.role-btn-active {
  background: rgba(22, 93, 255, 0.15);
  color: var(--primary);
  border-color: rgba(22, 93, 255, 0.3);
}

.subrole-chip-inactive {
  background: var(--color-bg-alpha-60, rgba(30, 30, 30, 0.5));
  color: var(--neutral-text-secondary);
  border-color: var(--color-border);
}
.subrole-chip-inactive:hover {
  background: var(--color-bg);
  border-color: var(--neutral-text-disabled);
}
.subrole-chip-active {
  background: rgba(255, 125, 0, 0.15);
  color: var(--secondary);
  border-color: rgba(255, 125, 0, 0.35);
}

.clear-btn {
  background: rgba(245, 63, 63, 0.08);
  color: var(--status-error);
  border: 1px solid rgba(245, 63, 63, 0.2);
}
.clear-btn:hover {
  background: rgba(245, 63, 63, 0.15);
  border-color: rgba(245, 63, 63, 0.35);
}

:deep(.p-dropdown) {
  background: var(--color-bg);
  border-color: var(--color-border);
}
:deep(.p-dropdown .p-dropdown-label) {
  color: var(--neutral-text);
  font-size: 0.875rem;
}
:deep(.p-dropdown .p-dropdown-trigger) {
  color: var(--neutral-text-secondary);
}
</style>
