import apiClient from './client'
import type { LoginRequest, LoginResponse, User } from '@/types'

export const authApi = {
  // ログイン
  login: async (credentials: LoginRequest): Promise<LoginResponse> => {
    const response = await apiClient.post<LoginResponse>('/api/auth/login', credentials)
    return response.data
  },

  // ログアウト
  logout: async (): Promise<void> => {
    await apiClient.post('/api/auth/logout')
  },

  // 現在のユーザー情報取得
  getCurrentUser: async (): Promise<User> => {
    const response = await apiClient.get<User>('/api/auth/me')
    return response.data
  },
}
