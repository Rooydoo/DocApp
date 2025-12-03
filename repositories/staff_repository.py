"""
職員リポジトリ
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from database.models.staff import Staff
from repositories.base_repository import BaseRepository
from config.constants import StaffType
from utils.logger import get_logger

logger = get_logger(__name__)


class StaffRepository(BaseRepository[Staff]):
    """職員リポジトリ"""
    
    def __init__(self, db: Session):
        super().__init__(Staff, db)
    
    def get_by_email(self, email: str) -> Optional[Staff]:
        """
        メールアドレスで検索
        
        Args:
            email: メールアドレス
        
        Returns:
            Staff: 職員インスタンス、存在しない場合None
        """
        return self.db.query(Staff).filter(Staff.email == email).first()
    
    def get_by_staff_type(self, staff_type: str) -> List[Staff]:
        """
        職員種別で検索
        
        Args:
            staff_type: 職員種別
        
        Returns:
            List[Staff]: 職員のリスト
        """
        return self.db.query(Staff).filter(Staff.staff_type == staff_type).all()
    
    def get_resident_doctors(self) -> List[Staff]:
        """
        選考医を全て取得
        
        Returns:
            List[Staff]: 選考医のリスト
        """
        return self.get_by_staff_type(StaffType.RESIDENT_DOCTOR)
    
    def get_resident_doctors_with_address(self) -> List[Staff]:
        """
        住所が登録されている全選考医を取得
        
        Returns:
            List[Staff]: 住所ありの選考医のリスト
        """
        return self.db.query(Staff).filter(
            Staff.staff_type == StaffType.RESIDENT_DOCTOR,
            Staff.address.isnot(None),
            Staff.address != ""
        ).all()
    
    def search_by_keyword(self, keyword: str) -> List[Staff]:
        """
        キーワードで検索（氏名、メールアドレス）
        
        Args:
            keyword: 検索キーワード
        
        Returns:
            List[Staff]: 職員のリスト
        """
        search_pattern = f"%{keyword}%"
        return self.db.query(Staff).filter(
            (Staff.name.like(search_pattern)) |
            (Staff.email.like(search_pattern))
        ).all()
    
    def count_by_staff_type(self, staff_type: str) -> int:
        """
        職員種別ごとの人数をカウント
        
        Args:
            staff_type: 職員種別
        
        Returns:
            int: 人数
        """
        return self.db.query(Staff).filter(Staff.staff_type == staff_type).count()