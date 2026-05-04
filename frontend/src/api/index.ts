/**
 * API 模块统一导出
 * 作者：帅姐姐
 * 创建日期：2024-01-15
 */

export * from './combat/logs'
export { default as logsApi } from './combat/logs'

export * from './data/attendance'
export { default as attendanceApi } from './data/attendance'

export { default as buildApi } from './build/build'

export * from './data/dashboard'
export { default as dashboardApi } from './data/dashboard'

export { default as skillsApi } from './build/skills'

export * from './ai/ai'
export { default as aiApi } from './ai/ai'

export * from './combat/fights'
export { default as fightsApi } from './combat/fights'

export * from './system/dictionary'
export { default as dictionaryApi } from './system/dictionary'
