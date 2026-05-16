/**
 * Mock数据服务
 * 功能：提供开发/测试用的模拟数据
 * 作者：帅姐姐
 * 创建日期：2024-01-15
 */

import type { LogFile, PlayerStats, BuildCode, DashboardStats, AttendanceRecord } from '@/types'
import { ParseStatus } from '@/constants/dictValues'

export const mockLogs: LogFile[] = [
  {
    id: '1',
    fileName: 'BL_GuildBattle_20240115_143022.zevtc',
    uploadTime: '2024-01-15 14:30:22',
    mapName: '蓝色边境',
    serverName: '浅夜森林',
    playerCount: 45,
    duration: 1823,
    status: 'completed',
    statusText: '已完成',
    fileSize: 15728640
  },
  {
    id: '2',
    fileName: 'EBG_PvP_Match_20240115_120521.zevtc',
    uploadTime: '2024-01-15 12:05:21',
    mapName: '永恒战场',
    serverName: '永恒战场',
    playerCount: 78,
    duration: 2341,
    status: 'completed',
    statusText: '已完成',
    fileSize: 25165824
  },
  {
    id: '3',
    fileName: 'OG_Skirmish_20240114_183045.zevtc',
    uploadTime: '2024-01-14 18:30:45',
    mapName: '荒漠绿洲',
    serverName: '绿茵王国',
    playerCount: 56,
    duration: 1654,
    status: 'parsing',
    statusText: '解析中',
    fileSize: 12582912
  },
  {
    id: '4',
    fileName: 'BL_Training_20240114_100012.zevtc',
    uploadTime: '2024-01-14 10:00:12',
    mapName: '蓝色边境',
    serverName: '浅夜森林',
    playerCount: 32,
    duration: 2156,
    status: 'completed',
    statusText: '已完成',
    fileSize: 18874368
  },
  {
    id: '5',
    fileName: 'EBG_Raid_20240113_201545.zevtc',
    uploadTime: '2024-01-13 20:15:45',
    mapName: '永恒战场',
    serverName: '永恒战场',
    playerCount: 89,
    duration: 3421,
    status: 'failed',
    statusText: '解析失败',
    fileSize: 41943040
  }
]

export const mockPlayers: PlayerStats[] = [
  {
    id: '1',
    name: 'Seraphina',
    profession: '元素使',
    damage: 15820000,
    healing: 8950000,
    kills: 23,
    deaths: 5,
    attendanceTime: 168900,
    score: 95.8,
    rank: 1
  },
  {
    id: '2',
    name: 'DragonSlayer',
    profession: '战士',
    damage: 14250000,
    healing: 2100000,
    kills: 31,
    deaths: 8,
    attendanceTime: 175200,
    score: 92.3,
    rank: 2
  },
  {
    id: '3',
    name: 'ShadowHunter',
    profession: '潜行者',
    damage: 12980000,
    healing: 1500000,
    kills: 28,
    deaths: 6,
    attendanceTime: 162000,
    score: 89.7,
    rank: 3
  },
  {
    id: '4',
    name: 'IronGuardian',
    profession: '守护者',
    damage: 8650000,
    healing: 12300000,
    kills: 12,
    deaths: 3,
    attendanceTime: 180000,
    score: 94.2,
    rank: 4
  },
  {
    id: '5',
    name: 'MysticMage',
    profession: '工程师',
    damage: 11230000,
    healing: 6800000,
    kills: 19,
    deaths: 7,
    attendanceTime: 158400,
    score: 87.5,
    rank: 5
  }
]

export const mockBuildCodes: BuildCode[] = [
  {
    id: '1',
    name: '元素使大团Build',
    code: '[&DQgEFQXw+v4fAwAAbAMAADwDAAA0BQAA7gAAAOABAADgAQAAAAAAAA==]',
    profession: '元素使',
    traits: [
      { id: '1', name: '风暴专家', tier: 3, slot: '天赋1' },
      { id: '2', name: '元素和谐', tier: 2, slot: '天赋2' },
      { id: '3', name: '火焰亲和', tier: 1, slot: '天赋3' }
    ],
    equipment: [
      { id: '1', name: '副手', type: 'weapon', stats: { power: 1000, precision: 800, toughness: 600, vitality: 700, critDamage: 1500 } },
      { id: '2', name: '胸甲', type: 'armor', stats: { power: 900, precision: 750, toughness: 650, vitality: 800, critDamage: 1400 } }
    ],
    skills: ['#1', '#2', '#3', '#4', '#5'],
    createdAt: '2024-01-10',
    updatedAt: '2024-01-15'
  },
  {
    id: '2',
    name: '战士冲锋Build',
    code: '[&DQgEFQXw+v4fAwAAbAMAADwDAAA0BQAA7gAAAOABAADgAQAAAAAAAA==]',
    profession: '战士',
    traits: [
      { id: '1', name: '力量训练', tier: 3, slot: '天赋1' },
      { id: '2', name: '战术精通', tier: 2, slot: '天赋2' },
      { id: '3', name: '武器专精', tier: 1, slot: '天赋3' }
    ],
    equipment: [
      { id: '1', name: '大剑', type: 'weapon', stats: { power: 1200, precision: 900, toughness: 700, vitality: 600, critDamage: 1600 } },
      { id: '2', name: '胸甲', type: 'armor', stats: { power: 1000, precision: 800, toughness: 800, vitality: 700, critDamage: 1500 } }
    ],
    skills: ['#1', '#2', '#3', '#4', '#5'],
    createdAt: '2024-01-12',
    updatedAt: '2024-01-14'
  }
]

export const mockDashboardStats: DashboardStats = {
  totalLogs: 156,
  totalPlayers: 42,
  totalDamage: 1856000000,
  totalHealing: 896000000,
  averageDuration: 2156,
  professionDistribution: {
    '元素使': 8,
    '战士': 7,
    '守护者': 6,
    '潜行者': 5,
    '工程师': 4,
    '幻术师': 3,
    '唤灵师': 3,
    '游侠': 2,
    '魂武师': 2,
    '铸剑师': 2
  },
  dailyTrend: [
    { date: '2024-01-10', damage: 125000000, healing: 68000000 },
    { date: '2024-01-11', damage: 138000000, healing: 72000000 },
    { date: '2024-01-12', damage: 142000000, healing: 75000000 },
    { date: '2024-01-13', damage: 119000000, healing: 65000000 },
    { date: '2024-01-14', damage: 156000000, healing: 82000000 },
    { date: '2024-01-15', damage: 168000000, healing: 89000000 }
  ]
}

export const mockAttendanceRecords: AttendanceRecord[] = [
  { id: '1', playerName: 'Seraphina', profession: '元素使', date: '2024-01-15', attendanceTime: 168900, damage: 15820000, healing: 8950000, kills: 23, deaths: 5, score: 95.8 },
  { id: '2', playerName: 'DragonSlayer', profession: '战士', date: '2024-01-15', attendanceTime: 175200, damage: 14250000, healing: 2100000, kills: 31, deaths: 8, score: 92.3 },
  { id: '3', playerName: 'ShadowHunter', profession: '潜行者', date: '2024-01-15', attendanceTime: 162000, damage: 12980000, healing: 1500000, kills: 28, deaths: 6, score: 89.7 },
  { id: '4', playerName: 'IronGuardian', profession: '守护者', date: '2024-01-15', attendanceTime: 180000, damage: 8650000, healing: 12300000, kills: 12, deaths: 3, score: 94.2 },
  { id: '5', playerName: 'MysticMage', profession: '工程师', date: '2024-01-14', attendanceTime: 158400, damage: 11230000, healing: 6800000, kills: 19, deaths: 7, score: 87.5 }
]

export class MockDataService {
  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms))
  }

  async fetchLogs(): Promise<LogFile[]> {
    await this.delay(500)
    return mockLogs
  }

  async fetchLogById(id: string): Promise<LogFile | undefined> {
    await this.delay(300)
    return mockLogs.find(log => log.id === id)
  }

  async fetchPlayers(): Promise<PlayerStats[]> {
    await this.delay(400)
    return mockPlayers
  }

  async fetchBuildCodes(): Promise<BuildCode[]> {
    await this.delay(350)
    return mockBuildCodes
  }

  async fetchDashboardStats(): Promise<DashboardStats> {
    await this.delay(450)
    return mockDashboardStats
  }

  async fetchAttendanceRecords(): Promise<AttendanceRecord[]> {
    await this.delay(400)
    return mockAttendanceRecords
  }

  generateRandomLogs(count: number): LogFile[] {
    const maps = ['蓝色边境', '永恒战场', '荒漠绿洲']
    const servers = ['浅夜森林', '永恒战场', '绿茵王国']
    const statuses: Array<'pending' | 'parsing' | 'completed' | 'failed'> = ['pending', 'parsing', 'completed', 'failed']

    return Array.from({ length: count }, (_, i) => ({
      id: String(i + 1),
      fileName: `Log_${Date.now()}_${i}.zevtc`,
      uploadTime: new Date(Date.now() - Math.random() * 86400000 * 7).toISOString(),
      mapName: maps[Math.floor(Math.random() * maps.length)],
      serverName: servers[Math.floor(Math.random() * servers.length)],
      playerCount: Math.floor(Math.random() * 50) + 20,
      duration: Math.floor(Math.random() * 3600) + 600,
      status: statuses[Math.floor(Math.random() * statuses.length)],
      statusText: statuses[Math.floor(Math.random() * statuses.length)] === ParseStatus.COMPLETED ? '已完成' : '处理中',
      fileSize: Math.floor(Math.random() * 50000000) + 5000000
    }))
  }
}

export const mockDataService = new MockDataService()
