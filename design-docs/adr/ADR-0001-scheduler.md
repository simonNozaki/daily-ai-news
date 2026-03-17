# ADR-0001: スケジューラーの選定

## ステータス

Accepted

## 日付

2026-03-17

## コンテキスト

日次でニュース収集・NotebookLM操作・メール通知を自動実行するためのスケジューラーが必要。
Playwrightによるブラウザ自動化を伴うため、実行環境にブラウザが使える必要がある。

## 決定

スケジューラーとして **GitHub Actions** を採用する。

## 理由

- 追加インフラ不要で、リポジトリと一体管理できる
- Playwrightの公式セットアップアクション（`microsoft/playwright-github-action`）が利用可能
- `schedule: cron` で日次実行が簡単に設定できる
- Secretsによる認証情報の管理が標準機能として備わっている
- 無料枠（パブリックリポジトリは無制限、プライベートは月2,000分）で日次1回の実行は十分賄える

## 検討した選択肢

### 選択肢 A: GitHub Actions（採用）

- **概要**: リポジトリに `.github/workflows/daily.yml` を置くだけで動作
- **メリット**: 設定が簡単、リポジトリと一体管理、Secrets管理が標準装備
- **デメリット**: Google認証クッキーの定期更新が手動で必要

### 選択肢 B: Modal

- **概要**: Pythonネイティブのサーバーレス実行環境、cron内蔵
- **メリット**: Playwrightイメージ対応、コードだけで完結
- **デメリット**: 別サービスへの登録・学習コストが発生する

### 選択肢 C: VPS + cron

- **概要**: DigitalOcean等のVPSにcrontabで設定
- **メリット**: セッション永続化が容易
- **デメリット**: サーバー管理コストが発生する、$5〜/月のコストがかかる

## 結果

### ポジティブな結果

- インフラ管理が不要
- コードとワークフローが同一リポジトリで管理される

### ネガティブな結果 / トレードオフ

- Googleセッションクッキーの有効期限が切れた際に手動更新が必要

### 中立的な結果

- ジョブの実行ログはGitHub Actions上で確認できる

## 関連するADR

- [ADR-0003: Google認証方式](./ADR-0003-google-auth.md)

## 参考資料

- [GitHub Actions - schedule event](https://docs.github.com/en/actions/writing-workflows/choosing-when-your-workflow-runs/events-that-trigger-workflows#schedule)
- [Playwright on CI](https://playwright.dev/docs/ci-github-actions)
