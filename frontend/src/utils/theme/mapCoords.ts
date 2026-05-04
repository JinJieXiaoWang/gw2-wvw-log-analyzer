/**
 * WvW 地图坐标转换工具
 * 将 EVTC 导出的 map 坐标转换为 Canvas 归一化坐标 [0,1]
 *
 * 转换链路：
 *   map coordinate (EVTC)
 *   → continent coordinate (via map_rect / continent_rect)
 *   → z=6 pixel coordinate (continent / 2, since maxZoom=7)
 *   → normalized [0,1] (relative to stitched image)
 *
 * 参考：tests/gw2_wvw_maps/data/replay_config.json
 */

import mapConfigJson from '@/assets/images/maps/wvw_map_config.json'

// ============================================================
// 类型定义
// ============================================================

export interface MapCoord {
  x: number
  y: number
}

export interface MapConfig {
  name: string
  filename: string
  imageSize: number[]
  continentRect: number[][]
  mapRect: number[][]
  tileRange: {
    txMin: number
    txMax: number
    tyMin: number
    tyMax: number
  }
  imagePixelOrigin: number[]
}

export interface WvWMapConfig {
  zoom: number
  max_zoom: number
  tile_size: number
  maps: Record<string, MapConfig>
}

// ============================================================
// 配置数据
// ============================================================

const CONFIG = mapConfigJson as unknown as WvWMapConfig

const ZOOM_SCALE = 2 ** (CONFIG.max_zoom - CONFIG.zoom) // = 2 for zoom=6, maxZoom=7

// ============================================================
// 坐标转换函数
// ============================================================

/**
 * 将 map 坐标转换为 continent 坐标
 *
 * formula: continent = continent_rect_min + (map - map_rect_min) * continent_rect_size / map_rect_size
 */
export function mapToContinent(mapCoord: MapCoord, mapCfg: MapConfig): MapCoord {
  const cr = mapCfg.continentRect
  const mr = mapCfg.mapRect

  const crWidth = cr[1][0] - cr[0][0]
  const crHeight = cr[1][1] - cr[0][1]
  const mrWidth = mr[1][0] - mr[0][0]
  const mrHeight = mr[1][1] - mr[0][1]

  const x = cr[0][0] + (mapCoord.x - mr[0][0]) * (crWidth / mrWidth)
  const y = cr[0][1] + (mapCoord.y - mr[0][1]) * (crHeight / mrHeight)

  return { x, y }
}

/**
 * 将 continent 坐标转换为 map 坐标（反向）
 */
export function continentToMap(continentCoord: MapCoord, mapCfg: MapConfig): MapCoord {
  const cr = mapCfg.continentRect
  const mr = mapCfg.mapRect

  const crWidth = cr[1][0] - cr[0][0]
  const crHeight = cr[1][1] - cr[0][1]
  const mrWidth = mr[1][0] - mr[0][0]
  const mrHeight = mr[1][1] - mr[0][1]

  const x = mr[0][0] + (continentCoord.x - cr[0][0]) * (mrWidth / crWidth)
  const y = mr[0][1] + (continentCoord.y - cr[0][1]) * (mrHeight / crHeight)

  return { x, y }
}

/**
 * 将 continent 坐标转换为 z=6 像素坐标
 *
 * 在 Leaflet L.CRS.Simple + maxZoom=7 下：
 *   zoom 7 像素 = continent 坐标
 *   zoom 6 像素 = continent 坐标 / 2
 */
export function continentToPixel(continentCoord: MapCoord): MapCoord {
  return {
    x: continentCoord.x / ZOOM_SCALE,
    y: continentCoord.y / ZOOM_SCALE,
  }
}

/**
 * 将 z=6 像素坐标转换为 continent 坐标
 */
export function pixelToContinent(pixelCoord: MapCoord): MapCoord {
  return {
    x: pixelCoord.x * ZOOM_SCALE,
    y: pixelCoord.y * ZOOM_SCALE,
  }
}

/**
 * 将 z=6 像素坐标转换为拼接图上的归一化坐标 [0,1]
 *
 * 结果 [0,0] 对应拼接图左上角，[1,1] 对应右下角
 */
export function pixelToNormalized(
  pixelCoord: MapCoord,
  mapCfg: MapConfig
): MapCoord {
  const [originX, originY] = mapCfg.imagePixelOrigin
  const [imgWidth, imgHeight] = mapCfg.imageSize

  return {
    x: (pixelCoord.x - originX) / imgWidth,
    y: (pixelCoord.y - originY) / imgHeight,
  }
}

/**
 * 将归一化坐标 [0,1] 转换为 z=6 像素坐标
 */
export function normalizedToPixel(
  normCoord: MapCoord,
  mapCfg: MapConfig
): MapCoord {
  const [originX, originY] = mapCfg.imagePixelOrigin
  const [imgWidth, imgHeight] = mapCfg.imageSize

  return {
    x: normCoord.x * imgWidth + originX,
    y: normCoord.y * imgHeight + originY,
  }
}

/**
 * 完整的 map → normalized 转换（一步到位）
 */
export function mapToNormalized(
  mapCoord: MapCoord,
  mapCfg: MapConfig
): MapCoord {
  const continent = mapToContinent(mapCoord, mapCfg)
  const pixel = continentToPixel(continent)
  return pixelToNormalized(pixel, mapCfg)
}

/**
 * 完整的 normalized → map 转换（反向）
 */
export function normalizedToMap(
  normCoord: MapCoord,
  mapCfg: MapConfig
): MapCoord {
  const pixel = normalizedToPixel(normCoord, mapCfg)
  const continent = pixelToContinent(pixel)
  return continentToMap(continent, mapCfg)
}

// ============================================================
// 配置查询
// ============================================================

/**
 * 根据地图 ID 获取配置
 */
export function getMapConfig(mapId: number | string): MapConfig | undefined {
  return CONFIG.maps[String(mapId)]
}

/**
 * 获取所有可用的地图配置
 */
export function getAllMapConfigs(): Record<string, MapConfig> {
  return CONFIG.maps
}

/**
 * 获取地图图片的 URL（从 public 目录直接引用）
 */
export function getMapImageUrl(mapId: number | string): string {
  const cfg = getMapConfig(mapId)
  if (!cfg) return ''
  // 使用 public 目录下的绝对路径，避免 Vite new URL() 动态模板字符串的问题
  return `/images/maps/${cfg.filename}`
}

/**
 * 根据日志数据中的地图 ID 判断是否为 WvW 地图
 */
export function isWvWMap(mapId: number | string): boolean {
  return String(mapId) in CONFIG.maps
}

// ============================================================
// 实用工具：生成随机地图坐标（用于 mock / 演示）
// ============================================================

/**
 * 在指定地图的 map_rect 范围内生成随机坐标
 */
export function randomMapCoord(mapCfg: MapConfig): MapCoord {
  const mr = mapCfg.mapRect
  return {
    x: mr[0][0] + Math.random() * (mr[1][0] - mr[0][0]),
    y: mr[0][1] + Math.random() * (mr[1][1] - mr[0][1]),
  }
}

/**
 * 在指定地图的中心区域生成随机坐标（避免边缘）
 */
export function randomMapCoordNearCenter(mapCfg: MapConfig, radius = 0.3): MapCoord {
  const mr = mapCfg.mapRect
  const centerX = (mr[0][0] + mr[1][0]) / 2
  const centerY = (mr[0][1] + mr[1][1]) / 2
  const rangeX = (mr[1][0] - mr[0][0]) * radius
  const rangeY = (mr[1][1] - mr[0][1]) * radius

  return {
    x: centerX + (Math.random() - 0.5) * rangeX,
    y: centerY + (Math.random() - 0.5) * rangeY,
  }
}
