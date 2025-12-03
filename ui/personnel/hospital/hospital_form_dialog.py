"""
病院登録・編集フォームダイアログ
"""
from typing import Optional, Dict
import customtkinter as ctk
from ui.components import FormDialog, FormField, FieldType
from database.connection import get_db_session
from repositories.hospital_repository import HospitalRepository
from database.models.hospital import Hospital
from config.constants import ValidationLimits
from utils.logger import get_logger
from utils.exceptions import RecordNotFoundException

logger = get_logger(__name__)


class HospitalFormDialog(FormDialog):
    """
    病院登録・編集フォームダイアログ
    
    使用例:
        # 新規登録
        dialog = HospitalFormDialog(parent, mode="create")
        dialog.on_submit(callback)
        
        # 編集
        dialog = HospitalFormDialog(parent, mode="edit", hospital=hospital_instance)
        dialog.on_submit(callback)
    """
    
    def __init__(
        self,
        parent,
        mode: str = "create",
        hospital: Optional[Hospital] = None
    ):
        """
        Args:
            parent: 親ウィジェット
            mode: "create" または "edit"
            hospital: 編集モード時の病院インスタンス
        """
        self.mode = mode
        self.hospital = hospital
        
        # フィールド定義
        fields = self._create_fields()
        
        # タイトル設定
        title = "🏥 病院新規登録" if mode == "create" else f"✏️ 病院編集 - {hospital.name}"
        
        # 親クラス初期化
        super().__init__(
            parent=parent,
            title=title,
            fields=fields,
            width=600,
            height=750
        )
        
        # 編集モードの場合、既存データを設定
        if mode == "edit" and hospital:
            self._load_hospital_data()
        
        logger.debug(f"HospitalFormDialog initialized: mode={mode}")
    
    def _create_fields(self) -> list[FormField]:
        """フィールド定義を作成"""
        return [
            FormField(
                key="name",
                label="病院名",
                field_type=FieldType.TEXT,
                required=True,
                placeholder="例: ○○総合病院",
                validator=self._validate_name
            ),
            FormField(
                key="director_name",
                label="院長名",
                field_type=FieldType.TEXT,
                required=False,
                placeholder="例: 山田 太郎"
            ),
            FormField(
                key="address",
                label="住所",
                field_type=FieldType.TEXT,
                required=True,
                placeholder="例: 東京都千代田区..."
            ),
            FormField(
                key="resident_capacity",
                label="専攻医受入人数",
                field_type=FieldType.NUMBER,
                required=True,
                default=0,
                validator=self._validate_capacity
            ),
            FormField(
                key="specialist_capacity",
                label="専門医受入人数",
                field_type=FieldType.NUMBER,
                required=True,
                default=0,
                validator=self._validate_capacity
            ),
            FormField(
                key="instructor_capacity",
                label="指導医受入人数",
                field_type=FieldType.NUMBER,
                required=True,
                default=0,
                validator=self._validate_capacity
            ),
            FormField(
                key="rotation_months",
                label="ローテーション期間（ヶ月）",
                field_type=FieldType.NUMBER,
                required=False,
                validator=self._validate_rotation_months
            ),
            FormField(
                key="annual_salary",
                label="年収（円）",
                field_type=FieldType.NUMBER,
                required=False,
                placeholder="例: 5000000"
            ),
            FormField(
                key="outpatient_flag",
                label="外勤対象",
                field_type=FieldType.CHECKBOX,
                default=False
            ),
            FormField(
                key="notes",
                label="備考",
                field_type=FieldType.TEXTAREA,
                required=False,
                placeholder="その他の情報や特記事項を入力..."
            ),
        ]
    
    def _load_hospital_data(self):
        """既存の病院データをフォームに設定"""
        if not self.hospital:
            return
        
        values = {
            "name": self.hospital.name,
            "director_name": self.hospital.director_name or "",
            "address": self.hospital.address,
            "resident_capacity": self.hospital.resident_capacity,
            "specialist_capacity": self.hospital.specialist_capacity,
            "instructor_capacity": self.hospital.instructor_capacity,
            "rotation_months": self.hospital.rotation_months or "",
            "annual_salary": self.hospital.annual_salary or "",
            "outpatient_flag": self.hospital.outpatient_flag,
            "notes": self.hospital.notes or "",
        }
        
        self.set_values(values)
    
    def _validate_name(self, value: str) -> tuple[bool, str]:
        """
        病院名のバリデーション
        
        Args:
            value: 病院名
            
        Returns:
            (is_valid, error_message)
        """
        if len(value) > ValidationLimits.MAX_NAME_LENGTH:
            return False, f"病院名は{ValidationLimits.MAX_NAME_LENGTH}文字以内で入力してください"
        
        # 編集モードで名前が変わっていない場合はスキップ
        if self.mode == "edit" and self.hospital and value == self.hospital.name:
            return True, ""
        
        # 重複チェック
        try:
            with get_db_session() as db:
                repo = HospitalRepository(db)
                existing = repo.get_by_name(value)
                
                if existing:
                    return False, "この病院名は既に登録されています"
        except Exception as e:
            logger.error(f"Name validation error: {e}")
        
        return True, ""
    
    def _validate_capacity(self, value) -> tuple[bool, str]:
        """
        受入人数のバリデーション
        
        Args:
            value: 受入人数
            
        Returns:
            (is_valid, error_message)
        """
        if not isinstance(value, (int, float)):
            return False, "数値を入力してください"
        
        value = int(value)
        
        if value < ValidationLimits.MIN_CAPACITY:
            return False, f"受入人数は{ValidationLimits.MIN_CAPACITY}以上で入力してください"
        
        if value > ValidationLimits.MAX_CAPACITY:
            return False, f"受入人数は{ValidationLimits.MAX_CAPACITY}以下で入力してください"
        
        return True, ""
    
    def _validate_rotation_months(self, value) -> tuple[bool, str]:
        """
        ローテーション期間のバリデーション
        
        Args:
            value: ローテーション期間
            
        Returns:
            (is_valid, error_message)
        """
        if value is None or value == "":
            return True, ""  # 任意フィールド
        
        if not isinstance(value, (int, float)):
            return False, "数値を入力してください"
        
        value = int(value)
        
        if value < ValidationLimits.MIN_ROTATION_MONTHS:
            return False, f"ローテーション期間は{ValidationLimits.MIN_ROTATION_MONTHS}ヶ月以上で入力してください"
        
        if value > ValidationLimits.MAX_ROTATION_MONTHS:
            return False, f"ローテーション期間は{ValidationLimits.MAX_ROTATION_MONTHS}ヶ月以下で入力してください"
        
        return True, ""
    
    def _on_save(self):
        """保存ボタンクリック時の処理（オーバーライド）"""
        if not self.validate():
            logger.warning("Form validation failed")
            return
        
        values = self.get_values()
        
        try:
            if self.mode == "create":
                self._create_hospital(values)
            else:
                self._update_hospital(values)
            
            # コールバック実行
            if self._on_submit_callback:
                self._on_submit_callback(values)
            
            self.destroy()
        
        except Exception as e:
            logger.error(f"Failed to save hospital: {e}")
            self._show_error_message(f"保存に失敗しました: {str(e)}")
    
    def _create_hospital(self, values: Dict):
        """
        病院を新規作成
        
        Args:
            values: フォーム入力値
        """
        with get_db_session() as db:
            repo = HospitalRepository(db)
            
            # データ整形
            hospital_data = {
                "name": values["name"],
                "director_name": values.get("director_name") or None,
                "address": values["address"],
                "resident_capacity": int(values["resident_capacity"]),
                "specialist_capacity": int(values["specialist_capacity"]),
                "instructor_capacity": int(values["instructor_capacity"]),
                "rotation_months": int(values["rotation_months"]) if values.get("rotation_months") else None,
                "annual_salary": float(values["annual_salary"]) if values.get("annual_salary") else None,
                "outpatient_flag": values.get("outpatient_flag", False),
                "notes": values.get("notes") or None,
            }
            
            hospital = repo.create(hospital_data)
            
            logger.info(f"Hospital created: {hospital.name} (ID: {hospital.id})")
            
            # 通勤時間キャッシュ更新トリガー
            self._trigger_commute_cache_update(hospital.id)
    
    def _update_hospital(self, values: Dict):
        """
        病院を更新
        
        Args:
            values: フォーム入力値
        """
        if not self.hospital:
            raise ValueError("Hospital instance is required for update")
        
        with get_db_session() as db:
            repo = HospitalRepository(db)
            
            # データ整形
            hospital_data = {
                "name": values["name"],
                "director_name": values.get("director_name") or None,
                "address": values["address"],
                "resident_capacity": int(values["resident_capacity"]),
                "specialist_capacity": int(values["specialist_capacity"]),
                "instructor_capacity": int(values["instructor_capacity"]),
                "rotation_months": int(values["rotation_months"]) if values.get("rotation_months") else None,
                "annual_salary": float(values["annual_salary"]) if values.get("annual_salary") else None,
                "outpatient_flag": values.get("outpatient_flag", False),
                "notes": values.get("notes") or None,
            }
            
            # 住所変更チェック
            address_changed = hospital_data["address"] != self.hospital.address
            
            hospital = repo.update(self.hospital.id, hospital_data)
            
            logger.info(f"Hospital updated: {hospital.name} (ID: {hospital.id})")
            
            # 住所が変更された場合は通勤時間キャッシュを更新
            if address_changed:
                logger.info(f"Address changed for hospital {hospital.id}, triggering commute cache update")
                self._trigger_commute_cache_update(hospital.id)
    
    def _trigger_commute_cache_update(self, hospital_id: int):
        """
        通勤時間キャッシュ更新をトリガー（非同期）
        
        Args:
            hospital_id: 病院ID
        """
        try:
            from services.commute_service import commute_service
            
            # バックグラウンドで実行（UIをブロックしない）
            import threading
            
            def update_cache():
                try:
                    commute_service.update_commute_cache_for_hospital(hospital_id)
                    logger.info(f"Commute cache update completed for hospital {hospital_id}")
                except Exception as e:
                    logger.error(f"Failed to update commute cache: {e}")
            
            thread = threading.Thread(target=update_cache, daemon=True)
            thread.start()
            
            logger.info(f"Commute cache update triggered in background for hospital {hospital_id}")
        
        except ImportError:
            logger.warning("commute_service not available, skipping cache update")
        except Exception as e:
            logger.error(f"Failed to trigger commute cache update: {e}")
    
    def _show_error_message(self, message: str):
        """
        エラーメッセージを表示
        
        Args:
            message: エラーメッセージ
        """
        # TODO: 適切なエラーダイアログに置き換え
        error_dialog = ctk.CTkInputDialog(
            text=message,
            title="エラー"
        )
        error_dialog.get_input()