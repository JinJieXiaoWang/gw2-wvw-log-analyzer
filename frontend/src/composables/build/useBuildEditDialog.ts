import { bdCodeService } from '@/services/build/bdCodeService'
import { configManager } from '@/services/core/configManager'
import { dictionaryService } from '@/services/system/dictionaryService'
import { useBuildLibraryStore } from '@/store/build/buildLibrary'
import type { BuildCreateDto, BuildEntry } from '@/types/buildLibrary'
import { useToast } from 'primevue/usetoast'
import { computed, onMounted, ref, watch } from 'vue'

export type SubRoleType = 'boon' | 'heal' | 'tank' | 'cc'

export const SUB_ROLE_OPTIONS: { label: string; value: SubRoleType }[] = [
  { label: '增益', value: 'boon' },
  { label: '治疗', value: 'heal' },
  { label: '承伤', value: 'tank' },
  { label: '削控', value: 'cc' }
]

// 缓存字典数据，避免重复加载
let cachedCascadeData: any[] = []
let cachedRolesDict: any[] = []
let isCacheLoaded = false

export function useBuildEditDialog(props: { visible: boolean; editingBuild?: BuildEntry | null }, emit: { (e: 'update:visible', value: boolean): void; (e: 'saved', build: BuildEntry): void }) {
  const toast = useToast()
  const store = useBuildLibraryStore()

  const localVisible = computed({ get: () => props.visible, set: v => emit('update:visible', v) })
  const isEdit = computed(() => !!props.editingBuild)
  const submitting = ref(false)
  const parsing = ref(false)

  const cascadeData = ref<any[]>([])
  const rolesDict = ref<any[]>([])
  const loadingDicts = ref(false)

  const professionOptions = computed(() => cascadeData.value.map((p: any) => ({ label: p.label, value: p.value })))
  const roleOptions = computed(() => rolesDict.value.map((r: any) => ({ label: r.label, value: r.value })))
  const eliteSpecOptions = computed(() => {
    if (!form.value.profession || cascadeData.value.length === 0) return []
    const prof = cascadeData.value.find((p: any) => p.value === form.value.profession)
    if (!prof || !prof.elite_specs) return []
    return prof.elite_specs.map((s: any) => ({ label: s.label, value: s.value }))
  })

  function createEmptyForm(): BuildCreateDto {
    return {
      title: '', profession: 'Elementalist', eliteSpec: null, role: 'dps', subRoles: [],
      armorType: '', weapons: [], relic: '', rune: '', food: '', wrench: '', infusion: '',
      attrRequirements: [], bdCode: '', traitLines: [], rotationCommands: [], mechanics: [],
      videos: [], author: '', isMeta: false
    }
  }

  const form = ref<BuildCreateDto>(createEmptyForm())

  // 使用 watch 代替 computed 来监听 profession 变化
  watch(() => form.value.profession, (newProf, oldProf) => {
    if (newProf !== oldProf) {
      form.value.eliteSpec = null
    }
  }, { immediate: false })

  const isValid = computed(() => {
    const f = form.value
    return f.title.trim().length >= 2 && 
           f.profession.length > 0 && 
           f.role.length > 0 && 
           /^\[&[A-Za-z0-9+/=]+\]$/.test(f.bdCode.trim())
  })

  // 优化：使用缓存机制
  async function loadDictionaries() {
    // 如果已缓存，直接使用
    if (isCacheLoaded) {
      cascadeData.value = [...cachedCascadeData]
      rolesDict.value = [...cachedRolesDict]
      loadingDicts.value = false
      return
    }

    loadingDicts.value = true
    try {
      const [cascadeRes, roles] = await Promise.all([
        fetch('/api/v1/professions/cascade'),
        dictionaryService.getOptions('role')
      ])
      const cascade = await cascadeRes.json()
      cachedCascadeData = cascade.data || []
      cachedRolesDict = roles
      isCacheLoaded = true
      
      cascadeData.value = [...cachedCascadeData]
      rolesDict.value = [...cachedRolesDict]
    } catch (e) {
      console.error('加载字典失败', e)
    } finally {
      loadingDicts.value = false
    }
  }

  function toggleSubRole(role: SubRoleType) {
    const idx = form.value.subRoles.indexOf(role)
    if (idx >= 0) {
      form.value.subRoles.splice(idx, 1)
    } else {
      form.value.subRoles.push(role)
    }
  }

  function addWeapon() {
    form.value.weapons.push({ set: form.value.weapons.length + 1, name: '', sigils: [] })
  }

  function removeWeapon(idx: number) {
    form.value.weapons.splice(idx, 1)
    // 更新剩余武器的 set 序号
    form.value.weapons.forEach((w, i) => {
      w.set = i + 1
    })
  }

  function addTraitLine() {
    form.value.traitLines.push({ name: '', choices: [1, 1, 1] })
  }

  function removeTraitLine(idx: number) {
    form.value.traitLines.splice(idx, 1)
  }

  function addRotationCommand() {
    form.value.rotationCommands.push({ callout: '', action: '', note: '' })
  }

  function removeRotationCommand(idx: number) {
    form.value.rotationCommands.splice(idx, 1)
  }

  function addMechanic() {
    form.value.mechanics.push({ name: '', sources: [] })
  }

  function removeMechanic(idx: number) {
    form.value.mechanics.splice(idx, 1)
  }

  function addMechanicSource(mechIdx: number) {
    form.value.mechanics[mechIdx].sources.push('')
  }

  function removeMechanicSource(mechIdx: number, srcIdx: number) {
    form.value.mechanics[mechIdx].sources.splice(srcIdx, 1)
  }

  function addVideo() {
    form.value.videos.push({ title: '', url: '', author: undefined })
  }

  function removeVideo(idx: number) {
    form.value.videos.splice(idx, 1)
  }

  function addAttrRequirement() {
    form.value.attrRequirements.push('')
  }

  function removeAttrRequirement(idx: number) {
    form.value.attrRequirements.splice(idx, 1)
  }

  // 优化：使用 watch 的 deep: false，只监听引用变化
  watch(() => props.editingBuild, (build) => {
    if (build) {
      // 优化：避免不必要的深拷贝，只复制必要字段
      form.value = {
        title: build.title,
        profession: build.profession,
        eliteSpec: build.eliteSpec,
        role: build.role,
        subRoles: [...build.subRoles],
        armorType: build.armorType,
        weapons: build.weapons.map(w => ({ ...w, sigils: [...w.sigils] })),
        relic: build.relic,
        rune: build.rune,
        food: build.food,
        wrench: build.wrench,
        infusion: build.infusion,
        attrRequirements: [...build.attrRequirements],
        bdCode: build.bdCode,
        traitLines: build.traitLines.map(t => ({ name: t.name, choices: [...t.choices] })),
        rotationCommands: build.rotationCommands.map(c => ({ ...c })),
        mechanics: build.mechanics.map(m => ({ name: m.name, sources: [...m.sources] })),
        videos: build.videos.map(v => ({ ...v })),
        author: build.author,
        isMeta: build.isMeta
      }
    } else {
      form.value = createEmptyForm()
    }
  }, { immediate: true, deep: false })

  function onHide() {
    if (!submitting.value) {
      form.value = createEmptyForm()
    }
  }

  async function parseBDCode() {
    const code = form.value.bdCode.trim()
    if (!code.startsWith('[&')) {
      toast.add({ severity: 'warn', summary: '格式错误', detail: 'BD Code 必须以 [& 开头', life: configManager.get('ui').toastLife })
      return
    }
    parsing.value = true
    try {
      const validateRes = await bdCodeService.validateBDCode({ bd_code: code })
      if (!validateRes.data?.is_valid) {
        toast.add({ severity: 'error', summary: '校验失败', detail: validateRes.data?.error || 'BD Code 格式不正确', life: configManager.get('ui').toastErrorLife })
        return
      }
      const response = await bdCodeService.parseBDCode({ bd_code: code })
      const data = response.data
      if (!data) {
        toast.add({ severity: 'error', summary: '解析失败', detail: '无法解析该 BD Code', life: configManager.get('ui').toastLife })
        return
      }
      const profMap: Record<string, string> = { 
        Guardian: 'Guardian', Revenant: 'Revenant', Warrior: 'Warrior', 
        Engineer: 'Engineer', Ranger: 'Ranger', Thief: 'Thief', 
        Elementalist: 'Elementalist', Mesmer: 'Mesmer', Necromancer: 'Necromancer' 
      }
      if (data.profession && profMap[data.profession]) {
        form.value.profession = profMap[data.profession]
      }
      const specs = data.specializations || []
      const eliteSpec = specs.find((s: any) => s.is_elite)
      if (eliteSpec?.name_cn || eliteSpec?.name) {
        form.value.eliteSpec = eliteSpec.name_cn || eliteSpec.name
      }
      form.value.traitLines = specs
        .filter((s: any) => Array.isArray(s.selected_traits) && s.selected_traits.length === 3)
        .map((s: any) => ({ 
          name: s.name_cn || s.name || '', 
          choices: s.selected_traits as [number, number, number] 
        }))
        .filter((t: any) => t.name)
      toast.add({ severity: 'success', summary: '解析成功', detail: `已自动填充职业、${form.value.traitLines.length} 条特性线`, life: configManager.get('ui').toastLife })
    } catch (e: any) {
      toast.add({ severity: 'error', summary: '解析失败', detail: e?.message || '网络错误', life: configManager.get('ui').toastErrorLife })
    } finally {
      parsing.value = false
    }
  }

  async function onSubmit() {
    if (!isValid.value) return
    submitting.value = true
    try {
      let result: any
      if (isEdit.value && props.editingBuild) {
        result = await store.updateBuild(props.editingBuild.id, form.value as any)
      } else {
        result = await store.createBuild(form.value)
      }
      if (result.success) {
        toast.add({ severity: 'success', summary: isEdit.value ? '修改成功' : '创建成功', detail: `配置「${form.value.title}」已${isEdit.value ? '更新' : '创建'}`, life: configManager.get('ui').toastLife })
        localVisible.value = false
        if (result.data) {
          emit('saved', result.data)
        }
      } else {
        toast.add({ severity: 'error', summary: isEdit.value ? '修改失败' : '创建失败', detail: result.error || '未知错误', life: configManager.get('ui').toastErrorLife })
      }
    } catch (e: any) {
      toast.add({ severity: 'error', summary: '提交失败', detail: e?.message || '网络错误或服务器异常', life: configManager.get('ui').toastErrorLife })
    } finally {
      submitting.value = false
    }
  }

  onMounted(() => {
    loadDictionaries()
  })

  return {
    form, isEdit, submitting, loadingDicts,
    professionOptions, eliteSpecOptions, roleOptions,
    parsing, isValid, localVisible,
    toggleSubRole, addWeapon, removeWeapon,
    addTraitLine, removeTraitLine,
    addRotationCommand, removeRotationCommand,
    addMechanic, removeMechanic, addMechanicSource, removeMechanicSource,
    addVideo, removeVideo,
    addAttrRequirement, removeAttrRequirement,
    parseBDCode, onSubmit, onHide
  }
}
