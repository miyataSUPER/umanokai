# デプロイ手順

## Google Cloud Run でのデプロイ（推奨）

Playwrightを使用しているため、コンテナベースのデプロイが必要です。Google Cloud Runが最も適しています。

### 前提条件

- Google Cloud Platformのアカウント
- `gcloud` CLIがインストールされている
- Dockerがインストールされている

### デプロイ手順

1. Google Cloudプロジェクトを設定:
```bash
gcloud config set project [YOUR-PROJECT-ID]
```

2. Cloud Build APIを有効化:
```bash
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
```

3. Dockerイメージをビルドしてプッシュ:
```bash
gcloud builds submit --tag gcr.io/[YOUR-PROJECT-ID]/umanokai-app
```

4. Cloud Runにデプロイ:
```bash
gcloud run deploy umanokai-app \
  --image gcr.io/[YOUR-PROJECT-ID]/umanokai-app \
  --platform managed \
  --region asia-northeast1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --timeout 300 \
  --port 8501
```

5. デプロイ完了後、URLが表示されます。

### 環境変数の設定（必要な場合）

```bash
gcloud run services update umanokai-app \
  --set-env-vars KEY=VALUE \
  --region asia-northeast1
```

## Vercel でのデプロイ（注意事項あり）

**注意**: Vercelは主にサーバーレス関数向けであり、Streamlitのような長時間実行アプリには適していません。
Playwrightを使用しているため、Vercelでのデプロイは推奨されません。

もし試す場合は：

1. Vercelアカウントを作成
2. GitHubリポジトリを接続
3. `vercel.json`が自動的に使用されます

ただし、Playwrightの動作が保証されない可能性があります。

## Render でのデプロイ

1. [Render](https://render.com)でアカウントを作成
2. "New Web Service"を選択
3. GitHubリポジトリを接続
4. 以下を設定:
   - **Name**: umanokai-app
   - **Environment**: Docker
   - **Dockerfile Path**: Dockerfile（デフォルト）
5. "Create Web Service"をクリック

## トラブルシューティング

### PlaywrightのChromiumがインストールされない場合

Dockerfile内で`playwright install chromium`が実行されるため、ビルド時間が長くなる可能性があります。

### メモリ不足エラー

Cloud Runのメモリ設定を増やしてください（最小2GB推奨）:

```bash
gcloud run services update umanokai-app \
  --memory 2Gi \
  --region asia-northeast1
```

### タイムアウトエラー

タイムアウト時間を延長してください:

```bash
gcloud run services update umanokai-app \
  --timeout 300 \
  --region asia-northeast1
```

