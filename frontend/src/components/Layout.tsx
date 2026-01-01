import { ReactNode } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '@/contexts/AuthContext'
import './Layout.css'

interface LayoutProps {
  children: ReactNode
}

const Layout = ({ children }: LayoutProps) => {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  return (
    <div className="layout">
      <header className="header">
        <div className="header-content">
          <h1 className="logo">
            <Link to="/">営業日報システム</Link>
          </h1>
          <nav className="nav">
            <Link to="/" className="nav-link">
              ダッシュボード
            </Link>
            <Link to="/reports" className="nav-link">
              日報管理
            </Link>
            {(user?.role === 'admin' || user?.role === 'manager') && (
              <Link to="/users" className="nav-link">
                ユーザー管理
              </Link>
            )}
          </nav>
          <div className="user-menu">
            <span className="user-name">{user?.name}</span>
            <button onClick={handleLogout} className="logout-button">
              ログアウト
            </button>
          </div>
        </div>
      </header>
      <main className="main">{children}</main>
    </div>
  )
}

export default Layout
