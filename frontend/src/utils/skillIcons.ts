/**
 * 技能图标路径映射
 * 使用 Vite import.meta.glob 在构建时收集所有技能图标路径
 */
const skillIcons = import.meta.glob('@/assets/images/skills/*.png', {
  eager: true,
  query: '?url',
  import: 'default',
})

export const getSkillIconUrl = (name: string): string => {
  if (!name) return ''
  const cleanName = name.replace(/^"|"$/g, '').trim()
  const key = `/src/assets/images/skills/${cleanName}.png`
  return (skillIcons[key] as string) || ''
}
