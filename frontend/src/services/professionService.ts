/**
 * 职业数据服务
 * 功能：统一管理职业、精英特长、角色定位数据
 * 作者：System
 */

import { apiFactory } from './core/apiService'

export interface RoleType {
  id: number
  role_key: string
  role_name: string
  color: string
  icon: string
  sort_order: number
}

export interface EliteSpecialization {
  id: number
  spec_key: string
  spec_name: string
  spec_name_en: string
  profession_key: string
  color: string
  icon: string
  default_role: string
  dps_type: 'power' | 'condi' | 'hybrid' | null
  scoring_config: Record<string, number>
  is_key_support: boolean
  is_active: boolean
  sort_order: number
}

export interface Profession {
  id: number
  profession_key: string
  profession_name: string
  name?: string
  profession_name_en: string
  color: string
  icon: string
  default_role: string
  possible_roles: string[]
  is_active: boolean
  sort_order: number
  elite_specializations?: EliteSpecialization[]
  elite_specs?: any[]
}

export interface ProfessionCascade {
  value: string
  label: string
  color: string
  elite_specs: Array<{
    value: string
    label: string
    color: string
  }>
}

export interface RoleProfessionMapping {
  [role: string]: Array<{
    profession: string
    profession_name: string
    color: string
    elite_specs: string[]
  }>
}

const API_PREFIX = '/api/v1/professions'

// 缓存数据
let roleTypesCache: RoleType[] = []
let professionsCache: Profession[] = []
let eliteSpecsCache: EliteSpecialization[] = []
let professionCascadeCache: ProfessionCascade[] = []
let roleMappingCache: RoleProfessionMapping = {}
let isLoaded = false
let loadPromise: Promise<void> | null = null

/**
 * 提取 API 响应数据（处理不同的响应格式）
 */
function extractApiData<T>(response: any): T {
  if (response && response.data) {
    // 处理 { data: { data: T } } 格式
    if (response.data.data !== undefined) {
      return response.data.data as T
    }
    // 处理 { data: T } 格式
    return response.data as T
  }
  return {} as T
}

/**
 * 提取包含列表的数据（处理带 totals 的响应）
 */
function extractListData<T>(response: any, key: string): T[] {
  const data = extractApiData(response)
  if (data && typeof data === 'object' && key in data) {
    return (data as Record<string, T[]>)[key]
  }
  return Array.isArray(data) ? data : []
}

/**
 * 触发数据加载（异步，不阻塞）
 */
function triggerLoadData(): void {
  if (isLoaded || loadPromise) return
  loadPromise = loadAllData().finally(() => {
    loadPromise = null
  })
}

/**
 * 加载所有职业数据
 */
export async function loadAllData(force = false): Promise<void> {
  if (isLoaded && !force) {
    return
  }

  try {
    const [roleTypesRes, professionsRes, eliteSpecsRes, cascadeRes, mappingRes] = await Promise.all([
      apiFactory.get<{ data: RoleType[] }>(`${API_PREFIX}/role-types`),
      apiFactory.get<{ data: { professions: Profession[] } }>(`${API_PREFIX}`, { params: { include_specs: true } }),
      apiFactory.get<{ data: { elite_specs: EliteSpecialization[] } }>(`${API_PREFIX}/elite-specs`),
      apiFactory.get<{ data: ProfessionCascade[] }>(`${API_PREFIX}/cascade`),
      apiFactory.get<{ data: RoleProfessionMapping }>(`${API_PREFIX}/role-mapping`),
    ])

    roleTypesCache = extractApiData<RoleType[]>(roleTypesRes)
    professionsCache = extractListData<Profession>(professionsRes, 'professions')
    eliteSpecsCache = extractListData<EliteSpecialization>(eliteSpecsRes, 'elite_specs') || professionsCache.flatMap((p: Profession) => p.elite_specializations || [])
    professionCascadeCache = extractApiData<ProfessionCascade[]>(cascadeRes)
    roleMappingCache = extractApiData<RoleProfessionMapping>(mappingRes)
    isLoaded = true
  } catch (error) {
    console.error('加载职业数据失败:', error)
    throw error
  }
}

/**
 * 获取职业列表
 */
export async function getProfessions(includeSpecs = true): Promise<Profession[]> {
  if (!isLoaded) await loadAllData()
  return professionsCache
}

/**
 * 同步获取职业列表（返回缓存数据，不触发加载）
 */
export function getProfessionsSync(): Profession[] {
  return professionsCache
}

/**
 * 获取所有精英特长
 */
export async function getEliteSpecs(): Promise<EliteSpecialization[]> {
  if (!isLoaded) await loadAllData()
  return eliteSpecsCache
}

/**
 * 获取角色定位列表
 */
export async function getRoleTypes(): Promise<RoleType[]> {
  if (!isLoaded) await loadAllData()
  return roleTypesCache
}

/**
 * 获取职业详情（同步版本，直接从缓存获取）
 */
export function getProfession(professionKey: string): Profession | undefined {
  return professionsCache.find(p => p.profession_key === professionKey)
}

/**
 * 获取职业详情（异步版本，自动加载数据）
 */
export async function getProfessionAsync(professionKey: string): Promise<Profession | undefined> {
  if (!isLoaded) await loadAllData()
  return professionsCache.find(p => p.profession_key === professionKey)
}

/**
 * 获取职业中文名（支持基础职业和精英特长）
 */
export function getProfessionName(professionKey: string): string {
  if (!isLoaded) {
    triggerLoadData()
    return professionKey
  }
  
  const profession = getProfession(professionKey)
  if (profession) {
    return profession.profession_name
  }
  
  const spec = getEliteSpec(professionKey)
  if (spec) {
    return spec.spec_name
  }
  
  return professionKey
}

/**
 * 获取职业颜色（支持基础职业和精英特长）
 */
export function getProfessionColor(professionKey: string): string {
  // 如果缓存未加载，触发异步加载
  if (!isLoaded) {
    triggerLoadData()
    return Colors.palette.gray
  }
  
  // 先尝试查找基础职业
  const profession = getProfession(professionKey)
  if (profession && profession.color) {
    return profession.color
  }
  
  // 再尝试查找精英特长
  const spec = getEliteSpec(professionKey)
  if (spec && spec.color) {
    return spec.color
  }
  
  return Colors.palette.gray
}

/**
 * 获取职业图标URL（支持基础职业和精英特长）
 */
export function getProfessionIconUrl(professionKey: string): string {
  if (!isLoaded) {
    triggerLoadData()
    return ''
  }
  
  const profession = getProfession(professionKey)
  if (profession && profession.icon) {
    return `/images/prof/${profession.icon}`
  }
  
  const spec = getEliteSpec(professionKey)
  if (spec && spec.icon) {
    return `/images/prof/${spec.icon}`
  }
  
  return ''
}

/**
 * 获取精英特长图标URL
 */
export function getEliteSpecIconUrl(specKey: string): string {
  const spec = getEliteSpec(specKey)
  if (!spec || !spec.icon) {
    return ''
  }
  return `/images/prof/${spec.icon}`
}

/**
 * 获取职业或精英特长图标URL（通用函数）
 */
export function getIconUrl(key: string): string {
  // 先尝试查找职业
  const professionIcon = getProfessionIconUrl(key)
  if (professionIcon) {
    return professionIcon
  }
  
  // 再尝试查找精英特长
  const specIcon = getEliteSpecIconUrl(key)
  if (specIcon) {
    return specIcon
  }
  
  return ''
}

/**
 * 获取职业默认角色定位
 */
export function getProfessionDefaultRole(professionKey: string): string {
  const profession = getProfession(professionKey)
  return profession?.default_role || 'dps'
}

/**
 * 获取职业可能的角色定位
 */
export function getProfessionPossibleRoles(professionKey: string): string[] {
  const profession = getProfession(professionKey)
  return profession?.possible_roles || ['dps']
}

/**
 * 获取指定职业的精英特长
 */
export async function getSpecsByProfession(professionKey: string): Promise<EliteSpecialization[]> {
  if (!isLoaded) await loadAllData()
  return eliteSpecsCache.filter(s => s.profession_key === professionKey)
}

/**
 * 获取精英特长详情
 */
export function getEliteSpec(specKey: string): EliteSpecialization | undefined {
  return eliteSpecsCache.find(s => s.spec_key === specKey)
}

/**
 * 获取精英特长中文名
 */
export function getEliteSpecName(specKey: string): string {
  const spec = getEliteSpec(specKey)
  return spec?.spec_name || specKey
}

/**
 * 获取精英特长颜色
 */
export function getEliteSpecColor(specKey: string): string | undefined {
  const spec = getEliteSpec(specKey)
  return spec?.color
}

/**
 * 获取精英特长所属职业
 */
export function getEliteSpecProfession(specKey: string): string | undefined {
  const spec = getEliteSpec(specKey)
  return spec?.profession_key
}

/**
 * 获取精英特长默认角色定位
 */
export function getEliteSpecDefaultRole(specKey: string): string {
  const spec = getEliteSpec(specKey)
  return spec?.default_role || 'dps'
}

/**
 * 判断是否为关键辅助
 */
export function isKeySupport(specKey: string): boolean {
  const spec = getEliteSpec(specKey)
  return spec?.is_key_support || false
}

/**
 * 获取角色职业映射
 */
export async function getRoleProfessionMapping(): Promise<RoleProfessionMapping> {
  if (!isLoaded) await loadAllData()
  return roleMappingCache
}

/**
 * 获取职业级联数据
 */
export async function getProfessionCascade(): Promise<ProfessionCascade[]> {
  if (!isLoaded) await loadAllData()
  return professionCascadeCache
}

/**
 * 获取职业选项
 */
export async function getProfessionOptions(): Promise<Array<{ label: string; value: string }>> {
  if (!isLoaded) await loadAllData()
  return professionsCache.map(p => ({
    label: p.profession_name,
    value: p.profession_key,
  }))
}

/**
 * 获取精英特长选项
 */
export async function getEliteSpecOptions(professionKey?: string): Promise<Array<{ label: string; value: string }>> {
  if (!isLoaded) await loadAllData()
  let specs = eliteSpecsCache
  if (professionKey) {
    specs = specs.filter(s => s.profession_key === professionKey)
  }
  return specs.map(s => ({
    label: s.spec_name,
    value: s.spec_key,
  }))
}

/**
 * 获取角色定位选项
 */
export async function getRoleOptions(): Promise<Array<{ label: string; value: string }>> {
  if (!isLoaded) await loadAllData()
  return roleTypesCache.map(r => ({
    label: r.role_name,
    value: r.role_key,
  }))
}

/**
 * 根据职业或精英特长获取角色定位
 */
export function getRoleByProfessionOrSpec(professionKey: string, specKey?: string): string {
  if (specKey) {
    const specRole = getEliteSpecDefaultRole(specKey)
    if (specRole !== 'dps') {
      return specRole
    }
  }
  return getProfessionDefaultRole(professionKey)
}

/**
 * 清空缓存
 */
import { Colors } from '@/config/designTokens'
export function clearCache(): void {
  isLoaded = false
  roleTypesCache = []
  professionsCache = []
  eliteSpecsCache = []
  professionCascadeCache = []
  roleMappingCache = {}
}

// CRUD操作

export async function createProfession(data: Partial<Profession>): Promise<any> {
  const res = await apiFactory.post(`${API_PREFIX}/profession`, data)
  clearCache()
  return res.data
}

export async function updateProfession(professionKey: string, data: Partial<Profession>): Promise<any> {
  const res = await apiFactory.put(`${API_PREFIX}/profession/${professionKey}`, data)
  clearCache()
  return res.data
}

export async function deleteProfession(professionKey: string): Promise<any> {
  const res = await apiFactory.delete(`${API_PREFIX}/profession/${professionKey}`)
  clearCache()
  return res.data
}

export async function createEliteSpec(data: Partial<EliteSpecialization>): Promise<any> {
  const res = await apiFactory.post(`${API_PREFIX}/elite-spec`, data)
  clearCache()
  return res.data
}

export async function updateEliteSpec(specKey: string, data: Partial<EliteSpecialization>): Promise<any> {
  const res = await apiFactory.put(`${API_PREFIX}/elite-spec/${specKey}`, data)
  clearCache()
  return res.data
}

export async function deleteEliteSpec(specKey: string): Promise<any> {
  const res = await apiFactory.delete(`${API_PREFIX}/elite-spec/${specKey}`)
  clearCache()
  return res.data
}

export async function createRoleType(data: Partial<RoleType>): Promise<any> {
  const res = await apiFactory.post(`${API_PREFIX}/role-type`, data)
  clearCache()
  return res.data
}

export async function updateRoleType(roleKey: string, data: Partial<RoleType>): Promise<any> {
  const res = await apiFactory.put(`${API_PREFIX}/role-type/${roleKey}`, data)
  clearCache()
  return res.data
}

export async function deleteRoleType(roleKey: string): Promise<any> {
  const res = await apiFactory.delete(`${API_PREFIX}/role-type/${roleKey}`)
  clearCache()
  return res.data
}

export const professionService = {
  get isLoaded() { return isLoaded },
  loadAllData,
  getProfessions,
  getProfessionsSync,
  getEliteSpecs,
  getRoleTypes,
  getProfession,
  getEliteSpec,
  getRoleProfessionMapping,
  getProfessionCascade,
  getProfessionName,
  getProfessionColor,
  getProfessionIconUrl,
  getEliteSpecIconUrl,
  getIconUrl,
  getProfessionDefaultRole,
  getProfessionPossibleRoles,
  getEliteSpecName,
  getEliteSpecColor,
  getEliteSpecProfession,
  getEliteSpecDefaultRole,
  isKeySupport,
  getSpecsByProfession,
  getRoleByProfessionOrSpec,
  getProfessionOptions,
  getEliteSpecOptions,
  getRoleOptions,
  clearCache,
  createProfession,
  updateProfession,
  deleteProfession,
  createEliteSpec,
  updateEliteSpec,
  deleteEliteSpec,
  createRoleType,
  updateRoleType,
  deleteRoleType,
  roleTypes: roleTypesCache,
  get professions() { return professionsCache },
  get eliteSpecs() { return eliteSpecsCache },
}

export default professionService
