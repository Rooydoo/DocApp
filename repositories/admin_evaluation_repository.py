"""
医局側評価リポジトリ
"""
from typing import List, Optional, Dict
from sqlalchemy.orm import Session, joinedload
from database.models.admin_evaluation import AdminEvaluation
from repositories.base_repository import BaseRepository


class AdminEvaluationRepository(BaseRepository[AdminEvaluation]):
    """
    医局側評価リポジトリ

    医局側評価のCRUD操作
    """

    def __init__(self, db: Session):
        super().__init__(AdminEvaluation, db)

    def get_by_staff_and_year(
        self, staff_id: int, fiscal_year: int
    ) -> List[AdminEvaluation]:
        """
        専攻医と年度で取得

        Args:
            staff_id: 職員ID
            fiscal_year: 年度

        Returns:
            List[AdminEvaluation]: 評価リスト
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
    ) -> Optional[AdminEvaluation]:
        """
        専攻医・要素・年度で取得

        Args:
            staff_id: 職員ID
            factor_id: 評価要素ID
            fiscal_year: 年度

        Returns:
            AdminEvaluation: 評価、存在しない場合None
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

    def bulk_upsert(
        self, staff_id: int, fiscal_year: int, evaluations: Dict[int, float],
        notes: Optional[Dict[int, str]] = None
    ) -> List[AdminEvaluation]:
        """
        一括で登録/更新

        Args:
            staff_id: 職員ID
            fiscal_year: 年度
            evaluations: {factor_id: value} の辞書（0.0-1.0）
            notes: {factor_id: notes} の辞書（オプション）

        Returns:
            List[AdminEvaluation]: 登録/更新された評価リスト
        """
        notes = notes or {}
        results = []

        for factor_id, value in evaluations.items():
            # 値を0.0-1.0の範囲に制限
            value = max(0.0, min(1.0, value))

            existing = self.get_by_staff_factor_year(staff_id, factor_id, fiscal_year)
            data = {
                "value": value,
                "notes": notes.get(factor_id)
            }

            if existing:
                updated = self.update(existing.id, data)
                results.append(updated)
            else:
                data.update({
                    "staff_id": staff_id,
                    "factor_id": factor_id,
                    "fiscal_year": fiscal_year
                })
                created = self.create(data)
                results.append(created)

        return results

    def get_evaluations_as_dict(
        self, staff_id: int, fiscal_year: int
    ) -> Dict[int, float]:
        """
        評価を辞書形式で取得

        Args:
            staff_id: 職員ID
            fiscal_year: 年度

        Returns:
            Dict[int, float]: {factor_id: value} の辞書
        """
        evaluations = self.get_by_staff_and_year(staff_id, fiscal_year)
        return {e.factor_id: float(e.value) for e in evaluations}

    def get_all_by_year(self, fiscal_year: int) -> List[AdminEvaluation]:
        """
        年度の全評価を取得

        Args:
            fiscal_year: 年度

        Returns:
            List[AdminEvaluation]: 評価リスト
        """
        return (
            self.db.query(self.model)
            .options(joinedload(self.model.factor), joinedload(self.model.staff))
            .filter(self.model.fiscal_year == fiscal_year)
            .all()
        )

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
