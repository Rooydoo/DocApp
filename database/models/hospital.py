"""
病院テーブルモデル
"""
from sqlalchemy import Column, Integer, String, Boolean, DECIMAL, DateTime, Text
from sqlalchemy.orm import relationship
from database.base import Base, TimestampMixin
from config.constants import TableName


class Hospital(Base, TimestampMixin):
    """
    病院マスタ
    
    選考医が配置される病院の情報を管理
    """
    __tablename__ = TableName.HOSPITAL
    
    # 主キー
    id = Column(Integer, primary_key=True, autoincrement=True, comment="病院ID")
    
    # 基本情報
    name = Column(String(100), nullable=False, unique=True, comment="病院名")
    director_name = Column(String(100), comment="院長名")
    address = Column(String(200), nullable=False, comment="住所")
    
    # 受入情報（3種類に分割）
    resident_capacity = Column(Integer, nullable=False, default=0, comment="専攻医受入人数")
    specialist_capacity = Column(Integer, nullable=False, default=0, comment="専門医受入人数")
    instructor_capacity = Column(Integer, nullable=False, default=0, comment="指導医受入人数")
    
    rotation_months = Column(Integer, comment="ローテーション期間(月)")
    annual_salary = Column(DECIMAL(10, 2), comment="年収")
    
    # フラグ
    outpatient_flag = Column(Boolean, default=False, comment="外勤対象フラグ")
    
    # 備考
    notes = Column(Text, comment="備考")
    
    # リレーションシップ
    assignments = relationship(
        "Assignment",
        back_populates="hospital",
        cascade="all, delete-orphan"
    )
    
    commute_caches = relationship(
        "CommuteCache",
        back_populates="hospital",
        cascade="all, delete-orphan"
    )
    
    outpatient_slots = relationship(
        "OutpatientSlot",
        back_populates="hospital",
        cascade="all, delete-orphan"
    )
    
    staff_weights_first = relationship(
        "StaffWeight",
        foreign_keys="[StaffWeight.first_choice_hospital_id]",
        back_populates="first_choice_hospital"
    )
    
    staff_weights_second = relationship(
        "StaffWeight",
        foreign_keys="[StaffWeight.second_choice_hospital_id]",
        back_populates="second_choice_hospital"
    )
    
    staff_weights_third = relationship(
        "StaffWeight",
        foreign_keys="[StaffWeight.third_choice_hospital_id]",
        back_populates="third_choice_hospital"
    )
    
    def __repr__(self):
        return f"<Hospital(id={self.id}, name='{self.name}', capacity=({self.resident_capacity},{self.specialist_capacity},{self.instructor_capacity}))>"
    
    def __str__(self):
        return self.name
    
    @property
    def total_capacity(self) -> int:
        """
        総受入人数
        
        Returns:
            int: 3種類の受入人数の合計
        """
        return self.resident_capacity + self.specialist_capacity + self.instructor_capacity
    
    @property
    def is_full(self) -> bool:
        """
        受入人数が上限に達しているか
        
        Returns:
            bool: 上限に達している場合True
        """
        # 現在の配置数を取得（実装時にカウント）
        # current_assignments = len([a for a in self.assignments if a.fiscal_year == current_year])
        # return current_assignments >= self.total_capacity
        return False  # 仮実装
    
    @property
    def available_capacity(self) -> int:
        """
        利用可能な受入人数
        
        Returns:
            int: 残り受入可能人数
        """
        # 実装時に現在の配置数を計算
        return self.total_capacity