# ADR-0007: Pythonバージョン・パッケージ管理ツールの選定

## ステータス

Accepted

## 日付

2026-03-17

## コンテキスト

Pythonプロジェクトとして実装することが決定（ADR-0006）した後、以下を管理するツールを選定する必要が生じた。

- Pythonバージョンの固定（再現性の確保）
- 依存ライブラリのインストール・管理
- 開発用依存（pytest等）と本番依存の分離
- GitHub Actions でのセットアップ

当初 `requirements.txt` / `requirements-dev.txt` で管理していたが、Pythonバージョン自体は固定されておらず、再現性に懸念があった。

## 決定

**uv** を採用し、`pyproject.toml` で依存関係とPythonバージョンを一元管理する。

## 理由

- バージョン管理（`uv python pin`）・パッケージ管理・仮想環境を1ツールで完結できる
- `pip` と比較して10〜100倍高速なインストール
- `pyproject.toml` による依存分離（本番 / 開発）が標準的な形式で行える
- GitHub Actions に `astral-sh/setup-uv` アクションが存在し、CI連携が容易
- `.python-version` ファイルでPythonバージョンをリポジトリに固定できる

## 検討した選択肢

### 選択肢 A: uv（採用）

- **概要**: Rust製の高速パッケージ・バージョン管理ツール。`pyproject.toml` で管理
- **メリット**: 高速、バージョン管理とパッケージ管理を一本化、モダンなツールチェーン
- **デメリット**: 比較的新しいツールのため、チームによっては学習コストが発生する可能性がある

### 選択肢 B: pyenv + pip + venv

- **概要**: Pythonバージョン管理に pyenv、パッケージに pip、仮想環境に venv を使う従来の構成
- **メリット**: 実績が長く情報が豊富
- **デメリット**: ツールが分散しており、セットアップ手順が煩雑。CI設定も複数ステップになる

### 選択肢 C: mise

- **概要**: Node/Ruby/Go など多言語を横断的に管理できるバージョンマネージャー
- **メリット**: 複数言語プロジェクトで統一管理できる
- **デメリット**: このプロジェクトはPythonのみのため、多言語対応のメリットを活かせない

## 結果

### ポジティブな結果

- `.python-version` によりPythonバージョンがリポジトリで固定され、環境差異がなくなる
- `uv sync` 一発でセットアップ完了
- GitHub Actions のインストールステップが高速化される

### ネガティブな結果 / トレードオフ

- `requirements.txt` に慣れた開発者は `pyproject.toml` の記法を学ぶ必要がある

### 中立的な結果

- `requirements.txt` / `requirements-dev.txt` を削除し `pyproject.toml` に一本化

## 関連するADR

- [ADR-0006: 実装言語の選定](./ADR-0006-language.md)

## 参考資料

- https://docs.astral.sh/uv/
- https://github.com/astral-sh/setup-uv
