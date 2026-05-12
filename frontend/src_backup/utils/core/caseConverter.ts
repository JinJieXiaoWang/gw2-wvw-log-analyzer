/**
 * 大小写转换工具类
 * 功能：提供 snake_case 与 CamelCase 的相互转换功能
 * 支持：字符串转换、对象属性名递归转换
 * 作者：System
 * 创建日期：2026-05-05
 */

/**
 * 将 snake_case 字符串转换为 CamelCase 字符串
 * @param str snake_case 格式字符串
 * @returns CamelCase 格式字符串
 * @example
 * snakeToCamel('hello_world') // 'helloWorld'
 * snakeToCamel('user_name_id') // 'userNameId'
 * snakeToCamel('alreadyCamel') // 'alreadyCamel'
 */
export function snakeToCamel(str: string): string {
  if (!str || typeof str !== 'string') {
    return str
  }
  return str.replace(/_([a-zA-Z0-9])/g, (_, char) => char.toUpperCase())
}

/**
 * 将 CamelCase 字符串转换为 snake_case 字符串
 * @param str CamelCase 格式字符串
 * @returns snake_case 格式字符串
 * @example
 * camelToSnake('helloWorld') // 'hello_world'
 * camelToSnake('userNameID') // 'user_name_i_d'
 * camelToSnake('already_snake') // 'already_snake'
 */
export function camelToSnake(str: string): string {
  if (!str || typeof str !== 'string') {
    return str
  }
  // 如果已经是全小写（无大写字母），直接返回，避免 user123 → user_123
  if (!/[A-Z]/.test(str)) {
    return str
  }
  // 处理连续大写字母以及普通驼峰（如 Name → _name）
  // 注意：数字边界不插入下划线（v2Api → v2_api 而非 v_2_api）
  return str
    .replace(/([A-Z])/g, (_, char, offset) =>
      offset === 0 ? char.toLowerCase() : `_${char.toLowerCase()}`
    )
}

/**
 * 将 PascalCase 字符串转换为 camelCase 字符串
 * @param str PascalCase 格式字符串
 * @returns camelCase 格式字符串（首字母小写）
 * @example
 * pascalToCamel('HelloWorld') // 'helloWorld'
 */
export function pascalToCamel(str: string): string {
  if (!str || typeof str !== 'string') {
    return str
  }
  return str.charAt(0).toLowerCase() + str.slice(1)
}

/**
 * 将 camelCase 字符串转换为 PascalCase 字符串
 * @param str camelCase 格式字符串
 * @returns PascalCase 格式字符串（首字母大写）
 * @example
 * camelToPascal('helloWorld') // 'HelloWorld'
 */
export function camelToPascal(str: string): string {
  if (!str || typeof str !== 'string') {
    return str
  }
  return str.charAt(0).toUpperCase() + str.slice(1)
}

/**
 * 递归将对象中的所有属性名从 snake_case 转换为 CamelCase
 * @param obj 任意类型的值（对象、数组、基本类型）
 * @returns 转换后的值
 * @example
 * convertKeysToCamelCase({ user_name: 'Tom', user_age: 20 })
 * // { userName: 'Tom', userAge: 20 }
 */
export function convertKeysToCamelCase(obj: any): any {
  if (obj === null || typeof obj !== 'object') {
    return obj
  }
  if (Array.isArray(obj)) {
    return obj.map((item) => convertKeysToCamelCase(item))
  }
  const result: Record<string, any> = {}
  for (const key in obj) {
    if (Object.prototype.hasOwnProperty.call(obj, key)) {
      const newKey = snakeToCamel(key)
      result[newKey] = convertKeysToCamelCase(obj[key])
    }
  }
  return result
}

/**
 * 递归将对象中的所有属性名从 CamelCase 转换为 snake_case
 * @param obj 任意类型的值（对象、数组、基本类型）
 * @returns 转换后的值
 * @example
 * convertKeysToSnakeCase({ userName: 'Tom', userAge: 20 })
 * // { user_name: 'Tom', user_age: 20 }
 */
export function convertKeysToSnakeCase(obj: any): any {
  if (obj === null || typeof obj !== 'object') {
    return obj
  }
  if (Array.isArray(obj)) {
    return obj.map((item) => convertKeysToSnakeCase(item))
  }
  const result: Record<string, any> = {}
  for (const key in obj) {
    if (Object.prototype.hasOwnProperty.call(obj, key)) {
      const newKey = camelToSnake(key)
      result[newKey] = convertKeysToSnakeCase(obj[key])
    }
  }
  return result
}

/**
 * 大小写转换器类（面向对象封装）
 * 提供链式调用和批量转换能力
 */
export class CaseConverter {
  private value: any

  constructor(value: any) {
    this.value = value
  }

  /**
   * 创建转换器实例（静态工厂方法）
   */
  static of(value: any): CaseConverter {
    return new CaseConverter(value)
  }

  /**
   * 将当前值中的属性名全部转换为 CamelCase
   */
  toCamelCase(): CaseConverter {
    this.value = convertKeysToCamelCase(this.value)
    return this
  }

  /**
   * 将当前值中的属性名全部转换为 snake_case
   */
  toSnakeCase(): CaseConverter {
    this.value = convertKeysToSnakeCase(this.value)
    return this
  }

  /**
   * 获取转换后的值
   */
  getValue<T = any>(): T {
    return this.value as T
  }
}
