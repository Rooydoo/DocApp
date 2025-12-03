"""
専攻医要素重みリポジトリ
"""
from typing import List, Optional, Dict
from decimal import Decimal
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from database.models.staff_factor_weight import StaffFactorWeight
from database.models.evaluation_factor import EvaluationFactor
from repositories.base_repository import BaseRepository
from config.constants import FactorType
from utils.exceptions import ValidationException


class StaffFactorWeightRepository(BaseRepository[StaffFactorWeight]):
    """
    専攻医要素重みリポジトリ

    専攻医の要素重みのCRUD操作（合計100の検証含む）
    """

    def __init__(self, db: Session):
        super().__init__(StaffFactorWeight, db)

    def get_by_staff_and_year(
        self, staff_id: int, fiscal_year: int
    ) -> List[StaffFactorWeight]:
        """
        専攻医と年度で取得

        Args:
            staff_id: 職員ID
            fiscal_year: 年度

        Returns:
            List[StaffFactorWeight]: 要素重みリスト
        """
        return (
            self.db.query(self.model)
            .options(joinedload(self.model.factor))
            .filter(
                self.model.staff_id == staff_id,
                self.model.fiscal_year == fiscal_year
            )
            .all()
        )

    def get_by_staff_factor_year(
        self, staff_id: int, factor_id: int, fiscal_year: int
    ) -> Optional[StaffFactorWeight]:
        """
        専攻医・要素・年度で取得

        Args:
            staff_id: 職員ID
            factor_id: 評価要素ID
            fiscal_year: 年度

        Returns:
            StaffFactorWeight: 要素重み、存在しない場合None
        """
        return (
            self.db.query(self.model)
            .filter(
                self.model.staff_id == staff_id,
                self.model.factor_id == factor_id,
                self.model.fiscal_year == fiscal_year
            )
            .first()
        )

    def get_total_weight(self, staff_id: int, fiscal_year: int) -> Decimal:
        """
        重みの合計を取得

        Args:
            staff_id: 職員ID
            fiscal_year: 年度

        Returns:
            Decimal: 重みの合計
        """
        result = (
            self.db.query(func.sum(self.model.weight))
            .filter(
                self.model.staff_id == staff_id,
                self.model.fiscal_year == fiscal_year
            )
            .scalar()
        )
        return result or Decimal("0")

    def validate_total_weight(self, staff_id: int, fiscal_year: int) -> bool:
        """
        重みの合計が100かどうか検証

        Args:
            staff_id: 職員ID
            fiscal_year: 年度

        Returns:
            bool: 合計が100の場合True
        """
        total = self.get_total_weight(staff_id, fiscal_year)
        return total == Decimal("100")

    def bulk_upsert(
        self, staff_id: int, fiscal_year: int, weights: Dict[int, float]
    ) -> List[StaffFactorWeight]:
        """
        一括で登録/更新（合計100の検証付き）

        Args:
            staff_id: 職員ID
            fiscal_year: 年度
            weights: {factor_id: weight} の辞書

        Returns:
            List[StaffFactorWeight]: 登録/更新された要素重みリスト

        Raises:
            ValidationException: 合計が100でない場合
        """
        # 合計が100かチェック
        total = sum(weights.values())
        if abs(total - 100) > 0.01:  # 浮動小数点誤差を考慮
            raise ValidationException(
                f"重みの合計は100である必要があります（現在: {total}）"
            )

        results = []
        for factor_id, weight in weights.items():
            existing = self.get_by_staff_factor_year(staff_id, factor_id, fiscal_year)
            if existing:
                updated = self.update(existing.id, {"weight": weight})
                results.append(updated)
            else:
                created = self.create({
                    "staff_id": staff_id,
                    "factor_id": factor_id,
                    "fiscal_year": fiscal_year,
                    "weight": weight
                })
                results.append(created)

        return results

    def get_weights_as_dict(
        self, staff_id: int, fiscal_year: int
    ) -> Dict[int, float]:
        """
        重みを辞書形式で取得

        Args:
            staff_id: 職員ID
            fiscal_year: 年度

        Returns:
            Dict[int, float]: {factor_id: weight} の辞書
        """
        weights = self.get_by_staff_and_year(staff_id, fiscal_year)
        return {w.factor_id: float(w.weight) for w in weights}

    def delete_by_staff_and_year(self, staff_id: int, fiscal_year: int) -> int:
        """
        専攻医と年度で削除

        Args:
            staff_id: 職員ID
            fiscal_year: 年度

        Returns:
            int: 削除件数
        """
        count = (
            self.db.query(self.model)
            .filter(
                self.model.staff_id == staff_id,
                self.model.fiscal_year == fiscal_year
            )
            .delete()
        )
        self.db.commit()
        return count
