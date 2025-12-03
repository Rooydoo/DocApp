"""
病院リポジトリ
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from database.models.hospital import Hospital
from repositories.base_repository import BaseRepository
from utils.logger import get_logger

logger = get_logger(__name__)


class HospitalRepository(BaseRepository[Hospital]):
    """病院リポジトリ"""
    
    def __init__(self, db: Session):
        super().__init__(Hospital, db)
    
    def get_by_name(self, name: str) -> Optional[Hospital]:
        """
        病院名で検索
        
        Args:
            name: 病院名
        
        Returns:
            Hospital: 病院インスタンス、存在しない場合None
        """
        return self.db.query(Hospital).filter(Hospital.name == name).first()
    
    def get_outpatient_hospitals(self) -> List[Hospital]:
        """
        外勤対象病院を取得
        
        Returns:
            List[Hospital]: 外勤対象病院のリスト
        """
        return self.db.query(Hospital).filter(Hospital.outpatient_flag == True).all()
    
    def get_hospitals_with_address(self) -> List[Hospital]:
        """
        住所が登録されている全病院を取得
        
        Returns:
            List[Hospital]: 住所ありの病院のリスト
        """
        return self.db.query(Hospital).filter(
            Hospital.address.isnot(None),
            Hospital.address != ""
        ).all()
    
    def get_by_capacity_range(self, min_capacity: int, max_capacity: int) -> List[Hospital]:
        """
        受入人数範囲で検索
        
        Args:
            min_capacity: 最小受入人数
            max_capacity: 最大受入人数
        
        Returns:
            List[Hospital]: 病院のリスト
        """
        return self.db.query(Hospital).filter(
            Hospital.capacity >= min_capacity,
            Hospital.capacity <= max_capacity
        ).all()
    
    def search_by_keyword(self, keyword: str) -> List[Hospital]:
        """
        キーワードで検索（病院名、住所、院長名）
        
        Args:
            keyword: 検索キーワード
        
        Returns:
            List[Hospital]: 病院のリスト
        """
        search_pattern = f"%{keyword}%"
        return self.db.query(Hospital).filter(
            (Hospital.name.like(search_pattern)) |
            (Hospital.address.like(search_pattern)) |
            (Hospital.director_name.like(search_pattern))
        ).all()