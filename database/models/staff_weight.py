"""
職員希望登録テーブルモデル
"""
from sqlalchemy import Column, Integer, ForeignKey, DECIMAL, UniqueConstraint
from sqlalchemy.orm import relationship
from database.base import Base, TimestampMixin
from config.constants import TableName


class StaffWeight(Base, TimestampMixin):
    """
    職員希望登録
    
    選考医の病院配置希望と重みを管理
    Googleフォームの回答から自動生成
    """
    __tablename__ = TableName.STAFF_WEIGHT
    
    # 主キー
    id = Column(Integer, primary_key=True, autoincrement=True, comment="希望ID")
    
    # 外部キー
    staff_id = Column(
        Integer,
        ForeignKey(f"{TableName.STAFF}.id", ondelete="CASCADE"),
        nullable=False,
        comment="職員ID"
    )
    
    # 年度
    fiscal_year = Column(Integer, nullable=False, comment="年度")
    
    # 希望病院（第1〜第3希望）
    first_choice_hospital_id = Column(
        Integer,
        ForeignKey(f"{TableName.HOSPITAL}.id", ondelete="SET NULL"),
        comment="第1希望病院ID"
    )
    second_choice_hospital_id = Column(
        Integer,
        ForeignKey(f"{TableName.HOSPITAL}.id", ondelete="SET NULL"),
        comment="第2希望病院ID"
    )
    third_choice_hospital_id = Column(
        Integer,
        ForeignKey(f"{TableName.HOSPITAL}.id", ondelete="SET NULL"),
        comment="第3希望病院ID"
    )
    
    # 重み（GA用の評価値）
    first_choice_weight = Column(DECIMAL(5, 2), default=3.0, comment="第1希望重み")
    second_choice_weight = Column(DECIMAL(5, 2), default=2.0, comment="第2希望重み")
    third_choice_weight = Column(DECIMAL(5, 2), default=1.0, comment="第3希望重み")
    
    # リレーションシップ
    staff = relationship("Staff", back_populates="staff_weights")
    
    first_choice_hospital = relationship(
        "Hospital",
        foreign_keys=[first_choice_hospital_id],
        back_populates="staff_weights_first"
    )
    second_choice_hospital = relationship(
        "Hospital",
        foreign_keys=[second_choice_hospital_id],
        back_populates="staff_weights_second"
    )
    third_choice_hospital = relationship(
        "Hospital",
        foreign_keys=[third_choice_hospital_id],
        back_populates="staff_weights_third"
    )
    
    # 一意制約（staff_id + fiscal_year）
    __table_args__ = (
        UniqueConstraint('staff_id', 'fiscal_year', name='uq_staff_weight_staff_year'),
    )
    
    def __repr__(self):
        return f"<StaffWeight(staff_id={self.staff_id}, year={self.fiscal_year})>"
    
    def __str__(self):
        return f"{self.fiscal_year}年度希望"
    
    def get_hope_rank(self, hospital_id: int) -> int:
        """
        指定病院の希望順位を取得
        
        Args:
            hospital_id: 病院ID
        
        Returns:
            int: 希望順位(1-3)、希望外の場合0
        """
        if self.first_choice_hospital_id == hospital_id:
            return 1
        elif self.second_choice_hospital_id == hospital_id:
            return 2
        elif self.third_choice_hospital_id == hospital_id:
            return 3
        return 0
    
    def get_weight_for_hospital(self, hospital_id: int) -> float:
        """
        指定病院の重みを取得
        
        Args:
            hospital_id: 病院ID
        
        Returns:
            float: 重み値、希望外の場合0.0
        """
        rank = self.get_hope_rank(hospital_id)
        if rank == 1:
            return float(self.first_choice_weight)
        elif rank == 2:
            return float(self.second_choice_weight)
        elif rank == 3:
            return float(self.third_choice_weight)
        return 0.0
    
    @property
    def all_choices(self) -> list[int]:
        """
        全ての希望病院IDのリストを取得
        
        Returns:
            list[int]: 希望病院IDのリスト
        """
        choices = []
        if self.first_choice_hospital_id:
            choices.append(self.first_choice_hospital_id)
        if self.second_choice_hospital_id:
            choices.append(self.second_choice_hospital_id)
        if self.third_choice_hospital_id:
            choices.append(self.third_choice_hospital_id)
        return choices
