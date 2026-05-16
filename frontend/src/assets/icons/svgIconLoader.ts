/**
 * SVG图标加载器配置
 * 功能：配置vite-plugin-svg-icons插件，统一管理所有SVG图标资源
 * 作者：System
 * 创建日期：2026-05-11
 * 
 * 使用说明：
 * 1. 在vite.config.ts中引入本配置
 * 2. 在main.ts中调用install方法
 * 3. 在组件中使用<SvgIcon name="图标名" />
 */

import { createSvgIconsPlugin } from 'vite-plugin-svg-icons'
import path from 'path'

/**
 * SVG图标插件配置
 * 自动扫描指定目录下的所有SVG文件
 */
export const svgIconsPlugin = createSvgIconsPlugin({
  // 指定需要缓存的图标文件夹
  iconDirs: [
    path.resolve(process.cwd(), 'src/assets/icons/ui'),
    path.resolve(process.cwd(), 'src/assets/icons/combat'),
    path.resolve(process.cwd(), 'src/assets/icons/status'),
    path.resolve(process.cwd(), 'src/assets/icons/profession'),
    path.resolve(process.cwd(), 'src/assets/icons/buff'),
    path.resolve(process.cwd(), 'src/assets/icons/decor')
  ],
  // 指定symbolId格式
  symbolId: 'icon-[dir]-[name]',
  // SVG压缩配置
  svgoOptions: {
    plugins: [
      // 移除fill属性，允许CSS控制颜色
      {
        name: 'removeAttrs',
        params: {
          attrs: ['fill', 'fill-rule']
        }
      },
      // 移除不必要的XML声明
      {
        name: 'removeXMLNS'
      },
      // 移除注释
      {
        name: 'removeComments'
      },
      // 移除多余的空属性
      {
        name: 'removeEmptyAttrs'
      },
      // 合并路径
      {
        name: 'mergePaths'
      }
    ]
  }
})

/**
 * 根据分类和名称获取图标ID
 */
export function getIconSymbolId(category: string, name: string): string {
  return `icon-${category}-${name}`
}

/**
 * 获取SVG图标的完整URL
 */
export function getIconUrl(category: string, name: string): string {
  return `#icon-${category}-${name}`
}
