import { useCombatLogDetail } from './useCombatLogDetail'

/**
 * useCombatLogData - 战斗日志数据的兼容层 composable
 * 现在为 useCombatLogDetail 的 thin wrapper，保持原有导出接口不变
 */
export function useCombatLogData() {
  const detail = useCombatLogDetail()

  // 兼容原有可选 sortBy 参数签名（参数不再使用，排序由服务端默认处理）
  const loadData = async (_sortBy?: string) => {
    await detail.loadData()
  }

  return {
    // State
    loading: detail.loading,
    parsing: detail.parsing,
    error: detail.error,
    logDetail: detail.logDetail,
    summary: detail.summary,
    selectedPlayer: detail.selectedPlayer,
    playerRotation: detail.playerRotation,
    rotationLoading: detail.rotationLoading,
    dialogVisible: detail.dialogVisible,

    // Computed
    fightSummary: detail.fightSummary,
    agg: detail.agg,
    players: detail.players,
    topDpsPlayers: detail.topDpsPlayers,
    commanders: detail.commanders,
    groups: detail.groups,
    ungroupedPlayers: detail.ungroupedPlayers,
    sortedPlayerList: detail.sortedPlayerList,
    quickInfoItems: detail.quickInfoItems,

    // Actions
    loadData,
    reparseLog: detail.reparseLog,
    openPlayerDialog: detail.openPlayerDialog,
  }
}
