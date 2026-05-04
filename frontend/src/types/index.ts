export interface User {
  id: string
  username: string
  email: string
  avatar?: string
  role: 'admin' | 'user'
}

export interface LogFile {
  id: string
  fileName: string
  uploadTime: string
  mapName: string
  serverName: string
  playerCount: number
  duration: number
  status: 'pending' | 'parsing' | 'completed' | 'failed'
  statusText?: string
  fileSize: number
  parsedData?: ParsedLogData
}

export interface ParsedLogData {
  totalDamage: number
  totalHealing: number
  totalKills: number
  totalDeaths: number
  duration: number
  players: PlayerStats[]
  skills: SkillUsage[]
  buffs: BuffInfo[]
}

export interface PlayerStats {
  id: string
  name: string
  profession: string
  damage: number
  healing: number
  kills: number
  deaths: number
  attendanceTime: number
  score: number
  rank: number
}

export interface SkillUsage {
  skillId: string
  skillName: string
  castCount: number
  damageContribution: number
  timing: string
}

export interface BuffInfo {
  buffId: string
  buffName: string
  uptime: number
  stackCount: number
}

export interface BuildCode {
  id: string
  name: string
  code: string
  profession: string
  traits: Trait[]
  equipment: Equipment[]
  skills: string[]
  createdAt: string
  updatedAt: string
}

export interface Trait {
  id: string
  name: string
  tier: number
  slot: string
}

export interface Equipment {
  id: string
  name: string
  type: 'weapon' | 'armor' | 'trinket'
  stats: EquipmentStats
}

export interface EquipmentStats {
  power: number
  precision: number
  toughness: number
  vitality: number
  critDamage: number
}

export interface DashboardStats {
  totalLogs: number
  totalPlayers: number
  totalDamage: number
  totalHealing: number
  averageDuration: number
  professionDistribution: { [key: string]: number }
  dailyTrend: { date: string; damage: number; healing: number }[]
}

export interface FilterOptions {
  mapName?: string
  serverName?: string
  dateRange?: [string, string]
  status?: string
  searchKeyword?: string
}

export interface PaginationState {
  page: number
  pageSize: number
  total: number
}

export interface AttendanceRecord {
  id: string
  playerName: string
  profession: string
  date: string
  attendanceTime: number
  damage: number
  healing: number
  kills: number
  deaths: number
  score: number
}
