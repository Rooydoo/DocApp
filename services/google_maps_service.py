"""
Google Maps Distance Matrix API サービス
"""
import requests
from typing import Optional, Dict
from config.settings import settings
from config.constants import GoogleMapsConfig
from utils.logger import get_logger
from utils.exceptions import APIException

logger = get_logger(__name__)


class GoogleMapsService:
    """
    Google Maps Distance Matrix API クライアント
    
    使用例:
        service = GoogleMapsService()
        result = service.get_distance_and_duration(
            origin="東京都千代田区丸の内1-1-1",
            destination="東京都港区六本木6-10-1"
        )
        if result:
            print(f"距離: {result['distance_meters']}m")
            print(f"所要時間: {result['duration_seconds']}秒")
    """
    
    API_ENDPOINT = "https://maps.googleapis.com/maps/api/distancematrix/json"
    MAX_RETRIES = 3
    
    def __init__(self):
        """初期化"""
        self.api_key = settings.GOOGLE_MAPS_API_KEY
        
        if not self.api_key:
            logger.warning("Google Maps API Key is not configured")
    
    def get_distance_and_duration(
        self,
        origin: str,
        destination: str
    ) -> Optional[Dict[str, int]]:
        """
        2地点間の距離と所要時間を取得
        
        Args:
            origin: 出発地住所
            destination: 目的地住所
            
        Returns:
            {
                "distance_meters": int,      # 距離（メートル）
                "duration_seconds": int      # 所要時間（秒）
            }
            取得失敗時は None
        """
        if not self.api_key:
            logger.warning("Google Maps API Key is not configured, skipping distance calculation")
            return None
        
        if not origin or not destination:
            logger.warning("Origin or destination is empty")
            return None
        
        # リトライ処理
        for attempt in range(self.MAX_RETRIES):
            try:
                result = self._call_api(origin, destination)
                
                if result:
                    logger.info(
                        f"Distance calculated: {origin} -> {destination} "
                        f"({result['distance_meters']}m, {result['duration_seconds']}s)"
                    )
                    return result
                
                logger.warning(f"Failed to get distance (attempt {attempt + 1}/{self.MAX_RETRIES})")
            
            except Exception as e:
                logger.error(f"API call failed (attempt {attempt + 1}/{self.MAX_RETRIES}): {e}")
                
                if attempt == self.MAX_RETRIES - 1:
                    raise APIException(f"Google Maps API call failed after {self.MAX_RETRIES} retries: {e}")
        
        return None
    
    def _call_api(self, origin: str, destination: str) -> Optional[Dict[str, int]]:
        """
        Distance Matrix API を呼び出し
        
        Args:
            origin: 出発地住所
            destination: 目的地住所
            
        Returns:
            距離・所要時間の辞書、または None
        """
        params = {
            "origins": origin,
            "destinations": destination,
            "mode": GoogleMapsConfig.MODE,
            "units": GoogleMapsConfig.UNITS,
            "key": self.api_key,
            "language": "ja"
        }
        
        response = requests.get(self.API_ENDPOINT, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # ステータスチェック
        if data.get("status") != "OK":
            logger.error(f"API returned error status: {data.get('status')}")
            return None
        
        # レスポンス解析
        rows = data.get("rows", [])
        if not rows:
            logger.error("No rows in API response")
            return None
        
        elements = rows[0].get("elements", [])
        if not elements:
            logger.error("No elements in API response")
            return None
        
        element = elements[0]
        
        # 個別要素のステータスチェック
        if element.get("status") != "OK":
            logger.error(f"Element status error: {element.get('status')}")
            return None
        
        # 距離・所要時間を抽出
        distance = element.get("distance", {})
        duration = element.get("duration", {})
        
        if not distance or not duration:
            logger.error("Missing distance or duration in API response")
            return None
        
        return {
            "distance_meters": distance.get("value"),
            "duration_seconds": duration.get("value")
        }


# シングルトンインスタンス
google_maps_service = GoogleMapsService()
