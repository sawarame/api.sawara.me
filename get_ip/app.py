import json

def lambda_handler(event, context):
    """
    API Gateway (HTTP API) から渡されるイベントからIPアドレスを抽出して返す
    """
    
    # 1. イベントオブジェクトからクライアントのIPアドレスを取得
    # HTTP API (v2) の場合、このパスにIPが含まれます
    try:
        ip_address = event['requestContext']['http']['sourceIp']
    except (KeyError, TypeError):
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