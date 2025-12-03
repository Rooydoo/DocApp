"""
配置テーブルモデル
"""
from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey, DECIMAL, Text
from sqlalchemy.orm import relationship
from database.base import Base, TimestampMixin
from config.constants import TableName, AssignmentStatus


class Assignment(Base, TimestampMixin):
    """
    選考医配置履歴
    
    選考医の病院配置結果を管理
    """
    __tablename__ = TableName.ASSIGNMENT
    
    # 主キー
    id = Column(Integer, primary_key=True, autoincrement=True, comment="配置ID")
    
    # 外部キー
    staff_id = Column(
        Integer,
        ForeignKey(f"{TableName.STAFF}.id", ondelete="CASCADE"),
        nullable=False,
        comment="職員ID"
    )
    hospital_id = Column(
        Integer,
        ForeignKey(f"{TableName.HOSPITAL}.id", ondelete="CASCADE"),
        nullable=False,
        comment="病院ID"
    )
    
    # 配置情報
    fiscal_year = Column(Integer, nullable=False, comment="年度")
    start_date = Column(Date, nullable=False, comment="開始日")
    end_date = Column(Date, nullable=False, comment="終了日")
    
    # マッチング情報
    mismatch_flag = Column(Boolean, default=False, comment="アンマッチフラグ")
    mismatch_reason = Column(String(100), comment="アンマッチ理由")
    
    # GA結果情報
    fitness_score = Column(DECIMAL(10, 4), comment="適合度スコア")
    hope_rank = Column(Integer, comment="希望順位(1-3, null=希望外)")
    
    # 通勤情報（キャッシュから取得した値）
    commute_time = Column(Integer, comment="通勤時間(分)")
    commute_distance = Column(DECIMAL(10, 2), comment="通勤距離(km)")
    
    # 年収情報
    salary = Column(DECIMAL(10, 2), comment="年収")
    
    # 備考
    notes = Column(Text, comment="備考")
    
    # リレーションシップ
    staff = relationship("Staff", back_populates="assignments")
    hospital = relationship("Hospital", back_populates="assignments")
    
    def __repr__(self):
        return f"<Assignment(id={self.id}, staff_id={self.staff_id}, hospital_id={self.hospital_id}, year={self.fiscal_year})>"
    
    def __str__(self):
        status = "アンマッチ" if self.mismatch_flag else "マッチ"
        return f"{self.fiscal_year}年度 {status}"
    
    @property
    def is_matched(self) -> bool:
        """
        マッチしているか
        
        Returns:
            bool: マッチしている場合True
        """
        return not self.mismatch_flag
    
    @property
    def status(self) -> str:
        """
        配置ステータス
        
        Returns:
            str: ステータス文字列
        """
        if self.mismatch_flag:
            return AssignmentStatus.MISMATCHED
        return AssignmentStatus.MATCHED
    
    @property
    def duration_months(self) -> int:
        """
        配置期間（月数）
        
        Returns:
            int: 月数
        """
        if not self.start_date or not self.end_date:
            return 0
        
        months = (self.end_date.year - self.start_date.year) * 12
        months += self.end_date.month - self.start_date.month
        return months
