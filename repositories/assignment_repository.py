"""
配置リポジトリ
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from database.models.assignment import Assignment
from repositories.base_repository import BaseRepository
from utils.logger import get_logger

logger = get_logger(__name__)


class AssignmentRepository(BaseRepository[Assignment]):
    """配置リポジトリ"""
    
    def __init__(self, db: Session):
        super().__init__(Assignment, db)
    
    def get_by_fiscal_year(self, fiscal_year: int) -> List[Assignment]:
        """
        年度で検索
        
        Args:
            fiscal_year: 年度
        
        Returns:
            List[Assignment]: 配置のリスト
        """
        return self.db.query(Assignment).filter(
            Assignment.fiscal_year == fiscal_year
        ).all()
    
    def get_by_staff_and_year(self, staff_id: int, fiscal_year: int) -> Optional[Assignment]:
        """
        職員IDと年度で検索
        
        Args:
            staff_id: 職員ID
            fiscal_year: 年度
        
        Returns:
            Assignment: 配置インスタンス、存在しない場合None
        """
        return self.db.query(Assignment).filter(
            and_(
                Assignment.staff_id == staff_id,
                Assignment.fiscal_year == fiscal_year
            )
        ).first()
    
    def get_by_hospital_and_year(self, hospital_id: int, fiscal_year: int) -> List[Assignment]:
        """
        病院IDと年度で検索
        
        Args:
            hospital_id: 病院ID
            fiscal_year: 年度
        
        Returns:
            List[Assignment]: 配置のリスト
        """
        return self.db.query(Assignment).filter(
            and_(
                Assignment.hospital_id == hospital_id,
                Assignment.fiscal_year == fiscal_year
            )
        ).all()
    
    def get_mismatched_assignments(self, fiscal_year: int) -> List[Assignment]:
        """
        アンマッチ配置を取得
        
        Args:
            fiscal_year: 年度
        
        Returns:
            List[Assignment]: アンマッチ配置のリスト
        """
        return self.db.query(Assignment).filter(
            and_(
                Assignment.fiscal_year == fiscal_year,
                Assignment.mismatch_flag == True
            )
        ).all()
    
    def get_matched_assignments(self, fiscal_year: int) -> List[Assignment]:
        """
        マッチ配置を取得
        
        Args:
            fiscal_year: 年度
        
        Returns:
            List[Assignment]: マッチ配置のリスト
        """
        return self.db.query(Assignment).filter(
            and_(
                Assignment.fiscal_year == fiscal_year,
                Assignment.mismatch_flag == False
            )
        ).all()
    
    def get_staff_history(self, staff_id: int) -> List[Assignment]:
        """
        職員の配置履歴を取得
        
        Args:
            staff_id: 職員ID
        
        Returns:
            List[Assignment]: 配置履歴のリスト（年度降順）
        """
        return self.db.query(Assignment).filter(
            Assignment.staff_id == staff_id
        ).order_by(Assignment.fiscal_year.desc()).all()
    
    def count_hospital_assignments(self, hospital_id: int, fiscal_year: int) -> int:
        """
        病院の配置数をカウント
        
        Args:
            hospital_id: 病院ID
            fiscal_year: 年度
        
        Returns:
            int: 配置数
        """
        return self.db.query(Assignment).filter(
            and_(
                Assignment.hospital_id == hospital_id,
                Assignment.fiscal_year == fiscal_year
            )
        ).count()
    
    def has_previous_mismatch(self, staff_id: int, hospital_id: int) -> bool:
        """
        過去にアンマッチがあったか確認
        
        Args:
            staff_id: 職員ID
            hospital_id: 病院ID
        
        Returns:
            bool: 過去にアンマッチがある場合True
        """
        count = self.db.query(Assignment).filter(
            and_(
                Assignment.staff_id == staff_id,
                Assignment.hospital_id == hospital_id,
                Assignment.mismatch_flag == True
            )
        ).count()
        return count > 0
