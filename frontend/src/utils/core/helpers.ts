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
