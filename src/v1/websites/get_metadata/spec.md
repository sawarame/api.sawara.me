# WEBサイトメタデータ取得API (get_metadata) 仕様

パラメーターで指定されたURLのメタ情報を返却するAPI

## 処理概要

AWS Lambda (Python 3.12) を利用して、指定されたURLからHTMLを取得し、BeautifulSoupを用いてメタデータを抽出する。

1. **リクエストのバリデーション**
   - イベントの `queryStringParameters` から `url` を取得。
   - 未指定や不正なURL形式の場合は、ステータス `400` で `{"error": "Failed to fetch metadata"}` を返却。
2. **HTMLの取得**
   - サードパーティライブラリ（`requests` 等）を使用し、対象URLへGETリクエストを送信。
   - 外部通信の遅延による関数のフリーズを防ぐため、通信時のタイムアウト（例: 10秒）を設定する（併せてSAMテンプレート上の関数タイムアウトも延長する）。
   - アクセス失敗時やタイムアウト時も同様に、ステータス `400` で `{"error": "Failed to fetch metadata"}` を返却。
   - 取得したレスポンスのエンコーディングを適切にデコードして文字化けを防ぐ。
3. **メタデータの抽出 (BeautifulSoup4を使用)**
   - 以下の要素を抽出する。
     - `<title>` タグ
     - `<meta name="...">`（`description`, `keywords`, `twitter:*` 等）
     - `<meta property="og:...">`（`og:*` 等）
     - `<link rel="canonical">`
     - `<link rel="icon">`, `<link rel="shortcut icon">`（Favicon）
   - 対象タグ・属性が存在しない場合は空文字 `""` を設定する。
   - `favicon` や `og:image` などが相対パスの場合は、対象URLをベースに絶対パスへ変換する。
   - ※SPA（シングルページアプリケーション）の対応については、Lambda上でのヘッドレスブラウザ（Playwright等）の導入・環境構築が複雑化・大規模化するため、本APIではサポート対象外とし、静的HTMLのパースのみを行う。
4. **レスポンス返却**
   - 抽出したデータをJSONに整形し、ステータス `200` で返却。
   - CORS対応として、レスポンスヘッダーに `Access-Control-Allow-Origin: https://sawara.me` を付与する。

## URL(パス)
- **メソッド**: `GET`
- **パス**: `/v1/website/metadata`

## リクエストパラメーター
- **`url`**: メタデータを取得する対象のURL
  - 例: https://sawara.me

## レスポンスパラメーター

### json例
```json
{
  "title": "sawara.me",
  "description": "sawara.me — 日常のちょっとした不便を解決する、小さな便利ツールやアプリケーションを公開しているサイトです。",
  "keywords": "Webツール, 便利ツール, ミニツール, 開発者向けツール, ブラウザ拡張機能, sawara.me",
  "favicon": "https://sawara.me/img/sawara_favicon.svg",
  "canonical": "https://sawara.me/",
  "ogTitle": "sawara.me",
  "ogDescription": "sawara.me — 日常のちょっとした不便を解決する、小さな便利ツールやアプリケーションを公開しているサイトです。",
  "ogImage": "https://sawara.me/img/sawara-ogp.png",
  "ogUrl": "https://sawara.me/",
  "ogType": "",
  "ogSiteName": "",
  "twitterCard": "summary_large_image",
  "twitterTitle": "sawara.me",
  "twitterDescription": "sawara.me — 日常のちょっとした不便を解決する、小さな便利ツールやアプリケーションを公開しているサイトです。",
  "twitterImage": "https://sawara.me/img/sawara-ogp.png",
  "robots": ""
}
```

- **`title`**: タイトル 
- **`description`**: 説明文 (Description)
- **`keywords`**: キーワード (Keywords)
- **`favicon`**: Favicon URL
- **`canonical`**: Canonical URL
- **`ogTitle`**: og:title
- **`ogDescription`**: og:description
- **`ogImage`**: og:image URL
- **`ogUrl`**: og:url
- **`ogType`**: og:type
- **`ogSiteName`**: og:site_name
- **`twitterCard`**: twitter:card
- **`twitterTitle`**: twitter:title
- **`twitterDescription`**: twitter:description
- **`twitterImage`**: twitter:image
- **`robots`**: 検索回避 (Robots)

## その他

`https://sawara.me/` 以外のアクセスは `403 Forbidden` を返却