/**
 * ECharts 主题配置 Composable
 * 提供统一的基础样式配置，减少各组件中的重复定义
 */

/** 统一 tooltip 样式 */
export const tooltipTheme = {
  backgroundColor: 'rgba(15, 23, 42, 0.9)',
  borderColor: 'rgba(148, 163, 184, 0.2)',
  textStyle: { color: '#e2e8f0' },
}

/** 统一 grid 配置 */
export const gridTheme = {
  left: 60,
  right: 20,
  top: 20,
  bottom: 40,
}

/** 统一轴线样式 */
export const axisLineTheme = {
  lineStyle: { color: 'rgba(148, 163, 184, 0.2)' },
}

/** 统一轴文字样式 */
export const axisLabelTheme = {
  color: '#94a3b8',
  fontSize: 11,
}

/** 统一分割线样式 */
export const splitLineTheme = {
  lineStyle: { color: 'rgba(148, 163, 184, 0.1)' },
}

/** 统一 legend 样式 */
export const legendTheme = {
  textStyle: { color: '#94a3b8' },
  pageTextStyle: { color: '#94a3b8' },
}

/** 统一颜色调色板 */
export const chartColors = [
  '#3b82f6',
  '#ef4444',
  '#22c55e',
  '#f59e0b',
  '#a855f7',
  '#06b6d4',
  '#ec4899',
  '#84cc16',
  '#f97316',
  '#6366f1',
  '#14b8a6',
  '#e11d48',
  '#8b5cf6',
  '#10b981',
  '#f43f5e',
]

export function useEChartsTheme() {
  return {
    tooltip: tooltipTheme,
    grid: gridTheme,
    axisLine: axisLineTheme,
    axisLabel: axisLabelTheme,
    splitLine: splitLineTheme,
    legend: legendTheme,
    colors: chartColors,
  }
}
