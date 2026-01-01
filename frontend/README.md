# 営業日報システム - フロントエンド

React + TypeScript + Vite で構築された営業日報管理システムのフロントエンドアプリケーション。

## 技術スタック

- **React 18** - UIライブラリ
- **TypeScript** - 型安全な開発
- **Vite** - 高速ビルドツール
- **React Router** - ルーティング
- **Axios** - HTTP クライアント

## ディレクトリ構造

```
frontend/
├── src/
│   ├── api/              # API クライアント
│   │   ├── client.ts     # Axios インスタンス、インターセプター
│   │   └── auth.ts       # 認証 API
│   ├── contexts/         # React コンテキスト
│   │   └── AuthContext.tsx
│   ├── pages/            # ページコンポーネント
│   │   ├── LoginPage.tsx
│   │   ├── DashboardPage.tsx
│   │   ├── DailyReportsPage.tsx
│   │   └── UsersPage.tsx
│   ├── router/           # ルーティング設定
│   │   └── index.tsx
│   ├── types/            # TypeScript 型定義
│   │   └── index.ts
│   ├── App.tsx           # ルートコンポーネント
│   ├── main.tsx          # エントリーポイント
│   └── vite-env.d.ts     # Vite 型定義
├── .env.example          # 環境変数サンプル
├── index.html            # HTML エントリーポイント
├── package.json
├── tsconfig.json
└── vite.config.ts
```

## セットアップ

### 前提条件

- Node.js 18.x 以上
- npm または yarn

### インストール

```bash
cd frontend
npm install
```

### 環境変数設定

`.env.example` をコピーして `.env` を作成:

```bash
cp .env.example .env
```

必要に応じて環境変数を編集:

```env
VITE_APP_TITLE=営業日報システム
VITE_PORT=5173
VITE_API_BASE_URL=http://localhost:8000
VITE_ENABLE_DEVTOOLS=true
```

## 開発

開発サーバーを起動:

```bash
npm run dev
```

ブラウザで http://localhost:5173 を開く

## ビルド

本番用ビルド:

```bash
npm run build
```

ビルド結果は `dist/` ディレクトリに出力されます。

## プレビュー

本番ビルドをプレビュー:

```bash
npm run preview
```

## リント

ESLint でコードチェック:

```bash
npm run lint
```

## 主な機能

### 認証

- JWT トークンベースの認証
- ログイン/ログアウト
- 自動トークン更新
- 保護されたルート

### API 統合

- Axios インターセプターで自動トークン付与
- 401 エラー時の自動ログアウト
- 403 エラーハンドリング

### ルーティング

- React Router v6 使用
- 認証が必要なルートの保護
- ログイン済みユーザーのリダイレクト

## 今後の実装予定

- 日報作成・編集機能
- ユーザー管理画面
- 権限管理
- UIコンポーネントライブラリ導入
- フォームバリデーション
- エラーハンドリング強化

## ライセンス

Private
