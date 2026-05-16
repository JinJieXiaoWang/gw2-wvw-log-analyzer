/**
 * 滚动加载组件单元测试
 * 功能：测试useInfiniteScroll和BaseInfiniteScroll组件的功能
 * 作者：System
 * 创建日期：2026-05-11
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { ref, nextTick } from 'vue'
import { mount } from '@vue/test-utils'
import BaseInfiniteScroll from '@/components/common/ui/overlay/BaseInfiniteScroll.vue'
import BaseLoadMore from '@/components/common/ui/overlay/BaseLoadMore.vue'

vi.mock('@/composables/common/useInfiniteScroll', () => ({
  useInfiniteScroll: vi.fn(() => ({
    isLoading: ref(false),
    isError: ref(false),
    hasMore: ref(true),
    error: ref(null),
    loadMore: vi.fn(),
    reset: vi.fn()
  })),
  useLoadMore: vi.fn(() => ({
    isLoading: ref(false),
    isError: ref(false),
    hasMore: ref(true),
    error: ref(null),
    loadMore: vi.fn(),
    reset: vi.fn()
  }))
}))

describe('滚动加载组件测试', () => {
  describe('useInfiniteScroll', () => {
    it('应该正确初始化状态', async () => {
      const mockLoadCallback = vi.fn().mockResolvedValue(undefined)
      
      const { isLoading, isError, hasMore, error, loadedCount } = 
        await import('@/composables/common/useInfiniteScroll')
        .then(m => m.useInfiniteScroll(mockLoadCallback))
      
      expect(isLoading.value).toBe(false)
      expect(isError.value).toBe(false)
      expect(hasMore.value).toBe(true)
      expect(error.value).toBe(null)
      expect(loadedCount.value).toBe(0)
    })

    it('应该正确处理加载成功', async () => {
      const mockLoadCallback = vi.fn().mockResolvedValue(undefined)
      const { isLoading, isError, hasMore, error, loadMore } = 
        await import('@/composables/common/useInfiniteScroll')
        .then(m => m.useInfiniteScroll(mockLoadCallback))
      
      await loadMore()
      
      expect(mockLoadCallback).toHaveBeenCalledTimes(1)
      expect(isLoading.value).toBe(false)
      expect(isError.value).toBe(false)
    })

    it('应该正确处理加载失败', async () => {
      const error = new Error('加载失败')
      const mockLoadCallback = vi.fn().mockRejectedValue(error)
      const { isLoading, isError, hasMore, error: errorRef, loadMore } = 
        await import('@/composables/common/useInfiniteScroll')
        .then(m => m.useInfiniteScroll(mockLoadCallback))
      
      await loadMore()
      
      expect(mockLoadCallback).toHaveBeenCalledTimes(1)
      expect(isLoading.value).toBe(false)
      expect(isError.value).toBe(true)
      expect(errorRef.value).toEqual(error)
    })

    it('应该在没有更多数据时停止加载', async () => {
      const mockLoadCallback = vi.fn().mockResolvedValue(undefined)
      const { hasMore, loadMore, setHasMore } = 
        await import('@/composables/common/useInfiniteScroll')
        .then(m => m.useInfiniteScroll(mockLoadCallback))
      
      setHasMore(false)
      expect(hasMore.value).toBe(false)
      
      await loadMore()
      expect(mockLoadCallback).not.toHaveBeenCalled()
    })

    it('应该正确重置状态', async () => {
      const mockLoadCallback = vi.fn().mockResolvedValue(undefined)
      const { reset, loadedCount } = 
        await import('@/composables/common/useInfiniteScroll')
        .then(m => m.useInfiniteScroll(mockLoadCallback))
      
      reset()
      
      expect(loadedCount.value).toBe(0)
    })
  })

  describe('useLoadMore', () => {
    it('应该正确初始化状态', async () => {
      const mockLoadCallback = vi.fn().mockResolvedValue(undefined)
      const { isLoading, isError, hasMore, error, loadedCount } = 
        await import('@/composables/common/useInfiniteScroll')
        .then(m => m.useLoadMore(mockLoadCallback))
      
      expect(isLoading.value).toBe(false)
      expect(isError.value).toBe(false)
      expect(hasMore.value).toBe(true)
      expect(error.value).toBe(null)
      expect(loadedCount.value).toBe(0)
    })

    it('应该正确处理加载成功', async () => {
      const mockLoadCallback = vi.fn().mockResolvedValue(undefined)
      const { loadMore, loadedCount } = 
        await import('@/composables/common/useInfiniteScroll')
        .then(m => m.useLoadMore(mockLoadCallback))
      
      await loadMore()
      
      expect(mockLoadCallback).toHaveBeenCalledTimes(1)
      expect(loadedCount.value).toBe(1)
    })

    it('应该正确处理加载失败', async () => {
      const error = new Error('加载失败')
      const mockLoadCallback = vi.fn().mockRejectedValue(error)
      const { loadMore, isError, error: errorRef } = 
        await import('@/composables/common/useInfiniteScroll')
        .then(m => m.useLoadMore(mockLoadCallback))
      
      await loadMore()
      
      expect(mockLoadCallback).toHaveBeenCalledTimes(1)
      expect(isError.value).toBe(true)
      expect(errorRef.value).toEqual(error)
    })
  })

  describe('BaseInfiniteScroll组件', () => {
    it('应该渲染默认插槽内容', async () => {
      const wrapper = mount(BaseInfiniteScroll, {
        props: {
          loadCallback: vi.fn().mockResolvedValue(undefined)
        },
        slots: {
          default: '<div class="test-content">测试内容</div>'
        }
      })

      expect(wrapper.find('.test-content').exists()).toBe(true)
    })

    it('应该显示加载状态', async () => {
      vi.mock('@/composables/common/useInfiniteScroll', () => ({
        useInfiniteScroll: vi.fn(() => ({
          isLoading: ref(true),
          isError: ref(false),
          hasMore: ref(true),
          error: ref(null),
          loadMore: vi.fn(),
          reset: vi.fn()
        }))
      }))

      const wrapper = mount(BaseInfiniteScroll, {
        props: {
          loadCallback: vi.fn().mockResolvedValue(undefined),
          showLoading: true
        },
        slots: {
          default: '<div>内容</div>'
        }
      })

      await nextTick()
      expect(wrapper.find('.infinite-scroll-loading').exists()).toBe(true)
    })

    it('应该显示错误状态和重试按钮', async () => {
      vi.mock('@/composables/common/useInfiniteScroll', () => ({
        useInfiniteScroll: vi.fn(() => ({
          isLoading: ref(false),
          isError: ref(true),
          hasMore: ref(true),
          error: ref(new Error('加载失败')),
          loadMore: vi.fn(),
          reset: vi.fn()
        }))
      }))

      const wrapper = mount(BaseInfiniteScroll, {
        props: {
          loadCallback: vi.fn().mockResolvedValue(undefined),
          showError: true,
          showRetryButton: true
        },
        slots: {
          default: '<div>内容</div>'
        }
      })

      await nextTick()
      expect(wrapper.find('.infinite-scroll-error').exists()).toBe(true)
      expect(wrapper.find('button').exists()).toBe(true)
    })

    it('应该显示没有更多数据的状态', async () => {
      vi.mock('@/composables/common/useInfiniteScroll', () => ({
        useInfiniteScroll: vi.fn(() => ({
          isLoading: ref(false),
          isError: ref(false),
          hasMore: ref(false),
          error: ref(null),
          loadMore: vi.fn(),
          reset: vi.fn()
        }))
      }))

      const wrapper = mount(BaseInfiniteScroll, {
        props: {
          loadCallback: vi.fn().mockResolvedValue(undefined),
          showNoMore: true
        },
        slots: {
          default: '<div>内容</div>'
        }
      })

      await nextTick()
      expect(wrapper.find('.infinite-scroll-no-more').exists()).toBe(true)
    })
  })

  describe('BaseLoadMore组件', () => {
    it('应该渲染默认插槽内容', async () => {
      const wrapper = mount(BaseLoadMore, {
        props: {
          loadCallback: vi.fn().mockResolvedValue(undefined)
        },
        slots: {
          default: '<div class="test-content">测试内容</div>'
        }
      })

      expect(wrapper.find('.test-content').exists()).toBe(true)
    })

    it('应该显示加载按钮', async () => {
      const wrapper = mount(BaseLoadMore, {
        props: {
          loadCallback: vi.fn().mockResolvedValue(undefined),
          hasMore: true,
          showLoadMoreButton: true
        },
        slots: {
          default: '<div>内容</div>'
        }
      })

      await nextTick()
      const button = wrapper.find('button')
      expect(button.exists()).toBe(true)
      expect(button.text()).toContain('加载更多')
    })

    it('应该显示没有更多数据的状态', async () => {
      const wrapper = mount(BaseLoadMore, {
        props: {
          loadCallback: vi.fn().mockResolvedValue(undefined),
          hasMore: false,
          showNoMore: true
        },
        slots: {
          default: '<div>内容</div>'
        }
      })

      await nextTick()
      expect(wrapper.find('.load-more-no-more').exists()).toBe(true)
    })

    it('应该在点击加载按钮时触发加载回调', async () => {
      const mockLoadCallback = vi.fn().mockResolvedValue(undefined)
      const wrapper = mount(BaseLoadMore, {
        props: {
          loadCallback: mockLoadCallback,
          hasMore: true,
          showLoadMoreButton: true
        },
        slots: {
          default: '<div>内容</div>'
        }
      })

      await nextTick()
      const button = wrapper.find('button')
      await button.trigger('click')

      expect(mockLoadCallback).toHaveBeenCalled()
    })
  })

  describe('性能优化', () => {
    it('应该支持IntersectionObserver', async () => {
      const { supportsIntersectionObserver } = 
        await import('@/utils/core/performance')
      
      expect(typeof supportsIntersectionObserver).toBe('function')
    })

    it('应该支持requestIdleCallback', async () => {
      const { supportsRequestIdleCallback } = 
        await import('@/utils/core/performance')
      
      expect(typeof supportsRequestIdleCallback).toBe('function')
    })

    it('应该提供安全的requestIdleCallback', async () => {
      const { safeRequestIdleCallback, safeCancelIdleCallback } = 
        await import('@/utils/core/performance')
      
      const callback = vi.fn()
      const id = safeRequestIdleCallback(callback, 1000)
      
      expect(typeof id).toBe('number')
      safeCancelIdleCallback(id)
    })

    it('应该支持节流函数', async () => {
      const { rafThrottle } = 
        await import('@/utils/core/performance')
      
      const fn = vi.fn()
      const throttledFn = rafThrottle(fn)
      
      expect(typeof throttledFn).toBe('function')
    })
  })

  describe('错误处理', () => {
    it('应该正确处理加载超时', async () => {
      const timeoutError = new Error('加载超时')
      const mockLoadCallback = vi.fn().mockRejectedValue(timeoutError)
      const { loadMore, isError, error } = 
        await import('@/composables/common/useInfiniteScroll')
        .then(m => m.useInfiniteScroll(mockLoadCallback))
      
      await loadMore()
      
      expect(isError.value).toBe(true)
      expect(error.value).toEqual(timeoutError)
    })

    it('应该正确处理网络错误', async () => {
      const networkError = new Error('网络连接失败')
      const mockLoadCallback = vi.fn().mockRejectedValue(networkError)
      const { loadMore, isError, error } = 
        await import('@/composables/common/useInfiniteScroll')
        .then(m => m.useInfiniteScroll(mockLoadCallback))
      
      await loadMore()
      
      expect(isError.value).toBe(true)
      expect(error.value).toEqual(networkError)
    })

    it('应该在错误后重试成功', async () => {
      let callCount = 0
      const mockLoadCallback = vi.fn().mockImplementation(() => {
        callCount++
        if (callCount === 1) {
          return Promise.reject(new Error('加载失败'))
        }
        return Promise.resolve()
      })

      const { loadMore, reset, isError } = 
        await import('@/composables/common/useInfiniteScroll')
        .then(m => m.useInfiniteScroll(mockLoadCallback))
      
      await loadMore()
      expect(isError.value).toBe(true)
      
      reset()
      await loadMore()
      expect(isError.value).toBe(false)
    })
  })

  describe('边界情况', () => {
    it('应该在disabled状态下不触发加载', async () => {
      const mockLoadCallback = vi.fn().mockResolvedValue(undefined)
      const { loadMore, isLoading } = 
        await import('@/composables/common/useInfiniteScroll')
        .then(m => m.useInfiniteScroll(mockLoadCallback, { disabled: true }))
      
      await loadMore()
      
      expect(mockLoadCallback).not.toHaveBeenCalled()
      expect(isLoading.value).toBe(false)
    })

    it('应该在hasMore为false时不触发加载', async () => {
      const mockLoadCallback = vi.fn().mockResolvedValue(undefined)
      const { loadMore, setHasMore } = 
        await import('@/composables/common/useInfiniteScroll')
        .then(m => m.useInfiniteScroll(mockLoadCallback))
      
      setHasMore(false)
      await loadMore()
      
      expect(mockLoadCallback).not.toHaveBeenCalled()
    })

    it('应该在加载中时不触发新的加载', async () => {
      let resolveLoadCallback: () => void
      const mockLoadCallback = vi.fn().mockImplementation(() => {
        return new Promise(resolve => {
          resolveLoadCallback = resolve
        })
      })
      
      const { loadMore, isLoading } = 
        await import('@/composables/common/useInfiniteScroll')
        .then(m => m.useInfiniteScroll(mockLoadCallback))
      
      const loadPromise = loadMore()
      expect(isLoading.value).toBe(true)
      
      resolveLoadCallback!()
      await loadPromise
      
      expect(isLoading.value).toBe(false)
    })
  })
})
