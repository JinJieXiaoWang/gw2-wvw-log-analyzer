/**
 * 设置页面常量定义
 * 集中管理设置相关的硬编码配置数据
 */

/** 设置侧边栏导航项 */
export const SETTING_SECTIONS = [
  { id: 'account', label: '账号设置', icon: 'pi pi-user' },
  { id: 'parsing', label: '解析参数', icon: 'pi pi-sliders-h' },
  { id: 'export', label: '导出格式', icon: 'pi pi-file-export' },
  { id: 'theme', label: '界面主题', icon: 'pi pi-palette' },
  { id: 'notifications', label: '通知设置', icon: 'pi pi-bell' },
  { id: 'scoring-rules', label: '评分规则', icon: 'pi pi-chart-line', isExternal: true, path: '/scoring-rules' },
  { id: 'profession-mgmt', label: '职业管理', icon: 'pi pi-users', isExternal: true, path: '/professions' },
  { id: 'system-params', label: '系统参数', icon: 'pi pi-database' },
  { id: 'dictionary', label: '字典管理', icon: 'pi pi-book' },
  { id: 'security', label: '安全设置', icon: 'pi pi-shield' },
  { id: 'watermark', label: '水印设置', icon: 'pi pi-circle-on' }
]

/** 导出格式选项 */
export const EXPORT_FORMAT_OPTIONS = [
  { id: 'csv', label: 'CSV', icon: 'pi pi-file', color: '#00B42A' },
  { id: 'excel', label: 'Excel', icon: 'pi pi-file-excel', color: '#00B42A' },
  { id: 'json', label: 'JSON', icon: 'pi pi-code', color: '#165DFF' },
  { id: 'pdf', label: 'PDF', icon: 'pi pi-file-pdf', color: '#F53F3F' }
]

/** 主题颜色选项 */
export const THEME_COLOR_OPTIONS = [
  { id: 'blue', value: '#165DFF' },
  { id: 'purple', value: '#722ED1' },
  { id: 'green', value: '#00B42A' },
  { id: 'orange', value: '#FF7D00' },
  { id: 'red', value: '#F53F3F' }
]

/** 数字格式选项 */
export const NUMBER_FORMAT_OPTIONS = [
  { label: '自动', value: 'auto' },
  { label: '千位分隔符 (1,000)', value: 'comma' },
  { label: '科学计数法 (1.0e6)', value: 'scientific' }
]

/** 评分模式选项 */
export const SCORING_MODE_OPTIONS = [
  { label: '角色定位评分', value: 'role_based' },
  { label: '职业评分', value: 'profession_based' }
]

/** 数据导出格式选项 */
export const EXPORT_FORMAT_SELECT_OPTIONS = [
  { label: 'JSON', value: 'json' },
  { label: 'CSV', value: 'csv' },
  { label: 'Excel', value: 'xlsx' }
]

/** 系统参数本地配置默认值 */
export const SYSTEM_CONFIG_DEFAULTS = {
  scoring_mode: 'role_based',
  default_server: 'Tarnished Coast',
  parse_parallel: 1,
  retention_days: 365,
  export_format: 'json',
  auto_backup: true,
  upload_max_file_size: 50,
  upload_allowed_extensions: '[".zevtc", ".evtc"]',
  analysis_max_fight_duration: 3600,
  cache_menu_ttl: 3600,
  auto_cleanup_enabled: true,
  auto_cleanup_retention_days: 30
}

/** 账号设置默认值 */
export const ACCOUNT_SETTINGS_DEFAULTS = {
  username: '',
  email: '',
  bio: ''
}

/** 解析参数设置默认值 */
export const PARSING_SETTINGS_DEFAULTS = {
  includeOverkill: true,
  ignoreSmallDamage: true,
  preFightBuffer: 5,
  autoCategorizeSkills: true
}

/** 导出设置默认值 */
export const EXPORT_SETTINGS_DEFAULTS = {
  defaultFormat: 'csv',
  includeHeader: true,
  utf8Encoding: true,
  numberFormat: 'auto'
}

/** 主题设置默认值 */
export const THEME_SETTINGS_DEFAULTS = {
  mode: 'dark',
  primaryColor: '#165DFF',
  zoom: 100
}

/** 通知设置默认值 */
export const NOTIFICATION_SETTINGS_DEFAULTS = {
  email: true,
  push: false,
  parseComplete: true
}

/** 安全设置默认值 */
export const SECURITY_SETTINGS_DEFAULTS = {
  twoFactorAuth: false
}

/** 系统参数中需要转换为数值的键 */
export const NUMERIC_CONFIG_KEYS = [
  'parse_parallel',
  'retention_days',
  'upload_max_file_size',
  'analysis_max_fight_duration',
  'cache_menu_ttl',
  'auto_cleanup_retention_days'
]

/** 系统参数中需要转换为布尔值的键 */
export const BOOLEAN_CONFIG_KEYS = ['auto_backup', 'auto_cleanup_enabled']
