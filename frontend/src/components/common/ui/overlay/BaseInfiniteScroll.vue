<template>
  <div 
    ref="scrollContainerRef"
    class="infinite-scroll-container"
    :class="containerClass"
    :style="containerStyle"
    @scroll="handleScroll"
  >
    <slot
      :is-loading="isLoading"
      :has-more="hasMore"
      :error="error"
    />
    
    <div
      ref="sentinelRef"
      class="infinite-scroll-sentinel"
    />

    <LoadingState
      v-if="isLoading && showLoading"
      :text="loadingText"
      :size="loadingSize"
      :variant="loadingVariant"
    />

    <div
      v-if="isError && showError"
      class="infinite-scroll-error"
    >
      <div class="flex flex-col items-center gap-2 text-center">
        <i class="pi pi-exclamation-circle text-error text-2xl" />
        <p class="text-sm text-error">
          {{ errorMessage }}
        </p>
        <BaseButton
          v-if="showRetryButton"
          :label="retryButtonText"
          icon="pi pi-refresh"
          variant="secondary"
          size="small"
          @click="handleRetry"
        />
      </div>
    </div>

    <div
      v-if="!hasMore && !isLoading && showNoMore"
      class="infinite-scroll-no-more"
    >
      <div class="flex items-center gap-2 text-neutral-text-secondary">
        <div class="h-px flex-1 bg-neutral-border" />
        <span class="text-xs">{{ noMoreText }}</span>
        <div class="h-px flex-1 bg-neutral-border" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * BaseInfiniteScroll - 无限滚动组件
 * 功能：基于PrimeVue的二次封装，支持自动加载和手动加载两种模式
 * 作者：System
 * 创建日期：2026-05-11
 */

import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import BaseButton from '@/components/common/ui/input/BaseButton.vue'
import LoadingState from '@/components/common/ui/feedback/LoadingState.vue'
import { useInfiniteScroll } from '@/composables/common/useInfiniteScroll'
import type { InfiniteScrollOptions } from '@/types/scroll'

interface Props {
  loadCallback: () => Promise<void>
  distance?: number
  direction?: 'down' | 'up'
  immediate?: boolean
  disabled?: boolean
  containerClass?: string
  containerStyle?: Record<string, any>
  showLoading?: boolean
  showError?: boolean
  showRetryButton?: boolean
  showNoMore?: boolean
  loadingText?: string
  loadingSize?: number
  loadingVariant?: 'default' | 'ai'
  errorMessage?: string
  retryButtonText?: string
  noMoreText?: string
  height?: string
  maxHeight?: string
}

const props = withDefaults(defineProps<Props>(), {
  distance: 200,
  direction: 'down',
  immediate: false,
  disabled: false,
  containerClass: '',
  containerStyle: () => ({}),
  showLoading: true,
  showError: true,
  showRetryButton: true,
  showNoMore: true,
  loadingText: '加载中...',
  loadingSize: 32,
  loadingVariant: 'default',
  errorMessage: '加载失败，请重试',
  retryButtonText: '重新加载',
  noMoreText: '没有更多了',
  height: '100%',
  maxHeight: '600px'
})

const emit = defineEmits<{
  'load-more': []
  'load-error': [error: Error]
  'load-complete': []
  'scroll': [event: Event]
}>()

const scrollContainerRef = ref<HTMLElement | null>(null)
const sentinelRef = ref<HTMLElement | null>(null)

const {
  isLoading,
  isError,
  hasMore,
  error,
  loadMore,
  reset,
  handleScroll: onScroll
} = useInfiniteScroll(props.loadCallback, {
  distance: props.distance,
  direction: props.direction,
  immediate: props.immediate,
  disabled: props.disabled
})

const handleScroll = (event: Event) => {
  onScroll(event)
  emit('scroll', event)
}

const handleRetry = async () => {
  reset()
  await loadMore()
}

watch(error, (newError) => {
  if (newError) {
    emit('load-error', newError)
  }
})

watch(hasMore, (newHasMore) => {
  if (!newHasMore) {
    emit('load-complete')
  }
})

onMounted(() => {
  if (props.immediate) {
    loadMore()
  }
})

defineExpose({
  scrollContainer: scrollContainerRef,
  sentinel: sentinelRef,
  isLoading,
  isError,
  hasMore,
  error,
  loadMore,
  reset,
  scrollTo: (top: number) => {
    if (scrollContainerRef.value) {
      scrollContainerRef.value.scrollTop = top
    }
  }
})
</script>

<style scoped>
.infinite-scroll-container {
  overflow-y: auto;
  overflow-x: hidden;
  position: relative;
}

.infinite-scroll-sentinel {
  height: 1px;
  width: 100%;
}

.infinite-scroll-error {
  padding: 16px;
  margin: 8px 0;
}

.infinite-scroll-no-more {
  padding: 16px 0;
  margin: 8px 0;
}
</style>
