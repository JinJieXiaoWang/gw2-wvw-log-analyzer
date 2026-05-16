/**
 * 图片颜色动态调整工具模块
 * 功能：根据当前系统UI主题动态调整图片颜色，确保图片与主题视觉一致
 * 作者：帅姐姐
 * 创建日期：2026-05-01
 * 
 * 实现原理：
 * 1. 使用CSS filter的brightness、saturate、hue-rotate等滤镜调整图片颜色
 * 2. 根据当前主题的主色调和背景色计算最佳适配参数
 * 3. 支持亮色/暗色模式自动切换
 * 4. 使用SVG滤镜实现更精确的颜色映射
 */

import { ThemeService } from '@/services/system/themeService'
import type { ThemeConfig } from '@/config/themes'

/**
 * 图片颜色调整模式
 */
export type ImageColorMode = 'auto' | 'light' | 'dark' | 'primary' | 'none'

/**
 * 图片颜色调整参数
 */
export interface ImageColorParams {
  /** 亮度调整 (0-2, 1为原始) */
  brightness?: number
  /** 对比度调整 (0-2, 1为原始) */
  contrast?: number
  /** 饱和度调整 (0-2, 1为原始) */
  saturate?: number
  /** 色相旋转 (0-360) */
  hueRotate?: number
  /** 灰度转换 (0-1, 1为完全灰度) */
  grayscale?: number
  /** 反转颜色 (0-1, 1为完全反转) */
  invert?: number
  /** 混合叠加颜色 */
  overlayColor?: string
  /** 混合模式 */
  blendMode?: string
}

/**
 * 主题适配配置
 */
export interface ThemeAdaptationConfig {
  /** 目标颜色模式 */
  mode: ImageColorMode
  /** 是否启用亮度反转（暗色主题下白色图片需要反转） */
  invertForDark?: boolean
  /** 是否启用颜色叠加 */
  applyOverlay?: boolean
  /** 自定义叠加颜色 */
  customOverlayColor?: string
}

/**
 * 从hex颜色提取RGB值
 */
function hexToRgb(hex: string): { r: number; g: number; b: number } | null {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex)
  return result
    ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16)
      }
    : null
}

/**
 * RGB转HSL
 */
function rgbToHsl(r: number, g: number, b: number): { h: number; s: number; l: number } {
  r /= 255
  g /= 255
  b /= 255

  const max = Math.max(r, g, b)
  const min = Math.min(r, g, b)
  let h = 0
  let s = 0
  const l = (max + min) / 2

  if (max !== min) {
    const d = max - min
    s = l > 0.5 ? d / (2 - max - min) : d / (max + min)

    switch (max) {
      case r:
        h = ((g - b) / d + (g < b ? 6 : 0)) / 6
        break
      case g:
        h = ((b - r) / d + 2) / 6
        break
      case b:
        h = ((r - g) / d + 4) / 6
        break
    }
  }

  return { h: h * 360, s: s * 100, l: l * 100 }
}

/**
 * 计算主题适配参数
 * 根据主题的背景色和主色调计算最佳的图片调整参数
 */
export function calculateThemeAdaptationParams(
  theme: ThemeConfig,
  mode: ImageColorMode = 'auto'
): ImageColorParams {
  const { colors } = theme
  
  // 判断是否为暗色主题
  const isDarkTheme = isDarkMode(theme)
  
  // 根据模式确定最终使用的模式
  let finalMode = mode
  if (mode === 'auto') {
    finalMode = isDarkTheme ? 'dark' : 'light'
  }

  // 基础参数
  const params: ImageColorParams = {
    brightness: 1,
    contrast: 1,
    saturate: 1,
    hueRotate: 0,
    grayscale: 0,
    invert: 0
  }

  switch (finalMode) {
    case 'dark':
      // 暗色主题：降低亮度，增加对比度
      params.brightness = 0.9
      params.contrast = 1.1
      params.saturate = 1.15
      // 对于以白色/浅色为主的图片（如职业图标），可能需要反转
      break

    case 'light':
      // 亮色主题：略微降低饱和度
      params.brightness = 1.05
      params.contrast = 0.95
      params.saturate = 0.95
      break

    case 'primary': {
      // 主色调模式：将图片色调向主题主色偏移
      const primaryRgb = hexToRgb(colors.primary)
      if (primaryRgb) {
        const hsl = rgbToHsl(primaryRgb.r, primaryRgb.g, primaryRgb.b)
        params.hueRotate = hsl.h
        params.saturate = 1.3
        params.contrast = 1.1
      }
      break
    }

    case 'none':
    default:
      // 不做任何调整
      break
  }

  return params
}

/**
 * 判断主题是否为暗色模式
 */
export function isDarkMode(theme: ThemeConfig): boolean {
  const { colors } = theme
  
  // 通过背景色的亮度判断
  const bgRgb = hexToRgb(colors.bg)
  if (bgRgb) {
    // 计算相对亮度
    const luminance = (0.299 * bgRgb.r + 0.587 * bgRgb.g + 0.114 * bgRgb.b) / 255
    return luminance < 0.5
  }
  
  // 默认为暗色主题
  return true
}

/**
 * 生成CSS filter字符串
 */
export function generateCssFilter(params: ImageColorParams): string {
  const filters: string[] = []
  
  if (params.brightness !== undefined && params.brightness !== 1) {
    filters.push(`brightness(${params.brightness})`)
  }
  
  if (params.contrast !== undefined && params.contrast !== 1) {
    filters.push(`contrast(${params.contrast})`)
  }
  
  if (params.saturate !== undefined && params.saturate !== 1) {
    filters.push(`saturate(${params.saturate})`)
  }
  
  if (params.hueRotate !== undefined && params.hueRotate !== 0) {
    filters.push(`hue-rotate(${params.hueRotate}deg)`)
  }
  
  if (params.grayscale !== undefined && params.grayscale !== 0) {
    filters.push(`grayscale(${params.grayscale})`)
  }
  
  if (params.invert !== undefined && params.invert !== 0) {
    filters.push(`invert(${params.invert})`)
  }
  
  return filters.length > 0 ? filters.join(' ') : 'none'
}

/**
 * 生成SVG滤镜定义
 */
export function generateSvgFilterDefinition(params: ImageColorParams): string {
  const filterParts: string[] = []
  
  if (params.brightness !== undefined && params.brightness !== 1) {
    filterParts.push(`<feComponentTransfer in="SourceGraphic"><feFuncR type="linear" slope="${params.brightness}"/><feFuncG type="linear" slope="${params.brightness}"/><feFuncB type="linear" slope="${params.brightness}"/></feComponentTransfer>`)
  }
  
  if (params.contrast !== undefined && params.contrast !== 1) {
    const intercept = (1 - params.contrast) / 2
    filterParts.push(`<feComponentTransfer><feFuncR type="linear" slope="${params.contrast}" intercept="${intercept}"/><feFuncG type="linear" slope="${params.contrast}" intercept="${intercept}"/><feFuncB type="linear" slope="${params.contrast}" intercept="${intercept}"/></feComponentTransfer>`)
  }
  
  if (params.saturate !== undefined && params.saturate !== 1) {
    filterParts.push(`<feColorMatrix type="saturate" values="${params.saturate}"/>`)
  }
  
  if (params.hueRotate !== undefined && params.hueRotate !== 0) {
    filterParts.push(`<feColorMatrix type="hueRotate" values="${params.hueRotate}"/>`)
  }
  
  if (params.grayscale !== undefined && params.grayscale !== 0) {
    filterParts.push(`<feColorMatrix type="matrix" values="${1 - params.grayscale * 0.2989} ${-params.grayscale * 0.587} ${-params.grayscale * 0.114} 0 0 ${-params.grayscale * 0.2989} ${1 - params.grayscale * 0.587} ${-params.grayscale * 0.114} 0 0 ${-params.grayscale * 0.2989} ${-params.grayscale * 0.587} ${1 - params.grayscale * 0.114} 0 0 0 0 0 1 0"/>`)
  }
  
  if (params.invert !== undefined && params.invert !== 0) {
    filterParts.push(`<feComponentTransfer><feFuncR type="table" tableValues="${params.invert} ${1 - params.invert}"/><feFuncG type="table" tableValues="${params.invert} ${1 - params.invert}"/><feFuncB type="table" tableValues="${params.invert} ${1 - params.invert}"/></feComponentTransfer>`)
  }
  
  return filterParts.join('\n')
}

/**
 * 获取主题适配的CSS filter
 */
export function getThemeAdaptedFilter(mode: ImageColorMode = 'auto'): string {
  const theme = ThemeService.getCurrentTheme()
  const params = calculateThemeAdaptationParams(theme, mode)
  return generateCssFilter(params)
}

/**
 * 主题适配的图片样式对象
 */
export function getThemeAdaptedStyle(mode: ImageColorMode = 'auto'): Record<string, string> {
  const theme = ThemeService.getCurrentTheme()
  const params = calculateThemeAdaptationParams(theme, mode)
  
  return {
    filter: generateCssFilter(params)
  }
}

/**
 * 带主题适配的图像URL处理
 * 为图像添加主题适配的query参数
 */
export function adaptImageUrlWithTheme(
  originalUrl: string,
  mode: ImageColorMode = 'auto'
): string {
  if (!originalUrl) return originalUrl
  
  // 对于外部URL或data URL，不做处理
  if (originalUrl.startsWith('http') || originalUrl.startsWith('data:')) {
    return originalUrl
  }
  
  // 添加主题参数
  const theme = ThemeService.getCurrentTheme()
  const params = calculateThemeAdaptationParams(theme, mode)
  const filterStr = generateCssFilter(params)

  // 检查URL是否已有参数
  const separator = originalUrl.includes('?') ? '&' : '?'

  return `${originalUrl}${separator}theme_filter=${encodeURIComponent(filterStr)}`
}

/**
 * 计算亮度对比度适配
 * 根据图片的平均亮度调整，使其在当前主题背景下更清晰
 */
export function calculateContrastAdaptation(theme: ThemeConfig): ImageColorParams {
  const { colors } = theme
  const isDark = isDarkMode(theme)
  
  // 获取背景色的亮度
  const bgRgb = hexToRgb(colors.bg)
  if (!bgRgb) {
    return {}
  }
  
  const bgLuminance = (0.299 * bgRgb.r + 0.587 * bgRgb.g + 0.114 * bgRgb.b) / 255
  
  // 计算需要的对比度调整
  let contrast = 1
  let brightness = 1
  
  if (isDark) {
    // 暗色背景：提高对比度
    if (bgLuminance < 0.2) {
      contrast = 1.2
      brightness = 0.95
    } else if (bgLuminance < 0.1) {
      contrast = 1.3
      brightness = 0.9
    }
  } else {
    // 亮色背景：略微降低对比度
    if (bgLuminance > 0.8) {
      contrast = 0.95
      brightness = 1.05
    }
  }
  
  return { contrast, brightness }
}

/**
 * 职业图标专用的主题适配参数
 * 职业图标通常是白色/浅色背景的透明PNG，需要特殊处理
 */
export function getProfessionIconAdaptation(theme: ThemeConfig): ImageColorParams {
  const isDark = isDarkMode(theme)
  
  // 职业图标为白色图标，在暗色背景下需要反转才能正常显示
  if (isDark) {
    // 暗色主题：反转白色图标使其可见
    return {
      brightness: 1.1,
      contrast: 1.2,
      saturate: 1.2,
      invert: 1  // 完全反转白色为黑色
    }
  } else {
    // 亮色主题：略微降低亮度以减少刺眼感
    return {
      brightness: 0.9,
      contrast: 1.1,
      saturate: 1.05,
      invert: 0
    }
  }
}

/**
 * 获取职业图标的CSS filter
 */
export function getProfessionIconFilter(): string {
  const theme = ThemeService.getCurrentTheme()
  const params = getProfessionIconAdaptation(theme)
  return generateCssFilter(params)
}

/**
 * 获取职业图标的SVG滤镜ID
 */
export function getProfessionIconSvgFilterId(): string {
  const theme = ThemeService.getCurrentTheme()
  const isDark = isDarkMode(theme)
  return isDark ? 'prof-icon-invert' : 'prof-icon-normal'
}

/**
 * 生成职业图标的SVG滤镜定义（内联SVG用）
 */
export function generateProfessionIconSvgFilter(): string {
  const theme = ThemeService.getCurrentTheme()
  const params = getProfessionIconAdaptation(theme)
  const filterContent = generateSvgFilterDefinition(params)
  
  return `
    <filter id="prof-icon-adapt">
      ${filterContent}
    </filter>
  `
}

/**
 * 创建主题适配的图像元素
 * 使用Canvas重新绘制主题适配后的图像
 */
export function createThemeAdaptedImage(
  originalSrc: string,
  mode: ImageColorMode = 'auto'
): Promise<string> {
  return new Promise((resolve) => {
    const img = new Image()
    img.crossOrigin = 'anonymous'
    
    img.onload = () => {
      try {
        const canvas = document.createElement('canvas')
        canvas.width = img.width
        canvas.height = img.height
        
        const ctx = canvas.getContext('2d')
        if (!ctx) {
          resolve(originalSrc)
          return
        }
        
        const theme = ThemeService.getCurrentTheme()
        const params = calculateThemeAdaptationParams(theme, mode)
        
        // 应用滤镜
        ctx.filter = generateCssFilter(params)
        ctx.drawImage(img, 0, 0)
        
        // 转换为Data URL
        resolve(canvas.toDataURL('image/png'))
      } catch (error) {
        console.error('[ImageColorUtils] 创建主题适配图像失败', error)
        resolve(originalSrc)
      }
    }
    
    img.onerror = () => {
      console.error('[ImageColorUtils] 加载图像失败', originalSrc)
      resolve(originalSrc)
    }
    
    img.src = originalSrc
  })
}

/**
 * 预加载并缓存主题适配图像
 */
const adaptedImageCache = new Map<string, string>()

export async function preloadAdaptedImage(
  originalSrc: string,
  mode: ImageColorMode = 'auto'
): Promise<string> {
  const cacheKey = `${originalSrc}:${mode}`
  
  if (adaptedImageCache.has(cacheKey)) {
    return adaptedImageCache.get(cacheKey)!
  }
  
  const adaptedSrc = await createThemeAdaptedImage(originalSrc, mode)
  adaptedImageCache.set(cacheKey, adaptedSrc)
  
  return adaptedSrc
}

/**
 * 清除图像缓存
 */
export function clearImageCache(): void {
  adaptedImageCache.clear()
}

/**
 * 清除指定图像的缓存
 */
export function clearImageCacheBySrc(src: string): void {
  for (const key of adaptedImageCache.keys()) {
    if (key.startsWith(src)) {
      adaptedImageCache.delete(key)
    }
  }
}

/**
 * 批量预加载图像
 */
export async function preloadAdaptedImages(
  images: { src: string; mode?: ImageColorMode }[]
): Promise<void> {
  const promises = images.map(img => preloadAdaptedImage(img.src, img.mode || 'auto'))
  await Promise.all(promises)
}

/**
 * 注册主题变更监听器
 * 当主题变更时自动刷新缓存的适配图像
 */
export function setupThemeChangeListener(onThemeChange?: (theme: ThemeConfig) => void): () => void {
  const originalApplyTheme = ThemeService.applyTheme.bind(ThemeService)
  
  ThemeService.applyTheme = async (themeId: string, isPreview: boolean = false) => {
    await originalApplyTheme(themeId, isPreview)
    
    // 清除缓存
    clearImageCache()
    
    // 触发回调
    const newTheme = ThemeService.getCurrentTheme()
    onThemeChange?.(newTheme)
  }
  
  // 返回清理函数
  return () => {
    ThemeService.applyTheme = originalApplyTheme
  }
}
