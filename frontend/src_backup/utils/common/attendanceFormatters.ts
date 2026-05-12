export function formatDateParam(date: Date): string {
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

export function formatDate(iso: string): string {
  try {
    const d = new Date(iso)
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
  } catch {
    return iso
  }
}

export function formatDateTime(iso: string): string {
  try {
    const d = new Date(iso)
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
  } catch {
    return iso
  }
}

export function formatNumber(num: number | string | undefined): string {
  const n = Number(num)
  if (!n && n !== 0) return '0'
  if (n >= 1000000) return (n / 1000000).toFixed(1) + 'M'
  if (n >= 1000) return (n / 1000).toFixed(1) + 'K'
  return n.toLocaleString()
}

export function formatDps(dps: number | string | undefined): string {
  const n = Number(dps)
  if (!n && n !== 0) return '0K'
  if (n >= 1000) {
    const result = Math.floor(n / 100) / 10
    return result.toFixed(1).replace(/\.0$/, '') + 'K'
  }
  return n + 'K'
}

export function formatDuration(seconds: number | string | undefined): string {
  const s = Number(seconds)
  if (!s || isNaN(s)) return '0分钟'
  const hours = Math.floor(s / 3600)
  const minutes = Math.floor((s % 3600) / 60)
  if (hours > 0 && minutes > 0) return `${hours}小时${minutes}分钟`
  if (hours > 0) return `${hours}Сʱ`
  return `${minutes}分钟`
}

export function getProfessionLabel(profession: string): string {
  const map: Record<string, string> = {
    warrior: '战士', guardian: '守护者', thief: '潜行者', ranger: '游侠',
    engineer: '工程师', elementalist: '元素使', necromancer: '死灵法师',
    mesmer: '幻术师', reaper: '唤灵师', revenant: '魂武者',
  }
  return map[profession] || profession
}

export function getScoreColor(score: number): string {
  if (score >= 90) return 'game-badge game-badge-legendary'
  if (score >= 80) return 'game-badge game-badge-exotic'
  if (score >= 70) return 'game-badge game-badge-rare'
  return 'game-badge'
}
