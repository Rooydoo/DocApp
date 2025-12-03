"""
外勤割り当てテーブルモデル
"""
from sqlalchemy import Column, Integer, Date, ForeignKey, Text
from sqlalchemy.orm import relationship
from database.base import Base, TimestampMixin
from config.constants import TableName


class OutpatientAssignment(Base, TimestampMixin):
    """
    外勤割り当て
    
    外勤枠への職員割り当てを管理
    """
    __tablename__ = TableName.OUTPATIENT_ASSIGNMENT
    
    # 主キー
    id = Column(Integer, primary_key=True, autoincrement=True, comment="割り当てID")
    
    # 外部キー
    slot_id = Column(
        Integer,
        ForeignKey(f"{TableName.OUTPATIENT_SLOT}.id", ondelete="CASCADE"),
        nullable=False,
        comment="外勤枠ID"
    )
    staff_id = Column(
        Integer,
        ForeignKey(f"{TableName.STAFF}.id", ondelete="CASCADE"),
        nullable=False,
        comment="職員ID"
    )
    
    # 割り当て期間
    start_date = Column(Date, nullable=False, comment="開始日")
    end_date = Column(Date, nullable=False, comment="終了日")
    
    # 備考
    notes = Column(Text, comment="備考")
    
    # リレーションシップ
    slot = relationship("OutpatientSlot", back_populates="outpatient_assignments")
    staff = relationship("Staff", back_populates="outpatient_assignments")
    
    def __repr__(self):
        return f"<OutpatientAssignment(id={self.id}, slot_id={self.slot_id}, staff_id={self.staff_id})>"
    
    def __str__(self):
        return f"{self.start_date} 〜 {self.end_date}"
    
    @property
    def duration_days(self) -> int:
        """
        割り当て期間（日数）
        
        Returns:
            int: 日数
        """
        if not self.start_date or not self.end_date:
            return 0
        return (self.end_date - self.start_date).days
