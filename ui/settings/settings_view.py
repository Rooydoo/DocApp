"""
設定画面
API設定、GA設定、システム設定を管理
"""
import customtkinter as ctk
from typing import Dict, Any
from config.constants import Colors, Fonts, Spacing
from services.config_service import config_service
from utils.logger import get_logger
from utils.exceptions import ValidationException

logger = get_logger(__name__)


class SettingsView(ctk.CTkFrame):
    """
    設定画面
    
    サブタブ:
    - API設定
    - GA設定
    - システム設定
    """
    
    def __init__(self, parent):
        super().__init__(parent, fg_color=Colors.BG_MAIN)
        
        self.current_tab = "api"
        self.input_widgets: Dict[str, Any] = {}
        
        # UI構築
        self._create_header()
        self._create_tab_bar()
        self._create_content_area()
        
        # 初期タブ表示
        self._load_tab_content(self.current_tab)
        
        logger.info("SettingsView initialized")
    
    def _create_header(self):
        """ヘッダーを作成"""
        header_frame = ctk.CTkFrame(
            self,
            fg_color="transparent",
            height=80
        )
        header_frame.pack(fill="x", padx=Spacing.PADDING_LARGE, pady=(Spacing.PADDING_LARGE, 0))
        header_frame.pack_propagate(False)
        
        # タイトル
        title_label = ctk.CTkLabel(
            header_frame,
            text="⚙️ 設定",
            font=(Fonts.FAMILY, Fonts.TITLE, Fonts.BOLD),
            text_color=Colors.TEXT_PRIMARY,
            anchor="w"
        )
        title_label.pack(side="left", pady=Spacing.PADDING_MEDIUM)
    
    def _create_tab_bar(self):
        """サブタブバーを作成"""
        tab_frame = ctk.CTkFrame(
            self,
            fg_color=Colors.MEDIUM_GRAY,
            height=50
        )
        tab_frame.pack(fill="x", padx=Spacing.PADDING_LARGE, pady=(Spacing.PADDING_MEDIUM, 0))
        tab_frame.pack_propagate(False)
        
        # タブ定義
        self.tabs = [
            ("api", "🔑 API設定"),
            ("ga", "🧬 GA設定"),
            ("system", "🖥️ システム設定"),
        ]
        
        # タブボタンを作成
        self.tab_buttons = {}
        for tab_id, tab_label in self.tabs:
            btn = ctk.CTkButton(
                tab_frame,
                text=tab_label,
                font=(Fonts.FAMILY, Fonts.BODY),
                fg_color=Colors.MEDIUM_GRAY,
                hover_color=Colors.DARK_GRAY,
                corner_radius=0,
                height=50,
                command=lambda t=tab_id: self._switch_tab(t)
            )
            btn.pack(side="left", fill="both", expand=True)
            self.tab_buttons[tab_id] = btn
        
        # 初期タブをアクティブ化
        self._update_tab_appearance()
    
    def _create_content_area(self):
        """コンテンツエリアを作成"""
        self.content_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=Colors.BG_CARD,
            corner_radius=Spacing.RADIUS_CARD
        )
        self.content_frame.pack(
            fill="both",
            expand=True,
            padx=Spacing.PADDING_LARGE,
            pady=Spacing.PADDING_MEDIUM
        )
    
    def _switch_tab(self, tab_id: str):
        """タブを切り替え"""
        logger.info(f"Switching to settings tab: {tab_id}")
        self.current_tab = tab_id
        self._update_tab_appearance()
        self._load_tab_content(tab_id)
    
    def _update_tab_appearance(self):
        """タブの見た目を更新"""
        for tab_id, btn in self.tab_buttons.items():
            if tab_id == self.current_tab:
                btn.configure(fg_color=Colors.PRIMARY, text_color=Colors.TEXT_WHITE)
            else:
                btn.configure(fg_color=Colors.MEDIUM_GRAY, text_color=Colors.LIGHT_GRAY)
    
    def _load_tab_content(self, tab_id: str):
        """タブのコンテンツを読み込み"""
        # 現在のコンテンツをクリア
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        self.input_widgets.clear()
        
        # タブ別のコンテンツを読み込み
        if tab_id == "api":
            self._load_api_settings()
        elif tab_id == "ga":
            self._load_ga_settings()
        elif tab_id == "system":
            self._load_system_settings()
    
    def _load_api_settings(self):
        """API設定を読み込み"""
        self._add_section_title("Google API設定")
        
        # Google Maps API Key
        self._add_input_field(
            key=config_service.Keys.GOOGLE_MAPS_API_KEY,
            label="Google Maps API Key",
            description="通勤時間計算に使用",
            field_type="text",
            placeholder="AIzaSy..."
        )
        
        # Gmail認証情報パス
        self._add_input_field(
            key=config_service.Keys.GMAIL_CREDENTIALS_PATH,
            label="Gmail API認証情報パス",
            description="credentials.jsonファイルのパス",
            field_type="text",
            placeholder="credentials/gmail_credentials.json"
        )
        
        # Google Forms認証情報パス
        self._add_input_field(
            key=config_service.Keys.GOOGLE_FORMS_CREDENTIALS_PATH,
            label="Google Forms API認証情報パス",
            description="credentials.jsonファイルのパス",
            field_type="text",
            placeholder="credentials/forms_credentials.json"
        )
        
        self._add_section_title("LLM設定", top_padding=True)
        
        # Ollama Base URL
        self._add_input_field(
            key=config_service.Keys.OLLAMA_BASE_URL,
            label="Ollama Base URL",
            description="OllamaサーバーのURL",
            field_type="text",
            placeholder="http://localhost:11434"
        )
        
        # Ollamaモデル名
        self._add_input_field(
            key=config_service.Keys.OLLAMA_MODEL,
            label="Ollamaモデル名",
            description="使用するモデル名",
            field_type="text",
            placeholder="llama3-elyza"
        )
        
        # 保存ボタン
        self._add_save_button()
    
    def _load_ga_settings(self):
        """GA設定を読み込み"""
        self._add_section_title("遺伝的アルゴリズム設定")
        
        # 個体数
        self._add_input_field(
            key=config_service.Keys.GA_POPULATION_SIZE,
            label="個体数",
            description="GAの個体数（10-500）",
            field_type="number",
            placeholder="100"
        )
        
        # 世代数
        self._add_input_field(
            key=config_service.Keys.GA_GENERATIONS,
            label="世代数",
            description="GAの世代数（50-1000）",
            field_type="number",
            placeholder="200"
        )
        
        # 交叉確率
        self._add_input_field(
            key=config_service.Keys.GA_CROSSOVER_PROB,
            label="交叉確率",
            description="交叉確率（0.0-1.0）",
            field_type="number",
            placeholder="0.7"
        )
        
        # 突然変異確率
        self._add_input_field(
            key=config_service.Keys.GA_MUTATION_PROB,
            label="突然変異確率",
            description="突然変異確率（0.0-1.0）",
            field_type="number",
            placeholder="0.2"
        )
        
        # アンマッチボーナス係数
        self._add_input_field(
            key=config_service.Keys.GA_MISMATCH_BONUS,
            label="アンマッチボーナス係数",
            description="アンマッチ時のボーナス係数（1.0-5.0）",
            field_type="number",
            placeholder="1.5"
        )
        
        # 保存ボタン
        self._add_save_button()
    
    def _load_system_settings(self):
        """システム設定を読み込み"""
        self._add_section_title("システム設定")
        
        # 会計年度
        self._add_input_field(
            key=config_service.Keys.FISCAL_YEAR,
            label="会計年度",
            description="現在の会計年度",
            field_type="number",
            placeholder="2025"
        )
        
        # ログレベル
        self._add_input_field(
            key=config_service.Keys.LOG_LEVEL,
            label="ログレベル",
            description="ログレベル（DEBUG/INFO/WARNING/ERROR/CRITICAL）",
            field_type="select",
            options=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        )
        
        # 保存ボタン
        self._add_save_button()
    
    def _add_section_title(self, title: str, top_padding: bool = False):
        """セクションタイトルを追加"""
        padding_top = Spacing.PADDING_LARGE * 2 if top_padding else Spacing.PADDING_LARGE
        
        title_label = ctk.CTkLabel(
            self.content_frame,
            text=title,
            font=(Fonts.FAMILY, Fonts.SUBTITLE, Fonts.BOLD),
            text_color=Colors.TEXT_PRIMARY,
            anchor="w"
        )
        title_label.pack(fill="x", pady=(padding_top, Spacing.PADDING_SMALL))
        
        separator = ctk.CTkFrame(
            self.content_frame,
            fg_color=Colors.PRIMARY,
            height=3
        )
        separator.pack(fill="x", pady=(0, Spacing.PADDING_MEDIUM))
    
    def _add_input_field(
        self,
        key: str,
        label: str,
        description: str,
        field_type: str = "text",
        placeholder: str = "",
        options: list = None
    ):
        """入力フィールドを追加"""
        container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        container.pack(fill="x", pady=Spacing.PADDING_SMALL)
        
        # ラベル
        label_widget = ctk.CTkLabel(
            container,
            text=label,
            font=(Fonts.FAMILY, Fonts.BODY, Fonts.BOLD),
            text_color=Colors.TEXT_PRIMARY,
            anchor="w"
        )
        label_widget.pack(fill="x")
        
        # 説明
        desc_label = ctk.CTkLabel(
            container,
            text=description,
            font=(Fonts.FAMILY, Fonts.SMALL),
            text_color=Colors.TEXT_SECONDARY,
            anchor="w"
        )
        desc_label.pack(fill="x", pady=(2, 4))
        
        # 現在の値を取得
        current_value = config_service.get(key, "")
        
        # 入力ウィジェット
        if field_type == "select":
            widget = ctk.CTkComboBox(
                container,
                values=options or [],
                font=(Fonts.FAMILY, Fonts.BODY),
                height=40
            )
            if current_value:
                widget.set(current_value)
        else:
            widget = ctk.CTkEntry(
                container,
                font=(Fonts.FAMILY, Fonts.BODY),
                placeholder_text=placeholder,
                height=40
            )
            if current_value:
                widget.insert(0, current_value)
        
        widget.pack(fill="x", pady=(0, Spacing.PADDING_MEDIUM))
        self.input_widgets[key] = widget
    
    def _add_save_button(self):
        """保存ボタンを追加"""
        button_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(Spacing.PADDING_LARGE, Spacing.PADDING_MEDIUM))
        
        save_btn = ctk.CTkButton(
            button_frame,
            text="💾 保存",
            font=(Fonts.FAMILY, Fonts.BODY, Fonts.BOLD),
            fg_color=Colors.PRIMARY,
            hover_color=Colors.PRIMARY_HOVER,
            width=200,
            height=45,
            command=self._on_save
        )
        save_btn.pack(side="right")
    
    def _on_save(self):
        """保存ボタンクリック時"""
        logger.info(f"Saving {self.current_tab} settings...")
        
        errors = []
        success_count = 0
        
        for key, widget in self.input_widgets.items():
            # 値を取得
            if isinstance(widget, ctk.CTkComboBox):
                value = widget.get()
            else:
                value = widget.get().strip()
            
            if not value:
                continue
            
            # バリデーション付きで保存
            try:
                config_service.validate_and_set(key, value)
                success_count += 1
                logger.info(f"Saved: {key} = {value}")
            except ValidationException as e:
                errors.append(f"{key}: {str(e)}")
                logger.warning(f"Validation failed for {key}: {e}")
            except Exception as e:
                errors.append(f"{key}: 保存に失敗しました")
                logger.error(f"Failed to save {key}: {e}")
        
        # 結果表示
        if errors:
            error_msg = "\n".join(errors)
            self._show_error(f"以下の設定の保存に失敗しました:\n\n{error_msg}")
        else:
            self._show_success(f"{success_count}件の設定を保存しました")
    
    def _show_success(self, message: str):
        """成功メッセージを表示"""
        dialog = ctk.CTkInputDialog(
            text=f"✅ {message}",
            title="保存成功"
        )
        dialog.get_input()
        logger.info(f"Success: {message}")
    
    def _show_error(self, message: str):
        """エラーメッセージを表示"""
        dialog = ctk.CTkInputDialog(
            text=f"❌ {message}",
            title="保存エラー"
        )
        dialog.get_input()
        logger.error(f"Error: {message}")
