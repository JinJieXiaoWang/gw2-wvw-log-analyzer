import { apiFactory } from '../core/apiService'
import { API_ENDPOINTS } from '@/constants/apiEndpoints'
import type { ApiResponse } from '../../models'

export interface AdminLogin {
  username: string
  password: string
}

export interface ChangePasswordRequest {
  /** 当前密码（兼容性：部分后端使用 current_password） */
  old_password?: string
  current_password?: string
  new_password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  expires_in: number
  user: {
    id: number
    username: string
    role: string
    is_active: boolean
  }
}

export class AuthService {
  async login(data: AdminLogin): Promise<ApiResponse<LoginResponse>> {
    return apiFactory.post<LoginResponse>(API_ENDPOINTS.AUTH.LOGIN, data)
  }

  async logout(): Promise<ApiResponse<void>> {
    return apiFactory.post<void>(API_ENDPOINTS.AUTH.LOGOUT)
  }

  async getLoginStatus(): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(API_ENDPOINTS.AUTH.STATUS)
  }

  async getProfile(): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(API_ENDPOINTS.AUTH.PROFILE)
  }

  async changePassword(data: ChangePasswordRequest): Promise<any> {
    return apiFactory.post(API_ENDPOINTS.AUTH.CHANGE_PASSWORD, data)
  }
}

export const authService = new AuthService()