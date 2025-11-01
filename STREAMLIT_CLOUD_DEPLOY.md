# Streamlit Cloud デプロイガイド

## 前提条件

- GitHubアカウント
- Streamlit Cloudアカウント（GitHubアカウントで作成可能）

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

### 2. Streamlit Cloudにアクセス

1. [Streamlit Cloud](https://share.streamlit.io/) にアクセス
2. GitHubアカウントで「Sign in」をクリック
3. 初回の場合、Streamlit CloudがGitHubリポジトリへのアクセスを要求します（許可してください）

### 3. アプリを作成

1. 「New app」ボタンをクリック
2. 以下の情報を入力：
   - **Repository**: `[YOUR-USERNAME]/umanokai`
   - **Branch**: `main`
   - **Main file path**: `app.py`
3. 「Deploy!」ボタンをクリック

### 4. デプロイの確認

デプロイが完了すると、以下のようなURLが発行されます：
```
https://[YOUR-APP-NAME].streamlit.app
```

初回デプロイには数分かかる場合があります。

## 注意事項

### Playwrightの初回実行

Playwrightを使用しているため、初回実行時にChromiumのダウンロードが必要です：

- **初回のオッズ取得**: 初回実行時はChromiumのダウンロードが行われるため、時間がかかります（数分かかる場合があります）
- **2回目以降**: 2回目以降は通常の速度で動作します

### タイムアウトについて

Streamlit Cloudのデフォルトタイムアウトは300秒です。オッズ取得に時間がかかる場合は：
- リトライしてください
- `delay_time`パラメータを調整することも可能です

### アプリの更新

コードを更新する場合：

```bash
git add .
git commit -m "Update: 説明"
git push
```

Streamlit Cloudは自動的に変更を検知して再デプロイします（通常は数秒〜数分）。

## トラブルシューティング

### Playwrightエラー

初回実行時にPlaywright関連のエラーが表示される場合：
1. アプリを再読み込みしてください
2. もう一度オッズ取得を試してください
3. エラーが続く場合は、Streamlit Cloudのログを確認してください

### タイムアウトエラー

オッズ取得に時間がかかりすぎる場合：
- ネットワーク状況を確認
- リトライしてください
- JRA公式サイトの応答時間に依存します

### ログの確認

Streamlit Cloudのダッシュボードで「Manage app」→「Logs」からログを確認できます。

