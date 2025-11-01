# JRAレースオッズ表示ツール

JRA公式サイトからレースオッズを取得し、単勝・複勝・馬連オッズを表示するStreamlitアプリケーションです。

## 機能

- netkeibaのURLまたはrace_idを入力してオッズ情報を取得
- 単勝・複勝・馬連オッズを横一列グリッド形式で表示
- オッズ順にソートして表示
- スプレッドシートに貼り付け可能な形式でクリップボードにコピー

## セットアップ

### ローカル環境での実行

1. 依存関係をインストール:
```bash
pip install -r requirements.txt
playwright install chromium
```

2. Streamlitアプリを起動:
```bash
streamlit run app.py
```

## デプロイ方法

### Streamlit Cloud（推奨）

Streamlit Cloudは公式の無料ホスティングサービスで、GitHubリポジトリと簡単に連携できます。

#### デプロイ手順

1. **GitHubにリポジトリをプッシュ**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/[YOUR-USERNAME]/umanokai.git
   git push -u origin main
   ```

2. **Streamlit Cloudにアクセス**
   - [Streamlit Cloud](https://share.streamlit.io/) にアクセス
   - GitHubアカウントでサインイン

3. **新しいアプリを作成**
   - "New app"をクリック
   - GitHubアカウントを接続（初回のみ）
   - リポジトリを選択: `[YOUR-USERNAME]/umanokai`
   - ブランチを選択: `main`
   - メインファイル: `app.py`
   - デプロイボタンをクリック

4. **設定（必要に応じて）**
   - Advanced settingsで以下を設定可能:
     - Python version: 3.11
     - Secrets: 環境変数を設定する場合

#### Streamlit CloudでのPlaywrightの動作について

Streamlit CloudでもPlaywrightは動作しますが、初回実行時にChromiumのダウンロードが必要なため、以下の点に注意してください：

- **初回実行時間**: 最初のオッズ取得時にChromiumのダウンロードが行われるため、時間がかかります
- **タイムアウト**: Streamlit Cloudのデフォルトタイムアウトは300秒です
- **メモリ制限**: 無料プランでは制限がありますが、通常の使用では問題ありません

#### トラブルシューティング

- **Playwrightのエラー**: 初回実行後、再試行してください（Chromiumのダウンロードが必要な場合があります）
- **タイムアウトエラー**: オッズ取得に時間がかかる場合は、リトライしてください

#### アプリのURL

デプロイが完了すると、以下のようなURLが発行されます：
```
https://[YOUR-APP-NAME].streamlit.app
```

### Dockerを使用したデプロイ

1. Dockerイメージをビルド:
```bash
docker build -t umanokai-app .
```

2. コンテナを起動:
```bash
docker run -p 8501:8501 umanokai-app
```

### Google Cloud Run

1. Dockerfileを使用してイメージをビルド
2. Google Cloud Runにデプロイ

```bash
gcloud builds submit --tag gcr.io/[PROJECT-ID]/umanokai-app
gcloud run deploy --image gcr.io/[PROJECT-ID]/umanokai-app --platform managed
```

### Heroku

1. Herokuアカウントを作成
2. Heroku CLIをインストール
3. デプロイ:

```bash
heroku create umanokai-app
heroku container:push web
heroku container:release web
```

## 制限事項

- JRA公式サイトのHTML構造に依存しているため、サイト構造が変更されると動作しない可能性があります
- Playwrightを使用しているため、デプロイ環境によっては追加の設定が必要です
- 非同期処理が必要なため、オッズ取得に時間がかかる場合があります

