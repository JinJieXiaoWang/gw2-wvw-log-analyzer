import { reactive, computed } from 'vue'

export function useAttendanceDetail(data: any) {
  const summary = computed(() => data?.summary || {})
  const characters = computed(() => data?.characters || [])
  const recentFights = computed(() => data?.recent_fights || [])

  // 从数据中计算能力值，或使用默认值
  const calculateAbilities = () => {
    const chars = characters.value
    if (!chars.length) {
      return {
        damage: 75, healing: 60, survival: 70,
        support: 55, utility: 65, mobility: 62,
      }
    }
    
    // 基于角色数据计算综合能力值
    let totalDamage = 0
    let totalHealing = 0
    let totalSurvival = 0
    let totalSupport = 0
    let totalUtility = 0
    let totalMobility = 0
    
    chars.forEach(char => {
      const avgScore = char.avg_score || 0
      const kd = char.kd_ratio || 0
      const dps = char.avg_dps || 0
      
      // 输出能力：基于DPS和评分
      totalDamage += Math.min(100, (dps / 15000) * 60 + (avgScore / 100) * 40)
      
      // 治疗能力：如果职业是治疗职业则加分
      const isHealer = ['守护', '魂武者', '元素使', '工程师'].includes(char.profession)
      totalHealing += isHealer ? avgScore * 0.8 : avgScore * 0.3
      
      // 生存能力：基于K/D
      totalSurvival += Math.min(100, kd * 30 + avgScore * 0.5)
      
      // 辅助能力：基于治疗职业
      totalSupport += isHealer ? avgScore * 0.7 : avgScore * 0.2
      
      // 技能运用：基于评分
      totalUtility += avgScore * 0.7 + 20
      
      // 机动能力：基于职业
      const isMobile = ['游侠', '盗贼', '战士', '魂武者'].includes(char.profession)
      totalMobility += isMobile ? avgScore * 0.8 : avgScore * 0.5
    })
    
    const count = chars.length
    return {
      damage: Math.round(totalDamage / count),
      healing: Math.round(totalHealing / count),
      survival: Math.round(totalSurvival / count),
      support: Math.round(totalSupport / count),
      utility: Math.round(totalUtility / count),
      mobility: Math.round(totalMobility / count),
    }
  }

  const abilities = reactive(calculateAbilities())

  // 从数据中计算出勤趋势，或使用默认值
  const calculateChartPoints = () => {
    const attendanceData = data?.attendance_trend || []
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

  const radarValues = computed(() => [
    abilities.damage, abilities.mobility, abilities.survival,
    abilities.healing, abilities.support, abilities.utility,
  ])

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

  const radarLabels = [
    { x: 100, y: 25, text: '输出' },
    { x: 162, y: 52, text: '机动' },
    { x: 162, y: 148, text: '生存' },
    { x: 100, y: 175, text: '治疗' },
    { x: 38, y: 148, text: '辅助' },
    { x: 38, y: 52, text: '技能' },
  ]

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
    summary, characters, recentFights, abilities,
    chartPoints, chartLinePath, chartAreaPath,
    radarPolygonPoints, radarCirclePoints, radarLabels,
    getHexagonPoints, getAxisPoint,
  }
}
