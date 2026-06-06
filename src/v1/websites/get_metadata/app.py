import json
import urllib.parse
import requests
from bs4 import BeautifulSoup

def lambda_handler(event, context):
    """
    指定されたURLのメタデータを取得するLambda関数
    
    @param event: API Gatewayからのイベント情報
    @param context: Lambdaコンテキスト
    @return: メタデータを含むJSONレスポンス
    """
    query_params = event.get('queryStringParameters') or {}
    url = query_params.get('url')

    if not url or not url.startswith(('http://', 'https://')):
        return error_response(400, "Failed to fetch metadata")

    try:
        # HTTP GETリクエスト、タイムアウトを10秒に設定
        headers = {
            "User-Agent": "sawara.me Metadata Fetcher (https://sawara.me)"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # requestsはcharsetが指定されていない場合 'ISO-8859-1' と推測するため、
        # その場合はHTMLのコンテンツから推測（apparent_encoding）を利用して文字化けを防ぐ
        if response.encoding is None or response.encoding.lower() == 'iso-8859-1':
            response.encoding = response.apparent_encoding
            
        html_content = response.text
    except Exception as e:
        print(f"Error fetching URL: {e}")
        return error_response(400, "Failed to fetch metadata")

    # BeautifulSoupでパース
    soup = BeautifulSoup(html_content, 'html.parser')

    # メタデータの抽出
    metadata = extract_metadata(soup, url)

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "https://sawara.me"
        },
        "body": json.dumps(metadata, ensure_ascii=False)
    }

def error_response(status_code, message):
    """
    エラーレスポンスを生成するヘルパー関数
    
    @param status_code: HTTPステータスコード
    @param message: エラーメッセージ
    @return: API Gateway用レスポンス
    """
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "https://sawara.me"
        },
        "body": json.dumps({"error": message}, ensure_ascii=False)
    }

def extract_metadata(soup, base_url):
    """
    HTML文字列（BeautifulSoupオブジェクト）から各メタデータを抽出・整形する
    
    @param soup: BeautifulSoupオブジェクト
    @param base_url: リクエスト対象のベースURL（相対パスの解決用）
    @return: 抽出したメタデータの辞書
    """
    def get_meta_content(name=None, property=None):
        if name:
            tag = soup.find('meta', attrs={'name': name})
            if not tag:
                # 大文字小文字の揺らぎ対応のため、小文字化して検索を試みるサイトもあるが基本はこれでカバー
                tag = soup.find('meta', attrs={'name': lambda x: x and x.lower() == name.lower()})
        elif property:
            tag = soup.find('meta', attrs={'property': property})
        else:
            return ""
        return tag['content'] if tag and tag.has_attr('content') else ""

    # title
    title_tag = soup.find('title')
    title = title_tag.text.strip() if title_tag else ""

    # description, keywords
    description = get_meta_content(name='description')
    keywords = get_meta_content(name='keywords')

    # favicon
    favicon = ""
    icon_tag = soup.find('link', rel=lambda x: x and x.lower() in ['icon', 'shortcut icon'])
    if icon_tag and icon_tag.has_attr('href'):
        favicon = urllib.parse.urljoin(base_url, icon_tag['href'])

    # canonical
    canonical = ""
    canonical_tag = soup.find('link', rel='canonical')
    if canonical_tag and canonical_tag.has_attr('href'):
        canonical = urllib.parse.urljoin(base_url, canonical_tag['href'])

    # og:*
    og_title = get_meta_content(property='og:title')
    og_description = get_meta_content(property='og:description')
    
    og_image = get_meta_content(property='og:image')
    if og_image:
        og_image = urllib.parse.urljoin(base_url, og_image)
        
    og_url = get_meta_content(property='og:url')
    if og_url:
        og_url = urllib.parse.urljoin(base_url, og_url)
        
    og_type = get_meta_content(property='og:type')
    og_site_name = get_meta_content(property='og:site_name')

    # twitter:*
    twitter_card = get_meta_content(name='twitter:card')
    twitter_title = get_meta_content(name='twitter:title')
    twitter_description = get_meta_content(name='twitter:description')
    
    twitter_image = get_meta_content(name='twitter:image')
    if twitter_image:
        twitter_image = urllib.parse.urljoin(base_url, twitter_image)

    # robots
    robots = get_meta_content(name='robots')

    return {
        "title": title,
        "description": description,
        "keywords": keywords,
        "favicon": favicon,
        "canonical": canonical,
        "ogTitle": og_title,
        "ogDescription": og_description,
        "ogImage": og_image,
        "ogUrl": og_url,
        "ogType": og_type,
        "ogSiteName": og_site_name,
        "twitterCard": twitter_card,
        "twitterTitle": twitter_title,
        "twitterDescription": twitter_description,
        "twitterImage": twitter_image,
        "robots": robots
    }
