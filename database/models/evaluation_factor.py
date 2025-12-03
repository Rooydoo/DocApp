"""
評価要素マスタテーブルモデル
"""
from sqlalchemy import Column, Integer, String, Boolean, Text
from sqlalchemy.orm import relationship
from database.base import Base, TimestampMixin
from config.constants import TableName, FactorType


class EvaluationFactor(Base, TimestampMixin):
    """
    評価要素マスタ

    GAのフィットネス計算に使用する評価要素を管理
    - 専攻医重視要素: 年収、通勤距離、外勤の多さ、症例数など
    - 医局側評価要素: 学術実績、人柄など
    """
    __tablename__ = TableName.EVALUATION_FACTOR

    # 主キー
    id = Column(Integer, primary_key=True, autoincrement=True, comment="評価要素ID")

    # 基本情報
    name = Column(String(100), nullable=False, unique=True, comment="要素名")
    description = Column(Text, comment="説明")

    # 要素タイプ
    factor_type = Column(
        String(30),
        nullable=False,
        comment="要素タイプ (staff_preference/admin_evaluation)"
    )

    # 表示順序
    display_order = Column(Integer, default=0, comment="表示順序")

    # 有効フラグ
    is_active = Column(Boolean, default=True, comment="有効フラグ")

    # リレーションシップ
    staff_factor_weights = relationship(
        "StaffFactorWeight",
        back_populates="factor",
        cascade="all, delete-orphan"
    )

    admin_evaluations = relationship(
        "AdminEvaluation",
        back_populates="factor",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<EvaluationFactor(id={self.id}, name='{self.name}', type='{self.factor_type}')>"

    def __str__(self):
        return self.name

    @property
    def is_staff_preference(self) -> bool:
        """専攻医重視要素かどうか"""
        return self.factor_type == FactorType.STAFF_PREFERENCE

    @property
    def is_admin_evaluation(self) -> bool:
        """医局側評価要素かどうか"""
        return self.factor_type == FactorType.ADMIN_EVALUATION

    @property
    def type_display_name(self) -> str:
        """タイプの表示名を取得"""
        return FactorType.display_name(self.factor_type)
