"""
外勤割り当てリポジトリ
"""
from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from database.models.outpatient_assignment import OutpatientAssignment
from repositories.base_repository import BaseRepository
from utils.logger import get_logger

logger = get_logger(__name__)


class OutpatientAssignmentRepository(BaseRepository[OutpatientAssignment]):
    """外勤割り当てリポジトリ"""
    
    def __init__(self, db: Session):
        super().__init__(OutpatientAssignment, db)
    
    def get_by_slot(self, slot_id: int) -> List[OutpatientAssignment]:
        """
        外勤枠の割り当てを取得
        
        Args:
            slot_id: 外勤枠ID
        
        Returns:
            List[OutpatientAssignment]: 割り当てのリスト
        """
        return self.db.query(OutpatientAssignment).filter(
            OutpatientAssignment.slot_id == slot_id
        ).all()
    
    def get_by_staff(self, staff_id: int) -> List[OutpatientAssignment]:
        """
        職員の割り当てを取得
        
        Args:
            staff_id: 職員ID
        
        Returns:
            List[OutpatientAssignment]: 割り当てのリスト
        """
        return self.db.query(OutpatientAssignment).filter(
            OutpatientAssignment.staff_id == staff_id
        ).all()
    
    def get_by_date_range(
        self, 
        start_date: date, 
        end_date: date
    ) -> List[OutpatientAssignment]:
        """
        期間で検索
        
        Args:
            start_date: 開始日
            end_date: 終了日
        
        Returns:
            List[OutpatientAssignment]: 割り当てのリスト
        """
        return self.db.query(OutpatientAssignment).filter(
            or_(
                and_(
                    OutpatientAssignment.start_date >= start_date,
                    OutpatientAssignment.start_date <= end_date
                ),
                and_(
                    OutpatientAssignment.end_date >= start_date,
                    OutpatientAssignment.end_date <= end_date
                )
            )
        ).all()
    
    def get_current_assignment_for_slot(
        self, 
        slot_id: int, 
        current_date: date
    ) -> Optional[OutpatientAssignment]:
        """
        指定日時点での外勤枠の割り当てを取得
        
        Args:
            slot_id: 外勤枠ID
            current_date: 基準日
        
        Returns:
            OutpatientAssignment: 割り当てインスタンス、存在しない場合None
        """
        return self.db.query(OutpatientAssignment).filter(
            and_(
                OutpatientAssignment.slot_id == slot_id,
                OutpatientAssignment.start_date <= current_date,
                OutpatientAssignment.end_date >= current_date
            )
        ).first()
    
    def delete_by_slot(self, slot_id: int) -> int:
        """
        外勤枠の全割り当てを削除
        
        Args:
            slot_id: 外勤枠ID
        
        Returns:
            int: 削除件数
        """
        count = self.db.query(OutpatientAssignment).filter(
            OutpatientAssignment.slot_id == slot_id
        ).delete()
        self.db.commit()
        logger.info(f"Deleted {count} outpatient assignments for slot_id={slot_id}")
        return count
    
    def delete_by_staff(self, staff_id: int) -> int:
        """
        職員の全割り当てを削除
        
        Args:
            staff_id: 職員ID
        
        Returns:
            int: 削除件数
        """
        count = self.db.query(OutpatientAssignment).filter(
            OutpatientAssignment.staff_id == staff_id
        ).delete()
        self.db.commit()
        logger.info(f"Deleted {count} outpatient assignments for staff_id={staff_id}")
        return count
