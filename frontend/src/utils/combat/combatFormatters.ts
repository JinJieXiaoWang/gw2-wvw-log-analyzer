/**
 * 战斗相关格式化工具函数
 * 功能：提供战斗日志分析页面专用的格式化函数
 * 规范：纯函数、无副作用、可复用
 */

/** 格式化战斗时长 */
export function fmtDuration(seconds: number): string {
  const m = Math.floor(seconds / 60)
  const s = seconds % 60
  return m > 0 ? `${m}分${s}秒` : `${s}秒`
}

/** 格式化日期（MM-DD HH:mm） */
export function fmtDate(dateStr: string): string {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  return d.toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

/** 排名徽章样式 */
export function rankClass(idx: number): string {
  if (idx === 0) return 'bg-yellow-500/20 text-yellow-600'
  if (idx === 1) return 'bg-gray-400/20 text-gray-500'
  if (idx === 2) return 'bg-orange-400/20 text-orange-500'
  return 'bg-neutral-bg text-neutral-text-secondary'
}

/** 小队颜色映射 */
const GROUP_COLORS: Record<string, string> = {
  '0': '#6b7280', '1': '#ef4444', '2': '#f97316', '3': '#eab308', '4': '#84cc16',
  '5': '#22c55e', '6': '#06b6d4', '7': '#3b82f6', '8': '#8b5cf6', '9': '#d946ef', '10': '#f43f5e'
}

export function groupColor(id: number): string {
  return GROUP_COLORS[String(id)] || '#6b7280'
}

/** 评分等级对应 PrimeVue Tag severity */
export function scoreSeverity(score?: string): string {
  if (!score) return 'secondary'
  const s = score.toLowerCase()
  if (s.startsWith('s')) return 'success'
  if (s.startsWith('a')) return 'info'
  if (s.startsWith('b')) return 'warn'
  return 'danger'
}

/** 评分数值颜色 */
export function scoreValueColor(score?: number | null): string {
  if (score == null) return 'text-neutral-text-secondary'
  if (score >= 90) return 'text-success'
  if (score >= 80) return 'text-info'
  if (score >= 70) return 'text-warning'
  if (score >= 60) return 'text-orange-400'
  return 'text-error'
}
