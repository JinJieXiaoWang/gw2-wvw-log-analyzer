import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import type { BuildEntry, BuildFilterState, BuildCreateDto } from '@/types/buildLibrary'
import { buildsService } from '@/services/build/buildsService'
import { PROFESSION_COLORS } from '@/types/buildLibrary'
import type { BuildLibraryCreateRequest, BuildLibraryUpdateRequest } from '@/services/build/buildsService'
import { dictionaryService, type DictOption } from '@/services/system/dictionaryService'

export const useBuildLibraryStore = defineStore('buildLibrary', () => {
  // State
  const builds = ref<BuildEntry[]>([])
  const filters = ref<BuildFilterState>({
    profession: 'all',
    role: 'all',
    subRoles: [],
    searchQuery: '',
    sortBy: 'updated',
  })
  const selectedBuildId = ref<string | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  
  // 字典数据
  const professionsDict = ref<DictOption[]>([])
  const eliteSpecsDict = ref<DictOption[]>([])
  const rolesDict = ref<DictOption[]>([])

  // Getters
  const filteredBuilds = computed(() => {
    let result = [...builds.value]

    // Profession filter
    if (filters.value.profession !== 'all') {
      result = result.filter(b => b.profession === filters.value.profession)
    }

    // Role filter
    if (filters.value.role !== 'all') {
      result = result.filter(b => b.role === filters.value.role)
    }

    // Sub-role filter (AND logic: build must have ALL selected sub-roles)
    if (filters.value.subRoles.length > 0) {
      result = result.filter(b =>
        filters.value.subRoles.every(sr => b.subRoles.includes(sr as any))
      )
    }

    // Search filter
    if (filters.value.searchQuery.trim()) {
      const q = filters.value.searchQuery.toLowerCase()
      result = result.filter(b =>
        b.title.toLowerCase().includes(q) ||
        b.profession.toLowerCase().includes(q) ||
        (b.eliteSpec?.toLowerCase().includes(q) ?? false) ||
        b.author.toLowerCase().includes(q)
      )
    }

    // Sorting
    result.sort((a, b) => {
      switch (filters.value.sortBy) {
        case 'updated':
          return new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
        case 'profession':
          return a.profession.localeCompare(b.profession) || a.title.localeCompare(b.title)
        case 'name':
          return a.title.localeCompare(b.title)
        default:
          return 0
      }
    })

    return result
  })

  const selectedBuild = computed(() => {
    if (!selectedBuildId.value) return null
    return builds.value.find(b => String(b.id) === selectedBuildId.value) || null
  })

  const professions = computed(() => {
    const set = new Set(builds.value.map(b => b.profession))
    return Array.from(set).sort()
  })

  // 修复：基于当前筛选后的Builds进行计数
  const roleCounts = computed(() => {
    const counts: Record<string, number> = { all: filteredBuilds.value.length, dps: 0, support: 0 }
    filteredBuilds.value.forEach(b => {
      counts[b.role] = (counts[b.role] || 0) + 1
    })
    return counts
  })

  // 修复：基于当前筛选后的Builds进行计数
  const subRoleCounts = computed(() => {
    const counts: Record<string, number> = { boon: 0, heal: 0, tank: 0, cc: 0 }
    filteredBuilds.value.forEach(b => {
      b.subRoles.forEach(sr => {
        counts[sr] = (counts[sr] || 0) + 1
      })
    })
    return counts
  })
  
  // 基于当前筛选后的职业计数
  const professionCounts = computed(() => {
    const counts: Record<string, number> = {}
    filteredBuilds.value.forEach(b => {
      counts[b.profession] = (counts[b.profession] || 0) + 1
    })
    return counts
  })
  
  // 获取指定职业的精英特长选项
  const getEliteSpecsForProfession = (profession: string) => {
    return eliteSpecsDict.value.filter(spec => 
      spec.value.toLowerCase().includes(profession.toLowerCase()) || 
      spec.css_class?.includes(profession.toLowerCase())
    )
  }

  // Actions
  /** 加载字典数据 */
  async function loadDictionaries() {
    try {
      const [professions, eliteSpecs, roles] = await Promise.all([
        dictionaryService.getOptions('profession'),
        dictionaryService.getOptions('specialization'),
        dictionaryService.getOptions('role'),
      ])
      professionsDict.value = professions
      eliteSpecsDict.value = eliteSpecs
      rolesDict.value = roles
    } catch (e) {
      console.error('[BuildLibrary] 加载字典失败', e)
    }
  }
  
  /** 将后端 snake_case 数据转为前端 camelCase BuildEntry */
  function mapBackendToBuildEntry(raw: any): BuildEntry {
    return {
      id: String(raw.id ?? ''),
      slug: raw.slug ?? '',
      title: raw.title ?? '',
      profession: raw.profession ?? '',
      professionColor: raw.profession_color || PROFESSION_COLORS[raw.profession] || '#888888',
      eliteSpec: raw.elite_spec ?? null,
      role: raw.role === 'dps' || raw.role === 'support' ? raw.role : 'dps',
      subRoles: (raw.sub_roles || []).filter((r: string) => ['boon', 'heal', 'tank', 'cc'].includes(r)),
      armorType: raw.armor_type ?? '',
      weapons: (raw.weapons || []).map((w: any) => ({
        set: w.set ?? 0,
        name: w.name ?? '',
        sigils: w.sigils || []
      })),
      relic: raw.relic ?? '',
      rune: raw.rune ?? '',
      food: raw.food ?? '',
      wrench: raw.wrench ?? '',
      infusion: raw.infusion ?? '',
      attrRequirements: raw.attr_requirements || [],
      bdCode: raw.bd_code ?? '',
      traitLines: (raw.trait_lines || []).map((t: any) => ({
        name: t.name ?? '',
        choices: (t.choices || []).slice(0, 3) as [number, number, number]
      })),
      rotationCommands: (raw.rotation_commands || []).map((c: any) => ({
        callout: c.callout ?? '',
        action: c.action ?? '',
        note: c.note
      })),
      mechanics: (raw.mechanics || []).map((m: any) => ({
        name: m.name ?? '',
        sources: m.sources || []
      })),
      videos: (raw.videos || []).map((v: any) => ({
        title: v.title ?? '',
        url: v.url ?? '',
        author: v.author
      })),
      author: raw.author ?? '',
      updatedAt: raw.updated_at || raw.created_at || new Date().toISOString(),
      wordCount: raw.word_count ?? 0,
      isMeta: raw.is_meta ?? false,
    }
  }

  async function fetchBuilds() {
    loading.value = true
    error.value = null
    try {
      // 先加载字典数据
      if (professionsDict.value.length === 0) {
        await loadDictionaries()
      }
      
      const params: Record<string, any> = {}
      if (filters.value.profession && filters.value.profession !== 'all') {
        params.profession = filters.value.profession
      }
      if (filters.value.role && filters.value.role !== 'all') {
        params.role = filters.value.role
      }
      if (filters.value.subRoles.length > 0) {
        params.sub_role = filters.value.subRoles.join(',')
      }
      if (filters.value.searchQuery.trim()) {
        params.search = filters.value.searchQuery.trim()
      }
      const sortMap: Record<string, string> = {
        updated: 'updated',
        profession: 'profession',
        name: 'name'
      }
      params.sort_by = sortMap[filters.value.sortBy] || 'updated'

      const response = await buildsService.getBuildLibraryList(params)
      const items = response.data?.items || []
      builds.value = items.map(mapBackendToBuildEntry)
    } catch (e: any) {
      error.value = e?.message || '加载失败'
      console.error('[BuildLibrary] fetchBuilds error:', e)
    } finally {
      loading.value = false
    }
  }

  function setFilter<K extends keyof BuildFilterState>(key: K, value: BuildFilterState[K]) {
    filters.value[key] = value
  }

  function toggleSubRole(role: string) {
    const idx = filters.value.subRoles.indexOf(role as any)
    if (idx >= 0) {
      filters.value.subRoles.splice(idx, 1)
    } else {
      filters.value.subRoles.push(role as any)
    }
  }

  function selectBuild(id: string | null) {
    selectedBuildId.value = id
  }

  function clearFilters() {
    filters.value = {
      profession: 'all',
      role: 'all',
      subRoles: [],
      searchQuery: '',
      sortBy: 'updated',
    }
  }

  /** 将前端 camelCase BuildEntry/DTO 转为后端 snake_case 请求体 */
  function mapBuildToBackend(build: Partial<BuildEntry> | BuildCreateDto): BuildLibraryCreateRequest {
    return {
      title: build.title ?? '',
      profession: build.profession ?? '',
      profession_color: (build as any).professionColor ?? PROFESSION_COLORS[build.profession ?? ''] ?? null,
      elite_spec: (build as any).eliteSpec ?? null,
      role: build.role ?? 'dps',
      sub_roles: (build as any).subRoles ?? [],
      armor_type: (build as any).armorType ?? null,
      weapons: (build as any).weapons ?? [],
      relic: (build as any).relic ?? null,
      rune: (build as any).rune ?? null,
      food: (build as any).food ?? null,
      wrench: (build as any).wrench ?? null,
      infusion: (build as any).infusion ?? null,
      attr_requirements: (build as any).attrRequirements ?? [],
      bd_code: (build as any).bdCode ?? '',
      trait_lines: ((build as any).traitLines ?? []).map((t: any) => ({
        name: t.name ?? '',
        choices: t.choices ?? [1, 1, 1]
      })),
      rotation_commands: ((build as any).rotationCommands ?? []).map((c: any) => ({
        callout: c.callout ?? '',
        action: c.action ?? '',
        note: c.note
      })),
      mechanics: ((build as any).mechanics ?? []).map((m: any) => ({
        name: m.name ?? '',
        sources: m.sources ?? []
      })),
      videos: ((build as any).videos ?? []).map((v: any) => ({
        title: v.title ?? '',
        url: v.url ?? '',
        author: v.author
      })),
      author: (build as any).author ?? '',
      is_meta: (build as any).isMeta ?? false,
    }
  }

  async function createBuild(build: BuildCreateDto) {
    loading.value = true
    error.value = null
    try {
      const data = mapBuildToBackend(build)
      const response = await buildsService.createBuildLibrary(data)
      if (response.data) {
        builds.value.unshift(mapBackendToBuildEntry(response.data))
      }
      return { success: true, data: response.data }
    } catch (e: any) {
      error.value = e?.message || '创建失败'
      console.error('[BuildLibrary] createBuild error:', e)
      return { success: false, error: e?.message || '创建失败' }
    } finally {
      loading.value = false
    }
  }

  async function updateBuild(buildId: string, build: Partial<BuildEntry>) {
    loading.value = true
    error.value = null
    try {
      const data: BuildLibraryUpdateRequest = mapBuildToBackend(build)
      const response = await buildsService.updateBuildLibrary(Number(buildId), data)
      if (response.data) {
        const idx = builds.value.findIndex(b => b.id === buildId)
        if (idx >= 0) {
          builds.value[idx] = mapBackendToBuildEntry(response.data)
        }
      }
      return { success: true, data: response.data }
    } catch (e: any) {
      error.value = e?.message || '更新失败'
      console.error('[BuildLibrary] updateBuild error:', e)
      return { success: false, error: e?.message || '更新失败' }
    } finally {
      loading.value = false
    }
  }

  async function deleteBuild(buildId: string) {
    loading.value = true
    error.value = null
    try {
      await buildsService.deleteBuildLibrary(Number(buildId))
      builds.value = builds.value.filter(b => b.id !== buildId)
      if (selectedBuildId.value === buildId) {
        selectedBuildId.value = null
      }
      return { success: true }
    } catch (e: any) {
      error.value = e?.message || '删除失败'
      console.error('[BuildLibrary] deleteBuild error:', e)
      return { success: false, error: e?.message || '删除失败' }
    } finally {
      loading.value = false
    }
  }

  return {
    builds,
    filters,
    selectedBuildId,
    loading,
    error,
    filteredBuilds,
    selectedBuild,
    professions,
    roleCounts,
    subRoleCounts,
    professionCounts,
    professionsDict,
    eliteSpecsDict,
    rolesDict,
    fetchBuilds,
    setFilter,
    toggleSubRole,
    selectBuild,
    clearFilters,
    createBuild,
    updateBuild,
    deleteBuild,
    loadDictionaries,
    getEliteSpecsForProfession,
  }
})
