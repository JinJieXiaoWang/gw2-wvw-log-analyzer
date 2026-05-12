/**
 * Build配置相关类型定义
 * 作者：帅姐姐
 * 创建日期：2026-05-04
 */

// Build解析响应
export interface BuildParseResponse {
  id: string;
  bdCode: string;
  profession: string;
  eliteSpec?: string;
  weapons: BuildWeapon[];
  traits: BuildTrait[];
  skills: BuildSkill[];
  attributes: BuildAttributes;
  isMeta: boolean;
  role: 'dps' | 'support';
  description?: string;
}

// 武器配置
export interface BuildWeapon {
  set: number;
  mainhand: string;
  offhand?: string;
  sigils: string[];
}

// 特性配置
export interface BuildTrait {
  line: string;
  major1: string;
  major2: string;
  major3: string;
  minor1: string;
  minor2: string;
  minor3: string;
}

// 技能配置
export interface BuildSkill {
  slot: string;
  name: string;
  id: number;
}

// 属性
export interface BuildAttributes {
  power: number;
  precision: number;
  ferocity: number;
  conditionDamage: number;
  conditionDuration: number;
  healingPower: number;
  toughness: number;
  vitality: number;
  concentration: number;
  boonDuration: number;
}

// Build配置保存请求
export interface BuildSaveRequest {
  title: string;
  description?: string;
  bdCode: string;
  profession: string;
  eliteSpec?: string;
  weapons: BuildWeapon[];
  traits: BuildTrait[];
  skills: BuildSkill[];
  attributes: BuildAttributes;
  isMeta: boolean;
  role: 'dps' | 'support';
  tags?: string[];
}

// Build配置列表项
export interface BuildEntry {
  id: string;
  title: string;
  description?: string;
  bdCode?: string;
  profession: string;
  eliteSpec?: string;
  role: 'dps' | 'support';
  isMeta: boolean;
  armorType?: string;
  weapons?: BuildWeapon[];
  rune?: string;
  tags?: string[];
  createdAt: string;
  updatedAt: string;
}

// Build配置查询参数
export interface BuildQueryParams {
  page?: number;
  pageSize?: number;
  profession?: string;
  role?: 'dps' | 'support';
  searchQuery?: string;
}

// Build配置列表响应
export interface BuildListResponse {
  items: BuildEntry[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

// 技能循环分析响应
export interface SkillAnalysisResponse {
  logId: string;
  memberId: string;
  rotations: SkillRotation[];
  idealRotation: SkillRotation[];
  stats: SkillStats;
}

// 技能循环项
export interface SkillRotation {
  id: number;
  name: string;
  icon?: string;
  timestamp: number;
  isMistake?: boolean;
}

// 技能统计
export interface SkillStats {
  totalCasts: number;
  successRate: number;
  mistakes: SkillMistake[];
  avgCastTime: number;
  boonCoverage: BoonCoverage;
}

// 技能失误
export interface SkillMistake {
  skillName: string;
  description: string;
  timestamp: number;
  type: 'missed' | 'early' | 'late' | 'wrong';
}

// 增益覆盖
export interface BoonCoverage {
  might?: number;
  fury?: number;
  quickness?: number;
  alacrity?: number;
}
