"""
職員希望登録リポジトリ
"""
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import and_
from database.models.staff_weight import StaffWeight
from repositories.base_repository import BaseRepository
from utils.logger import get_logger

logger = get_logger(__name__)


class StaffWeightRepository(BaseRepository[StaffWeight]):
    """職員希望登録リポジトリ"""
    
    def __init__(self, db: Session):
        super().__init__(StaffWeight, db)
    
    def get_by_staff_and_year(
        self, 
        staff_id: int, 
        fiscal_year: int
    ) -> Optional[StaffWeight]:
        """
        職員IDと年度で検索
        
        Args:
            staff_id: 職員ID
            fiscal_year: 年度
        
        Returns:
            StaffWeight: 希望登録インスタンス、存在しない場合None
        """
        return self.db.query(StaffWeight).filter(
            and_(
                StaffWeight.staff_id == staff_id,
                StaffWeight.fiscal_year == fiscal_year
            )
        ).first()
    
    def get_by_fiscal_year(self, fiscal_year: int) -> List[StaffWeight]:
        """
        年度で検索
        
        Args:
            fiscal_year: 年度
        
        Returns:
            List[StaffWeight]: 希望登録のリスト
        """
        return self.db.query(StaffWeight).filter(
            StaffWeight.fiscal_year == fiscal_year
        ).all()
    
    def create_or_update(self, weight_data: Dict) -> StaffWeight:
        """
        希望登録を作成または更新
        
        Args:
            weight_data: 希望登録データ
                {
                    "staff_id": int,
                    "fiscal_year": int,
                    "first_choice_hospital_id": int,
                    "second_choice_hospital_id": int,
                    "third_choice_hospital_id": int,
                    "first_choice_weight": Decimal,
                    "second_choice_weight": Decimal,
                    "third_choice_weight": Decimal
                }
        
        Returns:
            StaffWeight: 希望登録インスタンス
        """
        staff_id = weight_data["staff_id"]
        fiscal_year = weight_data["fiscal_year"]
        
        existing = self.get_by_staff_and_year(staff_id, fiscal_year)
        
        if existing:
            # 更新
            return self.update(existing.id, weight_data)
        else:
            # 新規作成
            return self.create(weight_data)
    
    def get_staff_choices(
        self, 
        staff_id: int, 
        fiscal_year: int
    ) -> Dict[int, int]:
        """
        職員の希望病院と順位を取得
        
        Args:
            staff_id: 職員ID
            fiscal_year: 年度
        
        Returns:
            Dict[int, int]: {hospital_id: rank}
        """
        weight = self.get_by_staff_and_year(staff_id, fiscal_year)
        if not weight:
            return {}
        
        choices = {}
        if weight.first_choice_hospital_id:
            choices[weight.first_choice_hospital_id] = 1
        if weight.second_choice_hospital_id:
            choices[weight.second_choice_hospital_id] = 2
        if weight.third_choice_hospital_id:
            choices[weight.third_choice_hospital_id] = 3
        
        return choices
    
    def get_hospital_popularity(
        self, 
        hospital_id: int, 
        fiscal_year: int
    ) -> Dict[str, int]:
        """
        病院の人気度を取得（何人が第何希望に入れたか）
        
        Args:
            hospital_id: 病院ID
            fiscal_year: 年度
        
        Returns:
            Dict[str, int]: {"first": count, "second": count, "third": count}
        """
        weights = self.get_by_fiscal_year(fiscal_year)
        
        popularity = {
            "first": 0,
            "second": 0,
            "third": 0
        }
        
        for weight in weights:
            if weight.first_choice_hospital_id == hospital_id:
                popularity["first"] += 1
            if weight.second_choice_hospital_id == hospital_id:
                popularity["second"] += 1
            if weight.third_choice_hospital_id == hospital_id:
                popularity["third"] += 1
        
        return popularity
    
    def delete_by_fiscal_year(self, fiscal_year: int) -> int:
        """
        年度の全希望登録を削除
        
        Args:
            fiscal_year: 年度
        
        Returns:
            int: 削除件数
        """
        count = self.db.query(StaffWeight).filter(
            StaffWeight.fiscal_year == fiscal_year
        ).delete()
        self.db.commit()
        logger.info(f"Deleted {count} staff weights for fiscal_year={fiscal_year}")
        return count
