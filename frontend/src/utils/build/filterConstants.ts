import { RoleType, BUILD_SORT_OPTIONS, BUILD_SUB_ROLE_OPTIONS } from '@/constants/dictValues'
import type { RoleFilter, SubRoleFilter } from '@/types/buildLibrary'

export const professionData: Record<string, { label: string; initial: string; color: string }> = {
  Elementalist: { label: '元素使', initial: '元', color: '#F18E38' },
  Engineer: { label: '工程师', initial: '工', color: '#D09C59' },
  Guardian: { label: '守护者', initial: '守', color: '#5C9AD6' },
  Mesmer: { label: '幻术师', initial: '幻', color: '#B679D5' },
  Necromancer: { label: '唤灵师', initial: '死', color: '#2A9D8F' },
  Ranger: { label: '游侠', initial: '游', color: '#8BC53F' },
  Revenant: { label: '魂武者', initial: '魂', color: '#C0363D' },
  Warrior: { label: '战士', initial: '战', color: '#FFD166' },
}

export const roleOptions = [
  { label: '全部', value: 'all' as RoleFilter },
  { label: '输出', value: RoleType.DPS as RoleFilter },
  { label: '辅助', value: RoleType.SUPPORT as RoleFilter },
]

export const subRoleOptions = BUILD_SUB_ROLE_OPTIONS.map(o => ({ label: o.label, value: o.value as SubRoleFilter }))

export const sortOptions = BUILD_SORT_OPTIONS.map(o => ({ ...o }))
