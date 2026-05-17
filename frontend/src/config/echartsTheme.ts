/**
 * ECharts 统一主题配置
 * 功能：集中管理所有图表的配色、字体、尺寸等视觉参数
 * 消除组件中散布的硬编码魔法数字
 */

/** 技能状态颜色映射 */
export const SKILL_STATE_COLORS = {
  full: 'rgba(34, 211, 238, 0.8)',      // cyan
  interrupted: 'rgba(239, 68, 68, 0.8)', // red
  instant: 'rgba(59, 130, 246, 0.8)',    // blue
  swap: 'rgba(168, 85, 247, 0.8)',       // purple
  trait: 'rgba(245, 158, 11, 0.8)',      // amber
} as const

/** 图表通用配置 */
export const CHART_COMMON_CONFIG = {
  /** 字体颜色 */
  textColor: '#e5e7eb',
  /** 次级文字颜色 */
  secondaryTextColor: '#9ca3af',
  /** 坐标轴线颜色 */
  axisLineColor: 'rgba(255,255,255,0.1)',
  /** 分隔线颜色 */
  splitLineColor: 'rgba(255,255,255,0.05)',
  /** 提示框背景 */
  tooltipBg: 'rgba(17, 17, 20, 0.95)',
  /** 提示框边框 */
  tooltipBorder: 'rgba(255,255,255,0.1)',
} as const

/** 时间轴视图配置 */
export const TIMELINE_CONFIG = {
  /** 时间刻度最多显示数量 */
  maxTimelineMarks: 20,
  /** 图表grid边距 */
  grid: { left: 140, right: 30, top: 20, bottom: 50 },
  /** 技能条最小宽度(px) */
  minBarWidth: 6,
  /** 技能条高度 */
  barHeight: 24,
  /** 显示图标的最小宽度 */
  minIconWidth: 28,
} as const

/** 热力图配置 */
export const HEATMAP_CONFIG = {
  /** 分桶大小(秒) */
  bucketSize: 5,
  /** 最多保留技能数 */
  maxSkills: 15,
} as const

/** 循环视图配置 */
export const CYCLE_CONFIG = {
  /** 初始可见循环数量 */
  initialVisibleCount: 20,
  /** 每次加载更多循环数量 */
  loadMoreCount: 20,
  /** 单个循环最大显示技能数 */
  maxSkillsPerCycle: 40,
} as const

/** 柱状图配置 */
export const BAR_CHART_CONFIG = {
  /** Top N 显示数量 */
  topN: 10,
  /** 柱条宽度 */
  barWidth: 12,
  /** 默认柱状图渐变色 */
  gradient: ['#3b82f6', '#1d4ed8'],
} as const
