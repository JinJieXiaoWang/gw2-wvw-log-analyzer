/**
 * 国际化配置模块
 * 功能：管理应用多语言支持
 * 作者：System
 * 创建日期：2024-01-15
 */

import { createI18n } from 'vue-i18n'
import zhCN from './zh-CN'
import enUS from './en-US'

const messages = {
  'zh-CN': zhCN,
  'en-US': enUS
}

const i18n = createI18n({
  legacy: false,
  locale: 'zh-CN',
  fallbackLocale: 'zh-CN',
  messages
})

export default i18n