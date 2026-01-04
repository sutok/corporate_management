import apiClient from './client'
import type { Branch, BranchCreate } from '@/types'

export const branchesApi = {
  // 支店一覧取得
  getAll: async (params?: { skip?: number; limit?: number }): Promise<Branch[]> => {
    const response = await apiClient.get<Branch[]>('/api/branches', { params })
    return response.data
  },

  // 支店詳細取得
  getById: async (id: number): Promise<Branch> => {
    const response = await apiClient.get<Branch>(`/api/branches/${id}`)
    return response.data
  },

  // 支店作成
  create: async (data: BranchCreate): Promise<Branch> => {
    const response = await apiClient.post<Branch>('/api/branches', data)
    return response.data
  },

  // 支店更新
  update: async (id: number, data: Partial<BranchCreate>): Promise<Branch> => {
    const response = await apiClient.put<Branch>(`/api/branches/${id}`, data)
    return response.data
  },

  // 支店削除
  delete: async (id: number): Promise<void> => {
    await apiClient.delete(`/api/branches/${id}`)
  },
}
