import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { authApi } from '@/api/auth'
import type { User, LoginRequest } from '@/types'

interface AuthContextType {
  user: User | null
  loading: boolean
  login: (credentials: LoginRequest) => Promise<void>
  logout: () => Promise<void>
  isAuthenticated: boolean
}

const AuthContext = createContext<AuthContextType | null>(null)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

interface AuthProviderProps {
  children: ReactNode
}

export const AuthProvider = ({ children }: AuthProviderProps) => {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  // 初期化: localStorageからユーザー情報を復元
  useEffect(() => {
    const initializeAuth = async () => {
      const token = localStorage.getItem('access_token')
      const storedUser = localStorage.getItem('user')

      if (token && storedUser) {
        try {
          setUser(JSON.parse(storedUser))
          // サーバーからユーザー情報を再取得して同期
          const currentUser = await authApi.getCurrentUser()
          setUser(currentUser)
          localStorage.setItem('user', JSON.stringify(currentUser))
        } catch (error) {
          // トークンが無効な場合はクリア
          localStorage.removeItem('access_token')
          localStorage.removeItem('user')
          setUser(null)
        }
      }
      setLoading(false)
    }

    initializeAuth()
  }, [])

  const login = async (credentials: LoginRequest) => {
    setLoading(true)
    try {
      const response = await authApi.login(credentials)
      localStorage.setItem('access_token', response.access_token)
      localStorage.setItem('user', JSON.stringify(response.user))
      setUser(response.user)
    } catch (error) {
      throw error
    } finally {
      setLoading(false)
    }
  }

  const logout = async () => {
    try {
      await authApi.logout()
    } catch (error) {
      console.error('ログアウトエラー:', error)
    } finally {
      localStorage.removeItem('access_token')
      localStorage.removeItem('user')
      setUser(null)
    }
  }

  const value = {
    user,
    loading,
    login,
    logout,
    isAuthenticated: !!user,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
