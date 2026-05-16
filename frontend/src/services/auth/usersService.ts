import { apiFactory } from '../core/apiService'
import { API_ENDPOINTS } from '@/config/apiEndpoints'
import type { ApiResponse } from '@/types/api'

export interface UsersListParams {
  page?: number
  page_size?: number
  role?: string | null
  is_active?: boolean | null
}

export interface UserCreate {
  username: string
  password: string
  role: string
  is_active?: boolean
}

export interface UserUpdate {
  username?: string
  role?: string
  is_active?: boolean
}

export interface PasswordChange {
  old_password: string
  new_password: string
}

export class UsersService {
  async getUsers(params: UsersListParams): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(API_ENDPOINTS.USERS.LIST, { params })
  }

  async createUser(data: UserCreate): Promise<ApiResponse<any>> {
    return apiFactory.post<any>(API_ENDPOINTS.USERS.CREATE, data)
  }

  async getUserProfile(): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(API_ENDPOINTS.USERS.PROFILE)
  }

  async getUser(userId: number): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(API_ENDPOINTS.USERS.DETAIL(userId))
  }

  async updateUser(userId: number, data: UserUpdate): Promise<ApiResponse<any>> {
    return apiFactory.put<any>(API_ENDPOINTS.USERS.UPDATE(userId), data)
  }

  async deleteUser(userId: number): Promise<ApiResponse<void>> {
    return apiFactory.delete<void>(API_ENDPOINTS.USERS.DELETE(userId))
  }

  async changePassword(data: PasswordChange): Promise<ApiResponse<void>> {
    return apiFactory.post<void>(API_ENDPOINTS.USERS.CHANGE_PASSWORD, data)
  }

  async resetUserPassword(userId: number): Promise<ApiResponse<any>> {
    return apiFactory.post<any>(API_ENDPOINTS.USERS.RESET_PASSWORD(userId))
  }

  async toggleUserActive(userId: number): Promise<ApiResponse<any>> {
    return apiFactory.post<any>(API_ENDPOINTS.USERS.TOGGLE_ACTIVE(userId))
  }

  async getRoles(): Promise<ApiResponse<any>> {
    return apiFactory.get<any>(API_ENDPOINTS.USERS.ROLES_LIST)
  }
}

export const usersService = new UsersService()