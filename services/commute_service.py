"""
通勤時間管理サービス
"""
from typing import Optional
from database.connection import get_db_session
from repositories.hospital_repository import HospitalRepository
from repositories.staff_repository import StaffRepository
from repositories.commute_cache_repository import CommuteCacheRepository
from services.google_maps_service import google_maps_service
from config.constants import StaffType
from utils.logger import get_logger
from utils.exceptions import RecordNotFoundException

logger = get_logger(__name__)


class CommuteService:
    """
    通勤時間キャッシュ管理サービス
    
    責務:
    - 病院・選考医の住所変更時に通勤時間キャッシュを更新
    - Google Maps APIを使用して距離・所要時間を計算
    - キャッシュの一括更新・個別更新
    """
    
    def update_commute_cache_for_hospital(self, hospital_id: int):
        """
        病院の住所変更時、全選考医との通勤時間を再計算
        
        Args:
            hospital_id: 病院ID
        """
        logger.info(f"Updating commute cache for hospital {hospital_id}")
        
        try:
            with get_db_session() as db:
                hospital_repo = HospitalRepository(db)
                staff_repo = StaffRepository(db)
                cache_repo = CommuteCacheRepository(db)
                
                # 病院情報取得
                hospital = hospital_repo.get_or_raise(hospital_id)
                
                if not hospital.address:
                    logger.warning(f"Hospital {hospital_id} has no address, skipping cache update")
                    return
                
                # 全選考医を取得（住所あり）
                resident_doctors = staff_repo.get_resident_doctors_with_address()
                
                logger.info(f"Found {len(resident_doctors)} resident doctors with address")
                
                # 各選考医との通勤時間を計算・更新
                for staff in resident_doctors:
                    self._update_cache_entry(
                        cache_repo=cache_repo,
                        staff_id=staff.id,
                        hospital_id=hospital.id,
                        staff_address=staff.address,
                        hospital_address=hospital.address
                    )
                
                logger.info(f"Commute cache update completed for hospital {hospital_id}")
        
        except RecordNotFoundException as e:
            logger.error(f"Hospital {hospital_id} not found: {e}")
            raise
        
        except Exception as e:
            logger.error(f"Failed to update commute cache for hospital {hospital_id}: {e}")
            raise
    
    def update_commute_cache_for_staff(self, staff_id: int):
        """
        選考医の住所変更時、全病院との通勤時間を再計算
        
        Args:
            staff_id: 職員ID
        """
        logger.info(f"Updating commute cache for staff {staff_id}")
        
        try:
            with get_db_session() as db:
                staff_repo = StaffRepository(db)
                hospital_repo = HospitalRepository(db)
                cache_repo = CommuteCacheRepository(db)
                
                # 職員情報取得
                staff = staff_repo.get_or_raise(staff_id)
                
                # 選考医でない場合はスキップ
                if staff.staff_type != StaffType.RESIDENT_DOCTOR:
                    logger.warning(f"Staff {staff_id} is not a resident doctor, skipping cache update")
                    return
                
                if not staff.address:
                    logger.warning(f"Staff {staff_id} has no address, skipping cache update")
                    return
                
                # 全病院を取得（住所あり）
                hospitals = hospital_repo.get_hospitals_with_address()
                
                logger.info(f"Found {len(hospitals)} hospitals with address")
                
                # 各病院との通勤時間を計算・更新
                for hospital in hospitals:
                    self._update_cache_entry(
                        cache_repo=cache_repo,
                        staff_id=staff.id,
                        hospital_id=hospital.id,
                        staff_address=staff.address,
                        hospital_address=hospital.address
                    )
                
                logger.info(f"Commute cache update completed for staff {staff_id}")
        
        except RecordNotFoundException as e:
            logger.error(f"Staff {staff_id} not found: {e}")
            raise
        
        except Exception as e:
            logger.error(f"Failed to update commute cache for staff {staff_id}: {e}")
            raise
    
    def rebuild_all_cache(self):
        """
        全ての通勤時間キャッシュを再構築
        
        注意: 大量のAPI呼び出しが発生するため、使用は慎重に
        """
        logger.info("Starting full commute cache rebuild")
        
        try:
            with get_db_session() as db:
                staff_repo = StaffRepository(db)
                hospital_repo = HospitalRepository(db)
                cache_repo = CommuteCacheRepository(db)
                
                # 既存キャッシュを削除
                cache_repo.delete_all()
                logger.info("Existing cache cleared")
                
                # 全選考医を取得（住所あり）
                resident_doctors = staff_repo.get_resident_doctors_with_address()
                
                # 全病院を取得（住所あり）
                hospitals = hospital_repo.get_hospitals_with_address()
                
                logger.info(
                    f"Rebuilding cache for {len(resident_doctors)} resident doctors "
                    f"and {len(hospitals)} hospitals"
                )
                
                total = len(resident_doctors) * len(hospitals)
                current = 0
                
                # 全組み合わせの通勤時間を計算
                for staff in resident_doctors:
                    for hospital in hospitals:
                        current += 1
                        
                        if current % 10 == 0:
                            logger.info(f"Cache rebuild progress: {current}/{total}")
                        
                        self._update_cache_entry(
                            cache_repo=cache_repo,
                            staff_id=staff.id,
                            hospital_id=hospital.id,
                            staff_address=staff.address,
                            hospital_address=hospital.address
                        )
                
                logger.info(f"Full cache rebuild completed: {total} entries processed")
        
        except Exception as e:
            logger.error(f"Failed to rebuild cache: {e}")
            raise
    
    def _update_cache_entry(
        self,
        cache_repo: CommuteCacheRepository,
        staff_id: int,
        hospital_id: int,
        staff_address: str,
        hospital_address: str
    ):
        """
        通勤時間キャッシュのエントリを更新
        
        Args:
            cache_repo: CommuteCacheRepository インスタンス
            staff_id: 職員ID
            hospital_id: 病院ID
            staff_address: 職員住所
            hospital_address: 病院住所
        """
        try:
            # Google Maps API で距離・所要時間を取得
            result = google_maps_service.get_distance_and_duration(
                origin=staff_address,
                destination=hospital_address
            )
            
            # キャッシュ更新（create_or_updateで重複を自動処理）
            if result:
                cache_repo.create_or_update(
                    staff_id=staff_id,
                    hospital_id=hospital_id,
                    distance_meters=result["distance_meters"],
                    duration_seconds=result["duration_seconds"]
                )
                logger.debug(
                    f"Cache updated: staff={staff_id}, hospital={hospital_id}, "
                    f"distance={result['distance_meters']}m, duration={result['duration_seconds']}s"
                )
            else:
                # API呼び出し失敗時はNULLで保存
                cache_repo.create_or_update(
                    staff_id=staff_id,
                    hospital_id=hospital_id,
                    distance_meters=None,
                    duration_seconds=None
                )
                logger.warning(
                    f"Failed to get distance, saved NULL cache: "
                    f"staff={staff_id}, hospital={hospital_id}"
                )
        
        except Exception as e:
            logger.error(
                f"Failed to update cache entry: "
                f"staff={staff_id}, hospital={hospital_id}, error={e}"
            )


# シングルトンインスタンス
commute_service = CommuteService()
