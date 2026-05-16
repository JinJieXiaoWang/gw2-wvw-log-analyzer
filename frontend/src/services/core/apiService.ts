/**
 * API 服务层
 * 功能：提供标准化的 API 接口调用，唯一 HTTP 客户端入口
 * 作者：System
 * 创建日期：2024-01-15
 * 更新：2026-05-15 - 统一封装为项目唯一 axios 实例
 */

import { configManager } from '@/services/core/configManager'
import type { ApiError, ApiResponse, PaginatedResponse, PaginationParams } from '@/types/api'
import { clearToken, getToken } from '@/utils/auth/tokenManager'
import axios, { AxiosInstance, AxiosRequestConfig } from 'axios'

export type { ApiError, ApiResponse, PaginatedResponse, PaginationParams }

// 记录连续失败次数
let consecutiveFailures = 0
let hasTriggeredUnavailable = false

/**
 * 将 params 对象转为 URL 查询字符串
 */
function tansParams(params: Record<string, any>): string {
  const parts: string[] = []
  for (const key in params) {
    if (params[key] !== undefined && params[key] !== null) {
      parts.push(`${encodeURIComponent(key)}=${encodeURIComponent(params[key])}`)
    }
  }
  return parts.join('&')
}

class ApiFactory {
  private client: AxiosInstance

  constructor() {
    const apiConfig = configManager.get('api')
    this.client = axios.create({
      baseURL: apiConfig.baseUrl || '/api/v1',
      timeout: apiConfig.timeout || 30000,
      headers: {
        'Content-Type': 'application/json'
      }
    })

    // ========== 请求拦截器 ==========
    this.client.interceptors.request.use(
      (config) => {
        const token = getToken()
        if (token) {
          config.headers = config.headers || {}
          config.headers.Authorization = `Bearer ${token.accessToken}`
        }

        // GET 请求：将 params 拼接到 URL（避免 axios 对数组参数的默认序列化问题）
        if (config.method === 'get' && config.params) {
          const queryString = tansParams(config.params)
          if (queryString) {
            config.url = config.url + (config.url?.includes('?') ? '&' : '?') + queryString
          }
          config.params = {} // 清空，避免 axios 重复拼接
        }

        return config
      },
      (error) => Promise.reject(error)
    )

    // ========== 响应拦截器 ==========
    this.client.interceptors.response.use(
      (response) => {
        // 成功响应，重置失败计数
        consecutiveFailures = 0
        if (hasTriggeredUnavailable) {
          hasTriggeredUnavailable = false
          window.dispatchEvent(new CustomEvent('backend:available'))
        }

        // 二进制数据直接返回（blob / arraybuffer）
        const responseType = response.config.responseType
        if (responseType === 'blob' || responseType === 'arraybuffer') {
          return response.data
        }

        return response.data
      },
      (error) => {
        const response = error.response?.data || {}
        const message = response.message || error.message || '请求失败'

        // 检测网络错误或连接失败
        const isNetworkError = !error.response ||
          error.code === 'ERR_NETWORK' ||
          error.message?.includes('Network Error') ||
          error.message?.includes('timeout') ||
          error.response?.status === 0

        if (isNetworkError) {
          consecutiveFailures++

          // 如果连续失败3次，触发服务不可用警告
          if (consecutiveFailures >= 3 && !hasTriggeredUnavailable) {
            hasTriggeredUnavailable = true
            window.dispatchEvent(new CustomEvent('backend:unavailable', {
              detail: { message: '无法连接到后端服务器，请检查服务是否正常运行' }
            }))
          }
        } else {
          // 有响应但出错，重置连续失败计数（服务是可用的）
          consecutiveFailures = 0
        }

        // 401 未授权：清除 Token 并触发登出事件
        if (error.response?.status === 401) {
          console.warn('[ApiClient] Received 401 Unauthorized, clearing token...')
          clearToken()
          window.dispatchEvent(new CustomEvent('auth:logout', {
            detail: { source: 'api', path: window.location.pathname }
          }))
        }

        return Promise.reject({
          success: false,
          code: error.response?.status || 500,
          message,
          data: null,
          errors: response.errors
        })
      }
    )
  }

  getClient(): AxiosInstance {
    return this.client
  }

  async get<T = any>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    return this.client.get(url, config)
  }

  async post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    return this.client.post(url, data, config)
  }

  async put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    return this.client.put(url, data, config)
  }

  async delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    return this.client.delete(url, config)
  }

  /**
   * 下载文件（返回 Blob）
   * 调用时请设置 config.responseType = 'blob'，拦截器会自动返回原始二进制数据
   */
  async download(url: string, config?: AxiosRequestConfig): Promise<Blob> {
    return this.client.get(url, {
      ...config,
      responseType: 'blob'
    })
  }
}

export const apiFactory = new ApiFactory()
export const HttpClient = apiFactory

// Token 管理已统一迁移到 @/utils/auth/tokenManager
// 请使用 saveAccessToken / getToken / clearToken / isLoggedIn 等函数
