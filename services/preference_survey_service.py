"""
希望調査スプレッドシートサービス

専攻医の希望調査用スプレッドシートの生成・インポート機能
"""
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session

from services.google_sheets_service import GoogleSheetsService, GoogleSheetsException
from repositories.staff_repository import StaffRepository
from repositories.hospital_repository import HospitalRepository
from repositories.evaluation_factor_repository import EvaluationFactorRepository
from repositories.staff_factor_weight_repository import StaffFactorWeightRepository
from repositories.hospital_choice_repository import HospitalChoiceRepository
from config.constants import FactorType
from utils.logger import get_logger

logger = get_logger(__name__)


class PreferenceSurveyException(Exception):
    """希望調査サービス例外"""
    pass


class PreferenceSurveyService:
    """
    希望調査スプレッドシートサービス

    専攻医の希望病院・重み付けデータの収集用スプレッドシート生成と
    入力データのインポート機能を提供
    """

    # シート名
    SHEET_HOSPITAL_CHOICES = "病院希望"
    SHEET_FACTOR_WEIGHTS = "要素重み付け"
    SHEET_INFO = "入力案内"

    def __init__(self, db: Session, sheets_service: Optional[GoogleSheetsService] = None):
        """
        Args:
            db: データベースセッション
            sheets_service: Google Sheetsサービス（省略時は新規作成）
        """
        self.db = db
        self.sheets_service = sheets_service or GoogleSheetsService()

        # リポジトリ
        self.staff_repo = StaffRepository(db)
        self.hospital_repo = HospitalRepository(db)
        self.factor_repo = EvaluationFactorRepository(db)
        self.weight_repo = StaffFactorWeightRepository(db)
        self.choice_repo = HospitalChoiceRepository(db)

    def create_survey_spreadsheet(
        self,
        title: Optional[str] = None,
        fiscal_year: Optional[int] = None,
        share_emails: Optional[List[str]] = None
    ) -> Tuple[str, str]:
        """
        希望調査用スプレッドシートを作成

        Args:
            title: スプレッドシートのタイトル（省略時は自動生成）
            fiscal_year: 対象年度（省略時は現在年度）
            share_emails: 共有先メールアドレスリスト

        Returns:
            Tuple[str, str]: (スプレッドシートID, URL)
        """
        # 年度設定
        if fiscal_year is None:
            now = datetime.now()
            fiscal_year = now.year if now.month >= 4 else now.year - 1

        # タイトル設定
        if title is None:
            title = f"{fiscal_year}年度 専攻医希望調査"

        try:
            # データ取得
            residents = self.staff_repo.get_resident_doctors()
            hospitals = self.hospital_repo.get_all()
            staff_factors = self.factor_repo.get_staff_preference_factors()

            if not residents:
                raise PreferenceSurveyException("専攻医が登録されていません")
            if not hospitals:
                raise PreferenceSurveyException("病院が登録されていません")
            if not staff_factors:
                raise PreferenceSurveyException("評価要素（専攻医重視）が登録されていません")

            # スプレッドシート作成
            sheets = [
                {"title": self.SHEET_INFO},
                {"title": self.SHEET_HOSPITAL_CHOICES},
                {"title": self.SHEET_FACTOR_WEIGHTS}
            ]
            spreadsheet_id = self.sheets_service.create_spreadsheet(title, sheets)

            # 各シートにデータを書き込み
            self._write_info_sheet(spreadsheet_id, fiscal_year, staff_factors)
            self._write_hospital_choices_sheet(spreadsheet_id, residents, hospitals)
            self._write_factor_weights_sheet(spreadsheet_id, residents, staff_factors)

            # データ検証（ドロップダウン）を追加
            self._add_validations(spreadsheet_id, residents, hospitals)

            # 書式設定
            self._format_sheets(spreadsheet_id, len(residents), len(staff_factors))

            # 共有
            if share_emails:
                for email in share_emails:
                    try:
                        self.sheets_service.share_spreadsheet(spreadsheet_id, email)
                    except GoogleSheetsException as e:
                        logger.warning(f"Failed to share with {email}: {e}")

            url = self.sheets_service.get_spreadsheet_url(spreadsheet_id)
            logger.info(f"Created survey spreadsheet: {spreadsheet_id}")

            return spreadsheet_id, url

        except GoogleSheetsException as e:
            logger.error(f"Failed to create survey spreadsheet: {e}")
            raise PreferenceSurveyException(f"スプレッドシートの作成に失敗しました: {e}")

    def _write_info_sheet(
        self,
        spreadsheet_id: str,
        fiscal_year: int,
        factors: List[Any]
    ):
        """入力案内シートを書き込み"""
        factor_list = "\n".join([f"  - {f.name}: {f.description or ''}" for f in factors])

        info_data = [
            [f"【{fiscal_year}年度 専攻医希望調査】"],
            [""],
            ["■ 入力方法"],
            ["1. 「病院希望」シートに第1希望〜第3希望の病院を選択してください"],
            ["2. 「要素重み付け」シートに各要素の重みを入力してください（合計100）"],
            [""],
            ["■ 病院希望について"],
            ["  - 第1希望〜第3希望をドロップダウンから選択してください"],
            ["  - 同じ病院を複数選択しないでください"],
            [""],
            ["■ 要素重み付けについて"],
            ["  - 各要素に対してどの程度重視するかを数値で入力してください"],
            ["  - 合計が100になるように配分してください"],
            ["  - 重視しない要素は0で構いません"],
            [""],
            ["■ 評価要素一覧"],
        ]

        for f in factors:
            desc = f"（{f.description}）" if f.description else ""
            info_data.append([f"  - {f.name}{desc}"])

        info_data.extend([
            [""],
            ["■ 入力期限"],
            ["  別途ご連絡する期限までに入力をお願いします"],
            [""],
            ["■ 注意事項"],
            ["  - 自分の行以外は編集しないでください"],
            ["  - 入力内容は随時保存されます"],
        ])

        self.sheets_service.write_data(
            spreadsheet_id,
            f"{self.SHEET_INFO}!A1",
            info_data
        )

    def _write_hospital_choices_sheet(
        self,
        spreadsheet_id: str,
        residents: List[Any],
        hospitals: List[Any]
    ):
        """病院希望シートを書き込み"""
        # ヘッダー
        header = ["氏名", "メールアドレス", "第1希望", "第2希望", "第3希望"]

        # データ行
        data = [header]
        for staff in residents:
            data.append([
                staff.name,
                staff.email or "",
                "",  # 第1希望
                "",  # 第2希望
                "",  # 第3希望
            ])

        self.sheets_service.write_data(
            spreadsheet_id,
            f"{self.SHEET_HOSPITAL_CHOICES}!A1",
            data
        )

    def _write_factor_weights_sheet(
        self,
        spreadsheet_id: str,
        residents: List[Any],
        factors: List[Any]
    ):
        """要素重み付けシートを書き込み"""
        # ヘッダー
        header = ["氏名", "メールアドレス"]
        header.extend([f.name for f in factors])
        header.append("合計")

        # データ行
        data = [header]
        for i, staff in enumerate(residents):
            row = [staff.name, staff.email or ""]
            # 要素列（空欄）
            row.extend(["" for _ in factors])
            # 合計列（数式）
            start_col = chr(ord('C'))  # C列から
            end_col = chr(ord('C') + len(factors) - 1)
            row_num = i + 2  # ヘッダーが1行目なので+2
            row.append(f"=SUM({start_col}{row_num}:{end_col}{row_num})")
            data.append(row)

        self.sheets_service.write_data(
            spreadsheet_id,
            f"{self.SHEET_FACTOR_WEIGHTS}!A1",
            data
        )

    def _add_validations(
        self,
        spreadsheet_id: str,
        residents: List[Any],
        hospitals: List[Any]
    ):
        """データ検証を追加"""
        # 病院名リスト
        hospital_names = [h.name for h in hospitals]

        # 病院希望シートのシートID取得
        choice_sheet_id = self.sheets_service.get_sheet_id(
            spreadsheet_id,
            self.SHEET_HOSPITAL_CHOICES
        )

        if choice_sheet_id is not None:
            # 第1〜3希望列にドロップダウン追加（C, D, E列 = 列2, 3, 4）
            for col in range(2, 5):
                self.sheets_service.add_data_validation(
                    spreadsheet_id,
                    choice_sheet_id,
                    start_row=1,  # ヘッダー行スキップ
                    end_row=len(residents) + 1,
                    column=col,
                    values=hospital_names
                )

    def _format_sheets(
        self,
        spreadsheet_id: str,
        num_residents: int,
        num_factors: int
    ):
        """シートの書式設定"""
        try:
            # 病院希望シートのシートID取得
            choice_sheet_id = self.sheets_service.get_sheet_id(
                spreadsheet_id,
                self.SHEET_HOSPITAL_CHOICES
            )

            # 要素重み付けシートのシートID取得
            weight_sheet_id = self.sheets_service.get_sheet_id(
                spreadsheet_id,
                self.SHEET_FACTOR_WEIGHTS
            )

            requests = []

            # ヘッダー行の書式（太字、背景色）
            for sheet_id in [choice_sheet_id, weight_sheet_id]:
                if sheet_id is not None:
                    requests.append({
                        "repeatCell": {
                            "range": {
                                "sheetId": sheet_id,
                                "startRowIndex": 0,
                                "endRowIndex": 1
                            },
                            "cell": {
                                "userEnteredFormat": {
                                    "backgroundColor": {
                                        "red": 0.85,
                                        "green": 0.92,
                                        "blue": 0.98
                                    },
                                    "textFormat": {"bold": True}
                                }
                            },
                            "fields": "userEnteredFormat(backgroundColor,textFormat)"
                        }
                    })

                    # 列幅の自動調整
                    requests.append({
                        "autoResizeDimensions": {
                            "dimensions": {
                                "sheetId": sheet_id,
                                "dimension": "COLUMNS",
                                "startIndex": 0,
                                "endIndex": 10
                            }
                        }
                    })

            # 合計列の条件付き書式（100でない場合は赤色）
            if weight_sheet_id is not None:
                total_col = 2 + num_factors  # 合計列
                requests.append({
                    "addConditionalFormatRule": {
                        "rule": {
                            "ranges": [{
                                "sheetId": weight_sheet_id,
                                "startRowIndex": 1,
                                "endRowIndex": num_residents + 1,
                                "startColumnIndex": total_col,
                                "endColumnIndex": total_col + 1
                            }],
                            "booleanRule": {
                                "condition": {
                                    "type": "NUMBER_NOT_EQ",
                                    "values": [{"userEnteredValue": "100"}]
                                },
                                "format": {
                                    "backgroundColor": {
                                        "red": 1.0,
                                        "green": 0.8,
                                        "blue": 0.8
                                    }
                                }
                            }
                        },
                        "index": 0
                    }
                })

            if requests:
                self.sheets_service.format_cells(spreadsheet_id, 0, requests)

        except Exception as e:
            # 書式設定の失敗は警告のみ
            logger.warning(f"Failed to format sheets: {e}")

    def import_from_spreadsheet(
        self,
        spreadsheet_id: str,
        fiscal_year: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        スプレッドシートからデータをインポート

        Args:
            spreadsheet_id: スプレッドシートID
            fiscal_year: 対象年度（省略時は現在年度）

        Returns:
            Dict: インポート結果 {
                "hospital_choices": {"imported": n, "errors": [...]},
                "factor_weights": {"imported": n, "errors": [...]}
            }
        """
        # 年度設定
        if fiscal_year is None:
            now = datetime.now()
            fiscal_year = now.year if now.month >= 4 else now.year - 1

        result = {
            "hospital_choices": {"imported": 0, "errors": []},
            "factor_weights": {"imported": 0, "errors": []}
        }

        try:
            # 病院希望のインポート
            choice_result = self._import_hospital_choices(spreadsheet_id, fiscal_year)
            result["hospital_choices"] = choice_result

            # 要素重み付けのインポート
            weight_result = self._import_factor_weights(spreadsheet_id, fiscal_year)
            result["factor_weights"] = weight_result

            self.db.commit()
            logger.info(f"Imported data from spreadsheet: {spreadsheet_id}")

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to import from spreadsheet: {e}")
            raise PreferenceSurveyException(f"インポートに失敗しました: {e}")

        return result

    def _import_hospital_choices(
        self,
        spreadsheet_id: str,
        fiscal_year: int
    ) -> Dict[str, Any]:
        """病院希望をインポート"""
        result = {"imported": 0, "errors": []}

        try:
            # データ読み取り
            data = self.sheets_service.read_data(
                spreadsheet_id,
                f"{self.SHEET_HOSPITAL_CHOICES}!A2:E1000"
            )

            if not data:
                return result

            # 病院名→ID マッピング
            hospitals = self.hospital_repo.get_all()
            hospital_map = {h.name: h.id for h in hospitals}

            for row_idx, row in enumerate(data, start=2):
                if len(row) < 3:
                    continue

                staff_name = row[0] if len(row) > 0 else ""
                email = row[1] if len(row) > 1 else ""

                # 職員を検索
                staff = None
                if email:
                    staff = self.staff_repo.get_by_email(email)
                if not staff and staff_name:
                    results = self.staff_repo.search_by_keyword(staff_name)
                    if len(results) == 1:
                        staff = results[0]

                if not staff:
                    result["errors"].append(f"行{row_idx}: 職員が見つかりません（{staff_name}）")
                    continue

                # 既存データを削除
                self.choice_repo.delete_by_staff_and_year(staff.id, fiscal_year)

                # 希望病院を登録
                for rank in range(1, 4):
                    col_idx = rank + 1  # C列=第1希望
                    if len(row) > col_idx and row[col_idx]:
                        hospital_name = row[col_idx].strip()
                        hospital_id = hospital_map.get(hospital_name)

                        if hospital_id:
                            self.choice_repo.create({
                                "staff_id": staff.id,
                                "hospital_id": hospital_id,
                                "fiscal_year": fiscal_year,
                                "rank": rank
                            })
                        else:
                            result["errors"].append(
                                f"行{row_idx}: 病院が見つかりません（{hospital_name}）"
                            )

                result["imported"] += 1

        except GoogleSheetsException as e:
            result["errors"].append(f"シート読み取りエラー: {e}")

        return result

    def _import_factor_weights(
        self,
        spreadsheet_id: str,
        fiscal_year: int
    ) -> Dict[str, Any]:
        """要素重み付けをインポート"""
        result = {"imported": 0, "errors": []}

        try:
            # データ読み取り（ヘッダーも含めて読み取り）
            all_data = self.sheets_service.read_data(
                spreadsheet_id,
                f"{self.SHEET_FACTOR_WEIGHTS}!A1:Z1000"
            )

            if not all_data or len(all_data) < 2:
                return result

            # ヘッダーから要素名を取得
            header = all_data[0]
            data = all_data[1:]

            # 要素名→ID マッピング
            factors = self.factor_repo.get_staff_preference_factors()
            factor_map = {f.name: f.id for f in factors}

            # 要素の列インデックスを特定
            factor_columns = {}  # factor_id -> column_index
            for col_idx, col_name in enumerate(header):
                if col_name in factor_map:
                    factor_columns[factor_map[col_name]] = col_idx

            if not factor_columns:
                result["errors"].append("評価要素の列が見つかりません")
                return result

            for row_idx, row in enumerate(data, start=2):
                if len(row) < 2:
                    continue

                staff_name = row[0] if len(row) > 0 else ""
                email = row[1] if len(row) > 1 else ""

                # 職員を検索
                staff = None
                if email:
                    staff = self.staff_repo.get_by_email(email)
                if not staff and staff_name:
                    results = self.staff_repo.search_by_keyword(staff_name)
                    if len(results) == 1:
                        staff = results[0]

                if not staff:
                    result["errors"].append(f"行{row_idx}: 職員が見つかりません（{staff_name}）")
                    continue

                # 重み付けデータを収集
                weights = []
                for factor_id, col_idx in factor_columns.items():
                    if len(row) > col_idx and row[col_idx]:
                        try:
                            weight_value = float(row[col_idx])
                            weights.append({
                                "staff_id": staff.id,
                                "factor_id": factor_id,
                                "fiscal_year": fiscal_year,
                                "weight": weight_value
                            })
                        except ValueError:
                            result["errors"].append(
                                f"行{row_idx}: 無効な数値（{row[col_idx]}）"
                            )

                # 重み付けを一括登録
                if weights:
                    try:
                        self.weight_repo.bulk_upsert(staff.id, fiscal_year, weights)
                        result["imported"] += 1
                    except ValueError as e:
                        result["errors"].append(f"行{row_idx}: {e}")

        except GoogleSheetsException as e:
            result["errors"].append(f"シート読み取りエラー: {e}")

        return result


# グローバルインスタンス生成用ヘルパー
def get_preference_survey_service(db: Session) -> PreferenceSurveyService:
    """
    PreferenceSurveyServiceのインスタンスを取得

    Args:
        db: データベースセッション

    Returns:
        PreferenceSurveyService: サービスインスタンス
    """
    return PreferenceSurveyService(db)
