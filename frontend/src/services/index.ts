export { authService, AuthService } from './auth/authService'
export { logsService, LogsService } from './combat/logsService'
export { fightsService, FightsService } from './combat/fightsService'
export { membersService, MembersService } from './data/membersService'
export { skillsService, SkillsService } from './combat/skillsService'
export { buildsService, BuildsService } from './build/buildsService'
export { aiService, AIService } from './core/aiService'
export { dashboardService, DashboardService } from './data/dashboardService'
export { gameDataService, GameDataService } from './data/gameDataService'
export { rolesService, RolesService } from './auth/rolesService'
export { skillRotationService, SkillRotationService } from './build/skillRotationService'
export { attendanceService, AttendanceService } from './data/attendanceService'
export { settingsService, SettingsService } from './system/settingsService'
export { usersService, UsersService } from './auth/usersService'
export { monitoringService, MonitoringService } from './core/monitoringService'
export { bdCodeService, BDCodeService } from './build/bdCodeService'
export { combatAnalysisService, CombatAnalysisService } from './combat/combatAnalysisService'
export { convertKeysToCamelCase } from '@/utils/core/caseConverter'
export { professionService } from './professionService'

export { errorHandler, ResponseParser, DataValidator, ApiResponseWrapper, ErrorCode, ErrorSeverity } from './core/errorHandler'

export type { AdminLogin, LoginResponse } from './auth/authService'
export type { LogEntry, LogMetadata, LogQueryParams, LogListParams, LogUploadParams, LogUpdate } from './combat/logsService'
export type { Fight, FightStats, FightQueryParams, FightsListParams } from './combat/fightsService'
export type { MembersListParams, MemberRankingParams } from './data/membersService'
export type { Skill, SkillRotationEvent, SkillsListParams } from './skills/skillsService'
export type { BuildParseResponse, BuildsListParams, BuildCreate, BuildUpdate, BuildLibraryListParams, BuildLibraryCreateRequest, BuildLibraryUpdateRequest } from './build/buildsService'
export type { ReportsListParams } from './core/aiService'
export type { AiReport, AiSuggestion, AiTrend } from './ai/aiService'
export type { RoleRuleCreate, RoleRuleUpdate, RoleTemplateCreate, RoleTemplateUpdate, TemplateApplyRequest, ImportDataRequest, ConditionExpressionCreate, RoleAssignmentRequest } from './auth/rolesService'
export type { SkillRotationAnalyzeRequest } from './build/skillRotationService'
export type { AttendanceListParams, AttendanceStatsParams, AttendanceExportParams } from './data/attendanceService'
export type { SettingsUpdate } from './system/settingsService'
export type { UsersListParams, UserCreate, UserUpdate, PasswordChange } from './auth/usersService'
export type { BDCodeParseRequest, BDCodeValidationRequest, BDCodeBatchRequest } from './build/bdCodeService'
export type {
  FightDetailResponse,
  PlayersListResponse,
  PlayerStatsResponse,
  PlayerBuffsResponse,
  PlayerRotationResponse,
  TeamBuffsResponse,
  LeaderboardResponse,
  PlayerListItem,
  PlayerQueryParams,
  RotationParams,
  AmbiguousResponse
} from './combat/combatAnalysisService'

export { wvwReportService } from './combat/wvwReportService'
export type { WvwReportListItem, WvwReportListResponse, WvwPlayersData, WvwTimelineData, WvwPlayerDetail, WvwTimelineEvent } from './combat/wvwReportService'

export { dictionaryService } from './system/dictionaryService'
export type { DictOption, DictData, DictType, DictApiResponse, PaginatedDictData } from './system/dictionaryService'

export { ThemeService } from './system/themeService'

export { eiAnalysisService } from './ei/eiAnalysisService'
export type { EiAnalysisFight, EiAnalysisPlayer, EiAnalysisAggregate, EiAnalysisEnemy, EiAnalysisResponse } from './ei/eiAnalysisService'

export { eiDataService, EiDataService } from './ei/eiDataService'

export { eiUnifiedService } from './ei/eiUnifiedService'
export type { EiUnifiedPlayer, EiUnifiedTarget, EiUnifiedPhase, EiUnifiedLogData, EiUnifiedResponse } from './ei/eiUnifiedService'

export type {
  RoleType,
  Profession,
  EliteSpecialization,
  ProfessionCascade,
  RoleProfessionMapping
} from './professionService'
