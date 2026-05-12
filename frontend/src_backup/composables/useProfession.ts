/**
 * 职业数据响应式管理 Composable
 * 功能：提供职业数据的便捷访问，直接代理 professionService
 * 作者：System
 * 创建日期：2026-05-12
 */

import professionService from '@/services/professionService'

export function useProfession() {
  return {
    loadProfessionData: professionService.loadAllData,
    isLoaded: () => professionService.isLoaded,
    professions: professionService.professions,
    eliteSpecs: professionService.eliteSpecs,
  }
}

export function useProfessionHelpers() {
  return {
    getProfessionName: professionService.getProfessionName,
    getProfessionColor: professionService.getProfessionColor,
    getProfessionIconUrl: professionService.getProfessionIconUrl,
    loadProfessionData: professionService.loadAllData,
  }
}

export default useProfession
