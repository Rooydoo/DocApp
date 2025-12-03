"""
外勤枠リポジトリ
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from database.models.outpatient_slot import OutpatientSlot
from repositories.base_repository import BaseRepository
from utils.logger import get_logger

logger = get_logger(__name__)


class OutpatientSlotRepository(BaseRepository[OutpatientSlot]):
    """外勤枠リポジトリ"""
    
    def __init__(self, db: Session):
        super().__init__(OutpatientSlot, db)
    
    def get_by_hospital(self, hospital_id: int) -> List[OutpatientSlot]:
        """
        病院の外勤枠を取得
        
        Args:
            hospital_id: 病院ID
        
        Returns:
            List[OutpatientSlot]: 外勤枠のリスト
        """
        return self.db.query(OutpatientSlot).filter(
            OutpatientSlot.hospital_id == hospital_id
        ).all()
    
    def get_by_weekday(self, weekday: str) -> List[OutpatientSlot]:
        """
        曜日で検索
        
        Args:
            weekday: 曜日
        
        Returns:
            List[OutpatientSlot]: 外勤枠のリスト
        """
        return self.db.query(OutpatientSlot).filter(
            OutpatientSlot.weekday == weekday
        ).all()
    
    def get_by_time_slot(self, time_slot: str) -> List[OutpatientSlot]:
        """
        時間帯で検索
        
        Args:
            time_slot: 時間帯
        
        Returns:
            List[OutpatientSlot]: 外勤枠のリスト
        """
        return self.db.query(OutpatientSlot).filter(
            OutpatientSlot.time_slot == time_slot
        ).all()
    
    def get_by_schedule(
        self, 
        hospital_id: int,
        weekday: str, 
        time_slot: str
    ) -> Optional[OutpatientSlot]:
        """
        病院・曜日・時間帯で検索
        
        Args:
            hospital_id: 病院ID
            weekday: 曜日
            time_slot: 時間帯
        
        Returns:
            OutpatientSlot: 外勤枠インスタンス、存在しない場合None
        """
        return self.db.query(OutpatientSlot).filter(
            and_(
                OutpatientSlot.hospital_id == hospital_id,
                OutpatientSlot.weekday == weekday,
                OutpatientSlot.time_slot == time_slot
            )
        ).first()
    
    def delete_by_hospital(self, hospital_id: int) -> int:
        """
        病院の全外勤枠を削除
        
        Args:
            hospital_id: 病院ID
        
        Returns:
            int: 削除件数
        """
        count = self.db.query(OutpatientSlot).filter(
            OutpatientSlot.hospital_id == hospital_id
        ).delete()
        self.db.commit()
        logger.info(f"Deleted {count} outpatient slots for hospital_id={hospital_id}")
        return count
