export interface Skill {
  id: number
  name: string
  name_cn?: string
  profession?: string
  skill_type: string
  slot?: string
  description?: string
  icon_url?: string
}

export interface SkillEvent {
  event_id: number
  fight_id: number
  account_name: string
  skill_id: number
  skill_name: string
  timestamp: number
  damage: number
  healing: number
  target?: string
}

export interface SkillRotation {
  account_name: string
  fight_id?: number
  total_casts: number
  ideal_rotation: string[]
  actual_rotation: string[]
  errors: RotationError[]
  accuracy: number
  timing_analysis: TimingAnalysis[]
}

export interface RotationError {
  timestamp: number
  expected_skill: string
  actual_skill: string
  error_type: 'early' | 'late' | 'wrong' | 'missing'
  severity: 'low' | 'medium' | 'high'
}

export interface TimingAnalysis {
  skill_id: number
  skill_name: string
  cast_count: number
  avg_interval: number
  ideal_interval: number
  deviation: number
}

export interface SkillsListParams {
  page?: number
  page_size?: number
  profession?: string | null
}