/**
 * 滚动加载Composable
 * 功能：提供滚动加载的逻辑封装，支持自动加载和手动加载两种模式
 * 作者：System
 * 创建日期：2026-05-11
 */

import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import type { ScrollState, InfiniteScrollOptions, ScrollEvent } from '@/types/scroll'
import { DEFAULT_SCROLL_OPTIONS } from '@/types/scroll'
import { supportsIntersectionObserver } from '@/utils/core/performance'

export function useInfiniteScroll(
  loadCallback: () => Promise<void>,
  options: InfiniteScrollOptions = {}
) {
  const opts = { ...DEFAULT_SCROLL_OPTIONS, ...options }
  
  const isLoading = ref(false)
  const isError = ref(false)
  const hasMore = ref(true)
  const error = ref<Error | null>(null)
  const loadedCount = ref(0)
  
  const scrollContainerRef = ref<HTMLElement | null>(null)
  const sentinelRef = ref<HTMLElement | null>(null)
  let intersectionObserver: IntersectionObserver | null = null

  const scrollState = computed<ScrollState>(() => ({
    isLoading: isLoading.value,
    isError: isError.value,
    hasMore: hasMore.value,
    error: error.value,
    loadedCount: loadedCount.value
  }))

  const createObserver = () => {
    if (!supportsIntersectionObserver()) {
      console.warn('浏览器不支持IntersectionObserver，将使用scroll事件')
      return null
    }

    intersectionObserver = new IntersectionObserver(
      (entries) => {
        const [entry] = entries
        if (entry.isIntersecting && hasMore.value && !isLoading.value && !opts.disabled) {
          loadMore()
        }
      },
      {
        root: scrollContainerRef.value,
        rootMargin: opts.rootMargin,
        threshold: opts.threshold
      }
    )

    return intersectionObserver
  }

  const loadMore = async () => {
    if (isLoading.value || !hasMore.value || opts.disabled) {
      return
    }

    isLoading.value = true
    isError.value = false
    error.value = null

    try {
      await loadCallback()
      loadedCount.value++
    } catch (e) {
      isError.value = true
      error.value = e instanceof Error ? e : new Error(String(e))
    } finally {
      isLoading.value = false
    }
  }

  const reset = () => {
    isLoading.value = false
    isError.value = false
    hasMore.value = true
    error.value = null
    loadedCount.value = 0
  }

  const setHasMore = (value: boolean) => {
    hasMore.value = value
  }

  const handleScroll = (event: Event) => {
    const target = event.target as HTMLElement
    const { scrollTop, scrollHeight, clientHeight } = target
    const scrollPercentage = (scrollTop / (scrollHeight - clientHeight)) * 100

    if (opts.direction === 'down') {
      const distanceFromBottom = scrollHeight - scrollTop - clientHeight
      if (distanceFromBottom <= opts.distance && hasMore.value && !isLoading.value && !opts.disabled) {
        loadMore()
      }
    } else {
      if (scrollTop <= opts.distance && hasMore.value && !isLoading.value && !opts.disabled) {
        loadMore()
      }
    }
  }

  const handleScrollEvent = (event: Event): ScrollEvent => {
    const target = event.target as HTMLElement
    return {
      scrollTop: target.scrollTop,
      scrollLeft: target.scrollLeft,
      scrollHeight: target.scrollHeight,
      clientHeight: target.clientHeight,
      scrollPercentage: target.scrollHeight > 0 
        ? (target.scrollTop / (target.scrollHeight - target.clientHeight)) * 100 
        : 0
    }
  }

  const initObserver = () => {
    if (sentinelRef.value && !intersectionObserver) {
      intersectionObserver = createObserver()
      if (intersectionObserver) {
        intersectionObserver.observe(sentinelRef.value)
      }
    }
  }

  const destroyObserver = () => {
    if (intersectionObserver) {
      intersectionObserver.disconnect()
      intersectionObserver = null
    }
  }

  watch(() => opts.disabled, (disabled) => {
    if (disabled) {
      destroyObserver()
    } else {
      initObserver()
    }
  })

  onMounted(() => {
    if (opts.immediate) {
      loadMore()
    }
  })

  onUnmounted(() => {
    destroyObserver()
  })

  return {
    isLoading,
    isError,
    hasMore,
    error,
    loadedCount,
    scrollState,
    scrollContainerRef,
    sentinelRef,
    loadMore,
    reset,
    setHasMore,
    handleScroll,
    handleScrollEvent,
    initObserver,
    destroyObserver
  }
}

export function useLoadMore(
  loadCallback: () => Promise<void>,
  options: { threshold?: number; disabled?: boolean } = {}
) {
  const { threshold = 200, disabled = false } = options

  const isLoading = ref(false)
  const isError = ref(false)
  const hasMore = ref(true)
  const error = ref<Error | null>(null)
  const loadedCount = ref(0)

  const scrollState = computed<ScrollState>(() => ({
    isLoading: isLoading.value,
    isError: isError.value,
    hasMore: hasMore.value,
    error: error.value,
    loadedCount: loadedCount.value
  }))

  const loadMore = async () => {
    if (isLoading.value || !hasMore.value || disabled) {
      return
    }

    isLoading.value = true
    isError.value = false
    error.value = null

    try {
      await loadCallback()
      loadedCount.value++
    } catch (e) {
      isError.value = true
      error.value = e instanceof Error ? e : new Error(String(e))
    } finally {
      isLoading.value = false
    }
  }

  const reset = () => {
    isLoading.value = false
    isError.value = false
    hasMore.value = true
    error.value = null
    loadedCount.value = 0
  }

  const setHasMore = (value: boolean) => {
    hasMore.value = value
  }

  return {
    isLoading,
    isError,
    hasMore,
    error,
    loadedCount,
    scrollState,
    loadMore,
    reset,
    setHasMore
  }
}

export function useScrollPosition() {
  const scrollTop = ref(0)
  const scrollLeft = ref(0)
  const scrollHeight = ref(0)
  const clientHeight = ref(0)

  const handleScroll = (event: Event) => {
    const target = event.target as HTMLElement
    scrollTop.value = target.scrollTop
    scrollLeft.value = target.scrollLeft
    scrollHeight.value = target.scrollHeight
    clientHeight.value = target.clientHeight
  }

  const scrollTo = (top: number, left?: number) => {
    if (scrollContainerRef.value) {
      scrollContainerRef.value.scrollTop = top
      if (left !== undefined) {
        scrollContainerRef.value.scrollLeft = left
      }
    }
  }

  const scrollContainerRef = ref<HTMLElement | null>(null)

  return {
    scrollTop,
    scrollLeft,
    scrollHeight,
    clientHeight,
    scrollContainerRef,
    handleScroll,
    scrollTo
  }
}
