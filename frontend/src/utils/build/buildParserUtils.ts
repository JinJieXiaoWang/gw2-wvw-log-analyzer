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
  return profession.charAt(0).toUpperCase()
}

export const cleanIconUrl = (iconUrl: string): string => {
  if (!iconUrl) return ''
  return iconUrl.trim().replace(/^[`'"]+|[`'"]+$/g, '')
}
