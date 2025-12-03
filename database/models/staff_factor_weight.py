"""
専攻医の要素重みテーブルモデル
"""
from sqlalchemy import Column, Integer, ForeignKey, DECIMAL, UniqueConstraint
from sqlalchemy.orm import relationship
from database.base import Base, TimestampMixin
from config.constants import TableName


class StaffFactorWeight(Base, TimestampMixin):
    """
    専攻医の要素重み

    各専攻医がどの評価要素をどれだけ重視するか（合計100）
    例: 山田さん → 年収:30, 通勤距離:40, 外勤:20, 症例数:10 = 合計100
    """
    __tablename__ = TableName.STAFF_FACTOR_WEIGHT

    # 主キー
    id = Column(Integer, primary_key=True, autoincrement=True, comment="重みID")

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

    # 重み（0-100、全要素の合計が100になる）
    weight = Column(
        DECIMAL(5, 2),
        nullable=False,
        default=0,
        comment="重み (0-100)"
    )

    # リレーションシップ
    staff = relationship("Staff", back_populates="factor_weights")
    factor = relationship("EvaluationFactor", back_populates="staff_factor_weights")

    # 一意制約（staff_id + factor_id + fiscal_year）
    __table_args__ = (
        UniqueConstraint(
            'staff_id', 'factor_id', 'fiscal_year',
            name='uq_staff_factor_weight_staff_factor_year'
        ),
    )

    def __repr__(self):
        return f"<StaffFactorWeight(staff_id={self.staff_id}, factor_id={self.factor_id}, weight={self.weight})>"

    def __str__(self):
        return f"{self.factor.name if self.factor else '?'}: {self.weight}"

    @property
    def weight_float(self) -> float:
        """重みをfloatで取得"""
        return float(self.weight) if self.weight else 0.0

    @property
    def weight_normalized(self) -> float:
        """重みを0-1に正規化して取得"""
        return self.weight_float / 100.0
