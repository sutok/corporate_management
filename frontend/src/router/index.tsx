import { createBrowserRouter, Navigate } from 'react-router-dom'
import { useAuth } from '@/contexts/AuthContext'
import { ReactNode } from 'react'

// ページコンポーネント（後で実装）
import LoginPage from '@/pages/LoginPage'
import DashboardPage from '@/pages/DashboardPage'
import DailyReportsPage from '@/pages/DailyReportsPage'
import UsersPage from '@/pages/UsersPage'
import BranchesPage from '@/pages/BranchesPage'

// 認証が必要なルートを保護するコンポーネント
interface ProtectedRouteProps {
  children: ReactNode
}

const ProtectedRoute = ({ children }: ProtectedRouteProps) => {
  const { isAuthenticated, loading } = useAuth()

  if (loading) {
    return <div>読み込み中...</div>
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return <>{children}</>
}

// ログイン済みの場合はダッシュボードにリダイレクト
const PublicRoute = ({ children }: ProtectedRouteProps) => {
  const { isAuthenticated, loading } = useAuth()

  if (loading) {
    return <div>読み込み中...</div>
  }

  if (isAuthenticated) {
    return <Navigate to="/" replace />
  }

  return <>{children}</>
}

export const router = createBrowserRouter([
  {
    path: '/login',
    element: (
      <PublicRoute>
        <LoginPage />
      </PublicRoute>
    ),
  },
  {
    path: '/',
    element: (
      <ProtectedRoute>
        <DashboardPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/reports',
    element: (
      <ProtectedRoute>
        <DailyReportsPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/users',
    element: (
      <ProtectedRoute>
        <UsersPage />
      </ProtectedRoute>
    ),
  },
  {
    path: '/branches',
    element: (
      <ProtectedRoute>
        <BranchesPage />
      </ProtectedRoute>
    ),
  },
])
