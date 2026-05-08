/**
 * 技能图标路径映射
 * 使用 Vite import.meta.glob 在构建时收集所有技能图标路径
 * 策略：优先使用后端提供的 GW2 CDN URL，fallback 到本地缓存 PNG
 */
const skillIcons = import.meta.glob('@/assets/images/skills/*.png', {
  eager: true,
  query: '?url',
  import: 'default',
})

export const getSkillIconUrl = (name: string, iconUrl?: string): string => {
  if (!name) return ''
  // 1. 优先使用后端提供的 GW2 CDN URL
  if (iconUrl && iconUrl.startsWith('http')) {
    return iconUrl
  }
  // 2. Fallback：尝试本地 PNG 缓存
  const cleanName = name.replace(/^"|"$/g, '').trim()
  const key = `/src/assets/images/skills/${cleanName}.png`
  return (skillIcons[key] as string) || ''
}
