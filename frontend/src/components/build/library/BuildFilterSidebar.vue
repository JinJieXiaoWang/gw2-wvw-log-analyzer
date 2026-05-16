<template>
  <div class="build-filter-sidebar p-6">
    <div class="mb-6">
      <div class="relative">
        <InputText
          v-model="localSearch"
          class="w-full pl-10 text-base h-11"
          placeholder="搜索 Build 名称、职业、角色"
          @input="onSearchInput"
        />
        <i class="pi pi-search absolute left-3.5 top-1/2 -translate-y-1/2 text-neutral-text-disabled" />
      </div>
    </div>

    <FilterSection title="职业">
      <div class="grid grid-cols-1 gap-2">
        <button
          v-for="prof in professionList"
          :key="prof.key"
          class="profession-btn flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200 text-left"
          :class="{ 'profession-btn-active': activeProfession === prof.key }"
          :style="activeProfession === prof.key ? { backgroundColor: prof.color + '18', borderColor: prof.color } : {}"
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
            <div class="text-xs text-neutral-text-secondary mt-0.5">
              {{ prof.count }} 个配置
            </div>
          </div>
        </button>
      </div>
    </FilterSection>

    <FilterSection title="职责">
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
    </FilterSection>

    <FilterSection title="子职责">
      <div class="flex flex-wrap gap-2">
        <button
          v-for="sub in subRoleOptions"
          :key="sub.value"
          class="subrole-chip px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 border"
          :class="activeSubRoles.includes(sub.value) ? 'subrole-chip-active' : 'subrole-chip-inactive'"
          @click="toggleSubRole(sub.value)"
        >
          {{ sub.label }}
          <span
            v-if="(subRoleCounts[sub.value] || 0) > 0"
            class="opacity-50 ml-1 text-xs"
          >({{ subRoleCounts[sub.value] }})</span>
        </button>
      </div>
    </FilterSection>

    <FilterSection title="排序">
      <BaseSelect
        v-model="localSort"
        :options="sortOptions"
        option-label="label"
        option-value="value"
        class="w-full"
        @change="onSortChange"
      />
    </FilterSection>

    <button
      v-if="hasActiveFilters"
      class="w-full py-2.5 rounded-xl text-sm font-semibold transition-all duration-200 flex items-center justify-center gap-2 clear-btn"
      @click="clearFilters"
    >
      <i class="pi pi-filter-slash" /> 清除筛选
    </button>
  </div>
</template>

<script setup lang="ts">
import BaseSelect from '@/components/common/ui/input/BaseSelect.vue'
import type { RoleFilter, SubRoleFilter } from '@/types/buildLibrary'
import { professionData, roleOptions, sortOptions, subRoleOptions } from '@/utils/build/filterConstants'
import InputText from 'primevue/inputtext'
import { computed, ref, watch } from 'vue'
import FilterSection from './FilterSection.vue'

interface Props {
  professions: string[]
  professionsDict: { value: string, label: string, css_class?: string, is_default: number }[]
  activeProfession: string
  activeRole: RoleFilter
  activeSubRoles: SubRoleFilter[]
  searchQuery: string
  sortBy: string
  roleCounts: Record<string, number>
  subRoleCounts: Record<string, number>
  professionCounts: Record<string, number>
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

watch(() => props.searchQuery, (val) => { localSearch.value = val })
watch(() => props.sortBy, (val) => { localSort.value = val })

let searchTimeout: ReturnType<typeof setTimeout>
const onSearchInput = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => emit('update-search', localSearch.value), 300)
}
const onSortChange = () => emit('update-sort', localSort.value)

const professionList = computed(() => {
  const result = props.professions.map((key) => {
    const dictProf = props.professionsDict.find(p => p.value === key)
    const fallback = professionData[key] || { label: key, initial: key.charAt(0), color: '#6B7280' }
    return { key, label: dictProf?.label || fallback.label, initial: fallback.initial, color: dictProf?.css_class || fallback.color, count: props.professionCounts[key] || 0 }
  })
  result.unshift({ key: 'all', label: '全部', initial: '全', color: '#165DFF', count: props.roleCounts.all || 0 })
  return result
})

const selectProfession = (prof: string) => emit('select-profession', props.activeProfession === prof ? 'all' : prof)
const selectRole = (role: RoleFilter) => emit('select-role', role)
const toggleSubRole = (subRole: SubRoleFilter) => emit('toggle-sub-role', subRole)

const hasActiveFilters = computed(() =>
  props.activeProfession !== 'all' || props.activeRole !== 'all' || props.activeSubRoles.length > 0 || props.searchQuery !== ''
)

const clearFilters = () => {
  localSearch.value = ''
  emit('clear-filters')
}
</script>

<style scoped>
@import '@/styles/components/build/BuildFilterSidebar.css';
</style>
