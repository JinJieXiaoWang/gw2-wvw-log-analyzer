import { reactive, computed } from 'vue'

export function useAttendanceDetail(data: any) {
  const summary = computed(() => data?.summary || {})
  const characters = computed(() => data?.characters || [])
  const recentFights = computed(() => data?.recent_fights || [])

  const abilities = reactive({
    damage: 85, healing: 65, survival: 72,
    support: 58, utility: 70, mobility: 68,
  })

  const chartPoints = computed(() => {
    const basePoints = [6, 8, 5, 9, 7, 10, 8]
    return basePoints.map((val, i) => ({ x: 50 + i * 55, y: 170 - val * 14 }))
  })

  const chartLinePath = computed(() =>
    chartPoints.value.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ')
  )

  const chartAreaPath = computed(() => {
    const last = chartPoints.value[chartPoints.value.length - 1]
    const first = chartPoints.value[0]
    return `${chartLinePath.value} L ${last.x} 170 L ${first.x} 170 Z`
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
