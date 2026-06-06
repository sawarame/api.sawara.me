# 取得IPアドレスAPI (get_ipaddress) 仕様

クライアントからリクエストを受け取り、アクセス元のIPアドレスを特定してJSON形式で返却するAPI

## 処理概要
IPアドレスは以下の順序で探索・抽出される。
1. API Gatewayの `requestContext.identity.sourceIp` (REST API想定)
2. API Gatewayの `requestContext.http.sourceIp` (HTTP API想定)
3. HTTPヘッダーの `X-Forwarded-For`
※いずれからも取得できない場合は `"unknown"` が返却される。

## URL(パス)
- **メソッド**: `GET`
- **パス**: `/v1/ipaddress`

## リクエストパラメーター
特になし

## レスポンスパラメーター

- **`ip`** (String): クライアントの送信元IPアドレス。取得できなかった場合は `"unknown"` となる。

### json例
```json
{
  "ip": "203.0.113.1"
}
```


## その他

`https://sawara.me/` 以外のアクセスは `403 Forbidden` を返却