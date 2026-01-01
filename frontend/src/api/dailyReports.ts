import apiClient from './client'
import type { DailyReport, DailyReportCreate } from '@/types'

export const dailyReportsApi = {
  // 日報一覧取得
  getAll: async (params?: {
    user_id?: number
    start_date?: string
    end_date?: string
    skip?: number
    limit?: number
  }): Promise<DailyReport[]> => {
    const response = await apiClient.get<DailyReport[]>('/api/daily-reports', { params })
    return response.data
  },

  // 日報詳細取得
  getById: async (id: number): Promise<DailyReport> => {
    const response = await apiClient.get<DailyReport>(`/api/daily-reports/${id}`)
    return response.data
  },

  // 日報作成
  create: async (data: DailyReportCreate): Promise<DailyReport> => {
    const response = await apiClient.post<DailyReport>('/api/daily-reports', data)
    return response.data
  },

  // 日報更新
  update: async (id: number, data: Partial<DailyReportCreate>): Promise<DailyReport> => {
    const response = await apiClient.put<DailyReport>(`/api/daily-reports/${id}`, data)
    return response.data
  },

  // 日報削除
  delete: async (id: number): Promise<void> => {
    await apiClient.delete(`/api/daily-reports/${id}`)
  },
}
