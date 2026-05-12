export const weaponNameMap: Record<string, string> = {
  Sword: '剑', Axe: '斧', Mace: '锤', Shield: '盾',
  Greatsword: '大剑', Hammer: '巨锤', Staff: '法杖',
  Scepter: '权杖', Focus: '聚能器', Dagger: '匕首',
  Pistol: '手枪', Rifle: '步枪', Shortbow: '短弓',
  Longbow: '长弓', Torch: '火炬', Warhorn: '战号',
  Spear: '矛', Trident: '三叉戟', Harpoon: '鱼叉',
}

export function getScoreSeverity(grade: string): string {
  const map: Record<string, string> = {
    'S+': 'success', 'S': 'success', 'S-': 'success',
    'A+': 'info', 'A': 'info', 'A-': 'info',
    'B+': 'warning', 'B': 'warning', 'B-': 'warning',
    'C+': 'danger', 'C': 'danger', 'C-': 'danger',
    'D': 'danger', 'F': 'danger',
  }
  return map[grade] || 'secondary'
}
