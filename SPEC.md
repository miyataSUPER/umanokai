# JRAレースオッズ表示ツール 仕様書

## 概要

netkeibaのURLまたはrace_idを入力し、JRA公式サイトからオッズ情報を取得して表示するWebアプリケーション。

## 機能仕様

### 1. 入力機能

- **入力形式**: 
  - netkeibaのURL（例: `https://race.netkeiba.com/race/shutuba.html?race_id=202505041007`）
  - またはrace_idのみ（例: `202505041007`）

- **処理**:
  - URLからrace_idを抽出
  - race_idをJRA形式に変換（必要に応じて）

### 2. オッズ取得機能

- **取得するオッズ**:
  - 単勝オッズ
  - 複勝オッズ（下限値）
  - 馬連オッズ（単勝1番人気と2番人気の両方を含む組み合わせでオッズが最も低いものを軸とする）

- **データソース**: JRA公式サイト（Playwrightを使用してスクレイピング）

### 3. 表示機能

#### 表示形式

横一列グリッド形式で表示：

| 行名 | 列1 | 列2 | 列3 | ... |
|------|-----|-----|-----|-----|
| 単勝_オッズ | 1.20 | 3.50 | 5.00 | ... |
| 単勝_馬番 | 01 | 02 | 03 | ... |
| 複勝_オッズ | 1.10 | 1.50 | 2.00 | ... |
| 複勝_馬番 | 01 | 02 | 03 | ... |
| 馬連_オッズ | 5.20 | 8.50 | 12.00 | ... |
| 馬連_馬番 | 1-2 | 1-3 | 1-5 | ... |

#### 表示ルール

1. **ソート順**:
   - 単勝・複勝・馬連それぞれをオッズの低い順（人気順）にソート

2. **馬連の表示順**:
   - 先頭2つ: 馬連オッズの上位2つ
   - 以降: 上位2つに共通する馬番を軸として、オッズ順にソート
   - 上位2つは除外（重複を避ける）

3. **馬連の組み合わせ表記**:
   - 形式: `小さい馬番-大きい馬番`
   - 例: `1-15`, `5-10`, `15-20`
   - ゼロ埋めなし（1桁は`1`、2桁は`15`のまま）

### 4. コピー機能

- **形式**: TSV（タブ区切り）
- **ヘッダー**: なし
- **データ**: 表示されているグリッドデータをそのままコピー
- **用途**: スプレッドシートに直接貼り付け可能

## 技術仕様

### バックエンド

- **言語**: Python 3.11+
- **フレームワーク**: 
  - ローカルテスト: Streamlit (`app.py`)
  - デプロイ: Vercel Serverless Functions（Python runtime）

### 主要ライブラリ

- `playwright`: ブラウザ自動化（JRA公式サイトのスクレイピング）
- `beautifulsoup4`: HTMLパース
- `lxml`: HTMLパーサー
- `pandas`: データ処理（ローカルテストのみ）

### フロントエンド

- **フレームワーク**: 
  - ローカルテスト: Streamlit（`app.py`）
  - デプロイ: HTML + JavaScript（Vercel）

### API仕様（Vercel版）

#### エンドポイント

- `GET /api/odds?race_id={race_id}`: オッズ情報を取得

#### リクエスト

```
GET /api/odds?race_id=202505041007
```

#### レスポンス

```json
{
  "success": true,
  "data": {
    "tansho": {
      "1": 1.20,
      "2": 3.50,
      ...
    },
    "fukusho": {
      "1": 1.10,
      "2": 1.50,
      ...
    },
    "umaren": {
      "1-2": 5.20,
      "1-3": 8.50,
      ...
    }
  }
}
```

エラー時:
```json
{
  "success": false,
  "error": "エラーメッセージ"
}
```

## ファイル構成

### 必須ファイル

- `extract_odds.py`: オッズ抽出ロジック
- `app.py`: Streamlit版（ローカルテスト用）
- `api/odds.py`: Vercel Serverless Function
- `index.html`: フロントエンド
- `static/js/app.js`: フロントエンドJavaScript
- `static/css/style.css`: スタイルシート
- `vercel.json`: Vercel設定
- `requirements.txt`: Python依存関係

### 削除するファイル

- `Dockerfile`
- `.dockerignore`
- `packages.txt`
- `DEPLOY.md`
- `.gcloudignore`
- `STREAMLIT_CLOUD_DEPLOY.md`
- `.streamlit/config.toml`（Streamlit依存のため）

### 保持するファイル

- `README.md`: プロジェクト説明
- `.gitignore`: Git除外設定
- `SPEC.md`: この仕様書

## 制約事項

1. **Playwrightの実行環境**:
   - VercelのServerless Functionsでは実行時間とメモリに制限がある
   - PlaywrightのChromiumは重いため、実行時間が長くなる可能性がある

2. **タイムアウト**:
   - Vercelの無料プラン: 10秒
   - Proプラン: 60秒
   - Playwrightの実行には時間がかかるため、タイムアウトに注意

3. **メモリ制限**:
   - Playwrightはメモリを多く消費する
   - Vercelの制限を超えないように注意

## 実装方針

1. **分離**:
   - オッズ抽出ロジック（`extract_odds.py`）は共通化
   - Streamlit版（`app.py`）とVercel版（`api/odds.py`）で使い回す

2. **非同期処理**:
   - Playwrightは非同期処理が必要
   - Vercel Serverless Functionsで対応

3. **エラーハンドリング**:
   - タイムアウト、メモリ不足などのエラーに対応

