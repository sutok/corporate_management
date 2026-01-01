import { useEffect, useState } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import Layout from '@/components/Layout'
import { usersApi } from '@/api/users'
import type { User } from '@/types'
import './UsersPage.css'

const UsersPage = () => {
  const { user: currentUser } = useAuth()
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    role: 'staff',
    position: '',
  })
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchUsers()
  }, [])

  const fetchUsers = async () => {
    try {
      const data = await usersApi.getAll()
      setUsers(data)
    } catch (err: any) {
      console.error('ユーザー取得エラー:', err)
      setError(err.response?.data?.detail || 'ユーザーの取得に失敗しました')
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitting(true)
    setError('')

    try {
      await usersApi.create({
        ...formData,
        company_id: currentUser!.company_id,
      })
      setShowForm(false)
      setFormData({
        name: '',
        email: '',
        password: '',
        role: 'staff',
        position: '',
      })
      await fetchUsers()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'ユーザーの作成に失敗しました')
    } finally {
      setSubmitting(false)
    }
  }

  const handleDelete = async (id: number) => {
    if (!confirm('このユーザーを削除しますか？')) return

    try {
      await usersApi.delete(id)
      await fetchUsers()
    } catch (err: any) {
      alert(err.response?.data?.detail || 'ユーザーの削除に失敗しました')
    }
  }

  const canManageUsers = currentUser?.role === 'admin' || currentUser?.role === 'manager'

  if (!canManageUsers) {
    return (
      <Layout>
        <div className="users-page">
          <h1>ユーザー管理</h1>
          <p className="error-message">この機能を利用する権限がありません。</p>
        </div>
      </Layout>
    )
  }

  return (
    <Layout>
      <div className="users-page">
        <div className="page-header">
          <h1>ユーザー管理</h1>
          <button onClick={() => setShowForm(!showForm)} className="primary-button">
            {showForm ? 'キャンセル' : '新規ユーザー作成'}
          </button>
        </div>

        {error && <div className="error-message">{error}</div>}

        {showForm && (
          <div className="form-container">
            <h2>新規ユーザー作成</h2>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label htmlFor="name">名前</label>
                <input
                  id="name"
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                  className="form-input"
                />
              </div>

              <div className="form-group">
                <label htmlFor="email">メールアドレス</label>
                <input
                  id="email"
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  required
                  className="form-input"
                />
              </div>

              <div className="form-group">
                <label htmlFor="password">パスワード</label>
                <input
                  id="password"
                  type="password"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  required
                  minLength={6}
                  className="form-input"
                  placeholder="6文字以上"
                />
              </div>

              <div className="form-group">
                <label htmlFor="role">役割</label>
                <select
                  id="role"
                  value={formData.role}
                  onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                  className="form-select"
                >
                  <option value="staff">スタッフ</option>
                  <option value="manager">マネージャー</option>
                  {currentUser?.role === 'admin' && <option value="admin">管理者</option>}
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="position">役職（任意）</label>
                <input
                  id="position"
                  type="text"
                  value={formData.position}
                  onChange={(e) => setFormData({ ...formData, position: e.target.value })}
                  className="form-input"
                />
              </div>

              <div className="form-actions">
                <button type="submit" disabled={submitting} className="primary-button">
                  {submitting ? '作成中...' : '作成'}
                </button>
                <button
                  type="button"
                  onClick={() => setShowForm(false)}
                  className="secondary-button"
                >
                  キャンセル
                </button>
              </div>
            </form>
          </div>
        )}

        <div className="users-list">
          <h2>ユーザー一覧</h2>
          {loading ? (
            <p>読み込み中...</p>
          ) : users.length > 0 ? (
            <table className="users-table">
              <thead>
                <tr>
                  <th>名前</th>
                  <th>メールアドレス</th>
                  <th>役割</th>
                  <th>役職</th>
                  <th>ステータス</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                {users.map((user) => (
                  <tr key={user.id}>
                    <td>{user.name}</td>
                    <td>{user.email}</td>
                    <td>
                      <span className={`role-badge role-${user.role}`}>
                        {user.role === 'admin'
                          ? '管理者'
                          : user.role === 'manager'
                            ? 'マネージャー'
                            : 'スタッフ'}
                      </span>
                    </td>
                    <td>{user.position || '-'}</td>
                    <td>
                      <span className={`status-badge ${user.is_active ? 'active' : 'inactive'}`}>
                        {user.is_active ? '有効' : '無効'}
                      </span>
                    </td>
                    <td>
                      {user.id !== currentUser?.id && (
                        <button
                          onClick={() => handleDelete(user.id)}
                          className="delete-button"
                        >
                          削除
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p className="empty-message">ユーザーがいません</p>
          )}
        </div>
      </div>
    </Layout>
  )
}

export default UsersPage
