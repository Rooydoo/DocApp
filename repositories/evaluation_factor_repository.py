"""
評価要素リポジトリ
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from database.models.evaluation_factor import EvaluationFactor
from repositories.base_repository import BaseRepository
from config.constants import FactorType


class EvaluationFactorRepository(BaseRepository[EvaluationFactor]):
    """
    評価要素リポジトリ

    評価要素マスタのCRUD操作
    """

    def __init__(self, db: Session):
        super().__init__(EvaluationFactor, db)

    def get_by_name(self, name: str) -> Optional[EvaluationFactor]:
        """
        要素名で取得

        Args:
            name: 要素名

        Returns:
            EvaluationFactor: 評価要素、存在しない場合None
        """
        return self.db.query(self.model).filter(self.model.name == name).first()

    def get_active_factors(self) -> List[EvaluationFactor]:
        """
        有効な評価要素を全て取得

        Returns:
            List[EvaluationFactor]: 有効な評価要素リスト（表示順序順）
        """
        return (
            self.db.query(self.model)
            .filter(self.model.is_active == True)
            .order_by(self.model.display_order)
            .all()
        )

    def get_by_type(self, factor_type: str) -> List[EvaluationFactor]:
        """
        タイプ別に取得

        Args:
            factor_type: 要素タイプ (staff_preference/admin_evaluation)

        Returns:
            List[EvaluationFactor]: 評価要素リスト（表示順序順）
        """
        return (
            self.db.query(self.model)
            .filter(
                self.model.factor_type == factor_type,
                self.model.is_active == True
            )
            .order_by(self.model.display_order)
            .all()
        )

    def get_staff_preference_factors(self) -> List[EvaluationFactor]:
        """
        専攻医重視要素を取得

        Returns:
            List[EvaluationFactor]: 専攻医重視要素リスト
        """
        return self.get_by_type(FactorType.STAFF_PREFERENCE)

    def get_admin_evaluation_factors(self) -> List[EvaluationFactor]:
        """
        医局側評価要素を取得

        Returns:
            List[EvaluationFactor]: 医局側評価要素リスト
        """
        return self.get_by_type(FactorType.ADMIN_EVALUATION)

    def update_display_order(self, factor_id: int, new_order: int) -> EvaluationFactor:
        """
        表示順序を更新

        Args:
            factor_id: 評価要素ID
            new_order: 新しい表示順序

        Returns:
            EvaluationFactor: 更新された評価要素
        """
        return self.update(factor_id, {"display_order": new_order})

    def toggle_active(self, factor_id: int) -> EvaluationFactor:
        """
        有効/無効を切り替え

        Args:
            factor_id: 評価要素ID

        Returns:
            EvaluationFactor: 更新された評価要素
        """
        factor = self.get_or_raise(factor_id)
        return self.update(factor_id, {"is_active": not factor.is_active})
