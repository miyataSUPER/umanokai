# Streamlit Cloud デプロイガイド

## 前提条件

- GitHubアカウント
- Streamlit Cloudアカウント（GitHubアカウントで作成可能）

## デプロイ手順

### 1. GitHubリポジトリの準備

プロジェクトをGitHubにプッシュします：

```bash
# リポジトリが既にGitHubに存在する場合
git add .
git commit -m "Prepare for Streamlit Cloud deployment"
git push origin main
```

### 2. Streamlit Cloudにアクセス

1. [Streamlit Cloud](https://streamlit.io/cloud) にアクセス
2. GitHubアカウントで「Sign Up」または「Log In」
3. 初回の場合、Streamlit CloudがGitHubリポジトリへのアクセスを要求します（許可してください）

### 3. プロジェクトをデプロイ

1. 「New app」をクリック
2. 設定項目：
   - **Repository**: `[YOUR-USERNAME]/umanokai` を選択
   - **Branch**: `main` を選択
   - **Main file path**: `app.py` を入力
   - **Python version**: `3.9` または `3.10` を選択（推奨: `3.10`）
3. 「Deploy!」をクリック

### 4. Playwrightのセットアップ

Streamlit Cloudでは、Playwrightのブラウザをインストールする必要があります。

#### 方法1: `.streamlit/secrets.toml`を使用（推奨）

デプロイ後、Streamlit Cloudのダッシュボードで：
1. **Settings** → **Secrets** を開く
2. 以下を追加（現在は不要ですが、将来的に使用する場合）:

```toml
# 現在は不要ですが、将来的に設定が必要な場合はここに記載
```

#### 方法2: `packages.txt`を使用

Playwrightの依存関係をインストールするために、ルートディレクトリに `packages.txt` を作成します：

```txt
chromium
chromium-chromedriver
```

しかし、Streamlit CloudはLinux環境のため、`playwright install chromium`を実行する必要があります。

### 5. ビルドコマンドの設定（重要）

Streamlit Cloudのダッシュボードで：
1. **Settings** → **General** を開く
2. **Advanced settings** を展開
3. **Dependencies** セクションで以下を確認：
   - **Python version**: `3.10` を選択
   - **Install command**: 
     ```
     pip install -r requirements.txt && playwright install chromium && playwright install-deps chromium
     ```

または、`packages.txt`を使用する場合：
- **Install command**: 
  ```
  pip install -r requirements.txt && playwright install chromium && playwright install-deps chromium
  ```

### 6. デプロイの確認

デプロイが完了すると、以下のようなURLが発行されます：
```
https://[YOUR-APP-NAME]--[YOUR-USERNAME].streamlit.app
```

初回デプロイには数分かかる場合があります（PlaywrightのChromiumのインストールが必要なため）。

## 重要な注意事項

### Playwrightの実行時間

Streamlit Cloudの無料プランでは、アプリの実行時間に制限がありますが、Playwrightの実行は通常問題ありません。

### 初回実行

- 初回実行時はChromiumのダウンロードが必要なため、時間がかかります
- タイムアウトする可能性がある場合は、Streamlit Cloudのタイムアウト設定を確認してください

### ログの確認

デプロイ後の問題確認：
1. Streamlit Cloudダッシュボードでアプリを選択
2. 「Manage app」→「Logs」でログを確認

## トラブルシューティング

### ビルドエラー

- **エラー**: `playwright: command not found`
  - **解決策**: Install commandに `playwright install chromium && playwright install-deps chromium` を追加

- **エラー**: `chromium not found`
  - **解決策**: `playwright install chromium` を実行する必要があります
  - Install commandを確認してください

### 実行時エラー

- **タイムアウトエラー**: 
  - Streamlit Cloudのタイムアウト設定を確認
  - 処理を最適化する

- **Playwrightエラー**: 
  - ログを確認し、Chromiumのインストール状況を確認
  - Install commandを再確認

### 依存関係エラー

- `requirements.txt`に必要なパッケージが含まれているか確認
- Streamlit Cloudのログでエラーメッセージを確認

## アプリの更新

コードを更新する場合：

```bash
git add .
git commit -m "Update: 説明"
git push
```

Streamlit Cloudは自動的に変更を検知して再デプロイします（通常は数秒〜数分）。

## 設定ファイル

### `.streamlit/config.toml`（オプション）

アプリの設定をカスタマイズする場合、`.streamlit/config.toml`を作成：

```toml
[server]
headless = true
port = 8501
enableCORS = false

[browser]
gatherUsageStats = false
```

現在は必要ありませんが、カスタマイズする場合は使用できます。

