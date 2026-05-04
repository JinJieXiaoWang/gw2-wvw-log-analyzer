export interface Member {
  id: number
  account_name: string
  character_name: string
  profession: string
  elite_spec?: string
  guild_tag?: string
  role?: string
  total_fights: number
  total_damage: number
  total_healing: number
  total_kills: number
  total_deaths: number
  avg_score: number
  created_at?: string
  updated_at?: string
}

export interface MemberStats {
  member_id: number
  account_name: string
  character_name: string
  profession: string
  elite_spec?: string
  total_fights: number
  total_damage: number
  total_healing: number
  total_kills: number
  total_deaths: number
  avg_damage: number
  avg_healing: number
  avg_kills: number
  avg_deaths: number
  avg_score: number
  recent_fights: FightSummary[]
}

export interface FightSummary {
  fight_id: number
  log_id: number
  map_name: string
  server: string
  date: string
  damage: number
  healing: number
  kills: number
  deaths: number
  score: number
}

export interface ProfessionDistribution {
  profession: string
  profession_name_cn: string
  count: number
  percentage: number
  avg_score: number
}

export interface MembersListParams {
  page?: number
  page_size?: number
  profession?: string | null
  guild_tag?: string | null
}

export interface MemberRankingParams {
  page?: number
  page_size?: number
  sort_by?: string
}