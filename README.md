# JRAレースオッズ表示ツール

JRA公式サイトからレースオッズを取得し、単勝・複勝・馬連オッズを表示するWebアプリケーションです。

## 構成

- **デプロイ版**: Streamlit Cloud（推奨）
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

### Streamlit Cloudでのデプロイ

1. **リポジトリを準備**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Streamlit Cloudにデプロイ**
   - [Streamlit Cloud](https://streamlit.io/cloud)にアクセス
   - GitHubアカウントでサインイン
   - "New app"をクリック
   - リポジトリを選択: `[YOUR-USERNAME]/umanokai`
   - **Main file path**: `app.py` を入力
   - **Python version**: `3.10` を選択
   - **Install command**: `pip install -r requirements.txt && python -m playwright install chromium && python -m playwright install-deps chromium`
   - "Deploy!"をクリック

3. **注意事項**
   - 初回デプロイには数分かかる場合があります（PlaywrightのChromiumのインストールが必要なため）
   - Streamlit Cloudの無料プランで動作します
   - 詳細は[DEPLOY_STREAMLIT_CLOUD.md](DEPLOY_STREAMLIT_CLOUD.md)を参照してください

## ファイル構成

- `app.py`: Streamlitアプリケーション（メインファイル）
- `extract_odds.py`: オッズ抽出ロジック（共通）
- `requirements.txt`: 依存関係（Streamlit Cloud用）
- `requirements-streamlit.txt`: Streamlit版用の依存関係（ローカルテスト用）
- `.streamlit/config.toml`: Streamlit設定
- `SPEC.md`: 仕様書
- `DEPLOY_STREAMLIT_CLOUD.md`: Streamlit Cloudデプロイガイド

## 制限事項

- JRA公式サイトのHTML構造に依存しているため、サイト構造が変更されると動作しない可能性があります
- Playwrightを使用しているため、初回実行時にChromiumのダウンロードが必要で時間がかかる場合があります
- 非同期処理が必要なため、オッズ取得に時間がかかる場合があります
