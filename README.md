# daily-ai-news

毎日のAI関連ニュースを複数ソースから収集し、NotebookLMのポッドキャストとしてまとめるツール。

## 機能

- HackerNews / TechCrunch / Zenn / Qiita / The Verge / MIT Technology Review / ITmedia AI+ からAI関連記事を収集
- 重複URLを自動排除
- NotebookLMにノートブックを作成し、ポッドキャストを生成
- 日付指定での実行に対応（`TARGET_DATE` 環境変数、または GitHub Actions の手動実行から指定）

## セットアップ

### 前提条件

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)

### インストール

```bash
uv sync
```

### NotebookLM認証

初回のみ、ブラウザでGoogleログインが必要です。

```bash
uv run notebooklm login
```

ログイン完了後、`~/.notebooklm/storage_state.json` に認証情報が保存されます。

## 実行

```bash
uv run python -m src.main
```

特定の日付を対象にする場合:

```bash
TARGET_DATE=2026-03-10 uv run python -m src.main
```

## 開発

### テスト

```bash
uv sync --group dev
uv run pytest
```

## GitHub Actions

毎日 JST 07:00（UTC 22:00）に自動実行されます。GitHub Actions タブ → "Daily AI News" → "Run workflow" から手動実行も可能で、その際に対象日付を指定できます。

### 認証トークンの更新

NotebookLM の認証クッキーには有効期限があります（目安: 数週間〜数ヶ月）。Actions が認証エラーで失敗し始めたら、以下の手順でシークレットを更新してください。

1. ローカルで再ログイン:
   ```bash
   uv run notebooklm login
   ```
2. 生成された JSON を確認:
   ```bash
   cat ~/.notebooklm/storage_state.json
   ```
3. GitHub リポジトリ → **Settings → Secrets and variables → Actions** を開く
4. `NOTEBOOKLM_AUTH_JSON` を選択し、上記 JSON の中身で値を更新する

## ソース別の収集ルール

| ソース | フィルタ | 上限 |
|--------|----------|------|
| HackerNews | Algolia API、日付指定でフィルタ | 3件 |
| TechCrunch | RSSフィード、AI関連キーワードで絞り込み | 3件 |
| Zenn | AI トレンドフィード | 3件 |
| Qiita | AI タグ、いいね数順 | 3件 |
| The Verge | AI 専用 RSSフィード | 3件 |
| MIT Technology Review | RSSフィード、AI関連キーワードで絞り込み | 3件 |
| ITmedia AI+ | AI 専用 RSSフィード | 3件 |
