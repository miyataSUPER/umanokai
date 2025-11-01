# Streamlit Cloud 無料版での動作確認と最適化

## 無料版の制限

Streamlit Cloudの無料版には以下の制限があります：
- **メモリ**: 1GB
- **CPU**: 制限あり
- **スリープ**: 一定期間アクセスがないとスリープ状態になる
- **実行時間**: 制限あり（ただし通常のWebアプリでは問題なし）

## Playwright使用時の注意点

### 可能なこと
- Playwrightのインストールと実行は**可能**です
- Chromiumのダウンロードは初回のみ必要（数分かかる場合あり）

### 問題が発生する可能性がある場合
1. **メモリ不足**: Chromiumはメモリを多く使用しますが、1GBあれば通常は動作します
2. **インストール時間**: 初回デプロイ時にChromiumのダウンロードに時間がかかります
3. **タイムアウト**: 処理が長すぎる場合、タイムアウトする可能性があります

## 最適化方法

### 1. Install Command の設定（必須）

Streamlit Cloudダッシュボードで以下を設定：

```
pip install -r requirements.txt && python -m playwright install chromium && python -m playwright install-deps chromium
```

### 2. delay_timeの短縮

`app.py`で`delay_time=300`に設定済み（デフォルトの1000から短縮）

### 3. メモリ使用量の削減

- `headless=True`で実行（デフォルト）
- 不要なページ遷移を避ける
- ブラウザを即座に閉じる

## 無料版で動作しない場合の代替案

### 1. ローカル実行（推奨）

```bash
# 依存関係をインストール
pip install -r requirements-streamlit.txt
playwright install chromium

# アプリを起動
streamlit run app.py
```

**メリット**:
- 無料
- 制限なし
- 高速

**デメリット**:
- 自分のPCでしか動作しない
- 他者と共有できない

### 2. Render（無料プランあり）

- [Render](https://render.com)は無料プランがあります
- Streamlitアプリをデプロイ可能
- Playwrightの実行も可能

### 3. Railway（無料プランあり）

- [Railway](https://railway.app)は無料プランがあります
- Streamlitアプリをデプロイ可能
- $5の無料クレジットあり

### 4. Fly.io（無料プランあり）

- [Fly.io](https://fly.io)は無料プランがあります
- Streamlitアプリをデプロイ可能
- 制限はありますが動作可能

## 推奨される方法

### 最初に試すこと
1. **Streamlit Cloud無料版で試す**（最適化済みのコードで試してみる）
2. エラーが発生した場合、ログを確認
3. それでも動作しない場合、代替案を検討

### 確実に動作させたい場合
- **ローカル実行**が最も確実
- 共有が必要な場合は、RenderやRailwayの無料プランを試す

## トラブルシューティング

### メモリエラー
- `delay_time`をさらに短縮
- 不要なデータを削除
- ページ遷移を最小限に

### タイムアウトエラー
- `delay_time`を短縮
- 処理を分割できないか検討
- 代替プラットフォームを試す

### Chromiumインストールエラー
- Install Commandを確認
- `python -m playwright install chromium`を使用
- ログを確認してエラー内容を確認

