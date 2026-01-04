# 営業日報システム API設計書

## 目次
1. [共通仕様](#共通仕様)
2. [認証API](#認証api)
3. [日報API](#日報api)
4. [訪問記録API](#訪問記録api)
5. [課題API](#課題api)
6. [計画API](#計画api)
7. [コメントAPI](#コメントapi)
8. [顧客マスタAPI](#顧客マスタapi)
9. [ユーザーマスタAPI](#ユーザーマスタapi)
10. [企業API](#企業api)
11. [支店マスタAPI](#支店マスタapi)
12. [部署マスタAPI](#部署マスタapi)
13. [ユーザー所属管理API](#ユーザー所属管理api)
14. [サービスマスタAPI](#サービスマスタapi)
15. [企業サービス契約API](#企業サービス契約api)
16. [エラーコード一覧](#エラーコード一覧)

---

## 共通仕様

### ベースURL
```
https://api.sales-report.example.com/v1
```

### 認証方式
- JWT（JSON Web Token）を使用
- Authorizationヘッダーに Bearer トークンを含める

```
Authorization: Bearer {access_token}
```

### リクエストヘッダー

| ヘッダー名 | 値 | 必須 | 備考 |
|-----------|-----|------|------|
| Content-Type | application/json | ○ | POST/PUT時 |
| Authorization | Bearer {token} | ○ | 認証が必要なエンドポイント |
| Accept | application/json | - | - |

### レスポンス形式

#### 成功時
```json
{
  "status": "success",
  "data": {
    // レスポンスデータ
  },
  "meta": {
    "timestamp": "2025-12-31T10:00:00Z"
  }
}
```

#### エラー時
```json
{
  "status": "error",
  "error": {
    "code": "ERROR_CODE",
    "message": "エラーメッセージ",
    "details": [
      {
        "field": "email",
        "message": "メールアドレスの形式が正しくありません"
      }
    ]
  },
  "meta": {
    "timestamp": "2025-12-31T10:00:00Z"
  }
}
```

### HTTPステータスコード

| コード | 説明 |
|--------|------|
| 200 | OK - 成功 |
| 201 | Created - 作成成功 |
| 204 | No Content - 削除成功 |
| 400 | Bad Request - リクエストが不正 |
| 401 | Unauthorized - 認証エラー |
| 403 | Forbidden - 権限エラー |
| 404 | Not Found - リソースが存在しない |
| 409 | Conflict - 競合エラー |
| 422 | Unprocessable Entity - バリデーションエラー |
| 500 | Internal Server Error - サーバーエラー |

### ページネーション

リスト取得系APIは以下のクエリパラメータでページネーションに対応

| パラメータ | 型 | デフォルト値 | 説明 |
|-----------|-----|-------------|------|
| page | integer | 1 | ページ番号 |
| per_page | integer | 20 | 1ページあたりの件数（最大100） |

#### ページネーション付きレスポンス例
```json
{
  "status": "success",
  "data": [
    // データ配列
  ],
  "meta": {
    "pagination": {
      "current_page": 1,
      "per_page": 20,
      "total_pages": 5,
      "total_count": 95
    },
    "timestamp": "2025-12-31T10:00:00Z"
  }
}
```

---

## 認証API

### ログイン

ユーザー認証を行い、アクセストークンを取得

- **Endpoint**: `POST /api/auth/login`
- **認証**: 不要

#### リクエスト
```json
{
  "email": "user@example.com",
  "password": "password123",
  "remember_me": false
}
```

#### レスポンス (200 OK)
```json
{
  "status": "success",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "expires_in": 3600,
    "user": {
      "id": 1,
      "name": "山田太郎",
      "email": "user@example.com",
      "role": "sales",
      "position": "営業担当",
      "company_id": 1
    }
  }
}
```

#### エラーレスポンス
- **401 Unauthorized**: 認証失敗
```json
{
  "status": "error",
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "メールアドレスまたはパスワードが正しくありません"
  }
}
```

---

### ログアウト

アクセストークンを無効化

- **Endpoint**: `POST /api/auth/logout`
- **認証**: 必要

#### リクエスト
```json
{}
```

#### レスポンス (200 OK)
```json
{
  "status": "success",
  "data": {
    "message": "ログアウトしました"
  }
}
```

---

### トークンリフレッシュ

リフレッシュトークンを使用して新しいアクセストークンを取得

- **Endpoint**: `POST /api/auth/refresh`
- **認証**: 不要（リフレッシュトークンが必要）

#### リクエスト
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### レスポンス (200 OK)
```json
{
  "status": "success",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "expires_in": 3600
  }
}
```

---

## 日報API

### 日報一覧取得

日報の一覧を取得。検索条件でフィルタリング可能

- **Endpoint**: `GET /api/daily-reports`
- **認証**: 必要
- **権限コード**: `report.view_all` OR `report.view_self`
  - `report.view_all`: 全ユーザーの日報を閲覧可能
  - `report.view_self`: 自分の日報のみ閲覧可能

#### クエリパラメータ

| パラメータ | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| page | integer | - | ページ番号（デフォルト: 1） |
| per_page | integer | - | 1ページあたりの件数（デフォルト: 20） |
| date_from | date | - | 検索期間（開始）YYYY-MM-DD |
| date_to | date | - | 検索期間（終了）YYYY-MM-DD |
| user_id | integer | - | 対象ユーザーID（上長のみ指定可） |
| sort | string | - | ソート項目（report_date, created_at） |
| order | string | - | ソート順（asc, desc）デフォルト: desc |

#### レスポンス (200 OK)
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "user_id": 5,
      "user_name": "山田太郎",
      "report_date": "2025-12-30",
      "visit_count": 3,
      "problem_count": 1,
      "plan_count": 2,
      "comment_count": 1,
      "created_at": "2025-12-30T18:00:00Z",
      "updated_at": "2025-12-30T18:30:00Z"
    }
  ],
  "meta": {
    "pagination": {
      "current_page": 1,
      "per_page": 20,
      "total_pages": 3,
      "total_count": 52
    }
  }
}
```

---

### 日報詳細取得

指定IDの日報詳細を取得

- **Endpoint**: `GET /api/daily-reports/{id}`
- **認証**: 必要
- **権限コード**: `report.view_all` OR `report.view_self`
  - `report.view_all`: 全ユーザーの日報を閲覧可能
  - `report.view_self`: 自分の日報のみ閲覧可能

#### レスポンス (200 OK)
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "user_id": 5,
    "user_name": "山田太郎",
    "report_date": "2025-12-30",
    "visit_records": [
      {
        "id": 1,
        "customer_id": 10,
        "customer_name": "田中商事",
        "visit_datetime": "2025-12-30T10:00:00Z",
        "remote": false,
        "visit_content": "新商品の提案を実施",
        "result": "検討していただけることになった",
        "created_at": "2025-12-30T18:00:00Z"
      }
    ],
    "problems": [
      {
        "id": 1,
        "content": "競合他社の価格が安い",
        "priority": "high",
        "status": "pending",
        "created_at": "2025-12-30T18:00:00Z"
      }
    ],
    "plans": [
      {
        "id": 1,
        "content": "見積書を作成して提出",
        "priority": "high",
        "created_at": "2025-12-30T18:00:00Z"
      }
    ],
    "comments": [
      {
        "id": 1,
        "commenter_id": 2,
        "commenter_name": "佐藤課長",
        "content": "良い提案ですね。価格交渉の余地を確認してください。",
        "commented_at": "2025-12-30T20:00:00Z"
      }
    ],
    "created_at": "2025-12-30T18:00:00Z",
    "updated_at": "2025-12-30T18:30:00Z"
  }
}
```

#### エラーレスポンス
- **404 Not Found**: 日報が存在しない
- **403 Forbidden**: アクセス権限がない

---

### 日報作成

新規日報を作成

- **Endpoint**: `POST /api/daily-reports`
- **認証**: 必要
- **権限コード**: `report.create`

#### リクエスト
```json
{
  "report_date": "2025-12-30",
  "visit_records": [
    {
      "customer_id": 10,
      "visit_datetime": "2025-12-30T10:00:00Z",
      "remote": false,
      "visit_content": "新商品の提案を実施",
      "result": "検討していただけることになった"
    }
  ],
  "problems": [
    {
      "content": "競合他社の価格が安い",
      "priority": "high"
    }
  ],
  "plans": [
    {
      "content": "見積書を作成して提出",
      "priority": "high"
    }
  ]
}
```

#### レスポンス (201 Created)
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "user_id": 5,
    "report_date": "2025-12-30",
    "created_at": "2025-12-30T18:00:00Z"
  }
}
```

#### エラーレスポンス
- **422 Unprocessable Entity**: バリデーションエラー
```json
{
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "入力内容に誤りがあります",
    "details": [
      {
        "field": "report_date",
        "message": "報告日は本日以前を指定してください"
      },
      {
        "field": "visit_records",
        "message": "訪問記録を1件以上登録してください"
      }
    ]
  }
}
```

---

### 日報更新

既存の日報を更新

- **Endpoint**: `PUT /api/daily-reports/{id}`
- **認証**: 必要
- **権限コード**: `report.update` OR `report.update_self`
  - `report.update`: 全ユーザーの日報を更新可能
  - `report.update_self`: 自分の日報のみ更新可能

#### リクエスト
```json
{
  "report_date": "2025-12-30",
  "visit_records": [
    {
      "id": 1,
      "customer_id": 10,
      "visit_datetime": "2025-12-30T10:00:00Z",
      "remote": false,
      "visit_content": "新商品の提案を実施（更新）",
      "result": "検討していただけることになった"
    }
  ],
  "problems": [
    {
      "id": 1,
      "content": "競合他社の価格が安い",
      "priority": "high"
    }
  ],
  "plans": [
    {
      "id": 1,
      "content": "見積書を作成して提出",
      "priority": "high"
    }
  ]
}
```

#### レスポンス (200 OK)
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "user_id": 5,
    "report_date": "2025-12-30",
    "updated_at": "2025-12-31T10:00:00Z"
  }
}
```

#### エラーレスポンス
- **403 Forbidden**: 編集期限切れまたは権限なし
```json
{
  "status": "error",
  "error": {
    "code": "EDIT_DEADLINE_EXCEEDED",
    "message": "編集期限を過ぎています"
  }
}
```

---

### 日報削除

日報を削除

- **Endpoint**: `DELETE /api/daily-reports/{id}`
- **認証**: 必要
- **権限コード**: `report.delete` OR `report.delete_self`
  - `report.delete`: 全ユーザーの日報を削除可能
  - `report.delete_self`: 自分の日報のみ削除可能

#### レスポンス (204 No Content)
```
（レスポンスボディなし）
```

#### エラーレスポンス
- **403 Forbidden**: 削除権限なし
- **404 Not Found**: 日報が存在しない

---

### ダッシュボード情報取得

ダッシュボード表示用のサマリー情報を取得

- **Endpoint**: `GET /api/daily-reports/dashboard`
- **認証**: 必要
- **権限**: 全ユーザー

#### レスポンス (200 OK)
```json
{
  "status": "success",
  "data": {
    "today": {
      "report_created": true,
      "visit_count": 3,
      "problem_count": 1
    },
    "this_week": {
      "visit_count": 15,
      "customer_count": 8,
      "visit_ratio": {
        "remote": 40,
        "onsite": 60
      }
    },
    "unread_comments": [
      {
        "daily_report_id": 1,
        "report_date": "2025-12-30",
        "commenter_name": "佐藤課長",
        "comment_preview": "良い提案ですね。価格交渉の...",
        "commented_at": "2025-12-30T20:00:00Z"
      }
    ]
  }
}
```

---

## 訪問記録API

### 訪問記録追加

日報に訪問記録を追加

- **Endpoint**: `POST /api/daily-reports/{daily_report_id}/visit-records`
- **認証**: 必要
- **権限**: 日報作成者本人

#### リクエスト
```json
{
  "customer_id": 10,
  "visit_datetime": "2025-12-30T14:00:00Z",
  "remote": false,
  "visit_content": "追加の商談",
  "result": "次回訪問のアポを取得"
}
```

#### レスポンス (201 Created)
```json
{
  "status": "success",
  "data": {
    "id": 2,
    "daily_report_id": 1,
    "customer_id": 10,
    "visit_datetime": "2025-12-30T14:00:00Z",
    "remote": false,
    "visit_content": "追加の商談",
    "result": "次回訪問のアポを取得",
    "created_at": "2025-12-30T19:00:00Z"
  }
}
```

---

### 訪問記録更新

訪問記録を更新

- **Endpoint**: `PUT /api/visit-records/{id}`
- **認証**: 必要
- **権限**: 日報作成者本人

#### リクエスト
```json
{
  "customer_id": 10,
  "visit_datetime": "2025-12-30T14:00:00Z",
  "remote": true,
  "visit_content": "追加の商談（リモート）",
  "result": "次回訪問のアポを取得"
}
```

#### レスポンス (200 OK)
```json
{
  "status": "success",
  "data": {
    "id": 2,
    "updated_at": "2025-12-30T19:30:00Z"
  }
}
```

---

### 訪問記録削除

訪問記録を削除

- **Endpoint**: `DELETE /api/visit-records/{id}`
- **認証**: 必要
- **権限**: 日報作成者本人

#### レスポンス (204 No Content)
```
（レスポンスボディなし）
```

---

## 課題API

### 課題追加

日報に課題を追加

- **Endpoint**: `POST /api/daily-reports/{daily_report_id}/problems`
- **認証**: 必要
- **権限**: 日報作成者本人

#### リクエスト
```json
{
  "content": "納期調整が必要",
  "priority": "medium"
}
```

#### レスポンス (201 Created)
```json
{
  "status": "success",
  "data": {
    "id": 2,
    "daily_report_id": 1,
    "content": "納期調整が必要",
    "priority": "medium",
    "status": "pending",
    "created_at": "2025-12-30T19:00:00Z"
  }
}
```

---

### 課題更新

課題を更新

- **Endpoint**: `PUT /api/problems/{id}`
- **認証**: 必要
- **権限**: 日報作成者本人

#### リクエスト
```json
{
  "content": "納期調整が必要（更新）",
  "priority": "high",
  "status": "resolved"
}
```

#### レスポンス (200 OK)
```json
{
  "status": "success",
  "data": {
    "id": 2,
    "updated_at": "2025-12-31T10:00:00Z"
  }
}
```

---

### 課題削除

課題を削除

- **Endpoint**: `DELETE /api/problems/{id}`
- **認証**: 必要
- **権限**: 日報作成者本人

#### レスポンス (204 No Content)
```
（レスポンスボディなし）
```

---

## 計画API

### 計画追加

日報に計画を追加

- **Endpoint**: `POST /api/daily-reports/{daily_report_id}/plans`
- **認証**: 必要
- **権限**: 日報作成者本人

#### リクエスト
```json
{
  "content": "A社へ新商品の提案",
  "priority": "high"
}
```

#### レスポンス (201 Created)
```json
{
  "status": "success",
  "data": {
    "id": 3,
    "daily_report_id": 1,
    "content": "A社へ新商品の提案",
    "priority": "high",
    "created_at": "2025-12-30T19:00:00Z"
  }
}
```

---

### 計画更新

計画を更新

- **Endpoint**: `PUT /api/plans/{id}`
- **認証**: 必要
- **権限**: 日報作成者本人

#### リクエスト
```json
{
  "content": "A社とB社へ新商品の提案",
  "priority": "high"
}
```

#### レスポンス (200 OK)
```json
{
  "status": "success",
  "data": {
    "id": 3,
    "updated_at": "2025-12-31T10:00:00Z"
  }
}
```

---

### 計画削除

計画を削除

- **Endpoint**: `DELETE /api/plans/{id}`
- **認証**: 必要
- **権限**: 日報作成者本人

#### レスポンス (204 No Content)
```
（レスポンスボディなし）
```

---

## コメントAPI

### コメント一覧取得

日報に対するコメント一覧を取得

- **Endpoint**: `GET /api/daily-reports/{daily_report_id}/comments`
- **認証**: 必要
- **権限**: 日報作成者本人、上長

#### レスポンス (200 OK)
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "daily_report_id": 1,
      "commenter_id": 2,
      "commenter_name": "佐藤課長",
      "content": "良い提案ですね。価格交渉の余地を確認してください。",
      "commented_at": "2025-12-30T20:00:00Z",
      "created_at": "2025-12-30T20:00:00Z"
    }
  ]
}
```

---

### コメント追加

日報にコメントを追加

- **Endpoint**: `POST /api/daily-reports/{daily_report_id}/comments`
- **認証**: 必要
- **権限**: 上長

#### リクエスト
```json
{
  "content": "価格交渉頑張ってください"
}
```

#### レスポンス (201 Created)
```json
{
  "status": "success",
  "data": {
    "id": 2,
    "daily_report_id": 1,
    "commenter_id": 2,
    "content": "価格交渉頑張ってください",
    "commented_at": "2025-12-31T10:00:00Z"
  }
}
```

---

### コメント削除

コメントを削除

- **Endpoint**: `DELETE /api/comments/{id}`
- **認証**: 必要
- **権限**: コメント作成者本人

#### レスポンス (204 No Content)
```
（レスポンスボディなし）
```

---

## 顧客マスタAPI

### 顧客一覧取得

顧客マスタの一覧を取得

- **Endpoint**: `GET /api/customers`
- **認証**: 必要
- **権限コード**: `customer.view`

#### クエリパラメータ

| パラメータ | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| page | integer | - | ページ番号 |
| per_page | integer | - | 1ページあたりの件数 |
| keyword | string | - | 検索キーワード（顧客名、会社名） |
| assigned_user_id | integer | - | 担当営業ID |
| sort | string | - | ソート項目 |
| order | string | - | ソート順 |

#### レスポンス (200 OK)
```json
{
  "status": "success",
  "data": [
    {
      "id": 10,
      "name": "田中太郎",
      "company_name": "田中商事",
      "address": "東京都渋谷区...",
      "phone": "03-1234-5678",
      "email": "tanaka@example.com",
      "assigned_user_id": 5,
      "assigned_user_name": "山田太郎",
      "last_visit_date": "2025-12-30",
      "created_at": "2025-01-15T10:00:00Z",
      "updated_at": "2025-12-30T18:00:00Z"
    }
  ],
  "meta": {
    "pagination": {
      "current_page": 1,
      "per_page": 20,
      "total_pages": 5,
      "total_count": 95
    }
  }
}
```

---

### 顧客詳細取得

指定IDの顧客詳細を取得

- **Endpoint**: `GET /api/customers/{id}`
- **認証**: 必要
- **権限コード**: `customer.view`

#### レスポンス (200 OK)
```json
{
  "status": "success",
  "data": {
    "id": 10,
    "company_id": 1,
    "assigned_user_id": 5,
    "assigned_user_name": "山田太郎",
    "name": "田中太郎",
    "company_name": "田中商事",
    "address": "東京都渋谷区...",
    "phone": "03-1234-5678",
    "email": "tanaka@example.com",
    "notes": "重要顧客",
    "last_visit_date": "2025-12-30",
    "visit_count": 15,
    "created_at": "2025-01-15T10:00:00Z",
    "updated_at": "2025-12-30T18:00:00Z"
  }
}
```

---

### 顧客登録

新規顧客を登録

- **Endpoint**: `POST /api/customers`
- **認証**: 必要
- **権限コード**: `customer.create`

#### リクエスト
```json
{
  "name": "鈴木一郎",
  "company_name": "鈴木物産",
  "address": "東京都新宿区...",
  "phone": "03-9876-5432",
  "email": "suzuki@example.com",
  "assigned_user_id": 5,
  "notes": "新規開拓顧客"
}
```

#### レスポンス (201 Created)
```json
{
  "status": "success",
  "data": {
    "id": 11,
    "name": "鈴木一郎",
    "company_name": "鈴木物産",
    "created_at": "2025-12-31T10:00:00Z"
  }
}
```

---

### 顧客更新

顧客情報を更新

- **Endpoint**: `PUT /api/customers/{id}`
- **認証**: 必要
- **権限コード**: `customer.update` OR `customer.update_self`
  - `customer.update`: 全顧客の情報を更新可能
  - `customer.update_self`: 自分が担当する顧客のみ更新可能

#### リクエスト
```json
{
  "name": "鈴木一郎",
  "company_name": "鈴木物産株式会社",
  "address": "東京都新宿区...",
  "phone": "03-9876-5432",
  "email": "suzuki@example.com",
  "assigned_user_id": 5,
  "notes": "重要顧客に昇格"
}
```

#### レスポンス (200 OK)
```json
{
  "status": "success",
  "data": {
    "id": 11,
    "updated_at": "2025-12-31T11:00:00Z"
  }
}
```

---

### 顧客削除

顧客を削除

- **Endpoint**: `DELETE /api/customers/{id}`
- **認証**: 必要
- **権限コード**: `customer.delete` OR `customer.delete_self`
  - `customer.delete`: 全顧客を削除可能
  - `customer.delete_self`: 自分が担当する顧客のみ削除可能

#### レスポンス (204 No Content)
```
（レスポンスボディなし）
```

#### エラーレスポンス
- **409 Conflict**: 訪問記録が存在する顧客
```json
{
  "status": "error",
  "error": {
    "code": "CUSTOMER_HAS_VISITS",
    "message": "この顧客には訪問記録が存在するため削除できません"
  }
}
```

---

## ユーザーマスタAPI

### ユーザー一覧取得

ユーザーマスタの一覧を取得

- **Endpoint**: `GET /api/users`
- **認証**: 必要
- **権限コード**: `user.view`

#### クエリパラメータ

| パラメータ | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| page | integer | - | ページ番号 |
| per_page | integer | - | 1ページあたりの件数 |
| keyword | string | - | 検索キーワード（氏名、メールアドレス） |
| role | string | - | 役割（sales, manager, admin） |
| status | string | - | ステータス（active, inactive） |

#### レスポンス (200 OK)
```json
{
  "status": "success",
  "data": [
    {
      "id": 5,
      "company_id": 1,
      "name": "山田太郎",
      "email": "yamada@example.com",
      "role": "sales",
      "position": "営業担当",
      "status": "active",
      "created_at": "2025-01-10T10:00:00Z",
      "updated_at": "2025-12-30T18:00:00Z"
    }
  ],
  "meta": {
    "pagination": {
      "current_page": 1,
      "per_page": 20,
      "total_pages": 2,
      "total_count": 35
    }
  }
}
```

---

### ユーザー詳細取得

指定IDのユーザー詳細を取得

- **Endpoint**: `GET /api/users/{id}`
- **認証**: 必要
- **権限コード**: `user.view`

#### レスポンス (200 OK)
```json
{
  "status": "success",
  "data": {
    "id": 5,
    "company_id": 1,
    "company_name": "サンプル商事株式会社",
    "name": "山田太郎",
    "email": "yamada@example.com",
    "role": "sales",
    "position": "営業担当",
    "status": "active",
    "created_at": "2025-01-10T10:00:00Z",
    "updated_at": "2025-12-30T18:00:00Z"
  }
}
```

---

### 自分のユーザー情報取得

ログインユーザー自身の情報を取得

- **Endpoint**: `GET /api/users/me`
- **認証**: 必要
- **権限コード**: 認証済みユーザー（権限チェックなし）

#### レスポンス (200 OK)
```json
{
  "status": "success",
  "data": {
    "id": 5,
    "company_id": 1,
    "company_name": "サンプル商事株式会社",
    "name": "山田太郎",
    "email": "yamada@example.com",
    "role": "sales",
    "position": "営業担当",
    "status": "active",
    "created_at": "2025-01-10T10:00:00Z",
    "updated_at": "2025-12-30T18:00:00Z"
  }
}
```

---

### ユーザー登録

新規ユーザーを登録

- **Endpoint**: `POST /api/users`
- **認証**: 必要
- **権限コード**: `user.create`

#### リクエスト
```json
{
  "name": "佐藤花子",
  "email": "sato@example.com",
  "password": "password123",
  "role": "sales",
  "position": "営業担当"
}
```

#### レスポンス (201 Created)
```json
{
  "status": "success",
  "data": {
    "id": 6,
    "name": "佐藤花子",
    "email": "sato@example.com",
    "role": "sales",
    "created_at": "2025-12-31T10:00:00Z"
  }
}
```

---

### ユーザー更新

ユーザー情報を更新

- **Endpoint**: `PUT /api/users/{id}`
- **認証**: 必要
- **権限コード**: `user.update` OR `user.update_self`
  - `user.update`: 全ユーザーの情報を更新可能
  - `user.update_self`: 自分の情報のみ更新可能

#### リクエスト
```json
{
  "name": "佐藤花子",
  "role": "manager",
  "position": "営業課長",
  "status": "active"
}
```

#### レスポンス (200 OK)
```json
{
  "status": "success",
  "data": {
    "id": 6,
    "updated_at": "2025-12-31T11:00:00Z"
  }
}
```

---

### ユーザー削除

ユーザーを削除

- **Endpoint**: `DELETE /api/users/{id}`
- **認証**: 必要
- **権限コード**: `user.delete`

#### レスポンス (204 No Content)
```
（レスポンスボディなし）
```

#### エラーレスポンス
- **409 Conflict**: 日報が存在するユーザー
```json
{
  "status": "error",
  "error": {
    "code": "USER_HAS_REPORTS",
    "message": "このユーザーには日報が存在するため削除できません"
  }
}
```

---

## 企業API

### 企業一覧取得

企業の一覧を取得

- **Endpoint**: `GET /api/companies`
- **認証**: 必要
- **権限コード**: `company.view`

#### レスポンス (200 OK)
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "name": "サンプル商事株式会社",
      "address": "東京都千代田区...",
      "phone": "03-0000-0000",
      "created_at": "2025-01-01T00:00:00Z",
      "updated_at": "2025-01-01T00:00:00Z"
    }
  ]
}
```

---

### 企業詳細取得

指定IDの企業詳細を取得

- **Endpoint**: `GET /api/companies/{id}`
- **認証**: 必要
- **権限コード**: `company.view`
  - 注: 所属企業の情報のみ閲覧可能（実行時チェック）

#### レスポンス (200 OK)
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "name": "サンプル商事株式会社",
    "address": "東京都千代田区...",
    "phone": "03-0000-0000",
    "user_count": 35,
    "customer_count": 120,
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z"
  }
}
```

---

## 支店マスタAPI

### 支店一覧取得

支店マスタの一覧を取得

- **Endpoint**: `GET /api/branches`
- **認証**: 必要
- **権限コード**: `branch.view`

#### クエリパラメータ

| パラメータ | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| page | integer | - | ページ番号 |
| per_page | integer | - | 1ページあたりの件数 |
| keyword | string | - | 検索キーワード（支店名、住所） |

#### レスポンス (200 OK)
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "company_id": 1,
      "name": "東京支店",
      "address": "東京都渋谷区...",
      "phone": "03-1234-5678",
      "department_count": 3,
      "user_count": 15,
      "created_at": "2025-01-01T00:00:00Z",
      "updated_at": "2025-01-01T00:00:00Z"
    }
  ],
  "meta": {
    "pagination": {
      "current_page": 1,
      "per_page": 20,
      "total_pages": 2,
      "total_count": 25
    }
  }
}
```

---

### 支店詳細取得

指定IDの支店詳細を取得

- **Endpoint**: `GET /api/branches/{id}`
- **認証**: 必要
- **権限コード**: `branch.view`

#### レスポンス (200 OK)
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "company_id": 1,
    "name": "東京支店",
    "address": "東京都渋谷区...",
    "phone": "03-1234-5678",
    "department_count": 3,
    "user_count": 15,
    "departments": [
      {
        "id": 1,
        "name": "営業部",
        "user_count": 10
      }
    ],
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z"
  }
}
```

---

### 支店登録

新規支店を登録

- **Endpoint**: `POST /api/branches`
- **認証**: 必要
- **権限コード**: `branch.create`

#### リクエスト
```json
{
  "name": "大阪支店",
  "address": "大阪府大阪市...",
  "phone": "06-1234-5678"
}
```

#### レスポンス (201 Created)
```json
{
  "status": "success",
  "data": {
    "id": 2,
    "name": "大阪支店",
    "created_at": "2025-12-31T10:00:00Z"
  }
}
```

---

### 支店更新

支店情報を更新

- **Endpoint**: `PUT /api/branches/{id}`
- **認証**: 必要
- **権限コード**: `branch.update`

#### リクエスト
```json
{
  "name": "大阪支店",
  "address": "大阪府大阪市中央区...",
  "phone": "06-1234-5678"
}
```

#### レスポンス (200 OK)
```json
{
  "status": "success",
  "data": {
    "id": 2,
    "updated_at": "2025-12-31T11:00:00Z"
  }
}
```

---

### 支店削除

支店を削除

- **Endpoint**: `DELETE /api/branches/{id}`
- **認証**: 必要
- **権限コード**: `branch.delete`

#### レスポンス (204 No Content)
```
（レスポンスボディなし）
```

#### エラーレスポンス
- **409 Conflict**: 部署が存在する支店
```json
{
  "status": "error",
  "error": {
    "code": "BRANCH_HAS_DEPARTMENTS",
    "message": "この支店には部署が存在するため削除できません"
  }
}
```

---

## 部署マスタAPI

### 部署一覧取得

部署マスタの一覧を取得

- **Endpoint**: `GET /api/departments`
- **認証**: 必要
- **権限コード**: `department.view`

#### クエリパラメータ

| パラメータ | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| page | integer | - | ページ番号 |
| per_page | integer | - | 1ページあたりの件数 |
| branch_id | integer | - | 支店IDで絞り込み |
| keyword | string | - | 検索キーワード（部署名） |

#### レスポンス (200 OK)
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "branch_id": 1,
      "branch_name": "東京支店",
      "name": "営業部",
      "description": "営業活動を担当",
      "user_count": 10,
      "created_at": "2025-01-01T00:00:00Z",
      "updated_at": "2025-01-01T00:00:00Z"
    }
  ],
  "meta": {
    "pagination": {
      "current_page": 1,
      "per_page": 20,
      "total_pages": 3,
      "total_count": 45
    }
  }
}
```

---

### 部署詳細取得

指定IDの部署詳細を取得

- **Endpoint**: `GET /api/departments/{id}`
- **認証**: 必要
- **権限コード**: `department.view`

#### レスポンス (200 OK)
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "branch_id": 1,
    "branch_name": "東京支店",
    "name": "営業部",
    "description": "営業活動を担当",
    "user_count": 10,
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z"
  }
}
```

---

### 部署登録

新規部署を登録

- **Endpoint**: `POST /api/departments`
- **認証**: 必要
- **権限コード**: `department.create`

#### リクエスト
```json
{
  "branch_id": 1,
  "name": "総務部",
  "description": "総務・人事業務を担当"
}
```

#### レスポンス (201 Created)
```json
{
  "status": "success",
  "data": {
    "id": 2,
    "branch_id": 1,
    "name": "総務部",
    "created_at": "2025-12-31T10:00:00Z"
  }
}
```

---

### 部署更新

部署情報を更新

- **Endpoint**: `PUT /api/departments/{id}`
- **認証**: 必要
- **権限コード**: `department.update`

#### リクエスト
```json
{
  "branch_id": 1,
  "name": "総務部",
  "description": "総務・人事・労務業務を担当"
}
```

#### レスポンス (200 OK)
```json
{
  "status": "success",
  "data": {
    "id": 2,
    "updated_at": "2025-12-31T11:00:00Z"
  }
}
```

---

### 部署削除

部署を削除

- **Endpoint**: `DELETE /api/departments/{id}`
- **認証**: 必要
- **権限コード**: `department.delete`

#### レスポンス (204 No Content)
```
（レスポンスボディなし）
```

#### エラーレスポンス
- **409 Conflict**: ユーザーが所属する部署
```json
{
  "status": "error",
  "error": {
    "code": "DEPARTMENT_HAS_USERS",
    "message": "この部署にはユーザーが所属しているため削除できません"
  }
}
```

---

## ユーザー所属管理API

### ユーザー所属情報取得

指定ユーザーの支店・部署所属情報を取得

- **Endpoint**: `GET /api/users/{user_id}/assignments`
- **認証**: 必要
- **権限コード**: `user.view`
  - 注: 管理者または本人のみアクセス可能（実行時チェック）

#### レスポンス (200 OK)
```json
{
  "status": "success",
  "data": {
    "user_id": 5,
    "user_name": "山田太郎",
    "branch_assignments": [
      {
        "id": 1,
        "branch_id": 1,
        "branch_name": "東京支店",
        "is_primary": true,
        "created_at": "2025-01-10T00:00:00Z"
      }
    ],
    "department_assignments": [
      {
        "id": 1,
        "department_id": 1,
        "department_name": "営業部",
        "branch_name": "東京支店",
        "is_primary": true,
        "created_at": "2025-01-10T00:00:00Z"
      }
    ]
  }
}
```

---

### 支店所属追加

ユーザーを支店に所属させる

- **Endpoint**: `POST /api/users/{user_id}/branches`
- **認証**: 必要
- **権限コード**: `user.update`

#### リクエスト
```json
{
  "branch_id": 2,
  "is_primary": false
}
```

#### レスポンス (201 Created)
```json
{
  "status": "success",
  "data": {
    "id": 2,
    "user_id": 5,
    "branch_id": 2,
    "branch_name": "大阪支店",
    "is_primary": false,
    "created_at": "2025-12-31T10:00:00Z"
  }
}
```

---

### 支店所属削除

ユーザーの支店所属を削除

- **Endpoint**: `DELETE /api/users/{user_id}/branches/{branch_id}`
- **認証**: 必要
- **権限コード**: `user.update`

#### レスポンス (204 No Content)
```
（レスポンスボディなし）
```

#### エラーレスポンス
- **400 Bad Request**: 最後の支店所属を削除しようとした場合
```json
{
  "status": "error",
  "error": {
    "code": "LAST_BRANCH_ASSIGNMENT",
    "message": "最低1つの支店に所属させる必要があります"
  }
}
```

---

### 主所属支店設定

ユーザーの主所属支店を変更

- **Endpoint**: `PUT /api/users/{user_id}/branches/{branch_id}/primary`
- **認証**: 必要
- **権限コード**: `user.update`

#### レスポンス (200 OK)
```json
{
  "status": "success",
  "data": {
    "user_id": 5,
    "primary_branch_id": 2,
    "updated_at": "2025-12-31T10:00:00Z"
  }
}
```

---

### 部署所属追加

ユーザーを部署に所属させる

- **Endpoint**: `POST /api/users/{user_id}/departments`
- **認証**: 必要
- **権限コード**: `user.update`

#### リクエスト
```json
{
  "department_id": 2,
  "is_primary": false
}
```

#### レスポンス (201 Created)
```json
{
  "status": "success",
  "data": {
    "id": 2,
    "user_id": 5,
    "department_id": 2,
    "department_name": "総務部",
    "is_primary": false,
    "created_at": "2025-12-31T10:00:00Z"
  }
}
```

---

### 部署所属削除

ユーザーの部署所属を削除

- **Endpoint**: `DELETE /api/users/{user_id}/departments/{department_id}`
- **認証**: 必要
- **権限コード**: `user.update`

#### レスポンス (204 No Content)
```
（レスポンスボディなし）
```

#### エラーレスポンス
- **400 Bad Request**: 最後の部署所属を削除しようとした場合
```json
{
  "status": "error",
  "error": {
    "code": "LAST_DEPARTMENT_ASSIGNMENT",
    "message": "最低1つの部署に所属させる必要があります"
  }
}
```

---

### 主所属部署設定

ユーザーの主所属部署を変更

- **Endpoint**: `PUT /api/users/{user_id}/departments/{department_id}/primary`
- **認証**: 必要
- **権限コード**: `user.update`

#### レスポンス (200 OK)
```json
{
  "status": "success",
  "data": {
    "user_id": 5,
    "primary_department_id": 2,
    "updated_at": "2025-12-31T10:00:00Z"
  }
}
```

---

## サービスマスタAPI

### サービス一覧取得

提供可能なオプションサービスの一覧を取得

- **Endpoint**: `GET /api/services`
- **認証**: 必要
- **権限コード**: `service.view` OR `subscription.view`

#### クエリパラメータ

| パラメータ | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| search | string | - | サービス名での部分一致検索 |
| is_active | boolean | - | 提供状態フィルタ（true/false） |
| page | integer | - | ページ番号（デフォルト: 1） |
| per_page | integer | - | 1ページあたり件数（デフォルト: 20） |

#### レスポンス (200 OK)
```json
{
  "status": "success",
  "data": {
    "services": [
      {
        "id": 1,
        "service_code": "DAILY_REPORT",
        "service_name": "営業日報サービス",
        "description": "日々の営業活動を記録・管理するサービス",
        "base_price": 5000,
        "is_active": true,
        "created_at": "2025-12-31T10:00:00Z",
        "updated_at": "2025-12-31T10:00:00Z"
      }
    ],
    "pagination": {
      "current_page": 1,
      "per_page": 20,
      "total_pages": 1,
      "total_count": 1
    }
  }
}
```

---

### サービス詳細取得

指定したサービスの詳細情報を取得

- **Endpoint**: `GET /api/services/{service_id}`
- **認証**: 必要
- **権限コード**: `service.view`

#### レスポンス (200 OK)
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "service_code": "DAILY_REPORT",
    "service_name": "営業日報サービス",
    "description": "日々の営業活動を記録・管理するサービス",
    "base_price": 5000,
    "is_active": true,
    "created_at": "2025-12-31T10:00:00Z",
    "updated_at": "2025-12-31T10:00:00Z"
  }
}
```

---

### サービス登録

新規オプションサービスを登録

- **Endpoint**: `POST /api/services`
- **認証**: 必要
- **権限コード**: `service.create`

#### リクエスト
```json
{
  "service_code": "DAILY_REPORT",
  "service_name": "営業日報サービス",
  "description": "日々の営業活動を記録・管理するサービス",
  "base_price": 5000,
  "is_active": true
}
```

#### バリデーション
- `service_code`: 必須、半角英数大文字アンダースコアのみ、最大50文字、ユニーク
- `service_name`: 必須、最大100文字
- `description`: 任意、最大500文字
- `base_price`: 必須、0以上の数値
- `is_active`: 任意、真偽値（デフォルト: true）

#### レスポンス (201 Created)
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "service_code": "DAILY_REPORT",
    "service_name": "営業日報サービス",
    "description": "日々の営業活動を記録・管理するサービス",
    "base_price": 5000,
    "is_active": true,
    "created_at": "2025-12-31T10:00:00Z",
    "updated_at": "2025-12-31T10:00:00Z"
  }
}
```

#### エラーレスポンス
- **409 Conflict**: サービスコードが重複
```json
{
  "status": "error",
  "error": {
    "code": "DUPLICATE_SERVICE_CODE",
    "message": "このサービスコードは既に登録されています"
  }
}
```

---

### サービス更新

既存サービス情報を更新

- **Endpoint**: `PUT /api/services/{service_id}`
- **認証**: 必要
- **権限コード**: `service.update`

#### リクエスト
```json
{
  "service_name": "営業日報サービス（更新版）",
  "description": "日々の営業活動を記録・管理するサービス（更新）",
  "base_price": 6000,
  "is_active": true
}
```

#### バリデーション
- `service_code`: 変更不可（リクエストに含めない）
- その他はサービス登録と同様

#### レスポンス (200 OK)
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "service_code": "DAILY_REPORT",
    "service_name": "営業日報サービス（更新版）",
    "description": "日々の営業活動を記録・管理するサービス（更新）",
    "base_price": 6000,
    "is_active": true,
    "updated_at": "2025-12-31T11:00:00Z"
  }
}
```

---

### サービス削除

サービスを削除（論理削除推奨）

- **Endpoint**: `DELETE /api/services/{service_id}`
- **認証**: 必要
- **権限コード**: `service.delete`

#### レスポンス (204 No Content)
```
（レスポンスボディなし）
```

#### エラーレスポンス
- **409 Conflict**: 契約企業が存在する
```json
{
  "status": "error",
  "error": {
    "code": "SERVICE_HAS_SUBSCRIPTIONS",
    "message": "このサービスは契約企業が存在するため削除できません"
  }
}
```

---

## 企業サービス契約API

### 企業のサービス契約一覧取得

指定企業のサービス契約状況を取得

- **Endpoint**: `GET /api/companies/{company_id}/service-subscriptions`
- **認証**: 必要
- **権限コード**: `subscription.view`

#### レスポンス (200 OK)
```json
{
  "status": "success",
  "data": {
    "company_id": 1,
    "company_name": "株式会社サンプル",
    "subscriptions": [
      {
        "id": 1,
        "service_id": 1,
        "service_code": "DAILY_REPORT",
        "service_name": "営業日報サービス",
        "status": "active",
        "start_date": "2025-01-01",
        "end_date": null,
        "monthly_price": 5000,
        "created_at": "2025-12-31T10:00:00Z",
        "updated_at": "2025-12-31T10:00:00Z"
      }
    ]
  }
}
```

---

### サービス契約追加

企業に新規サービス契約を追加

- **Endpoint**: `POST /api/companies/{company_id}/service-subscriptions`
- **認証**: 必要
- **権限コード**: `service.subscribe`

#### リクエスト
```json
{
  "service_id": 1,
  "status": "active",
  "start_date": "2025-01-01",
  "end_date": null,
  "monthly_price": 5000
}
```

#### バリデーション
- `service_id`: 必須、存在するサービスID、未契約チェック
- `status`: 必須、"active"/"suspended"/"cancelled"のいずれか
- `start_date`: 必須、日付形式（YYYY-MM-DD）
- `end_date`: 任意、日付形式、start_date以降の日付、nullの場合は無期限
- `monthly_price`: 必須、0以上の数値

#### レスポンス (201 Created)
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "company_id": 1,
    "service_id": 1,
    "service_code": "DAILY_REPORT",
    "service_name": "営業日報サービス",
    "status": "active",
    "start_date": "2025-01-01",
    "end_date": null,
    "monthly_price": 5000,
    "created_at": "2025-12-31T10:00:00Z"
  }
}
```

#### エラーレスポンス
- **409 Conflict**: 既に契約済み
```json
{
  "status": "error",
  "error": {
    "code": "SERVICE_ALREADY_SUBSCRIBED",
    "message": "このサービスは既に契約済みです"
  }
}
```

---

### サービス契約更新

企業のサービス契約情報を更新

- **Endpoint**: `PUT /api/companies/{company_id}/service-subscriptions/{subscription_id}`
- **認証**: 必要
- **権限コード**: `subscription.update`

#### リクエスト
```json
{
  "status": "suspended",
  "end_date": "2025-12-31",
  "monthly_price": 6000
}
```

#### バリデーション
- `service_id`: 変更不可
- その他はサービス契約追加と同様

#### レスポンス (200 OK)
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "company_id": 1,
    "service_id": 1,
    "service_code": "DAILY_REPORT",
    "service_name": "営業日報サービス",
    "status": "suspended",
    "start_date": "2025-01-01",
    "end_date": "2025-12-31",
    "monthly_price": 6000,
    "updated_at": "2025-12-31T11:00:00Z"
  }
}
```

---

### サービス契約削除

企業のサービス契約を削除

- **Endpoint**: `DELETE /api/companies/{company_id}/service-subscriptions/{subscription_id}`
- **認証**: 必要
- **権限コード**: `service.unsubscribe`

#### レスポンス (204 No Content)
```
（レスポンスボディなし）
```

---

### サービス有効性チェック

企業が特定サービスを利用可能かチェック

- **Endpoint**: `GET /api/companies/{company_id}/service-subscriptions/check/{service_code}`
- **認証**: 必要
- **権限コード**: 認証済みユーザー（権限チェックなし）
  - 注: 所属企業の情報のみチェック可能（実行時チェック）

#### レスポンス (200 OK)
```json
{
  "status": "success",
  "data": {
    "service_code": "DAILY_REPORT",
    "service_name": "営業日報サービス",
    "is_available": true,
    "subscription_status": "active",
    "start_date": "2025-01-01",
    "end_date": null
  }
}
```

#### 契約なし・無効の場合
```json
{
  "status": "success",
  "data": {
    "service_code": "DAILY_REPORT",
    "service_name": "営業日報サービス",
    "is_available": false,
    "subscription_status": null,
    "start_date": null,
    "end_date": null
  }
}
```

---

### サービス契約変更履歴取得

特定のサービス契約の変更履歴を取得

- **Endpoint**: `GET /api/companies/{company_id}/service-subscriptions/{subscription_id}/history`
- **認証**: 必要
- **権限コード**: `subscription.history`

#### クエリパラメータ

| パラメータ | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| page | integer | - | ページ番号（デフォルト: 1） |
| per_page | integer | - | 1ページあたり件数（デフォルト: 20） |

#### レスポンス (200 OK)
```json
{
  "status": "success",
  "data": {
    "subscription_id": 1,
    "company_name": "株式会社サンプル",
    "service_name": "営業日報サービス",
    "history": [
      {
        "id": 3,
        "change_type": "update",
        "old_status": "active",
        "new_status": "suspended",
        "old_end_date": null,
        "new_end_date": "2025-12-31",
        "old_monthly_price": 5000,
        "new_monthly_price": 5000,
        "change_reason": "契約一時停止（顧客要望）",
        "changed_by_user_name": "システム管理者",
        "changed_at": "2025-12-31T14:00:00Z"
      },
      {
        "id": 2,
        "change_type": "update",
        "old_status": "active",
        "new_status": "active",
        "old_end_date": null,
        "new_end_date": null,
        "old_monthly_price": 5000,
        "new_monthly_price": 6000,
        "change_reason": "料金改定",
        "changed_by_user_name": "システム管理者",
        "changed_at": "2025-06-01T10:00:00Z"
      },
      {
        "id": 1,
        "change_type": "create",
        "old_status": null,
        "new_status": "active",
        "old_end_date": null,
        "new_end_date": null,
        "old_monthly_price": null,
        "new_monthly_price": 5000,
        "change_reason": "新規契約",
        "changed_by_user_name": "システム管理者",
        "changed_at": "2025-01-01T09:00:00Z"
      }
    ],
    "pagination": {
      "current_page": 1,
      "per_page": 20,
      "total_pages": 1,
      "total_count": 3
    }
  }
}
```

---

### 企業の全サービス契約変更履歴取得

企業の全サービス契約に関する変更履歴を取得

- **Endpoint**: `GET /api/companies/{company_id}/service-subscriptions/history`
- **認証**: 必要
- **権限コード**: `subscription.history`

#### クエリパラメータ

| パラメータ | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| service_id | integer | - | サービスIDでフィルタ |
| change_type | string | - | 変更種別でフィルタ（create/update/delete） |
| from_date | date | - | 変更日時の開始日（YYYY-MM-DD） |
| to_date | date | - | 変更日時の終了日（YYYY-MM-DD） |
| page | integer | - | ページ番号（デフォルト: 1） |
| per_page | integer | - | 1ページあたり件数（デフォルト: 20） |

#### レスポンス (200 OK)
```json
{
  "status": "success",
  "data": {
    "company_id": 1,
    "company_name": "株式会社サンプル",
    "history": [
      {
        "id": 3,
        "subscription_id": 1,
        "service_name": "営業日報サービス",
        "change_type": "update",
        "old_status": "active",
        "new_status": "suspended",
        "change_reason": "契約一時停止（顧客要望）",
        "changed_by_user_name": "システム管理者",
        "changed_at": "2025-12-31T14:00:00Z"
      },
      {
        "id": 2,
        "subscription_id": 2,
        "service_name": "顧客管理サービス",
        "change_type": "create",
        "old_status": null,
        "new_status": "active",
        "change_reason": "新規契約",
        "changed_by_user_name": "システム管理者",
        "changed_at": "2025-12-15T10:00:00Z"
      }
    ],
    "pagination": {
      "current_page": 1,
      "per_page": 20,
      "total_pages": 1,
      "total_count": 2
    }
  }
}
```

---

## エラーコード一覧

| エラーコード | HTTPステータス | 説明 |
|------------|--------------|------|
| INVALID_CREDENTIALS | 401 | 認証失敗（メールアドレスまたはパスワードが不正） |
| UNAUTHORIZED | 401 | 認証トークンが不正または期限切れ |
| FORBIDDEN | 403 | アクセス権限なし |
| NOT_FOUND | 404 | リソースが存在しない |
| VALIDATION_ERROR | 422 | バリデーションエラー |
| DUPLICATE_EMAIL | 409 | メールアドレスが既に登録されている |
| EDIT_DEADLINE_EXCEEDED | 403 | 日報の編集期限切れ |
| CUSTOMER_HAS_VISITS | 409 | 訪問記録が存在する顧客は削除不可 |
| USER_HAS_REPORTS | 409 | 日報が存在するユーザーは削除不可 |
| BRANCH_HAS_DEPARTMENTS | 409 | 部署が存在する支店は削除不可 |
| DEPARTMENT_HAS_USERS | 409 | ユーザーが所属する部署は削除不可 |
| LAST_BRANCH_ASSIGNMENT | 400 | 最低1つの支店に所属させる必要がある |
| LAST_DEPARTMENT_ASSIGNMENT | 400 | 最低1つの部署に所属させる必要がある |
| DUPLICATE_SERVICE_CODE | 409 | サービスコードが既に登録されている |
| SERVICE_HAS_SUBSCRIPTIONS | 409 | 契約企業が存在するサービスは削除不可 |
| SERVICE_ALREADY_SUBSCRIBED | 409 | 既に契約済みのサービス |
| SERVICE_NOT_AVAILABLE | 403 | サービスが利用不可（未契約または無効） |
| INTERNAL_SERVER_ERROR | 500 | サーバー内部エラー |

---

## データ型定義

### 優先度 (priority)
- `high`: 高
- `medium`: 中
- `low`: 低

### 課題ステータス (problem status)
- `pending`: 未解決
- `resolved`: 解決済

### ユーザー役割 (role)
- `sales`: 営業担当
- `manager`: 上長
- `admin`: 管理者

### ユーザーステータス (status)
- `active`: 有効
- `inactive`: 無効

### リモート種別 (remote)
- `false` (0): 対面訪問
- `true` (1): リモート訪問

### サービス契約状態 (subscription status)
- `active`: 有効（サービス利用可能）
- `suspended`: 一時停止（サービス利用不可）
- `cancelled`: 解約済（サービス利用不可）

---

## セキュリティ仕様

### 認証
- JWT（JSON Web Token）を使用
- アクセストークン有効期限: 1時間
- リフレッシュトークン有効期限: 30日

### 認可
- ロールベースアクセス制御（RBAC）
- リソースベースアクセス制御（所有者チェック）

### データ保護
- 全通信はHTTPS（TLS 1.2以上）
- パスワードはbcryptでハッシュ化（コスト係数: 12）
- 機密情報はログに出力しない

### レート制限
- 認証API: 5回/分
- その他API: 100回/分
- 超過時は429 Too Many Requestsを返却

---

## 権限システム参照

本API設計書で使用されている権限コードの詳細については、以下のドキュメントを参照してください:

### 📄 関連ドキュメント

- **[API権限マッピング](./API権限マッピング.md)** - エンドポイントと権限コードの完全なマッピング
- **[権限管理システム](./権限管理.md)** - 権限システムの全体設計と実装詳細

### 🔑 権限コードについて

権限コードは `<resource>.<action>` の形式で表現されます:

**Resource (リソース)**:
- `branch` - 支店管理
- `company` - 企業管理
- `customer` - 顧客管理
- `department` - 部署管理
- `report` - 日報管理
- `service` - サービス管理
- `subscription` - サービス契約管理
- `user` - ユーザー管理

**Action (操作)**:
- `view` - 閲覧
- `view_all` - 全件閲覧
- `view_self` - 自分のみ閲覧
- `create` - 作成
- `update` - 更新
- `update_self` - 自分のみ更新
- `delete` - 削除
- `delete_self` - 自分のみ削除
- `subscribe` - サービス契約
- `unsubscribe` - サービス契約解除
- `history` - 履歴閲覧

### 📊 権限チェックパターン

1. **Pattern 1: 単一権限 (Basic CRUD)** - 1つの特定権限が必要
   - 例: `branch.view`, `company.create`

2. **Pattern 2: 自己操作許可 (Self-Operation)** - 自分のデータと他人のデータで異なる権限
   - 例: `user.update` OR `user.update_self`

3. **Pattern 3: 動的スコープ (Dynamic Scope)** - 実行時にデータ所有者を判定
   - 例: `report.view_all` OR `report.view_self`

詳細は [API権限マッピング - 権限チェックパターン](./API権限マッピング.md#権限チェックパターン) を参照してください。

---

**作成日**: 2025-12-31
**最終更新**: 2026-01-04 (権限コード追加)
**バージョン**: 1.1
