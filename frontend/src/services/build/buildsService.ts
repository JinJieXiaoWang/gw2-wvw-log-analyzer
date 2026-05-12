import { apiFactory } from '../core/apiService'
import { API_ENDPOINTS } from '@/config/apiEndpoints'
import type { ApiResponse } from '@/types/api'

export interface BuildsListParams {
  page?: number
  page_size?: number
  profession?: string | null
  member_id?: number | null
}

/** Build图书馆列表查询参数 */
export interface BuildLibraryListParams {
  page?: number
  page_size?: number
  profession?: string | null
  role?: string | null
  sub_role?: string | null
  search?: string | null
  sort_by?: string
}

export interface BuildCreate {
  name: string
  profession: string
  build_code: string
  description?: string
}

export interface BuildUpdate {
  name?: string
  build_code?: string
  description?: string
}

/** Build图书馆创建/更新请求体（snake_case，与后端对齐） */
export interface BuildLibraryCreateRequest {
  title: string
  profession: string
  profession_color?: string | null
  elite_spec?: string | null
  role: 'dps' | 'support'
  sub_roles?: string[]
  armor_type?: string | null
  weapons?: { set: number; name: string; sigils: string[] }[]
  relic?: string | null
  rune?: string | null
  food?: string | null
  wrench?: string | null
  infusion?: string | null
  attr_requirements?: string[]
  bd_code: string
  trait_lines?: { name: string; choices: number[] }[]
  rotation_commands?: { callout: string; action: string; note?: string }[]
  mechanics?: { name: string; sources: string[] }[]
  videos?: { title: string; url: string; author?: string }[]
  author?: string
  is_meta?: boolean
}

export type BuildLibraryUpdateRequest = Partial<BuildLibraryCreateRequest>

export class BuildsService {
  async getBuilds(params: BuildsListParams): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(API_ENDPOINTS.BUILD.LIST, { params })
  }

  async createBuild(data: BuildCreate): Promise<ApiResponse<any>> {
    return apiFactory.post<any>(API_ENDPOINTS.BUILD.LIST, data)
  }

  async parseBuild(buildCode: string): Promise<ApiResponse<any>> {
    return apiFactory.post<any>(API_ENDPOINTS.BUILD.SAVE, null, {
      params: { build_code: buildCode }
    })
  }

  async compareBuilds(buildId1: number, buildId2: number): Promise<ApiResponse<any>> {
    return apiFactory.post<any>(API_ENDPOINTS.BUILD.COMPARE, null, {
      params: { build_id_1: buildId1, build_id_2: buildId2 }
    })
  }

  async getBuild(buildId: number): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(API_ENDPOINTS.BUILD.DETAIL(buildId))
  }

  async updateBuild(buildId: number, data: BuildUpdate): Promise<ApiResponse<void>> {
    return apiFactory.put<void>(API_ENDPOINTS.BUILD.DETAIL(buildId), data)
  }

  async deleteBuild(buildId: number): Promise<ApiResponse<void>> {
    return apiFactory.delete<void>(API_ENDPOINTS.BUILD.DETAIL(buildId))
  }

  /** Build图书馆：获取列表 */
  async getBuildLibraryList(params: BuildLibraryListParams = {}): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(API_ENDPOINTS.BUILD.LIST, { params })
  }

  /** Build图书馆：获取详情 */
  async getBuildLibraryDetail(buildId: number): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(API_ENDPOINTS.BUILD.DETAIL(buildId))
  }

  /** Build图书馆：创建 */
  async createBuildLibrary(data: BuildLibraryCreateRequest): Promise<ApiResponse<any>> {
    return apiFactory.post<any>(API_ENDPOINTS.BUILD.LIST, data)
  }

  /** Build图书馆：更新 */
  async updateBuildLibrary(buildId: number, data: BuildLibraryUpdateRequest): Promise<ApiResponse<any>> {
    return apiFactory.put<any>(API_ENDPOINTS.BUILD.DETAIL(buildId), data)
  }

  /** Build图书馆：删除 */
  async deleteBuildLibrary(buildId: number): Promise<ApiResponse<void>> {
    return apiFactory.delete<void>(API_ENDPOINTS.BUILD.DETAIL(buildId))
  }
}

export const buildsService = new BuildsService()