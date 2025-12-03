"""
病院希望テーブルモデル
"""
from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import relationship
from database.base import Base, TimestampMixin
from config.constants import TableName


class HospitalChoice(Base, TimestampMixin):
    """
    病院希望

    専攻医の病院希望（第1希望〜第3希望）
    """
    __tablename__ = TableName.HOSPITAL_CHOICE

    # 主キー
    id = Column(Integer, primary_key=True, autoincrement=True, comment="希望ID")

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

    # 年度
    fiscal_year = Column(Integer, nullable=False, comment="年度")

    # 希望順位（1-3）
    rank = Column(
        Integer,
        nullable=False,
        comment="希望順位 (1-3)"
    )

    # リレーションシップ
    staff = relationship("Staff", back_populates="hospital_choices")
    hospital = relationship("Hospital", back_populates="hospital_choices")

    # 制約
    __table_args__ = (
        # 同一専攻医・年度・病院の重複禁止
        UniqueConstraint(
            'staff_id', 'hospital_id', 'fiscal_year',
            name='uq_hospital_choice_staff_hospital_year'
        ),
        # 同一専攻医・年度・順位の重複禁止
        UniqueConstraint(
            'staff_id', 'rank', 'fiscal_year',
            name='uq_hospital_choice_staff_rank_year'
        ),
        # 順位は1-3のみ
        CheckConstraint('rank >= 1 AND rank <= 3', name='ck_hospital_choice_rank'),
    )

    def __repr__(self):
        return f"<HospitalChoice(staff_id={self.staff_id}, hospital_id={self.hospital_id}, rank={self.rank})>"

    def __str__(self):
        return f"第{self.rank}希望: {self.hospital.name if self.hospital else '?'}"

    @property
    def rank_display(self) -> str:
        """希望順位の表示名を取得"""
        rank_names = {1: "第1希望", 2: "第2希望", 3: "第3希望"}
        return rank_names.get(self.rank, f"第{self.rank}希望")
