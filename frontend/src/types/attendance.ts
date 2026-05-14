/**
 * 出勤模块共享类型定义
 */

export interface AttendanceSummary {
  attendance_count?: number
  total_duration_sec?: number
  total_damage?: number
  kd_ratio?: number
  avg_score?: number
  server?: string
  [key: string]: unknown
}

export interface AttendanceCharacter {
  character_name: string
  profession: string
  attendance_count: number
  avg_dps: number
  total_damage: number
  avg_score: number
  kd_ratio: number
}

export interface AttendanceFight {
  fight_date: string
  profession: string
  character_name: string
  map_name: string
  damage: number
  dps: number
  downed: number
  killed: number
  dead_count: number
  ai_score: number
}

export interface AttendanceDetailData {
  account?: string
  server?: string
  rank?: string
  join_date?: string
  summary?: AttendanceSummary
  characters?: AttendanceCharacter[]
  recent_fights?: AttendanceFight[]
  attendance_trend?: number[]
  comprehensive_abilities?: Record<string, number>
  [key: string]: unknown
}

export interface CardStyle {
  gradient: string
  border: string
  iconBg: string
  textColor: string
}
