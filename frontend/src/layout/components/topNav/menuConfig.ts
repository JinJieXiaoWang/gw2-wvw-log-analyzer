export interface MenuItem {
  path: string
  label: string
  icon: string
  description?: string
  requireAuth?: boolean
}

export const menuItems: MenuItem[] = [
  { path: '/', label: '数据看板', icon: 'pi pi-chart-line', description: '可视化数据' },
  { path: '/logs', label: '日志管理', icon: 'pi pi-file', description: '解析与管理' },
  { path: '/attendance', label: '出勤统计', icon: 'pi pi-users', description: '团队数据' },
  { path: '/skill-analysis', label: '技能循环', icon: 'pi pi-sync', description: '循环分析' },
  { path: '/builds', label: '配置图书馆', icon: 'pi pi-book', description: '战场配置百科' },
  { path: '/build-parser', label: 'Build解析', icon: 'pi pi-code', description: '配置分析' },
  { path: '/settings', label: '系统设置', icon: 'pi pi-cog', description: '系统配置', requireAuth: true },
]
