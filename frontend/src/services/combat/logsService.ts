import { apiFactory } from '../core/apiService'
import { API_ENDPOINTS } from '@/config/apiEndpoints'
import type { ApiResponse } from '@/types/api'

export interface LogListParams {
  page?: number
  page_size?: number
  parse_status?: string | null
  search?: string | null
  server?: string | null
  map_name?: string | null
}

export interface LogUploadParams {
  server?: string | null
  map_name?: string | null
  guild_tag?: string | null
  auto_parse?: boolean
}

export interface LogUpdate {
  server?: string
  map_name?: string
  guild_tag?: string
}

export interface BatchParseParams {
  task_name?: string
  log_ids: number[]
  overwrite?: boolean
}

export class LogsService {
  async getLogs(params: LogListParams): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(API_ENDPOINTS.LOGS.LIST, { params })
  }

  async uploadLog(file: File, params: LogUploadParams, onProgress?: (percent: number) => void): Promise<ApiResponse<any>> {
    const formData = new FormData()
    formData.append('file', file)
    Object.keys(params).forEach(key => {
      if (params[key as keyof LogUploadParams] !== undefined) {
        formData.append(key, String(params[key as keyof LogUploadParams]))
      }
    })
    return apiFactory.post<any>(API_ENDPOINTS.LOGS.LIST, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: onProgress ? (e) => {
        if (e.total) {
          onProgress(Math.round((e.loaded * 100) / e.total))
        }
      } : undefined
    })
  }

  async getLog(logId: number): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(API_ENDPOINTS.LOGS.DETAIL(logId))
  }

  async deleteLog(logId: number): Promise<ApiResponse<void>> {
    return apiFactory.delete<void>(API_ENDPOINTS.LOGS.DELETE(logId))
  }

  async updateLog(logId: number, data: LogUpdate): Promise<ApiResponse<void>> {
    return apiFactory.put<void>(API_ENDPOINTS.LOGS.UPDATE(logId), data)
  }

  async parseLog(logId: number): Promise<ApiResponse<any>> {
    return apiFactory.post<any>(API_ENDPOINTS.LOGS.PARSE(logId))
  }

  async getParseProgress(logId: number): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(API_ENDPOINTS.LOGS.PARSE_PROGRESS(logId))
  }

  async getParseResult(logId: number): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(API_ENDPOINTS.LOGS.PARSE_RESULT(logId))
  }

  async getFightInfo(logId: number): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(API_ENDPOINTS.LOGS.FIGHT_INFO(logId))
  }

  async getPlayersStats(logId: number): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(API_ENDPOINTS.LOGS.PLAYERS_STATS(logId))
  }

  async getPlayerStats(logId: number, accountName: string): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(API_ENDPOINTS.LOGS.PLAYER_STATS(logId, accountName))
  }

  async getPlayerBuffs(logId: number, accountName: string): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(API_ENDPOINTS.LOGS.PLAYER_BUFFS(logId, accountName))
  }

  async getPlayerRotation(logId: number, accountName: string): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(API_ENDPOINTS.LOGS.PLAYER_ROTATION(logId, accountName))
  }

  async getRawParsedData(logId: number): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(API_ENDPOINTS.LOGS.RAW_DATA(logId))
  }

  async validateParsedData(logId: number): Promise<ApiResponse<any>> {
    return apiFactory.post<any>(API_ENDPOINTS.LOGS.VALIDATE(logId))
  }

  async batchDeleteLogs(logIds: number[]): Promise<ApiResponse<void>> {
    return apiFactory.post<void>(API_ENDPOINTS.LOGS.BATCH_DELETE, logIds)
  }

  async batchParseLogs(params: BatchParseParams): Promise<ApiResponse<any>> {
    return apiFactory.post<any>(API_ENDPOINTS.LOGS.BATCH_PARSE, params)
  }

  async checkSha256(sha256: string): Promise<ApiResponse<any>> {
    return apiFactory.post<any>(`${API_ENDPOINTS.LOGS.CHECK_SHA256}?sha256=${sha256}`)
  }

}

export const logsService = new LogsService()