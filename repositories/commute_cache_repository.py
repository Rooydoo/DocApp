"""
通勤時間キャッシュリポジトリ
"""
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import and_
from database.models.commute_cache import CommuteCache
from repositories.base_repository import BaseRepository
from utils.logger import get_logger
from utils.exceptions import RecordNotFoundException

logger = get_logger(__name__)


class CommuteCacheRepository(BaseRepository[CommuteCache]):
    """通勤時間キャッシュリポジトリ"""
    
    def __init__(self, db: Session):
        super().__init__(CommuteCache, db)
    
    def get_by_staff_and_hospital(
        self, 
        staff_id: int, 
        hospital_id: int
    ) -> Optional[CommuteCache]:
        """
        職員IDと病院IDで検索
        
        Args:
            staff_id: 職員ID
            hospital_id: 病院ID
        
        Returns:
            CommuteCache: キャッシュインスタンス、存在しない場合None
        """
        return self.db.query(CommuteCache).filter(
            and_(
                CommuteCache.staff_id == staff_id,
                CommuteCache.hospital_id == hospital_id
            )
        ).first()
    
    def create_or_update(
        self,
        staff_id: int,
        hospital_id: int,
        distance_meters: Optional[int] = None,
        duration_seconds: Optional[int] = None
    ) -> CommuteCache:
        """
        キャッシュを作成または更新
        
        Args:
            staff_id: 職員ID
            hospital_id: 病院ID
            distance_meters: 距離（メートル）
            duration_seconds: 所要時間（秒）
        
        Returns:
            CommuteCache: キャッシュインスタンス
        """
        existing = self.get_by_staff_and_hospital(staff_id, hospital_id)
        
        # データ整形
        cache_data = {
            "staff_id": staff_id,
            "hospital_id": hospital_id,
        }
        
        # distance_meters と duration_seconds を driving_distance_km と driving_time_minutes に変換
        if distance_meters is not None:
            cache_data["driving_distance_km"] = round(distance_meters / 1000, 2)
        else:
            cache_data["driving_distance_km"] = None
        
        if duration_seconds is not None:
            cache_data["driving_time_minutes"] = round(duration_seconds / 60)
        else:
            cache_data["driving_time_minutes"] = None
        
        if existing:
            # 更新
            return self.update(existing.id, cache_data)
        else:
            # 新規作成
            return self.create(cache_data)
    
    def get_by_staff(self, staff_id: int) -> List[CommuteCache]:
        """
        職員の全キャッシュを取得
        
        Args:
            staff_id: 職員ID
        
        Returns:
            List[CommuteCache]: キャッシュのリスト
        """
        return self.db.query(CommuteCache).filter(
            CommuteCache.staff_id == staff_id
        ).all()
    
    def get_by_hospital(self, hospital_id: int) -> List[CommuteCache]:
        """
        病院の全キャッシュを取得
        
        Args:
            hospital_id: 病院ID
        
        Returns:
            List[CommuteCache]: キャッシュのリスト
        """
        return self.db.query(CommuteCache).filter(
            CommuteCache.hospital_id == hospital_id
        ).all()
    
    def delete_by_staff(self, staff_id: int) -> int:
        """
        職員の全キャッシュを削除
        
        Args:
            staff_id: 職員ID
        
        Returns:
            int: 削除件数
        """
        count = self.db.query(CommuteCache).filter(
            CommuteCache.staff_id == staff_id
        ).delete()
        self.db.commit()
        logger.info(f"Deleted {count} commute caches for staff_id={staff_id}")
        return count
    
    def delete_by_hospital(self, hospital_id: int) -> int:
        """
        病院の全キャッシュを削除
        
        Args:
            hospital_id: 病院ID
        
        Returns:
            int: 削除件数
        """
        count = self.db.query(CommuteCache).filter(
            CommuteCache.hospital_id == hospital_id
        ).delete()
        self.db.commit()
        logger.info(f"Deleted {count} commute caches for hospital_id={hospital_id}")
        return count
    
    def delete_all(self) -> int:
        """
        全キャッシュを削除
        
        Returns:
            int: 削除件数
        """
        count = self.db.query(CommuteCache).delete()
        self.db.commit()
        logger.info(f"Deleted all commute caches: {count} records")
        return count
    
    def get_commute_info(self, staff_id: int, hospital_id: int) -> Dict:
        """
        通勤情報を取得（GA用）
        
        Args:
            staff_id: 職員ID
            hospital_id: 病院ID
        
        Returns:
            Dict: 通勤情報
                {
                    "time_minutes": int,
                    "distance_km": float
                }
        
        Raises:
            RecordNotFoundException: キャッシュが存在しない
        """
        cache = self.get_by_staff_and_hospital(staff_id, hospital_id)
        if not cache:
            raise RecordNotFoundException(
                "CommuteCache",
                details={
                    "staff_id": staff_id,
                    "hospital_id": hospital_id
                }
            )
        
        return {
            "time_minutes": cache.driving_time_minutes,
            "distance_km": float(cache.driving_distance_km)
        }