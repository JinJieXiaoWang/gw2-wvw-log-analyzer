/**
 * 出勤详情 CSV 导出工具
 */

function escapeCsv(val: unknown): string {
  const str = String(val ?? '')
  if (str.includes(',') || str.includes('"') || str.includes('\n')) {
    return `"${str.replace(/"/g, '""')}"`
  }
  return str
}

function rowToCsv(cells: unknown[]): string {
  return cells.map(escapeCsv).join(',')
}

function downloadCsv(filename: string, content: string) {
  const blob = new Blob(['\uFEFF' + content], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

/**
 * 导出出勤详情为 CSV
 * @param account 玩家账号
 * @param data 出勤详情数据
 */
export function exportAttendanceCsv(account: string, data: any) {
  const summary = data?.summary || {}
  const characters = data?.characters || []
  const fights = data?.recent_fights || []

  const lines: string[] = []

  // === 基本信息 ===
  lines.push('基本信息')
  lines.push(rowToCsv(['账号', account]))
  lines.push(rowToCsv(['服务器', data?.server || '']))
  lines.push(rowToCsv(['排名', data?.rank || '']))
  lines.push(rowToCsv(['加入日期', data?.join_date || '']))
  lines.push('')

  // === 出勤摘要 ===
  lines.push('出勤摘要')
  lines.push(rowToCsv(['指标', '数值']))
  lines.push(rowToCsv(['出勤天数', summary.attendance_count || 0]))
  lines.push(rowToCsv(['总参战时长(秒)', summary.total_duration_sec || 0]))
  lines.push(rowToCsv(['总伤害', summary.total_damage || 0]))
  lines.push(rowToCsv(['K/D', summary.kd_ratio || 0]))
  lines.push(rowToCsv(['平均评分', summary.avg_score || 0]))
  lines.push(rowToCsv(['总击杀', summary.total_kills || 0]))
  lines.push(rowToCsv(['总死亡', summary.total_deaths || 0]))
  lines.push(rowToCsv(['总击倒', summary.total_downed || 0]))
  lines.push('')

  // === 角色列表 ===
  lines.push('角色列表')
  lines.push(rowToCsv([
    '角色名', '职业', '使用次数', '总伤害', '平均DPS',
    '总击杀', '总死亡', '平均评分', '主要角色'
  ]))
  for (const char of characters) {
    lines.push(rowToCsv([
      char.character_name,
      char.profession,
      char.use_count || 0,
      char.total_damage || 0,
      char.avg_dps || 0,
      char.total_kills || 0,
      char.total_deaths || 0,
      char.avg_score || 0,
      char.primary_role || '',
    ]))
  }
  lines.push('')

  // === 战斗记录 ===
  lines.push('战斗记录')
  lines.push(rowToCsv([
    '日期', '地图', '角色名', '职业', '伤害', 'DPS',
    '击杀', '死亡', '击倒', '评分', '评分等级', '时长(秒)'
  ]))
  for (const fight of fights) {
    lines.push(rowToCsv([
      fight.fight_date || '',
      fight.map_name || '',
      fight.character_name || '',
      fight.profession || '',
      fight.damage || 0,
      fight.dps || 0,
      fight.kills || 0,
      fight.deaths || 0,
      fight.downed || 0,
      fight.score || 0,
      fight.score_grade || '',
      fight.duration_sec || 0,
    ]))
  }

  const safeAccount = account.replace(/[@#]/g, '_')
  downloadCsv(`出勤详情_${safeAccount}_${new Date().toISOString().slice(0, 10)}.csv`, lines.join('\n'))
}
