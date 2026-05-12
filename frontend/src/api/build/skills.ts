/**
 * 技能 API 服务模块
 * 功能：处理技能相关的API请求
 * 作者：帅姐姐
 * 创建日期：2026-05-04
 */

import { apiFactory } from '@/services/core/apiService';
import { API_ENDPOINTS } from '@/config/apiEndpoints';

export interface Skill {
  id: string;
  name: string;
  icon: string;
  profession?: string;
  elite_spec?: string;
  type: 'heal' | 'utility' | 'elite' | 'weapon';
  description?: string;
  cooldown?: number;
  energy_cost?: number;
  initiative_cost?: number;
}

export interface SkillRotationEvent {
  timestamp: number;
  skill_id: string;
  skill_name: string;
  target?: string;
  success: boolean;
}

export interface SkillAnalysisRequest {
  log_id: string;
  member_id: string;
}

export interface SkillAnalysisResponse {
  rotations: SkillRotationEvent[];
  stats: {
    total_casts: number;
    average_cast_time: number;
    mistakes: Array<{
      timestamp: number;
      skill_id: string;
      description: string;
    }>;
  };
  ideal_rotation: SkillRotationEvent[];
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
      const params = profession ? { profession } : {};
      const response = await apiFactory.get<Skill[]>(
        API_ENDPOINTS.SKILLS.LIST,
        { params }
      );

      if (response.success && response.data) {
        return response.data;
      }

      return null;
    } catch (error) {
      console.error('[SkillsApi] 获取技能列表失败', error);
      throw error;
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
      );

      if (response.success && response.data) {
        return response.data;
      }

      return null;
    } catch (error) {
      console.error('[SkillsApi] 获取技能详情失败', error);
      throw error;
    }
  }

  /**
   * 分析技能循环
   * @param logId 日志ID
   * @param memberId 成员ID
   */
  async analyzeSkillRotation(logId: string, memberId: string): Promise<SkillAnalysisResponse | null> {
    try {
      const response = await apiFactory.post<SkillAnalysisResponse>(
        API_ENDPOINTS.SKILL_ROTATION.ANALYZE,
        { log_id: logId, member_id: memberId }
      );

      if (response.success && response.data) {
        return response.data;
      }

      return null;
    } catch (error) {
      console.error('[SkillsApi] 分析技能循环失败', error);
      throw error;
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
      );

      if (response.success && response.data) {
        return response.data;
      }

      return null;
    } catch (error) {
      console.error('[SkillsApi] 对比技能循环失败', error);
      throw error;
    }
  }

  /**
   * 获取技能历史记录
   */
  async getSkillRotationHistory(): Promise<any[] | null> {
    try {
      const response = await apiFactory.get<any[]>(
        API_ENDPOINTS.SKILL_ROTATION.HISTORY
      );

      if (response.success && response.data) {
        return response.data;
      }

      return null;
    } catch (error) {
      console.error('[SkillsApi] 获取技能历史失败', error);
      throw error;
    }
  }
}

// 导出单例实例
export default new SkillsApiService();
export { SkillsApiService };

// 类型已通过 interface 声明自动导出，无需重复 export type