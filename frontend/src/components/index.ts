/**
 * 组件统一导出
 * 功能：所有业务/通用组件从此文件导入
 * 使用方式: import { ComponentName } from '@/components'
 * 更新日期：2026-05-11 - 清理重复目录，统一结构
 */

// ── AI 分析 ──
export { default as AiAnalysisTools } from './ai/AiAnalysisTools.vue'
export { default as AiReportList } from './ai/AiReportList.vue'
export { default as AiSuggestions } from './ai/AiSuggestions.vue'
export { default as AiTrendAnalysis } from './ai/AiTrendAnalysis.vue'

// ── 出勤统计 ──
export { default as AttendanceDetail } from './attendance/AttendanceDetail.vue'
export { default as AttendanceFilter } from './attendance/AttendanceFilter.vue'
export { default as AttendanceFilterBar } from './attendance/AttendanceFilterBar.vue'
export { default as AttendanceStatCards } from './attendance/AttendanceStatCards.vue'
export { default as AttendanceTable } from './attendance/AttendanceTable.vue'
export { default as PlayerRanking } from './attendance/PlayerRanking.vue'
export { default as ScoreBreakdownDialog } from './attendance/ScoreBreakdownDialog.vue'
export { default as ScoringRulesDialog } from './attendance/ScoringRulesDialog.vue'
export { default as TeamRanking } from './attendance/TeamRanking.vue'

// ── 出勤详情 ──
export { default as AttendanceCharacters } from './attendance/detail/AttendanceCharacters.vue'
export { default as AttendanceCharts } from './attendance/detail/AttendanceCharts.vue'
export { default as AttendanceFights } from './attendance/detail/AttendanceFights.vue'
export { default as AttendanceSummaryCards } from './attendance/detail/AttendanceSummaryCards.vue'
export { default as AttendanceStatCard } from './attendance/detail/StatCard.vue'

// ── 配装库 ──
export { default as BuildBasicInfoPanel } from './build/library/BuildBasicInfoPanel.vue'
export { default as BuildCard } from './build/library/BuildCard.vue'
export { default as BuildCodePanel } from './build/library/BuildCodePanel.vue'
export { default as BuildDetailDrawer } from './build/library/BuildDetailDrawer.vue'
export { default as BuildEditDialog } from './build/library/BuildEditDialog.vue'
export { default as BuildExtrasPanel } from './build/library/BuildExtrasPanel.vue'
export { default as BuildFilterSidebar } from './build/library/BuildFilterSidebar.vue'
export { default as BuildGearPanel } from './build/library/BuildGearPanel.vue'
export { default as BuildTraitLinesPanel } from './build/library/BuildTraitLinesPanel.vue'
export { default as CommanderCheatsheet } from './build/library/CommanderCheatsheet.vue'
export { default as FilterSection } from './build/library/FilterSection.vue'
export { default as GearOverviewCard } from './build/library/GearOverviewCard.vue'

// ── 配装解析 ──
export { default as BuildCodeInput } from './build/parser/BuildCodeInput.vue'
export { default as BuildDialog } from './build/parser/BuildDialog.vue'
export { default as CompareDialog } from './build/parser/CompareDialog.vue'
export { default as Equipment } from './build/parser/Equipment.vue'
export { default as ImportDialog } from './build/parser/ImportDialog.vue'
export { default as LogImportDialog } from './build/parser/LogImportDialog.vue'
export { default as SaveDialog } from './build/parser/SaveDialog.vue'
export { default as SavedBuilds } from './build/parser/SavedBuilds.vue'
export { default as Skills } from './build/parser/Skills.vue'
export { default as Stats } from './build/parser/Stats.vue'
export { default as TemplateInfo } from './build/parser/TemplateInfo.vue'

// ── 配装共享 ──
export { default as BuildComparison } from './build/shared/BuildComparison.vue'
export { default as StatItem } from './build/shared/StatItem.vue'
export { default as Traits } from './build/shared/Traits.vue'

// ── 战斗日志 ──
export { default as PlayerDetailHeader } from './combat/PlayerDetailHeader.vue'
export { default as PlayerDetailPanel } from './combat/PlayerDetailPanel.vue'
export { default as PlayerDetailRotation } from './combat/PlayerDetailRotation.vue'
export { default as SkillRotationTimeline } from './combat/SkillRotationTimeline.vue'
export { default as SkillRotationViewer } from './combat/SkillRotationViewer.vue'

// ── 战斗详情 ──
export { default as DamageDetailDialog } from './combat/detail/DamageDetailDialog.vue'
export { default as FightOverviewTab } from './combat/detail/FightOverviewTab.vue'
export { default as FightPlayerStatsTable } from './combat/detail/FightPlayerStatsTable.vue'
export { default as PlayerSquadTab } from './combat/detail/PlayerSquadTab.vue'
export { default as SquadRoster } from './combat/detail/SquadRoster.vue'
export { default as StatDetailDialog } from './combat/detail/StatDetailDialog.vue'

// ── 战斗轮转 ──
export { default as AdvancedRotationView } from './combat/rotation/AdvancedRotationView.vue'
export { default as RotationCycleView } from './combat/rotation/RotationCycleView.vue'
export { default as RotationHeatmapView } from './combat/rotation/RotationHeatmapView.vue'
export { default as RotationTimelineLegend } from './combat/rotation/RotationTimelineLegend.vue'
export { default as RotationTimelineView } from './combat/rotation/RotationTimelineView.vue'
export { default as RotationViewModeBar } from './combat/rotation/RotationViewModeBar.vue'
export { default as SimpleRotationView } from './combat/rotation/SimpleRotationView.vue'

// ── 仪表盘 ──
export { default as BattleHistory } from './dashboard/BattleHistory.vue'
export { default as BuffOverview } from './dashboard/BuffOverview.vue'
export { default as DamageTrend } from './dashboard/DamageTrend.vue'
export { default as DashboardStatCards } from './dashboard/StatCards.vue'
export { default as MapHeatmap } from './dashboard/MapHeatmap.vue'
export { default as ProfessionDistribution } from './dashboard/ProfessionDistribution.vue'
export { default as TopPlayers } from './dashboard/TopPlayers.vue'
export { default as DashboardWelcomeBanner } from './dashboard/WelcomeBanner.vue'

// ── 字典管理 ──
export { default as DictDataDialog } from './common/dictionary/DictDataDialog.vue'
export { default as DictDataTable } from './common/dictionary/DictDataTable.vue'
export { default as DictDataToolbar } from './common/dictionary/DictDataToolbar.vue'
export { default as DictManagementHeader } from './common/dictionary/DictManagementHeader.vue'
export { default as DictOverviewCards } from './common/dictionary/DictOverviewCards.vue'
export { default as DictOverviewView } from './common/dictionary/DictOverviewView.vue'
export { default as DictTypeDialog } from './common/dictionary/DictTypeDialog.vue'
export { default as DictTypeSidebar } from './common/dictionary/DictTypeSidebar.vue'
export { default as DictionaryManagement } from './common/dictionary/DictionaryManagement.vue'
export { default as DictionaryManagementWrapper } from './common/dictionary/DictionaryManagementWrapper.vue'
export { default as InitConfirmDialog } from './common/dictionary/InitConfirmDialog.vue'

// ── 通用组件: 布局 ──
export { default as PageHeader } from './common/layout/PageHeader.vue'
export { default as PermissionDenied } from './common/layout/PermissionDenied.vue'

// ── 通用组件: UI 基础 ──
export { default as BaseButton } from './common/ui/input/BaseButton.vue'
export { default as BaseCheckbox } from './common/ui/input/BaseCheckbox.vue'
export { default as BaseDialog } from './common/ui/feedback/BaseDialog.vue'
export { default as BaseInput } from './common/ui/input/BaseInput.vue'
export { default as BaseInputNumber } from './common/ui/input/BaseInputNumber.vue'
export { default as BaseProgressBar } from './common/ui/display/BaseProgressBar.vue'
export { default as BaseProgressSpinner } from './common/ui/display/BaseProgressSpinner.vue'
export { default as BaseRadioButton } from './common/ui/input/BaseRadioButton.vue'
export { default as BaseSelect } from './common/ui/input/BaseSelect.vue'
export { default as BaseState } from './common/ui/display/BaseState.vue'
export { default as BaseTag } from './common/ui/display/BaseTag.vue'
export { default as BaseTextarea } from './common/ui/input/BaseTextarea.vue'
export { default as ColorPickerInput } from './common/ui/input/ColorPickerInput.vue'
export { default as ColorPickerPanel } from './common/ui/overlay/ColorPickerPanel.vue'
export { default as EmptyState } from './common/ui/display/EmptyState.vue'
export { default as FormField } from './common/ui/input/FormField.vue'
export { default as LoadingState } from './common/ui/feedback/LoadingState.vue'

// ── 通用组件: 反馈 ──
export { default as DataCard } from './common/feedback/DataCard.vue'
export { default as MetricCard } from './common/feedback/MetricCard.vue'
export { default as StatCard } from './common/feedback/StatCard.vue'

// ── 通用组件: 主题 ──
export { default as ThemeSelector } from './common/theme/ThemeSelector.vue'
export { default as ThemeSwitcher } from './common/theme/ThemeSwitcher.vue'

// ── EI详情 ──
export { default as ActorSelector } from './eiDetail/player/ActorSelector.vue'
export { default as BoonsUptimeCard } from './eiDetail/charts/BoonsUptimeCard.vue'
export { default as BuffsView } from './eiDetail/stats/BuffsView.vue'
export { default as CombatReplay } from './eiDetail/replay/CombatReplay.vue'
export { default as DamageAnalysisView } from './eiDetail/stats/DamageAnalysisView.vue'
export { default as DamageDistributionChart } from './eiDetail/charts/DamageDistributionChart.vue'
export { default as DefenseStatsTable } from './eiDetail/tables/DefenseStatsTable.vue'
export { default as DpsGraphView } from './eiDetail/charts/DpsGraphView.vue'
export { default as EncounterHeader } from './eiDetail/stats/EncounterHeader.vue'
export { default as EnemyTargetsView } from './eiDetail/stats/EnemyTargetsView.vue'
export { default as EventTimelineView } from './eiDetail/replay/EventTimelineView.vue'
export { default as HealingExtension } from './eiDetail/stats/HealingExtension.vue'
export { default as OffensiveStatsTable } from './eiDetail/tables/OffensiveStatsTable.vue'
export { default as OverviewView } from './eiDetail/stats/OverviewView.vue'
export { default as PhaseNavigator } from './eiDetail/stats/PhaseNavigator.vue'
export { default as PlayerDetailModal } from './eiDetail/player/PlayerDetailModal.vue'
export { default as PlayerDetailSidebar } from './eiDetail/player/PlayerDetailSidebar.vue'
export { default as PlayerStatsDetail } from './eiDetail/player/PlayerStatsDetail.vue'
export { default as PlayerStatsTable } from './eiDetail/player/PlayerStatsTable.vue'
export { default as PlayerSummaryView } from './eiDetail/player/PlayerSummaryView.vue'
export { default as SkillCastChart } from './eiDetail/charts/SkillCastChart.vue'
export { default as SkillRotationView } from './eiDetail/player/SkillRotationView.vue'
export { default as SquadCompositionView } from './eiDetail/stats/SquadCompositionView.vue'
export { default as StatsView } from './eiDetail/stats/StatsView.vue'
export { default as SupportStatsTable } from './eiDetail/tables/SupportStatsTable.vue'
export { default as TargetStatsCard } from './eiDetail/stats/TargetStatsCard.vue'
export { default as TargetSummaryView } from './eiDetail/stats/TargetSummaryView.vue'
export { default as TeamSummaryCard } from './eiDetail/stats/TeamSummaryCard.vue'

// ── 日志上传 ──
export { default as UploadDropZone } from './log/upload/UploadDropZone.vue'
export { default as UploadFileList } from './log/upload/UploadFileList.vue'
export { default as UploadResultSummary } from './log/upload/UploadResultSummary.vue'

// ── 日志管理 ──
export { default as BatchParseDialog } from './log/BatchParseDialog.vue'
export { default as DeleteConfirmDialog } from './log/DeleteConfirmDialog.vue'
export { default as LogFilters } from './log/LogFilters.vue'
export { default as LogStatCards } from './log/StatCards.vue'
export { default as LogTable } from './log/LogTable.vue'
export { default as LogTableActions } from './log/LogTableActions.vue'
export { default as LogUploadDialog } from './log/LogUploadDialog.vue'

// ── 设置 ──
export { default as AccountSettings } from './settings/account/AccountSettings.vue'
export { default as ChangePasswordDialog } from './settings/account/ChangePasswordDialog.vue'
export { default as ExportSettings } from './settings/account/ExportSettings.vue'
export { default as NotificationSettings } from './settings/appearance/NotificationSettings.vue'
export { default as ParsingSettings } from './settings/upload/ParsingSettings.vue'
export { default as ScoringGradeCards } from './settings/scoring/ScoringGradeCards.vue'
export { default as ScoringRecalcPanel } from './settings/scoring/ScoringRecalcPanel.vue'
export { default as ScoringRoleCards } from './settings/scoring/ScoringRoleCards.vue'
export { default as ScoringRoleHeader } from './settings/scoring/ScoringRoleHeader.vue'
export { default as ScoringRuleEditor } from './settings/scoring/ScoringRuleEditor.vue'
export { default as ScoringRuleExtras } from './settings/scoring/ScoringRuleExtras.vue'
export { default as ScoringRulesSettings } from './settings/scoring/ScoringRulesSettings.vue'
export { default as ScoringRulesTable } from './settings/scoring/ScoringRulesTable.vue'
export { default as ScoringVersionHistory } from './settings/scoring/ScoringVersionHistory.vue'
export { default as SectionHeader } from './settings/SectionHeader.vue'
export { default as SecuritySettings } from './settings/account/SecuritySettings.vue'
export { default as SettingItem } from './settings/SettingItem.vue'
export { default as SettingTabs } from './settings/SettingTabs.vue'
export { default as SystemFunctionsPanel } from './settings/system/SystemFunctionsPanel.vue'
export { default as ThemeSettings } from './settings/appearance/ThemeSettings.vue'
export { default as WatermarkSettings } from './settings/appearance/WatermarkSettings.vue'

// ── 技能循环 ──
export { default as ActualRotation } from './skillRotation/ActualRotation.vue'
export { default as AnalysisConfig } from './skillRotation/AnalysisConfig.vue'
export { default as IdealRotation } from './skillRotation/IdealRotation.vue'
export { default as SkillRotationImportDialog } from './skillRotation/ImportDialog.vue'
export { default as MistakeStats } from './skillRotation/MistakeStats.vue'
export { default as OptimizationSuggestions } from './skillRotation/OptimizationSuggestions.vue'
export { default as SkillRatioAnalysis } from './skillRotation/SkillRatioAnalysis.vue'
export { default as SkillTimeline } from './skillRotation/SkillTimeline.vue'
export { default as SkillRotationWelcomeBanner } from './skillRotation/WelcomeBanner.vue'

// ── 系统 ──
export { default as AppWatermark } from './system/AppWatermark.vue'

// ── 测试 ──
export { default as DpsTestResult } from './test/DpsTestResult.vue'
