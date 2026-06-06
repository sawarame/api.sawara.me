# プロジェクト仕様書 (api.sawara.me)

## 1. プロジェクトの目的
本プロジェクトは、AWS SAM (Serverless Application Model) を利用して構築されたサーバーレスAPIです。主に `sawara.me` ドメインからのリクエストに対して、各種API機能（現在はクライアントのIPアドレス取得機能など）を提供することを目的としています。

## 2. システム構成・技術スタック
- **インフラストラクチャ/フレームワーク**: AWS SAM
- **プログラミング言語・ランタイム**: Python
- **CI/CD**: GitHub Actions による自動デプロイ (`.github/workflows/deploy.yml`)

## 3. セキュリティとアクセス制御
- **ドメイン制限**: セキュリティの観点から、`sawara.me` ドメイン以外からのアクセスは拒否されるよう、設定（`template.yaml`）で制御されています。

## 4. ディレクトリ構成概要
- `src/v1/get_ipaddress/`: IPアドレス取得APIのソースコードおよび要件定義（`app.py`, `requirements.txt`）
- `template.yaml`: AWS SAM のインフラリソース定義
- `samconfig.toml`: デプロイ時の設定情報
- `.github/workflows/`: GitHub Actions のワークフロー定義
