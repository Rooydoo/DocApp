"""
病院希望リポジトリ
"""
from typing import List, Optional, Dict
from sqlalchemy.orm import Session, joinedload
from database.models.hospital_choice import HospitalChoice
from repositories.base_repository import BaseRepository
from utils.exceptions import ValidationException


class HospitalChoiceRepository(BaseRepository[HospitalChoice]):
    """
    病院希望リポジトリ

    病院希望のCRUD操作
    """

    def __init__(self, db: Session):
        super().__init__(HospitalChoice, db)

    def get_by_staff_and_year(
        self, staff_id: int, fiscal_year: int
    ) -> List[HospitalChoice]:
        """
        専攻医と年度で取得（順位順）

        Args:
            staff_id: 職員ID
            fiscal_year: 年度

        Returns:
            List[HospitalChoice]: 病院希望リスト（順位順）
        """
        return (
            self.db.query(self.model)
            .options(joinedload(self.model.hospital))
            .filter(
                self.model.staff_id == staff_id,
                self.model.fiscal_year == fiscal_year
            )
            .order_by(self.model.rank)
            .all()
        )

    def get_by_rank(
        self, staff_id: int, fiscal_year: int, rank: int
    ) -> Optional[HospitalChoice]:
        """
        専攻医・年度・順位で取得

        Args:
            staff_id: 職員ID
            fiscal_year: 年度
            rank: 希望順位（1-3）

        Returns:
            HospitalChoice: 病院希望、存在しない場合None
        """
        return (
            self.db.query(self.model)
            .filter(
                self.model.staff_id == staff_id,
                self.model.fiscal_year == fiscal_year,
                self.model.rank == rank
            )
            .first()
        )

    def get_hope_rank(
        self, staff_id: int, hospital_id: int, fiscal_year: int
    ) -> int:
        """
        指定病院の希望順位を取得

        Args:
            staff_id: 職員ID
            hospital_id: 病院ID
            fiscal_year: 年度

        Returns:
            int: 希望順位（1-3）、希望外の場合0
        """
        choice = (
            self.db.query(self.model)
            .filter(
                self.model.staff_id == staff_id,
                self.model.hospital_id == hospital_id,
                self.model.fiscal_year == fiscal_year
            )
            .first()
        )
        return choice.rank if choice else 0

    def bulk_upsert(
        self, staff_id: int, fiscal_year: int, choices: Dict[int, int]
    ) -> List[HospitalChoice]:
        """
        一括で登録/更新

        Args:
            staff_id: 職員ID
            fiscal_year: 年度
            choices: {rank: hospital_id} の辞書（rank: 1-3）

        Returns:
            List[HospitalChoice]: 登録/更新された病院希望リスト

        Raises:
            ValidationException: 順位が1-3でない場合、または重複がある場合
        """
        # バリデーション
        for rank in choices.keys():
            if rank < 1 or rank > 3:
                raise ValidationException(f"順位は1-3である必要があります（指定: {rank}）")

        # 病院IDの重複チェック
        hospital_ids = list(choices.values())
        if len(hospital_ids) != len(set(hospital_ids)):
            raise ValidationException("同じ病院を複数回選択することはできません")

        # 既存データを削除
        self.delete_by_staff_and_year(staff_id, fiscal_year)

        # 新規作成
        results = []
        for rank, hospital_id in choices.items():
            created = self.create({
                "staff_id": staff_id,
                "hospital_id": hospital_id,
                "fiscal_year": fiscal_year,
                "rank": rank
            })
            results.append(created)

        return results

    def get_choices_as_dict(
        self, staff_id: int, fiscal_year: int
    ) -> Dict[int, int]:
        """
        希望を辞書形式で取得

        Args:
            staff_id: 職員ID
            fiscal_year: 年度

        Returns:
            Dict[int, int]: {rank: hospital_id} の辞書
        """
        choices = self.get_by_staff_and_year(staff_id, fiscal_year)
        return {c.rank: c.hospital_id for c in choices}

    def get_all_by_year(self, fiscal_year: int) -> List[HospitalChoice]:
        """
        年度の全希望を取得

        Args:
            fiscal_year: 年度

        Returns:
            List[HospitalChoice]: 病院希望リスト
        """
        return (
            self.db.query(self.model)
            .options(joinedload(self.model.hospital), joinedload(self.model.staff))
            .filter(self.model.fiscal_year == fiscal_year)
            .order_by(self.model.staff_id, self.model.rank)
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

    def get_hospital_popularity(self, fiscal_year: int) -> Dict[int, Dict[str, int]]:
        """
        病院ごとの希望数を集計

        Args:
            fiscal_year: 年度

        Returns:
            Dict[int, Dict[str, int]]: {hospital_id: {rank1: count, rank2: count, ...}}
        """
        choices = self.get_all_by_year(fiscal_year)
        result: Dict[int, Dict[str, int]] = {}

        for choice in choices:
            if choice.hospital_id not in result:
                result[choice.hospital_id] = {"rank1": 0, "rank2": 0, "rank3": 0, "total": 0}
            result[choice.hospital_id][f"rank{choice.rank}"] += 1
            result[choice.hospital_id]["total"] += 1

        return result
