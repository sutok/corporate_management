import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from 'axios'
import type { ApiError } from '@/types'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// Axiosインスタンスの作成
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
})

// リクエストインターセプター: JWTトークンを自動付与
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('access_token')
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// レスポンスインターセプター: エラーハンドリング
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiError>) => {
    // 401エラー: 認証切れ
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }

    // 403エラー: 権限不足
    if (error.response?.status === 403) {
      console.error('権限が不足しています:', error.response.data?.detail)
    }

    return Promise.reject(error)
  }
)

export default apiClient
