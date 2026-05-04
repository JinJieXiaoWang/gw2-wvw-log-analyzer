/**
 * 通用工具函数
 * 功能：提供项目中常用的工具函数
 * 作者：System
 * 创建日期：2026-04-29
 */

/**
 * 防抖函数
 * @param fn 要执行的函数
 * @param delay 延迟时间（毫秒）
 */
export function debounce<T extends (...args: any[]) => any>(
  fn: T,
  delay: number = 300
): (...args: Parameters<T>) => void {
  let timer: ReturnType<typeof setTimeout> | null = null;
  
  return function(...args: Parameters<T>) {
    if (timer) {
      clearTimeout(timer);
    }
    
    timer = setTimeout(() => {
      fn(...args);
      timer = null;
    }, delay);
  };
}

/**
 * 节流函数
 * @param fn 要执行的函数
 * @param delay 延迟时间（毫秒）
 */
export function throttle<T extends (...args: any[]) => any>(
  fn: T,
  delay: number = 300
): (...args: Parameters<T>) => void {
  let lastTime = 0;
  
  return function(...args: Parameters<T>) {
    const now = Date.now();
    
    if (now - lastTime >= delay) {
      fn(...args);
      lastTime = now;
    }
  };
}

/**
 * 安全访问深层对象属性
 * @param obj 对象
 * @param path 属性路径
 * @param defaultValue 默认值
 */
export function safeGet<T = any>(
  obj: any,
  path: string,
  defaultValue?: T
): T {
  const keys = path.split('.');
  let result: any = obj;
  
  for (const key of keys) {
    if (result === null || result === undefined) {
      return defaultValue as T;
    }
    result = result[key];
  }
  
  return (result === undefined || result === null) ? defaultValue as T : result;
}

/**
 * 格式化时间
 * @param date Date对象或时间戳
 * @param format 格式化字符串，默认为 'YYYY-MM-DD HH:mm:ss'
 */
export function formatDate(
  date: Date | number | string,
  format: string = 'YYYY-MM-DD HH:mm:ss'
): string {
  let d: Date;
  
  if (date instanceof Date) {
    d = date;
  } else if (typeof date === 'number') {
    d = new Date(date);
  } else {
    d = new Date(date);
  }
  
  if (isNaN(d.getTime())) {
    return '';
  }
  
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  const hours = String(d.getHours()).padStart(2, '0');
  const minutes = String(d.getMinutes()).padStart(2, '0');
  const seconds = String(d.getSeconds()).padStart(2, '0');
  
  return format
    .replace('YYYY', String(year))
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hours)
    .replace('mm', minutes)
    .replace('ss', seconds);
}

/**
 * 获取相对时间描述
 * @param date Date对象或时间戳
 */
export function getRelativeTime(date: Date | number | string): string {
  let d: Date;
  
  if (date instanceof Date) {
    d = date;
  } else if (typeof date === 'number') {
    d = new Date(date);
  } else {
    d = new Date(date);
  }
  
  if (isNaN(d.getTime())) {
    return '';
  }
  
  const now = new Date();
  const diff = now.getTime() - d.getTime();
  
  const seconds = Math.floor(diff / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);
  const months = Math.floor(days / 30);
  const years = Math.floor(days / 365);
  
  if (years > 0) return `${years}年前`;
  if (months > 0) return `${months}个月前`;
  if (days > 0) return `${days}天前`;
  if (hours > 0) return `${hours}小时前`;
  if (minutes > 0) return `${minutes}分钟前`;
  if (seconds > 10) return `${seconds}秒前`;
  
  return '刚刚';
}

/**
 * 生成唯一ID
 */
export function generateId(): string {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * 深拷贝
 * @param obj 要拷贝的对象
 */
export function deepClone<T>(obj: T): T {
  if (obj === null || typeof obj !== 'object') {
    return obj;
  }
  
  if (obj instanceof Date) {
    return new Date(obj.getTime()) as T;
  }
  
  if (obj instanceof Array) {
    return obj.map(item => deepClone(item)) as T;
  }
  
  if (obj instanceof Object) {
    const clonedObj: any = {};
    for (const key in obj) {
      if (obj.hasOwnProperty(key)) {
        clonedObj[key] = deepClone(obj[key]);
      }
    }
    return clonedObj as T;
  }
  
  return obj;
}

/**
 * 数组去重
 * @param arr 要去重的数组
 * @param key 用于去重的键名（可选，用于对象数组）
 */
export function unique<T>(arr: T[], key?: keyof T): T[] {
  if (!key) {
    return [...new Set(arr)];
  }
  
  const seen = new Map();
  return arr.filter(item => {
    const k = item[key];
    if (seen.has(k)) {
      return false;
    }
    seen.set(k, true);
    return true;
  });
}

/**
 * 安全的JSON解析
 * @param str JSON字符串
 * @param defaultValue 默认值
 */
export function safeJsonParse<T = any>(str: string, defaultValue?: T): T {
  try {
    return JSON.parse(str) as T;
  } catch {
    return defaultValue as T;
  }
}

/**
 * 字节大小格式化
 * @param bytes 字节数
 */
export function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 B';
  
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
}

/**
 * 数字格式化（千分位）
 * @param num 数字
 */
export function formatNumber(num: number): string {
  return num.toLocaleString();
}

/**
 * 睡眠函数
 * @param ms 毫秒数
 */
export function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * 检查是否是有效的URL
 * @param url URL字符串
 */
export function isValidUrl(url: string): boolean {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
}

/**
 * 检查是否是有效的邮箱
 * @param email 邮箱地址
 */
export function isValidEmail(email: string): boolean {
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return regex.test(email);
}

/**
 * 格式化紧凑数字
 * @param num 数字
 * @returns 紧凑格式字符串（如 1.2K, 3.4M）
 */
export function formatCompactNumber(num: number): string {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M'
  } else if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K'
  }
  return num.toString()
}
