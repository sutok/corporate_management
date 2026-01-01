import { useEffect, useState } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import Layout from '@/components/Layout'
import { dailyReportsApi } from '@/api/dailyReports'
import type { DailyReport, DailyReportCreate } from '@/types'
import './DailyReportsPage.css'

const DailyReportsPage = () => {
  const { user } = useAuth()
  const [reports, setReports] = useState<DailyReport[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState<DailyReportCreate>({
    report_date: new Date().toISOString().split('T')[0],
    content: '',
    status: 'draft',
  })
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchReports()
  }, [])

  const fetchReports = async () => {
    try {
      const data = await dailyReportsApi.getAll({ limit: 50 })
      setReports(data)
    } catch (err: any) {
      console.error('日報取得エラー:', err)
      setError(err.response?.data?.detail || '日報の取得に失敗しました')
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitting(true)
    setError('')

    try {
      await dailyReportsApi.create({
        ...formData,
        user_id: user!.id,
      })
      setShowForm(false)
      setFormData({
        report_date: new Date().toISOString().split('T')[0],
        content: '',
        status: 'draft',
      })
      await fetchReports()
    } catch (err: any) {
      setError(err.response?.data?.detail || '日報の作成に失敗しました')
    } finally {
      setSubmitting(false)
    }
  }

  const handleDelete = async (id: number) => {
    if (!confirm('この日報を削除しますか？')) return

    try {
      await dailyReportsApi.delete(id)
      await fetchReports()
    } catch (err: any) {
      alert(err.response?.data?.detail || '日報の削除に失敗しました')
    }
  }

  return (
    <Layout>
      <div className="daily-reports-page">
        <div className="page-header">
          <h1>日報管理</h1>
          <button onClick={() => setShowForm(!showForm)} className="primary-button">
            {showForm ? 'キャンセル' : '新規日報作成'}
          </button>
        </div>

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        {showForm && (
          <div className="form-container">
            <h2>新規日報作成</h2>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label htmlFor="report_date">日付</label>
                <input
                  id="report_date"
                  type="date"
                  value={formData.report_date}
                  onChange={(e) => setFormData({ ...formData, report_date: e.target.value })}
                  required
                  className="form-input"
                />
              </div>

              <div className="form-group">
                <label htmlFor="content">内容</label>
                <textarea
                  id="content"
                  value={formData.content}
                  onChange={(e) => setFormData({ ...formData, content: e.target.value })}
                  required
                  rows={10}
                  className="form-textarea"
                  placeholder="本日の活動内容を入力してください..."
                />
              </div>

              <div className="form-group">
                <label htmlFor="status">ステータス</label>
                <select
                  id="status"
                  value={formData.status}
                  onChange={(e) =>
                    setFormData({ ...formData, status: e.target.value as 'draft' | 'submitted' })
                  }
                  className="form-select"
                >
                  <option value="draft">下書き</option>
                  <option value="submitted">提出</option>
                </select>
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

        <div className="reports-list">
          <h2>日報一覧</h2>
          {loading ? (
            <p>読み込み中...</p>
          ) : reports.length > 0 ? (
            <table className="reports-table">
              <thead>
                <tr>
                  <th>日付</th>
                  <th>ユーザー</th>
                  <th>ステータス</th>
                  <th>内容</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                {reports.map((report) => (
                  <tr key={report.id}>
                    <td>{report.report_date}</td>
                    <td>ID: {report.user_id}</td>
                    <td>
                      <span className={`status-badge status-${report.status}`}>
                        {report.status === 'approved'
                          ? '承認済み'
                          : report.status === 'submitted'
                            ? '提出済み'
                            : '下書き'}
                      </span>
                    </td>
                    <td className="content-cell">
                      {report.content.substring(0, 100)}
                      {report.content.length > 100 ? '...' : ''}
                    </td>
                    <td>
                      {report.user_id === user?.id && (
                        <button
                          onClick={() => handleDelete(report.id)}
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
            <p className="empty-message">日報がありません</p>
          )}
        </div>
      </div>
    </Layout>
  )
}

export default DailyReportsPage
