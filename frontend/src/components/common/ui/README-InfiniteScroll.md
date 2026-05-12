# 滚动加载组件使用文档

## 概述

本文档描述了基于PrimeVue的滚动加载二次封装组件，提供自动滚动加载和手动加载更多两种模式。

## 组件列表

### 1. BaseInfiniteScroll - 自动滚动加载组件

基于IntersectionObserver实现自动滚动加载功能。

#### 使用方法

```vue
<template>
  <BaseInfiniteScroll
    :load-callback="handleLoadMore"
    :distance="200"
    :immediate="false"
    :show-loading="true"
    :show-error="true"
    :show-retry-button="true"
    :show-no-more="true"
    loading-text="加载中..."
    error-message="加载失败，请重试"
    no-more-text="没有更多了"
    height="600px"
    max-height="800px"
    @load-more="onLoadMore"
    @load-error="onLoadError"
    @load-complete="onLoadComplete"
  >
    <template #default="{ isLoading, hasMore, error }">
      <div v-for="item in items" :key="item.id">
        {{ item.name }}
      </div>
    </template>
  </BaseInfiniteScroll>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import BaseInfiniteScroll from '@/components/common/ui/overlay/BaseInfiniteScroll.vue'

const items = ref<any[]>([])
const page = ref(1)
const hasMore = ref(true)

const handleLoadMore = async () => {
  if (!hasMore.value) return
  
  try {
    const response = await fetch(`/api/items?page=${page.value}`)
    const data = await response.json()
    
    if (data.items.length === 0) {
      hasMore.value = false
    } else {
      items.value = [...items.value, ...data.items]
      page.value++
    }
  } catch (error) {
    throw error // 抛出错误以便组件显示错误状态
  }
}

const onLoadMore = () => {
  console.log('触发加载更多')
}

const onLoadError = (error: Error) => {
  console.error('加载失败:', error)
}

const onLoadComplete = () => {
  console.log('已加载所有数据')
}
</script>
```

#### Props属性

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| loadCallback | Function | required | 加载回调函数，返回Promise |
| distance | number | 200 | 距离底部多少像素时触发加载 |
| direction | 'down' \| 'up' | 'down' | 滚动方向，down表示向下滑动加载 |
| immediate | boolean | false | 是否立即加载第一页数据 |
| disabled | boolean | false | 是否禁用滚动加载 |
| containerClass | string | '' | 容器额外类名 |
| containerStyle | object | {} | 容器额外样式 |
| showLoading | boolean | true | 是否显示加载状态 |
| showError | boolean | true | 是否显示错误状态 |
| showRetryButton | boolean | true | 是否显示重试按钮 |
| showNoMore | boolean | true | 是否显示没有更多数据提示 |
| loadingText | string | '加载中...' | 加载提示文字 |
| loadingSize | number | 32 | 加载图标大小 |
| loadingVariant | 'default' \| 'ai' | 'default' | 加载变体样式 |
| errorMessage | string | '加载失败，请重试' | 错误提示文字 |
| retryButtonText | string | '重新加载' | 重试按钮文字 |
| noMoreText | string | '没有更多了' | 没有更多数据提示文字 |
| height | string | '100%' | 容器高度 |
| maxHeight | string | '600px' | 容器最大高度 |

#### Events事件

| 事件名 | 参数 | 说明 |
|--------|------|------|
| load-more | - | 触发加载更多时触发 |
| load-error | Error | 加载失败时触发 |
| load-complete | - | 加载完成（没有更多数据）时触发 |
| scroll | Event | 滚动时触发 |

#### Slots插槽

| 插槽名 | 作用域数据 | 说明 |
|--------|-----------|------|
| default | { isLoading, hasMore, error } | 默认插槽，显示列表内容 |

#### Expose方法

| 方法名 | 参数 | 说明 |
|--------|------|------|
| loadMore | - | 手动触发加载 |
| reset | - | 重置状态 |
| scrollTo | top: number | 滚动到指定位置 |

---

### 2. BaseLoadMore - 手动加载更多组件

提供手动点击按钮加载更多的功能。

#### 使用方法

```vue
<template>
  <div>
    <div v-for="item in items" :key="item.id">
      {{ item.name }}
    </div>
    
    <BaseLoadMore
      :load-callback="handleLoadMore"
      :has-more="hasMore"
      :show-loading="true"
      :show-error="true"
      :show-retry-button="true"
      :show-load-more-button="true"
      :show-no-more="true"
      :show-icon="false"
      loading-text="加载中..."
      error-message="加载失败，请重试"
      retry-button-text="重新加载"
      load-more-button-text="加载更多"
      no-more-text="没有更多了"
      @load-more="onLoadMore"
      @load-error="onLoadError"
      @load-complete="onLoadComplete"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import BaseLoadMore from '@/components/common/ui/overlay/BaseLoadMore.vue'

const items = ref<any[]>([])
const page = ref(1)
const hasMore = ref(true)

const handleLoadMore = async () => {
  if (!hasMore.value) return
  
  try {
    const response = await fetch(`/api/items?page=${page.value}`)
    const data = await response.json()
    
    if (data.items.length === 0) {
      hasMore.value = false
    } else {
      items.value = [...items.value, ...data.items]
      page.value++
    }
  } catch (error) {
    throw error
  }
}
</script>
```

#### Props属性

| 属性名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| loadCallback | Function | required | 加载回调函数，返回Promise |
| disabled | boolean | false | 是否禁用加载 |
| showLoading | boolean | true | 是否显示加载状态 |
| showError | boolean | true | 是否显示错误状态 |
| showRetryButton | boolean | true | 是否显示重试按钮 |
| showLoadMoreButton | boolean | true | 是否显示加载更多按钮 |
| showNoMore | boolean | true | 是否显示没有更多数据提示 |
| showIcon | boolean | false | 是否显示按钮图标 |
| loadingText | string | '加载中...' | 加载提示文字 |
| loadingSize | number | 24 | 加载图标大小 |
| loadingVariant | 'default' \| 'ai' | 'default' | 加载变体样式 |
| errorMessage | string | '加载失败，请重试' | 错误提示文字 |
| retryButtonText | string | '重新加载' | 重试按钮文字 |
| loadMoreButtonText | string | '加载更多' | 加载更多按钮文字 |
| noMoreText | string | '没有更多了' | 没有更多数据提示文字 |

#### Events事件

| 事件名 | 参数 | 说明 |
|--------|------|------|
| load-more | - | 点击加载更多按钮时触发 |
| load-error | Error | 加载失败时触发 |
| load-complete | - | 加载完成（没有更多数据）时触发 |

#### Expose方法

| 方法名 | 说明 |
|--------|------|
| loadMore | 手动触发加载 |
| reset | 重置状态 |
| scrollToLoadButton | 滚动到加载按钮位置 |

---

### 3. useInfiniteScroll - 滚动加载Composable

提供滚动加载的逻辑封装，可在组合式函数中使用。

#### 使用方法

```typescript
import { ref } from 'vue'
import { useInfiniteScroll } from '@/composables/common/useInfiniteScroll'

export default {
  setup() {
    const items = ref<any[]>([])
    const page = ref(1)
    
    const loadCallback = async () => {
      const response = await fetch(`/api/items?page=${page.value}`)
      const data = await response.json()
      
      if (data.items.length === 0) {
        setHasMore(false)
      } else {
        items.value = [...items.value, ...data.items]
        page.value++
      }
    }
    
    const {
      isLoading,
      isError,
      hasMore,
      error,
      loadedCount,
      loadMore,
      reset,
      setHasMore
    } = useInfiniteScroll(loadCallback, {
      distance: 200,
      direction: 'down',
      immediate: true,
      disabled: false
    })
    
    return {
      items,
      isLoading,
      isError,
      hasMore,
      error,
      loadedCount,
      loadMore,
      reset,
      setHasMore
    }
  }
}
```

#### 参数

| 参数名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| loadCallback | () => Promise<void> | required | 加载回调函数 |
| options | InfiniteScrollOptions | {} | 配置选项 |

#### 返回值

| 返回值 | 类型 | 说明 |
|--------|------|------|
| isLoading | Ref<boolean> | 是否正在加载 |
| isError | Ref<boolean> | 是否有错误 |
| hasMore | Ref<boolean> | 是否还有更多数据 |
| error | Ref<Error \| null> | 错误对象 |
| loadedCount | Ref<number> | 已加载次数 |
| scrollState | ComputedRef<ScrollState> | 滚动状态对象 |
| scrollContainerRef | Ref<HTMLElement \| null> | 滚动容器引用 |
| sentinelRef | Ref<HTMLElement \| null> | 观察器 sentinel 引用 |
| loadMore | () => Promise<void> | 加载更多 |
| reset | () => void | 重置状态 |
| setHasMore | (value: boolean) => void | 设置是否还有更多数据 |
| handleScroll | (event: Event) => void | 处理滚动事件 |
| handleScrollEvent | (event: Event) => ScrollEvent | 获取滚动事件详情 |

---

## 性能优化特性

### 1. IntersectionObserver 支持

组件优先使用IntersectionObserver API来实现自动加载，如果浏览器不支持则回退到scroll事件。

### 2. 内存优化

- 自动断开IntersectionObserver连接，避免内存泄漏
- 支持禁用状态，停止所有监听
- 提供reset方法清理状态

### 3. 错误处理

- 自动捕获加载过程中的错误
- 提供重试机制
- 支持自定义错误提示

### 4. 无障碍支持

- 使用语义化HTML结构
- 提供适当的aria标签
- 支持键盘导航

---

## 使用场景

### 1. 自动滚动加载

适用于无限滚动的场景，如：
- 社交媒体信息流
- 新闻列表
- 商品列表

推荐使用：`BaseInfiniteScroll`

### 2. 手动加载更多

适用于需要用户明确操作的场景，如：
- 分页列表
- 历史记录
- 搜索结果

推荐使用：`BaseLoadMore`

### 3. 组合式函数

适用于需要自定义UI的场景，如：
- 自定义加载动画
- 特殊列表布局
- 与其他组件集成

推荐使用：`useInfiniteScroll`

---

## 最佳实践

### 1. 数据管理

```typescript
// ✅ 推荐：使用hasMore控制加载
const hasMore = ref(true)
const setHasMore = (value: boolean) => {
  hasMore.value = value
}

// ❌ 不推荐：在回调中直接返回空数组
const loadCallback = async () => {
  const data = await fetchData()
  if (data.length === 0) {
    return [] // 没有设置hasMore
  }
}
```

### 2. 错误处理

```typescript
// ✅ 推荐：抛出错误以便组件处理
const loadCallback = async () => {
  try {
    const data = await fetchData()
    return data
  } catch (error) {
    throw error // 抛出错误
  }
}

// ❌ 不推荐：吞掉错误
const loadCallback = async () => {
  try {
    const data = await fetchData()
    return data
  } catch (error) {
    console.error(error) // 错误被吞掉
  }
}
```

### 3. 防抖处理

```typescript
// ✅ 推荐：使用disabled状态防止重复加载
const isLoading = ref(false)
const loadCallback = async () => {
  if (isLoading.value) return
  isLoading.value = true
  try {
    // 加载逻辑
  } finally {
    isLoading.value = false
  }
}

// 组件内部已自动处理防抖
```

### 4. 性能优化

```vue
<!-- ✅ 推荐：使用v-if控制渲染 -->
<BaseInfiniteScroll v-if="items.length > 0" :load-callback="handleLoadMore">
  <div v-for="item in items" :key="item.id">
    {{ item.name }}
  </div>
</BaseInfiniteScroll>

<!-- ❌ 不推荐：大列表使用v-show -->
<BaseInfiniteScroll :load-callback="handleLoadMore">
  <div v-for="item in items" :key="item.id" v-show="true">
    {{ item.name }}
  </div>
</BaseInfiniteScroll>
```

---

## 浏览器兼容性

- Chrome 51+
- Firefox 55+
- Safari 12.1+
- Edge 79+
- 不支持IE浏览器

对于不支持IntersectionObserver的浏览器，组件会自动回退到scroll事件。

---

## 常见问题

### Q: 如何在加载完成后自动滚动到底部？

```typescript
const handleLoadComplete = () => {
  nextTick(() => {
    const container = scrollContainerRef.value
    if (container) {
      container.scrollTop = container.scrollHeight
    }
  })
}
```

### Q: 如何实现下拉刷新？

可以结合第三方下拉刷新组件，或者使用`usePullToRefresh` composable。

### Q: 如何实现多列布局的滚动加载？

可以使用CSS Grid或Flexbox布局，每个列表项需要唯一的key。

---

## 测试覆盖

组件已实现以下测试用例：

- ✅ 状态初始化测试
- ✅ 加载成功测试
- ✅ 加载失败测试
- ✅ 错误重试测试
- ✅ 边界条件测试
- ✅ 性能优化测试
- ✅ 内存泄漏测试

测试覆盖率目标：≥80%

---

## 更新日志

### v1.0.0 (2026-05-11)

- ✨ 初始版本发布
- 🎨 支持自动滚动加载和手动加载更多两种模式
- ⚡ 集成IntersectionObserver优化性能
- 📝 提供完整的TypeScript类型定义
- 🧪 包含完整的单元测试
