# ADR-0006: 実装言語の選定

## ステータス

Accepted

## 日付

2026-03-17

## コンテキスト

実装言語としてPythonとRubyを検討した。開発者はRubyに慣れているが、NotebookLM操作に使用するライブラリの選択が言語選定に影響する。

## 決定

**Python** を採用する。

## 理由

ADR-0002で採用した `notebooklm-py` がPythonライブラリであり、NotebookLMのUI自動操作は最も壊れやすい部分のため、実績あるライブラリに乗っかることを優先した。

## 検討した選択肢

### 選択肢 A: Python（採用）

- **概要**: notebooklm-pyをそのまま利用
- **メリット**: NotebookLM操作を自前実装せずに済む、ライブラリのメンテに追随できる
- **デメリット**: 開発者がRubyほど慣れていない

### 選択肢 B: Ruby

- **概要**: `playwright-ruby-client` を使ってNotebookLM操作を自前実装
- **メリット**: 開発者が慣れている
- **デメリット**: NotebookLMのPlaywright操作を自前で書く必要があり、UI変更時のメンテコストが高い

## 結果

### ポジティブな結果

- notebooklm-pyの恩恵をそのまま受けられる

### ネガティブな結果 / トレードオフ

- 開発者がPythonに不慣れなため、実装時に学習コストが発生する可能性がある

## 関連するADR

- [ADR-0002: NotebookLM操作ライブラリの選定](./ADR-0002-notebooklm-client.md)
