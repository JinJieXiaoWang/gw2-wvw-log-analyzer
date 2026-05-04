/**
 * 性能优化工具
 * 功能：提供性能监控和优化相关的工具函数
 * 作者：System
 * 创建日期：2026-04-29
 */

// 性能监控数据
interface PerformanceMetrics {
  name: string;
  startTime: number;
  duration: number;
}

// 性能监控器
class PerformanceMonitor {
  private metrics: Map<string, number> = new Map();
  private history: PerformanceMetrics[] = [];
  private maxHistory: number = 100;

  /**
   * 开始计时
   */
  start(name: string): void {
    this.metrics.set(name, performance.now());
  }

  /**
   * 结束计时
   */
  end(name: string): number {
    const startTime = this.metrics.get(name);
    if (!startTime) {
      console.warn(`No active timer for "${name}"`);
      return 0;
    }

    const duration = performance.now() - startTime;
    this.metrics.delete(name);

    this.history.push({
      name,
      startTime,
      duration
    });

    if (this.history.length > this.maxHistory) {
      this.history.shift();
    }

    return duration;
  }

  /**
   * 测量函数执行时间
   */
  measure<T>(name: string, fn: () => T): T {
    this.start(name);
    try {
      return fn();
    } finally {
      this.end(name);
    }
  }

  /**
   * 测量异步函数执行时间
   */
  async measureAsync<T>(name: string, fn: () => Promise<T>): Promise<T> {
    this.start(name);
    try {
      return await fn();
    } finally {
      this.end(name);
    }
  }

  /**
   * 获取所有性能指标
   */
  getMetrics(): PerformanceMetrics[] {
    return [...this.history];
  }

  /**
   * 获取平均执行时间
   */
  getAverageDuration(name: string): number | null {
    const filtered = this.history.filter(m => m.name === name);
    if (filtered.length === 0) return null;
    
    const total = filtered.reduce((sum, m) => sum + m.duration, 0);
    return total / filtered.length;
  }

  /**
   * 清除所有指标
   */
  clear(): void {
    this.metrics.clear();
    this.history = [];
  }

  /**
   * 打印性能报告
   */
  report(): void {
    const grouped = new Map<string, PerformanceMetrics[]>();
    
    this.history.forEach(m => {
      if (!grouped.has(m.name)) {
        grouped.set(m.name, []);
      }
      grouped.get(m.name)!.push(m);
    });

    console.group('Performance Report');
    grouped.forEach((metrics, name) => {
      const avg = metrics.reduce((sum, m) => sum + m.duration, 0) / metrics.length;
      const min = Math.min(...metrics.map(m => m.duration));
      const max = Math.max(...metrics.map(m => m.duration));
      
      console.log(`[${name}]`, {
        count: metrics.length,
        avg: `${avg.toFixed(2)}ms`,
        min: `${min.toFixed(2)}ms`,
        max: `${max.toFixed(2)}ms`
      });
    });
    console.groupEnd();
  }
}

// 导出单例
export const perfMonitor = new PerformanceMonitor();

/**
 * 装饰器风格的性能监控
 */
export function withPerformance<T extends (...args: any[]) => any>(
  name: string,
  fn: T
): T {
  return ((...args: any[]) => {
    return perfMonitor.measure(name, () => fn(...args));
  }) as T;
}

/**
 * 异步函数性能监控装饰器
 */
export function withPerformanceAsync<T extends (...args: any[]) => Promise<any>>(
  name: string,
  fn: T
): T {
  return ((...args: any[]) => {
    return perfMonitor.measureAsync(name, () => fn(...args));
  }) as T;
}

/**
 * 检查浏览器是否支持 IntersectionObserver
 */
export function supportsIntersectionObserver(): boolean {
  return typeof window !== 'undefined' && 'IntersectionObserver' in window;
}

/**
 * 检查浏览器是否支持 requestIdleCallback
 */
export function supportsRequestIdleCallback(): boolean {
  return typeof window !== 'undefined' && 'requestIdleCallback' in window;
}

/**
 * 安全的 requestIdleCallback，回退到 setTimeout
 */
export function safeRequestIdleCallback(callback: () => void, timeout?: number): number {
  if (supportsRequestIdleCallback()) {
    return (window as any).requestIdleCallback(callback, { timeout });
  }
  return window.setTimeout(callback, timeout || 0);
}

/**
 * 取消空闲回调
 */
export function safeCancelIdleCallback(id: number): void {
  if (supportsRequestIdleCallback()) {
    (window as any).cancelIdleCallback(id);
  } else {
    window.clearTimeout(id);
  }
}

/**
 * 批量执行任务，避免阻塞主线程
 */
export function batchTasks<T>(
  tasks: (() => T)[],
  batchSize: number = 10
): Promise<T[]> {
  return new Promise((resolve) => {
    const results: T[] = [];
    let index = 0;

    function processBatch() {
      const end = Math.min(index + batchSize, tasks.length);
      
      for (; index < end; index++) {
        results.push(tasks[index]());
      }

      if (index < tasks.length) {
        safeRequestIdleCallback(processBatch);
      } else {
        resolve(results);
      }
    }

    processBatch();
  });
}

/**
 * 内存使用监控
 */
export function getMemoryUsage(): { used: number; total: number; limit: number } | null {
  if (typeof window !== 'undefined' && (window as any).performance && (window as any).performance.memory) {
    const memory = (window as any).performance.memory;
    return {
      used: memory.usedJSHeapSize,
      total: memory.totalJSHeapSize,
      limit: memory.jsHeapSizeLimit
    };
  }
  return null;
}

/**
 * 强制浏览器重排（谨慎使用）
 */
export function forceReflow(): void {
  if (typeof document !== 'undefined') {
    void document.body.offsetHeight;
  }
}

/**
 * 使用 requestAnimationFrame 优化动画
 */
export function raf(callback: () => void): number {
  return window.requestAnimationFrame(callback);
}

/**
 * 取消 requestAnimationFrame
 */
export function cancelRaf(id: number): void {
  window.cancelAnimationFrame(id);
}

/**
 * 节流+raf 组合，用于滚动等高频事件
 */
export function rafThrottle<T extends (...args: any[]) => any>(fn: T): T {
  let rafId: number | null = null;
  let latestArgs: any[] | null = null;

  const throttledFn = ((...args: any[]) => {
    latestArgs = args;
    
    if (rafId === null) {
      rafId = raf(() => {
        fn(...latestArgs!);
        rafId = null;
        latestArgs = null;
      });
    }
  }) as T;

  return throttledFn;
}

/**
 * 缓存工具
 */
export class SimpleCache<K, V> {
  private cache: Map<K, { value: V; timestamp: number; ttl?: number }> = new Map();
  private maxSize: number;

  constructor(maxSize: number = 1000) {
    this.maxSize = maxSize;
  }

  /**
   * 获取缓存
   */
  get(key: K): V | undefined {
    const entry = this.cache.get(key);
    
    if (!entry) return undefined;
    
    if (entry.ttl && Date.now() - entry.timestamp > entry.ttl) {
      this.cache.delete(key);
      return undefined;
    }
    
    return entry.value;
  }

  /**
   * 设置缓存
   */
  set(key: K, value: V, ttl?: number): void {
    if (this.cache.size >= this.maxSize) {
      const oldestKey = this.cache.keys().next().value;
      if (oldestKey !== undefined) {
        this.cache.delete(oldestKey);
      }
    }
    
    this.cache.set(key, {
      value,
      timestamp: Date.now(),
      ttl
    });
  }

  /**
   * 检查是否存在
   */
  has(key: K): boolean {
    return this.get(key) !== undefined;
  }

  /**
   * 删除缓存
   */
  delete(key: K): boolean {
    return this.cache.delete(key);
  }

  /**
   * 清空缓存
   */
  clear(): void {
    this.cache.clear();
  }

  /**
   * 获取大小
   */
  size(): number {
    return this.cache.size;
  }
}

// 导出一个全局缓存实例
export const globalCache = new SimpleCache<string, any>(500);
