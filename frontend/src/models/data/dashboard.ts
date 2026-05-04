export interface DashboardOverview {
  total_logs: number
  total_fights: number
  total_members: number
  total_builds: number
  recent_logs: RecentLog[]
  top_players: TopPlayer[]
  activity_summary: ActivitySummary
}

export interface RecentLog {
  id: number
  file_name: string
  upload_time: string
  map_name: string
  server: string
  status: string
}

export interface TopPlayer {
  account_name: string
  character_name: string
  profession: string
  total_score: number
  fight_count: number
}

export interface ActivitySummary {
  today: ActivityData
  week: ActivityData
  month: ActivityData
}

export interface ActivityData {
  logs_uploaded: number
  fights_parsed: number
  members_active: number
}

export interface RecentData {
  logs: RecentLog[]
  fights: RecentFight[]
  members: RecentMember[]
}

export interface RecentFight {
  id: number
  map_name: string
  server: string
  date: string
  player_count: number
}

export interface RecentMember {
  id: number
  account_name: string
  character_name: string
  profession: string
  last_active: string
}

export interface TrendData {
  logs: TrendPoint[]
  fights: TrendPoint[]
  members: TrendPoint[]
}

export interface TrendPoint {
  date: string
  value: number
}

export interface DashboardStats {
  total_logs: number
  total_fights: number
  total_members: number
  total_builds: number
  avg_damage_per_fight: number
  avg_healing_per_fight: number
  avg_duration: number
  most_active_members: TopPlayer[]
  most_played_maps: MapStats[]
}

export interface MapStats {
  map_name: string
  fight_count: number
  player_count: number
  avg_score: number
}

export interface ProfessionDistribution {
  profession: string
  profession_name_cn: string
  count: number
  percentage: number
  avg_score: number
}