export interface AttendanceRecord {
  id: number
  member_id: number
  account_name: string
  character_name: string
  profession: string
  elite_spec?: string
  date: string
  attendance_time: number
  damage: number
  healing: number
  kills: number
  deaths: number
  score: number
  rank: number
  server?: string
  map_name?: string
  guild_tag?: string
}

export interface AttendanceStats {
  total_members: number
  total_attendance_time: number
  avg_damage: number
  avg_healing: number
  avg_kills: number
  avg_deaths: number
  total_fights: number
  date_range: [string, string]
  top_players: AttendancePlayerStats[]
}

export interface AttendancePlayerStats {
  id: number
  member_id: number
  account_name: string
  character_name: string
  profession: string
  elite_spec?: string
  damage: number
  healing: number
  kills: number
  deaths: number
  attendance_time: number
  score: number
  rank: number
  fight_count: number
}

export interface AttendanceListParams {
  page?: number
  page_size?: number
  start_date?: string | null
  end_date?: string | null
  server?: string | null
  map_name?: string | null
  profession?: string | null
}

export interface AttendanceStatsParams {
  start_date?: string | null
  end_date?: string | null
}

export interface AttendanceExportParams {
  start_date?: string | null
  end_date?: string | null
  format?: 'csv' | 'json'
}