# ADR-0004: ニュース収集方式

## ステータス

Accepted

## 日付

2026-03-17

## コンテキスト

日次で日本・アメリカのAI関連ニュースを約10本収集し、NotebookLMのソースとしてURLを登録する。
収集ソースはHackerNews・TechCrunch（英語）、Zenn・Qiita（日本語）を中心とする。

## 決定

各ソースの公開API・RSSフィードを使って記事URLを取得し、NotebookLMにURLのリストとして渡す。
重複排除はURLの完全一致で行い、判断が難しい場合は重複を許容する。

## ソースと取得方法

| ソース | 取得方法 | フィルタリング |
|--------|----------|--------------|
| HackerNews | [Algolia HN API](https://hn.algolia.com/api) | `tags=story&query=AI` でAI関連を検索 |
| TechCrunch | RSS (`techcrunch.com/feed/`) | タイトル・タグにAI関連キーワードを含むもの |
| Zenn | RSS (`zenn.dev/topics/ai/feed`) | AIトピックのトレンドフィード |
| Qiita | [Qiita API v2](https://qiita.com/api/v2/docs) | `tag:AI` でトレンド記事を取得 |

## 重複排除

- 同一URL（完全一致）は除外
- タイトルの類似判断は行わない（実装コストに見合わないため）
- 前日以前の記事が再度トレンドに上がった場合は重複を許容する

## ノートブック構成

- 日本・アメリカのニュースを1つのノートブックにまとめる
- ノートブック名: `AI News YYYY-MM-DD`
- 各URLをソースとして追加し、ポッドキャストを生成する

## 検討した選択肢

### 選択肢 A: API・RSSで取得（採用）

- **概要**: 各サービスの公開API/RSSを利用
- **メリット**: 安定、利用規約の範囲内、追加ライブラリ不要
- **デメリット**: APIの仕様変更に追随する必要がある

### 選択肢 B: スクレイピング

- **概要**: BeautifulSoupなどでHTMLをスクレイピング
- **メリット**: APIがないサイトにも対応できる
- **デメリット**: サイト構造変更に弱い、利用規約上のリスクがある

### 選択肢 C: NewsAPIなどの集約サービス

- **概要**: NewsAPIなどのニュース集約サービスを使う
- **メリット**: 一元管理できる
- **デメリット**: 有料プランが必要、Zenn・Qiitaが対象外

## 結果

### ポジティブな結果

- 公開API・RSSを使うため安定して取得できる
- NotebookLMに渡すのはURLだけなので、記事本文の取得・保存が不要

### ネガティブな結果 / トレードオフ

- 各ソースのAPI制限に注意が必要（特にQiita APIは認証なしで1時間60リクエスト）
- NotebookLMがURLを読み込めない場合（ペイウォールなど）はソースとして機能しない

### 中立的な結果

- 収集件数は各ソース2〜3本ずつ、合計10本前後を目安とする

## 関連するADR

- [ADR-0002: NotebookLM操作ライブラリの選定](./ADR-0002-notebooklm-client.md)

## 参考資料

- [HackerNews Algolia API](https://hn.algolia.com/api)
- [Qiita API v2](https://qiita.com/api/v2/docs)
- [Zenn RSS](https://zenn.dev/zenn/articles/zenn-feed-rss)
