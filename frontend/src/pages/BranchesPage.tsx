import { useEffect, useState } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import Layout from '@/components/Layout'
import { branchesApi } from '@/api/branches'
import type { Branch, BranchCreate } from '@/types'
import './BranchesPage.css'

const BranchesPage = () => {
  const { user: currentUser } = useAuth()
  const [branches, setBranches] = useState<Branch[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [editingBranch, setEditingBranch] = useState<Branch | null>(null)
  const [formData, setFormData] = useState<BranchCreate>({
    company_id: 0,
    name: '',
    address: '',
    phone: '',
  })
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (currentUser) {
      setFormData((prev) => ({ ...prev, company_id: currentUser.company_id }))
      fetchBranches()
    }
  }, [currentUser])

  const fetchBranches = async () => {
    try {
      const data = await branchesApi.getAll()
      setBranches(data)
    } catch (err: any) {
      console.error('支店取得エラー:', err)
      setError(err.response?.data?.detail || '支店の取得に失敗しました')
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitting(true)
    setError('')

    try {
      if (editingBranch) {
        await branchesApi.update(editingBranch.id, formData)
      } else {
        await branchesApi.create({
          ...formData,
          company_id: currentUser!.company_id,
        })
      }
      setShowForm(false)
      setEditingBranch(null)
      setFormData({
        company_id: currentUser!.company_id,
        name: '',
        address: '',
        phone: '',
      })
      await fetchBranches()
    } catch (err: any) {
      setError(
        err.response?.data?.detail ||
          `支店の${editingBranch ? '更新' : '作成'}に失敗しました`
      )
    } finally {
      setSubmitting(false)
    }
  }

  const handleEdit = (branch: Branch) => {
    setEditingBranch(branch)
    setFormData({
      company_id: branch.company_id,
      name: branch.name,
      address: branch.address || '',
      phone: branch.phone || '',
    })
    setShowForm(true)
  }

  const handleCancelEdit = () => {
    setEditingBranch(null)
    setShowForm(false)
    setFormData({
      company_id: currentUser!.company_id,
      name: '',
      address: '',
      phone: '',
    })
  }

  const handleDelete = async (id: number) => {
    if (!confirm('この支店を削除しますか？')) return

    try {
      await branchesApi.delete(id)
      await fetchBranches()
    } catch (err: any) {
      alert(err.response?.data?.detail || '支店の削除に失敗しました')
    }
  }

  const canManageBranches = currentUser?.role === 'admin' || currentUser?.role === 'manager'

  if (!canManageBranches) {
    return (
      <Layout>
        <div className="branches-page">
          <h1>支店管理</h1>
          <p className="error-message">この機能を利用する権限がありません。</p>
        </div>
      </Layout>
    )
  }

  return (
    <Layout>
      <div className="branches-page">
        <div className="page-header">
          <h1>支店管理</h1>
          <button
            onClick={() => {
              if (showForm && !editingBranch) {
                setShowForm(false)
              } else {
                setEditingBranch(null)
                setFormData({
                  company_id: currentUser!.company_id,
                  name: '',
                  address: '',
                  phone: '',
                })
                setShowForm(!showForm)
              }
            }}
            className="primary-button"
          >
            {showForm ? 'キャンセル' : '新規支店作成'}
          </button>
        </div>

        {error && <div className="error-message">{error}</div>}

        {showForm && (
          <div className="form-container">
            <h2>{editingBranch ? '支店編集' : '新規支店作成'}</h2>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label htmlFor="name">支店名</label>
                <input
                  id="name"
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                  className="form-input"
                  placeholder="例: 東京本社"
                />
              </div>

              <div className="form-group">
                <label htmlFor="address">住所（任意）</label>
                <input
                  id="address"
                  type="text"
                  value={formData.address}
                  onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                  className="form-input"
                  placeholder="例: 東京都渋谷区1-2-3"
                />
              </div>

              <div className="form-group">
                <label htmlFor="phone">電話番号（任意）</label>
                <input
                  id="phone"
                  type="tel"
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                  className="form-input"
                  placeholder="例: 03-1234-5678"
                />
              </div>

              <div className="form-actions">
                <button type="submit" disabled={submitting} className="primary-button">
                  {submitting
                    ? `${editingBranch ? '更新' : '作成'}中...`
                    : editingBranch
                      ? '更新'
                      : '作成'}
                </button>
                <button
                  type="button"
                  onClick={handleCancelEdit}
                  className="secondary-button"
                >
                  キャンセル
                </button>
              </div>
            </form>
          </div>
        )}

        <div className="branches-list">
          <h2>支店一覧</h2>
          {loading ? (
            <p>読み込み中...</p>
          ) : branches.length > 0 ? (
            <table className="branches-table">
              <thead>
                <tr>
                  <th>支店名</th>
                  <th>住所</th>
                  <th>電話番号</th>
                  <th>作成日</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                {branches.map((branch) => (
                  <tr key={branch.id}>
                    <td>{branch.name}</td>
                    <td>{branch.address || '-'}</td>
                    <td>{branch.phone || '-'}</td>
                    <td>{new Date(branch.created_at).toLocaleDateString('ja-JP')}</td>
                    <td>
                      <div className="action-buttons">
                        <button
                          onClick={() => handleEdit(branch)}
                          className="edit-button"
                        >
                          編集
                        </button>
                        <button
                          onClick={() => handleDelete(branch.id)}
                          className="delete-button"
                        >
                          削除
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p className="empty-message">支店がありません</p>
          )}
        </div>
      </div>
    </Layout>
  )
}

export default BranchesPage
