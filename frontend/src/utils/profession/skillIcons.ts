/**
 * 技能图标路径工具
 * 图标文件存放在 public/images/skills/ 目录下，通过 URL 直接引用
 * 避免将大量 PNG 打包到 JS chunk 中
 */

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
  if (cleanName) {
    return `/images/skills/${cleanName}.png`
  }

  // 2. Fallback：使用后端提供的 GW2 CDN URL
  if (iconUrl && iconUrl.startsWith('http')) {
    return iconUrl
  }

  return ''
}
