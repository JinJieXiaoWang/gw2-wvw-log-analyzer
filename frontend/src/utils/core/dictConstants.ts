/**
 * 字典模块常量
 * 注意：本文件用于字典管理模块自身的表单配置
 */

import { NormalDisable } from '@/constants/dictValues'

const ENABLED = parseInt(NormalDisable.ENABLED, 10)
const DISABLED = parseInt(NormalDisable.DISABLED, 10)

export const STATUS_OPTIONS = [
  { label: '全部', value: null },
  { label: '启用', value: ENABLED },
  { label: '禁用', value: DISABLED }
]

export const EMPTY_DATA_FORM = {
  dict_label: '',
  dict_value: '',
  dict_sort: 0,
  css_class: '',
  list_class: '',
  status: ENABLED,
  remark: ''
}

export const EMPTY_TYPE_FORM = {
  dict_name: '',
  dict_type: '',
  sort_order: 0,
  status: ENABLED,
  remark: ''
}
