"""
Vercel Serverless Function: オッズ情報取得API

概要:
    race_idを受け取り、JRA公式サイトからオッズ情報を取得して返す。

制限事項:
    - Vercel Serverless Functionsの実行時間制限に注意（無料プラン: 10秒、Pro: 60秒）
    - Playwrightの実行には時間がかかるため、タイムアウトに注意
"""

import json
import asyncio
import sys
from pathlib import Path

# 親ディレクトリをパスに追加（extract_odds.pyをインポートするため）
sys.path.insert(0, str(Path(__file__).parent.parent))

from extract_odds import RealtimeOdds


async def fetch_odds(race_id: str) -> dict:
    """
    指定されたrace_idのオッズ情報を取得する。
    
    Parameters
    ----------
    race_id : str
        JRA形式のrace_id
    
    Returns
    -------
    dict
        オッズ情報を含む辞書。キーは 'tansho', 'fukusho', 'umaren', 'error'
    """
    try:
        # RealtimeOddsインスタンスを作成
        odds_extractor = RealtimeOdds(race_id)
        
        # HTMLを取得（単勝・複勝、馬連を含む）
        await odds_extractor.scrape_html(
            skip_bet_types=["wakuren", "wide", "umatan", "sanrenpuku", "sanrentan"],
            headless=True,
            delay_time=500,  # Vercelのタイムアウトを考慮して短縮
        )
        
        # 単勝オッズを抽出
        odds_extractor.extract_tansho()
        
        # 複勝オッズを抽出
        odds_extractor.extract_fukusho()
        
        # 馬連オッズを抽出
        odds_extractor.extract_umaren()
        
        return {
            "tansho": getattr(odds_extractor, "tansho", {}),
            "fukusho": getattr(odds_extractor, "fukusho", {}),
            "umaren": getattr(odds_extractor, "umaren", {}),
            "error": None,
        }
    except Exception as e:
        return {
            "tansho": {},
            "fukusho": {},
            "umaren": {},
            "error": str(e),
        }


def handler(request):
    """
    Vercel Serverless Functionのハンドラー関数。
    
    Parameters
    ----------
    request : Request
        Vercelのリクエストオブジェクト
    
    Returns
    -------
    Response
        HTTPレスポンス（辞書形式: {statusCode, headers, body}）
    """
    # CORSヘッダー
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
        "Content-Type": "application/json",
    }
    
    # リクエストメソッドを取得
    method = getattr(request, "method", "GET")
    
    # OPTIONSリクエストの処理（CORS preflight）
    if method == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": headers,
            "body": "",
        }
    
    try:
        # クエリパラメータを取得
        from urllib.parse import urlparse, parse_qs
        
        # リクエストURLを取得
        url = getattr(request, "url", "/")
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        
        # リストを単一値に変換
        query_params = {k: v[0] if isinstance(v, list) and len(v) > 0 else None 
                       for k, v in query_params.items()}
        
        # race_idを取得
        race_id = query_params.get("race_id")
        
        if not race_id:
            return {
                "statusCode": 400,
                "headers": headers,
                "body": json.dumps({
                    "success": False,
                    "error": "race_idパラメータが必要です",
                }),
            }
        
        # オッズを取得（非同期処理を実行）
        odds_data = asyncio.run(fetch_odds(race_id))
        
        if odds_data.get("error"):
            return {
                "statusCode": 500,
                "headers": headers,
                "body": json.dumps({
                    "success": False,
                    "error": odds_data["error"],
                }),
            }
        
        # 成功レスポンス
        return {
            "statusCode": 200,
            "headers": headers,
            "body": json.dumps({
                "success": True,
                "data": {
                    "tansho": odds_data["tansho"],
                    "fukusho": odds_data["fukusho"],
                    "umaren": odds_data["umaren"],
                },
            }),
        }
    
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": headers,
            "body": json.dumps({
                "success": False,
                "error": str(e),
            }),
        }
