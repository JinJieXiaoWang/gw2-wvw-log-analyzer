import { computed } from 'vue'

const ABILITY_LABEL_MAP: Record<string, string> = {
  damage: '输出',
  mobility: '机动',
  survival: '生存',
  healing: '治疗',
  support: '辅助',
  utility: '技能',
}

const DEFAULT_ABILITIES: Record<string, number> = {
  damage: 70, mobility: 65, survival: 65,
  healing: 60, support: 55, utility: 60,
}

const ABILITY_ORDER = ['damage', 'mobility', 'survival', 'healing', 'support', 'utility']

/**
 * 出勤详情数据计算组合式函数
 * @param dataSource 返回详情数据的 getter 函数，确保响应式更新
 */
export function useAttendanceDetail(dataSource: () => any) {
  const summary = computed(() => dataSource()?.summary || {})
  const characters = computed(() => dataSource()?.characters || [])
  const recentFights = computed(() => dataSource()?.recent_fights || [])
  const dailyFights = computed(() => dataSource()?.daily_fights || [])

  // 使用后端返回的综合能力评分，缺失项使用默认值补齐
  const abilities = computed(() => {
    const comprehensiveAbilities = dataSource()?.comprehensive_abilities
    return { ...DEFAULT_ABILITIES, ...comprehensiveAbilities }
  })

  // 按固定顺序排列的能力条目，支持动态渲染
  const abilityEntries = computed(() => {
    return ABILITY_ORDER
      .filter(k => k in abilities.value)
      .map(k => ({
        key: k,
        value: abilities.value[k],
        label: ABILITY_LABEL_MAP[k] || k,
      }))
  })

  // 从数据中计算出勤趋势，或使用默认值
  const calculateChartPoints = () => {
    const attendanceData = dataSource()?.attendance_trend || []
    if (attendanceData.length >= 7) {
      return attendanceData.slice(-7).map((val: number, i: number) => ({
        x: 50 + i * 80,
        y: Math.max(30, 220 - val * 18)
      }))
    }

    // 使用默认模拟数据，但基于出勤天数调整
    const avgAttendance = summary.value.attendance_count || 10
    const basePoints = [6, 8, 5, 9, 7, 10, 8].map(v => Math.round(v * (avgAttendance / 10)))
    return basePoints.map((val, i) => ({ x: 50 + i * 80, y: Math.max(30, 220 - val * 14) }))
  }

  const chartPoints = computed(() => calculateChartPoints())

  const chartLinePath = computed(() =>
    chartPoints.value.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ')
  )

  const chartAreaPath = computed(() => {
    if (chartPoints.value.length === 0) return ''
    const last = chartPoints.value[chartPoints.value.length - 1]
    const first = chartPoints.value[0]
    return `${chartLinePath.value} L ${last.x} 220 L ${first.x} 220 Z`
  })

  const radarValues = computed(() =>
    abilityEntries.value.map(e => e.value)
  )

  const radarPolygonPoints = computed(() =>
    radarValues.value.map((val, i) => {
      const angle = (Math.PI / 3) * i - Math.PI / 2
      const r = (val / 100) * 65
      return `${100 + r * Math.cos(angle)},${100 + r * Math.sin(angle)}`
    }).join(' ')
  )

  const radarCirclePoints = computed(() =>
    radarValues.value.map((val, i) => {
      const angle = (Math.PI / 3) * i - Math.PI / 2
      const r = (val / 100) * 65
      return { x: 100 + r * Math.cos(angle), y: 100 + r * Math.sin(angle) }
    })
  )

  const radarLabels = computed(() => {
    const positions = [
      { x: 100, y: 25 },
      { x: 162, y: 52 },
      { x: 162, y: 148 },
      { x: 100, y: 175 },
      { x: 38, y: 148 },
      { x: 38, y: 52 },
    ]
    return abilityEntries.value.map((e, i) => ({
      x: positions[i]?.x ?? 100,
      y: positions[i]?.y ?? 25,
      text: e.label,
      key: e.key,
    }))
  })

  function getHexagonPoints(radius: number) {
    const points: string[] = []
    for (let i = 0; i < 6; i++) {
      const angle = (Math.PI / 3) * i - Math.PI / 2
      points.push(`${100 + radius * Math.cos(angle)},${100 + radius * Math.sin(angle)}`)
    }
    return points.join(' ')
  }

  function getAxisPoint(index: number) {
    const angle = (Math.PI / 3) * index - Math.PI / 2
    return { x: 100 + 70 * Math.cos(angle), y: 100 + 70 * Math.sin(angle) }
  }

  return {
    summary, characters, recentFights, dailyFights, abilities, abilityEntries,
    chartPoints, chartLinePath, chartAreaPath,
    radarPolygonPoints, radarCirclePoints, radarLabels,
    getHexagonPoints, getAxisPoint,
  }
}
