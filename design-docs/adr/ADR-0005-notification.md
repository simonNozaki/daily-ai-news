# ADR-0005: 完了通知方式

## ステータス

Accepted

## 日付

2026-03-17

## コンテキスト

ノートブックとポッドキャストの生成が完了した際に、ユーザーへ通知する手段が必要。
設定の簡単さを優先する。

## 決定

**Gmail SMTP** を使ったメール通知を採用する。

## 理由

- 追加サービスの登録が不要（Gmailアカウントのみ）
- PythonのSMTPlib標準ライブラリで実装できる
- Googleアカウントのアプリパスワードを発行するだけで使える
- SendGridなど外部サービスと比べて設定手順が最も少ない

## 設定手順

1. Googleアカウントで2段階認証を有効にする
2. Googleアカウント設定からアプリパスワードを発行
3. GitHub SecretsにSMTP認証情報を登録
   - `GMAIL_ADDRESS`: 送信元メールアドレス
   - `GMAIL_APP_PASSWORD`: アプリパスワード
   - `NOTIFY_EMAIL`: 通知先メールアドレス

## 通知内容

```
件名: [AI News] ノートブック作成完了 YYYY-MM-DD

本日のAIニュースノートブックが作成されました。

ノートブック: https://notebooklm.google.com/notebook/XXXX
作成記事数: 10件
作成日時: YYYY-MM-DD HH:MM (JST)
```

## 検討した選択肢

### 選択肢 A: Gmail SMTP（採用）

- **概要**: GmailのSMTPサーバーとアプリパスワードを使う
- **メリット**: 設定が最も簡単、追加サービス不要
- **デメリット**: 1日500通の送信制限（日次1通なので問題なし）

### 選択肢 B: SendGrid

- **概要**: メール配信サービス
- **メリット**: 安定性が高い、無料枠あり
- **デメリット**: アカウント登録・API Key取得が必要

### 選択肢 C: Slack通知

- **概要**: Slack Incoming Webhookで通知
- **メリット**: リアルタイム通知、既読管理しやすい
- **デメリット**: Slackアカウント・ワークスペースが必要、メールより設定が増える

## 結果

### ポジティブな結果

- 追加サービス不要で即座に設定できる

### ネガティブな結果 / トレードオフ

- Googleアカウントのアプリパスワードはセキュリティ上の注意が必要（GitHub Secretsで管理）
- ジョブ失敗時の通知は GitHub Actions のデフォルト通知（メール）に依存する

### 中立的な結果

- 将来的にSlackやLINEへの通知追加も容易

## 関連するADR

- [ADR-0001: スケジューラーの選定](./ADR-0001-scheduler.md)

## 参考資料

- [Gmail アプリパスワード](https://support.google.com/accounts/answer/185833)
- [Python smtplib](https://docs.python.org/3/library/smtplib.html)
