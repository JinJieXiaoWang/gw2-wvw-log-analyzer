/**
 * 事件监听器管理器
 * 功能：统一管理 window/document 上的事件监听器，确保组件卸载时正确清理
 * 作者：System
 * 创建日期：2026-05-10
 */

type EventHandler = (...args: any[]) => void

interface ListenerInfo {
  handler: EventHandler
  options?: AddEventListenerOptions
}

export class EventListenerManager {
  private static instance: EventListenerManager
  private listeners: Map<string, Map<EventHandler, ListenerInfo>> = new Map()
  private eventTarget: Window | Document = window

  private constructor() {}

  static getInstance(): EventListenerManager {
    if (!EventListenerManager.instance) {
      EventListenerManager.instance = new EventListenerManager()
    }
    return EventListenerManager.instance
  }

  /**
   * 添加事件监听器
   * @param event 事件名称
   * @param handler 事件处理函数
   * @param options 事件监听选项
   */
  add(
    event: string,
    handler: EventHandler,
    options?: AddEventListenerOptions
  ): void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Map())
    }

    const eventListeners = this.listeners.get(event)!
    eventListeners.set(handler, { handler, options })

    this.eventTarget.addEventListener(event, handler, options)
  }

  /**
   * 移除事件监听器
   * @param event 事件名称
   * @param handler 事件处理函数
   */
  remove(event: string, handler: EventHandler): void {
    const eventListeners = this.listeners.get(event)
    if (eventListeners) {
      const info = eventListeners.get(handler)
      if (info) {
        this.eventTarget.removeEventListener(event, handler, info.options)
        eventListeners.delete(handler)
      }
      if (eventListeners.size === 0) {
        this.listeners.delete(event)
      }
    }
  }

  /**
   * 移除特定事件的所有监听器
   * @param event 事件名称
   */
  removeAll(event: string): void {
    const eventListeners = this.listeners.get(event)
    if (eventListeners) {
      eventListeners.forEach((info, handler) => {
        this.eventTarget.removeEventListener(event, handler, info.options)
      })
      eventListeners.clear()
      this.listeners.delete(event)
    }
  }

  /**
   * 清空所有事件监听器
   */
  clear(): void {
    this.listeners.forEach((eventListeners, event) => {
      eventListeners.forEach((info, handler) => {
        this.eventTarget.removeEventListener(event, handler, info.options)
      })
    })
    this.listeners.clear()
  }

  /**
   * 获取事件监听器数量
   */
  getSize(event?: string): number {
    if (event) {
      return this.listeners.get(event)?.size || 0
    }
    let total = 0
    this.listeners.forEach((eventListeners) => {
      total += eventListeners.size
    })
    return total
  }

  /**
   * 检查事件是否有监听器
   */
  hasListeners(event: string): boolean {
    return (this.listeners.get(event)?.size || 0) > 0
  }

  /**
   * 获取所有已注册的事件列表
   */
  getEventList(): string[] {
    return Array.from(this.listeners.keys())
  }
}

export const eventListenerManager = EventListenerManager.getInstance()

export default EventListenerManager
