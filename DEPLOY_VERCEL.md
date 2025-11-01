# Vercelデプロイガイド

## 前提条件

- GitHubアカウント
- Vercelアカウント（GitHubアカウントで作成可能）

## デプロイ手順

### 1. GitHubリポジトリの準備

プロジェクトをGitHubにプッシュします：

```bash
# リポジトリを初期化（まだの場合）
git init

# ファイルを追加
git add .

# コミット
git commit -m "Initial commit: JRAオッズ表示ツール"

# ブランチ名をmainに設定
git branch -M main

# GitHubリポジトリを作成して接続
# GitHub上で新しいリポジトリを作成後：
git remote add origin https://github.com/[YOUR-USERNAME]/umanokai.git
git push -u origin main
```

### 2. Vercelにアクセス

1. [Vercel](https://vercel.com) にアクセス
2. GitHubアカウントで「Sign Up」または「Log In」
3. 初回の場合、VercelがGitHubリポジトリへのアクセスを要求します（許可してください）

### 3. プロジェクトを作成

1. 「Add New Project」または「New Project」をクリック
2. GitHubリポジトリを選択: `[YOUR-USERNAME]/umanokai`
3. プロジェクト設定:
   - **Framework Preset**: `Other`を選択
   - **Root Directory**: `./`（デフォルト）
   - **Build Command**: （空欄のまま）
   - **Output Directory**: （空欄のまま）
   - **Install Command**: `pip install -r requirements.txt && playwright install chromium`
4. 「Deploy」をクリック

### 4. 環境変数の設定（必要に応じて）

現在は不要ですが、将来的にAPIキーなどが必要になった場合は：
- Project Settings → Environment Variables で設定

### 5. デプロイの確認

デプロイが完了すると、以下のようなURLが発行されます：
```
https://[YOUR-PROJECT-NAME].vercel.app
```

初回デプロイには数分かかる場合があります（PlaywrightのChromiumのインストールが必要なため）。

## 重要な注意事項

### Playwrightの実行時間

Playwrightを使用しているため、以下の制約があります：

1. **実行時間制限**:
   - 無料プラン: 10秒（非常に短い）
   - Proプラン: 60秒（推奨）
   - Playwrightの実行には通常10〜30秒かかります

2. **初回実行**:
   - 初回実行時はChromiumのダウンロードが必要なため、時間がかかります
   - タイムアウトする可能性があります

3. **推奨事項**:
   - **Proプランを使用することを強く推奨します**
   - 無料プランでは、タイムアウトエラーが発生する可能性が高いです

### タイムアウトエラーが発生する場合

1. **Vercel Proプランにアップグレード**（最も確実な解決策）
2. `vercel.json`の`maxDuration`を確認（60秒に設定済み）
3. `delay_time`をさらに短縮する（`api/odds.py`内で調整）

### ログの確認

デプロイ後の問題確認：

1. Vercelダッシュボードで「Deployments」を選択
2. デプロイメントをクリック
3. 「Functions」タブでログを確認

## トラブルシューティング

### ビルドエラー

- PlaywrightのChromiumインストールに時間がかかることがあります
- ビルド時間の制限を超える場合は、Vercelの有料プランが必要です

### 実行時エラー

- タイムアウトエラー: Proプランを使用するか、処理を最適化
- Playwrightエラー: ログを確認し、Chromiumのインストール状況を確認

### CORSエラー

- `api/odds.py`でCORSヘッダーを設定済み
- フロントエンドからAPIを呼び出す際にエラーが出る場合は、CORSヘッダーを確認

## アプリの更新

コードを更新する場合：

```bash
git add .
git commit -m "Update: 説明"
git push
```

Vercelは自動的に変更を検知して再デプロイします（通常は数秒〜数分）。

