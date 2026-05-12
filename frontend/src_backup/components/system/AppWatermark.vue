<template>
  <div ref="hostRef" />
</template>

<script setup lang="ts">
/**
 * AppWatermark - 全局页面水印组件（防篡改版）
 * 功能：根据系统设置在全站显示倾斜文字水印，带 MutationObserver 防删除
 * 更新日期：2026-05-05
 */

import { computed, watch, onMounted, onUnmounted, ref } from 'vue'
import { storeToRefs } from 'pinia'
import { useSettingsStore } from '@/store/system/settings'

const settingsStore = useSettingsStore()
const { settings } = storeToRefs(settingsStore)

const hostRef = ref<HTMLDivElement>()

const effectiveEnabled = computed(() => settings.value.watermarkEnabled)
const effectiveText = computed(() => {
  const text = settings.value.watermarkText?.trim()
  if (text) return text
  const date = new Date().toLocaleDateString('zh-CN')
  return `GW2-APEX ${date}`
})

// 检测当前是否为深色模式
function isDarkMode(): boolean {
  return document.documentElement.classList.contains('dark') ||
    window.matchMedia('(prefers-color-scheme: dark)').matches
}

// 根据主题返回水印颜色
function getWatermarkColor(): string {
  // 深色主题用偏亮的灰，浅色主题用偏暗的灰
  return isDarkMode()
    ? 'rgba(200, 205, 215, 0.14)'
    : 'rgba(80, 85, 95, 0.10)'
}

let observer: MutationObserver | null = null
let watermarkId = ''

function generateWatermarkDataUrl(text: string): string {
  const canvas = document.createElement('canvas')
  const ctx = canvas.getContext('2d')!
  const fontSize = 14
  const gapX = 220
  const gapY = 140

  canvas.width = gapX
  canvas.height = gapY

  ctx.clearRect(0, 0, canvas.width, canvas.height)
  ctx.save()
  ctx.translate(gapX / 2, gapY / 2)
  ctx.rotate((-22 * Math.PI) / 180)
  ctx.font = `500 ${fontSize}px ui-sans-serif, system-ui, -apple-system, sans-serif`
  ctx.fillStyle = getWatermarkColor()
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  ctx.fillText(text, 0, 0)
  ctx.restore()

  return canvas.toDataURL('image/png')
}

function createWatermarkElement(text: string): HTMLDivElement {
  const id = `gw2-watermark-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`
  watermarkId = id

  const div = document.createElement('div')
  div.id = id
  div.setAttribute('data-watermark', 'true')
  div.style.cssText = `
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    width: 100vw !important;
    height: 100vh !important;
    pointer-events: none !important;
    z-index: 2147483647 !important;
    background-image: url(${generateWatermarkDataUrl(text)}) !important;
    background-repeat: repeat !important;
    user-select: none !important;
    -webkit-user-select: none !important;
    opacity: 1 !important;
    visibility: visible !important;
    display: block !important;
  `
  return div
}

function mountWatermark() {
  if (!effectiveEnabled.value) {
    removeWatermark()
    return
  }

  // 如果已存在，先移除旧的
  removeWatermark()

  const el = createWatermarkElement(effectiveText.value)
  document.body.appendChild(el)

  // 启动 MutationObserver 防删除
  startObserver(el)
}

function removeWatermark() {
  if (observer) {
    observer.disconnect()
    observer = null
  }
  if (watermarkId) {
    const old = document.getElementById(watermarkId)
    if (old) old.remove()
    watermarkId = ''
  }
  // 兜底：清除所有带 data-watermark 属性的元素
  document.querySelectorAll('[data-watermark="true"]').forEach((n) => n.remove())
}

function startObserver(target: HTMLDivElement) {
  if (observer) observer.disconnect()

  observer = new MutationObserver((mutations) => {
    for (const mutation of mutations) {
      if (mutation.type === 'childList') {
        const removed = Array.from(mutation.removedNodes)
        if (removed.some((n) => n === target || (n as Element).id === watermarkId)) {
          // 水印被删除了，立即重新创建
          setTimeout(() => mountWatermark(), 0)
          return
        }
      }
      if (mutation.type === 'attributes' && mutation.target === target) {
        // 属性被修改，强制恢复
        const style = target.style
        if (style.display === 'none') style.display = 'block'
        if (style.visibility === 'hidden') style.visibility = 'visible'
        if (style.opacity === '0') style.opacity = '1'
        if (parseInt(style.zIndex || '0') < 9999) style.zIndex = '2147483647'
      }
    }
  })

  observer.observe(document.body, {
    childList: true,
    subtree: false,
    attributes: true,
    attributeFilter: ['style', 'class', 'id']
  })
}

// 监听设置变化
watch(
  () => [settings.value.watermarkEnabled, settings.value.watermarkText],
  () => {
    if (effectiveEnabled.value) {
      mountWatermark()
    } else {
      removeWatermark()
    }
  },
  { deep: true }
)

// 监听主题变化，自动调整水印颜色
const themeMedia = window.matchMedia('(prefers-color-scheme: dark)')
function handleThemeChange() {
  if (effectiveEnabled.value) mountWatermark()
}
themeMedia.addEventListener?.('change', handleThemeChange)

onMounted(() => {
  if (effectiveEnabled.value) mountWatermark()
})

onUnmounted(() => {
  removeWatermark()
  themeMedia.removeEventListener?.('change', handleThemeChange)
})
</script>
