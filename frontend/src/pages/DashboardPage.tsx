import { useEffect, useState } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import Layout from '@/components/Layout'
import { dailyReportsApi } from '@/api/dailyReports'
import type { DailyReport } from '@/types'

const DashboardPage = () => {
  const { user } = useAuth()
  const [recentReports, setRecentReports] = useState<DailyReport[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchRecentReports = async () => {
      try {
        const reports = await dailyReportsApi.getAll({ user_id: user?.id, limit: 5 })
        setRecentReports(reports)
      } catch (error) {
        console.error('日報取得エラー:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchRecentReports()
  }, [user?.id])

  return (
    <Layout>
      <div>
        <h1>ダッシュボード</h1>

        <div style={{ marginBottom: '30px' }}>
          <h2>ユーザー情報</h2>
          <div style={{ background: '#f8f9fa', padding: '20px', borderRadius: '8px' }}>
            <p>
              <strong>名前:</strong> {user?.name}
            </p>
            <p>
              <strong>メール:</strong> {user?.email}
            </p>
            <p>
              <strong>役割:</strong> {user?.role}
            </p>
            <p>
              <strong>役職:</strong> {user?.position || '未設定'}
            </p>
          </div>
        </div>

        <div>
          <h2>最近の日報</h2>
          {loading ? (
            <p>読み込み中...</p>
          ) : recentReports.length > 0 ? (
            <div style={{ background: '#f8f9fa', padding: '20px', borderRadius: '8px' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ borderBottom: '2px solid #dee2e6' }}>
                    <th style={{ padding: '10px', textAlign: 'left' }}>日付</th>
                    <th style={{ padding: '10px', textAlign: 'left' }}>ステータス</th>
                    <th style={{ padding: '10px', textAlign: 'left' }}>内容</th>
                  </tr>
                </thead>
                <tbody>
                  {recentReports.map((report) => (
                    <tr key={report.id} style={{ borderBottom: '1px solid #dee2e6' }}>
                      <td style={{ padding: '10px' }}>{report.report_date}</td>
                      <td style={{ padding: '10px' }}>
                        <span
                          style={{
                            padding: '4px 8px',
                            borderRadius: '4px',
                            background:
                              report.status === 'approved'
                                ? '#d4edda'
                                : report.status === 'submitted'
                                  ? '#fff3cd'
                                  : '#f8d7da',
                            color:
                              report.status === 'approved'
                                ? '#155724'
                                : report.status === 'submitted'
                                  ? '#856404'
                                  : '#721c24',
                          }}
                        >
                          {report.status === 'approved'
                            ? '承認済み'
                            : report.status === 'submitted'
                              ? '提出済み'
                              : '下書き'}
                        </span>
                      </td>
                      <td style={{ padding: '10px' }}>
                        {report.content.substring(0, 50)}
                        {report.content.length > 50 ? '...' : ''}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p style={{ color: '#6c757d' }}>日報がまだありません</p>
          )}
        </div>
      </div>
    </Layout>
  )
}

export default DashboardPage
