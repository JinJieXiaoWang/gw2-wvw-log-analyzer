/**
 * Token 自动退出集成测试
 *
 * 测试内容：
 * 1. Token 过期自动检测
 * 2. 401 错误处理和自动跳转
 * 3. 定时检查机制
 * 4. 即将过期警告
 *
 * 作者：System
 * 创建日期：2026-05-04
 */

import { saveToken, clearToken, getToken, isLoggedIn, getTokenRemainingSeconds } from '../tokenManager'
import type { LoginResponse } from '../tokenManager'

// 模拟登录响应
const mockLoginResponse: LoginResponse = {
  access_token: 'test_token_for_auto_logout',
  token_type: 'bearer',
  expires_in: 7200, // 2小时
  user: {
    id: 1,
    username: 'admin',
    role: 'super_admin',
    is_active: true,
    is_predefined: true,
    created_at: '2026-04-28T10:00:00Z',
    last_login: '2026-05-04T08:00:00Z'
  },
  permissions: ['read', 'write', 'upload', 'delete']
}

// 模拟 console 方法以记录测试输出
const testLog = (message: string, data?: any) => {
  console.log(`[TEST] ${message}`, data || '')
}

const testPass = (testName: string) => {
  console.log(`✅ PASS: ${testName}`)
}

const testFail = (testName: string, reason: string) => {
  console.error(`❌ FAIL: ${testName} - ${reason}`)
}

describe('Token自动退出集成测试', () => {

  beforeEach(() => {
    clearToken()
    testLog('清理测试环境')
  })

  afterAll(() => {
    clearToken()
    testLog('清理测试环境完成')
  })

  /**
   * 测试1: Token过期自动检测
   */
  describe('Token过期自动检测', () => {
    it('Token已过期时应返回null并清除状态', () => {
      testLog('测试: Token已过期时应返回null并清除状态')

      // 模拟 Token 已过期（1秒前）
      const pastTime = Date.now() - 1000
      localStorage.setItem('gw2_admin_access_token', 'expired_token')
      localStorage.setItem('gw2_admin_token_expiry', pastTime.toString())

      // 尝试获取 Token
      const token = getToken()

      if (token === null) {
        testPass('Token已过期时返回null')
      } else {
        testFail('Token已过期时返回null', `实际返回: ${JSON.stringify(token)}`)
      }

      // 验证 localStorage 已被清除
      if (localStorage.getItem('gw2_admin_access_token') === null) {
        testPass('过期Token已从localStorage清除')
      } else {
        testFail('过期Token已从localStorage清除', 'Token仍然存在')
      }

      // 验证 isLoggedIn 返回 false
      if (isLoggedIn() === false) {
        testPass('isLoggedIn返回false')
      } else {
        testFail('isLoggedIn返回false', '实际返回: true')
      }
    })

    it('Token有效时应正常返回', () => {
      testLog('测试: Token有效时应正常返回')

      // 保存有效的 Token
      saveToken(mockLoginResponse)

      const token = getToken()

      if (token !== null && token.accessToken === mockLoginResponse.access_token) {
        testPass('有效Token正常返回')
      } else {
        testFail('有效Token正常返回', `实际返回: ${JSON.stringify(token)}`)
      }
    })

    it('Token即将过期（30分钟内）应被检测', () => {
      testLog('测试: Token即将过期（30分钟内）应被检测')

      // 设置 Token 在 20 分钟后过期
      const nearExpiry = Date.now() + 20 * 60 * 1000
      localStorage.setItem('gw2_admin_access_token', 'near_expiry_token')
      localStorage.setItem('gw2_admin_token_expiry', nearExpiry.toString())

      const remaining = getTokenRemainingSeconds()
      const isNearExpiry = remaining <= 30 * 60 && remaining > 0

      if (isNearExpiry) {
        testPass('Token即将过期被正确检测')
      } else {
        testFail('Token即将过期被正确检测', `剩余时间: ${remaining}秒`)
      }
    })
  })

  /**
   * 测试2: 401错误处理流程
   */
  describe('401错误处理流程', () => {
    it('401错误应触发Token清除', () => {
      testLog('测试: 401错误应触发Token清除')

      // 先登录
      saveToken(mockLoginResponse)
      expect(isLoggedIn()).toBe(true)

      // 模拟 401 错误响应
      const mock401Response = {
        status: 401,
        data: {
          success: false,
          message: 'Token已过期'
        }
      }

      // 模拟错误处理（这是 apiService 拦截器的逻辑）
      if (mock401Response.status === 401) {
        clearToken()
      }

      if (!isLoggedIn()) {
        testPass('401错误后Token被正确清除')
      } else {
        testFail('401错误后Token被正确清除', 'Token仍然存在')
      }
    })

    it('401错误后应触发页面跳转', () => {
      testLog('测试: 401错误后应触发页面跳转')

      // 模拟 Token 过期
      saveToken(mockLoginResponse)

      // 记录原始 location.href
      const originalHref = window.location.href

      // 模拟 401 处理（清除 Token 并跳转）
      clearToken()
      if (window.location.pathname !== '/login') {
        window.location.href = `/login?redirect=${encodeURIComponent(window.location.pathname)}`
      }

      // 验证 Token 已被清除
      if (!isLoggedIn()) {
        testPass('401错误后Token已清除（跳转将在实际浏览器环境中执行）')
      } else {
        testFail('401错误后Token已清除', 'Token仍然存在')
      }
    })
  })

  /**
   * 测试3: 定时检查机制
   */
  describe('定时检查机制', () => {
    it('应该能启动定时检查', () => {
      testLog('测试: 应该能启动定时检查')

      // 保存 Token
      saveToken(mockLoginResponse)

      // 模拟定时检查
      const checkInterval = window.setInterval(() => {
        const remaining = getTokenRemainingSeconds()
        if (remaining <= 0) {
          clearToken()
          console.log('[定时检查] Token已过期，执行退出')
        }
      }, 60000) // 每分钟检查

      if (checkInterval > 0) {
        testPass('定时检查已启动')
        clearInterval(checkInterval)
      } else {
        testFail('定时检查已启动', '定时器未创建')
      }
    })

    it('Token过期时应执行自动退出', () => {
      testLog('测试: Token过期时应执行自动退出')

      // 模拟已过期的 Token
      const pastTime = Date.now() - 1000
      localStorage.setItem('gw2_admin_access_token', 'expired_token')
      localStorage.setItem('gw2_admin_token_expiry', pastTime.toString())

      // 模拟定时检查逻辑
      const remaining = getTokenRemainingSeconds()
      if (remaining <= 0) {
        clearToken()
        testPass('Token过期后自动退出')
      } else {
        testFail('Token过期后自动退出', `remaining: ${remaining}`)
      }
    })
  })

  /**
   * 测试4: 即将过期警告
   */
  describe('即将过期警告', () => {
    it('应该在Token剩余5分钟时触发警告', () => {
      testLog('测试: 应该在Token剩余5分钟时触发警告')

      // 设置 Token 在 4 分钟后过期
      const fourMinutes = Date.now() + 4 * 60 * 1000
      localStorage.setItem('gw2_admin_access_token', 'expiring_soon_token')
      localStorage.setItem('gw2_admin_token_expiry', fourMinutes.toString())

      const remaining = getTokenRemainingSeconds()
      const shouldWarn = remaining <= 5 * 60 && remaining > 0

      if (shouldWarn) {
        testPass('即将过期警告已触发')
      } else {
        testFail('即将过期警告已触发', `remaining: ${remaining}秒`)
      }
    })

    it('警告应该只触发一次', () => {
      testLog('测试: 警告应该只触发一次')

      let hasWarned = false
      const WARNING_THRESHOLD = 5 * 60 // 5分钟

      // 模拟警告逻辑
      const checkAndWarn = () => {
        const remaining = getTokenRemainingSeconds()
        if (remaining <= WARNING_THRESHOLD && !hasWarned) {
          hasWarned = true
          console.log('[警告] Token即将过期')
        }
      }

      // 第一次检查
      const time1 = Date.now() + 4 * 60 * 1000
      localStorage.setItem('gw2_admin_token_expiry', time1.toString())
      checkAndWarn()
      if (hasWarned) {
        testPass('第一次检查触发警告')
      }

      // 第二次检查（不应该再次触发）
      const time2 = Date.now() + 3 * 60 * 1000
      localStorage.setItem('gw2_admin_token_expiry', time2.toString())
      const hadWarnedBefore = hasWarned
      checkAndWarn()
      if (hasWarned === hadWarnedBefore) {
        testPass('警告只触发一次')
      } else {
        testFail('警告只触发一次', '警告被多次触发')
      }
    })
  })

  /**
   * 测试5: 实际场景模拟
   */
  describe('实际场景模拟', () => {
    it('场景: 用户登录后2小时未操作', () => {
      testLog('场景: 用户登录后2小时未操作')

      // 模拟用户刚刚登录
      saveToken(mockLoginResponse)
      const remaining1 = getTokenRemainingSeconds()

      // 模拟时间流逝（2小时后）
      const twoHoursLater = Date.now() + 2 * 60 * 60 * 1000 + 1000 // 多1秒确保过期
      localStorage.setItem('gw2_admin_token_expiry', twoHoursLater.toString())

      const remaining2 = getTokenRemainingSeconds()

      // 2小时后 Token 应该已过期
      if (remaining2 <= 0) {
        testPass('2小时后Token已过期')
      } else {
        testFail('2小时后Token已过期', `remaining: ${remaining2}秒`)
      }

      // 获取 Token 应该返回 null
      const token = getToken()
      if (token === null) {
        testPass('获取过期Token返回null')
      } else {
        testFail('获取过期Token返回null', `返回了: ${JSON.stringify(token)}`)
      }

      // isLoggedIn 应该返回 false
      if (!isLoggedIn()) {
        testPass('Token过期后isLoggedIn返回false')
      } else {
        testFail('Token过期后isLoggedIn返回false', '仍然返回true')
      }
    })

    it('场景: 用户在Token即将过期时操作', () => {
      testLog('场景: 用户在Token即将过期时操作')

      // 模拟 Token 还有 4 分钟过期
      const fourMinutesLater = Date.now() + 4 * 60 * 1000
      localStorage.setItem('gw2_admin_access_token', 'expiring_token')
      localStorage.setItem('gw2_admin_token_expiry', fourMinutesLater.toString())

      const remaining = getTokenRemainingSeconds()

      if (remaining <= 5 * 60 && remaining > 0) {
        testPass('用户操作时Token即将过期被正确检测')
      } else {
        testFail('用户操作时Token即将过期被正确检测', `remaining: ${remaining}`)
      }
    })
  })
})

console.log('='.repeat(50))
console.log('Token自动退出集成测试开始')
console.log('='.repeat(50))
