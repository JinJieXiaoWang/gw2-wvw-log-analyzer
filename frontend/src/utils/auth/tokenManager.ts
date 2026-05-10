/**
 * Token 管理工具模块
 *
 * 功能：
 * - 存储和读取访问令牌
 * - 检查令牌是否过期
 * - 自动刷新即将过期的令牌
 * - 处理令牌相关的错误
 *
 * 作者：帅妹妹丶.8297
 * 创建日期：2026-05-04
 */

const TOKEN_KEY = 'gw2_admin_access_token';
const TOKEN_EXPIRY_KEY = 'gw2_admin_token_expiry';
const LEGACY_TOKEN_KEY = 'gw2_wvw_token';
const REFRESH_THRESHOLD_MS = 30 * 60 * 1000; // 30分钟阈值

export interface TokenInfo {
  accessToken: string;
  expiresIn: number;
  expiresAt: number;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: {
    id: number;
    username: string;
    role: string;
    is_active: boolean;
    is_predefined: boolean;
    created_at: string;
    last_login: string;
  };
  permissions: string[];
}

/**
 * 保存原始 access token（用于不持有完整 LoginResponse 的场景）
 * @param accessToken 访问令牌
 * @param expiresInSeconds 过期秒数，默认24小时
 */
export function saveAccessToken(accessToken: string, expiresInSeconds: number = 2 * 60 * 60): void {
  const expiresAt = Date.now() + (expiresInSeconds * 1000);
  localStorage.setItem(TOKEN_KEY, accessToken);
  localStorage.setItem(TOKEN_EXPIRY_KEY, expiresAt.toString());
  console.log(`[TokenManager] Token saved, expires at: ${new Date(expiresAt).toLocaleString()}`);
}

/**
 * 保存登录响应中的 Token 信息
 * @param response 登录接口响应数据
 */
export function saveToken(response: LoginResponse): void {
  const expiresAt = Date.now() + (response.expires_in * 1000);

  localStorage.setItem(TOKEN_KEY, response.access_token);
  localStorage.setItem(TOKEN_EXPIRY_KEY, expiresAt.toString());

  console.log(`[TokenManager] Token saved, expires at: ${new Date(expiresAt).toLocaleString()}`);
}

/**
 * 获取当前存储的 Token 信息
 * @returns Token 信息或 null（未登录或已过期）
 */
export function getToken(): TokenInfo | null {
  // 优先读取新键名，fallback 到旧键名（兼容 usePermission.ts 的登录流程）
  let accessToken = localStorage.getItem(TOKEN_KEY);
  let expiresAtStr = localStorage.getItem(TOKEN_EXPIRY_KEY);

  if (!accessToken) {
    accessToken = localStorage.getItem(LEGACY_TOKEN_KEY);
    // 旧系统没有过期时间，默认 24 小时
    if (accessToken) {
      expiresAtStr = null;
    }
  }

  if (!accessToken) {
    return null;
  }

  let expiresAt: number;
  if (expiresAtStr) {
    expiresAt = parseInt(expiresAtStr, 10);
    // 检查是否已过期
    if (Date.now() >= expiresAt) {
      clearToken();
      return null;
    }
  } else {
    // 旧系统 token，默认 2 小时有效期（从存储时间推算）
    expiresAt = Date.now() + 2 * 60 * 60 * 1000;
  }

  return {
    accessToken,
    expiresIn: Math.floor((expiresAt - Date.now()) / 1000),
    expiresAt
  };
}

/**
 * 检查 Token 是否即将过期（30分钟内）
 * @returns true 表示即将过期
 */
export function isTokenExpiringSoon(): boolean {
  const expiresAtStr = localStorage.getItem(TOKEN_EXPIRY_KEY);

  if (!expiresAtStr) {
    return true;
  }

  const expiresAt = parseInt(expiresAtStr, 10);
  return Date.now() >= expiresAt - REFRESH_THRESHOLD_MS;
}

/**
 * 获取剩余有效时间（秒）
 * @returns 剩余秒数，0 表示已过期
 */
export function getTokenRemainingSeconds(): number {
  const expiresAtStr = localStorage.getItem(TOKEN_EXPIRY_KEY);

  if (!expiresAtStr) {
    return 0;
  }

  const expiresAt = parseInt(expiresAtStr, 10);
  return Math.max(0, Math.floor((expiresAt - Date.now()) / 1000));
}

/**
 * 清除本地存储的 Token
 */
export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(TOKEN_EXPIRY_KEY);
  localStorage.removeItem(LEGACY_TOKEN_KEY);
  console.log('[TokenManager] Token cleared');
}

/**
 * 检查是否已登录（Token 有效）
 * @returns true 表示已登录且 Token 有效
 */
export function isLoggedIn(): boolean {
  return getToken() !== null;
}

/**
 * 获取 Authorization Header 值
 * @returns Bearer {token} 格式字符串
 */
export function getAuthHeader(): string {
  const token = getToken();
  return token ? `Bearer ${token.accessToken}` : '';
}

// =============================================================================
// Token 过期定时监控
// =============================================================================

let _tokenMonitorInterval: ReturnType<typeof setInterval> | null = null;

/**
 * 启动 Token 过期后台监控
 * @param onExpired Token 过期时的回调函数
 * @param intervalMs 检测间隔（毫秒），默认 60 秒
 */
export function startTokenMonitor(
  onExpired: () => void,
  intervalMs: number = 60000
): void {
  if (_tokenMonitorInterval) {
    clearInterval(_tokenMonitorInterval);
  }

  // 立即执行一次检测
  if (!getToken()) {
    onExpired();
  }

  _tokenMonitorInterval = setInterval(() => {
    if (!getToken()) {
      onExpired();
    }
  }, intervalMs);
}

/**
 * 停止 Token 过期监控
 */
export function stopTokenMonitor(): void {
  if (_tokenMonitorInterval) {
    clearInterval(_tokenMonitorInterval);
    _tokenMonitorInterval = null;
  }
}