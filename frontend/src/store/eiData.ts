/**
 * Elite Insights 数据状态管�? * 作者：帅姐�? * 创建日期�?024-01-15
 */

import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { EliteInsightsLog, Player } from '@/types/eliteInsights';
import { eiDataService } from '@/services/ei/eiDataService';

export const useEiDataStore = defineStore('eiData', () => {
  // =============================================
  // 状态定�?  // =============================================

  const logData = ref<EliteInsightsLog | null>(null);
  const isLoading = ref(false);
  const isError = ref(false);
  const errorMessage = ref('');
  const activeTab = ref<'stats' | 'replay' | 'healing'>('stats');
  const selectedPlayerId = ref<number | null>(null);
  const lightTheme = ref(false);

  // =============================================
  // 计算属�?  // =============================================

  const players = computed(() => eiDataService.getRealPlayers());

  const playersSortedByDmg = computed(() => eiDataService.getPlayersSortedByDmg());

  const playersSortedByScore = computed(() => eiDataService.getPlayersSortedByScore());

  const fightName = computed(() => eiDataService.getFightName());

  const fightDuration = computed(() => eiDataService.getDuration());

  const teamStats = computed(() => eiDataService.getTeamStats());

  const totalDamageStats = computed(() => eiDataService.getTotalDamageStats());

  const selectedPlayer = computed(() => {
    if (selectedPlayerId.value === null) return null;
    return players.value.find(p => p.instanceID === selectedPlayerId.value) || null;
  });

  const recorderInfo = computed(() => eiDataService.getRecorderInfo());

  const versions = computed(() => eiDataService.getVersions());

  // =============================================
  // 方法
  // =============================================

  /**
   * 加载 JSON 数据
   */
  async function loadLogData(data: EliteInsightsLog): Promise<void> {
    isLoading.value = true;
    isError.value = false;
    errorMessage.value = '';

    try {
      eiDataService.setLogData(data);
      logData.value = data;
    } catch (error) {
      isError.value = true;
      errorMessage.value = error instanceof Error ? error.message : '加载数据失败';
      console.error('Failed to load log data:', error);
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * �?JSON 字符串加�?   */
  async function loadLogDataFromJson(jsonString: string): Promise<void> {
    try {
      const data = JSON.parse(jsonString);
      await loadLogData(data);
    } catch (error) {
      isError.value = true;
      errorMessage.value = 'JSON 解析失败';
      console.error('Failed to parse JSON:', error);
    }
  }

  /**
   * 从文件加�?   */
  async function loadLogDataFromFile(file: File): Promise<void> {
    isLoading.value = true;
    isError.value = false;

    try {
      const text = await file.text();
      await loadLogDataFromJson(text);
    } catch (error) {
      isError.value = true;
      errorMessage.value = error instanceof Error ? error.message : '文件读取失败';
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * 重置数据
   */
  function resetData(): void {
    logData.value = null;
    selectedPlayerId.value = null;
    isError.value = false;
    errorMessage.value = '';
  }

  /**
   * 切换标签�?   */
  function setActiveTab(tab: 'stats' | 'replay' | 'healing'): void {
    activeTab.value = tab;
  }

  /**
   * 选择玩家
   */
  function selectPlayer(instanceId: number): void {
    selectedPlayerId.value = instanceId;
  }

  /**
   * 取消选择玩家
   */
  function clearPlayerSelection(): void {
    selectedPlayerId.value = null;
  }

  /**
   * 切换主题
   */
  function toggleTheme(light?: boolean): void {
    if (typeof light === 'boolean') {
      lightTheme.value = light;
    } else {
      lightTheme.value = !lightTheme.value;
    }
  }

  // =============================================
  // 数据查询
  // =============================================

  function getPlayerById(instanceId: number): Player | undefined {
    return players.value.find(p => p.instanceID === instanceId);
  }

  function getPlayersByProfession(profession: string): Player[] {
    return players.value.filter(p => p.profession === profession);
  }

  return {
    // 状�?    logData,
    isLoading,
    isError,
    errorMessage,
    activeTab,
    selectedPlayerId,
    lightTheme,

    // 计算属�?    isDataLoaded,
    players,
    playersSortedByDmg,
    playersSortedByScore,
    fightName,
    fightDuration,
    teamStats,
    totalDamageStats,
    selectedPlayer,
    recorderInfo,
    versions,

    // 方法
    loadLogData,
    loadLogDataFromJson,
    loadLogDataFromFile,
    resetData,
    setActiveTab,
    selectPlayer,
    clearPlayerSelection,
    toggleTheme,
    getPlayerById,
    getPlayersByProfession
  };
});
