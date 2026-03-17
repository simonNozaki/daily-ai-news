# ADR-0002: NotebookLM操作ライブラリの選定

## ステータス

Accepted

## 日付

2026-03-17

## コンテキスト

NotebookLMには公式APIが存在しない。ノートブックの作成・ソース追加・ポッドキャスト生成をプログラムから操作するためのライブラリを選定する必要がある。

## 決定

**notebooklm-py** を採用する。

## 理由

- NotebookLMを操作できるPythonライブラリとして現状で最も実績のある選択肢
- Playwrightベースのブラウザ自動化で、公式APIがなくても操作可能
- ノートブック作成・URLソース追加・ポッドキャスト生成の一連の操作をサポートしている

## 検討した選択肢

### 選択肢 A: notebooklm-py（採用）

- **概要**: PlaywrightでNotebookLMのUIを操作するPythonライブラリ
- **メリット**: NotebookLMの全操作をカバー、Pythonから直接呼び出せる
- **デメリット**: 非公式ライブラリのためNotebookLMのUI変更で壊れるリスクがある

### 選択肢 B: 独自Playwright実装

- **概要**: Playwrightを使ってNotebookLMのUIを自分で操作するスクリプトを書く
- **メリット**: 自由度が高い
- **デメリット**: 実装・メンテナンスコストが高い

### 選択肢 C: 公式API待ち

- **概要**: GoogleがNotebookLMの公式APIを公開するまで待つ
- **メリット**: 安定性が高い
- **デメリット**: 公開時期未定のため現実的でない

## 結果

### ポジティブな結果

- 少ないコードでノートブック作成からポッドキャスト生成まで自動化できる

### ネガティブな結果 / トレードオフ

- NotebookLMのUI変更に追随してライブラリのアップデートが必要になる場合がある
- 非公式ライブラリのためサポートは期待できない

### 中立的な結果

- ポッドキャスト生成はNotebookLM側で非同期処理されるため、完了待ちのポーリングが必要

## 関連するADR

- [ADR-0003: Google認証方式](./ADR-0003-google-auth.md)

## 参考資料

- [notebooklm-py GitHub](https://github.com/tavita-io/notebooklm-py)
