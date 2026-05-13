/**
 * 技能 API 服务模块
 * 功能：处理技能相关的API请求
 * 作者：帅姐姐
 * 创建日期：2026-05-04
 * 更新日期：2026-05-14
 */

import { apiFactory } from '@/services/core/apiService'
import { API_ENDPOINTS } from '@/config/apiEndpoints'
import type { RotationAnalysis } from '@/models/skillRotation'

export interface Skill {
  id: string
  name: string
  icon: string
  profession?: string
  elite_spec?: string
  type: 'heal' | 'utility' | 'elite' | 'weapon'
  description?: string
  cooldown?: number
  energy_cost?: number
  initiative_cost?: number
}

export interface SkillRotationEvent {
  timestamp: number
  skill_id: string
  skill_name: string
  target?: string
  success: boolean
}

export interface SkillAnalysisRequest {
  log_id: string | number
  member_id: string | number
}

export interface SkillAnalysisResponse {
  member_id?: number
  account?: string
  log_id: number
  fight_count: number
  total_damage: number
  avg_dps: number
  total_healing: number
  skill_cast_uptime: number
  buffs: {
    might: number
    fury: number
    quickness: number
    alacrity: number
    protection: number
    stability: number
  }
  survival: {
    damage_taken: number
    deaths: number
    downs: number
    dodge_count: number
  }
  combat: {
    killed: number
    downed: number
    boon_strips: number
    condition_cleanses: number
    interrupts: number
  }
}

/**
 * 技能 API 服务类
 */
class SkillsApiService {
  /**
   * 获取技能列表
   * @param profession 职业筛选
   */
  async getSkillList(profession?: string): Promise<Skill[] | null> {
    try {
      const params = profession ? { profession } : {}
      const response = await apiFactory.get<Skill[]>(
        API_ENDPOINTS.SKILLS.LIST,
        { params }
      )

      if (response.success && response.data) {
        return response.data
      }

      return null
    } catch (error) {
      console.error('[SkillsApi] 获取技能列表失败', error)
      throw error
    }
  }

  /**
   * 获取技能详情
   * @param skillId 技能ID
   */
  async getSkillDetail(skillId: string): Promise<Skill | null> {
    try {
      const response = await apiFactory.get<Skill>(
        API_ENDPOINTS.SKILLS.DETAIL(skillId)
      )

      if (response.success && response.data) {
        return response.data
      }

      return null
    } catch (error) {
      console.error('[SkillsApi] 获取技能详情失败', error)
      throw error
    }
  }

  /**
   * 分析技能循环
   * @param logId 日志ID
   * @param memberId 成员ID
   */
  async analyzeSkillRotation(
    logId: string,
    memberId: string
  ): Promise<RotationAnalysis | null> {
    try {
      const response = await apiFactory.post<RotationAnalysis>(
        API_ENDPOINTS.SKILL_ROTATION.ANALYZE,
        { log_id: logId, member_id: memberId }
      )

      if (response.success && response.data) {
        return response.data
      }

      return null
    } catch (error) {
      console.error('[SkillsApi] 分析技能循环失败', error)
      throw error
    }
  }

  /**
   * 对比技能循环
   * @param logIds 日志ID数组
   */
  async compareSkillRotations(logIds: string[]): Promise<any | null> {
    try {
      const response = await apiFactory.post(
        API_ENDPOINTS.SKILL_ROTATION.COMPARE,
        { log_ids: logIds }
      )

      if (response.success && response.data) {
        return response.data
      }

      return null
    } catch (error) {
      console.error('[SkillsApi] 对比技能循环失败', error)
      throw error
    }
  }

  /**
   * 获取技能历史记录
   */
  async getSkillRotationHistory(): Promise<any[] | null> {
    try {
      const response = await apiFactory.get<any[]>(
        API_ENDPOINTS.SKILL_ROTATION.HISTORY
      )

      if (response.success && response.data) {
        return response.data
      }

      return null
    } catch (error) {
      console.error('[SkillsApi] 获取技能历史失败', error)
      throw error
    }
  }

  /**
   * 获取玩家技能循环（从EI分析）
   * @param logId 日志ID
   * @param account 账号名
   */
  async getPlayerRotation(logId: string, account: string): Promise<any | null> {
    try {
      const response = await apiFactory.get(
        API_ENDPOINTS.EI.ANALYSIS_PLAYER_ROTATION(logId, account)
      )

      if (response.success && response.data) {
        return response.data
      }

      return null
    } catch (error) {
      console.error('[SkillsApi] 获取玩家技能循环失败', error)
      throw error
    }
  }

  /**
   * 导出分析报告
   * @param logId 日志ID
   * @param memberId 成员ID
   */
  async exportReport(logId: string, memberId: string): Promise<Blob | null> {
    try {
      const response = await apiFactory.post<Blob>(
        API_ENDPOINTS.SKILL_ROTATION.EXPORT_REPORT,
        { log_id: logId, member_id: memberId },
        { responseType: 'blob' }
      )

      if (response.success && response.data) {
        return response.data
      }

      return null
    } catch (error) {
      console.error('[SkillsApi] 导出报告失败', error)
      throw error
    }
  }

  /**
   * 获取理想技能循环配置
   * @param profession 职业名称
   */
  async getIdealRotations(profession?: string): Promise<any[] | null> {
    try {
      const params = profession ? { profession } : {}
      const response = await apiFactory.get<any[]>(
        API_ENDPOINTS.SKILL_ROTATION.IDEAL_ROTATIONS,
        { params }
      )

      if (response.success && response.data) {
        return response.data
      }

      return null
    } catch (error) {
      console.error('[SkillsApi] 获取理想技能循环失败', error)
      throw error
    }
  }
}

// 导出单例实例
export default new SkillsApiService()
export { SkillsApiService }
export { SkillsApiService as skillsApi }
