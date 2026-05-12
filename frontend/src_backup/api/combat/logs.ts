/**
 * 日志管理 API
 * 功能：处理日志上传、解析、查询、删除等操作
 * 作者：帅姐姐
 * 创建日期：2024-01-15
 */

import { HttpClient } from '../../services/core/apiService'
import { API_ENDPOINTS } from '@/config/apiEndpoints'

export interface LogEntry {
  id: string
  fileName: string
  fileSize: number
  mapName: string
  serverName: string
  date: string
  duration: string
  playerCount: number
  status: 'pending' | 'parsing' | 'completed' | 'error'
  uploadedAt: string
  parsedAt?: string
  metadata?: LogMetadata
}

export interface LogMetadata {
  version: string
  gameVersion: string
  bossId?: string
  bossName?: string
  isCm?: boolean
  duration: number
  success: boolean
}

export interface LogQueryParams {
  page?: number
  pageSize?: number
  search?: string
  map?: string
  server?: string
  dateFrom?: string
  dateTo?: string
  status?: string
  sortBy?: string
  sortOrder?: 'asc' | 'desc'
}

class LogsApi {
  /**
   * 获取日志列表
   */
  async getLogs(params?: LogQueryParams) {
    return await HttpClient.get<LogEntry[]>(API_ENDPOINTS.LOGS.LIST, { params })
  }

  /**
   * 获取日志详情
   */
  async getLogDetail(id: string) {
    return await HttpClient.get<any>(API_ENDPOINTS.LOGS.DETAIL(id))
  }

  /**
   * 上传日志文件
   */
  async uploadLog(file: File, onProgress?: (percent: number) => void) {
    const formData = new FormData()
    formData.append('file', file)
    return await HttpClient.post<any>(API_ENDPOINTS.LOGS.UPLOAD, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: onProgress ? (e) => {
        if (e.total) {
          onProgress(Math.round((e.loaded * 100) / e.total))
        }
      } : undefined
    })
  }

  /**
   * 解析日志
   */
  async parseLog(id: string) {
    return await HttpClient.post<any>(`/api/v1/logs/${id}/parse`)
  }

  /**
   * 删除日志
   */
  async deleteLog(id: string) {
    return await HttpClient.delete<void>(API_ENDPOINTS.LOGS.DELETE(id))
  }

  /**
   * 批量删除日志
   */
  async batchDeleteLogs(ids: string[]) {
    return await HttpClient.post<void>(API_ENDPOINTS.LOGS.BATCH_DELETE, { ids })
  }

  /**
   * 下载日志文件
   */
  async downloadLog(id: string): Promise<Blob> {
    const response = await HttpClient.getClient().get(API_ENDPOINTS.LOGS.DOWNLOAD(id), {
      responseType: 'blob'
    })
    return response.data as Blob
  }

  /**
   * 获取指定玩家的统计信息
   */
  async getPlayerStats(logId: string, accountName: string) {
    return await HttpClient.get<any>(API_ENDPOINTS.LOGS.PLAYER_STATS(logId, accountName))
  }

  /**
   * 获取指定玩家的BUFF覆盖率
   */
  async getPlayerBuffs(logId: string, accountName: string) {
    return await HttpClient.get<any>(API_ENDPOINTS.LOGS.PLAYER_BUFFS(logId, accountName))
  }
}

export const logsApi = new LogsApi()
export default logsApi
