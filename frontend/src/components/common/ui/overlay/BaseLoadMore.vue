<template>
  <div class="load-more-container">
    <slot
      :is-loading="isLoading"
      :has-more="hasMore"
      :error="error"
    />
    
    <div class="load-more-trigger">
      <LoadingState
        v-if="isLoading && showLoading"
        :text="loadingText"
        :size="loadingSize"
        :variant="loadingVariant"
      />
      
      <div
        v-else-if="isError && showError"
        class="load-more-error"
      >
        <div class="flex flex-col items-center gap-3 text-center">
          <i class="pi pi-exclamation-circle text-error text-2xl" />
          <p class="text-sm text-error">
            {{ errorMessage }}
          </p>
          <BaseButton
            v-if="showRetryButton"
            :label="retryButtonText"
            icon="pi pi-refresh"
            severity="secondary"
            size="small"
            outlined
            @click="handleRetry"
          />
        </div>
      </div>
      
      <BaseButton
        v-else-if="hasMore && showLoadMoreButton"
        ref="loadMoreButtonRef"
        :label="loadMoreButtonText"
        :icon="showIcon ? 'pi pi-chevron-down' : undefined"
        severity="secondary"
        outlined
        class="load-more-button"
        @click="handleLoadMore"
      />
      
      <div
        v-else-if="!hasMore && showNoMore"
        class="load-more-no-more"
      >
        <div class="flex items-center gap-3 text-neutral-text-secondary">
          <div class="h-px flex-1 bg-neutral-border" />
          <span class="text-xs">{{ noMoreText }}</span>
          <div class="h-px flex-1 bg-neutral-border" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * BaseLoadMore - 手动加载更多组件
 * 功能：基于PrimeVue的二次封装，提供手动点击加载更多的功能
 * 作者：System
 * 创建日期：2026-05-11
 */

import { ref } from 'vue'
import BaseButton from '@/components/common/ui/input/BaseButton.vue'
import LoadingState from '@/components/common/ui/feedback/LoadingState.vue'
import { useLoadMore } from '@/composables/common/useInfiniteScroll'

interface Props {
  loadCallback: () => Promise<void>
  disabled?: boolean
  showLoading?: boolean
  showError?: boolean
  showRetryButton?: boolean
  showLoadMoreButton?: boolean
  showNoMore?: boolean
  showIcon?: boolean
  loadingText?: string
  loadingSize?: number
  loadingVariant?: 'default' | 'ai'
  errorMessage?: string
  retryButtonText?: string
  loadMoreButtonText?: string
  noMoreText?: string
}

const props = withDefaults(defineProps<Props>(), {
  disabled: false,
  showLoading: true,
  showError: true,
  showRetryButton: true,
  showLoadMoreButton: true,
  showNoMore: true,
  showIcon: false,
  loadingText: '加载中...',
  loadingSize: 24,
  loadingVariant: 'default',
  errorMessage: '加载失败，请重试',
  retryButtonText: '重新加载',
  loadMoreButtonText: '加载更多',
  noMoreText: '没有更多了'
})

const emit = defineEmits<{
  'load-more': []
  'load-error': [error: Error]
  'load-complete': []
}>()

const loadMoreButtonRef = ref<InstanceType<typeof BaseButton> | null>(null)

const {
  isLoading,
  isError,
  hasMore,
  error,
  loadMore,
  reset
} = useLoadMore(props.loadCallback, {
  disabled: props.disabled
})

const handleLoadMore = async () => {
  emit('load-more')
  await loadMore()
}

const handleRetry = async () => {
  reset()
  await loadMore()
}

defineExpose({
  isLoading,
  isError,
  hasMore,
  error,
  loadMore,
  reset,
  scrollToLoadButton: () => {
    loadMoreButtonRef.value?.$el?.scrollIntoView({ behavior: 'smooth', block: 'center' })
  }
})
</script>

<style scoped>
.load-more-container {
  width: 100%;
}

.load-more-trigger {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 16px 0;
  margin-top: 8px;
}

.load-more-error {
  padding: 12px;
}

.load-more-no-more {
  padding: 12px 0;
  width: 100%;
}

.load-more-button {
  min-width: 140px;
}
</style>
