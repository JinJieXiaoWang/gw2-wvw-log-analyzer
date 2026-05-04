export interface LogFile {
  id: number
  file_name: string
  upload_time: string
  map_name: string
  server: string
  guild_tag?: string
  player_count: number
  duration: number
  status: 'pending' | 'parsing' | 'completed' | 'failed'
  status_text?: string
  file_size: number
  parsed_data?: ParsedLogData
  created_at?: string
  updated_at?: string
}

export interface ParsedLogData {
  total_damage: number
  total_healing: number
  total_kills: number
  total_deaths: number
  duration: number
  players: PlayerStats[]
  skills: SkillUsage[]
  buffs: BuffInfo[]
}

export interface PlayerStats {
  id: string
  name: string
  account_name: string
  profession: string
  elite_spec?: string
  damage: number
  healing: number
  kills: number
  deaths: number
  attendance_time: number
  score: number
  rank: number
  buffs?: BuffInfo[]
  skills?: SkillUsage[]
}

export interface SkillUsage {
  skill_id: number
  skill_name: string
  cast_count: number
  damage_contribution: number
  timing: string
}

export interface BuffInfo {
  buff_id: number
  buff_name: string
  uptime: number
  stack_count: number
}

export interface FightInfo {
  id: number
  log_id: number
  map_name: string
  server: string
  start_time: string
  end_time: string
  duration: number
  total_damage: number
  total_healing: number
  total_kills: number
  total_deaths: number
  player_count: number
}

export interface ParseProgress {
  log_id: number
  status: 'pending' | 'parsing' | 'completed' | 'failed'
  progress: number
  current_step: string
  error_message?: string
}

export interface FilterOptions {
  map_name?: string
  server?: string
  date_range?: [string, string]
  status?: string
  search_keyword?: string
  parse_status?: string
}

export interface PaginationState {
  page: number
  page_size: number
  total: number
}

export interface LogListParams {
  page?: number
  page_size?: number
  parse_status?: string | null
  server?: string | null
  map_name?: string | null
}

export interface LogUploadParams {
  server?: string | null
  map_name?: string | null
  guild_tag?: string | null
  auto_parse?: boolean
}

export interface LogUpdate {
  server?: string
  map_name?: string
  guild_tag?: string
}