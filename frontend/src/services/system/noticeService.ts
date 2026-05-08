import { API_ENDPOINTS } from '@/constants/apiEndpoints'
import { apiFactory } from '../core/apiService'
import type { ApiResponse } from '@/types/api'

export interface NoticeItem {
  notice_id: number
  notice_title: string
  notice_content: string | null
  notice_type: string
  source_type: string | null
  source_id: string | null
  create_time: string | null
  is_read: boolean
}

export interface NoticeListResponse {
  items: NoticeItem[]
  total: number
  page: number
  page_size: number
}

export class NoticeService {
  /** 获取未读通知数 */
  async getUnreadCount(): Promise<ApiResponse<{ count: number }>> {
    return apiFactory.get(API_ENDPOINTS.NOTICES.UNREAD_COUNT)
  }

  /** 获取通知列表 */
  async getNoticeList(params?: {
    page?: number
    page_size?: number
    unread_only?: boolean
  }): Promise<ApiResponse<NoticeListResponse>> {
    return apiFactory.get(API_ENDPOINTS.NOTICES.LIST, { params })
  }

  /** 标记单条通知已读 */
  async markAsRead(noticeId: number): Promise<ApiResponse<void>> {
    return apiFactory.post(API_ENDPOINTS.NOTICES.MARK_READ(noticeId))
  }

  /** 标记全部已读 */
  async markAllAsRead(): Promise<ApiResponse<{ count: number }>> {
    return apiFactory.post(API_ENDPOINTS.NOTICES.MARK_ALL_READ)
  }
}

export const noticeService = new NoticeService()
