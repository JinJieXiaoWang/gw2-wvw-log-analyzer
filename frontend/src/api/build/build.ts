/**
 * Build API 服务模块
 * 功能：处理Build代码解析、保存、列表查询等API请求
 * 作者：帅姐姐
 * 创建日期：2026-05-04
 */

import { apiFactory } from '@/services/core/apiService';
import { API_ENDPOINTS } from '@/constants/apiEndpoints';
import type { BuildEntry, BuildCreateDto, BuildUpdateDto } from '@/types/buildLibrary';

// 类型定义
export interface BuildParseRequest {
  bd_code: string;
  include_icons: boolean;
}

export interface BuildParseResponse {
  bd_code: string;
  profession_id: number;
  profession: string;
  profession_cn: string;
  specializations: Array<{
    id: number;
    name: string;
    name_cn: string;
    icon: string;
    is_elite: boolean;
    selected_traits: [number, number, number];
    traits: Array<{
      id: number;
      name: string;
      icon: string;
      description: string;
      is_selected: boolean;
    }>;
  }>;
  skills: {
    heal: {
      id: number;
      palette_id: number;
      name: string;
      name_cn: string;
      icon: string;
      description: string;
      slot: string;
      recharge: number;
    };
    utility: Array<{
      id: number;
      palette_id: number;
      name: string;
      name_cn: string;
      icon: string;
      description: string;
      slot: string;
      recharge: number;
    }>;
    elite: {
      id: number;
      palette_id: number;
      name: string;
      name_cn: string;
      icon: string;
      description: string;
      slot: string;
      recharge: number;
    };
  };
}

export interface BuildCompareRequest {
  build_ids: string[];
}

export interface BuildCompareResponse {
  builds: Array<{
    id: string;
    name: string;
    profession: string;
    stats: Record<string, number>;
  }>;
  differences: Array<{
    field: string;
    values: Record<string, any>;
  }>;
}

/**
 * Build API 服务类
 */
class BuildApiService {
  /**
   * 解析Build代码
   * @param buildCode Build代码字符串
   * @param includeIcons 是否包含图标数据
   */
  async parseBuildCode(buildCode: string, includeIcons: boolean = true): Promise<BuildParseResponse | null> {
    try {
      const response = await apiFactory.post<BuildParseResponse>(
        API_ENDPOINTS.BUILD.PARSE,
        { bd_code: buildCode, include_icons: includeIcons },
        { timeout: 30000 }
      );

      if (response.success && response.data) {
        return response.data;
      }

      console.warn('[BuildApi] 解析Build代码响应格式异常', response);
      return null;
    } catch (error) {
      console.error('[BuildApi] 解析Build代码失败', error);
      throw error;
    }
  }

  /**
   * 保存Build配置
   * @param buildData Build数据
   */
  async saveBuild(buildData: BuildCreateDto): Promise<BuildEntry | null> {
    try {
      const response = await apiFactory.post<BuildEntry>(
        API_ENDPOINTS.BUILD.BASE,
        buildData
      );

      if (response.success && response.data) {
        return response.data;
      }

      return null;
    } catch (error) {
      console.error('[BuildApi] 保存Build失败', error);
      throw error;
    }
  }

  /**
   * 获取Build列表
   * @param params 查询参数
   */
  async getBuildList(params?: {
    page?: number;
    pageSize?: number;
    profession?: string;
    role?: string;
    searchQuery?: string;
  }): Promise<{ items: BuildEntry[]; total: number; page: number; pageSize: number; totalPages: number } | null> {
    try {
      const response = await apiFactory.get<{
        items: BuildEntry[];
        total: number;
        page: number;
        pageSize: number;
        totalPages: number;
      }>(API_ENDPOINTS.BUILD.LIST, { params });

      if (response.success && response.data) {
        return response.data;
      }

      return null;
    } catch (error) {
      console.error('[BuildApi] 获取Build列表失败', error);
      throw error;
    }
  }

  /**
   * 获取Build详情
   * @param buildId Build ID
   */
  async getBuildDetail(buildId: string): Promise<BuildEntry | null> {
    try {
      const response = await apiFactory.get<BuildEntry>(
        API_ENDPOINTS.BUILD.DETAIL(buildId)
      );

      if (response.success && response.data) {
        return response.data;
      }

      return null;
    } catch (error) {
      console.error('[BuildApi] 获取Build详情失败', error);
      throw error;
    }
  }

  /**
   * 更新Build配置
   * @param buildId Build ID
   * @param buildData 更新数据
   */
  async updateBuild(buildId: string, buildData: BuildUpdateDto): Promise<BuildEntry | null> {
    try {
      const response = await apiFactory.put<BuildEntry>(
        API_ENDPOINTS.BUILD.DETAIL(buildId),
        buildData
      );

      if (response.success && response.data) {
        return response.data;
      }

      return null;
    } catch (error) {
      console.error('[BuildApi] 更新Build失败', error);
      throw error;
    }
  }

  /**
   * 删除Build配置
   * @param buildId Build ID
   */
  async deleteBuild(buildId: string): Promise<boolean> {
    try {
      const response = await apiFactory.delete(
        API_ENDPOINTS.BUILD.DETAIL(buildId)
      );

      return response.success;
    } catch (error) {
      console.error('[BuildApi] 删除Build失败', error);
      throw error;
    }
  }

  /**
   * 对比多个Build配置
   * @param buildIds Build ID数组
   */
  async compareBuilds(buildIds: string[]): Promise<BuildCompareResponse | null> {
    try {
      const response = await apiFactory.post<BuildCompareResponse>(
        API_ENDPOINTS.BUILD.COMPARE,
        { build_ids: buildIds }
      );

      if (response.success && response.data) {
        return response.data;
      }

      return null;
    } catch (error) {
      console.error('[BuildApi] 对比Build失败', error);
      throw error;
    }
  }

  /**
   * 导出Build配置
   * @param buildId Build ID
   */
  async exportBuild(buildId: string): Promise<Blob | null> {
    try {
      const response = await apiFactory.get(
        API_ENDPOINTS.BUILD.EXPORT(buildId),
        { responseType: 'blob' }
      );

      if (response.success && response.data) {
        return response.data as Blob;
      }

      return null;
    } catch (error) {
      console.error('[BuildApi] 导出Build失败', error);
      throw error;
    }
  }
}

// 导出单例实例
export default new BuildApiService();
export { BuildApiService };

// 类型已通过 interface 声明自动导出，无需重复 export type