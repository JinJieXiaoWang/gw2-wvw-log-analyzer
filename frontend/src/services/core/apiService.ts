/**
 * API 服务层
 * 功能：提供标准化的 API 接口调用，包含请求拦截器和响应处理
 * 作者：System
 * 创建日期：2024-01-15
 */

import axios, { AxiosInstance, AxiosRequestConfig } from 'axios'
import type { ApiResponse, ApiError, PaginationParams, PaginatedResponse } from '@/types/api'
import { getToken, clearToken } from '@/utils/auth/tokenManager'
import { configManager } from '@/services/core/configManager'

export type { ApiResponse, ApiError, PaginationParams, PaginatedResponse }

// 记录连续失败次数
let consecutiveFailures = 0
let hasTriggeredUnavailable = false

class ApiFactory {
  private client: AxiosInstance

  constructor() {
    const apiConfig = configManager.get('api')
    this.client = axios.create({
      baseURL: apiConfig.baseUrl || 'http://localhost:8000/api/v1',
      timeout: apiConfig.timeout || 30000,
      headers: {
        'Content-Type': 'application/json'
      }
    })

    // 请求拦截器：自动附加 Token
    this.client.interceptors.request.use(
      (config) => {
        const token = getToken()
        if (token) {
          config.headers = config.headers || {}
          config.headers.Authorization = `Bearer ${token.accessToken}`
        }
        return config
      },
      (error) => Promise.reject(error)
    )

    // 响应拦截器：统一错误处理和 401 处理
    this.client.interceptors.response.use(
      (response) => {
        // 成功响应，重置失败计数
        consecutiveFailures = 0
        if (hasTriggeredUnavailable) {
          hasTriggeredUnavailable = false
          window.dispatchEvent(new CustomEvent('backend:available'))
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

        // 401 未授权：清除 Token 并触发登出事件，由应用层决定是否跳转
        // 避免在公开页面上因游客访问而强制跳转到登录页
        if (error.response?.status === 401) {
          console.warn('[ApiClient] Received 401 Unauthorized, clearing token...')
          clearToken()
          // 触发认证过期事件，传递来源信息
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
}

export const apiFactory = new ApiFactory()
export const HttpClient = apiFactory

// Token 管理已统一迁移到 @/utils/auth/tokenManager
// 请使用 saveAccessToken / getToken / clearToken / isLoggedIn 等函数