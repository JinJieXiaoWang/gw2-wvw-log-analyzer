export const getProfessionColor = (profession: string): string => {
  const colors: Record<string, string> = {
    Warrior: '#E85D04',
    Guardian: '#FAA307',
    Revenant: '#9D4EDD',
    Ranger: '#06D6A0',
    Engineer: '#7B8FA1',
    Necromancer: '#8D0801',
    Mesmer: '#4361EE',
    Elementalist: '#FF6B6B'
  }
  return colors[profession] || '#6C757D'
}

export const getProfessionInitial = (profession: string): string => {
  const map: Record<string, string> = {
    Elementalist: '元', Engineer: '工', Guardian: '守', Mesmer: '幻',
    Necromancer: '死', Ranger: '游', Revenant: '魂', Thief: '潜',
    Warrior: '战',
  }
  return map[profession] || profession.charAt(0).toUpperCase()
}

export const cleanIconUrl = (iconUrl: string): string => {
  if (!iconUrl) return ''
  return iconUrl.trim().replace(/^[`'"]+|[`'"]+$/g, '')
}
