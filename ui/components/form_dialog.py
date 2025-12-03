"""
汎用フォームダイアログコンポーネント
登録・編集フォームの表示を提供
"""
import customtkinter as ctk
from typing import Callable, Optional, Any, List, Dict
from enum import Enum
from config.constants import Colors, Fonts, Spacing
from utils.logger import get_logger

logger = get_logger(__name__)


class FieldType(Enum):
    """フィールドタイプ"""
    TEXT = "text"
    NUMBER = "number"
    EMAIL = "email"
    TEXTAREA = "textarea"
    CHECKBOX = "checkbox"
    SELECT = "select"


class FormField:
    """フォームフィールド定義"""
    
    def __init__(
        self,
        key: str,
        label: str,
        field_type: FieldType = FieldType.TEXT,
        required: bool = False,
        default: Any = None,
        options: Optional[List[str]] = None,
        validator: Optional[Callable[[Any], tuple[bool, str]]] = None,
        placeholder: str = ""
    ):
        """
        Args:
            key: データのキー名
            label: フィールドラベル
            field_type: フィールドタイプ
            required: 必須フィールドかどうか
            default: デフォルト値
            options: SELECT用の選択肢リスト
            validator: カスタムバリデーター関数 (value) -> (is_valid, error_message)
            placeholder: プレースホルダーテキスト
        """
        self.key = key
        self.label = label
        self.field_type = field_type
        self.required = required
        self.default = default
        self.options = options or []
        self.validator = validator
        self.placeholder = placeholder


class FormDialog(ctk.CTkToplevel):
    """
    汎用フォームダイアログ
    
    使用例:
        fields = [
            FormField("name", "病院名", required=True),
            FormField("capacity", "受入人数", field_type=FieldType.NUMBER),
        ]
        dialog = FormDialog(parent, title="病院登録", fields=fields)
        dialog.on_submit(callback)
        
        # 編集モード
        dialog.set_values({"name": "テスト病院", "capacity": 5})
    """
    
    def __init__(
        self,
        parent,
        title: str,
        fields: List[FormField],
        width: int = 600,
        height: int = 700
    ):
        """
        Args:
            parent: 親ウィジェット
            title: ダイアログタイトル
            fields: フィールド定義リスト
            width: ダイアログ幅
            height: ダイアログ高さ
        """
        super().__init__(parent)
        
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.resizable(False, False)
        
        # モーダル化
        self.transient(parent)
        self.grab_set()
        
        self.fields = fields
        self.widgets: Dict[str, Any] = {}
        self.error_labels: Dict[str, ctk.CTkLabel] = {}
        
        # コールバック
        self._on_submit_callback: Optional[Callable[[Dict], None]] = None
        self._on_cancel_callback: Optional[Callable[[], None]] = None
        
        # UI構築
        self._create_ui()
        
        # 画面中央に配置
        self._center_window()
        
        logger.debug(f"FormDialog created: {title}")
    
    def _create_ui(self):
        """UI要素を作成"""
        # ヘッダー
        header_frame = ctk.CTkFrame(
            self,
            fg_color=Colors.GRADIENT_START,
            corner_radius=0,
            height=60
        )
        header_frame.pack(fill="x", side="top")
        header_frame.pack_propagate(False)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text=self.title(),
            font=(Fonts.FAMILY, Fonts.TITLE, Fonts.BOLD),
            text_color=Colors.TEXT_WHITE
        )
        title_label.pack(side="left", padx=Spacing.PADDING_LARGE, pady=Spacing.PADDING_MEDIUM)
        
        # フォームエリア（スクロール可能）
        self.form_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=Colors.BG_MAIN
        )
        self.form_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        # フィールドを生成
        for field in self.fields:
            self._create_field(field)
        
        # ボタンエリア
        button_frame = ctk.CTkFrame(
            self,
            fg_color=Colors.LIGHT_GRAY,
            corner_radius=0,
            height=70
        )
        button_frame.pack(fill="x", side="bottom")
        button_frame.pack_propagate(False)
        
        # キャンセルボタン
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="キャンセル",
            font=(Fonts.FAMILY, Fonts.BODY),
            fg_color=Colors.MEDIUM_GRAY,
            hover_color=Colors.DARK_GRAY,
            width=120,
            height=40,
            command=self._on_cancel
        )
        cancel_btn.pack(side="right", padx=Spacing.PADDING_LARGE, pady=Spacing.PADDING_MEDIUM)
        
        # 保存ボタン
        save_btn = ctk.CTkButton(
            button_frame,
            text="保存",
            font=(Fonts.FAMILY, Fonts.BODY, Fonts.BOLD),
            fg_color=Colors.PRIMARY,
            hover_color=Colors.PRIMARY_HOVER,
            width=120,
            height=40,
            command=self._on_save
        )
        save_btn.pack(side="right", padx=Spacing.PADDING_SMALL, pady=Spacing.PADDING_MEDIUM)
    
    def _create_field(self, field: FormField):
        """
        フィールドを作成
        
        Args:
            field: フィールド定義
        """
        # フィールドコンテナ
        container = ctk.CTkFrame(
            self.form_frame,
            fg_color="transparent"
        )
        container.pack(fill="x", padx=Spacing.PADDING_LARGE, pady=Spacing.PADDING_SMALL)
        
        # ラベル
        label_text = field.label
        if field.required:
            label_text += " *"
        
        label = ctk.CTkLabel(
            container,
            text=label_text,
            font=(Fonts.FAMILY, Fonts.BODY, Fonts.BOLD),
            text_color=Colors.TEXT_PRIMARY,
            anchor="w"
        )
        label.pack(fill="x", pady=(Spacing.PADDING_SMALL, 4))
        
        # フィールドウィジェット
        widget = self._create_field_widget(container, field)
        self.widgets[field.key] = widget
        
        # エラーラベル
        error_label = ctk.CTkLabel(
            container,
            text="",
            font=(Fonts.FAMILY, Fonts.SMALL),
            text_color=Colors.ERROR,
            anchor="w"
        )
        error_label.pack(fill="x", pady=(2, 0))
        self.error_labels[field.key] = error_label
    
    def _create_field_widget(self, parent, field: FormField) -> Any:
        """
        フィールドタイプに応じたウィジェットを作成
        
        Args:
            parent: 親ウィジェット
            field: フィールド定義
            
        Returns:
            作成されたウィジェット
        """
        if field.field_type == FieldType.TEXT or field.field_type == FieldType.EMAIL:
            widget = ctk.CTkEntry(
                parent,
                font=(Fonts.FAMILY, Fonts.BODY),
                placeholder_text=field.placeholder or f"{field.label}を入力",
                height=40
            )
            widget.pack(fill="x")
            
        elif field.field_type == FieldType.NUMBER:
            widget = ctk.CTkEntry(
                parent,
                font=(Fonts.FAMILY, Fonts.BODY),
                placeholder_text=field.placeholder or "数値を入力",
                height=40
            )
            widget.pack(fill="x")
            
        elif field.field_type == FieldType.TEXTAREA:
            widget = ctk.CTkTextbox(
                parent,
                font=(Fonts.FAMILY, Fonts.BODY),
                height=100
            )
            widget.pack(fill="x")
            
        elif field.field_type == FieldType.CHECKBOX:
            widget = ctk.CTkCheckBox(
                parent,
                text="",
                font=(Fonts.FAMILY, Fonts.BODY)
            )
            widget.pack(anchor="w")
            
        elif field.field_type == FieldType.SELECT:
            widget = ctk.CTkComboBox(
                parent,
                values=field.options,
                font=(Fonts.FAMILY, Fonts.BODY),
                height=40,
                state="readonly"
            )
            widget.pack(fill="x")
        
        else:
            # デフォルトはテキストフィールド
            widget = ctk.CTkEntry(
                parent,
                font=(Fonts.FAMILY, Fonts.BODY),
                height=40
            )
            widget.pack(fill="x")
        
        # デフォルト値を設定
        if field.default is not None:
            self._set_widget_value(widget, field.field_type, field.default)
        
        return widget
    
    def _set_widget_value(self, widget: Any, field_type: FieldType, value: Any):
        """ウィジェットに値を設定"""
        if field_type == FieldType.TEXTAREA:
            widget.delete("1.0", "end")
            widget.insert("1.0", str(value))
        elif field_type == FieldType.CHECKBOX:
            if value:
                widget.select()
            else:
                widget.deselect()
        elif field_type == FieldType.SELECT:
            widget.set(str(value))
        else:
            widget.delete(0, "end")
            widget.insert(0, str(value))
    
    def _get_widget_value(self, widget: Any, field_type: FieldType) -> Any:
        """ウィジェットから値を取得"""
        if field_type == FieldType.TEXTAREA:
            return widget.get("1.0", "end-1c").strip()
        elif field_type == FieldType.CHECKBOX:
            return widget.get() == 1
        elif field_type == FieldType.NUMBER:
            text = widget.get().strip()
            if not text:
                return None
            try:
                return int(text) if '.' not in text else float(text)
            except ValueError:
                return text
        else:
            return widget.get().strip()
    
    def set_values(self, values: Dict[str, Any]):
        """
        フォームに値を設定（編集モード）
        
        Args:
            values: 設定する値の辞書
        """
        for field in self.fields:
            if field.key in values and field.key in self.widgets:
                value = values[field.key]
                widget = self.widgets[field.key]
                self._set_widget_value(widget, field.field_type, value)
        
        logger.debug(f"Form values set: {list(values.keys())}")
    
    def get_values(self) -> Dict[str, Any]:
        """
        フォームから値を取得
        
        Returns:
            入力値の辞書
        """
        values = {}
        for field in self.fields:
            if field.key in self.widgets:
                widget = self.widgets[field.key]
                value = self._get_widget_value(widget, field.field_type)
                values[field.key] = value
        
        return values
    
    def validate(self) -> bool:
        """
        フォームをバリデーション
        
        Returns:
            バリデーション成功時True
        """
        is_valid = True
        
        # エラーメッセージをクリア
        for error_label in self.error_labels.values():
            error_label.configure(text="")
        
        values = self.get_values()
        
        for field in self.fields:
            value = values.get(field.key)
            error_msg = ""
            
            # 必須チェック
            if field.required:
                if value is None or value == "":
                    error_msg = f"{field.label}は必須です"
                    is_valid = False
            
            # 数値チェック
            if not error_msg and field.field_type == FieldType.NUMBER:
                if value is not None and value != "" and not isinstance(value, (int, float)):
                    error_msg = "数値を入力してください"
                    is_valid = False
            
            # メールチェック
            if not error_msg and field.field_type == FieldType.EMAIL:
                if value and "@" not in str(value):
                    error_msg = "正しいメールアドレスを入力してください"
                    is_valid = False
            
            # カスタムバリデーター
            if not error_msg and field.validator and value:
                valid, msg = field.validator(value)
                if not valid:
                    error_msg = msg
                    is_valid = False
            
            # エラー表示
            if error_msg and field.key in self.error_labels:
                self.error_labels[field.key].configure(text=error_msg)
        
        return is_valid
    
    def _on_save(self):
        """保存ボタンクリック時の処理"""
        if not self.validate():
            logger.warning("Form validation failed")
            return
        
        values = self.get_values()
        
        if self._on_submit_callback:
            self._on_submit_callback(values)
        
        logger.info(f"Form submitted: {list(values.keys())}")
        self.destroy()
    
    def _on_cancel(self):
        """キャンセルボタンクリック時の処理"""
        if self._on_cancel_callback:
            self._on_cancel_callback()
        
        logger.debug("Form cancelled")
        self.destroy()
    
    def on_submit(self, callback: Callable[[Dict], None]):
        """
        送信時のコールバックを設定
        
        Args:
            callback: コールバック関数（入力値の辞書を引数に受け取る）
        """
        self._on_submit_callback = callback
    
    def on_cancel(self, callback: Callable[[], None]):
        """
        キャンセル時のコールバックを設定
        
        Args:
            callback: コールバック関数
        """
        self._on_cancel_callback = callback
    
    def _center_window(self):
        """ウィンドウを画面中央に配置"""
        self.update_idletasks()
        
        # 画面サイズ取得
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # ウィンドウサイズ取得
        window_width = self.winfo_width()
        window_height = self.winfo_height()
        
        # 中央座標計算
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.geometry(f"+{x}+{y}")
