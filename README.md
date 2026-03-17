# daily-ai-news

毎日のAI関連ニュースを複数ソースから収集し、NotebookLMのポッドキャストとしてまとめるツール。

## 機能

- HackerNews / TechCrunch / Zenn / Qiita からAI関連記事を収集
- 重複URLを自動排除
- NotebookLMにノートブックを作成し、ポッドキャストを生成

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

## 開発

### テスト

```bash
uv sync --group dev
uv run pytest
```

## ソース別の収集ルール

| ソース | フィルタ | 上限 |
|--------|----------|------|
| HackerNews | Algolia APIで取得 | 5件 |
| TechCrunch | RSSフィード、AI関連キーワードで絞り込み | 3件 |
| Zenn | トレンドフィード | 3件 |
| Qiita | いいね数順、AI関連タグ | 3件 |
