/**
 * 错误处理工具模块
 * 功能：统一的错误处理、错误类型定义、错误提示和日志记录
 * 作者：帅姐姐
 * 创建日期：2024-01-15
 */

// 错误类型枚举
export enum ErrorCode {
  NETWORK_ERROR = 'NETWORK_ERROR',
  TIMEOUT = 'TIMEOUT',
  UNAUTHORIZED = 'UNAUTHORIZED',
  FORBIDDEN = 'FORBIDDEN',
  NOT_FOUND = 'NOT_FOUND',
  VALIDATION_ERROR = 'VALIDATION_ERROR',
  SERVER_ERROR = 'SERVER_ERROR',
  UNKNOWN_ERROR = 'UNKNOWN_ERROR',
  UPLOAD_FAILED = 'UPLOAD_FAILED',
  PARSE_FAILED = 'PARSE_FAILED'
}

// 自定义应用错误类
export class AppError extends Error {
  code: ErrorCode
  details?: any
  isUserFriendly: boolean

  constructor(
    code: ErrorCode,
    message: string,
    details?: any,
    isUserFriendly: boolean = true
  ) {
    super(message)
    this.name = 'AppError'
    this.code = code
    this.details = details
    this.isUserFriendly = isUserFriendly
    Object.setPrototypeOf(this, new.target.prototype)
  }
}

// 错误消息映射
const ERROR_MESSAGES: Record<ErrorCode, string> = {
  [ErrorCode.NETWORK_ERROR]: '网络连接失败，请检查您的网络设置',
  [ErrorCode.TIMEOUT]: '请求超时，请稍后重试',
  [ErrorCode.UNAUTHORIZED]: '登录已过期，请重新登录',
  [ErrorCode.FORBIDDEN]: '您没有权限执行此操作',
  [ErrorCode.NOT_FOUND]: '请求的资源不存在',
  [ErrorCode.VALIDATION_ERROR]: '数据验证失败，请检查您的输入',
  [ErrorCode.SERVER_ERROR]: '服务器发生错误，请稍后重试',
  [ErrorCode.UNKNOWN_ERROR]: '发生未知错误，请稍后重试',
  [ErrorCode.UPLOAD_FAILED]: '文件上传失败，请重试',
  [ErrorCode.PARSE_FAILED]: '日志解析失败，请检查文件格式'
}

/**
 * 获取用户友好的错误消息
 */
export function getErrorMessage(error: any): string {
  if (error instanceof AppError) {
    if (error.isUserFriendly) {
      return error.message
    }
    return ERROR_MESSAGES[error.code] || ERROR_MESSAGES[ErrorCode.UNKNOWN_ERROR]
  }
  
  if (error instanceof Error) {
    return error.message
  }
  
  if (typeof error === 'string') {
    return error
  }
  
  return ERROR_MESSAGES[ErrorCode.UNKNOWN_ERROR]
}

/**
 * 从 HTTP 响应创建 AppError
 */
export function createErrorFromResponse(
  status: number,
  data?: any
): AppError {
  let code: ErrorCode
  let message: string
  
  switch (status) {
    case 400:
      code = ErrorCode.VALIDATION_ERROR
      message = data?.message || ERROR_MESSAGES[ErrorCode.VALIDATION_ERROR]
      break
    case 401:
      code = ErrorCode.UNAUTHORIZED
      message = ERROR_MESSAGES[ErrorCode.UNAUTHORIZED]
      break
    case 403:
      code = ErrorCode.FORBIDDEN
      message = ERROR_MESSAGES[ErrorCode.FORBIDDEN]
      break
    case 404:
      code = ErrorCode.NOT_FOUND
      message = ERROR_MESSAGES[ErrorCode.NOT_FOUND]
      break
    case 408:
      code = ErrorCode.TIMEOUT
      message = ERROR_MESSAGES[ErrorCode.TIMEOUT]
      break
    case 413:
      code = ErrorCode.UPLOAD_FAILED
      message = '文件过大，请选择更小的文件'
      break
    case 500:
    case 502:
    case 503:
    case 504:
      code = ErrorCode.SERVER_ERROR
      message = data?.message || ERROR_MESSAGES[ErrorCode.SERVER_ERROR]
      break
    default:
      code = ErrorCode.UNKNOWN_ERROR
      message = data?.message || ERROR_MESSAGES[ErrorCode.UNKNOWN_ERROR]
  }
  
  return new AppError(code, message, data)
}

/**
 * 从错误对象创建 AppError
 */
export function createErrorFromError(
  error: any,
  defaultCode: ErrorCode = ErrorCode.UNKNOWN_ERROR
): AppError {
  if (error instanceof AppError) {
    return error
  }
  
  if (error.name === 'AbortError') {
    return new AppError(ErrorCode.TIMEOUT, ERROR_MESSAGES[ErrorCode.TIMEOUT])
  }
  
  if (error.name === 'TypeError' && error.message.includes('fetch')) {
    return new AppError(ErrorCode.NETWORK_ERROR, ERROR_MESSAGES[ErrorCode.NETWORK_ERROR])
  }
  
  return new AppError(defaultCode, getErrorMessage(error))
}

/**
 * 记录错误日志
 */
export function logError(error: any, context?: string) {
  const errorInfo = {
    timestamp: new Date().toISOString(),
    context,
    error: error instanceof Error ? {
      name: error.name,
      message: error.message,
      stack: error.stack
    } : error
  }
  
  // 开发环境输出到控制台
  if (import.meta.env.DEV) {
    console.error('[Error]', errorInfo)
  }
  
  // 生产环境可以发送到错误监控服务
  // TODO: 实现错误上报
}

/**
 * 错误边界钩子（用于组件）
 */
export function useErrorHandler() {
  const handleError = (error: any, context?: string) => {
    const appError = createErrorFromError(error)
    logError(appError, context)
    return appError
  }
  
  const throwError = (code: ErrorCode, message?: string, details?: any) => {
    const error = new AppError(code, message || ERROR_MESSAGES[code], details)
    logError(error)
    throw error
  }
  
  return {
    handleError,
    throwError,
    getErrorMessage,
    ErrorCode
  }
}

export default {
  AppError,
  ErrorCode,
  getErrorMessage,
  createErrorFromResponse,
  createErrorFromError,
  logError,
  useErrorHandler
}
