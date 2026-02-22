import json

def lambda_handler(event, context):
    """
    API Gateway (HTTP API) から渡されるイベントからIPアドレスを抽出して返す
    """

    # 1. イベントオブジェクトからクライアントのIPアドレスを取得
    # 1-1. REST API (v1) の構造から探す（今回のJSONのパターン）
    ip_address = event.get('requestContext', {}).get('identity', {}).get('sourceIp')
    
    # 1-2. もし空なら、HTTP API (v2) の構造から探す
    if not ip_address:
        ip_address = event.get('requestContext', {}).get('http', {}).get('sourceIp')
        
    # 1-3. それでもダメならヘッダーから探す（プロキシ経由など）
    if not ip_address:
        ip_address = event.get('headers', {}).get('X-Forwarded-For', '').split(',')[0]

    # 1-4. それでも見つからない場合は "unknown" とする
    if not ip_address:
        ip_address = "unknown"

    # 2. レスポンスの作成
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            # GitHub PagesからJavaScriptで呼び出すために必要（CORS対応）
            "Access-Control-Allow-Origin": "*" 
        },
        "body": json.dumps({
            "ip": ip_address
        }),
    }