# プロジェクト TODO リスト

**最終更新**: 2026-01-01 (Service Subscription History機能実装完了)
**プロジェクト**: 営業日報システム (FastAPI + React)

---

## 📊 進捗サマリー

- **バックエンドAPI**: 11/11 ルーター実装済み ✅
- **バックエンドテスト**: 11/11 テストファイル実装済み ✅
- **Permission & Role システム**: 実装完了 ✅
- **フロントエンド**: 基本画面実装完了 ✅
- **権限統合**: 一部のみ（1/11 ルーター） ⚠️

---

## ✅ 完了済みタスク

### バックエンド実装
- [x] JWT認証システム (auth.py)
- [x] 企業管理API (companies.py)
- [x] 支店管理API (branches.py)
- [x] 部署管理API (departments.py)
- [x] ユーザー管理API (users.py)
- [x] 顧客管理API (customers.py)
- [x] 日報管理API (daily_reports.py)
- [x] 施設管理API (facilities.py)
- [x] 施設所属管理API (facility_assignments.py)
- [x] サービス契約管理API (subscriptions.py)
- [x] Permission & Role 管理システム実装
- [x] 初期データ投入スクリプト (seed_permissions.py)

### テスト
- [x] 全APIルーターのテスト実装 (11ファイル)
- [x] Permission管理テスト (test_permissions.py - 7テストケース)
- [x] Subscriptions APIテスト (test_subscriptions.py - 8テストケース)
- [x] Service Subscription History テスト (4テストケース追加)
- [x] テスト実行確認 (全テスト成功)

### データベース
- [x] スキーマ設計とマイグレーション
- [x] Permission & Role テーブル実装
- [x] 権限・ロール初期データ投入

### フロントエンド
- [x] Vite + React + TypeScript プロジェクト作成
- [x] 基本的なディレクトリ構造設定
- [x] 環境変数設定 (.env)
- [x] APIクライアント設定 (axios + dailyReports + users)
- [x] ルーティング設定 (React Router)
- [x] 認証コンテキスト実装
- [x] ビルド・開発サーバー動作確認
- [x] 共通レイアウトコンポーネント (Layout)
- [x] ログイン画面
- [x] ダッシュボード（ユーザー情報 + 最近の日報表示）
- [x] 日報一覧・作成画面（CRUD機能）
- [x] ユーザー管理画面（管理者用・CRUD機能）

---

## ❌ 未完了タスク

### 🔴 高優先度 (セキュリティ & 基盤)

#### 1. 既存ルーターへの権限チェック適用
**説明**: 現在、subscriptions.py のみ権限チェックが実装されています。他の全ルーターにも適用が必要です。

**対象ルーター**:
- [ ] auth.py - 認証関連（一部のみ必要）
- [ ] branches.py - 支店管理
- [ ] companies.py - 企業管理
- [ ] customers.py - 顧客管理
- [ ] daily_reports.py - 日報管理
- [ ] departments.py - 部署管理
- [ ] facilities.py - 施設管理
- [ ] facility_assignments.py - 施設所属管理
- [ ] users.py - ユーザー管理

**実装方法**:
```python
from app.auth.permissions import require_permission, require_any_permission

@router.get("/endpoint")
async def endpoint(
    current_user: User = Depends(require_permission("resource.action")),
    ...
):
    ...
```

**参考実装**: `app/routers/subscriptions.py`

**推定工数**: 4-6時間

---

#### 2. フロントエンド環境セットアップ ✅ **完了**
**説明**: React + TypeScript + Vite プロジェクトの初期構築

**タスク**:
- [x] Vite + React + TypeScript プロジェクト作成
- [x] 基本的なディレクトリ構造設定
- [x] 環境変数設定 (.env)
- [x] APIクライアント設定 (axios)
- [x] ルーティング設定 (React Router)
- [x] 認証コンテキスト実装
- [x] ビルド・開発サーバー動作確認

**実装内容**:
- React 18 + TypeScript + Vite プロジェクト構築
- 認証機能付きルーティング (ProtectedRoute, PublicRoute)
- Axios インターセプターによる JWT トークン自動付与
- AuthContext による認証状態管理
- ログイン、ダッシュボード、日報、ユーザー管理ページ作成
- 開発サーバー起動確認済み (http://localhost:5173)

**参考**: `frontend/README.md`

**実施日**: 2026-01-01

---

### 🟡 中優先度 (機能拡張)

#### 3. Service Subscription History 機能実装 ✅ **完了**
**説明**: 契約履歴の取得・表示機能

**場所**: `app/routers/subscriptions.py:47-104`

**実装内容**:
- [x] ServiceSubscriptionHistory モデル活用
- [x] 履歴取得エンドポイント実装
- [x] 履歴データの整形・返却
- [x] テストケース追加

**実装詳細**:
- GET `/api/subscriptions/history` エンドポイント実装
- オプションの `subscription_id` パラメータでフィルタリング
- 会社レベルのアクセス制御（他社データ防止）
- 新しい順にソート（changed_at DESC）
- 4つのテストケース追加（成功、フィルタ、アクセス制御、空データ）

**実施日**: 2026-01-01
**PR**: #4

---

#### 4. 権限チェック統合後のテスト拡充
**説明**: 既存テストに権限チェックのテストケースを追加

**タスク**:
- [ ] test_auth.py - 権限チェックテスト追加
- [ ] test_branches.py - 権限チェックテスト追加
- [ ] test_companies.py - 権限チェックテスト追加
- [ ] test_customers.py - 権限チェックテスト追加
- [ ] test_daily_reports.py - 権限チェックテスト追加
- [ ] test_departments.py - 権限チェックテスト追加
- [ ] test_facilities.py - 権限チェックテスト追加
- [ ] test_facility_assignments.py - 権限チェックテスト追加
- [ ] test_users.py - 権限チェックテスト追加

**各テストに追加すべき項目**:
- 認証なしでのアクセステスト (401 Unauthorized)
- 権限なしでのアクセステスト (403 Forbidden)
- 適切な権限を持つユーザーでのアクセステスト (200 OK)

**参考**: `tests/test_subscriptions.py:170-203`

**推定工数**: 6-8時間

---

#### 5. フロントエンド基本画面実装 ✅ **完了**
**説明**: 主要画面のUI実装

**優先実装画面**:
- [x] ログイン画面
- [x] ダッシュボード
- [x] 日報一覧・作成画面
- [x] ユーザー管理画面（管理者用）

**実装内容**:
- 共通Layoutコンポーネント（ナビゲーション、ヘッダー、ユーザーメニュー）
- ログインページ（既存を維持）
- ダッシュボード（ユーザー情報 + 最近の日報5件表示）
- 日報管理ページ（一覧表示、新規作成フォーム、削除機能）
- ユーザー管理ページ（一覧表示、新規作成フォーム、削除機能、権限チェック）
- レスポンシブデザイン対応
- エラーハンドリング実装

**実施日**: 2026-01-01

---

### 🟢 低優先度 (品質向上・最適化)

#### 6. APIドキュメント更新
**タスク**:
- [ ] Permission & Role システムのAPI仕様追加
- [ ] Swagger/OpenAPI ドキュメント充実
- [ ] 各エンドポイントの権限要件を明記
- [ ] レスポンススキーマの詳細化

**場所**: `claudedocs/API設計書.md`

**推定工数**: 2-3時間

---

#### 7. エラーハンドリング強化
**タスク**:
- [ ] カスタムエラーレスポンスの統一
- [ ] 詳細なエラーメッセージ
- [ ] ロギング強化
- [ ] エラー監視設定

**推定工数**: 3-4時間

---

#### 8. パフォーマンス最適化
**タスク**:
- [ ] データベースクエリの最適化
- [ ] N+1問題の解消
- [ ] キャッシング戦略の実装
- [ ] ページネーション実装
- [ ] インデックス最適化

**推定工数**: 4-6時間

---

#### 9. CI/CD パイプライン構築
**タスク**:
- [ ] GitHub Actions 設定
- [ ] 自動テスト実行
- [ ] リンター・フォーマッター統合
- [ ] デプロイ自動化

**推定工数**: 4-6時間

---

#### 10. セキュリティ強化
**タスク**:
- [ ] CORS設定の厳格化
- [ ] レート制限実装
- [ ] CSRFトークン実装
- [ ] セキュリティヘッダー設定
- [ ] 依存関係の脆弱性スキャン

**推定工数**: 3-4時間

---

## 📋 推奨作業順序

### Phase 1: セキュリティ基盤 (優先度: 🔴)
1. 既存ルーターへの権限チェック適用 (4-6h)
2. 権限チェック統合後のテスト拡充 (6-8h)

**合計**: 10-14時間

---

### Phase 2: フロントエンド基盤 (優先度: 🔴)
1. フロントエンド環境セットアップ (3-4h)
2. ログイン画面実装 (2-4h)
3. ダッシュボード実装 (3-4h)

**合計**: 8-12時間

---

### Phase 3: 機能拡張 (優先度: 🟡)
1. Service Subscription History 実装 (2-3h)
2. 日報画面実装 (3-4h)
3. ユーザー管理画面実装 (3-4h)

**合計**: 8-11時間

---

### Phase 4: 品質向上 (優先度: 🟢)
1. APIドキュメント更新 (2-3h)
2. エラーハンドリング強化 (3-4h)
3. パフォーマンス最適化 (4-6h)

**合計**: 9-13時間

---

## 📌 メモ

### 技術的な注意事項
- Permission & Role システムの権限コード一覧は `backend/scripts/seed_permissions.py` を参照
- 既存の権限チェック実装例は `app/routers/subscriptions.py` を参照
- テストデータ作成のヘルパー関数は `tests/test_subscriptions.py:create_test_data()` を参照

### 未コミット変更
- `.claude/settings.local.json` - ローカル設定（必要に応じてコミット）
- `.gitallowed` - git-secrets 除外パターン（必要に応じてコミット）

---

## 🎯 次のアクション

**即座に取り組むべきタスク**:
1. 既存ルーターへの権限チェック適用（セキュリティクリティカル）
2. フロントエンド環境セットアップ（開発開始に必要）

**チームで相談が必要な項目**:
- フロントエンドのUIフレームワーク選定（Material-UI, Ant Design, etc.）
- 権限設定の詳細仕様（各エンドポイントに必要な権限レベル）
- デプロイ環境の決定（AWS, GCP, Azure）

---

**作成日**: 2026-01-01
**作成者**: Claude Code
**バージョン**: 1.0.0
