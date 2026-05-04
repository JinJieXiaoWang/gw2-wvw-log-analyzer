export interface User {
  id: number
  username: string
  email?: string
  avatar?: string
  role: string
  is_active: boolean
  created_at?: string
  updated_at?: string
}

export interface UserProfile extends User {
  last_login?: string
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
  current_password: string
  new_password: string
  confirm_password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: User
}

export interface AdminLogin {
  username: string
  password: string
}

export interface ChangePasswordRequest {
  current_password: string
  new_password: string
  confirm_password: string
}