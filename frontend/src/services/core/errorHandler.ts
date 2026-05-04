/**
 * API错误处理工具
 * 功能：提供统一的错误处理、响应数据解析和错误提示机制
 * 作者：系统
 * 创建日期：2026-04-27
 */

import { ApiResponse } from './apiService'

export enum ErrorCode {
  NETWORK_ERROR = 'NETWORK_ERROR',
  TIMEOUT = 'TIMEOUT',
  UNAUTHORIZED = 'UNAUTHORIZED',
  FORBIDDEN = 'FORBIDDEN',
  NOT_FOUND = 'NOT_FOUND',
  VALIDATION_ERROR = 'VALIDATION_ERROR',
  SERVER_ERROR = 'SERVER_ERROR',
  UNKNOWN = 'UNKNOWN'
}

export enum ErrorSeverity {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical'
}

export interface ErrorContext {
  url?: string
  method?: string
  params?: Record<string, any>
  data?: any
  timestamp: number
}

export interface HandledError {
  code: ErrorCode
  message: string
  severity: ErrorSeverity
  context?: ErrorContext
  details?: any
  userMessage?: string
  canRetry?: boolean
}

export interface ValidationError {
  field: string
  message: string
  value?: any
}

export interface IResponseParser<T> {
  parse(data: any): T
  validate(data: any): boolean
  getValidationErrors(data: any): ValidationError[]
}

/**
 * 错误处理器类
 */
export class ErrorHandler {
  private static instance: ErrorHandler
  private errorHandlers: Map<ErrorCode, (error: HandledError) => void> = new Map()
  private globalErrorHandler?: (error: HandledError) => void

  private constructor() {
    this.setupDefaultHandlers()
  }

  static getInstance(): ErrorHandler {
    if (!ErrorHandler.instance) {
      ErrorHandler.instance = new ErrorHandler()
    }
    return ErrorHandler.instance
  }

  private setupDefaultHandlers(): void {
    this.registerHandler(ErrorCode.UNAUTHORIZED, (error) => {
      console.error('认证失败:', error)
      this.clearAuthTokens()
      this.redirectToLogin()
    })

    this.registerHandler(ErrorCode.FORBIDDEN, (error) => {
      console.error('权限不足:', error)
      this.showUserMessage('您没有权限执行此操作', ErrorSeverity.HIGH)
    })

    this.registerHandler(ErrorCode.NETWORK_ERROR, (error) => {
      console.error('网络错误:', error)
      this.showUserMessage('网络连接失败，请检查网络设置', ErrorSeverity.MEDIUM)
    })

    this.registerHandler(ErrorCode.TIMEOUT, (error) => {
      console.error('请求超时:', error)
      this.showUserMessage('请求超时，请稍后重试', ErrorSeverity.LOW)
    })

    this.registerHandler(ErrorCode.VALIDATION_ERROR, (error) => {
      console.error('数据验证失败:', error)
      this.showUserMessage('提交的数据格式不正确', ErrorSeverity.MEDIUM)
    })

    this.registerHandler(ErrorCode.SERVER_ERROR, (error) => {
      console.error('服务器错误:', error)
      this.showUserMessage('服务器内部错误，请联系管理员', ErrorSeverity.HIGH)
    })
  }

  registerHandler(code: ErrorCode, handler: (error: HandledError) => void): void {
    this.errorHandlers.set(code, handler)
  }

  setGlobalHandler(handler: (error: HandledError) => void): void {
    this.globalErrorHandler = handler
  }

  handle(error: any, context?: ErrorContext): HandledError {
    const handledError = this.parseError(error, context)
    
    if (this.globalErrorHandler) {
      this.globalErrorHandler(handledError)
    }

    const handler = this.errorHandlers.get(handledError.code)
    if (handler) {
      handler(handledError)
    }

    return handledError
  }

  private parseError(error: any, context?: ErrorContext): HandledError {
    if (error instanceof Error) {
      if (error.message.includes('timeout') || error.message.includes('Timeout')) {
        return {
          code: ErrorCode.TIMEOUT,
          message: error.message,
          severity: ErrorSeverity.LOW,
          context,
          userMessage: '请求超时，请稍后重试',
          canRetry: true
        }
      }
      if (error.message.includes('network') || error.message.includes('Network')) {
        return {
          code: ErrorCode.NETWORK_ERROR,
          message: error.message,
          severity: ErrorSeverity.MEDIUM,
          context,
          userMessage: '网络连接失败，请检查网络设置',
          canRetry: true
        }
      }
    }

    if (error.response) {
      const status = error.response.status
      switch (status) {
        case 401:
          return {
            code: ErrorCode.UNAUTHORIZED,
            message: '未授权访问',
            severity: ErrorSeverity.HIGH,
            context,
            userMessage: '登录已过期，请重新登录',
            canRetry: false
          }
        case 403:
          return {
            code: ErrorCode.FORBIDDEN,
            message: '权限不足',
            severity: ErrorSeverity.HIGH,
            context,
            userMessage: '您没有权限执行此操作',
            canRetry: false
          }
        case 404:
          return {
            code: ErrorCode.NOT_FOUND,
            message: '资源不存在',
            severity: ErrorSeverity.MEDIUM,
            context,
            userMessage: '请求的资源不存在',
            canRetry: false
          }
        case 422:
          return {
            code: ErrorCode.VALIDATION_ERROR,
            message: '数据验证失败',
            severity: ErrorSeverity.MEDIUM,
            context,
            details: error.response.data,
            userMessage: '提交的数据格式不正确',
            canRetry: false
          }
        case 500:
        case 502:
        case 503:
        case 504:
          return {
            code: ErrorCode.SERVER_ERROR,
            message: '服务器错误',
            severity: ErrorSeverity.HIGH,
            context,
            userMessage: '服务器内部错误，请联系管理员',
            canRetry: true
          }
        default:
          return {
            code: ErrorCode.UNKNOWN,
            message: `HTTP错误: ${status}`,
            severity: ErrorSeverity.MEDIUM,
            context,
            userMessage: '请求失败，请稍后重试',
            canRetry: true
          }
      }
    }

    return {
      code: ErrorCode.UNKNOWN,
      message: error.message || '未知错误',
      severity: ErrorSeverity.MEDIUM,
      context,
      userMessage: '发生未知错误，请稍后重试',
      canRetry: true
    }
  }

  private clearAuthTokens(): void {
    // 统一清除所有可能的认证存储键，防止"幽灵登录"
    localStorage.removeItem('gw2_wvw_auth')
    localStorage.removeItem('gw2_wvw_token')
    localStorage.removeItem('gw2_admin_access_token')
    localStorage.removeItem('gw2_admin_token_expiry')
    localStorage.removeItem('gw2_wvw_refresh_token')
  }

  private redirectToLogin(): void {
    window.dispatchEvent(new CustomEvent('auth:logout', { detail: { reason: 'token_expired' } }))
  }

  private showUserMessage(message: string, severity: ErrorSeverity): void {
    window.dispatchEvent(new CustomEvent('notification:show', {
      detail: {
        message,
        severity,
        duration: severity === ErrorSeverity.HIGH ? 5000 : 3000
      }
    }))
  }
}

/**
 * 响应数据解析器
 */
export class ResponseParser {
  static parseResponse<T>(response: ApiResponse<T>): T {
    if (!response.success) {
      throw response.error || new Error('请求失败')
    }
    return response.data as T
  }

  static parsePaginatedResponse<T>(response: ApiResponse<any>): {
    items: T[]
    total: number
    page: number
    pageSize: number
    totalPages: number
  } {
    const data = this.parseResponse(response)
    return {
      items: data.items || [],
      total: data.total || 0,
      page: data.page || 1,
      pageSize: data.page_size || 20,
      totalPages: Math.ceil((data.total || 0) / (data.page_size || 20))
    }
  }

  static validateResponse<T>(response: ApiResponse<T>, validator?: (data: T) => boolean): boolean {
    if (!response.success) {
      return false
    }
    if (validator && response.data) {
      return validator(response.data)
    }
    return true
  }

  static extractError(response: ApiResponse): string {
    if (response.error) {
      if (response.error instanceof Error) {
        return response.error.message || '未知错误'
      }
      return response.error.message || (response.error.details && response.error.details.message) || '未知错误'
    }
    return '请求失败'
  }

  static isSuccess(response: ApiResponse): boolean {
    return response.success === true
  }

  static hasError(response: ApiResponse): boolean {
    return response.success === false && !!response.error
  }
}

/**
 * 数据验证器
 */
export class DataValidator {
  static validateRequired(value: any, fieldName: string): ValidationError[] {
    const errors: ValidationError[] = []
    if (value === undefined || value === null || value === '') {
      errors.push({
        field: fieldName,
        message: `${fieldName}不能为空`,
        value
      })
    }
    return errors
  }

  static validateEmail(value: string, fieldName: string): ValidationError[] {
    const errors: ValidationError[] = []
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (value && !emailRegex.test(value)) {
      errors.push({
        field: fieldName,
        message: `${fieldName}格式不正确`,
        value
      })
    }
    return errors
  }

  static validateLength(value: string, fieldName: string, min: number, max: number): ValidationError[] {
    const errors: ValidationError[] = []
    if (value && (value.length < min || value.length > max)) {
      errors.push({
        field: fieldName,
        message: `${fieldName}长度必须在${min}-${max}之间`,
        value
      })
    }
    return errors
  }

  static validateNumber(value: any, fieldName: string, min?: number, max?: number): ValidationError[] {
    const errors: ValidationError[] = []
    const num = Number(value)
    if (isNaN(num)) {
      errors.push({
        field: fieldName,
        message: `${fieldName}必须是数字`,
        value
      })
    } else if (min !== undefined && num < min) {
      errors.push({
        field: fieldName,
        message: `${fieldName}不能小于${min}`,
        value
      })
    } else if (max !== undefined && num > max) {
      errors.push({
        field: fieldName,
        message: `${fieldName}不能大于${max}`,
        value
      })
    }
    return errors
  }

  static validateDate(value: string, fieldName: string): ValidationError[] {
    const errors: ValidationError[] = []
    const date = new Date(value)
    if (isNaN(date.getTime())) {
      errors.push({
        field: fieldName,
        message: `${fieldName}格式不正确`,
        value
      })
    }
    return errors
  }

  static validateEnum(value: any, fieldName: string, enumValues: any[]): ValidationError[] {
    const errors: ValidationError[] = []
    if (value && !enumValues.includes(value)) {
      errors.push({
        field: fieldName,
        message: `${fieldName}的值无效`,
        value
      })
    }
    return errors
  }
}

/**
 * API响应包装器
 */
export class ApiResponseWrapper {
  static async wrap<T>(
    promise: Promise<ApiResponse<T>>,
    options?: {
      showSuccessMessage?: boolean
      successMessage?: string
      showErrorMessage?: boolean
      errorHandler?: (error: HandledError) => void
    }
  ): Promise<{ success: boolean; data?: T; error?: HandledError }> {
    try {
      const response = await promise
      
      if (!ResponseParser.isSuccess(response)) {
        const handledError = ErrorHandler.getInstance().handle(response.error, {
          timestamp: Date.now()
        })
        
        if (options?.showErrorMessage !== false) {
          window.dispatchEvent(new CustomEvent('notification:show', {
            detail: {
              message: handledError.userMessage || '请求失败',
              severity: handledError.severity,
              duration: 3000
            }
          }))
        }

        if (options?.errorHandler) {
          options.errorHandler(handledError)
        }

        return { success: false, error: handledError }
      }

      if (options?.showSuccessMessage) {
        window.dispatchEvent(new CustomEvent('notification:show', {
          detail: {
            message: options.successMessage || '操作成功',
            severity: 'low',
            duration: 2000
          }
        }))
      }

      return { success: true, data: response.data }
    } catch (error) {
      const handledError = ErrorHandler.getInstance().handle(error, {
        timestamp: Date.now()
      })
      
      if (options?.showErrorMessage !== false) {
        window.dispatchEvent(new CustomEvent('notification:show', {
          detail: {
            message: handledError.userMessage || '请求失败',
            severity: handledError.severity,
            duration: 3000
          }
        }))
      }

      if (options?.errorHandler) {
        options.errorHandler(handledError)
      }

      return { success: false, error: handledError }
    }
  }
}

export const errorHandler = ErrorHandler.getInstance()