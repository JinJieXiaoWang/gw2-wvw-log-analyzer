/**
 * 滚动加载组件类型定义
 * 功能：定义滚动加载相关的类型、接口和常量
 * 作者：帅姐姐
 * 创建日期：2026-05-11
 */

export type ScrollDirection = 'down' | 'up'

export type LoadStatus = 'idle' | 'loading' | 'success' | 'error' | 'nomore'

export interface InfiniteScrollOptions {
  distance?: number
  direction?: ScrollDirection
  immediate?: boolean
  disabled?: boolean
  rootMargin?: string
  threshold?: number | number[]
}

export interface LoadMoreOptions {
  threshold?: number
  disabled?: boolean
}

export interface ScrollState {
  isLoading: boolean
  isError: boolean
  hasMore: boolean
  error: Error | null
  loadedCount: number
}

export interface ScrollEvent {
  scrollTop: number
  scrollLeft: number
  scrollHeight: number
  clientHeight: number
  scrollPercentage: number
}

export const DEFAULT_SCROLL_OPTIONS: Required<InfiniteScrollOptions> = {
  distance: 200,
  direction: 'down',
  immediate: false,
  disabled: false,
  rootMargin: '0px',
  threshold: 0
}

export const DEFAULT_LOAD_MORE_OPTIONS: Required<LoadMoreOptions> = {
  threshold: 200,
  disabled: false
}

export interface UseInfiniteScrollReturn {
  isLoading: import('vue').Ref<boolean>
  isError: import('vue').Ref<boolean>
  hasMore: import('vue').Ref<boolean>
  error: import('vue').Ref<Error | null>
  loadMore: () => Promise<void>
  reset: () => void
  scrollState: import('vue').ComputedRef<ScrollState>
}

export interface UseLoadMoreReturn {
  isLoading: import('vue').Ref<boolean>
  isError: import('vue').Ref<boolean>
  hasMore: import('vue').Ref<boolean>
  error: import('vue').Ref<Error | null>
  loadMore: () => Promise<void>
  reset: () => void
  scrollState: import('vue').ComputedRef<ScrollState>
}
