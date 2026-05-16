import { ref, onMounted, onUnmounted } from 'vue'

export interface ScreenshotDetectionOptions {
  /** 检测到截图行为时的回调 */
  onDetect?: () => void
  /** 是否监听 PrintScreen 按键 */
  detectPrintScreen?: boolean
  /** 是否监听窗口失焦（某些截图工具会触发） */
  detectBlur?: boolean
  /** 是否监听剪贴板变化（部分浏览器支持） */
  detectClipboard?: boolean
  /** 是否在开发者工具打开时提示 */
  detectDevTools?: boolean
}

/**
 * 截图行为检测 Composable
 *
 * ⚠️ 重要提示：
 * 纯 Web/H5 技术**无法真正阻止**操作系统级别的截图（如手机电源键+音量键、
 * PrintScreen、系统截图工具等）。此工具只能检测部分截图相关行为并给出提示。
 *
 * 如需真正禁止截图，必须借助原生 App 能力：
 * - Android：WindowManager.LayoutParams.FLAG_SECURE
 * - iOS：App 级别无直接禁止 API，可监听截图事件后覆盖内容
 */
export function useScreenshotDetection(options: ScreenshotDetectionOptions = {}) {
  const {
    onDetect,
    detectPrintScreen = true,
    detectBlur = true,
    detectClipboard = false,
    detectDevTools = false
  } = options

  const detected = ref(false)
  let blurTimer: ReturnType<typeof setTimeout> | null = null
  let devToolsTimer: ReturnType<typeof setTimeout> | null = null

  /**
   * 处理 PrintScreen 按键
   */
  const handleKeyDown = (e: KeyboardEvent) => {
    // PrintScreen 键
    if (e.key === 'PrintScreen' || e.code === 'PrintScreen') {
      detected.value = true
      onDetect?.()
      return
    }

    // Win+Shift+S (Windows 截图工具)
    if (e.key === 'S' && e.shiftKey && (e.metaKey || e.ctrlKey)) {
      // 这个组合键通常被系统拦截，前端可能收不到
    }
  }

  /**
   * 处理窗口失焦
   * 某些截图工具（如 QQ 截图、微信截图）在激活时会令当前窗口失焦
   */
  const handleBlur = () => {
    if (!detectBlur) return

    // 延迟检测，排除正常的 Tab 切换
    blurTimer = setTimeout(() => {
      // 如果窗口失焦超过 300ms，可能是截图工具激活
      if (document.hidden || document.visibilityState !== 'visible') {
        return
      }
      // 这里可以认为是截图工具激活了
      // 但由于误报率高，建议只用于记录日志，不做强提示
    }, 300)
  }

  const handleFocus = () => {
    if (blurTimer) {
      clearTimeout(blurTimer)
      blurTimer = null
    }
  }

  /**
   * 处理剪贴板变化
   * 部分浏览器支持 clipboardchange 事件
   */
  const handleClipboardChange = async () => {
    if (!detectClipboard) return
    try {
      // 尝试读取剪贴板，如果包含图片则可能是截图
      const items = await navigator.clipboard.read()
      for (const item of items) {
        if (item.types.some((t) => t.startsWith('image/'))) {
          detected.value = true
          onDetect?.()
          break
        }
      }
    } catch {
      // 没有剪贴板权限则静默失败
    }
  }

  /**
   * 检测开发者工具（F12 / Ctrl+Shift+I / Cmd+Option+I）
   */
  const handleDevToolsKey = (e: KeyboardEvent) => {
    if (!detectDevTools) return
    // F12
    if (e.key === 'F12') {
      detected.value = true
      onDetect?.()
      return
    }
    // Ctrl+Shift+I / Cmd+Option+I
    if (e.key === 'i' && e.shiftKey && (e.ctrlKey || e.metaKey)) {
      detected.value = true
      onDetect?.()
    }
  }

  /**
   * 使用 debugger 技巧检测开发者工具是否打开
   */
  const detectDevToolsOpen = () => {
    if (!detectDevTools) return
    const threshold = 160
    const check = () => {
      const widthThreshold = window.outerWidth - window.innerWidth > threshold
      const heightThreshold = window.outerHeight - window.innerHeight > threshold
      if (widthThreshold || heightThreshold) {
        detected.value = true
        onDetect?.()
      }
    }
    devToolsTimer = setInterval(check, 1000)
  }

  onMounted(() => {
    if (detectPrintScreen) {
      window.addEventListener('keydown', handleKeyDown)
    }
    if (detectBlur) {
      window.addEventListener('blur', handleBlur)
      window.addEventListener('focus', handleFocus)
    }
    if (detectClipboard && 'clipboard' in navigator) {
      navigator.clipboard?.addEventListener?.('clipboardchange', handleClipboardChange)
    }
    if (detectDevTools) {
      window.addEventListener('keydown', handleDevToolsKey)
      detectDevToolsOpen()
    }
  })

  onUnmounted(() => {
    window.removeEventListener('keydown', handleKeyDown)
    window.removeEventListener('keydown', handleDevToolsKey)
    window.removeEventListener('blur', handleBlur)
    window.removeEventListener('focus', handleFocus)
    navigator.clipboard?.removeEventListener?.('clipboardchange', handleClipboardChange)
    if (blurTimer) clearTimeout(blurTimer)
    if (devToolsTimer) clearInterval(devToolsTimer)
  })

  return {
    detected
  }
}

/**
 * 更实用的方案：在检测到潜在截图行为时，自动覆盖一层高透明度遮罩
 * 这样截图出来的内容会被模糊/遮挡
 */
export function useScreenshotShield() {
  const shieldVisible = ref(false)
  let shieldTimer: ReturnType<typeof setTimeout> | null = null

  const showShield = (duration = 3000) => {
    shieldVisible.value = true
    if (shieldTimer) clearTimeout(shieldTimer)
    shieldTimer = setTimeout(() => {
      shieldVisible.value = false
    }, duration)
  }

  const hideShield = () => {
    shieldVisible.value = false
    if (shieldTimer) clearTimeout(shieldTimer)
  }

  onUnmounted(() => {
    if (shieldTimer) clearTimeout(shieldTimer)
  })

  return {
    shieldVisible,
    showShield,
    hideShield
  }
}
