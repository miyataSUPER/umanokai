# Vercel デプロイ トラブルシューティング

## 404エラーが発生する場合

### 確認事項

1. **Output Directory の設定**
   - Vercelダッシュボード → Settings → General
   - **Output Directory** を `public` に設定
   - または空欄のまま（`public`ディレクトリが自動認識される）

2. **ファイル構造の確認**
   - `public/index.html` が存在するか
   - `public/static/css/style.css` が存在するか
   - `public/static/js/app.js` が存在するか
   - `api/odds.py` が存在するか

3. **`vercel.json`の確認**
   - `rewrites`が正しく設定されているか
   - APIエンドポイント `/api/odds` が `/api/odds.py` にマッピングされているか

### 解決方法

#### 方法1: Vercelダッシュボードで設定

1. **Settings** → **General**
2. **Build & Development Settings**
3. **Output Directory**: `public` を設定
4. **Save** をクリック
5. 再デプロイ

#### 方法2: プロジェクトを削除して再作成

既存のプロジェクトに問題がある場合：
1. プロジェクトを削除
2. 新しくプロジェクトを作成
3. 同じリポジトリを接続
4. 設定を確認してデプロイ

## 動作確認

デプロイ後、以下のURLでアクセス：
- `https://uma-no-kai-odd-logic.vercel.app`
- `https://uma-no-kai-odd-logic.vercel.app/api/odds?race_id=202505041007` (APIテスト)

## ログの確認

Vercelダッシュボードで以下を確認：
1. **Deployments** → 最新のデプロイメントをクリック
2. **Functions** タブ → ログを確認
3. **Runtime Logs** → 実行時のエラーを確認

