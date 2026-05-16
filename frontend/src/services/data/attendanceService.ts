import { apiFactory } from '../core/apiService'
import { API_ENDPOINTS } from '@/config/apiEndpoints'
import type { ApiResponse } from '@/types/api'


export interface AttendanceListParams {
  page?: number
  page_size?: number
  start_date?: string | null
  end_date?: string | null
  search?: string | null
  server_name?: string | null
  map_name?: string | null
  profession?: string | null
  sort_by?: string
  sort_order?: string
}

export interface AttendanceStatsParams {
  start_date?: string | null
  end_date?: string | null
}

export interface AttendanceExportParams {
  start_date?: string | null
  end_date?: string | null
  format?: 'csv' | 'json'
}

export class AttendanceService {
  /** v2.0 获取账号出勤列表 */
  async getAccounts(params: AttendanceListParams): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(API_ENDPOINTS.ATTENDANCE.ACCOUNTS, { params })
  }

  /** v2.0 获取账号出勤详情 */
  async getAccountDetail(account: string, startDate?: string | null, endDate?: string | null): Promise<ApiResponse<any>> {
    const params: any = {}
    if (startDate) params.start_date = startDate
    if (endDate) params.end_date = endDate
    return apiFactory.get<any>(API_ENDPOINTS.ATTENDANCE.ACCOUNT_DETAIL(account), { params })
  }

  /** v2.0 获取账号评分维度明细 */
  async getAccountScoreBreakdown(account: string, startDate?: string | null, endDate?: string | null): Promise<ApiResponse<any>> {
    const params: any = {}
    if (startDate) params.start_date = startDate
    if (endDate) params.end_date = endDate
    return apiFactory.get<any>(API_ENDPOINTS.ATTENDANCE.ACCOUNT_SCORE_BREAKDOWN(account), { params })
  }

  /** v2.0 获取角色战斗记录 */
  async getCharacterDetail(
    account: string,
    character: string,
    page: number = 1,
    pageSize: number = 20,
    startDate?: string | null,
    endDate?: string | null
  ): Promise<ApiResponse<any>> {
    const params: any = { page, page_size: pageSize }
    if (startDate) params.start_date = startDate
    if (endDate) params.end_date = endDate
    return apiFactory.get<any>(API_ENDPOINTS.ATTENDANCE.CHARACTER_DETAIL(account, character), { params })
  }

  /** v2.0 获取筛选选项（服务器/地图/职业） */
  async getFilters(): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(API_ENDPOINTS.ATTENDANCE.FILTERS)
  }

  // --- 兼容旧接口 ---
  async getAttendanceList(params: AttendanceListParams): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(API_ENDPOINTS.ATTENDANCE.LIST, { params })
  }

  async getAttendanceStats(params: AttendanceStatsParams): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(API_ENDPOINTS.ATTENDANCE.STATS, { params })
  }

  async exportAttendance(params: AttendanceExportParams): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(API_ENDPOINTS.ATTENDANCE.EXPORT, { params })
  }

  async getMemberAttendance(memberId: number, startDate?: string | null, endDate?: string | null): Promise<ApiResponse<any>> {
    const params: any = {}
    if (startDate) params.start_date = startDate
    if (endDate) params.end_date = endDate
    return apiFactory.get<any>(API_ENDPOINTS.ATTENDANCE.DETAIL(memberId), { params })
  }

  /** v2.0 导出账号出勤详情 */
  async exportAccountDetail(
    account: string,
    format: 'csv' | 'excel' = 'csv',
    startDate?: string | null,
    endDate?: string | null
  ): Promise<void> {
    const params: any = {}
    if (startDate) params.start_date = startDate
    if (endDate) params.end_date = endDate
    params.format = format

    // 构建URL
    let url = API_ENDPOINTS.ATTENDANCE.ACCOUNT_EXPORT(account)
    const queryString = new URLSearchParams(params).toString()
    if (queryString) {
      url += `?${queryString}`
    }

    try {
      const blob = await apiFactory.download(url)
      const downloadUrl = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = downloadUrl
      const fileExt = format === 'excel' ? 'xlsx' : 'csv'
      link.download = `${account}_attendance_detail.${fileExt}`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(downloadUrl)
    } catch (error) {
      console.error('导出失败:', error)
      throw error
    }
  }
}

export const attendanceService = new AttendanceService()
