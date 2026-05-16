import { computed, ref } from 'vue'

export interface PageChangeEvent {
  page: number
  rows?: number
}

export interface UsePaginationOptions {
  defaultPage?: number
  defaultPageSize?: number
  pageSizeOptions?: number[]
}

export function usePagination(options: UsePaginationOptions = {}) {
  const {
    defaultPage = 1,
    defaultPageSize = 20,
    pageSizeOptions = [10, 20, 50, 100]
  } = options

  const page = ref(defaultPage)
  const pageSize = ref(defaultPageSize)
  const total = ref(0)

  const pagination = computed(() => ({
    page: page.value,
    pageSize: pageSize.value,
    total: total.value
  }))

  const onPageChange = (event: PageChangeEvent) => {
    page.value = (event.page || 0) + 1
    if (event.rows !== undefined) {
      pageSize.value = event.rows
    }
  }

  const resetPage = () => {
    page.value = defaultPage
  }

  return {
    page,
    pageSize,
    total,
    pagination,
    onPageChange,
    resetPage,
    pageSizeOptions
  }
}
