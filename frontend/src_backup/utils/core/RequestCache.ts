/**
 * 请求缓存管理器
 * 功能：提供统一的 API 请求缓存，支持 TTL 过期和手动清理
 * 作者：System
 * 创建日期：2026-05-10
 */

import { CACHE_CONFIG } from '@/config/app.config'

interface CacheItem<T> {
  data: T
  timestamp: number
  key: string
}

type CacheKey = string

export class RequestCache {
  private cache: Map<CacheKey, CacheItem<any>> = new Map()
  private readonly ttl: number

  constructor(ttl: number = CACHE_CONFIG.REQUEST_CACHE_TTL) {
    this.ttl = ttl
  }

  /**
   * 生成缓存键
   */
  static generateKey(url: string, params?: Record<string, any>): string {
    const paramStr = params ? JSON.stringify(params) : ''
    return `${url}::${paramStr}`
  }

  /**
   * 获取缓存数据
   */
  get<T>(key: string): T | null {
    const item = this.cache.get(key)
    if (!item) return null

    const isExpired = Date.now() - item.timestamp > this.ttl
    if (isExpired) {
      this.cache.delete(key)
      return null
    }

    return item.data as T
  }

  /**
   * 设置缓存数据
   */
  set<T>(key: string, data: T): void {
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      key
    })
  }

  /**
   * 检查缓存是否存在且有效
   */
  has(key: string): boolean {
    return this.get(key) !== null
  }

  /**
   * 删除指定缓存
   */
  delete(key: string): boolean {
    return this.cache.delete(key)
  }

  /**
   * 清空所有缓存
   */
  clear(): void {
    this.cache.clear()
  }

  /**
   * 获取缓存数量
   */
  get size(): number {
    return this.cache.size
  }

  /**
   * 清理过期缓存
   */
  cleanup(): number {
    const now = Date.now()
    let cleaned = 0

    this.cache.forEach((item, key) => {
      if (now - item.timestamp > this.ttl) {
        this.cache.delete(key)
        cleaned++
      }
    })

    return cleaned
  }
}

export const requestCache = new RequestCache()

export default RequestCache
