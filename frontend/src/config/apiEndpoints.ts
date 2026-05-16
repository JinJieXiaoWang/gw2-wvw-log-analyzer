/**
 * API端点配置
 * 功能：定义所有API路由路径常量，统一入口管理
 * 约束：所有路径均为相对路径（不含 /api/v1 前缀），前缀由 apiService.ts baseURL 控制
 * 更新日期：2026-05-15
 */


export const API_ENDPOINTS = {
  // 认证相关
  AUTH: {
    LOGIN: `auth/login`,
    LOGOUT: `auth/logout`,
    REFRESH: `auth/refresh`,
    PROFILE: `auth/profile`,
    CHANGE_PASSWORD: `auth/change-password`,
    STATUS: `auth/status`
  },

  // 日志管理
  LOGS: {
    BASE: `logs`,
    LIST: `logs`,
    DETAIL: (id: string | number) => `logs/${id}`,
    UPLOAD: `logs/upload`,
    DELETE: (id: string | number) => `logs/${id}`,
    UPDATE: (id: string | number) => `logs/${id}`,
    PARSE: (id: string | number) => `logs/${id}/parse`,
    PARSE_PROGRESS: (id: string | number) => `logs/${id}/parse/progress`,
    PARSE_RESULT: (id: string | number) => `logs/${id}/parse/result`,
    DOWNLOAD: (id: string | number) => `logs/${id}/download`,
    BATCH_DELETE: `logs/batch-delete`,
    BATCH_PARSE: `logs/batch-parse`,
    CHECK_SHA256: `logs/check-sha256`,
    FIGHT_INFO: (id: string | number) => `logs/${id}/fight`,
    PLAYERS_STATS: (id: string | number) => `logs/${id}/players`,
    PLAYER_STATS: (logId: string | number, accountName: string) => `logs/${logId}/players/${accountName}/stats`,
    PLAYER_BUFFS: (logId: string | number, accountName: string) => `logs/${logId}/players/${accountName}/buffs`,
    PLAYER_ROTATION: (logId: string | number, accountName: string) => `logs/${logId}/players/${accountName}/rotation`,
    RAW_DATA: (id: string | number) => `logs/${id}/raw`,
    VALIDATE: (id: string | number) => `logs/${id}/validate`
  },

  // 出勤统计
  ATTENDANCE: {
    BASE: `attendance`,
    LIST: `attendance`,
    DETAIL: (id: string | number) => `attendance/${id}`,
    EXPORT: `attendance/export`,
    STATS: `attendance/stats`,
    // v2.0 新接口：账号维度出勤管理
    ACCOUNTS: `attendance/accounts`,
    ACCOUNT_DETAIL: (account: string) => `attendance/accounts/${encodeURIComponent(account)}`,
    ACCOUNT_SCORE_BREAKDOWN: (account: string) => `attendance/accounts/${encodeURIComponent(account)}/score-breakdown`,
    ACCOUNT_EXPORT: (account: string) => `attendance/accounts/${encodeURIComponent(account)}/export`,
    CHARACTER_DETAIL: (account: string, character: string) => `attendance/accounts/${encodeURIComponent(account)}/characters/${encodeURIComponent(character)}`,
    FILTERS: `attendance/filters`
  },

  // 技能循环
  SKILL_ROTATION: {
    BASE: `skill-rotation`,
    HEALTH: `skill-rotation/health`,
    ANALYZE: `skill-rotation/analyze`,
    COMPARE: `skill-rotation/compare`,
    COMPARE_PLAYER: (memberAccount: string) => `skill-rotation/compare/${memberAccount}`,
    HISTORY: `skill-rotation/history`,
    PLAYER: (memberAccount: string) => `skill-rotation/player/${memberAccount}`,
    ERRORS: `skill-rotation/errors`,
    EXPORT_REPORT: `skill-rotation/export-report`,
    IDEAL_ROTATIONS: `skill-rotation/ideal-rotations`
  },

  // Build解析（保留 /api/bdcode 特殊前缀）
  BUILD: {
    // bdcode 特殊前缀
    BDCODE_BASE: `bdcode`,
    PARSE: `bdcode/parse`,
    PARSE_BY_URL: (code: string) => `bdcode/parse/${code}`,
    VALIDATE: `bdcode/validate`,
    BATCH: `bdcode/batch`,
    STATS: `bdcode/stats`,
    HEALTH: `bdcode/health`,  
    // builds 主接口
    BASE: `builds`,
    LIST: `builds`,
    SAVE: `builds/save`,
    DETAIL: (id: string | number) => `builds/${id}`,
    DELETE: (id: string | number) => `builds/${id}`,
    COMPARE: `builds/compare`,
    EXPORT: (id: string | number) => `builds/${id}/export`
  },

  // 数据看板
  DASHBOARD: {
    BASE: `dashboard`,
    OVERVIEW: `dashboard/overview`,
    RECENT: `dashboard/recent`,
    STATS: `dashboard/stats`,
    TRENDS: `dashboard/trends`,
    MAPS: `dashboard/map-stats`,
    PROFESSION_DISTRIBUTION: `dashboard/profession-distribution`,
    TOP_PLAYERS: `dashboard/top-players`,
    RECENT_FIGHTS: `dashboard/recent-fights`,
    PARSE_STATUS: `dashboard/parse-status`,
    AI_SCORE_DISTRIBUTION: `dashboard/ai-score-distribution`,
    BUFF_OVERVIEW: `dashboard/buff-overview`
  },

  // 用户管理
  USERS: {
    BASE: `users`,
    LIST: `users`,
    DETAIL: (id: string | number) => `users/${id}`,
    CREATE: `users`,
    UPDATE: (id: string | number) => `users/${id}`,
    DELETE: (id: string | number) => `users/${id}`,
    PROFILE: `users/profile`,
    CHANGE_PASSWORD: `users/change-password`,
    RESET_PASSWORD: (id: string | number) => `users/${id}/reset-password`,
    TOGGLE_ACTIVE: (id: string | number) => `users/${id}/toggle-active`,
    ROLES_LIST: `users/roles/list`
  },

  // 系统设置
  SETTINGS: {
    BASE: `settings`,
    GET: `settings`,
    UPDATE: `settings`,
    RESET: `settings/reset`
  },

  // 技能分析
  SKILLS: {
    BASE: `skills`,
    LIST: `skills`,
    DETAIL: (id: string | number) => `skills/${id}`,
    FIGHT_EVENTS: (fightId: string | number) => `skills/${fightId}/events`,
    MEMBER_ROTATION: (memberId: string | number) => `skills/${memberId}/rotation`
  },

  // AI分析
  AI: {
    BASE: `ai`,
    REPORTS: `ai/reports`,
    REPORT_DETAIL: (id: string | number) => `ai/reports/${id}`,
    ANALYZE_FIGHT: (fightId: string | number) => `ai/analyze/fight/${fightId}`,
    ANALYZE_MEMBER: (memberId: string | number) => `ai/analyze/member/${memberId}`,
    ANALYZE_BUILD: (buildId: string | number) => `ai/analyze/build/${buildId}`,
    TREND: `ai/trend`,
    SUGGESTIONS: `ai/suggestions`,
    STATUS: `ai/status`,
    TEST: `ai/test`,
    CLEAR_CACHE: `ai/cache/clear`,
    ANALYZE_PERSONAL_GROWTH: `ai/analyze/personal-growth`,
    ANALYZE_DEATH_ATTRIBUTION: `ai/analyze/death-attribution`,
    ANALYZE_SQUAD_SYNERGY: `ai/analyze/squad-synergy`,
    ANALYZE_BUILD_EXECUTION: `ai/analyze/build-execution`,
    ANALYZE_CRITICAL_MOMENTS: `ai/analyze/critical-moments`,
  },

  // 战斗数据
  FIGHTS: {
    BASE: `fights`,
    LIST: `fights`,
    DETAIL: (id: string | number) => `fights/${id}`,
    STATS: (id: string | number) => `fights/${id}/stats`
  },

  // 字典管理
  DICTIONARY: {
    OPTIONS: (dictType: string) => `dictionary/options/${dictType}`,
    DATA: `dictionary/data`,
    DATA_DETAIL: (dictCode: string | number) => `dictionary/data/${dictCode}`,
    TYPES: `dictionary/types`,
    TYPE_DETAIL: (dictId: string | number) => `dictionary/types/${dictId}`,
    TYPES_ALL: `dictionary/types/all`,
    RELOAD_CACHE: `dictionary/reload-cache`,
    INIT: `dictionary/init`,
    PROFESSION_SPECS_CASCADE: `dictionary/cascade/profession-specs`,
  },

  // 成员管理
  MEMBERS: {
    LIST: `members`,
    RANKING: `members/ranking`,
    PROFESSIONS: `members/professions`,
    DETAIL: (id: string | number) => `members/${id}`,
    STATS: (id: string | number) => `members/${id}/stats`
  },

  // 监控
  MONITORING: {
    PERFORMANCE: `monitoring/performance`,
    PERFORMANCE_SUMMARY: `monitoring/performance/summary`,
    PERFORMANCE_RESET: `monitoring/performance/reset`,
    BENCHMARK: `monitoring/benchmark`,
    BENCHMARK_COMPARE: `monitoring/benchmark/compare`
  },

  // 职业数据（professions 路由，与 game-data 区分）
  PROFESSIONS: {
    LIST: `professions`,
    DETAIL: (name: string) => `professions/${name}`,
    ELITE_SPECS: `professions/elite-specs`,
    ROLE_TYPES: `professions/role-types`,
    CASCADE: `professions/cascade`,
    STATISTICS: `professions/statistics`,
    ROLE_MAPPING: `professions/role-mapping`,
    UPDATE_PROFESSION_ROLE: (key: string) => `professions/profession/${key}/role`,
    UPDATE_ELITE_SPEC_ROLE: (key: string) => `professions/elite-spec/${key}/role`,
  },

  // 游戏数据
  GAME_DATA: {
    INFO: `game-data/info`,
    RELOAD: `game-data/reload`,
    PROFESSIONS: `game-data/professions`,
    PROFESSION_DETAIL: (name: string) => `game-data/professions/${name}`,
    PROFESSION_NAME_CN: (name: string) => `game-data/professions/${name}/name-cn`,
    PROFESSION_DEFAULT_ROLE: (name: string) => `game-data/professions/${name}/default-role`,
    PROFESSION_SCORING_CONFIG: (name: string) => `game-data/professions/${name}/scoring-config`,
    ELITE_SPECS: `game-data/elite-specs`,
    ELITE_SPEC_DETAIL: (name: string) => `game-data/elite-specs/${name}`,
    BUFFS: `game-data/buffs`,
    BUFF_DETAIL: (id: string | number) => `game-data/buffs/${id}`,
    BUFF_NAME_CN: (id: string | number) => `game-data/buffs/${id}/name-cn`,
    BUFF_CATEGORIES: `game-data/categories/buffs`
  },

  // GW2参考数据（装备下拉列表）
  REF_DATA: {
    RUNES: `ref-data/runes`,
    SIGILS: `ref-data/sigils`,
    RELICS: `ref-data/relics`,
    FOODS: `ref-data/foods`,
    UTILITIES: `ref-data/utilities`,
  },



  // 评分规则管理
  SCORING_RULES: {
    BASE: `scoring-rules`,
    ROLES: `scoring-rules/roles`,
    RULES: `scoring-rules/rules`,
    RULE_DETAIL: (id: string | number) => `scoring-rules/rules/${id}`,
    RULE_UPDATE: (id: string | number) => `scoring-rules/rules/${id}`,
    RULE_DELETE: (id: string | number) => `scoring-rules/rules/${id}`,
    BATCH: `scoring-rules/rules/batch`,
    RESET: `scoring-rules/rules/reset`,
    DIMENSIONS: `scoring-rules/dimensions`,
    // v3.0 新增：职业特定规则
    PROFESSION_RULES: (profession: string) => `scoring-rules/rules/profession/${encodeURIComponent(profession)}`,
    PROFESSIONS: `scoring-rules/professions`,
    // v3.0 新增：版本管理
    VERSIONS: `scoring-rules/versions`,
    VERSION_DETAIL: (id: string | number) => `scoring-rules/versions/${id}`,
    VERSION_BUMP: `scoring-rules/versions/bump`,
  },

  // 评分系统（实时计算 + 重算任务）
  SCORING: {
    RULES: `scoring/rules`,
    FIGHT: (id: string | number) => `scoring/fight/${id}`,
    RECALCULATE: `scoring/recalculate`,
    RECALCULATE_STATUS: (versionId: string | number) => `scoring/recalculate/${versionId}`,
  },

  // 角色管理
  ROLES: {
    RULES: `roles/rules`,
    RULES_BY_PROFESSION: (professionId: string) => `roles/rules/profession/${professionId}`,
    RULE_DETAIL: (ruleId: string | number) => `roles/rules/${ruleId}`,
    RULE_UPDATE: (ruleId: string | number) => `roles/rules/${ruleId}`,
    RULE_DELETE: (ruleId: string | number) => `roles/rules/${ruleId}`,
    TEMPLATES: `roles/templates`,
    TEMPLATE_CREATE: `roles/templates`,
    TEMPLATE_DETAIL: (templateId: string | number) => `roles/templates/${templateId}`,
    TEMPLATE_UPDATE: (templateId: string | number) => `roles/templates/${templateId}`,
    TEMPLATE_DELETE: (templateId: string | number) => `roles/templates/${templateId}`,
    TEMPLATE_BY_NAME: (templateName: string) => `roles/templates/name/${templateName}`,
    TEMPLATE_APPLY: (templateId: string | number) => `roles/templates/${templateId}/apply`,
    TEMPLATE_INIT_PRESETS: `roles/templates/init-presets`,
    EXPORT: `roles/export`,
    IMPORT: `roles/import`,
    EXPRESSIONS: `roles/expressions`,
    EXPRESSION_CREATE: `roles/expressions`,
    ASSIGN: `roles/assign`,
    QUERY: `roles/query`
  },

  // EI 分析
  EI: {
    ANALYSIS_SUMMARY: (logId: string | number) => `ei-analysis/${logId}`,
    ANALYSIS_PLAYER_DETAIL: (logId: string | number, account: string) => `ei-analysis/${logId}/player/${account}`,
    ANALYSIS_PLAYER_ROTATION: (logId: string | number, account: string) => `ei-analysis/${logId}/player/${account}/rotation`,
    UNIFIED: (logId: string | number) => `ei-report/logs/${logId}/unified`
  },

  // WvW 战斗报告
  WVW_REPORT: {
    LOGS: `wvw-report/logs`,
    SUMMARY: (logId: string | number) => `wvw-report/${logId}/summary`,
    PLAYERS: (logId: string | number) => `wvw-report/${logId}/players`,
    PLAYER_DETAIL: (logId: string | number, playerId: string | number) => `wvw-report/${logId}/players/${playerId}`,
    TARGETS: (logId: string | number) => `wvw-report/${logId}/targets`,
    PHASES: (logId: string | number) => `wvw-report/${logId}/phases`,
    TIMELINE: (logId: string | number) => `wvw-report/${logId}/timeline`,
    SKILL_MAP: (logId: string | number) => `wvw-report/${logId}/skill-map`,
  },

  // 通知中心
  NOTICES: {
    UNREAD_COUNT: `notices/unread-count`,
    LIST: `notices`,
    MARK_READ: (id: string | number) => `notices/${id}/read`,
    MARK_ALL_READ: `notices/read-all`,
  },

  // 健康检查
  HEALTH: `health`,

  // 测试接口
  TEST: {
    DPS_REPORT: `test/dps-report`
  },

  // 菜单管理
  MENUS: {
    PUBLIC: `menus/public`,
    LIST: `menus`,
    DETAIL: (id: string | number) => `menus/${id}`,
    TREE: `menus/tree`,
    ROLE: (roleId: string | number) => `menus/role/${roleId}`
  },

  // 战斗分析
  COMBAT_ANALYSIS: {
    FIGHT_BASIC: (logId: string | number) => `combat-analysis/logs/${logId}/fight`,
    PLAYERS_LIST: (logId: string | number) => `combat-analysis/logs/${logId}/players`,
    PLAYER_STATS: (logId: string | number) => `combat-analysis/logs/${logId}/players/stats`,
    PLAYER_BUFFS: (logId: string | number) => `combat-analysis/logs/${logId}/players/buffs`,
    PLAYER_ROTATION: (logId: string | number) => `combat-analysis/logs/${logId}/players/rotation`,
    RAW_DATA: (logId: string | number) => `combat-analysis/logs/${logId}/raw`,
    PLAYER_DETAIL_LEGACY: (logId: string | number, accountName: string) => `combat-analysis/logs/${logId}/players/${encodeURIComponent(accountName)}`,
    PLAYER_BUFFS_LEGACY: (logId: string | number, accountName: string) => `combat-analysis/logs/${logId}/players/${encodeURIComponent(accountName)}/buffs`,
    PLAYER_ROTATION_LEGACY: (logId: string | number, accountName: string) => `combat-analysis/logs/${logId}/players/${encodeURIComponent(accountName)}/rotation`,
    LEADERBOARD: (logId: string | number) => `combat-analysis/leaderboard/${logId}`,
    TEAM_BUFFS: (logId: string | number) => `combat-analysis/team-buffs/${logId}`,
    FIGHT_DETAILS: (logId: string | number) => `combat-analysis/logs/${logId}/fight/details`,
    FIGHT_METRICS: (logId: string | number) => `combat-analysis/fight-metrics/${logId}`
  }
} as const;

export type ApiEndpointKey = typeof API_ENDPOINTS;
