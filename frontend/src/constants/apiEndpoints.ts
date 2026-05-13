/**
 * API端点配置
 * 功能：定义所有API路由路径常量，统一入口管理
 * 约束：所有路径均已包含 /api/v1 前缀（除特殊路径外）
 * 更新日期：2026-05-04
 */

const API_V1 = '/api/v1';

export const API_ENDPOINTS = {
  // 认证相关
  AUTH: {
    LOGIN: `${API_V1}/auth/login`,
    LOGOUT: `${API_V1}/auth/logout`,
    REFRESH: `${API_V1}/auth/refresh`,
    PROFILE: `${API_V1}/auth/profile`,
    CHANGE_PASSWORD: `${API_V1}/auth/change-password`,
    STATUS: `${API_V1}/auth/status`
  },

  // 日志管理
  LOGS: {
    BASE: `${API_V1}/logs`,
    LIST: `${API_V1}/logs`,
    DETAIL: (id: string | number) => `${API_V1}/logs/${id}`,
    UPLOAD: `${API_V1}/logs/upload`,
    DELETE: (id: string | number) => `${API_V1}/logs/${id}`,
    UPDATE: (id: string | number) => `${API_V1}/logs/${id}`,
    PARSE: (id: string | number) => `${API_V1}/logs/${id}/parse`,
    PARSE_PROGRESS: (id: string | number) => `${API_V1}/logs/${id}/parse/progress`,
    PARSE_RESULT: (id: string | number) => `${API_V1}/logs/${id}/parse/result`,
    DOWNLOAD: (id: string | number) => `${API_V1}/logs/${id}/download`,
    BATCH_DELETE: `${API_V1}/logs/batch-delete`,
    BATCH_PARSE: `${API_V1}/logs/batch-parse`,
    FIGHT_INFO: (id: string | number) => `${API_V1}/logs/${id}/fight`,
    PLAYERS_STATS: (id: string | number) => `${API_V1}/logs/${id}/players`,
    PLAYER_STATS: (logId: string | number, accountName: string) => `${API_V1}/logs/${logId}/players/${accountName}/stats`,
    PLAYER_BUFFS: (logId: string | number, accountName: string) => `${API_V1}/logs/${logId}/players/${accountName}/buffs`,
    PLAYER_ROTATION: (logId: string | number, accountName: string) => `${API_V1}/logs/${logId}/players/${accountName}/rotation`,
    RAW_DATA: (id: string | number) => `${API_V1}/logs/${id}/raw`,
    VALIDATE: (id: string | number) => `${API_V1}/logs/${id}/validate`
  },

  // 出勤统计
  ATTENDANCE: {
    BASE: `${API_V1}/attendance`,
    LIST: `${API_V1}/attendance`,
    DETAIL: (id: string | number) => `${API_V1}/attendance/${id}`,
    EXPORT: `${API_V1}/attendance/export`,
    STATS: `${API_V1}/attendance/stats`,
    // v2.0 新接口：账号维度出勤管理
    ACCOUNTS: `${API_V1}/attendance/accounts`,
    ACCOUNT_DETAIL: (account: string) => `${API_V1}/attendance/accounts/${encodeURIComponent(account)}`,
    ACCOUNT_SCORE_BREAKDOWN: (account: string) => `${API_V1}/attendance/accounts/${encodeURIComponent(account)}/score-breakdown`,
    CHARACTER_DETAIL: (account: string, character: string) => `${API_V1}/attendance/accounts/${encodeURIComponent(account)}/characters/${encodeURIComponent(character)}`,
    FILTERS: `${API_V1}/attendance/filters`
  },

  // 技能循环
  SKILL_ROTATION: {
    BASE: `${API_V1}/skill-rotation`,
    HEALTH: `${API_V1}/skill-rotation/health`,
    ANALYZE: `${API_V1}/skill-rotation/analyze`,
    COMPARE: `${API_V1}/skill-rotation/compare`,
    COMPARE_PLAYER: (memberAccount: string) => `${API_V1}/skill-rotation/compare/${memberAccount}`,
    HISTORY: `${API_V1}/skill-rotation/history`,
    PLAYER: (memberAccount: string) => `${API_V1}/skill-rotation/player/${memberAccount}`,
    ERRORS: `${API_V1}/skill-rotation/errors`,
    EXPORT_REPORT: `${API_V1}/skill-rotation/export-report`,
    IDEAL_ROTATIONS: `${API_V1}/skill-rotation/ideal-rotations`
  },

  // Build解析（保留 /api/bdcode 特殊前缀）
  BUILD: {
    // bdcode 特殊前缀
    BDCODE_BASE: '/api/bdcode',
    PARSE: '/api/bdcode/parse',
    PARSE_BY_URL: (code: string) => `/api/bdcode/parse/${code}`,
    VALIDATE: '/api/bdcode/validate',
    BATCH: '/api/bdcode/batch',
    STATS: '/api/bdcode/stats',
    HEALTH: '/api/bdcode/health',
    // builds 前缀
    BASE: `${API_V1}/builds`,
    LIST: `${API_V1}/builds`,
    SAVE: `${API_V1}/builds/save`,
    DETAIL: (id: string | number) => `${API_V1}/builds/${id}`,
    DELETE: (id: string | number) => `${API_V1}/builds/${id}`,
    COMPARE: `${API_V1}/builds/compare`,
    EXPORT: (id: string | number) => `${API_V1}/builds/${id}/export`
  },

  // 数据看板
  DASHBOARD: {
    BASE: `${API_V1}/dashboard`,
    OVERVIEW: `${API_V1}/dashboard/overview`,
    RECENT: `${API_V1}/dashboard/recent`,
    STATS: `${API_V1}/dashboard/stats`,
    TRENDS: `${API_V1}/dashboard/trends`,
    MAPS: `${API_V1}/dashboard/maps`,
    PROFESSION_DISTRIBUTION: `${API_V1}/dashboard/profession-distribution`
  },

  // 用户管理
  USERS: {
    BASE: `${API_V1}/users`,
    LIST: `${API_V1}/users`,
    DETAIL: (id: string | number) => `${API_V1}/users/${id}`,
    CREATE: `${API_V1}/users`,
    UPDATE: (id: string | number) => `${API_V1}/users/${id}`,
    DELETE: (id: string | number) => `${API_V1}/users/${id}`,
    PROFILE: `${API_V1}/users/profile`,
    CHANGE_PASSWORD: `${API_V1}/users/change-password`,
    RESET_PASSWORD: (id: string | number) => `${API_V1}/users/${id}/reset-password`,
    TOGGLE_ACTIVE: (id: string | number) => `${API_V1}/users/${id}/toggle-active`,
    ROLES_LIST: `${API_V1}/users/roles/list`
  },

  // 系统设置
  SETTINGS: {
    BASE: `${API_V1}/settings`,
    GET: `${API_V1}/settings`,
    UPDATE: `${API_V1}/settings`,
    RESET: `${API_V1}/settings/reset`
  },

  // 技能分析
  SKILLS: {
    BASE: `${API_V1}/skills`,
    LIST: `${API_V1}/skills`,
    DETAIL: (id: string | number) => `${API_V1}/skills/${id}`,
    FIGHT_EVENTS: (fightId: string | number) => `${API_V1}/skills/${fightId}/events`,
    MEMBER_ROTATION: (memberId: string | number) => `${API_V1}/skills/${memberId}/rotation`
  },

  // AI分析
  AI: {
    BASE: `${API_V1}/ai`,
    REPORTS: `${API_V1}/ai/reports`,
    REPORT_DETAIL: (id: string | number) => `${API_V1}/ai/reports/${id}`,
    ANALYZE_FIGHT: (fightId: string | number) => `${API_V1}/ai/analyze/fight/${fightId}`,
    ANALYZE_MEMBER: (memberId: string | number) => `${API_V1}/ai/analyze/member/${memberId}`,
    ANALYZE_BUILD: (buildId: string | number) => `${API_V1}/ai/analyze/build/${buildId}`,
    TREND: `${API_V1}/ai/trend`,
    SUGGESTIONS: `${API_V1}/ai/suggestions`
  },

  // 战斗数据
  FIGHTS: {
    BASE: `${API_V1}/fights`,
    LIST: `${API_V1}/fights`,
    DETAIL: (id: string | number) => `${API_V1}/fights/${id}`,
    STATS: (id: string | number) => `${API_V1}/fights/${id}/stats`
  },

  // 字典管理
  DICTIONARY: {
    OPTIONS: (dictType: string) => `${API_V1}/dictionary/options/${dictType}`,
    DATA: `${API_V1}/dictionary/data`,
    DATA_DETAIL: (dictCode: string | number) => `${API_V1}/dictionary/data/${dictCode}`,
    TYPES: `${API_V1}/dictionary/types`,
    TYPE_DETAIL: (dictId: string | number) => `${API_V1}/dictionary/types/${dictId}`,
    TYPES_ALL: `${API_V1}/dictionary/types/all`,
    RELOAD_CACHE: `${API_V1}/dictionary/reload-cache`,
    INIT: `${API_V1}/dictionary/init`,
    PROFESSION_SPECS_CASCADE: `${API_V1}/dictionary/cascade/profession-specs`,
  },

  // 成员管理
  MEMBERS: {
    LIST: `${API_V1}/members`,
    RANKING: `${API_V1}/members/ranking`,
    PROFESSIONS: `${API_V1}/members/professions`,
    DETAIL: (id: string | number) => `${API_V1}/members/${id}`,
    STATS: (id: string | number) => `${API_V1}/members/${id}/stats`
  },

  // 监控
  MONITORING: {
    PERFORMANCE: `${API_V1}/monitoring/performance`,
    PERFORMANCE_SUMMARY: `${API_V1}/monitoring/performance/summary`,
    PERFORMANCE_RESET: `${API_V1}/monitoring/performance/reset`,
    BENCHMARK: `${API_V1}/monitoring/benchmark`,
    BENCHMARK_COMPARE: `${API_V1}/monitoring/benchmark/compare`
  },

  // 游戏数据
  GAME_DATA: {
    INFO: `${API_V1}/game-data/info`,
    RELOAD: `${API_V1}/game-data/reload`,
    PROFESSIONS: `${API_V1}/game-data/professions`,
    PROFESSION_DETAIL: (name: string) => `${API_V1}/game-data/professions/${name}`,
    PROFESSION_NAME_CN: (name: string) => `${API_V1}/game-data/professions/${name}/name-cn`,
    PROFESSION_DEFAULT_ROLE: (name: string) => `${API_V1}/game-data/professions/${name}/default-role`,
    PROFESSION_SCORING_CONFIG: (name: string) => `${API_V1}/game-data/professions/${name}/scoring-config`,
    ELITE_SPECS: `${API_V1}/game-data/elite-specs`,
    ELITE_SPEC_DETAIL: (name: string) => `${API_V1}/game-data/elite-specs/${name}`,
    BUFFS: `${API_V1}/game-data/buffs`,
    BUFF_DETAIL: (id: string | number) => `${API_V1}/game-data/buffs/${id}`,
    BUFF_NAME_CN: (id: string | number) => `${API_V1}/game-data/buffs/${id}/name-cn`,
    BUFF_CATEGORIES: `${API_V1}/game-data/categories/buffs`
  },



  // 评分规则管理
  SCORING_RULES: {
    BASE: `${API_V1}/scoring-rules`,
    ROLES: `${API_V1}/scoring-rules/roles`,
    RULES: `${API_V1}/scoring-rules/rules`,
    RULE_DETAIL: (id: string | number) => `${API_V1}/scoring-rules/rules/${id}`,
    RULE_UPDATE: (id: string | number) => `${API_V1}/scoring-rules/rules/${id}`,
    RULE_DELETE: (id: string | number) => `${API_V1}/scoring-rules/rules/${id}`,
    BATCH: `${API_V1}/scoring-rules/rules/batch`,
    RESET: `${API_V1}/scoring-rules/rules/reset`,
    DIMENSIONS: `${API_V1}/scoring-rules/dimensions`,
    // v3.0 新增：职业特定规则
    PROFESSION_RULES: (profession: string) => `${API_V1}/scoring-rules/rules/profession/${encodeURIComponent(profession)}`,
    PROFESSIONS: `${API_V1}/scoring-rules/professions`,
    // v3.0 新增：版本管理
    VERSIONS: `${API_V1}/scoring-rules/versions`,
    VERSION_DETAIL: (id: string | number) => `${API_V1}/scoring-rules/versions/${id}`,
    VERSION_BUMP: `${API_V1}/scoring-rules/versions/bump`,
  },

  // 评分系统（实时计算 + 重算任务）
  SCORING: {
    RULES: `${API_V1}/scoring/rules`,
    FIGHT: (id: string | number) => `${API_V1}/scoring/fight/${id}`,
    RECALCULATE: `${API_V1}/scoring/recalculate`,
    RECALCULATE_STATUS: (versionId: string | number) => `${API_V1}/scoring/recalculate/${versionId}`,
  },

  // 角色管理
  ROLES: {
    RULES: `${API_V1}/roles/rules`,
    RULES_BY_PROFESSION: (professionId: string) => `${API_V1}/roles/rules/profession/${professionId}`,
    RULE_DETAIL: (ruleId: string | number) => `${API_V1}/roles/rules/${ruleId}`,
    RULE_UPDATE: (ruleId: string | number) => `${API_V1}/roles/rules/${ruleId}`,
    RULE_DELETE: (ruleId: string | number) => `${API_V1}/roles/rules/${ruleId}`,
    TEMPLATES: `${API_V1}/roles/templates`,
    TEMPLATE_CREATE: `${API_V1}/roles/templates`,
    TEMPLATE_DETAIL: (templateId: string | number) => `${API_V1}/roles/templates/${templateId}`,
    TEMPLATE_UPDATE: (templateId: string | number) => `${API_V1}/roles/templates/${templateId}`,
    TEMPLATE_DELETE: (templateId: string | number) => `${API_V1}/roles/templates/${templateId}`,
    TEMPLATE_BY_NAME: (templateName: string) => `${API_V1}/roles/templates/name/${templateName}`,
    TEMPLATE_APPLY: (templateId: string | number) => `${API_V1}/roles/templates/${templateId}/apply`,
    TEMPLATE_INIT_PRESETS: `${API_V1}/roles/templates/init-presets`,
    EXPORT: `${API_V1}/roles/export`,
    IMPORT: `${API_V1}/roles/import`,
    EXPRESSIONS: `${API_V1}/roles/expressions`,
    EXPRESSION_CREATE: `${API_V1}/roles/expressions`,
    ASSIGN: `${API_V1}/roles/assign`,
    QUERY: `${API_V1}/roles/query`
  },

  // EI 分析
  EI: {
    ANALYSIS_SUMMARY: (logId: string | number) => `${API_V1}/ei-analysis/${logId}`,
    ANALYSIS_PLAYER_DETAIL: (logId: string | number, account: string) => `${API_V1}/ei-analysis/${logId}/player/${account}`,
    ANALYSIS_PLAYER_ROTATION: (logId: string | number, account: string) => `${API_V1}/ei-analysis/${logId}/player/${account}/rotation`,
    UNIFIED: (logId: string | number) => `${API_V1}/ei-report/logs/${logId}/unified`
  },

  // WvW 战斗报告
  WVW_REPORT: {
    LOGS: `${API_V1}/wvw-report/logs`,
    SUMMARY: (logId: string | number) => `${API_V1}/wvw-report/${logId}/summary`,
    PLAYERS: (logId: string | number) => `${API_V1}/wvw-report/${logId}/players`,
    PLAYER_DETAIL: (logId: string | number, playerId: string | number) => `${API_V1}/wvw-report/${logId}/players/${playerId}`,
    TARGETS: (logId: string | number) => `${API_V1}/wvw-report/${logId}/targets`,
    PHASES: (logId: string | number) => `${API_V1}/wvw-report/${logId}/phases`,
    TIMELINE: (logId: string | number) => `${API_V1}/wvw-report/${logId}/timeline`,
    SKILL_MAP: (logId: string | number) => `${API_V1}/wvw-report/${logId}/skill-map`,
  },

  // 通知中心
  NOTICES: {
    UNREAD_COUNT: `${API_V1}/notices/unread-count`,
    LIST: `${API_V1}/notices`,
    MARK_READ: (id: string | number) => `${API_V1}/notices/${id}/read`,
    MARK_ALL_READ: `${API_V1}/notices/read-all`,
  },

  // 战斗分析
  COMBAT_ANALYSIS: {
    FIGHT_BASIC: (logId: string | number) => `${API_V1}/combat-analysis/logs/${logId}/fight`,
    PLAYERS_LIST: (logId: string | number) => `${API_V1}/combat-analysis/logs/${logId}/players`,
    PLAYER_STATS: (logId: string | number) => `${API_V1}/combat-analysis/logs/${logId}/players/stats`,
    PLAYER_BUFFS: (logId: string | number) => `${API_V1}/combat-analysis/logs/${logId}/players/buffs`,
    PLAYER_ROTATION: (logId: string | number) => `${API_V1}/combat-analysis/logs/${logId}/players/rotation`,
    RAW_DATA: (logId: string | number) => `${API_V1}/combat-analysis/logs/${logId}/raw`,
    PLAYER_DETAIL_LEGACY: (logId: string | number, accountName: string) => `${API_V1}/combat-analysis/logs/${logId}/players/${encodeURIComponent(accountName)}`,
    PLAYER_BUFFS_LEGACY: (logId: string | number, accountName: string) => `${API_V1}/combat-analysis/logs/${logId}/players/${encodeURIComponent(accountName)}/buffs`,
    PLAYER_ROTATION_LEGACY: (logId: string | number, accountName: string) => `${API_V1}/combat-analysis/logs/${logId}/players/${encodeURIComponent(accountName)}/rotation`,
    LEADERBOARD: (logId: string | number) => `${API_V1}/combat-analysis/leaderboard/${logId}`,
    TEAM_BUFFS: (logId: string | number) => `${API_V1}/combat-analysis/team-buffs/${logId}`,
    FIGHT_DETAILS: (logId: string | number) => `${API_V1}/combat-analysis/logs/${logId}/fight/details`,
    FIGHT_METRICS: (logId: string | number) => `${API_V1}/combat-analysis/fight-metrics/${logId}`
  }
} as const;

export type ApiEndpointKey = typeof API_ENDPOINTS;
