# uv - 高速Pythonパッケージマネージャー

## uvとは

**uv**は、Rustで書かれた超高速なPythonパッケージマネージャーです。従来の`pip`の代替として使用でき、**10-100倍高速**なパッケージインストールを実現します。

### 主な特徴

- ⚡ **超高速**: pipやpip-toolsより10-100倍高速
- 🦀 **Rust製**: メモリ効率が良く、並列処理に優れる
- 🔒 **信頼性**: 厳密な依存関係解決
- 🎯 **pip互換**: 既存のrequirements.txtをそのまま使用可能
- 📦 **仮想環境管理**: `venv`の代替も提供

## インストール

### macOS / Linux

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Windows (PowerShell)

```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

### パスの確認

```bash
# インストール後、シェルを再起動するか以下を実行
source ~/.bashrc  # または ~/.zshrc

# uvが使えることを確認
uv --version
```

## 基本的な使い方

### 仮想環境の作成

```bash
# 新しい仮想環境を作成
uv venv

# 特定のPythonバージョンで作成
uv venv --python 3.11

# 仮想環境を有効化
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
```

### パッケージインストール

```bash
# requirements.txtからインストール
uv pip install -r requirements.txt

# 個別のパッケージをインストール
uv pip install fastapi
uv pip install "fastapi[all]" uvicorn

# 開発用依存関係
uv pip install -r requirements-dev.txt
```

### パッケージ管理

```bash
# インストール済みパッケージ一覧
uv pip list

# パッケージのアップグレード
uv pip install --upgrade fastapi

# パッケージのアンインストール
uv pip uninstall fastapi

# 環境の完全クリーンアップ
uv pip freeze | uv pip uninstall -r /dev/stdin
```

### requirements.txt生成

```bash
# 現在の環境からrequirements.txt生成
uv pip freeze > requirements.txt

# 最小限のrequirements.txt（直接依存のみ）
uv pip compile requirements.in -o requirements.txt
```

## プロジェクトでの使い方

### 初回セットアップ

```bash
# プロジェクトディレクトリに移動
cd /Users/kazuh/Documents/GitHub/attendance/backend

# 仮想環境作成
uv venv

# 仮想環境有効化
source .venv/bin/activate

# 依存関係インストール
uv pip install -r requirements.txt
```

### 日常的な開発

```bash
# 仮想環境有効化
source .venv/bin/activate

# 新しいパッケージを追加
uv pip install sqlalchemy-utils

# requirements.txtを更新
uv pip freeze > requirements.txt

# アプリケーション実行
uvicorn app.main:app --reload
```

### Docker環境での使用

Dockerfileでは既にuvを使用するように設定されています:

```dockerfile
# uvインストール
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:${PATH}"

# 依存関係インストール
RUN uv pip install --system -r requirements.txt
```

`--system` フラグは、仮想環境外（システムPython）にインストールする際に使用します。

## pipとの比較

| 操作 | pip | uv |
|------|-----|-----|
| パッケージインストール | `pip install package` | `uv pip install package` |
| requirements.txtからインストール | `pip install -r requirements.txt` | `uv pip install -r requirements.txt` |
| パッケージ一覧 | `pip list` | `uv pip list` |
| freeze | `pip freeze` | `uv pip freeze` |
| アンインストール | `pip uninstall package` | `uv pip uninstall package` |
| 仮想環境作成 | `python -m venv .venv` | `uv venv` |

## パフォーマンス比較

実際のベンチマーク例（requirements.txtから全依存関係をインストール）:

```bash
# pip（従来）
time pip install -r requirements.txt
# 約 45秒

# uv（新方式）
time uv pip install -r requirements.txt
# 約 2秒

# 速度向上: 約22倍
```

## トラブルシューティング

### uvが見つからない

```bash
# パスを確認
echo $PATH

# シェル再起動
exec $SHELL

# または手動でパスを追加
export PATH="$HOME/.cargo/bin:$PATH"
```

### 依存関係の競合

```bash
# 依存関係の解決を強制
uv pip install -r requirements.txt --force-reinstall

# キャッシュをクリア
rm -rf ~/.cache/uv
```

### pipに戻したい場合

uvは完全にpip互換なので、いつでも`pip`に戻せます:

```bash
# uvで作った仮想環境でもpipは使える
pip install -r requirements.txt
```

## 高度な使い方

### requirements.inからrequirements.txt生成

```bash
# requirements.in（直接依存のみ記述）
echo "fastapi" > requirements.in
echo "uvicorn[standard]" >> requirements.in
echo "sqlalchemy" >> requirements.in

# 完全な依存関係ツリーを生成
uv pip compile requirements.in -o requirements.txt
```

### 複数環境の管理

```bash
# 開発環境用
uv pip install -r requirements-dev.txt

# 本番環境用
uv pip install -r requirements.txt --no-dev
```

### ロックファイルの活用

```bash
# 現在の環境を完全に固定
uv pip freeze > requirements.lock

# ロックファイルから正確に再現
uv pip install -r requirements.lock
```

## 参考リンク

- [公式ドキュメント](https://github.com/astral-sh/uv)
- [インストールガイド](https://astral.sh/uv)
- [リリースノート](https://github.com/astral-sh/uv/releases)

## まとめ

uvは以下の場合に特に有効:
- ✅ 大規模プロジェクトで依存関係が多い
- ✅ CI/CDでビルド時間を短縮したい
- ✅ Dockerビルドを高速化したい
- ✅ 開発環境のセットアップを高速化したい

このプロジェクトでは、すべてのpip操作をuvで置き換えることで、開発体験を大幅に向上させています。
