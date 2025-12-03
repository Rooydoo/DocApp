"""
職員テーブルモデル
"""
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from database.base import Base, TimestampMixin
from config.constants import TableName, StaffType


class Staff(Base, TimestampMixin):
    """
    職員マスタ
    
    医局に所属する全職員の情報を管理
    """
    __tablename__ = TableName.STAFF
    
    # 主キー
    id = Column(Integer, primary_key=True, autoincrement=True, comment="職員ID")
    
    # 基本情報
    name = Column(String(100), nullable=False, comment="氏名")
    email = Column(String(100), nullable=False, unique=True, comment="メールアドレス")
    phone = Column(String(20), comment="電話番号")
    
    # 職員種別
    staff_type = Column(String(20), nullable=False, comment="職員種別")
    
    # 住所情報（選考医の場合必須）
    address = Column(String(200), comment="住所")
    
    # 選考医専用フィールド
    rotation_months = Column(Integer, comment="希望ローテーション期間(月)")
    
    # 備考
    notes = Column(Text, comment="備考")
    
    # リレーションシップ
    assignments = relationship(
        "Assignment",
        back_populates="staff",
        cascade="all, delete-orphan"
    )
    
    commute_caches = relationship(
        "CommuteCache",
        back_populates="staff",
        cascade="all, delete-orphan"
    )
    
    staff_weights = relationship(
        "StaffWeight",
        back_populates="staff",
        cascade="all, delete-orphan"
    )
    
    outpatient_assignments = relationship(
        "OutpatientAssignment",
        back_populates="staff",
        cascade="all, delete-orphan"
    )

    # GA用評価関連
    factor_weights = relationship(
        "StaffFactorWeight",
        back_populates="staff",
        cascade="all, delete-orphan"
    )

    admin_evaluations = relationship(
        "AdminEvaluation",
        back_populates="staff",
        cascade="all, delete-orphan"
    )

    hospital_choices = relationship(
        "HospitalChoice",
        back_populates="staff",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Staff(id={self.id}, name='{self.name}', type='{self.staff_type}')>"
    
    def __str__(self):
        return f"{self.name} ({self.staff_type})"
    
    @property
    def is_resident_doctor(self) -> bool:
        """
        選考医かどうか
        
        Returns:
            bool: 選考医の場合True
        """
        return self.staff_type == StaffType.RESIDENT_DOCTOR
    
    @property
    def full_name_with_type(self) -> str:
        """
        職員種別付きの氏名
        
        Returns:
            str: "氏名 (職員種別)"
        """
        return f"{self.name} ({self.staff_type})"
