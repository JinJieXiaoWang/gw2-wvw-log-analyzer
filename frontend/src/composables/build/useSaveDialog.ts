import { ref, watch, computed, type Ref } from 'vue'
import { useDictMapping } from '@/composables/core/useDictMapping'

export interface SaveFormData {
  title: string
  profession: string
  eliteSpec: string | null
  role: string
  subRoles: string[]
  armorType: string
  weapons: unknown[]
  relic: string
  rune: string
  food: string
  wrench: string
  infusion: string
  attrRequirements: string[]
  bdCode: string
  traitLines: unknown[]
  rotationCommands: unknown[]
  mechanics: unknown[]
  videos: unknown[]
  author: string
  notes: string
  isMeta: boolean
}

export function useSaveDialog(visible: Ref<boolean>, parsedData?: Record<string, unknown>, buildCode?: string) {
  const isSaving = ref(false)
  const formData = ref<SaveFormData>({
    title: '', profession: '', eliteSpec: null, role: '', subRoles: [],
    armorType: '', weapons: [], relic: '', rune: '', food: '',
    wrench: '', infusion: '', attrRequirements: [], bdCode: '',
    traitLines: [], rotationCommands: [], mechanics: [], videos: [],
    author: '', notes: '', isMeta: false,
  })
  const errors = ref<{ title?: string; profession?: string; role?: string }>({})

  const { data: professionDictData } = useDictMapping('profession', false)
  const { data: roleDictData } = useDictMapping('role', false)

  const professionOptions = computed(() => professionDictData.value.length > 0
    ? professionDictData.value.map((p) => ({ label: p.label, value: p.value }))
    : [])
  const roleOptions = computed(() => roleDictData.value.length > 0
    ? roleDictData.value.map((r) => ({ label: r.label, value: r.value }))
    : [])

  const initializeForm = () => {
    if (parsedData) {
      formData.value = {
        title: '', profession: (parsedData.profession as string) || '', eliteSpec: (parsedData.elite_spec as string | null) || null,
        role: '', subRoles: [], armorType: (parsedData.armor_type as string) || '', weapons: (parsedData.weapons as unknown[]) || [],
        relic: (parsedData.relic as string) || '', rune: (parsedData.rune as string) || '', food: '', wrench: '',
        infusion: '', attrRequirements: [], bdCode: buildCode || '',
        traitLines: (parsedData.traits as unknown[]) || [], rotationCommands: [], mechanics: [],
        videos: [], author: '', notes: '', isMeta: false,
      }
    }
    errors.value = {}
  }

  watch(visible, (v) => { if (v) initializeForm() })

  const validateForm = (): boolean => {
    errors.value = {}
    let isValid = true
    if (!formData.value.title.trim()) { errors.value.title = '请输入Build名称'; isValid = false }
    if (!formData.value.profession) { errors.value.profession = '请选择职业'; isValid = false }
    if (!formData.value.role) { errors.value.role = '请选择职责'; isValid = false }
    return isValid
  }

  const handleSubmit = async (emitSave: (data: SaveFormData) => void) => {
    if (!validateForm()) return
    isSaving.value = true
    try { emitSave(formData.value) } catch (e) { console.error('保存失败:', e) } finally { isSaving.value = false }
  }

  return { isSaving, formData, errors, professionOptions, roleOptions, handleSubmit }
}
