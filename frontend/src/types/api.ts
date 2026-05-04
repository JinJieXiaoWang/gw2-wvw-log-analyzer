/**
 * API 核心类型定义
 * 功能：统一存放 API 响应、错误、分页等基础设施类型
 * 设计原则：types 层不依赖 services 层，确保分层清晰
 * 更新日期：2026-05-04
 */

export interface ApiResponse<T = any> {
  success: boolean
  code: number
  message: string
  data?: T
  errors?: any
  error?: {
    message?: string
    details?: {
      message?: string
    }
  } | Error
}

export interface ApiError {
  message: string
  code?: number
  details?: any
}

export interface PaginationParams {
  page?: number
  page_size?: number
  sort_by?: string
  sort_order?: 'asc' | 'desc'
}

export interface PaginatedResponse<T = any> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}
