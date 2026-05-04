/**
 * Elite Insights 数据处理服务
 * 作者：帅姐�? * 创建日期�?024-01-15
 */

import type { EliteInsightsLog, Player } from '@/types/eliteInsights';

export class EiDataService {
  private logData: EliteInsightsLog | null = null;

  constructor(data?: EliteInsightsLog) {
    if (data) {
      this.logData = data;
    }
  }

  /**
   * 设置日志数据
   */
  setLogData(data: EliteInsightsLog): void {
    this.logData = data;
  }

  /**
   * 获取日志数据
   */
  getLogData(): EliteInsightsLog | null {
    return this.logData;
  }

  /**
   * 检查数据是否已加载
   */
  isDataLoaded(): boolean {
    return this.logData !== null;
  }

  // =============================================
  // 战斗基本信息
  // =============================================

  /**
   * 获取战斗名称
   */
  getFightName(): string {
    return this.logData?.fightName || '未知战斗';
  }

  /**
   * 获取战斗时长 (毫秒)
   */
  getDuration(): number {
    return this.logData?.durationMS || 0;
  }

  /**
   * 获取记录者信�?   */
  getRecorderInfo(): { name: string; account: string } {
    return {
      name: this.logData?.recordedBy || '未知',
      account: this.logData?.recordedAccountBy || '未知'
    };
  }

  /**
   * 获取版本信息
   */
  getVersions(): {
    eliteInsights: string;
    arc: string;
    gw2: number;
  } {
    return {
      eliteInsights: this.logData?.eliteInsightsVersion || '未知',
      arc: this.logData?.arcVersion || '未知',
      gw2: this.logData?.gw2Build || 0
    };
  }

  // =============================================
  // 玩家数据处理
  // =============================================

  /**
   * 获取所有玩�?   */
  getAllPlayers(): Player[] {
    return this.logData?.players || [];
  }

  /**
   * 获取�?NPC 玩家
   */
  getRealPlayers(): Player[] {
    return this.getAllPlayers().filter(p => !p.isFake && !p.friendlyNPC);
  }

  /**
   * 按职业分组玩�?   */
  getPlayersByProfession(): Map<string, Player[]> {
    const groups = new Map<string, Player[]>();
    this.getRealPlayers().forEach(player => {
      if (!groups.has(player.profession)) {
        groups.set(player.profession, []);
      }
      groups.get(player.profession)!.push(player);
    });
    return groups;
  }

  /**
   * 按伤害排序玩�?   */
  getPlayersSortedByDmg(): Player[] {
    return [...this.getRealPlayers()].sort((a, b) => b.dps - a.dps);
  }

  /**
   * 按评分排序玩�?   */
  getPlayersSortedByScore(): Player[] {
    return [...this.getRealPlayers()].sort((a, b) => b.total_score - a.total_score);
  }

  /**
   * 获取总伤害统�?   */
  getTotalDamageStats(): {
    total: number;
    power: number;
    condi: number;
  } {
    let total = 0;
    let power = 0;
    let condi = 0;

    this.getRealPlayers().forEach(player => {
      const dps = player.dpsAll?.[0];
      if (dps) {
        total += dps.damage;
        power += dps.powerDamage;
        condi += dps.condiDamage;
      }
    });

    return { total, power, condi };
  }

  /**
   * 获取团队统计信息
   */
  getTeamStats(): {
    playerCount: number;
    totalDps: number;
    avgDps: number;
    totalDowns: number;
    totalDeaths: number;
    totalCleanses: number;
    totalStrips: number;
  } {
    const players = this.getRealPlayers();
    let totalDps = 0;
    let totalDowns = 0;
    let totalDeaths = 0;
    let totalCleanses = 0;
    let totalStrips = 0;

    players.forEach(player => {
      totalDps += player.dps;
      totalDowns += player.downs;
      totalDeaths += player.deaths;
      totalCleanses += player.cleanses;
      totalStrips += player.strips;
    });

    return {
      playerCount: players.length,
      totalDps,
      avgDps: players.length > 0 ? totalDps / players.length : 0,
      totalDowns,
      totalDeaths,
      totalCleanses,
      totalStrips
    };
  }

  // =============================================
  // 目标数据处理
  // =============================================

  /**
   * 获取所有目�?   */
  getTargets(): any[] {
    return this.logData?.targets || [];
  }

  /**
   * 获取真实目标 (�?dummy)
   */
  getRealTargets(): any[] {
    return this.getTargets().filter(t => !t.isFake);
  }

  // =============================================
  // 数据筛选和查询
  // =============================================

  /**
   * 根据 ID 查询玩家
   */
  getPlayerById(instanceId: number): Player | undefined {
    return this.getRealPlayers().find(p => p.instanceID === instanceId);
  }

  /**
   * 根据名称查询玩家
   */
  getPlayerByName(name: string): Player | undefined {
    return this.getRealPlayers().find(p => p.name === name);
  }

  /**
   * 根据职业筛选玩�?   */
  getPlayersByProfessionFilter(profession: string): Player[] {
    return this.getRealPlayers().filter(p => p.profession === profession);
  }
}

// 单例导出
export const eiDataService = new EiDataService();

export default eiDataService;
