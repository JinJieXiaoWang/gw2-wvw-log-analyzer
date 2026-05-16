export const professionInitial = (prof: string): string => {
  const map: Record<string, string> = {
    Elementalist: '元',
    Engineer: '工',
    Guardian: '守',
    Mesmer: '幻',
    Necromancer: '死',
    Ranger: '游',
    Revenant: '魂',
    Warrior: '战'
  }
  return map[prof] || prof.charAt(0)
}

export const subRoleLabel = (sub: string): string => {
  const map: Record<string, string> = { boon: '增益', heal: '治疗', tank: '承伤', cc: '削控' }
  return map[sub] || sub
}

export const formatFullDate = (dateStr: string): string => {
  return new Date(dateStr).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}
