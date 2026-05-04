/**
 * 增强型错误处理工具
 * 功能：提供更强大的错误处理机制，与原 errorHandler.ts 兼容
 * 作者：System
 * 创建日期：2026-04-29
 */

/**
 * 自定义错误类
 */
export class AppError extends Error {
  public code: string;
  public details?: any;

  constructor(message: string, code: string = 'UNKNOWN_ERROR', details?: any) {
    super(message);
    this.name = 'AppError';
    this.code = code;
    this.details = details;

    // 保持正确的堆栈追踪
    if (typeof (Error as any).captureStackTrace === 'function') {
      (Error as any).captureStackTrace(this, AppError);
    }
  }
}

/**
 * 错误代码枚举
 */
export enum ErrorCode {
  NETWORK_ERROR = 'NETWORK_ERROR',
  AUTH_ERROR = 'AUTH_ERROR',
  VALIDATION_ERROR = 'VALIDATION_ERROR',
  NOT_FOUND = 'NOT_FOUND',
  PERMISSION_DENIED = 'PERMISSION_DENIED',
  INTERNAL_ERROR = 'INTERNAL_ERROR',
  UNKNOWN_ERROR = 'UNKNOWN_ERROR'
}

/**
 * 错误处理结果接口
 */
export interface ErrorHandleResult {
  success: boolean;
  error?: AppError;
  message: string;
}

/**
 * 错误处理器类
 */
class ErrorHandler {
  private listeners: Set<(error: AppError) => void> = new Set();

  /**
   * 添加错误监听器
   */
  addListener(listener: (error: AppError) => void): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  /**
   * 通知所有监听器
   */
  private notifyListeners(error: AppError): void {
    this.listeners.forEach(listener => {
      try {
        listener(error);
      } catch (err) {
        console.error('Error in error listener:', err);
      }
    });
  }

  /**
   * 处理错误
   */
  handle(error: any, context?: string): ErrorHandleResult {
    const appError = this.normalize(error, context);
    this.log(appError);
    this.notifyListeners(appError);
    
    return {
      success: false,
      error: appError,
      message: appError.message
    };
  }

  /**
   * 标准化错误
   */
  normalize(error: any, context?: string): AppError {
    if (error instanceof AppError) {
      return error;
    }

    if (error instanceof Error) {
      return new AppError(
        context ? `${context}: ${error.message}` : error.message,
        this.guessErrorCode(error),
        { stack: error.stack }
      );
    }

    return new AppError(
      context ? `${context}: ${String(error)}` : String(error),
      ErrorCode.UNKNOWN_ERROR
    );
  }

  /**
   * 根据错误类型猜测错误代码
   */
  private guessErrorCode(error: Error): string {
    const message = error.message.toLowerCase();
    
    if (message.includes('network') || message.includes('fetch') || message.includes('timeout')) {
      return ErrorCode.NETWORK_ERROR;
    }
    
    if (message.includes('auth') || message.includes('login') || message.includes('unauthorized')) {
      return ErrorCode.AUTH_ERROR;
    }
    
    if (message.includes('validation') || message.includes('invalid')) {
      return ErrorCode.VALIDATION_ERROR;
    }
    
    if (message.includes('not found') || message.includes('404')) {
      return ErrorCode.NOT_FOUND;
    }
    
    if (message.includes('permission') || message.includes('denied') || message.includes('403')) {
      return ErrorCode.PERMISSION_DENIED;
    }
    
    return ErrorCode.INTERNAL_ERROR;
  }

  /**
   * 记录错误日志
   */
  log(error: AppError): void {
    const logData = {
      timestamp: new Date().toISOString(),
      code: error.code,
      message: error.message,
      details: error.details,
      stack: error.stack
    };

    console.error('[App Error]', logData);
  }

  /**
   * 创建成功结果
   */
  success(): ErrorHandleResult {
    return {
      success: true,
      message: 'Operation completed successfully'
    };
  }

  /**
   * 创建错误结果
   */
  createError(message: string, code: string = ErrorCode.UNKNOWN_ERROR, details?: any): ErrorHandleResult {
    const error = new AppError(message, code, details);
    return this.handle(error);
  }

  /**
   * 安全执行异步函数
   */
  async safeExecute<T>(
    fn: () => Promise<T>,
    context?: string
  ): Promise<{ success: true; data: T } | (ErrorHandleResult & { data: undefined })> {
    try {
      const data = await fn();
      return { success: true, data };
    } catch (error) {
      const result = this.handle(error, context);
      return { ...result, data: undefined };
    }
  }

  /**
   * 安全执行同步函数
   */
  safeExecuteSync<T>(
    fn: () => T,
    context?: string
  ): { success: true; data: T } | (ErrorHandleResult & { data: undefined }) {
    try {
      const data = fn();
      return { success: true, data };
    } catch (error) {
      const result = this.handle(error, context);
      return { ...result, data: undefined };
    }
  }
}

// 导出单例
export const advancedErrorHandler = new ErrorHandler();

/**
 * 便捷函数：安全执行
 */
export function safe<T>(fn: () => Promise<T>, context?: string): Promise<any> {
  return advancedErrorHandler.safeExecute(fn, context);
}

/**
 * 便捷函数：安全执行同步
 */
export function safeSync<T>(fn: () => T, context?: string): ReturnType<ErrorHandler['safeExecuteSync']> {
  return advancedErrorHandler.safeExecuteSync(fn, context);
}

/**
 * 便捷函数：创建错误
 */
export function createAppError(message: string, code?: string, details?: any): AppError {
  return new AppError(message, code, details);
}
