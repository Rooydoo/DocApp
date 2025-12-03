"""
通勤時間キャッシュテーブルモデル
"""
from sqlalchemy import Column, Integer, ForeignKey, DECIMAL, UniqueConstraint
from sqlalchemy.orm import relationship
from database.base import Base, TimestampMixin
from config.constants import TableName


class CommuteCache(Base, TimestampMixin):
    """
    通勤時間キャッシュ
    
    Google Maps APIで取得した通勤時間・距離をキャッシュ
    選考医と病院の組み合わせごとに保存
    """
    __tablename__ = TableName.COMMUTE_CACHE
    
    # 主キー
    id = Column(Integer, primary_key=True, autoincrement=True, comment="キャッシュID")
    
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
    
    # 通勤情報
    driving_time_minutes = Column(Integer, nullable=False, comment="車での通勤時間(分)")
    driving_distance_km = Column(DECIMAL(10, 2), nullable=False, comment="車での通勤距離(km)")
    
    # リレーションシップ
    staff = relationship("Staff", back_populates="commute_caches")
    hospital = relationship("Hospital", back_populates="commute_caches")
    
    # 一意制約（staff_id + hospital_id）
    __table_args__ = (
        UniqueConstraint('staff_id', 'hospital_id', name='uq_commute_cache_staff_hospital'),
    )
    
    def __repr__(self):
        return f"<CommuteCache(staff_id={self.staff_id}, hospital_id={self.hospital_id}, time={self.driving_time_minutes}min)>"
    
    def __str__(self):
        return f"{self.driving_time_minutes}分 / {self.driving_distance_km}km"
    
    @property
    def is_long_commute(self) -> bool:
        """
        長距離通勤かどうか（60分以上）
        
        Returns:
            bool: 長距離通勤の場合True
        """
        return self.driving_time_minutes >= 60
    
    @property
    def commute_info(self) -> dict:
        """
        通勤情報を辞書形式で取得
        
        Returns:
            dict: 通勤時間・距離の情報
        """
        return {
            "time_minutes": self.driving_time_minutes,
            "distance_km": float(self.driving_distance_km),
            "is_long_commute": self.is_long_commute
        }
