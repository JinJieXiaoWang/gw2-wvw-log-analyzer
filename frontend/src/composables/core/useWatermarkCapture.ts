import html2canvas from 'html2canvas'
import { useSettingsStore } from '@/store/system/settings'

export interface CaptureOptions {
  /** 截图元素，默认 document.body */
  element?: HTMLElement
  /** 保存文件名，默认 screenshot-{timestamp}.png */
  filename?: string
  /** 是否强制添加水印（忽略设置） */
  forceWatermark?: boolean
  /** 自定义水印文字（优先级高于设置） */
  customWatermarkText?: string
  /** html2canvas 配置 */
  canvasOptions?: Partial<Parameters<typeof html2canvas>[1]>
}

/**
 * 截图并自动添加水印
 * @returns 截图的 DataURL
 */
export async function captureWithWatermark(options: CaptureOptions = {}): Promise<string> {
  const {
    element = document.body,
    filename,
    forceWatermark = false,
    customWatermarkText,
    canvasOptions = {}
  } = options

  const settingsStore = useSettingsStore()
  const settings = settingsStore.settings

  // 1. 使用 html2canvas 截图
  const canvas = await html2canvas(element, {
    scale: 2,
    useCORS: true,
    allowTaint: true,
    backgroundColor: null,
    logging: false,
    ...canvasOptions
  })

  const ctx = canvas.getContext('2d')
  if (!ctx) {
    throw new Error('无法获取 canvas 上下文')
  }

  // 2. 判断是否需要添加水印
  const shouldAddWatermark = forceWatermark || settings.watermarkScreenshotEnabled

  if (shouldAddWatermark) {
    const watermarkText = customWatermarkText?.trim()
      || settings.watermarkText?.trim()
      || `GW2-APEX · ${new Date().toLocaleString('zh-CN')}`

    const timestamp = new Date().toLocaleString('zh-CN')
    const fullText = `${watermarkText} · ${timestamp}`

    // 绘制水印背景条（增加可读性）
    const padding = 16
    const fontSize = 16
    ctx.font = `500 ${fontSize}px ui-sans-serif, system-ui, -apple-system, sans-serif`
    const textMetrics = ctx.measureText(fullText)
    const textWidth = textMetrics.width
    const barWidth = textWidth + padding * 2
    const barHeight = fontSize + padding
    const x = canvas.width - barWidth - 16
    const y = canvas.height - barHeight - 16

    // 半透明背景
    ctx.save()
    ctx.fillStyle = 'rgba(0, 0, 0, 0.45)'
    ctx.beginPath()
    ctx.roundRect(x, y, barWidth, barHeight, 8)
    ctx.fill()

    // 文字
    ctx.fillStyle = 'rgba(255, 255, 255, 0.85)'
    ctx.textBaseline = 'middle'
    ctx.textAlign = 'left'
    ctx.fillText(fullText, x + padding, y + barHeight / 2)
    ctx.restore()
  }

  // 3. 生成 DataURL
  const dataUrl = canvas.toDataURL('image/png')

  // 4. 自动下载（如果提供了文件名）
  if (filename) {
    const link = document.createElement('a')
    link.download = filename
    link.href = dataUrl
    link.click()
  }

  return dataUrl
}

/**
 * 纯函数：在已有 Canvas 上绘制水印
 */
export function drawWatermarkOnCanvas(
  canvas: HTMLCanvasElement,
  text: string,
  options: {
    position?: 'bottom-right' | 'bottom-left' | 'top-right' | 'top-left' | 'center'
    fontSize?: number
    color?: string
    bgColor?: string
    alpha?: number
  } = {}
): HTMLCanvasElement {
  const ctx = canvas.getContext('2d')
  if (!ctx) return canvas

  const {
    position = 'bottom-right',
    fontSize = 16,
    color = 'rgba(255, 255, 255, 0.85)',
    bgColor = 'rgba(0, 0, 0, 0.45)',
    alpha = 1
  } = options

  ctx.save()
  ctx.globalAlpha = alpha

  const padding = 16
  ctx.font = `500 ${fontSize}px ui-sans-serif, system-ui, -apple-system, sans-serif`
  const textMetrics = ctx.measureText(text)
  const textWidth = textMetrics.width
  const barWidth = textWidth + padding * 2
  const barHeight = fontSize + padding

  let x = 0
  let y = 0

  const margin = 16
  switch (position) {
    case 'bottom-right':
      x = canvas.width - barWidth - margin
      y = canvas.height - barHeight - margin
      break
    case 'bottom-left':
      x = margin
      y = canvas.height - barHeight - margin
      break
    case 'top-right':
      x = canvas.width - barWidth - margin
      y = margin
      break
    case 'top-left':
      x = margin
      y = margin
      break
    case 'center':
      x = (canvas.width - barWidth) / 2
      y = (canvas.height - barHeight) / 2
      break
  }

  // 背景
  ctx.fillStyle = bgColor
  ctx.beginPath()
  ctx.roundRect(x, y, barWidth, barHeight, 8)
  ctx.fill()

  // 文字
  ctx.fillStyle = color
  ctx.textBaseline = 'middle'
  ctx.textAlign = 'left'
  ctx.fillText(text, x + padding, y + barHeight / 2)

  ctx.restore()
  return canvas
}
