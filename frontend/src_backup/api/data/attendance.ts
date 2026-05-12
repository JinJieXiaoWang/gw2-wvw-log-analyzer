/**
 * 出勤统计 API
 * 功能：处理出勤记录查询、统计分析、导出等
 * 作者：帅姐姐
 * 创建日期：2024-01-15
 */

import { HttpClient } from '../../services/core/apiService'
import { API_ENDPOINTS } from '@/config/apiEndpoints'

export interface AttendanceQueryParams {
  startDate?: string
  endDate?: string
  playerId?: string
  mapName?: string
  serverName?: string
  page?: number
  pageSize?: number
}

export interface AttendanceStats {
  totalPlayers: number
  totalLogs: number
  totalDuration: number
  avgAttendance: number
  topPlayers: Array<{
    id: string
    name: string
    count: number
    duration: number
  }>
}

class AttendanceApi {
  /**
   * 获取出勤记录列表
   */
  async getAttendance(params?: AttendanceQueryParams) {
    return await HttpClient.get(API_ENDPOINTS.ATTENDANCE.LIST, { params })
  }

  /**
   * 获取出勤统计数据
   */
  async getStats(params?: AttendanceQueryParams) {
    return await HttpClient.get<AttendanceStats>(API_ENDPOINTS.ATTENDANCE.LIST, { params })
  }

  /**
   * 导出出勤数据
   */
  async exportData(format: 'csv' | 'excel', params?: AttendanceQueryParams) {
    return await HttpClient.get(API_ENDPOINTS.ATTENDANCE.EXPORT, { params: { ...params, format } })
  }
}

export const attendanceApi = new AttendanceApi()
export default attendanceApi
