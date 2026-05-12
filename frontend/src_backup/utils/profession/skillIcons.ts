/**
 * 技能图标路径映射
 * 使用 Vite import.meta.glob 在构建时收集所有技能图标路径
 * 策略：优先使用本地 PNG 图标（性能更好），fallback 到后端提供的 GW2 CDN URL
 */
const skillIcons = import.meta.glob('@/assets/images/skills/*.png', {
  eager: true,
  query: '?url',
  import: 'default',
})

/**
 * 获取技能图标URL
 * @param name 技能名称（用于查找本地图标）
 * @param iconUrl 后端提供的CDN URL（作为fallback）
 * @returns 图标URL
 */
export const getSkillIconUrl = (name: string, iconUrl?: string): string => {
  if (!name) return ''
  
  // 1. 优先使用本地 PNG 图标（性能更好，无网络请求）
  const cleanName = name.replace(/^"|"$/g, '').trim()
  const localKey = `/src/assets/images/skills/${cleanName}.png`
  const localUrl = skillIcons[localKey] as string
  if (localUrl) {
    return localUrl
  }
  
  // 2. Fallback：使用后端提供的 GW2 CDN URL
  if (iconUrl && iconUrl.startsWith('http')) {
    return iconUrl
  }
  
  // 3. 最终 fallback：返回空字符串
  return ''
}

/**
 * 检查技能图标是否存在于本地
 * @param name 技能名称
 * @returns 是否存在本地图标
 */
export const hasLocalSkillIcon = (name: string): boolean => {
  if (!name) return false
  const cleanName = name.replace(/^"|"$/g, '').trim()
  const key = `/src/assets/images/skills/${cleanName}.png`
  return !!skillIcons[key]
}

/**
 * 获取所有本地技能图标名称列表
 * @returns 技能名称数组
 */
export const getLocalSkillIconNames = (): string[] => {
  return Object.keys(skillIcons).map(key => {
    // 从路径中提取技能名称：/src/assets/images/skills/xxx.png -> xxx
    const match = key.match(/\/skills\/(.+)\.png$/)
    return match ? match[1] : ''
  }).filter(Boolean)
}
