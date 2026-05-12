/**
 * 评分规则配置相关常量
 * 所有硬编码颜色、图标、文案统一提取
 */

/** 角色类型图标映射 */
export const ROLE_ICON_MAP: Record<string, string> = {
  dps: 'pi pi-bolt',
  support: 'pi pi-heart',
  tank: 'pi pi-shield',
  condition: 'pi pi-fire',
  healing: 'pi pi-heart-fill',
  control: 'pi pi-lock',
  utility: 'pi pi-wrench',
}

/** 角色类型渐变色映射 */
export const ROLE_GRADIENT_MAP: Record<string, string> = {
  dps: '#FF8A65',
  support: '#00B4FF',
  tank: '#165DFF',
  condition: '#FF6B35',
  healing: '#00E5A0',
  control: '#6366F1',
  utility: '#0EA5E9',
}

/** 评分维度图标映射 */
export const DIMENSION_ICONS: Record<string, string> = {
  damage: 'pi pi-bolt',
  healing: 'pi pi-heart',
  protection: 'pi pi-shield',
  crowd_control: 'pi pi-lock',
  support: 'pi pi-star',
  survival: 'pi pi-users',
  objective: 'pi pi-flag',
  downstacks: 'pi pi-arrow-down',
}

/** 评分维度颜色映射 */
export const DIMENSION_COLORS: Record<string, string> = {
  damage: '#FF4D6A',
  healing: '#00D68F',
  protection: '#165DFF',
  crowd_control: '#9D4EDD',
  support: '#FFAA00',
  survival: '#00B4FF',
  objective: '#4CAF50',
  downstacks: '#FF5722',
}

/** 评分等级列表 */
export const GRADE_LIST = [
  { grade: 'S', range: '≥90分', desc: '表现卓越，远超平均水平', color: '#FFD700', color2: '#FFA500' },
  { grade: 'A', range: '≥80分', desc: '表现优秀，高于平均水平', color: '#00D68F', color2: '#00B4FF' },
  { grade: 'B', range: '≥70分', desc: '表现良好，达到平均水平', color: '#165DFF', color2: '#4080FF' },
  { grade: 'C', range: '≥60分', desc: '表现一般，略低于平均', color: '#FFAA00', color2: '#FFB347' },
  { grade: 'D', range: '≥40分', desc: '表现较差，需要改进', color: '#FF6B35', color2: '#FF8A65' },
  { grade: 'F', range: '<40分', desc: '表现很差，急需提升', color: '#FF4D6A', color2: '#FF8A80' },
]

/** 默认角色类型（API失败回退） */
export const DEFAULT_ROLE_TYPES = [
  { type: 'dps', label: '输出', description: '以伤害输出为主要职责', icon: 'pi pi-bolt', color: '#FF4D6A' },
  { type: 'support', label: '辅助', description: '以治疗和增益为主要职责', icon: 'pi pi-heart', color: '#00D68F' },
  { type: 'tank', label: '承伤', description: '以吸收伤害和控制为主要职责', icon: 'pi pi-shield', color: '#9D4EDD' },
]
