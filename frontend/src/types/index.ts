// ユーザー関連の型定義
export interface User {
  id: number
  company_id: number
  name: string
  email: string
  role: string
  position?: string
  branch_id?: number
  department_id?: number
  is_active: boolean
  created_at: string
  updated_at: string
}

// 認証関連の型定義
export interface LoginRequest {
  email: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: User
}

// 企業関連の型定義
export interface Company {
  id: number
  name: string
  address?: string
  phone?: string
  created_at: string
  updated_at: string
}

// 支店関連の型定義
export interface Branch {
  id: number
  company_id: number
  name: string
  address?: string
  created_at: string
  updated_at: string
}

// 部署関連の型定義
export interface Department {
  id: number
  company_id: number
  name: string
  created_at: string
  updated_at: string
}

// 顧客関連の型定義
export interface Customer {
  id: number
  company_id: number
  name: string
  address?: string
  phone?: string
  email?: string
  created_at: string
  updated_at: string
}

// 日報関連の型定義
export interface DailyReport {
  id: number
  user_id: number
  report_date: string
  content: string
  customer_id?: number
  branch_id?: number
  status: 'draft' | 'submitted' | 'approved'
  submitted_at?: string
  approved_at?: string
  approved_by?: number
  created_at: string
  updated_at: string
}

export interface DailyReportCreate {
  report_date: string
  content: string
  customer_id?: number
  branch_id?: number
  status?: 'draft' | 'submitted'
}

// API エラーレスポンス
export interface ApiError {
  detail: string
}

// ページネーション
export interface PaginationParams {
  skip?: number
  limit?: number
}

// 施設関連の型定義
export interface Facility {
  id: number
  company_id: number
  name: string
  address?: string
  phone?: string
  created_at: string
  updated_at: string
}

// サービス関連の型定義
export interface Service {
  id: number
  service_code: string
  service_name: string
  description?: string
  base_price: number
  is_active: boolean
  created_at: string
  updated_at: string
}

// サービス契約関連の型定義
export interface ServiceSubscription {
  id: number
  company_id: number
  service_id: number
  status: 'active' | 'inactive' | 'suspended'
  start_date: string
  end_date?: string
  monthly_price: number
  created_at: string
  updated_at: string
}
