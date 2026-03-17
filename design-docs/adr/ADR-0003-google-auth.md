# ADR-0003: Google認証方式

## ステータス

Accepted

## 日付

2026-03-17

## コンテキスト

notebooklm-pyはPlaywrightでNotebookLMのUIを操作するため、Googleアカウントへのログインが必要。
GitHub Actions上では対話的なログインができないため、認証状態を持ち越す方法が必要。

## 決定

**Googleセッションクッキーをエクスポートし、GitHub Secretsに保存して使い回す** 方式を採用する。

## 理由

- GitHub Actionsでの非対話型実行に対応できる唯一の現実的な方法
- セッションクッキーはPlaywrightの `storage_state` として保存・復元できる
- GitHub Secretsによる暗号化保管でセキュリティを担保できる

## 運用フロー

1. ローカルで一度手動ログインし、`playwright storage_state` をJSONファイルとしてエクスポート
2. そのJSONをGitHub Secretsに `GOOGLE_SESSION` として登録
3. GitHub Actionsのワークフロー内でSecretからファイルに書き出してPlaywrightに渡す
4. セッション期限切れ時（目安: 数週間〜数ヶ月）に手動で再エクスポート・再登録

## 検討した選択肢

### 選択肢 A: セッションクッキーを使い回す（採用）

- **概要**: `playwright storage_state` でセッションを保存し、GitHub Secretsで管理
- **メリット**: 設定がシンプル、追加サービス不要
- **デメリット**: セッション期限切れ時に手動更新が必要

### 選択肢 B: OAuth2 サービスアカウント

- **概要**: Google Cloud のサービスアカウントで認証
- **メリット**: 期限切れがない
- **デメリット**: NotebookLMはサービスアカウントでのアクセスに対応していない

### 選択肢 C: 毎回手動ログイン

- **概要**: 実行のたびに手動でログイン
- **メリット**: シンプル
- **デメリット**: 自動化できない

## 結果

### ポジティブな結果

- GitHub Actionsで完全に自動実行できる

### ネガティブな結果 / トレードオフ

- セッション期限切れ時にワークフローが失敗し、手動での再設定が必要
- セッション期限は明示的でないため、定期的な確認が推奨される

### 中立的な結果

- セッションクッキーのJSONにはアクセストークンが含まれるため、Secretの管理に注意が必要

## 関連するADR

- [ADR-0001: スケジューラーの選定](./ADR-0001-scheduler.md)
- [ADR-0002: NotebookLM操作ライブラリの選定](./ADR-0002-notebooklm-client.md)

## 参考資料

- [Playwright - Authentication](https://playwright.dev/python/docs/auth)
- [GitHub Encrypted Secrets](https://docs.github.com/en/actions/security-for-github-actions/security-guides/using-secrets-in-github-actions)
