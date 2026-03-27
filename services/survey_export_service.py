"""
質問回答データの集計・エクスポートサービス
病院希望、要素重み、医局側評価のデータを集計してスプレッドシートに出力
"""
from typing import Dict, List, Any, Optional
from database.connection import get_db_session
from repositories.staff_repository import StaffRepository
from repositories.hospital_repository import HospitalRepository
from repositories.hospital_choice_repository import HospitalChoiceRepository
from repositories.staff_factor_weight_repository import StaffFactorWeightRepository
from repositories.admin_evaluation_repository import AdminEvaluationRepository
from repositories.evaluation_factor_repository import EvaluationFactorRepository
from config.constants import StaffType
from services.config_service import config_service
from services.google_sheets_service import google_sheets_service
from utils.logger import get_logger

logger = get_logger(__name__)


class SurveyExportService:
    """
    質問回答データの集計・エクスポートサービス

    責務:
    - 病院希望・要素重み・医局側評価の集計データ取得
    - Googleスプレッドシートへのエクスポート
    """

    def get_hospital_choices_summary(self, fiscal_year: int) -> Dict[str, Any]:
        """
        病院希望の集計データを取得

        Returns:
            {
                "headers": [...],
                "rows": [[...], ...],
                "stats": {
                    "total_staff": int,
                    "staff_with_choices": int,
                    "popularity": {hospital_name: count}
                }
            }
        """
        with get_db_session() as db:
            staff_repo = StaffRepository(db)
            hospital_repo = HospitalRepository(db)
            choice_repo = HospitalChoiceRepository(db)

            residents = staff_repo.get_resident_doctors()
            hospitals = hospital_repo.get_all()
            hospital_map = {h.id: h.name for h in hospitals}

            headers = ["職員名", "第1希望", "第2希望", "第3希望"]
            rows = []
            staff_with_choices = 0
            popularity: Dict[str, int] = {}

            for staff in residents:
                choices = choice_repo.get_choices_as_dict(staff.id, fiscal_year)
                if choices:
                    staff_with_choices += 1

                row = [staff.name]
                for rank in [1, 2, 3]:
                    hospital_id = choices.get(rank)
                    if hospital_id:
                        name = hospital_map.get(hospital_id, "不明")
                        row.append(name)
                        popularity[name] = popularity.get(name, 0) + 1
                    else:
                        row.append("")
                rows.append(row)

            return {
                "headers": headers,
                "rows": rows,
                "stats": {
                    "total_staff": len(residents),
                    "staff_with_choices": staff_with_choices,
                    "popularity": dict(sorted(
                        popularity.items(), key=lambda x: x[1], reverse=True
                    ))
                }
            }

    def get_factor_weights_summary(self, fiscal_year: int) -> Dict[str, Any]:
        """
        要素重みの集計データを取得

        Returns:
            {
                "headers": [...],
                "rows": [[...], ...],
                "stats": {
                    "factor_averages": {factor_name: avg_weight}
                }
            }
        """
        with get_db_session() as db:
            staff_repo = StaffRepository(db)
            factor_repo = EvaluationFactorRepository(db)
            weight_repo = StaffFactorWeightRepository(db)

            residents = staff_repo.get_resident_doctors()
            factors = factor_repo.get_staff_preference_factors()

            headers = ["職員名"] + [f.name for f in factors] + ["合計"]
            rows = []
            factor_totals: Dict[str, float] = {f.name: 0.0 for f in factors}
            count_with_weights = 0

            for staff in residents:
                weights = weight_repo.get_weights_as_dict(staff.id, fiscal_year)
                if not weights:
                    row = [staff.name] + ["" for _ in factors] + [""]
                    rows.append(row)
                    continue

                count_with_weights += 1
                row = [staff.name]
                total = 0.0
                for factor in factors:
                    w = weights.get(factor.id, 0)
                    val = float(w)
                    row.append(str(int(val)) if val else "")
                    factor_totals[factor.name] += val
                    total += val
                row.append(str(int(total)))
                rows.append(row)

            # 平均値を計算
            factor_averages = {}
            if count_with_weights > 0:
                for name, total in factor_totals.items():
                    factor_averages[name] = round(total / count_with_weights, 1)

            return {
                "headers": headers,
                "rows": rows,
                "stats": {
                    "factor_averages": factor_averages,
                    "count_with_weights": count_with_weights
                }
            }

    def get_admin_evaluations_summary(self, fiscal_year: int) -> Dict[str, Any]:
        """
        医局側評価の集計データを取得

        Returns:
            {
                "headers": [...],
                "rows": [[...], ...],
                "stats": {
                    "factor_averages": {factor_name: avg_value}
                }
            }
        """
        with get_db_session() as db:
            staff_repo = StaffRepository(db)
            factor_repo = EvaluationFactorRepository(db)
            eval_repo = AdminEvaluationRepository(db)

            residents = staff_repo.get_resident_doctors()
            factors = factor_repo.get_admin_evaluation_factors()

            headers = ["職員名"] + [f.name for f in factors] + ["平均"]
            rows = []
            factor_totals: Dict[str, float] = {f.name: 0.0 for f in factors}
            count_with_evals = 0

            for staff in residents:
                evals = eval_repo.get_evaluations_as_dict(staff.id, fiscal_year)
                if not evals:
                    row = [staff.name] + ["" for _ in factors] + [""]
                    rows.append(row)
                    continue

                count_with_evals += 1
                row = [staff.name]
                values = []
                for factor in factors:
                    v = evals.get(factor.id, 0)
                    val = float(v)
                    row.append(str(val))
                    factor_totals[factor.name] += val
                    values.append(val)
                avg = round(sum(values) / len(values), 2) if values else 0
                row.append(str(avg))
                rows.append(row)

            # 平均値を計算
            factor_averages = {}
            if count_with_evals > 0:
                for name, total in factor_totals.items():
                    factor_averages[name] = round(total / count_with_evals, 2)

            return {
                "headers": headers,
                "rows": rows,
                "stats": {
                    "factor_averages": factor_averages,
                    "count_with_evals": count_with_evals
                }
            }

    def get_popularity_summary(self, fiscal_year: int) -> Dict[str, Any]:
        """
        病院人気度の集計データを取得

        Returns:
            {
                "headers": [...],
                "rows": [[...], ...],
            }
        """
        with get_db_session() as db:
            hospital_repo = HospitalRepository(db)
            choice_repo = HospitalChoiceRepository(db)

            hospitals = hospital_repo.get_all()
            hospital_map = {h.id: h for h in hospitals}

            # 全病院の人気度を一括取得
            all_popularity = choice_repo.get_hospital_popularity(fiscal_year)

            headers = ["病院名", "第1希望数", "第2希望数", "第3希望数", "合計希望数", "受入定員"]
            rows = []

            for hospital in hospitals:
                pop = all_popularity.get(hospital.id, {})
                first = pop.get("rank1", 0)
                second = pop.get("rank2", 0)
                third = pop.get("rank3", 0)
                total = pop.get("total", 0)

                rows.append([
                    hospital.name,
                    str(first),
                    str(second),
                    str(third),
                    str(total),
                    str(hospital.resident_capacity)
                ])

            # 合計希望数で降順ソート
            rows.sort(key=lambda r: int(r[4]), reverse=True)

            return {
                "headers": headers,
                "rows": rows,
            }

    def get_all_summaries(self, fiscal_year: Optional[int] = None) -> Dict[str, Dict[str, Any]]:
        """
        全ての集計データを取得

        Args:
            fiscal_year: 年度（省略時は現在の年度）

        Returns:
            {
                "hospital_choices": {...},
                "factor_weights": {...},
                "admin_evaluations": {...},
                "popularity": {...}
            }
        """
        if fiscal_year is None:
            fiscal_year = config_service.get_fiscal_year()

        return {
            "hospital_choices": self.get_hospital_choices_summary(fiscal_year),
            "factor_weights": self.get_factor_weights_summary(fiscal_year),
            "admin_evaluations": self.get_admin_evaluations_summary(fiscal_year),
            "popularity": self.get_popularity_summary(fiscal_year),
        }

    def export_to_spreadsheet(self, fiscal_year: Optional[int] = None) -> Optional[str]:
        """
        集計データをGoogleスプレッドシートにエクスポート

        Args:
            fiscal_year: 年度（省略時は現在の年度）

        Returns:
            スプレッドシートのURL（失敗時None）
        """
        if fiscal_year is None:
            fiscal_year = config_service.get_fiscal_year()

        summaries = self.get_all_summaries(fiscal_year)

        # スプレッドシートのシートデータを構築
        sheets_data = [
            {
                "title": "病院希望一覧",
                "headers": summaries["hospital_choices"]["headers"],
                "rows": summaries["hospital_choices"]["rows"],
            },
            {
                "title": "要素重み一覧",
                "headers": summaries["factor_weights"]["headers"],
                "rows": summaries["factor_weights"]["rows"],
            },
            {
                "title": "医局側評価一覧",
                "headers": summaries["admin_evaluations"]["headers"],
                "rows": summaries["admin_evaluations"]["rows"],
            },
            {
                "title": "病院人気度",
                "headers": summaries["popularity"]["headers"],
                "rows": summaries["popularity"]["rows"],
            },
        ]

        title = f"質問項目集計_{fiscal_year}年度"

        if not google_sheets_service.is_authenticated():
            if not google_sheets_service.authenticate():
                logger.error("Failed to authenticate with Google Sheets API")
                return None

        url = google_sheets_service.create_spreadsheet(title, sheets_data)
        if url:
            logger.info(f"Exported survey data to spreadsheet: {url}")
        return url


# シングルトンインスタンス
survey_export_service = SurveyExportService()
