/**
 * CaseConverter 单元测试
 *
 * 测试内容：
 * - snake_case 转 CamelCase 字符串
 * - CamelCase 转 snake_case 字符串
 * - PascalCase 与 camelCase 互转
 * - 对象属性名递归转换（snake_case ↔ CamelCase）
 * - CaseConverter 类的链式调用
 * - 边界条件处理（空值、特殊字符、嵌套对象/数组）
 *
 * 作者：System
 * 创建日期：2026-05-05
 */

import {
  snakeToCamel,
  camelToSnake,
  pascalToCamel,
  camelToPascal,
  convertKeysToCamelCase,
  convertKeysToSnakeCase,
  CaseConverter,
} from '../caseConverter'

// ============================================================
// 1. snakeToCamel 测试
// ============================================================
describe('snakeToCamel', () => {
  it('应正确转换标准 snake_case 字符串', () => {
    expect(snakeToCamel('hello_world')).toBe('helloWorld')
    expect(snakeToCamel('user_name')).toBe('userName')
    expect(snakeToCamel('fight_stats')).toBe('fightStats')
  })

  it('应正确处理多段下划线', () => {
    expect(snakeToCamel('user_name_id')).toBe('userNameId')
    expect(snakeToCamel('a_b_c_d')).toBe('aBCD')
    expect(snakeToCamel('condition_cleanses_ally')).toBe('conditionCleansesAlly')
  })

  it('应保留已经是 CamelCase 的字符串', () => {
    expect(snakeToCamel('alreadyCamel')).toBe('alreadyCamel')
    expect(snakeToCamel('helloWorld')).toBe('helloWorld')
  })

  it('应正确处理纯大写缩写', () => {
    expect(snakeToCamel('user_id')).toBe('userId')
    expect(snakeToCamel('api_key')).toBe('apiKey')
    expect(snakeToCamel('http_url')).toBe('httpUrl')
  })

  it('应正确处理边界条件', () => {
    expect(snakeToCamel('')).toBe('')
    expect(snakeToCamel('a')).toBe('a')
    expect(snakeToCamel('_')).toBe('_')
    expect(snakeToCamel('__')).toBe('__')
    expect(snakeToCamel('_leading')).toBe('Leading')
    expect(snakeToCamel('trailing_')).toBe('trailing_')
  })

  it('应正确处理非字符串输入', () => {
    expect(snakeToCamel(null as any)).toBe(null)
    expect(snakeToCamel(undefined as any)).toBe(undefined)
    expect(snakeToCamel(123 as any)).toBe(123)
  })

  it('应正确处理包含数字的字符串', () => {
    expect(snakeToCamel('user_123')).toBe('user123')
    expect(snakeToCamel('v2_api')).toBe('v2Api')
    expect(snakeToCamel('build_2026_05')).toBe('build202605')
  })
})

// ============================================================
// 2. camelToSnake 测试
// ============================================================
describe('camelToSnake', () => {
  it('应正确转换标准 CamelCase 字符串', () => {
    expect(camelToSnake('helloWorld')).toBe('hello_world')
    expect(camelToSnake('userName')).toBe('user_name')
    expect(camelToSnake('fightStats')).toBe('fight_stats')
  })

  it('应正确处理连续大写字母（缩写）', () => {
    // 连续大写字母会被逐个处理
    expect(camelToSnake('userID')).toBe('user_i_d')
    expect(camelToSnake('URLParser')).toBe('u_r_l_parser')
    expect(camelToSnake('HTTPURL')).toBe('h_t_t_p_u_r_l')
  })

  it('应保留已经是 snake_case 的字符串', () => {
    expect(camelToSnake('already_snake')).toBe('already_snake')
    expect(camelToSnake('hello_world')).toBe('hello_world')
  })

  it('应正确处理首字母大写（PascalCase）', () => {
    expect(camelToSnake('HelloWorld')).toBe('hello_world')
    expect(camelToSnake('UserName')).toBe('user_name')
    expect(camelToSnake('FightStats')).toBe('fight_stats')
  })

  it('应正确处理边界条件', () => {
    expect(camelToSnake('')).toBe('')
    expect(camelToSnake('a')).toBe('a')
    expect(camelToSnake('A')).toBe('a')
  })

  it('应正确处理非字符串输入', () => {
    expect(camelToSnake(null as any)).toBe(null)
    expect(camelToSnake(undefined as any)).toBe(undefined)
    expect(camelToSnake(123 as any)).toBe(123)
  })

  it('应正确处理包含数字的字符串', () => {
    expect(camelToSnake('user123')).toBe('user123')
    expect(camelToSnake('v2Api')).toBe('v2_api')
    expect(camelToSnake('apiV2')).toBe('api_v2')
  })
})

// ============================================================
// 3. pascalToCamel / camelToPascal 测试
// ============================================================
describe('pascalToCamel', () => {
  it('应正确将 PascalCase 转为 camelCase', () => {
    expect(pascalToCamel('HelloWorld')).toBe('helloWorld')
    expect(pascalToCamel('UserName')).toBe('userName')
    expect(pascalToCamel('FightStats')).toBe('fightStats')
  })

  it('应正确处理已经是 camelCase 的字符串', () => {
    expect(pascalToCamel('helloWorld')).toBe('helloWorld')
  })

  it('应正确处理边界条件', () => {
    expect(pascalToCamel('')).toBe('')
    expect(pascalToCamel('A')).toBe('a')
  })
})

describe('camelToPascal', () => {
  it('应正确将 camelCase 转为 PascalCase', () => {
    expect(camelToPascal('helloWorld')).toBe('HelloWorld')
    expect(camelToPascal('userName')).toBe('UserName')
    expect(camelToPascal('fightStats')).toBe('FightStats')
  })

  it('应正确处理已经是 PascalCase 的字符串', () => {
    expect(camelToPascal('HelloWorld')).toBe('HelloWorld')
  })

  it('应正确处理边界条件', () => {
    expect(camelToPascal('')).toBe('')
    expect(camelToPascal('a')).toBe('A')
  })
})

// ============================================================
// 4. convertKeysToCamelCase 测试
// ============================================================
describe('convertKeysToCamelCase (对象递归转换)', () => {
  it('应正确转换单层对象', () => {
    const input = { user_name: 'Tom', user_age: 20 }
    const expected = { userName: 'Tom', userAge: 20 }
    expect(convertKeysToCamelCase(input)).toEqual(expected)
  })

  it('应正确转换嵌套对象', () => {
    const input = {
      fight_stats: {
        player_count: 50,
        total_damage: 1000000,
      },
    }
    const expected = {
      fightStats: {
        playerCount: 50,
        totalDamage: 1000000,
      },
    }
    expect(convertKeysToCamelCase(input)).toEqual(expected)
  })

  it('应正确转换包含数组的对象', () => {
    const input = {
      player_list: [
        { account_name: 'user1', character_name: 'Char1' },
        { account_name: 'user2', character_name: 'Char2' },
      ],
    }
    const expected = {
      playerList: [
        { accountName: 'user1', characterName: 'Char1' },
        { accountName: 'user2', characterName: 'Char2' },
      ],
    }
    expect(convertKeysToCamelCase(input)).toEqual(expected)
  })

  it('应正确处理 null 和 undefined', () => {
    expect(convertKeysToCamelCase(null)).toBe(null)
    expect(convertKeysToCamelCase(undefined)).toBe(undefined)
  })

  it('应正确处理基本类型', () => {
    expect(convertKeysToCamelCase('string')).toBe('string')
    expect(convertKeysToCamelCase(123)).toBe(123)
    expect(convertKeysToCamelCase(true)).toBe(true)
  })

  it('应正确处理空对象和空数组', () => {
    expect(convertKeysToCamelCase({})).toEqual({})
    expect(convertKeysToCamelCase([])).toEqual([])
  })

  it('应保留已经是 CamelCase 的键', () => {
    const input = { userName: 'Tom', user_age: 20 }
    const expected = { userName: 'Tom', userAge: 20 }
    expect(convertKeysToCamelCase(input)).toEqual(expected)
  })
})

// ============================================================
// 5. convertKeysToSnakeCase 测试
// ============================================================
describe('convertKeysToSnakeCase (对象递归转换)', () => {
  it('应正确转换单层对象', () => {
    const input = { userName: 'Tom', userAge: 20 }
    const expected = { user_name: 'Tom', user_age: 20 }
    expect(convertKeysToSnakeCase(input)).toEqual(expected)
  })

  it('应正确转换嵌套对象', () => {
    const input = {
      fightStats: {
        playerCount: 50,
        totalDamage: 1000000,
      },
    }
    const expected = {
      fight_stats: {
        player_count: 50,
        total_damage: 1000000,
      },
    }
    expect(convertKeysToSnakeCase(input)).toEqual(expected)
  })

  it('应正确转换包含数组的对象', () => {
    const input = {
      playerList: [
        { accountName: 'user1', characterName: 'Char1' },
        { accountName: 'user2', characterName: 'Char2' },
      ],
    }
    const expected = {
      player_list: [
        { account_name: 'user1', character_name: 'Char1' },
        { account_name: 'user2', character_name: 'Char2' },
      ],
    }
    expect(convertKeysToSnakeCase(input)).toEqual(expected)
  })

  it('应正确处理 null 和 undefined', () => {
    expect(convertKeysToSnakeCase(null)).toBe(null)
    expect(convertKeysToSnakeCase(undefined)).toBe(undefined)
  })

  it('应正确处理基本类型', () => {
    expect(convertKeysToSnakeCase('string')).toBe('string')
    expect(convertKeysToSnakeCase(123)).toBe(123)
    expect(convertKeysToSnakeCase(true)).toBe(true)
  })

  it('应正确处理空对象和空数组', () => {
    expect(convertKeysToSnakeCase({})).toEqual({})
    expect(convertKeysToSnakeCase([])).toEqual([])
  })

  it('应保留已经是 snake_case 的键', () => {
    const input = { user_name: 'Tom', userAge: 20 }
    const expected = { user_name: 'Tom', user_age: 20 }
    expect(convertKeysToSnakeCase(input)).toEqual(expected)
  })
})

// ============================================================
// 6. CaseConverter 类测试
// ============================================================
describe('CaseConverter 类', () => {
  it('应支持链式调用转换为 CamelCase', () => {
    const input = { user_name: 'Tom', fight_stats: { player_count: 5 } }
    const result = CaseConverter.of(input).toCamelCase().getValue()
    expect(result).toEqual({ userName: 'Tom', fightStats: { playerCount: 5 } })
  })

  it('应支持链式调用转换为 snake_case', () => {
    const input = { userName: 'Tom', fightStats: { playerCount: 5 } }
    const result = CaseConverter.of(input).toSnakeCase().getValue()
    expect(result).toEqual({ user_name: 'Tom', fight_stats: { player_count: 5 } })
  })

  it('应支持双向链式转换', () => {
    const input = { user_name: 'Tom' }
    const result = CaseConverter.of(input).toCamelCase().toSnakeCase().getValue()
    expect(result).toEqual({ user_name: 'Tom' })
  })

  it('应支持泛型类型推断', () => {
    interface User { user_name: string }
    interface UserCamel { userName: string }
    const input: User = { user_name: 'Tom' }
    const result = CaseConverter.of(input).toCamelCase().getValue<UserCamel>()
    expect(result.userName).toBe('Tom')
  })
})

// ============================================================
// 7. 互逆性测试
// ============================================================
describe('互逆性测试（双向转换一致性）', () => {
  it('snake_case → CamelCase → snake_case 应保持一致', () => {
    const original = {
      account_name: 'Player',
      character_name: 'Hero',
      group_id: 1,
      has_commander_tag: true,
      condition_cleanses: 42,
      boon_strips_ally: 10,
    }
    const camel = convertKeysToCamelCase(original)
    const backToSnake = convertKeysToSnakeCase(camel)
    expect(backToSnake).toEqual(original)
  })

  it('CamelCase → snake_case → CamelCase 应保持一致', () => {
    const original = {
      accountName: 'Player',
      characterName: 'Hero',
      groupId: 1,
      hasCommanderTag: true,
    }
    const snake = convertKeysToSnakeCase(original)
    const backToCamel = convertKeysToCamelCase(snake)
    expect(backToCamel).toEqual(original)
  })
})
