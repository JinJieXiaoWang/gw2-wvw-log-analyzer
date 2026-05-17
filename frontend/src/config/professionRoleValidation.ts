/**
 * 职业角色定位校验配置
 * 功能：定义各精英特长的推荐角色定位，用于检测不合理的配置
 * 数据来源：backend/app/data/seeds/v1.0.0/006_gw_elite_specialization.json
 */

export type RoleType = 'dps' | 'support' | 'tank' | 'control'

/** 精英特长推荐角色定位映射 */
export const RECOMMENDED_ROLE_MAP: Record<string, RoleType> = {
  // Guardian
  Dragonhunter: 'dps',
  Firebrand: 'support',
  Willbender: 'dps',
  Luminary: 'support',
  // Warrior
  Berserker: 'dps',
  Spellbreaker: 'control',
  Bladesworn: 'dps',
  Paragon: 'tank',
  // Engineer
  Scrapper: 'support',
  Holosmith: 'dps',
  Mechanist: 'support',
  Amalgam: 'dps',
  // Ranger
  Druid: 'support',
  Soulbeast: 'dps',
  Untamed: 'dps',
  Galeshot: 'dps',
  // Thief
  Daredevil: 'dps',
  Deadeye: 'dps',
  Specter: 'dps',
  Antiquary: 'support',
  // Elementalist
  Tempest: 'support',
  Weaver: 'dps',
  Catalyst: 'dps',
  Evoker: 'dps',
  // Mesmer
  Chronomancer: 'support',
  Mirage: 'dps',
  Virtuoso: 'dps',
  Troubadour: 'support',
  // Necromancer
  Reaper: 'dps',
  Scourge: 'support',
  Harbinger: 'dps',
  Ritualist: 'support',
  // Revenant
  Herald: 'support',
  Renegade: 'dps',
  Vindicator: 'dps',
  Conduit: 'support',
} as const

/** 角色定位显示名称 */
export const ROLE_LABEL_MAP: Record<RoleType, string> = {
  dps: '输出',
  support: '辅助',
  tank: '坦克',
  control: '控制',
}

/** 检查角色定位是否与推荐定位冲突
 * @param profession 精英特长英文名
 * @param currentRole 当前角色定位
 * @returns 冲突信息，无冲突返回 null
 */
export function checkRoleConflict(profession: string | undefined, currentRole: string | undefined): { recommended: RoleType; message: string } | null {
  if (!profession || !currentRole) return null
  const recommended = RECOMMENDED_ROLE_MAP[profession]
  if (!recommended) return null
  if (recommended === currentRole) return null
  return {
    recommended,
    message: `${profession} 的推荐定位为「${ROLE_LABEL_MAP[recommended]}」，当前设置为「${ROLE_LABEL_MAP[currentRole as RoleType] || currentRole}」`,
  }
}

/** 检查是否为高风险的角色-职业组合（如坦克+狂战士） */
export function isHighRiskRoleProfCombination(roleLabel: string, profession: string | undefined): boolean {
  if (!profession) return false
  const recommended = RECOMMENDED_ROLE_MAP[profession]
  if (!recommended) return false
  // 如果角色定位与推荐定位不同，认为是高风险
  return recommended !== roleLabel
}
