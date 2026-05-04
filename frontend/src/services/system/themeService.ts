/**
 * 主题服务管理器（增强版）
 * 功能：管理主题切换逻辑、状态同步和CSS变量更新，支持PrimeUIX多主题生态系统
 * 作者：System
 * 创建日期：2026-04-28
 * 更新：2026-04-30 - 添加性能优化、防抖机制和性能监控
 */

import type { ThemeConfig } from '@/constants/themes';
import { GameThemes, getThemeById, getDefaultTheme, DEFAULT_THEME_ID } from '@/constants/themes';

const STORAGE_KEY = 'gw2_wvw_theme_id';

// 性能监控配置
const PERFORMANCE_LOGGING = process.env.NODE_ENV === 'development';

// 预览防抖配置
const PREVIEW_DEBOUNCE_MS = 50;
let previewTimeout: ReturnType<typeof setTimeout> | null = null;

export class ThemeService {
  private static currentTheme: ThemeConfig = getDefaultTheme();
  private static savedTheme: ThemeConfig = getDefaultTheme();
  private static listeners: Set<(theme: ThemeConfig) => void> = new Set();
  private static isTransitioning = false;
  private static isPreviewMode = false;
  // 性能统计
  private static switchCount = 0;
  private static totalSwitchTime = 0;
  private static minSwitchTime = Infinity;
  private static maxSwitchTime = 0;

  /**
   * 获取所有可用主题列表
   */
  static getAllThemes(): ThemeConfig[] {
    return [...GameThemes];
  }

  /**
   * 获取当前主题
   */
  static getCurrentTheme(): ThemeConfig {
    return this.currentTheme;
  }

  /**
   * 获取当前保存的主题（真实选择，非预览）
   */
  static getSavedTheme(): ThemeConfig {
    return this.savedTheme;
  }

  /**
   * 获取当前主题ID
   */
  static getCurrentThemeId(): string {
    return this.currentTheme.id;
  }

  /**
   * 检查是否处于预览模式
   */
  static getIsPreviewMode(): boolean {
    return this.isPreviewMode;
  }

  /**
   * 应用主题（带性能优化的版本）
   * @param themeId 主题ID
   * @param isPreview 是否为预览模式
   */
  static async applyTheme(themeId: string, isPreview: boolean = false): Promise<void> {
    // 性能监控：记录开始时间
    const startTime = performance.now();
    
    const theme = getThemeById(themeId) || getDefaultTheme();
    
    // 检查是否需要切换主题（跳过相同主题，但预览模式下允许强制刷新）
    const shouldSkip = theme.id === this.currentTheme.id && !isPreview;
    
    if (shouldSkip) {
      // 如果是取消预览回到保存主题，仍需通知监听器更新状态
      if (this.isPreviewMode) {
        this.isPreviewMode = false;
        this.notifyListeners(theme);
      }
      return;
    }

    // 如果正在切换，先设置标志再开始新切换（允许打断当前切换）
    this.isTransitioning = true;
    this.isPreviewMode = isPreview;

    try {
      // 添加过渡动画类
      document.documentElement.classList.add('theme-transition');

      // 更新当前主题
      this.currentTheme = theme;

      // 保存主题ID到localStorage（仅非预览模式）
      if (!isPreview) {
        this.savedTheme = theme;
        this.saveThemeId(themeId);
      }

      // 使用 requestAnimationFrame 优化CSS变量注入，避免强制同步布局
      await new Promise(resolve => requestAnimationFrame(resolve));
      
      // 注入游戏风格CSS变量
      this.injectGameVariables(theme.colors);

      // 通知所有监听器
      this.notifyListeners(theme);

    } finally {
      // 立即释放转换状态，允许下一次切换（不等动画完成）
      this.isTransitioning = false;
      document.documentElement.classList.remove('theme-transition');
      
      // 性能监控：记录结束时间并统计
      const endTime = performance.now();
      const switchTime = endTime - startTime;
      
      this.switchCount++;
      this.totalSwitchTime += switchTime;
      this.minSwitchTime = Math.min(this.minSwitchTime, switchTime);
      this.maxSwitchTime = Math.max(this.maxSwitchTime, switchTime);
      
      if (PERFORMANCE_LOGGING) {
        console.info(`[ThemeService] Theme switch completed in ${switchTime.toFixed(2)}ms`);
        console.info(`[ThemeService] Performance stats:`, this.getPerformanceStats());
      }
    }
  }

  /**
   * 预览主题（悬停效果，不保存）
   * 使用防抖机制防止快速悬停时频繁切换
   */
  static async previewTheme(themeId: string): Promise<void> {
    // 清除之前的预览定时器
    if (previewTimeout) {
      clearTimeout(previewTimeout);
    }
    
    // 使用防抖，只有悬停超过一定时间才应用预览
    return new Promise((resolve) => {
      previewTimeout = setTimeout(async () => {
        try {
          await this.applyTheme(themeId, true);
        } finally {
          previewTimeout = null;
          resolve();
        }
      }, PREVIEW_DEBOUNCE_MS);
    });
  }

  /**
   * 取消预览，恢复保存的主题
   */
  static async cancelPreview(): Promise<void> {
    // 清除预览定时器，防止延迟的预览操作继续执行
    if (previewTimeout) {
      clearTimeout(previewTimeout);
      previewTimeout = null;
    }
    
    if (this.isPreviewMode) {
      await this.applyTheme(this.savedTheme.id, false);
    }
  }

  /**
   * 确认并保存预览的主题
   */
  static async confirmPreview(): Promise<void> {
    if (this.isPreviewMode) {
      this.savedTheme = this.currentTheme;
      this.saveThemeId(this.currentTheme.id);
      this.isPreviewMode = false;
      this.notifyListeners(this.currentTheme);
    }
  }

  /**
   * 注入游戏风格CSS变量
   * @param colors 主题颜色配置
   */
  private static injectGameVariables(colors: ThemeConfig['colors']): void {
    const root = document.documentElement;
    
    const colorMap: Record<string, string> = {
      // 主色调
      '--color-primary': colors.primary,
      '--color-primary-light': colors.primaryLight,
      '--color-primary-dark': colors.primaryDark,
      
      // 辅助色
      '--color-secondary': colors.secondary,
      '--color-secondary-light': colors.secondaryLight,
      '--color-secondary-dark': colors.secondaryDark,
      
      // 中性色
      '--color-bg': colors.bg,
      '--color-bg-secondary': colors.bgSecondary,
      '--color-card': colors.card,
      '--color-card-hover': colors.cardHover,
      '--color-card-active': colors.cardActive,
      '--color-border': colors.border,
      '--color-border-light': colors.borderLight,
      
      // 文本色
      '--color-text': colors.text,
      '--color-text-secondary': colors.textSecondary,
      '--color-text-disabled': colors.textDisabled,
      '--color-text-inverse': colors.textInverse,
      
      // 状态色
      '--color-success': colors.success,
      '--color-warning': colors.warning,
      '--color-error': colors.error,
      '--color-info': colors.info,
      
      // AI色
      '--color-ai': colors.ai,
      
      // 新增：强调色、高亮色、发光色、阴影色
      '--color-accent': colors.accent,
      '--color-highlight': colors.highlight,
      '--color-glow': colors.glow,
      '--color-shadow': colors.shadow,
      
      // Alpha 透明度变体
      '--color-primary-alpha-10': `${colors.primary}1A`,
      '--color-primary-alpha-20': `${colors.primary}33`,
      '--color-primary-alpha-30': `${colors.primary}4D`,
      '--color-primary-alpha-40': `${colors.primary}66`,
      '--color-primary-alpha-50': `${colors.primary}80`,
      
      '--color-secondary-alpha-10': `${colors.secondary}1A`,
      '--color-secondary-alpha-20': `${colors.secondary}33`,
      '--color-secondary-alpha-30': `${colors.secondary}4D`,
      
      '--color-success-alpha-10': `${colors.success}1A`,
      '--color-warning-alpha-10': `${colors.warning}1A`,
      '--color-error-alpha-10': `${colors.error}1A`,
      '--color-info-alpha-10': `${colors.info}1A`,
      
      '--color-ai-alpha-10': `${colors.ai}1A`,
      '--color-ai-alpha-20': `${colors.ai}33`,
      '--color-ai-alpha-30': `${colors.ai}4D`,
      
      '--color-accent-alpha-10': `${colors.accent}1A`,
      '--color-accent-alpha-20': `${colors.accent}33`,
      '--color-accent-alpha-30': `${colors.accent}4D`,
      
      // PrimeVue/Aura 变量桥接
      '--p-primary-500': colors.primary,
      '--p-primary-600': colors.primaryLight,
      '--p-primary-400': colors.primaryDark,
      
      '--p-surface-0': colors.bg,
      '--p-surface-50': colors.bgSecondary,
      '--p-surface-100': colors.card,
      '--p-surface-200': colors.cardHover,
      '--p-surface-300': colors.border,
      '--p-surface-400': colors.borderLight,
      '--p-surface-500': colors.textSecondary,
      '--p-surface-600': colors.textSecondary,
      '--p-surface-700': colors.text,
      '--p-surface-800': colors.text,
      '--p-surface-900': colors.text,
      
      '--p-text-color': colors.text,
      '--p-text-color-secondary': colors.textSecondary,
      '--p-text-color-tertiary': colors.textDisabled,
      
      // 阴影色（使用主色调）
      '--p-shadow-color': `${colors.primary}1A`,
      
      // PrimeVue 背景色变量
      '--p-background': colors.bg,
      '--p-overlay-bg': `${colors.bg}CC`,
      
      // 旧版兼容变量
      '--neutral-bg': colors.bg,
      '--neutral-bg-secondary': colors.bgSecondary,
      '--neutral-card': colors.card,
      '--neutral-card-hover': colors.cardHover,
      '--neutral-border': colors.border,
      '--neutral-text': colors.text,
      '--neutral-text-secondary': colors.textSecondary,
      '--neutral-text-disabled': colors.textDisabled,
      
      // 新增兼容变量
      '--neutral-accent': colors.accent,
      '--neutral-highlight': colors.highlight
    };

    // 批量更新CSS变量以提高性能
    Object.entries(colorMap).forEach(([key, value]) => {
      root.style.setProperty(key, value);
    });
  }

  /**
   * 保存主题ID到localStorage
   */
  private static saveThemeId(themeId: string): void {
    try {
      localStorage.setItem(STORAGE_KEY, themeId);
      if (PERFORMANCE_LOGGING) {
        console.info(`[ThemeService] Saved theme ID to localStorage: ${themeId}`);
      }
    } catch (error) {
      console.error('Failed to save theme ID:', error);
    }
  }

  /**
   * 加载保存的主题ID
   * 优先从 settings store 的存储位置读取，确保一致性
   */
  static loadSavedThemeId(): string {
    try {
      // 首先尝试从 settings store 的存储位置读取
      const settingsStoreKey = 'gw2_wvw_settings';
      const savedSettings = localStorage.getItem(settingsStoreKey);
      
      if (savedSettings) {
        try {
          const parsed = JSON.parse(savedSettings);
          if (parsed.gameThemeId) {
            if (PERFORMANCE_LOGGING) {
              console.info(`[ThemeService] Loaded theme ID from settings store: ${parsed.gameThemeId}`);
            }
            return parsed.gameThemeId;
          }
        } catch (e) {
          console.warn('[ThemeService] Failed to parse settings JSON, falling back to theme storage');
        }
      }
      
      // 回退到旧的主题存储位置
      const savedId = localStorage.getItem(STORAGE_KEY);
      const result = savedId || DEFAULT_THEME_ID;
      
      if (PERFORMANCE_LOGGING) {
        console.info(`[ThemeService] Loaded theme ID from theme storage: ${savedId || 'NOT FOUND, using default'}`);
        console.info(`[ThemeService] Final theme ID: ${result}`);
      }
      
      return result;
    } catch (error) {
      console.error('Failed to load theme ID:', error);
      return DEFAULT_THEME_ID;
    }
  }

  /**
   * 初始化主题（从localStorage加载或使用默认）
   */
  static initialize(): void {
    const savedThemeId = this.loadSavedThemeId();
    const theme = getThemeById(savedThemeId) || getDefaultTheme();
    
    // 立即应用主题，不等待动画
    this.currentTheme = theme;
    this.savedTheme = theme;
    this.injectGameVariables(theme.colors);
    
    // 通知所有订阅者当前主题，确保UI同步
    // 使用 setTimeout 确保在 Vue 应用挂载后执行
    setTimeout(() => {
      this.notifyListeners(theme);
    }, 0);
  }

  /**
   * 订阅主题变化
   */
  static subscribe(listener: (theme: ThemeConfig) => void): () => void {
    this.listeners.add(listener);
    
    // 立即通知当前状态
    listener(this.currentTheme);
    
    return () => {
      this.listeners.delete(listener);
    };
  }

  /**
   * 通知所有订阅者主题变化
   */
  private static notifyListeners(theme: ThemeConfig): void {
    this.listeners.forEach(listener => {
      try {
        listener(theme);
      } catch (error) {
        console.error('Error notifying theme listener:', error);
      }
    });
  }

  /**
   * 重置为默认主题
   */
  static async resetToDefault(): Promise<void> {
    await this.applyTheme(DEFAULT_THEME_ID, false);
  }

  /**
   * 检查主题是否存在
   */
  static themeExists(themeId: string): boolean {
    return GameThemes.some(t => t.id === themeId);
  }

  /**
   * 获取当前主题是否在切换中
   */
  static getIsTransitioning(): boolean {
    return this.isTransitioning;
  }

  /**
   * 获取性能统计信息
   */
  static getPerformanceStats(): {
    switchCount: number;
    avgSwitchTime: number;
    minSwitchTime: number;
    maxSwitchTime: number;
  } {
    return {
      switchCount: this.switchCount,
      avgSwitchTime: this.switchCount > 0 ? Math.round(this.totalSwitchTime / this.switchCount * 100) / 100 : 0,
      minSwitchTime: this.minSwitchTime === Infinity ? 0 : this.minSwitchTime,
      maxSwitchTime: this.maxSwitchTime
    };
  }

  /**
   * 重置性能统计
   */
  static resetPerformanceStats(): void {
    this.switchCount = 0;
    this.totalSwitchTime = 0;
    this.minSwitchTime = Infinity;
    this.maxSwitchTime = 0;
  }
}
