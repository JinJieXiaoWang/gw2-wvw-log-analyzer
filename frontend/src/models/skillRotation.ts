// 模块功能: 技能循环分析相关数据模型定义
// 作者: 帅姐姐
// 创建日期: 2026-05-14

/**
 * 技能事件状态类型
 */
export type SkillState = 'full' | 'interrupted' | 'instant' | 'swap' | 'trait'

/**
 * 影响程度类型
 */
export type ImpactLevel = 'low' | 'medium' | 'high'

/**
 * 优化建议优先级
 */
export type SuggestionPriority = 'high' | 'medium' | 'low'

/**
 * 视图模式
 */
export type ViewMode = 'cycle' | 'timeline' | 'heatmap'

/**
 * 对比模式
 */
export type CompareMode = 'time' | 'damage' | 'efficiency'

/**
 * 时间范围
 */
export type TimeRange = 'full' | 'first5' | 'last5'

/**
 * 技能事件接口
 */
export interface RotationEvent {
  id: number
  cast_time: number // 相对时间（毫秒）
  duration: number
  skill_id: number
  skill_name: string
  skill_icon: string
  state: SkillState
  time_gained: number
  quickness: number
  auto_attack: boolean
  damage: number
  targets: number
}

/**
 * 技能循环接口
 */
export interface SkillCycle {
  id: number
  events: RotationEvent[]
  duration: number
  start: number
  end: number
  interrupted_count: number
  total_damage: number
}

/**
 * 技能统计信息
 */
export interface SkillStat {
  skill_id: number
  skill_name: string
  skill_icon: string
  count: number
  damage: number
  percent: number
  avg_cast_time: number
}

/**
 * 错误/失误信息
 */
export interface Mistake {
  type: 'interrupt' | 'cancel' | 'early' | 'late'
  event?: RotationEvent
  description: string
  impact: ImpactLevel
}

/**
 * 优化建议
 */
export interface OptimizationSuggestion {
  priority: SuggestionPriority
  title: string
  description: string
  expected_impact: string
  related_skill?: number
}

/**
 * 完整的技能循环分析结果
 */
export interface RotationAnalysis {
  log_id: number
  member_id: number
  account: string
  character_name: string
  profession: string
  fight_duration: number // 毫秒
  events: RotationEvent[]
  cycles: SkillCycle[]
  stats: RotationStats
  mistakes: Mistake[]
  optimizations: OptimizationSuggestion[]
}

/**
 * 技能循环统计信息
 */
export interface RotationStats {
  total_casts: number
  total_damage: number
  avg_dps: number
  skill_cast_uptime: number // %
  interrupted_rate: number // %
  auto_attack_rate: number // %
  top_skills: SkillStat[]
  buff_coverage: Record<string, number>
}

/**
 * 过滤器选项
 */
export interface FilterOptions {
  show_auto: boolean
  show_instant: boolean
  show_swap: boolean
  show_trait: boolean
}

/**
 * 创建空的技能循环分析对象
 */
export function createEmptyRotationAnalysis(): RotationAnalysis {
  return {
    log_id: 0,
    member_id: 0,
    account: '',
    character_name: '',
    profession: '',
    fight_duration: 0,
    events: [],
    cycles: [],
    stats: {
      total_casts: 0,
      total_damage: 0,
      avg_dps: 0,
      skill_cast_uptime: 0,
      interrupted_rate: 0,
      auto_attack_rate: 0,
      top_skills: [],
      buff_coverage: {}
    },
    mistakes: [],
    optimizations: []
  }
}

/**
 * 创建默认的过滤器选项
 */
export function createDefaultFilters(): FilterOptions {
  return {
    show_auto: false,
    show_instant: true,
    show_swap: true,
    show_trait: false
  }
}

/**
 * 根据过滤器过滤技能事件
 */
export function computeFilteredEvents(
  events: RotationEvent[] | undefined | null,
  filters: FilterOptions
): RotationEvent[] {
  if (!Array.isArray(events)) return []
  return events.filter((event) => {
    if (!event) return false
    if (event.auto_attack && !filters.show_auto) return false
    if (event.state === 'instant' && !filters.show_instant) return false
    if (event.state === 'swap' && !filters.show_swap) return false
    if (event.state === 'trait' && !filters.show_trait) return false
    return true
  })
}

/**
 * 根据时间范围裁剪技能事件
 */
export function cropEventsByTimeRange(
  events: RotationEvent[] | undefined | null,
  timeRange: TimeRange,
  totalDuration: number
): RotationEvent[] {
  if (!Array.isArray(events)) return []
  if (timeRange === 'full') return events

  const cutoff = 5 * 60 * 1000 // 5分钟（毫秒）

  if (timeRange === 'first5') {
    return events.filter((e) => e && e.cast_time !== undefined && e.cast_time <= cutoff)
  }

  if (timeRange === 'last5') {
    const start = Math.max(0, (totalDuration || 0) - cutoff)
    return events.filter((e) => e && e.cast_time !== undefined && e.cast_time >= start)
  }

  return events
}
