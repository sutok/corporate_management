import apiClient from './client'
import type { User } from '@/types'

interface UserCreate {
  company_id: number
  name: string
  email: string
  password: string
  role: string
  position?: string
  branch_id?: number
  department_id?: number
}

export const usersApi = {
  // ユーザー一覧取得
  getAll: async (params?: { skip?: number; limit?: number }): Promise<User[]> => {
    const response = await apiClient.get<User[]>('/api/users', { params })
    return response.data
  },

  // ユーザー詳細取得
  getById: async (id: number): Promise<User> => {
    const response = await apiClient.get<User>(`/api/users/${id}`)
    return response.data
  },

  // ユーザー作成
  create: async (data: UserCreate): Promise<User> => {
    const response = await apiClient.post<User>('/api/users', data)
    return response.data
  },

  // ユーザー更新
  update: async (id: number, data: Partial<UserCreate>): Promise<User> => {
    const response = await apiClient.put<User>(`/api/users/${id}`, data)
    return response.data
  },

  // ユーザー削除
  delete: async (id: number): Promise<void> => {
    await apiClient.delete(`/api/users/${id}`)
  },
}
