# JRAレースオッズ表示ツール

JRA公式サイトからレースオッズを取得し、単勝・複勝・馬連オッズを表示するWebアプリケーションです。

## 構成

- **デプロイ版**: Vercel（HTML + JavaScript + Python Serverless Functions）
- **ローカルテスト版**: Streamlit（`app.py`）

詳細は[仕様書](SPEC.md)を参照してください。

## 機能

- netkeibaのURLまたはrace_idを入力してオッズ情報を取得
- 単勝・複勝・馬連オッズを横一列グリッド形式で表示
- オッズ順にソートして表示
- スプレッドシートに貼り付け可能な形式でクリップボードにコピー

## セットアップ

### ローカル環境でのテスト（Streamlit版）

1. 依存関係をインストール:
```bash
pip install -r requirements-streamlit.txt
playwright install chromium
```

2. Streamlitアプリを起動:
```bash
streamlit run app.py
```

ブラウザで `http://localhost:8501` にアクセスしてください。

### Vercelでのデプロイ

1. **リポジトリを準備**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Vercelにデプロイ**
   - [Vercel](https://vercel.com)にアクセス
   - GitHubアカウントでサインイン
   - "New Project"をクリック
   - リポジトリを選択
   - "Deploy"をクリック

3. **注意事項**
   - Playwrightは実行時間とメモリを多く消費します
   - Vercelの無料プランは10秒のタイムアウトがあります
   - Proプラン（60秒）を推奨します
   - 初回実行時にChromiumのダウンロードが必要なため、時間がかかります

## ファイル構成

- `app.py`: Streamlit版（ローカルテスト用）
- `extract_odds.py`: オッズ抽出ロジック（共通）
- `api/odds.py`: Vercel Serverless Function
- `index.html`: フロントエンド（HTML）
- `static/js/app.js`: フロントエンド（JavaScript）
- `static/css/style.css`: スタイルシート
- `vercel.json`: Vercel設定
- `requirements.txt`: Vercel用の依存関係
- `requirements-streamlit.txt`: Streamlit版用の依存関係
- `SPEC.md`: 仕様書

## 制限事項

- JRA公式サイトのHTML構造に依存しているため、サイト構造が変更されると動作しない可能性があります
- Playwrightを使用しているため、デプロイ環境によっては追加の設定が必要です
- 非同期処理が必要なため、オッズ取得に時間がかかる場合があります
- VercelのServerless Functionsの実行時間制限に注意してください
