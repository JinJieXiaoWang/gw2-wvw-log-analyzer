/**
 * 定时器管理器
 * 功能：统一管理 setInterval 和 setTimeout，避免内存泄漏
 * 作者：System
 * 创建日期：2026-05-10
 */

type TimerId = ReturnType<typeof setInterval> | ReturnType<typeof setTimeout>

interface TimerInfo {
  id: TimerId
  type: 'interval' | 'timeout'
  callback: (...args: any[]) => void
}

export class TimerManager {
  private static instance: TimerManager
  private timers: Map<string, TimerInfo> = new Map()

  private constructor() {}

  static getInstance(): TimerManager {
    if (!TimerManager.instance) {
      TimerManager.instance = new TimerManager()
    }
    return TimerManager.instance
  }

  /**
   * 设置定时器
   * @param name 定时器名称（唯一标识）
   * @param callback 回调函数
   * @param delay 延迟时间（毫秒）
   * @param type 定时器类型
   */
  set(
    name: string,
    callback: (...args: any[]) => void,
    delay: number,
    type: 'interval' | 'timeout' = 'interval'
  ): TimerId {
    this.clear(name)

    let id: TimerId
    if (type === 'interval') {
      id = setInterval(callback, delay)
    } else {
      id = setTimeout(callback, delay)
    }

    this.timers.set(name, { id, type, callback })
    return id
  }

  /**
   * 设置间隔定时器
   */
  setInterval(name: string, callback: (...args: any[]) => void, delay: number): TimerId {
    return this.set(name, callback, delay, 'interval')
  }

  /**
   * 设置超时定时器
   */
  setTimeout(name: string, callback: (...args: any[]) => void, delay: number): TimerId {
    return this.set(name, callback, delay, 'timeout')
  }

  /**
   * 清除指定定时器
   */
  clear(name: string): boolean {
    const timer = this.timers.get(name)
    if (timer) {
      if (timer.type === 'interval') {
        clearInterval(timer.id)
      } else {
        clearTimeout(timer.id)
      }
      this.timers.delete(name)
      return true
    }
    return false
  }

  /**
   * 检查定时器是否存在
   */
  has(name: string): boolean {
    return this.timers.has(name)
  }

  /**
   * 获取定时器信息
   */
  get(name: string): TimerInfo | undefined {
    return this.timers.get(name)
  }

  /**
   * 清除所有定时器
   */
  clearAll(): void {
    this.timers.forEach((timer) => {
      if (timer.type === 'interval') {
        clearInterval(timer.id)
      } else {
        clearTimeout(timer.id)
      }
    })
    this.timers.clear()
  }

  /**
   * 获取定时器数量
   */
  get size(): number {
    return this.timers.size
  }

  /**
   * 获取所有定时器名称
   */
  getTimerNames(): string[] {
    return Array.from(this.timers.keys())
  }
}

export const timerManager = TimerManager.getInstance()

export default TimerManager
