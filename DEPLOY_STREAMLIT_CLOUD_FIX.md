# Streamlit Cloud 無料版での Install Command 設定方法

## 問題: Advanced Settings で Install Command が設定できない

Streamlit Cloudの無料版では、**Advanced Settings**で**Install Command**が表示されない、または設定できない場合があります。

## 解決策

### 方法1: 自動インストール機能（実装済み）

`app.py`に自動インストール機能を追加しました。アプリ起動時に自動的にChromiumがインストールされているかチェックし、なければ自動的にインストールを試みます。

**動作**:
- アプリ起動時に自動的にChromiumの存在をチェック
- なければ`python -m playwright install chromium`を実行
- 初回実行時は数分かかる場合があります

### 方法2: Streamlit Cloud の設定を確認

もしまだ設定できる場合は、以下の手順で設定してください：

1. Streamlit Cloudダッシュボードでアプリを選択
2. 「⋮」（三点メニュー）→ **Settings** をクリック
3. **General** タブを開く
4. **Advanced settings** セクションを探す
5. **Dependencies** セクションで以下を設定:
   - **Install command**: 
     ```
     pip install -r requirements.txt && python -m playwright install chromium && python -m playwright install-deps chromium
     ```

**注意**: 無料版ではこの設定オプションが表示されない場合があります。

### 方法3: デプロイ時の設定

新規アプリを作成する際に、デプロイフォームで設定できる場合があります：

1. **New app** をクリック
2. リポジトリを選択
3. **Advanced settings** を展開
4. **Install command** に以下を入力:
   ```
   pip install -r requirements.txt && python -m playwright install chromium && python -m playwright install-deps chromium
   ```

## 現在の実装

`app.py`に以下の機能が実装されています：

```python
def ensure_playwright_chromium():
    """
    PlaywrightのChromiumがインストールされているか確認し、
    インストールされていない場合は自動的にインストールする。
    """
    # Chromiumが存在するかチェック
    # なければ自動的にインストール
    ...
```

この機能により、**Install Command**が設定できなくても、アプリ起動時に自動的にChromiumのインストールを試みます。

## 注意事項

1. **初回実行時**: Chromiumのインストールに数分かかる場合があります
2. **タイムアウト**: Streamlit Cloudのタイムアウトに注意（通常は問題ありません）
3. **ログ確認**: エラーが発生した場合は、Streamlit Cloudのログを確認してください

## エラーが発生する場合

もし自動インストールが失敗する場合は：

1. **ログを確認**: Streamlit Cloudダッシュボード → 「Manage app」→ 「Logs」
2. **エラーメッセージ**: エラーの詳細を確認
3. **手動対応**: ログを基に対処方法を検討

一般的なエラー：
- **メモリ不足**: Streamlit Cloud無料版の1GB制限に引っかかる場合
- **タイムアウト**: Chromiumのインストールに時間がかかりすぎる場合
- **権限エラー**: ファイルシステムへの書き込み権限がない場合

これらの場合、代替プラットフォーム（Render、Railway等）の利用を検討してください。

