/**
 * Token 管理器单元测试
 *
 * 测试内容：
 * - Token 保存和读取
 * - Token 过期检查
 * - Token 清除
 * - Token 即将过期检查
 * - 剩余时间计算
 *
 * 作者：System
 * 创建日期：2026-05-04
 */

import {
  saveToken,
  getToken,
  clearToken,
  isLoggedIn,
  getTokenRemainingSeconds,
  isTokenExpiringSoon,
  getToken as getTokenInfo,
  type LoginResponse
} from '../tokenManager'

// 模拟 localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {}
  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => { store[key] = value },
    removeItem: (key: string) => { delete store[key] },
    clear: () => { store = {} },
    get length() { return Object.keys(store).length },
    key: (i: number) => Object.keys(store)[i] || null
  }
})()

// 替换全局 localStorage
Object.defineProperty(window, 'localStorage', { value: localStorageMock })

// 模拟登录响应
const mockLoginResponse: LoginResponse = {
  access_token: 'test_token_123',
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

describe('TokenManager', () => {

  beforeEach(() => {
    localStorage.clear()
  })

  describe('saveToken', () => {
    it('应该正确保存 Token 和过期时间', () => {
      saveToken(mockLoginResponse)

      const token = getToken()
      expect(token).not.toBeNull()
      expect(token?.accessToken).toBe(mockLoginResponse.access_token)

      // 验证过期时间被正确保存
      const expiryStored = localStorage.getItem('gw2_admin_token_expiry')
      expect(expiryStored).not.toBeNull()
      const expiry = parseInt(expiryStored!, 10)
      expect(expiry).toBeGreaterThan(Date.now())
      expect(expiry).toBeLessThanOrEqual(Date.now() + mockLoginResponse.expires_in * 1000)
    })

    it('应该正确计算过期时间戳', () => {
      const beforeSave = Date.now()
      saveToken(mockLoginResponse)
      const afterSave = Date.now()

      const expiryStored = localStorage.getItem('gw2_admin_token_expiry')
      const expiry = parseInt(expiryStored!, 10)

      expect(expiry).toBeGreaterThanOrEqual(beforeSave + mockLoginResponse.expires_in * 1000)
      expect(expiry).toBeLessThanOrEqual(afterSave + mockLoginResponse.expires_in * 1000)
    })
  })

  describe('getToken', () => {
    it('应该返回 null 当没有存储 Token', () => {
      const token = getToken()
      expect(token).toBeNull()
    })

    it('应该返回 null 当 Token 已过期', () => {
      // 手动设置一个已过期的时间（1秒前）
      const pastTime = Date.now() - 1000
      localStorage.setItem('gw2_admin_access_token', 'expired_token')
      localStorage.setItem('gw2_admin_token_expiry', pastTime.toString())

      const token = getToken()
      expect(token).toBeNull()

      // 验证过期Token已被清除
      expect(localStorage.getItem('gw2_admin_access_token')).toBeNull()
    })

    it('应该返回正确的 Token 信息当 Token 有效', () => {
      saveToken(mockLoginResponse)
      const token = getToken()

      expect(token).not.toBeNull()
      expect(token?.accessToken).toBe(mockLoginResponse.access_token)
      expect(token?.expiresIn).toBeGreaterThan(0)
      expect(token?.expiresAt).toBeGreaterThan(Date.now())
    })

    it('应该返回 null 当只有 accessToken 没有过期时间', () => {
      localStorage.setItem('gw2_admin_access_token', 'some_token')
      // 没有设置过期时间

      const token = getToken()
      expect(token).toBeNull()
    })

    it('应该返回 null 当只有过期时间没有 accessToken', () => {
      localStorage.setItem('gw2_admin_token_expiry', (Date.now() + 7200000).toString())
      // 没有设置 accessToken

      const token = getToken()
      expect(token).toBeNull()
    })
  })

  describe('isLoggedIn', () => {
    it('应该返回 false 当没有 Token', () => {
      expect(isLoggedIn()).toBe(false)
    })

    it('应该返回 true 当有有效 Token', () => {
      saveToken(mockLoginResponse)
      expect(isLoggedIn()).toBe(true)
    })

    it('应该返回 false 当 Token 已过期', () => {
      const pastTime = Date.now() - 1000
      localStorage.setItem('gw2_admin_access_token', 'expired_token')
      localStorage.setItem('gw2_admin_token_expiry', pastTime.toString())

      expect(isLoggedIn()).toBe(false)
    })
  })

  describe('clearToken', () => {
    it('应该清除所有 Token 相关数据', () => {
      saveToken(mockLoginResponse)
      expect(isLoggedIn()).toBe(true)

      clearToken()
      expect(isLoggedIn()).toBe(false)
      expect(localStorage.getItem('gw2_admin_access_token')).toBeNull()
      expect(localStorage.getItem('gw2_admin_token_expiry')).toBeNull()
    })

    it('应该能够清除不存在的 Token', () => {
      // 不应该抛出错误
      clearToken()
      expect(isLoggedIn()).toBe(false)
    })
  })

  describe('getTokenRemainingSeconds', () => {
    it('应该返回 0 当没有 Token', () => {
      expect(getTokenRemainingSeconds()).toBe(0)
    })

    it('应该返回正确的剩余秒数', () => {
      saveToken(mockLoginResponse)
      const remaining = getTokenRemainingSeconds()

      // 应该在 7195-7200 秒之间（允许一些误差）
      expect(remaining).toBeGreaterThanOrEqual(7195)
      expect(remaining).toBeLessThanOrEqual(7200)
    })

    it('应该返回 0 当 Token 已过期', () => {
      const pastTime = Date.now() - 1000
      localStorage.setItem('gw2_admin_access_token', 'expired_token')
      localStorage.setItem('gw2_admin_token_expiry', pastTime.toString())

      expect(getTokenRemainingSeconds()).toBe(0)
    })
  })

  describe('isTokenExpiringSoon', () => {
    it('应该返回 true 当没有 Token', () => {
      expect(isTokenExpiringSoon()).toBe(true)
    })

    it('应该返回 false 当 Token 还有充足时间（超过30分钟）', () => {
      // 设置过期时间为 60 分钟后
      const futureTime = Date.now() + 60 * 60 * 1000
      localStorage.setItem('gw2_admin_access_token', 'some_token')
      localStorage.setItem('gw2_admin_token_expiry', futureTime.toString())

      expect(isTokenExpiringSoon()).toBe(false)
    })

    it('应该返回 true 当 Token 在 30 分钟内过期', () => {
      // 设置过期时间为 20 分钟后
      const futureTime = Date.now() + 20 * 60 * 1000
      localStorage.setItem('gw2_admin_access_token', 'some_token')
      localStorage.setItem('gw2_admin_token_expiry', futureTime.toString())

      expect(isTokenExpiringSoon()).toBe(true)
    })

    it('应该返回 true 当 Token 已经过期', () => {
      const pastTime = Date.now() - 1000
      localStorage.setItem('gw2_admin_access_token', 'expired_token')
      localStorage.setItem('gw2_admin_token_expiry', pastTime.toString())

      expect(isTokenExpiringSoon()).toBe(true)
    })
  })

  describe('边界条件测试', () => {
    it('应该处理极短的 Token 有效期（1秒）', () => {
      const shortExpiryResponse = {
        ...mockLoginResponse,
        expires_in: 1
      }
      saveToken(shortExpiryResponse)

      // 立即获取应该还有时间
      let remaining = getTokenRemainingSeconds()
      expect(remaining).toBeGreaterThanOrEqual(0)
      expect(remaining).toBeLessThanOrEqual(1)

      // 等待 2 秒后应该过期
      return new Promise(resolve => {
        setTimeout(() => {
          expect(getTokenRemainingSeconds()).toBe(0)
          expect(isLoggedIn()).toBe(false)
          resolve()
        }, 2100)
      })
    })

    it('应该处理极长的 Token 有效期（30天）', () => {
      const longExpiryResponse = {
        ...mockLoginResponse,
        expires_in: 30 * 24 * 60 * 60 // 30天
      }
      saveToken(longExpiryResponse)

      const remaining = getTokenRemainingSeconds()
      expect(remaining).toBe(30 * 24 * 60 * 60)
      expect(isLoggedIn()).toBe(true)
      expect(isTokenExpiringSoon()).toBe(false)
    })

    it('应该正确处理 localStorage 异常', () => {
      // 模拟 localStorage 读取错误
      const originalGetItem = localStorage.getItem
      localStorage.getItem = () => { throw new Error('Storage error') }

      expect(() => getToken()).toThrow('Storage error')

      // 恢复
      localStorage.getItem = originalGetItem
    })
  })
})

// 运行测试
console.log('Running TokenManager tests...')
