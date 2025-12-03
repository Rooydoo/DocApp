"""
外勤枠テーブルモデル
"""
from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from database.base import Base, TimestampMixin
from config.constants import TableName


class OutpatientSlot(Base, TimestampMixin):
    """
    外勤枠
    
    病院ごとの外勤スケジュール枠を管理
    """
    __tablename__ = TableName.OUTPATIENT_SLOT
    
    # 主キー
    id = Column(Integer, primary_key=True, autoincrement=True, comment="外勤枠ID")
    
    # 外部キー
    hospital_id = Column(
        Integer,
        ForeignKey(f"{TableName.HOSPITAL}.id", ondelete="CASCADE"),
        nullable=False,
        comment="病院ID"
    )
    
    # スケジュール情報
    weekday = Column(String(10), nullable=False, comment="曜日")
    time_slot = Column(String(10), nullable=False, comment="時間帯")
    
    # 備考
    notes = Column(Text, comment="備考")
    
    # リレーションシップ
    hospital = relationship("Hospital", back_populates="outpatient_slots")
    
    outpatient_assignments = relationship(
        "OutpatientAssignment",
        back_populates="slot",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<OutpatientSlot(id={self.id}, hospital_id={self.hospital_id}, weekday='{self.weekday}', time='{self.time_slot}')>"
    
    def __str__(self):
        return f"{self.weekday}{self.time_slot}"
    
    @property
    def schedule_label(self) -> str:
        """
        スケジュールラベル
        
        Returns:
            str: "曜日 時間帯"
        """
        return f"{self.weekday} {self.time_slot}"
