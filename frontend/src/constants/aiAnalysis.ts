/**
 * AI 分析模块 UI 文本常量
 * 包含页面标题、标签页、按钮文本、提示信息、通知文案等
 * 后续统一迁移到 vue-i18n 国际化体系
 */

// ==================== 页面级标题 ====================
export const PAGE_TITLE = 'AI 战斗分析中心'
export const PAGE_SUBTITLE = '智能分析战斗数据，发现隐藏的优化机会'

// ==================== 通用按钮 ====================
export const BTN_REFRESH = '刷新数据'
export const BTN_REFRESHING = '刷新中...'
export const BTN_CONFIG_MANAGE = '配置管理'
export const BTN_ANALYZING = '分析中...'
export const BTN_VERIFYING = '验证中...'
export const BTN_GENERATE = '生成档案'

// ==================== 分析类型标签页 ====================
export const TAB_OVERVIEW = '概览'
export const TAB_GROWTH = '成长档案'
export const TAB_DEATH = '死亡归因'
export const TAB_SQUAD = '小队协同'
export const TAB_BUILD = 'Build验证'
export const TAB_MOMENTS = '关键片段'

export const ANALYSIS_TABS = [
  { key: 'overview', label: TAB_OVERVIEW, icon: 'layout-dashboard' },
  { key: 'growth', label: TAB_GROWTH, icon: 'trending-up' },
  { key: 'death', label: TAB_DEATH, icon: 'shield-alert' },
  { key: 'squad', label: TAB_SQUAD, icon: 'users' },
  { key: 'build', label: TAB_BUILD, icon: 'check-circle' },
  { key: 'moments', label: TAB_MOMENTS, icon: 'clock' },
] as const

// ==================== 下拉选择标签与占位符 ====================
export const LABEL_SELECT_PLAYER = '选择玩家'
export const LABEL_SELECT_FIGHT = '选择战斗'
export const LABEL_HISTORY_FIGHTS = '历史场次'
export const PLACEHOLDER_SELECT_PLAYER = '请选择玩家'
export const PLACEHOLDER_SELECT_FIGHT = '请选择战斗'

// ==================== 历史场次选项 ====================
export const OPTION_RECENT_10 = '最近10场'
export const OPTION_RECENT_30 = '最近30场'
export const OPTION_RECENT_50 = '最近50场'

export const HISTORY_OPTIONS = [
  { value: 10, label: OPTION_RECENT_10 },
  { value: 30, label: OPTION_RECENT_30 },
  { value: 50, label: OPTION_RECENT_50 },
] as const

// ==================== 各页操作按钮 ====================
export const BTN_DEATH_ANALYSIS = '死亡归因分析'
export const BTN_SQUAD_SYNERGY = '小队协同诊断'
export const BTN_BUILD_VERIFY = 'Build执行验证'
export const BTN_CRITICAL_MOMENTS = '关键片段复盘'

// ==================== 小队协同页标签 ====================
export const LABEL_SQUAD_PREFIX = '小队'
export const LABEL_SQUAD_MEMBERS_SUFFIX = '人 · 角色:'

// ==================== 空状态/提示文本 ====================
export const TIP_SELECT_FIGHT_AND_ANALYZE = '选择战斗并点击分析'
export const TIP_SELECT_PLAYER_AND_VERIFY = '选择玩家并点击验证'
export const TIP_SELECT_FIGHT_AND_REVIEW = '选择战斗并点击分析'

// ==================== Build 验证页标签 ====================
export const LABEL_BUILD_TYPE = 'Build类型'
export const LABEL_EXECUTION_SCORE = '执行评分'
export const LABEL_ACTUAL_PREFIX = '实际:'

// ==================== 通知标题 ====================
export const NOTIFY_TITLE_SUCCESS = '操作成功'
export const NOTIFY_TITLE_WARNING = '提示'
export const NOTIFY_TITLE_ERROR = '操作失败'
export const NOTIFY_TITLE_TEST_SUCCESS = '测试成功'
export const NOTIFY_TITLE_TEST_FAIL = '测试失败'
export const NOTIFY_TITLE_ANALYZE_COMPLETE = '分析完成'

// ==================== 通知消息 ====================
export const NOTIFY_MSG_REFRESH_COMPLETE = '数据刷新完成'
export const NOTIFY_MSG_TEST_SUCCESS = '连接测试成功！AI服务正常运行'
export const NOTIFY_MSG_TEST_FAIL = '连接测试失败，请检查配置'
export const NOTIFY_MSG_TEST_FAIL_SHORT = '连接测试失败'
export const NOTIFY_MSG_NO_FIGHT_DATA = '暂无最近战斗数据'
export const NOTIFY_MSG_FIGHT_ANALYZE_COMPLETE = '战斗分析完成！报告已生成'
export const NOTIFY_MSG_ANALYZE_FAIL = '分析失败'
export const NOTIFY_MSG_PLAYER_ANALYZE_DEV = '玩家分析功能开发中'
export const NOTIFY_MSG_TEAM_ANALYZE_DEV = '团队分析功能开发中'
export const NOTIFY_MSG_PERSONAL_GROWTH_COMPLETE = '个人成长档案生成完成'
export const NOTIFY_MSG_DEATH_ANALYSIS_COMPLETE = '死亡归因分析完成'
export const NOTIFY_MSG_SQUAD_SYNERGY_COMPLETE = '小队协同诊断完成'
export const NOTIFY_MSG_BUILD_VERIFY_COMPLETE = 'Build执行验证完成'
export const NOTIFY_MSG_CRITICAL_MOMENTS_COMPLETE = '关键片段复盘完成'
export const NOTIFY_MSG_VERIFY_FAIL = '验证失败'
export const NOTIFY_MSG_GET_REPORT_FAIL = '获取报告详情失败'
export const NOTIFY_MSG_DELETE_SUCCESS = '报告删除成功'
export const NOTIFY_MSG_DELETE_FAIL = '删除失败'
export const NOTIFY_MSG_CONFIG_UPDATED = '配置已更新'

// ==================== 控制台错误日志 ====================
export const LOG_REFRESH_FAIL = '刷新数据失败:'
export const LOG_LOAD_FIGHTS_FAIL = '加载最近战斗失败:'
export const LOG_LOAD_PLAYERS_FAIL = '加载最近玩家失败:'

// ==================== AiAnalysisTools.vue 专用常量 ====================
export const TOOLS_CONFIG_REQUIRED = '请先在配置管理中完成AI配置'
export const TOOLS_CONFIG_HINT = '配置完成后即可使用智能分析功能'
export const TOOLS_SMART_RECOMMEND = 'AI智能推荐'
export const TOOLS_SMART_RECOMMEND_HINT = '系统会根据您的战斗数据自动推荐分析选项'

export const TOOLS_SECTION_ANALYZE_FIGHT = '分析战斗'
export const TOOLS_SECTION_ANALYZE_PLAYER = '分析玩家'
export const TOOLS_SECTION_ANALYZE_BUILD = '分析Build'

export const TOOLS_BTN_AUTO_SELECT_LATEST = '自动选择最新'
export const TOOLS_BTN_AUTO_SELECT = '自动选择'
export const TOOLS_BTN_START_ANALYZE = '开始分析'
export const TOOLS_BTN_ANALYZING = '分析中...'
export const TOOLS_BTN_ONE_CLICK_ANALYZE = '一键全面分析'
export const TOOLS_BTN_FULL_ANALYZING = '全面分析中...'

export const TOOLS_LABEL_SELECT_FIGHT = '选择战斗'
export const TOOLS_LABEL_PLAYER_NAME_ID = '玩家名称或ID'
export const TOOLS_LABEL_BUILD_CODE_ID = 'Build代码或ID'

export const TOOLS_PLACEHOLDER_SELECT_FIGHT = '选择战斗日志...'
export const TOOLS_PLACEHOLDER_PLAYER_INPUT = '输入玩家名称或ID'
export const TOOLS_PLACEHOLDER_BUILD_INPUT = '输入Build代码或ID'

export const TOOLS_SUPPORT_NAME_OR_ID = '支持名称或ID'
export const TOOLS_MATCH_RESULT_PREFIX = '找到'
export const TOOLS_MATCH_RESULT_SUFFIX = '个匹配结果'

export const TOOLS_SMART_MODE = '智能分析模式'
export const TOOLS_SMART_MODE_ON = '已开启：AI将自动关联战斗数据，提供智能推荐和自动化分析'
export const TOOLS_SMART_MODE_OFF = '已关闭：手动选择分析目标'

export const TOOLS_AI_ANALYZE_HINT = 'AI分析将自动识别战斗中的关键数据，提供个性化优化建议'
export const TOOLS_ANALYZE_RESULT_HINT = '分析结果包括：伤害输出、技能循环、团队配合、Build优化等'

export const TOOLS_ERROR_SELECT_FIGHT = '请先选择战斗日志'
export const TOOLS_ERROR_ENTER_PLAYER = '请输入玩家名称或ID'
export const TOOLS_ERROR_ENTER_BUILD = '请输入Build代码或ID'

export const SMART_SUGGESTION_TITLE = '智能分析建议'
export const SMART_SUGGESTION_COMBO_MSG = '检测到您已选择战斗和玩家，建议一起分析该玩家在这场战斗中的表现'
export const SMART_SUGGESTION_COMBO_ACTION = '立即分析组合'
export const SMART_SUGGESTION_FIGHT_MSG = '系统推荐分析这场战斗中表现最佳的玩家，以获取详细的技能循环分析'
export const SMART_SUGGESTION_FIGHT_ACTION = '分析最佳玩家'
export const SMART_SUGGESTION_PLAYER_MSG = '建议为该玩家选择一场战斗进行深入分析'
export const SMART_SUGGESTION_PLAYER_ACTION = '选择战斗'
