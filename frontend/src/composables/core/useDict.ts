/**
 * useDict - 字典数据管理组合式函数
 * 功能：批量并行加载字典，自动读写 Pinia Store 缓存
 * 设计理念：借鉴若依(RuoYi) useDict，支持一次性加载多个字典类型
 * 作者：系统
 * 创建日期：2026-05-07
 *
 * 使用示例：
 *   const { role, gameMode, dictLoading } = useDict('role', 'game_mode')
 *   const label = dictStore.getDictLabel('role', 'dps') // -> '输出'
 *   const color = dictStore.getDictColor('role', 'dps') // -> '#FF6B35'
 */

import { ref, computed, toRefs, type ToRefs, type ComputedRef } from 'vue'
import { storeToRefs } from 'pinia'
import { useDictStore, type DictItem } from '@/store/system/dict'

/**
 * useDict 返回类型
 */
export type UseDictResult<T extends string = string> = ToRefs<Record<T, DictItem[]>> & {
  dictLoading: ComputedRef<boolean>
  dictReady: ComputedRef<boolean>
}

/**
 * 批量加载字典数据
 * @param args 一个或多个字典类型编码
 * @returns 响应式字典数据 + 加载状态
 *
 * 示例：
 *   const { role, scoringDimension, dictLoading } = useDict('role', 'scoring_dimension')
 *   // role.value -> [{label:'输出', value:'dps', css_class:'#FF6B35'}, ...]
 *   // dictLoading.value -> true/false
 */
export function useDict<T extends string>(...args: T[]): UseDictResult<T> {
  const dictStore = useDictStore()
  const { loadingTypes } = storeToRefs(dictStore)

  // 需要加载的字典类型
  const targetTypes = args.filter((t) => !!t)

  // 加载完成标记
  const internalReady = ref(false)

  // 响应式字典对象
  const dictObject = ref<Record<T, DictItem[]>>({} as Record<T, DictItem[]>)

  // 初始化每个字典类型为空数组
  targetTypes.forEach((type) => {
    dictObject.value[type] = []
  })

  // 计算是否正在加载
  const dictLoading = computed(() => {
    return targetTypes.some((type) => loadingTypes.value.has(type))
  })

  // 计算是否全部就绪
  const dictReady = computed(() => {
    return targetTypes.every((type) => {
      const cached = dictStore.getDict(type)
      return cached && cached.length > 0
    })
  })

  // 加载逻辑
  async function doLoad() {
    const promises: Promise<void>[] = []

    targetTypes.forEach((type) => {
      // 检查 Store 缓存
      const cached = dictStore.getDict(type)
      if (cached && cached.length > 0) {
        dictObject.value[type] = cached
        promises.push(Promise.resolve())
        return
      }

      // 从 API 加载
      const p = dictStore.loadDict(type).then((data) => {
        dictObject.value[type] = data
      })
      promises.push(p)
    })

    await Promise.all(promises)
    internalReady.value = true
  }

  // 立即执行加载
  doLoad()

  // 将响应式对象转为独立 ref
  const refs = toRefs(dictObject.value)

  return {
    ...refs,
    dictLoading,
    dictReady,
  } as UseDictResult<T>
}

/**
 * useDictAsync - 异步版 useDict，支持 await 等待加载完成
 * @param args 一个或多个字典类型编码
 * @returns Promise<UseDictResult>
 */
export async function useDictAsync<T extends string>(...args: T[]): Promise<UseDictResult<T>> {
  const result = useDict(...args)
  // 等待加载完成
  const maxWait = 100 // 最多等待 10 秒
  for (let i = 0; i < maxWait; i++) {
    if (!result.dictLoading.value) break
    await new Promise((r) => setTimeout(r, 100))
  }
  return result
}
