/**
 * Elite Insights JSON 数据格式类型定义
 * 作者：帅姐姐
 * 创建日期：2024-01-15
 *
 * 该文件定义了 GW2 WvW 日志解析系统的完整数据结构
 *
 * 注意：职业相关映射已迁移到 @/utils/profession/professionUtils
 * 请使用 getProfessionName(), getProfessionColor(), getProfessionIconUrl() 等函数
 * 该文件中的 PROFESSIONS, PROFESSION_COLORS 等硬编码数据仅作为向后兼容保留
 */

import {
  getProfessionName as _getProfessionName,
  getProfessionColor as _getProfessionColor,
  getProfessionIconUrl as _getProfessionIconUrl
} from '@/utils/profession/professionUtils'

// =============================================
// 基础类型定义
// =============================================

export interface Phase {
  name: string;
  start: number;
  end: number;
  breakbarPhase: boolean;
  phaseIndex: number;
  phaseTargets: number[];
  canSubPhase: boolean;
  isSubPhase: boolean;
}

export interface ScoreDetails {
  effectiveDamage: number;
  breakbarDamage: number;
  survival: number;
  boonStrips?: number;
  condiCleanses?: number;
}

// =============================================
// 目标 (Target) 数据结构
// =============================================

export interface Target {
  id: number;
  finalHealth: number;
  healthPercentBurned: number;
  firstAware: number;
  lastAware: number;
  buffs: any[];
  enemyPlayer: boolean;
  breakbarPercents: number[];
  name: string;
  totalHealth: number;
  condition: number;
  concentration: number;
  healing: number;
  toughness: number;
  hitboxHeight: number;
  hitboxWidth: number;
  instanceID: number;
  teamID: number;
  isFake: boolean;
  dpsAll: TargetDps[];
  statsAll: TargetStats[];
  defenses: TargetDefense[];
  totalDamageDist: any[][];
  totalDamageTaken: any[][];
  damage1S: number[][];
  powerDamage1S: number[][];
  conditionDamage1S: number[][];
  icon?: string;
}

export interface TargetDps {
  [key: string]: any;
}

export interface TargetStats {
  [key: string]: any;
}

export interface TargetDefense {
  [key: string]: any;
}

// =============================================
// 玩家 (Player) 数据结构
// =============================================

export interface Player {
  account: string;
  group: number;
  hasCommanderTag: boolean;
  profession: string;
  friendlyNPC: boolean;
  notInSquad: boolean;
  weapons: any[];
  consumables?: {
    food: { id: number; time: number; duration: number }[];
    utility: { id: number; time: number; duration: number }[];
  };
  dpsAll: PlayerDps[];
  statsAll: PlayerStats[];
  defenses: PlayerDefense[];
  support: PlayerSupport[];
  totalDamageDist: any[][];
  totalDamageTaken: any[][];
  damage1S: number[][];
  powerDamage1S: number[][];
  conditionDamage1S: number[][];
  buffUptimes: PlayerBuffUptime[];
  selfBuffs: any[];
  buffUptimesActive: any[];
  selfBuffsActive: any[];
  activeTimes: number[];
  name: string;
  totalHealth: number;
  condition: number;
  concentration: number;
  healing: number;
  toughness: number;
  hitboxHeight: number;
  hitboxWidth: number;
  instanceID: number;
  teamID: number;
  isFake: boolean;
  dpsTargets: any[][];
  targetDamage1S: any[][];
  targetPowerDamage1S: any[][];
  targetConditionDamage1S: any[][];
  targetDamageDist: any[][];
  statsTargets: any[][];
  healthPercents: number[];
  barrierPercents: number[];
  rotation: any[][];
  damageModifiers: any[][];
  damageModifiersTarget: any[][];
  role: string;
  total_score: number;
  score_details: ScoreDetails;
  dps: number;
  cc: number;
  cleanses: number;
  strips: number;
  downs: number;
  deaths: number;
  buffs: {
    [buffId: string]: {
      id: number;
      uptime_ms: number;
    };
  };
  healingStats?: HealingStats;
  hps?: number;
  critRate?: number;
  healingSkillsCount?: number;
  critDamage?: number;
  precision?: number;
  power?: number;
  vitality?: number;
}

export interface HealingStats {
  healing: number;
  hps: number;
  healingTargetCount: number;
  avgHealing: number;
  overhealing: number;
  overhealingPct: number;
  absorbed: number;
  absorbedHps: number;
  overheal?: number;
  barrier?: number;
  critPercent?: number;
}

export interface PlayerDps {
  dps: number;
  damage: number;
  condiDps: number;
  condiDamage: number;
  powerDps: number;
  powerDamage: number;
  breakbarDamage: number;
  actorDps: number;
  actorDamage: number;
  actorCondiDps: number;
  actorCondiDamage: number;
  actorPowerDps: number;
  actorPowerDamage: number;
  actorBreakbarDamage: number;
}

export interface PlayerStats {
  wasted: number;
  timeWasted: number;
  saved: number;
  timeSaved: number;
  stackDist: number;
  distToCom: number;
  avgBoons: number;
  avgActiveBoons: number;
  avgConditions: number;
  avgActiveConditions: number;
  swapCount: number;
  skillCastUptime: number;
  skillCastUptimeNoAA: number;
  totalDamageCount: number;
  totalDmg: number;
  directDamageCount: number;
  directDmg: number;
  connectedDirectDamageCount: number;
  connectedDirectDmg: number;
  connectedDamageCount: number;
  connectedDmg: number;
  critableDirectDamageCount: number;
  criticalRate: number;
  criticalDmg: number;
  flankingRate: number;
  againstMovingRate: number;
  glanceRate: number;
  missed: number;
  evaded: number;
  blocked: number;
  interrupts: number;
  invulned: number;
  killed: number;
  downed: number;
  downContribution: number;
  connectedPowerCount: number;
  connectedPowerAbove90HPCount: number;
  connectedConditionCount: number;
  connectedConditionAbove90HPCount: number;
  againstDownedCount: number;
  againstDownedDamage: number;
}

export interface PlayerDefense {
  damageTaken: number;
  downedDamageTaken: number;
  breakbarDamageTaken: number;
  blockedCount: number;
  evadedCount: number;
  missedCount: number;
  dodgeCount: number;
  invulnedCount: number;
  damageBarrier: number;
  interruptedCount: number;
  downCount: number;
  downDuration: number;
  deadCount: number;
  deadDuration: number;
  dcCount: number;
  dcDuration: number;
  boonStrips: number;
  boonStripsTime: number;
  conditionCleanses: number;
  conditionCleansesTime: number;
}

export interface PlayerSupport {
  condiCleanse: number;
  boonStrips: number;
}

export interface PlayerBuffUptime {
  id: number;
  buffData: {
    uptime: number;
    buffApplied: number;
    wasted: number;
    extended: number;
    unknownExtended: number;
    stackRemoval: number;
    stackDist: number[];
  }[];
  uptime: number;
}

// =============================================
// 完整的 Elite Insights 日志数据结构
// =============================================

export interface EliteInsightsLog {
  eliteInsightsVersion: string;
  triggerID: number;
  eiEncounterID: number;
  fightName: string;
  fightIcon: string;
  arcVersion: string;
  gw2Build: number;
  language: string;
  fractalScale: number;
  languageID: number;
  recordedBy: string;
  recordedAccountBy: string;
  timeStart: string;
  timeEnd: string;
  timeStartStd: string;
  timeEndStd: string;
  duration: number;
  durationMS: number;
  logStartOffset: number;
  success: boolean;
  isCM: boolean;
  anonymous: boolean;
  detailedWvW: boolean;
  phases: Phase[];
  targets: Target[];
  players: Player[];
  // 可选的额外数据字段
  graphData?: any;
  healingStatsExtension?: any;
  barrierStatsExtension?: any;
  crData?: any;
}

// =============================================
// 辅助工具类型
// =============================================

// 职业映射
export const PROFESSIONS = {
  // Guardian 守护者
  'Guardian': '守护者',
  'Dragonhunter': '猎龙者',
  'Firebrand': '燃火者',
  'Willbender': '破锋者',
  'Luminary': '圣辉者',
  
  // Warrior 战士
  'Warrior': '战士',
  'Berserker': '狂战士',
  'Spellbreaker': '破法者',
  'Bladesworn': '誓剑士',
  'Paragon': '圣言士',
  
  // Engineer 工程师
  'Engineer': '工程师',
  'Scrapper': '机械师',
  'Holosmith': '全息师',
  'Mechanist': '玉偃师',
  'Amalgam': '流金师',
  
  // Ranger 游侠
  'Ranger': '游侠',
  'Druid': '德鲁伊',
  'Soulbeast': '魂兽师',
  'Untamed': '狂兽师',
  'Galeshot': '风冲击',
  
  // Thief 潜行者
  'Thief': '潜行者',
  'Daredevil': '独行侠',
  'Deadeye': '神枪手',
  'Specter': '缚影者',
  'Antiquary': '彩戏师',
  
  // Elementalist 元素使
  'Elementalist': '元素使',
  'Tempest': '暴风使',
  'Weaver': '编织者',
  'Catalyst': '元晶师',
  'Evoker': '唤元师',
  
  // Mesmer 幻术师
  'Mesmer': '幻术师',
  'Chronomancer': '时空术士',
  'Mirage': '幻象术士',
  'Virtuoso': '灵刃术士',
  'Troubadour': '吟游诗人',
  
  // Necromancer 死灵法师
  'Necromancer': '死灵法师',
  'Reaper': '夺魂者',
  'Scourge': '灾厄师',
  'Harbinger': '先驱者',
  'Ritualist': '祭祀者',
  
  // Revenant 魂武者
  'Revenant': '魂武者',
  'Herald': '预告者',
  'Renegade': '龙魂使',
  'Vindicator': '裁决者',
  'Conduit': '契灵使'
};

// 角色颜色映射
export const PROFESSION_COLORS = {
  // Guardian 守护者
  'Guardian': 'rgb(251,207,75)',
  'Dragonhunter': 'rgb(232,159,72)',
  'Firebrand': 'rgb(245,173,31)',
  'Willbender': 'rgb(255,223,128)',
  'Luminary': 'rgb(255,215,0)',
  
  // Warrior 战士
  'Warrior': 'rgb(255,218,107)',
  'Berserker': 'rgb(255,153,0)',
  'Spellbreaker': 'rgb(239,217,125)',
  'Bladesworn': 'rgb(215,175,105)',
  'Paragon': 'rgb(255,200,100)',
  
  // Engineer 工程师
  'Engineer': 'rgb(184,116,44)',
  'Scrapper': 'rgb(160,140,80)',
  'Holosmith': 'rgb(255,215,0)',
  'Mechanist': 'rgb(208,156,89)',
  'Amalgam': 'rgb(200,180,120)',
  
  // Ranger 游侠
  'Ranger': 'rgb(119,186,79)',
  'Druid': 'rgb(89,166,59)',
  'Soulbeast': 'rgb(109,176,69)',
  'Untamed': 'rgb(139,196,99)',
  'Galeshot': 'rgb(150,200,100)',
  
  // Thief 潜行者
  'Thief': 'rgb(231,124,3)',
  'Daredevil': 'rgb(232,127,12)',
  'Deadeye': 'rgb(242,147,22)',
  'Specter': 'rgb(180,100,30)',
  'Antiquary': 'rgb(220,140,60)',
  
  // Elementalist 元素使
  'Elementalist': 'rgb(238,105,105)',
  'Tempest': 'rgb(100,180,220)',
  'Weaver': 'rgb(200,120,120)',
  'Catalyst': 'rgb(180,100,100)',
  'Evoker': 'rgb(220,100,140)',
  
  // Mesmer 幻术师
  'Mesmer': 'rgb(153,102,204)',
  'Chronomancer': 'rgb(170,151,217)',
  'Mirage': 'rgb(180,122,224)',
  'Virtuoso': 'rgb(160,140,210)',
  'Troubadour': 'rgb(190,160,220)',
  
  // Necromancer 死灵法师
  'Necromancer': 'rgb(68,138,92)',
  'Reaper': 'rgb(88,158,112)',
  'Scourge': 'rgb(100,140,100)',
  'Harbinger': 'rgb(78,148,102)',
  'Ritualist': 'rgb(90,160,120)',
  
  // Revenant 魂武者
  'Revenant': 'rgb(141,194,244)',
  'Herald': 'rgb(121,174,224)',
  'Renegade': 'rgb(161,214,255)',
  'Vindicator': 'rgb(129,182,228)',
  'Conduit': 'rgb(130,190,230)'
};

// 职业图标路径映射 - 使用本地资源（相对路径，需通过 getProfessionIconUrl 函数获取正确URL）
const PROFESSION_ICON_PATHS: Record<string, string> = {
  // Guardian 守护者
  'Guardian': '守护者.png',
  'Dragonhunter': '猎龙者.png',
  'Firebrand': '燃火者.png',
  'Willbender': '破锋者.png',
  'Luminary': '圣辉者.png',
  
  // Warrior 战士
  'Warrior': '战士.png',
  'Berserker': '狂战士.png',
  'Spellbreaker': '破法者.png',
  'Bladesworn': '誓剑士.png',
  'Paragon': '圣言者.png',
  
  // Engineer 工程师
  'Engineer': '工程师.png',
  'Scrapper': '机械师.png',
  'Holosmith': '全息师.png',
  'Mechanist': '玉偃师.png',
  'Amalgam': '流金师.png',
  
  // Ranger 游侠
  'Ranger': '游侠.png',
  'Druid': '德鲁伊.png',
  'Soulbeast': '魂兽师.png',
  'Untamed': '狂兽师.png',
  'Galeshot': '风羽者.png',
  
  // Thief 潜行者
  'Thief': '潜行者.png',
  'Daredevil': '独行侠.png',
  'Deadeye': '神枪手.png',
  'Specter': '缚影者.png',
  'Antiquary': '彩戏师.png',
  
  // Elementalist 元素使
  'Elementalist': '元素师.png',
  'Tempest': '暴风使.png',
  'Weaver': '编织者.png',
  'Catalyst': '元晶师.png',
  'Evoker': '唤元师.png',
  
  // Mesmer 幻术师
  'Mesmer': '幻术师.png',
  'Chronomancer': '时空术士.png',
  'Mirage': '幻象术士.png',
  'Virtuoso': '灵刃术士.png',
  'Troubadour': '吟游诗人.png',
  
  // Necromancer 死灵法师
  'Necromancer': '唤灵师.png',
  'Reaper': '夺魂者.png',
  'Scourge': '灾厄师.png',
  'Harbinger': '先驱者.png',
  'Ritualist': '祭祀者.png',
  
  // Revenant 魂武者
  'Revenant': '魂武者.png',
  'Herald': '预告者.png',
  'Renegade': '龙魂使.png',
  'Vindicator': '裁决者.png',
  'Conduit': '契灵使.png'
};

/**
 * 获取职业图标URL - Vite环境下正确处理静态资源路径
 * @param prof 职业英文名称
 * @returns 图标资源的完整URL
 */
export function getProfessionIconUrl(prof: string): string {
  const fileName = PROFESSION_ICON_PATHS[prof];
  if (!fileName) {
    console.warn(`职业图标未找到: ${prof}`);
    return '';
  }
  try {
    return new URL(`/src/assets/images/prof/${fileName}`, import.meta.url).href;
  } catch (error) {
    console.error(`加载职业图标失败: ${prof}`, error);
    return '';
  }
}

// 保持向后兼容性 - 旧版 PROFESSION_ICONS 对象（已废弃，建议使用 getProfessionIconUrl 函数）
export const PROFESSION_ICONS = PROFESSION_ICON_PATHS;

/**
 * 验证伤害值是否在合理范围内
 * @param value 原始伤害值
 * @returns 修正后的合理伤害值
 */
export function validateDamageValue(value: number): number {
  // GW2中WVW单场战斗伤害上限合理值约为10亿（1,000,000,000）
  const MAX_REASONABLE_DAMAGE = 1000000000;
  const MIN_REASONABLE_DAMAGE = 0;
  
  if (isNaN(value) || value < MIN_REASONABLE_DAMAGE) {
    return 0;
  }
  
  if (value > MAX_REASONABLE_DAMAGE) {
    console.warn(`[validateDamageValue] 检测到异常伤害值: ${value}，已修正为最大值`);
    return MAX_REASONABLE_DAMAGE;
  }
  
  return value;
}

/**
 * 格式化伤害数字显示
 * @param value 伤害值
 * @param validate 是否验证数值合理性（默认true）
 */
export function formatDamage(value: number, validate: boolean = true): string {
  const validatedValue = validate ? validateDamageValue(value) : value;
  
  if (validatedValue >= 1000000000) {
    return (validatedValue / 1000000000).toFixed(1) + 'b';
  }
  if (validatedValue >= 1000000) {
    return (validatedValue / 1000000).toFixed(1) + 'm';
  }
  if (validatedValue >= 1000) {
    return (validatedValue / 1000).toFixed(1) + 'k';
  }
  return validatedValue.toString();
}

/**
 * 团队评分系统规则说明
 * 
 * 评分指标及权重分配：
 * 
 * 1. DPS评分（占比约50%）
 *    - 计算公式：Math.floor(dps / 10)
 *    - 说明：基于每秒伤害值，反映输出能力
 * 
 * 2. 击杀评分（占比约30%）
 *    - 计算公式：kills * 100
 *    - 说明：每击杀一个敌人获得100分
 * 
 * 3. 破甲评分（占比约20%）
 *    - 计算公式：Math.floor(breakbar_damage / 100)
 *    - 说明：基于破坏条伤害，反映控制能力
 * 
 * 4. 死亡惩罚
 *    - 计算公式：deaths * 50
 *    - 说明：每死亡一次扣除50分
 * 
 * 综合评分 = DPS评分 + 击杀评分 + 破甲评分 - 死亡惩罚
 * 
 * 评分等级划分：
 * - S级：1000分以上（优秀）
 * - A级：700-999分（良好）
 * - B级：400-699分（中等）
 * - C级：200-399分（较差）
 * - D级：200分以下（需改进）
 */
export interface ScoreLevel {
  level: string;
  minScore: number;
  maxScore: number;
  description: string;
}

export const SCORE_LEVELS: ScoreLevel[] = [
  { level: 'S', minScore: 1000, maxScore: Infinity, description: '优秀' },
  { level: 'A', minScore: 700, maxScore: 999, description: '良好' },
  { level: 'B', minScore: 400, maxScore: 699, description: '中等' },
  { level: 'C', minScore: 200, maxScore: 399, description: '较差' },
  { level: 'D', minScore: 0, maxScore: 199, description: '需改进' },
];

/**
 * 根据评分获取等级
 * @param score 玩家评分
 * @returns 评分等级信息
 */
export function getScoreLevel(score: number): ScoreLevel {
  return SCORE_LEVELS.find(l => score >= l.minScore && score <= l.maxScore) || SCORE_LEVELS[4];
}

/**
 * 格式化时长显示 (毫秒转为分:秒)
 */
export function formatDuration(ms: number): string {
  const totalSeconds = Math.floor(ms / 1000);
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  return `${minutes}:${seconds.toString().padStart(2, '0')}`;
}

/**
 * 格式化百分比显示
 */
export function formatPercent(value: number, decimals = 1): string {
  return (value * 100).toFixed(decimals) + '%';
}
