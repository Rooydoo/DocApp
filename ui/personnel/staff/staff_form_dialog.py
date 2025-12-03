"""
職員登録・編集フォームダイアログ
"""
from typing import Optional, Dict
import customtkinter as ctk
from ui.components import FormDialog, FormField, FieldType
from database.connection import get_db_session
from repositories.staff_repository import StaffRepository
from database.models.staff import Staff
from config.constants import ValidationLimits, StaffType
from utils.logger import get_logger
from utils.validators import validate_email
from utils.exceptions import RecordNotFoundException

logger = get_logger(__name__)


class StaffFormDialog(FormDialog):
    """
    職員登録・編集フォームダイアログ
    
    使用例:
        # 新規登録
        dialog = StaffFormDialog(parent, mode="create")
        dialog.on_submit(callback)
        
        # 編集
        dialog = StaffFormDialog(parent, mode="edit", staff=staff_instance)
        dialog.on_submit(callback)
    """
    
    def __init__(
        self,
        parent,
        mode: str = "create",
        staff: Optional[Staff] = None
    ):
        """
        Args:
            parent: 親ウィジェット
            mode: "create" または "edit"
            staff: 編集モード時の職員インスタンス
        """
        self.mode = mode
        self.staff = staff
        
        # フィールド定義
        fields = self._create_fields()
        
        # タイトル設定
        title = "👥 職員新規登録" if mode == "create" else f"✏️ 職員編集 - {staff.name}"
        
        # 親クラス初期化
        super().__init__(
            parent=parent,
            title=title,
            fields=fields,
            width=600,
            height=800
        )
        
        # 編集モードの場合、既存データを設定
        if mode == "edit" and staff:
            self._load_staff_data()
        
        logger.debug(f"StaffFormDialog initialized: mode={mode}")
    
    def _create_fields(self) -> list[FormField]:
        """フィールド定義を作成"""
        return [
            FormField(
                key="name",
                label="氏名",
                field_type=FieldType.TEXT,
                required=True,
                placeholder="例: 山田 太郎"
            ),
            FormField(
                key="staff_type",
                label="職員種別",
                field_type=FieldType.SELECT,
                required=True,
                options=StaffType.all(),
                default=StaffType.RESIDENT_DOCTOR
            ),
            FormField(
                key="email",
                label="メールアドレス",
                field_type=FieldType.EMAIL,
                required=True,
                placeholder="例: yamada@example.com",
                validator=self._validate_email
            ),
            FormField(
                key="phone",
                label="電話番号",
                field_type=FieldType.TEXT,
                required=False,
                placeholder="例: 090-1234-5678"
            ),
            FormField(
                key="address",
                label="住所",
                field_type=FieldType.TEXT,
                required=False,
                placeholder="例: 東京都千代田区..."
            ),
            FormField(
                key="rotation_months",
                label="希望ローテーション期間（ヶ月）",
                field_type=FieldType.NUMBER,
                required=False,
                validator=self._validate_rotation_months
            ),
            FormField(
                key="notes",
                label="備考",
                field_type=FieldType.TEXTAREA,
                required=False,
                placeholder="その他の情報や特記事項を入力..."
            ),
        ]
    
    def _load_staff_data(self):
        """既存の職員データをフォームに設定"""
        if not self.staff:
            return
        
        values = {
            "name": self.staff.name,
            "staff_type": self.staff.staff_type,
            "email": self.staff.email,
            "phone": self.staff.phone or "",
            "address": self.staff.address or "",
            "rotation_months": self.staff.rotation_months or "",
            "notes": self.staff.notes or "",
        }
        
        self.set_values(values)
    
    def _validate_email(self, value: str) -> tuple[bool, str]:
        """
        メールアドレスのバリデーション
        
        Args:
            value: メールアドレス
            
        Returns:
            (is_valid, error_message)
        """
        # 形式チェック
        try:
            validate_email(value)
        except ValueError as e:
            return False, str(e)
        
        # 編集モードでメールアドレスが変わっていない場合はスキップ
        if self.mode == "edit" and self.staff and value == self.staff.email:
            return True, ""
        
        # 重複チェック
        try:
            with get_db_session() as db:
                repo = StaffRepository(db)
                existing = repo.get_by_email(value)
                
                if existing:
                    return False, "このメールアドレスは既に登録されています"
        except Exception as e:
            logger.error(f"Email validation error: {e}")
        
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
        
        # 選考医の場合、住所が必須
        if values["staff_type"] == StaffType.RESIDENT_DOCTOR and not values.get("address"):
            # エラー表示
            if "address" in self.error_labels:
                self.error_labels["address"].configure(text="選考医の場合、住所は必須です")
            logger.warning("Address is required for resident doctor")
            return
        
        try:
            if self.mode == "create":
                self._create_staff(values)
            else:
                self._update_staff(values)
            
            # コールバック実行
            if self._on_submit_callback:
                self._on_submit_callback(values)
            
            self.destroy()
        
        except Exception as e:
            logger.error(f"Failed to save staff: {e}")
            self._show_error_message(f"保存に失敗しました: {str(e)}")
    
    def _create_staff(self, values: Dict):
        """
        職員を新規作成
        
        Args:
            values: フォーム入力値
        """
        with get_db_session() as db:
            repo = StaffRepository(db)
            
            # データ整形
            staff_data = {
                "name": values["name"],
                "staff_type": values["staff_type"],
                "email": values["email"],
                "phone": values.get("phone") or None,
                "address": values.get("address") or None,
                "rotation_months": int(values["rotation_months"]) if values.get("rotation_months") else None,
                "notes": values.get("notes") or None,
            }
            
            staff = repo.create(staff_data)
            
            logger.info(f"Staff created: {staff.name} (ID: {staff.id})")
            
            # 選考医の場合、通勤時間キャッシュ更新トリガー
            if staff.staff_type == StaffType.RESIDENT_DOCTOR and staff.address:
                logger.info(f"Resident doctor created with address, triggering commute cache update")
                self._trigger_commute_cache_update(staff.id)
    
    def _update_staff(self, values: Dict):
        """
        職員を更新
        
        Args:
            values: フォーム入力値
        """
        if not self.staff:
            raise ValueError("Staff instance is required for update")
        
        with get_db_session() as db:
            repo = StaffRepository(db)
            
            # データ整形
            staff_data = {
                "name": values["name"],
                "staff_type": values["staff_type"],
                "email": values["email"],
                "phone": values.get("phone") or None,
                "address": values.get("address") or None,
                "rotation_months": int(values["rotation_months"]) if values.get("rotation_months") else None,
                "notes": values.get("notes") or None,
            }
            
            # 住所変更チェック（選考医の場合のみ）
            address_changed = (
                staff_data["staff_type"] == StaffType.RESIDENT_DOCTOR and
                staff_data.get("address") and
                staff_data["address"] != self.staff.address
            )
            
            staff = repo.update(self.staff.id, staff_data)
            
            logger.info(f"Staff updated: {staff.name} (ID: {staff.id})")
            
            # 住所が変更された場合は通勤時間キャッシュを更新
            if address_changed:
                logger.info(f"Address changed for resident doctor {staff.id}, triggering commute cache update")
                self._trigger_commute_cache_update(staff.id)
    
    def _trigger_commute_cache_update(self, staff_id: int):
        """
        通勤時間キャッシュ更新をトリガー（非同期）
        
        Args:
            staff_id: 職員ID
        """
        try:
            from services.commute_service import commute_service
            
            # バックグラウンドで実行（UIをブロックしない）
            import threading
            
            def update_cache():
                try:
                    commute_service.update_commute_cache_for_staff(staff_id)
                    logger.info(f"Commute cache update completed for staff {staff_id}")
                except Exception as e:
                    logger.error(f"Failed to update commute cache: {e}")
            
            thread = threading.Thread(target=update_cache, daemon=True)
            thread.start()
            
            logger.info(f"Commute cache update triggered in background for staff {staff_id}")
        
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