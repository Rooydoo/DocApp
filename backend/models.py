"""SQLAlchemyモデル定義"""
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base


class Staff(Base):
    """職員マスタ"""
    __tablename__ = "staff"

    id = Column(Integer, primary_key=True, index=True)
    last_name = Column(String(50), nullable=False)  # 姓
    first_name = Column(String(50), nullable=False)  # 名
    last_name_kana = Column(String(50))  # 姓（かな）
    first_name_kana = Column(String(50))  # 名（かな）
    position = Column(String(20), nullable=False)  # 職種
    email = Column(String(100))
    phone = Column(String(20))
    join_year = Column(Integer)  # 入局年
    address = Column(String(200))
    evaluation_memo = Column(Text)  # 評価メモ

    # リレーション
    careers = relationship("Career", back_populates="staff")
    external_works = relationship("ExternalWork", back_populates="staff")

    @property
    def display_name(self):
        """表示名: 山田（太）"""
        return f"{self.last_name}（{self.first_name[0]}）"


class Hospital(Base):
    """病院マスタ（勤務先）"""
    __tablename__ = "hospitals"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    address = Column(String(200))
    capacity = Column(Integer, default=0)  # 受入可能人数
    allows_external = Column(Boolean, default=True)  # 外勤可否

    # リレーション
    careers = relationship("Career", back_populates="hospital")


class ExternalHospital(Base):
    """外勤病院マスタ"""
    __tablename__ = "external_hospitals"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    address = Column(String(200))

    # リレーション
    external_works = relationship("ExternalWork", back_populates="external_hospital")


class Career(Base):
    """経歴（配置履歴）"""
    __tablename__ = "careers"

    id = Column(Integer, primary_key=True, index=True)
    staff_id = Column(Integer, ForeignKey("staff.id"), nullable=False)
    period = Column(String(20), nullable=False)  # "2024Q1" など
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=True)  # 入局前はNULL
    hospital_name_manual = Column(String(100))  # 入局前用の自由入力
    notes = Column(Text)

    # リレーション
    staff = relationship("Staff", back_populates="careers")
    hospital = relationship("Hospital", back_populates="careers")

    @property
    def hospital_display(self):
        """配置先表示"""
        if self.hospital:
            return self.hospital.name
        return self.hospital_name_manual or ""


class ExternalWork(Base):
    """外勤登録"""
    __tablename__ = "external_works"

    id = Column(Integer, primary_key=True, index=True)
    staff_id = Column(Integer, ForeignKey("staff.id"), nullable=False)
    external_hospital_id = Column(Integer, ForeignKey("external_hospitals.id"), nullable=False)
    day_of_week = Column(String(10), nullable=False)  # 月/火/水/木/金
    time_slot = Column(String(10), nullable=False)  # 午前/午後
    frequency = Column(String(20), nullable=False)  # 毎週/第1週/第2週/第3週/第4週/第1,3週/第2,4週
    period = Column(String(20), nullable=False)  # "2024Q1" など

    # リレーション
    staff = relationship("Staff", back_populates="external_works")
    external_hospital = relationship("ExternalHospital", back_populates="external_works")
