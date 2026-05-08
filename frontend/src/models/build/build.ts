export interface BuildCode {
  id: number
  name: string
  build_code: string
  profession: string
  elite_spec?: string
  traits: Trait[]
  equipment: Equipment[]
  skills: string[]
  description?: string
  member_id?: number
  created_at: string
  updated_at: string
}

export interface Trait {
  id: number
  name: string
  tier: number
  slot: string
  description?: string
}

export interface Equipment {
  id: number
  name: string
  type: 'weapon' | 'armor' | 'trinket'
  stats: EquipmentStats
  slot?: string
}

export interface EquipmentStats {
  power: number
  precision: number
  toughness: number
  vitality: number
  crit_damage: number
  healing_power?: number
  condition_damage?: number
  expertise?: number
  concentration?: number
}

export interface BuildComparison {
  build1: BuildCode
  build2: BuildCode
  differences: BuildDifference[]
  similarity_score: number
}

export interface BuildDifference {
  category: 'traits' | 'equipment' | 'skills'
  item_name: string
  value1: any
  value2: any
  impact: 'major' | 'minor' | 'neutral'
}

export interface BuildsListParams {
  page?: number
  page_size?: number
  profession?: string | null
  member_id?: number | null
}

export interface BuildCreate {
  name: string
  profession: string
  build_code: string
  description?: string
}

export interface BuildUpdate {
  name?: string
  build_code?: string
  description?: string
}