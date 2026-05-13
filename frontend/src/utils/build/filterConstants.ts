import type { RoleFilter, SubRoleFilter } from '@/types/buildLibrary'

export const professionData: Record<string, { label: string; initial: string; color: string }> = {
  Elementalist: { label: '元素使', initial: '元', color: '#F18E38' },
  Engineer: { label: '工程师', initial: '工', color: '#D09C59' },
  Guardian: { label: '守护者', initial: '守', color: '#5C9AD6' },
  Mesmer: { label: '幻术师', initial: '幻', color: '#B679D5' },
  Necromancer: { label: '唤灵师', initial: '死', color: '#2A9D8F' },
  Ranger: { label: '游侠', initial: '游', color: '#8BC53F' },
  Revenant: { label: '魂武者', initial: '魂', color: '#C0363D' },
  Warrior: { label: 'սʿ', initial: 'ս', color: '#FFD166' },
}

export const roleOptions = [
  { label: '全部', value: 'all' as RoleFilter },
  { label: '输出', value: 'dps' as RoleFilter },
  { label: '辅助', value: 'support' as RoleFilter },
]

export const subRoleOptions = [
  { label: '增益', value: 'boon' as SubRoleFilter },
  { label: '治疗', value: 'heal' as SubRoleFilter },
  { label: '承伤', value: 'tank' as SubRoleFilter },
  { label: '削控', value: 'cc' as SubRoleFilter },
]

export const sortOptions = [
  { label: '最新更新', value: 'updated' },
  { label: '最旧更新', value: 'updated-asc' },
  { label: '职业排序', value: 'profession' },
]
