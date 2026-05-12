import { apiFactory } from '../core/apiService'
import { API_ENDPOINTS } from '@/config/apiEndpoints'
import type { ApiResponse } from '@/types/api'

export interface SettingsUpdate {
  theme?: string
  language?: string
  timezone?: string
  [key: string]: any
}

// 配置项元数据（用于 allConfigs 表格展示）
const CONFIG_METADATA: Record<string, { config_name: string; config_type: string; remark: string }> = {
  theme: { config_name: '界面主题', config_type: 'N', remark: '系统界面主题模式' },
  default_server: { config_name: '默认服务器', config_type: 'N', remark: '新建日志时默认选中的服务器' },
  parse_parallel: { config_name: '解析并行数', config_type: 'N', remark: '批量解析时的并行任务数' },
  export_format: { config_name: '导出格式', config_type: 'N', remark: '数据导出默认格式' },
  auto_backup: { config_name: '自动备份', config_type: 'Y', remark: '是否启用自动数据库备份' },
  retention_days: { config_name: '数据保留天数', config_type: 'N', remark: '日志数据自动清理保留天数' },
  scoring_mode: { config_name: '评分模式', config_type: 'N', remark: 'role_based=按角色定位评分, profession_based=按职业评分' },
  watermark_enabled: { config_name: '水印启用', config_type: 'Y', remark: '是否启用水印功能' },
  watermark_text: { config_name: '水印文字', config_type: 'N', remark: '水印显示的文字内容' },
  watermark_screenshot_enabled: { config_name: '截图水印', config_type: 'Y', remark: '截图时是否添加水印' },
  // 新增配置项
  upload_max_file_size: { config_name: '最大上传文件大小', config_type: 'N', remark: '单位：MB' },
  upload_allowed_extensions: { config_name: '允许上传的文件扩展名', config_type: 'N', remark: 'JSON数组格式，如[".zevtc", ".evtc"]' },
  analysis_max_fight_duration: { config_name: '最大战斗时长', config_type: 'N', remark: '单位：秒' },
  cache_menu_ttl: { config_name: '菜单缓存时长', config_type: 'N', remark: '单位：秒' },
  auto_cleanup_enabled: { config_name: '自动清理', config_type: 'Y', remark: '是否启用日志自动清理' },
  auto_cleanup_retention_days: { config_name: '自动清理保留天数', config_type: 'N', remark: '自动清理时保留的日志天数' },
}

export class SettingsService {
  async getSettings(): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(API_ENDPOINTS.SETTINGS.GET)
  }

  async updateSettings(data: SettingsUpdate): Promise<ApiResponse<any>> {
    return apiFactory.put<any>(API_ENDPOINTS.SETTINGS.UPDATE, data)
  }

  async resetSettings(): Promise<ApiResponse<any>> {
    return apiFactory.post<any>(API_ENDPOINTS.SETTINGS.RESET)
  }

  /**
   * 获取系统配置数组（适配 SystemParamsSettings 组件）
   * 将扁平对象转换为配置项数组格式
   */
  async getSystemSettings(): Promise<any[]> {
    const res = await this.getSettings()
    if (res.code !== 200 || !res.data) {
      throw new Error(res.message || '获取系统配置失败')
    }

    const data = res.data
    const configs: any[] = []

    for (const [key, meta] of Object.entries(CONFIG_METADATA)) {
      configs.push({
        config_key: key,
        config_value: data[key] !== undefined ? String(data[key]) : '',
        config_name: meta.config_name,
        config_type: meta.config_type,
        remark: meta.remark,
      })
    }

    return configs
  }

  /**
   * 更新单个系统配置
   */
  async updateSystemSetting(key: string, value: any): Promise<ApiResponse<any>> {
    return this.updateSettings({ [key]: value })
  }
}

export const settingsService = new SettingsService()
