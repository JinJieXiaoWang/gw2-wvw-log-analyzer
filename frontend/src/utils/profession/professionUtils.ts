/**
 * 职业信息工具函数模块
 * 功能：提供职业名称、颜色、图标等信息的获取（简单代理）
 * 作者：System
 * 创建日期：2026-05-12
 * 说明：此文件为简单代理层，核心逻辑在 professionService
 */

import professionService from '@/services/professionService'

export const getProfessionName = professionService.getProfessionName
export const getProfessionColor = professionService.getProfessionColor
export const getProfessionIconUrl = professionService.getProfessionIconUrl
export const getIconUrl = professionService.getIconUrl
export const getProfession = professionService.getProfession
export const getEliteSpec = professionService.getEliteSpec

export async function initProfessionData(): Promise<void> {
  await professionService.loadAllData()
}
