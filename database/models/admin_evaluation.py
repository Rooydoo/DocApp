"""
医局側評価テーブルモデル
"""
from sqlalchemy import Column, Integer, ForeignKey, DECIMAL, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from database.base import Base, TimestampMixin
from config.constants import TableName


class AdminEvaluation(Base, TimestampMixin):
    """
    医局側評価

    医局側が各専攻医に対して付ける評価値
    例: 山田さん → 学術実績:0.8, 人柄:0.9
    """
    __tablename__ = TableName.ADMIN_EVALUATION

    # 主キー
    id = Column(Integer, primary_key=True, autoincrement=True, comment="評価ID")

    # 外部キー
    staff_id = Column(
        Integer,
        ForeignKey(f"{TableName.STAFF}.id", ondelete="CASCADE"),
        nullable=False,
        comment="職員ID"
    )
    factor_id = Column(
        Integer,
        ForeignKey(f"{TableName.EVALUATION_FACTOR}.id", ondelete="CASCADE"),
        nullable=False,
        comment="評価要素ID"
    )

    # 年度
    fiscal_year = Column(Integer, nullable=False, comment="年度")

    # 評価値（0.0-1.0）
    value = Column(
        DECIMAL(3, 2),
        nullable=False,
        default=0.5,
        comment="評価値 (0.0-1.0)"
    )

    # 備考
    notes = Column(Text, comment="備考")

    # リレーションシップ
    staff = relationship("Staff", back_populates="admin_evaluations")
    factor = relationship("EvaluationFactor", back_populates="admin_evaluations")

    # 一意制約（staff_id + factor_id + fiscal_year）
    __table_args__ = (
        UniqueConstraint(
            'staff_id', 'factor_id', 'fiscal_year',
            name='uq_admin_evaluation_staff_factor_year'
        ),
    )

    def __repr__(self):
        return f"<AdminEvaluation(staff_id={self.staff_id}, factor_id={self.factor_id}, value={self.value})>"

    def __str__(self):
        return f"{self.factor.name if self.factor else '?'}: {self.value}"

    @property
    def value_float(self) -> float:
        """評価値をfloatで取得"""
        return float(self.value) if self.value else 0.0
