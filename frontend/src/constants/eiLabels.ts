/**
 * Elite Insights 详情页面 UI 文本常量
 * 包含统计标签、表格列头、板块标题、选项文本等
 * 后续统一迁移到 vue-i18n 国际化体系
 */

// ==================== HealingExtension.vue ====================
export const HEALING_SECTION_TITLE = '治疗统计'
export const HEALING_SECTION_SUBTITLE = '显示团队治疗数据和屏障统计'

export const LABEL_TOTAL_HEALING = '总治疗量'
export const LABEL_TOTAL_BARRIER = '总屏障量'
export const LABEL_AVG_HPS = '平均HPS'
export const LABEL_OVERHEAL = '过量治疗'

export const DISTRIBUTION_CHART_TITLE = '治疗与屏障分布'

export const TAB_HEALING_ONLY = '仅治疗'
export const TAB_BARRIER_ONLY = '仅屏障'
export const TAB_COMBINED = '综合'

export const DISTRIBUTION_TABS = [
  { key: 'healing', label: TAB_HEALING_ONLY },
  { key: 'barrier', label: TAB_BARRIER_ONLY },
  { key: 'combined', label: TAB_COMBINED },
] as const

export const HEALING_SKILLS_TITLE = '治疗技能统计'
export const LABEL_HEALING_AMOUNT = '治疗量'
export const LABEL_OVERHEAL_PERCENT = '过量%'
export const LABEL_TARGETS = '目标数'
export const LABEL_TIMES_SUFFIX = '次'

export const PLAYER_HEALING_DETAIL_TITLE = '玩家治疗详情'

export const SORT_OPTION_HEALING = '治疗量'
export const SORT_OPTION_BARRIER = '屏障量'
export const SORT_OPTION_HPS = 'HPS'
export const SORT_OPTION_OVERHEAL = '过量治疗'

export const TABLE_HEADER_RANK = '#'
export const TABLE_HEADER_PLAYER = '玩家'
export const TABLE_HEADER_PROFESSION = '职业'
export const TABLE_HEADER_HEALING = '治疗量'
export const TABLE_HEADER_BARRIER = '屏障量'
export const TABLE_HEADER_HPS = 'HPS'
export const TABLE_HEADER_OVERHEAL_PERCENT = '过量%'
export const TABLE_HEADER_CRIT_PERCENT = '暴击%'
export const TABLE_HEADER_HEALING_SKILLS = '治疗技能'

// ==================== PlayerStatsDetail.vue ====================
export const LABEL_TOTAL_DAMAGE = '总伤害'
export const LABEL_DPS = 'DPS'
export const LABEL_SCORE = '评分'
export const LABEL_CLEANSE = '清症'

export const SECTION_BATTLE_DETAILS = '战斗数据详情'
export const LABEL_DIRECT_DAMAGE = '直伤'
export const LABEL_CONDITION_DAMAGE = '症状'
export const LABEL_CRIT_RATE = '暴击率'
export const LABEL_CRIT_DAMAGE = '暴击伤害'
export const LABEL_PRECISION = '精准'
export const LABEL_POWER = '威力'
export const LABEL_TOUGHNESS = '坚韧'
export const LABEL_VITALITY = '体力'

export const SECTION_BATTLE_STATUS = '战斗状态'
export const LABEL_DOWNS = '倒地'
export const LABEL_DEATHS = '死亡'
export const LABEL_CC = 'CC'
export const LABEL_CLEARS = '清除'

export const SECTION_WEAPON_CONFIG = '武器配置'
export const LABEL_WEAPONS_NOT_RECORDED = '未记录'

// ==================== StatsView.vue ====================
export const LABEL_AVG_DPS = '平均DPS'
export const LABEL_ALIVE_PLAYERS = '存活玩家'
export const LABEL_TEAM_SCORE = '团队评分'

// ==================== PlayerStatsTab.vue / 通用 ====================
export const LABEL_HPS = 'HPS'

// ==================== PlayerRotationTab.vue ====================
export const LABEL_LOADING_ROTATION = '正在加载循环数据...'
export const SECTION_ROTATION_SEQUENCE = '技能循环序列'
export const LABEL_WEAPON_SKILL = '武器技能'
export const LABEL_ROTATION_ACCURACY = '循环准确率'
export const LABEL_IDEAL_ROTATION_MATCH = '理想循环匹配'

export const ERROR_MISSING_LOG_ID = '缺少日志ID'
export const ERROR_LOAD_FAILED = '加载失败'
export const ERROR_MULTIPLE_SAME_NAME = '存在多个同名玩家'
export const ERROR_NETWORK_ERROR = '网络错误'

// ==================== BuffsView.vue ====================
export const SECTION_TEAM_BUFF_COVERAGE = '团队增益覆盖'
export const SECTION_BUFF_DETAIL_STATS = '增益详细统计'
export const LABEL_AVG_BOON = '平均增益'
export const LABEL_ACTIVE_BOON = '活跃增益'
export const LABEL_AVG_CONDITION = '平均症状'
export const LABEL_ACTIVE_CONDITION = '活跃症状'
export const LABEL_WEAPON_SWAP = '武器切换'
export const LABEL_BUFF_PREFIX = 'Buff'
