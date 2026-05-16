/**
 * 字典功能API模块
 * 功能：提供字典数据的API调用封装，支持前后端缓存机制
 * 作者：帅姐姐
 * 创建日期：2026-04-30
 */

import { apiFactory } from '../core/apiService'
import { API_ENDPOINTS } from '@/config/apiEndpoints'

/**
 * 认证错误类型
 */
export interface AuthError {
  isAuthError: boolean
  code: number
  message: string
  isTokenExpired: boolean
}

/**
 * 字典选项接口 - 用于下拉选择等场景
 */
export interface DictOption {
  value: string
  label: string
  css_class?: string
  is_default: number
}

/**
 * 字典数据接口 - 完整的字典项信息
 */
export interface DictData {
  dict_code: number
  dict_type: string
  dict_label: string
  dict_value: string
  dict_sort: number
  data_type?: string
  css_class?: string
  list_class?: string
  is_default: number
  status: number
  remark?: string
}

/**
 * 字典类型接口 - 字典分组信息
 */
export interface DictType {
  dict_id: number
  dict_type: string
  dict_name: string
  status: number
  sort_order: number
  remark?: string
}

/**
 * 字典API响应结果
 */
export interface DictApiResponse<T = any> {
  success: boolean
  message: string
  data: T
  code: number
}

/**
 * 分页响应
 */
export interface PaginatedDictData {
  items: DictData[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

/**
 * 精英特长级联项
 */
export interface SpecCascadeItem {
  value: string
  label: string
  color: string
  role_type: string
}

/**
 * 职业级联数据
 */
export interface ProfessionCascade {
  value: string
  label: string
  color: string
  role_type: string
  elite_specs: SpecCascadeItem[]
}

/**
 * 检测是否为认证错误
 */
function isAuthError(error: any): error is AuthError {
  return error &&
    typeof error === 'object' &&
    'isAuthError' in error &&
    error.isAuthError === true
}

class DictionaryService {
  /**
   * 获取字典选项列表（最常用方法）
   * @param dictType 字典类型编码，如 'profession', 'role', 'specialization'
   * @returns Promise<DictOption[]> 下拉选项数据
   */
  async getOptions(dictType: string): Promise<DictOption[]> {
    try {
      const response = await apiFactory.get<DictOption[]>(
        API_ENDPOINTS.DICTIONARY.OPTIONS(dictType)
      )
      if (response.success && response.data) {
        return response.data as DictOption[]
      }
      console.warn(`[DictionaryService] 获取字典选项失败: ${dictType}`, response.message)
      return []
    } catch (error) {
      if (isAuthError(error)) {
        console.error(`[DictionaryService] 认证失败: ${dictType}`, error.message)
        this.handleAuthError(error)
      } else {
        console.error(`[DictionaryService] 获取字典选项异常: ${dictType}`, error)
      }
      return []
    }
  }

  /**
   * 获取字典数据列表
   * @param dictType 字典类型编码
   * @param page 页码
   * @param pageSize 每页数量
   * @param status 状态筛选
   * @returns Promise<PaginatedDictData>
   */
  async getData(
    dictType: string,
    page: number = 1,
    pageSize: number = 50,
    status?: number
  ): Promise<PaginatedDictData | null> {
    try {
      const params: any = { page, page_size: pageSize, dict_type: dictType }
      if (status !== undefined) params.status = status

      const response = await apiFactory.get<PaginatedDictData>(
        API_ENDPOINTS.DICTIONARY.DATA,
        { params }
      )
      if (response.success && response.data) {
        return response.data as PaginatedDictData
      }
      return null
    } catch (error) {
      if (isAuthError(error)) {
        console.error(`[DictionaryService] 认证失败: ${dictType}`, error.message)
        this.handleAuthError(error)
      } else {
        console.error(`[DictionaryService] 获取字典数据异常: ${dictType}`, error)
      }
      return null
    }
  }

  /**
   * 获取字典类型列表
   * @param page 页码
   * @param pageSize 每页数量
   * @param status 状态筛选
   * @param keyword 关键词搜索
   * @returns Promise<PaginatedDictType>
   */
  async getTypes(
    page: number = 1,
    pageSize: number = 20,
    status?: number,
    keyword?: string
  ): Promise<{ items: DictType[]; total: number; page: number; page_size: number; total_pages: number } | null> {
    try {
      const params: any = { page, page_size: pageSize }
      if (status !== undefined) params.status = status
      if (keyword) params.keyword = keyword

      const response = await apiFactory.get<any>(
        API_ENDPOINTS.DICTIONARY.TYPES,
        { params }
      )
      if (response.success && response.data) {
        return response.data as { items: DictType[]; total: number; page: number; page_size: number; total_pages: number }
      }
      return null
    } catch (error) {
      if (isAuthError(error)) {
        console.error('[DictionaryService] 认证失败: 获取字典类型列表', error.message)
        this.handleAuthError(error)
      } else {
        console.error('[DictionaryService] 获取字典类型异常', error)
      }
      return null
    }
  }

  /**
   * 获取所有启用的字典类型
   * @returns Promise<DictType[]>
   */
  async getAllTypes(): Promise<DictType[]> {
    try {
      const response = await apiFactory.get<DictType[]>(
        API_ENDPOINTS.DICTIONARY.TYPES_ALL
      )
      if (response.success && response.data) {
        return response.data as DictType[]
      }
      return []
    } catch (error) {
      if (isAuthError(error)) {
        console.error('[DictionaryService] 认证失败: 获取所有字典类型', error.message)
        this.handleAuthError(error)
      } else {
        console.error('[DictionaryService] 获取所有字典类型异常', error)
      }
      return []
    }
  }

  /**
   * 获取单个字典项详情
   * @param dictCode 字典项编码
   * @returns Promise<DictData | null>
   */
  async getDataByCode(dictCode: number): Promise<DictData | null> {
    try {
      const response = await apiFactory.get<DictData>(
        API_ENDPOINTS.DICTIONARY.DATA_DETAIL(dictCode)
      )
      if (response.success && response.data) {
        return response.data as DictData
      }
      return null
    } catch (error) {
      if (isAuthError(error)) {
        console.error(`[DictionaryService] 认证失败: 获取字典项 ${dictCode}`, error.message)
        this.handleAuthError(error)
      } else {
        console.error(`[DictionaryService] 获取字典项异常: ${dictCode}`, error)
      }
      return null
    }
  }

  /**
   * 值转标签
   * @param dictType 字典类型编码
   * @param value 字典值
   * @returns Promise<string> 标签名称
   */
  async getLabel(dictType: string, value: string): Promise<string> {
    const options = await this.getOptions(dictType)
    const option = options.find(opt => opt.value === value)
    return option ? option.label : value
  }

  /**
   * 标签转值
   * @param dictType 字典类型编码
   * @param label 字典标签
   * @returns Promise<string> 字典值
   */
  async getValue(dictType: string, label: string): Promise<string> {
    const options = await this.getOptions(dictType)
    const option = options.find(opt => opt.label === label)
    return option ? option.value : label
  }

  /**
   * 获取颜色值
   * @param dictType 字典类型编码
   * @param value 字典值
   * @returns Promise<string> CSS颜色值
   */
  async getColor(dictType: string, value: string): Promise<string> {
    const options = await this.getOptions(dictType)
    const option = options.find(opt => opt.value === value)
    return option?.css_class || '#6b7280'
  }

  /**
   * 刷新字典缓存
   * @returns Promise<boolean>
   */
  async reloadCache(): Promise<boolean> {
    try {
      const response = await apiFactory.post<DictApiResponse<any>>(
        API_ENDPOINTS.DICTIONARY.RELOAD_CACHE
      )
      return response.success
    } catch (error) {
      if (isAuthError(error)) {
        console.error('[DictionaryService] 认证失败: 刷新缓存', error.message)
        this.handleAuthError(error)
      } else {
        console.error('[DictionaryService] 刷新字典缓存异常', error)
      }
      return false
    }
  }

  /**
   * 获取职业-精英特长级联数据
   * @returns Promise<{ professions: ProfessionCascade[], count: number }>
   */
  async getProfessionSpecsCascade(): Promise<{ professions: ProfessionCascade[]; count: number } | null> {
    try {
      const response = await apiFactory.get<any>(
        API_ENDPOINTS.DICTIONARY.PROFESSION_SPECS_CASCADE
      )
      if (response.success && response.data) {
        return response.data as { professions: ProfessionCascade[]; count: number }
      }
      return null
    } catch (error) {
      console.error('[DictionaryService] 获取职业级联数据异常', error)
      return null
    }
  }

  /**
   * 初始化字典数据（仅管理员）
   * @returns Promise<boolean>
   */
  async init(): Promise<boolean> {
    try {
      const response = await apiFactory.post<DictApiResponse<any>>(
        API_ENDPOINTS.DICTIONARY.INIT
      )
      return response.success
    } catch (error) {
      if (isAuthError(error)) {
        console.error('[DictionaryService] 认证失败: 初始化字典', error.message)
        this.handleAuthError(error)
      } else {
        console.error('[DictionaryService] 初始化字典数据异常', error)
      }
      return false
    }
  }

  /**
   * 创建字典类型
   * @param data 字典类型数据
   * @returns Promise<DictType | null>
   */
  async createDictType(data: {
    dict_type: string
    dict_name: string
    sort_order?: number
    status?: number
    remark?: string
  }): Promise<DictType | null> {
    try {
      const response = await apiFactory.post<DictType>(
        API_ENDPOINTS.DICTIONARY.TYPES,
        data
      )
      if (response.success && response.data) {
        return response.data as DictType
      }
      return null
    } catch (error) {
      if (isAuthError(error)) {
        console.error('[DictionaryService] 认证失败: 创建字典类型', error.message)
        this.handleAuthError(error)
      } else {
        console.error('[DictionaryService] 创建字典类型异常', error)
      }
      return null
    }
  }

  /**
   * 更新字典类型
   * @param dictId 字典类型ID
   * @param data 更新数据
   * @returns Promise<DictType | null>
   */
  async updateDictType(
    dictId: number,
    data: {
      dict_name?: string
      sort_order?: number
      status?: number
      remark?: string
    }
  ): Promise<DictType | null> {
    try {
      const response = await apiFactory.put<DictType>(
        API_ENDPOINTS.DICTIONARY.TYPE_DETAIL(dictId),
        data
      )
      if (response.success && response.data) {
        return response.data as DictType
      }
      return null
    } catch (error) {
      if (isAuthError(error)) {
        console.error(`[DictionaryService] 认证失败: 更新字典类型 ${dictId}`, error.message)
        this.handleAuthError(error)
      } else {
        console.error(`[DictionaryService] 更新字典类型异常: ${dictId}`, error)
      }
      return null
    }
  }

  /**
   * 删除字典类型
   * @param dictId 字典类型ID
   * @returns Promise<boolean>
   */
  async deleteDictType(dictId: number): Promise<boolean> {
    try {
      const response = await apiFactory.delete<DictApiResponse<any>>(
        API_ENDPOINTS.DICTIONARY.TYPE_DETAIL(dictId)
      )
      return response.success
    } catch (error) {
      if (isAuthError(error)) {
        console.error(`[DictionaryService] 认证失败: 删除字典类型 ${dictId}`, error.message)
        this.handleAuthError(error)
      } else {
        console.error(`[DictionaryService] 删除字典类型异常: ${dictId}`, error)
      }
      return false
    }
  }

  /**
   * 创建字典项
   * @param data 字典项数据
   * @returns Promise<DictData | null>
   */
  async createDataItem(data: {
    dict_type: string
    dict_label: string
    dict_value: string
    dict_sort?: number
    css_class?: string
    list_class?: string
    is_default?: number
    status?: number
    remark?: string
  }): Promise<DictData | null> {
    try {
      const response = await apiFactory.post<DictData>(
        API_ENDPOINTS.DICTIONARY.DATA,
        data
      )
      if (response.success && response.data) {
        return response.data as DictData
      }
      return null
    } catch (error) {
      if (isAuthError(error)) {
        console.error('[DictionaryService] 认证失败: 创建字典项', error.message)
        this.handleAuthError(error)
      } else {
        console.error('[DictionaryService] 创建字典项异常', error)
      }
      return null
    }
  }

  /**
   * 更新字典项
   * @param dictCode 字典项编码
   * @param data 更新数据
   * @returns Promise<DictData | null>
   */
  async updateDataItem(
    dictCode: number,
    data: {
      dict_label?: string
      dict_value?: string
      dict_sort?: number
      css_class?: string
      list_class?: string
      is_default?: number
      status?: number
      remark?: string
    }
  ): Promise<DictData | null> {
    try {
      const response = await apiFactory.put<DictData>(
        API_ENDPOINTS.DICTIONARY.DATA_DETAIL(dictCode),
        data
      )
      if (response.success && response.data) {
        return response.data as DictData
      }
      return null
    } catch (error) {
      if (isAuthError(error)) {
        console.error(`[DictionaryService] 认证失败: 更新字典项 ${dictCode}`, error.message)
        this.handleAuthError(error)
      } else {
        console.error(`[DictionaryService] 更新字典项异常: ${dictCode}`, error)
      }
      return null
    }
  }

  /**
   * 删除字典项
   * @param dictCode 字典项编码
   * @returns Promise<boolean>
   */
  async deleteDataItem(dictCode: number): Promise<boolean> {
    try {
      const response = await apiFactory.delete<DictApiResponse<any>>(
        API_ENDPOINTS.DICTIONARY.DATA_DETAIL(dictCode)
      )
      return response.success
    } catch (error) {
      if (isAuthError(error)) {
        console.error(`[DictionaryService] 认证失败: 删除字典项 ${dictCode}`, error.message)
        this.handleAuthError(error)
      } else {
        console.error(`[DictionaryService] 删除字典项异常: ${dictCode}`, error)
      }
      return false
    }
  }

  /**
   * 处理认证错误
   * @param error 认证错误对象
   */
  private handleAuthError(error: AuthError): void {
    const isTokenExpired = error.message.includes('过期') ||
                          error.message.includes('expired') ||
                          error.message.includes('token')

    if (isTokenExpired) {
      console.warn('[DictionaryService] 认证令牌可能已过期，请重新登录')
      window.dispatchEvent(new CustomEvent('auth:token-expired', {
        detail: { message: error.message }
      }))
    } else {
      console.warn('[DictionaryService] 认证失败，可能没有权限访问此资源')
      window.dispatchEvent(new CustomEvent('auth:failed', {
        detail: { message: error.message }
      }))
    }
  }
}

export const dictionaryService = new DictionaryService()
export default dictionaryService