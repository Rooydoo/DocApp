"""
設定画面
API設定、GA設定、システム設定、評価要素を管理
"""
import customtkinter as ctk
from typing import Dict, Any, Optional
from config.constants import Colors, Fonts, Spacing, FactorType
from services.config_service import config_service
from database.base import SessionLocal
from database.models.evaluation_factor import EvaluationFactor
from repositories.evaluation_factor_repository import EvaluationFactorRepository
from utils.logger import get_logger
from utils.exceptions import ValidationException, DuplicateRecordException

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
            ("factors", "📊 評価要素"),
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
        elif tab_id == "factors":
            self._load_factors_settings()
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

        # Google Sheets認証情報パス
        self._add_input_field(
            key=config_service.Keys.GOOGLE_SHEETS_CREDENTIALS_PATH,
            label="Google Sheets API認証情報パス",
            description="スプレッドシート集計出力用のcredentials.jsonファイルのパス",
            field_type="text",
            placeholder="credentials/sheets_credentials.json"
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

    # ===== 評価要素管理 =====

    def _load_factors_settings(self):
        """評価要素設定を読み込み"""
        # 専攻医重視要素セクション
        self._add_section_title("専攻医重視要素")
        self._add_factor_description(
            "専攻医が配属先を選ぶ際に重視する要素です。\n"
            "各専攻医は合計100ポイントをこれらの要素に配分します。"
        )
        self._add_factor_add_button(FactorType.STAFF_PREFERENCE)
        self._load_factor_list(FactorType.STAFF_PREFERENCE)

        # 医局側評価要素セクション
        self._add_section_title("医局側評価要素", top_padding=True)
        self._add_factor_description(
            "医局側が各専攻医を評価する際に使用する要素です。\n"
            "各要素に対して0.0〜1.0の評価値を設定します。"
        )
        self._add_factor_add_button(FactorType.ADMIN_EVALUATION)
        self._load_factor_list(FactorType.ADMIN_EVALUATION)

    def _add_factor_description(self, text: str):
        """要素の説明を追加"""
        desc_label = ctk.CTkLabel(
            self.content_frame,
            text=text,
            font=(Fonts.FAMILY, Fonts.SMALL),
            text_color=Colors.TEXT_SECONDARY,
            anchor="w",
            justify="left"
        )
        desc_label.pack(fill="x", pady=(0, Spacing.PADDING_MEDIUM))

    def _add_factor_add_button(self, factor_type: str):
        """要素追加ボタンを追加"""
        btn_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(0, Spacing.PADDING_SMALL))

        add_btn = ctk.CTkButton(
            btn_frame,
            text="➕ 新規要素を追加",
            font=(Fonts.FAMILY, Fonts.BODY),
            fg_color=Colors.SUCCESS,
            hover_color="#219a52",
            width=180,
            height=36,
            command=lambda: self._show_factor_dialog(None, factor_type)
        )
        add_btn.pack(side="left")

    def _load_factor_list(self, factor_type: str):
        """評価要素リストを表示"""
        with SessionLocal() as db:
            repo = EvaluationFactorRepository(db)
            factors = repo.get_by_type(factor_type)

        if not factors:
            no_data_label = ctk.CTkLabel(
                self.content_frame,
                text="登録されている要素はありません",
                font=(Fonts.FAMILY, Fonts.BODY),
                text_color=Colors.TEXT_SECONDARY,
            )
            no_data_label.pack(pady=Spacing.PADDING_MEDIUM)
            return

        # 要素リスト
        for factor in factors:
            self._create_factor_row(factor)

    def _create_factor_row(self, factor: EvaluationFactor):
        """評価要素の行を作成"""
        row_frame = ctk.CTkFrame(
            self.content_frame,
            fg_color=Colors.BG_MAIN,
            corner_radius=Spacing.RADIUS_CARD
        )
        row_frame.pack(fill="x", pady=4)

        # 左側: 要素情報
        info_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=Spacing.PADDING_MEDIUM, pady=Spacing.PADDING_SMALL)

        # 要素名
        name_label = ctk.CTkLabel(
            info_frame,
            text=factor.name,
            font=(Fonts.FAMILY, Fonts.BODY, Fonts.BOLD),
            text_color=Colors.TEXT_PRIMARY,
            anchor="w"
        )
        name_label.pack(fill="x")

        # 説明
        if factor.description:
            desc_label = ctk.CTkLabel(
                info_frame,
                text=factor.description,
                font=(Fonts.FAMILY, Fonts.SMALL),
                text_color=Colors.TEXT_SECONDARY,
                anchor="w"
            )
            desc_label.pack(fill="x")

        # ステータス
        status_text = "✓ 有効" if factor.is_active else "✗ 無効"
        status_color = Colors.SUCCESS if factor.is_active else Colors.TEXT_SECONDARY
        status_label = ctk.CTkLabel(
            info_frame,
            text=status_text,
            font=(Fonts.FAMILY, Fonts.SMALL),
            text_color=status_color,
            anchor="w"
        )
        status_label.pack(fill="x")

        # 右側: アクションボタン
        btn_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        btn_frame.pack(side="right", padx=Spacing.PADDING_MEDIUM, pady=Spacing.PADDING_SMALL)

        # 編集ボタン
        edit_btn = ctk.CTkButton(
            btn_frame,
            text="✏️",
            font=(Fonts.FAMILY, Fonts.BODY),
            fg_color=Colors.INFO,
            hover_color=Colors.PRIMARY_HOVER,
            width=40,
            height=32,
            command=lambda: self._show_factor_dialog(factor.id, factor.factor_type)
        )
        edit_btn.pack(side="left", padx=2)

        # 有効/無効切り替えボタン
        toggle_text = "🚫" if factor.is_active else "✓"
        toggle_btn = ctk.CTkButton(
            btn_frame,
            text=toggle_text,
            font=(Fonts.FAMILY, Fonts.BODY),
            fg_color=Colors.WARNING if factor.is_active else Colors.SUCCESS,
            hover_color="#c78c0a" if factor.is_active else "#219a52",
            width=40,
            height=32,
            command=lambda fid=factor.id: self._toggle_factor(fid)
        )
        toggle_btn.pack(side="left", padx=2)

        # 削除ボタン
        delete_btn = ctk.CTkButton(
            btn_frame,
            text="🗑️",
            font=(Fonts.FAMILY, Fonts.BODY),
            fg_color=Colors.ERROR,
            hover_color="#c0392b",
            width=40,
            height=32,
            command=lambda fid=factor.id: self._delete_factor(fid)
        )
        delete_btn.pack(side="left", padx=2)

    def _show_factor_dialog(self, factor_id: Optional[int], factor_type: str):
        """評価要素の追加/編集ダイアログを表示"""
        dialog = FactorEditDialog(
            self,
            factor_id=factor_id,
            factor_type=factor_type,
            on_save=lambda: self._load_tab_content("factors")
        )
        dialog.grab_set()

    def _toggle_factor(self, factor_id: int):
        """評価要素の有効/無効を切り替え"""
        try:
            with SessionLocal() as db:
                repo = EvaluationFactorRepository(db)
                repo.toggle_active(factor_id)
            self._load_tab_content("factors")
            logger.info(f"Toggled factor {factor_id}")
        except Exception as e:
            self._show_error(f"切り替えに失敗しました: {str(e)}")
            logger.error(f"Failed to toggle factor {factor_id}: {e}")

    def _delete_factor(self, factor_id: int):
        """評価要素を削除"""
        # 確認ダイアログ
        confirm = ctk.CTkInputDialog(
            text="この評価要素を削除しますか？\n関連するデータも削除されます。\n\n削除する場合は「削除」と入力してください。",
            title="削除確認"
        )
        result = confirm.get_input()

        if result == "削除":
            try:
                with SessionLocal() as db:
                    repo = EvaluationFactorRepository(db)
                    repo.delete(factor_id)
                self._load_tab_content("factors")
                logger.info(f"Deleted factor {factor_id}")
            except Exception as e:
                self._show_error(f"削除に失敗しました: {str(e)}")
                logger.error(f"Failed to delete factor {factor_id}: {e}")


class FactorEditDialog(ctk.CTkToplevel):
    """評価要素編集ダイアログ"""

    def __init__(
        self,
        parent,
        factor_id: Optional[int],
        factor_type: str,
        on_save: callable
    ):
        super().__init__(parent)

        self.factor_id = factor_id
        self.factor_type = factor_type
        self.on_save = on_save
        self.factor: Optional[EvaluationFactor] = None

        # ダイアログ設定
        self.title("評価要素の編集" if factor_id else "新規評価要素")
        self.geometry("500x400")
        self.resizable(False, False)

        # 既存データを読み込み
        if factor_id:
            with SessionLocal() as db:
                repo = EvaluationFactorRepository(db)
                self.factor = repo.get(factor_id)

        self._create_form()

    def _create_form(self):
        """フォームを作成"""
        main_frame = ctk.CTkFrame(self, fg_color=Colors.BG_MAIN)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # タイプ表示
        type_name = FactorType.display_name(self.factor_type)
        type_label = ctk.CTkLabel(
            main_frame,
            text=f"タイプ: {type_name}",
            font=(Fonts.FAMILY, Fonts.SMALL),
            text_color=Colors.TEXT_SECONDARY
        )
        type_label.pack(anchor="w", pady=(0, Spacing.PADDING_MEDIUM))

        # 要素名
        name_label = ctk.CTkLabel(
            main_frame,
            text="要素名 *",
            font=(Fonts.FAMILY, Fonts.BODY, Fonts.BOLD),
            text_color=Colors.TEXT_PRIMARY,
            anchor="w"
        )
        name_label.pack(fill="x")

        self.name_entry = ctk.CTkEntry(
            main_frame,
            font=(Fonts.FAMILY, Fonts.BODY),
            placeholder_text="例: 年収、通勤距離、学術実績",
            height=40
        )
        self.name_entry.pack(fill="x", pady=(4, Spacing.PADDING_MEDIUM))
        if self.factor:
            self.name_entry.insert(0, self.factor.name)

        # 説明
        desc_label = ctk.CTkLabel(
            main_frame,
            text="説明",
            font=(Fonts.FAMILY, Fonts.BODY, Fonts.BOLD),
            text_color=Colors.TEXT_PRIMARY,
            anchor="w"
        )
        desc_label.pack(fill="x")

        self.desc_entry = ctk.CTkTextbox(
            main_frame,
            font=(Fonts.FAMILY, Fonts.BODY),
            height=100
        )
        self.desc_entry.pack(fill="x", pady=(4, Spacing.PADDING_MEDIUM))
        if self.factor and self.factor.description:
            self.desc_entry.insert("1.0", self.factor.description)

        # 表示順序
        order_label = ctk.CTkLabel(
            main_frame,
            text="表示順序",
            font=(Fonts.FAMILY, Fonts.BODY, Fonts.BOLD),
            text_color=Colors.TEXT_PRIMARY,
            anchor="w"
        )
        order_label.pack(fill="x")

        self.order_entry = ctk.CTkEntry(
            main_frame,
            font=(Fonts.FAMILY, Fonts.BODY),
            placeholder_text="0",
            height=40
        )
        self.order_entry.pack(fill="x", pady=(4, Spacing.PADDING_MEDIUM))
        if self.factor:
            self.order_entry.insert(0, str(self.factor.display_order))

        # 有効フラグ
        self.active_var = ctk.BooleanVar(value=self.factor.is_active if self.factor else True)
        active_checkbox = ctk.CTkCheckBox(
            main_frame,
            text="有効",
            font=(Fonts.FAMILY, Fonts.BODY),
            variable=self.active_var
        )
        active_checkbox.pack(anchor="w", pady=Spacing.PADDING_MEDIUM)

        # ボタン
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(Spacing.PADDING_LARGE, 0))

        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="キャンセル",
            font=(Fonts.FAMILY, Fonts.BODY),
            fg_color=Colors.MEDIUM_GRAY,
            hover_color=Colors.DARK_GRAY,
            width=120,
            height=40,
            command=self.destroy
        )
        cancel_btn.pack(side="left")

        save_btn = ctk.CTkButton(
            btn_frame,
            text="💾 保存",
            font=(Fonts.FAMILY, Fonts.BODY, Fonts.BOLD),
            fg_color=Colors.PRIMARY,
            hover_color=Colors.PRIMARY_HOVER,
            width=120,
            height=40,
            command=self._on_save
        )
        save_btn.pack(side="right")

    def _on_save(self):
        """保存処理"""
        # バリデーション
        name = self.name_entry.get().strip()
        if not name:
            self._show_error("要素名を入力してください")
            return

        description = self.desc_entry.get("1.0", "end-1c").strip()

        try:
            display_order = int(self.order_entry.get().strip() or "0")
        except ValueError:
            self._show_error("表示順序は数値で入力してください")
            return

        is_active = self.active_var.get()

        # 保存
        try:
            with SessionLocal() as db:
                repo = EvaluationFactorRepository(db)

                data = {
                    "name": name,
                    "description": description,
                    "factor_type": self.factor_type,
                    "display_order": display_order,
                    "is_active": is_active
                }

                if self.factor_id:
                    repo.update(self.factor_id, data)
                else:
                    repo.create(data)

            logger.info(f"Saved factor: {name}")
            self.on_save()
            self.destroy()

        except DuplicateRecordException:
            self._show_error("同じ名前の要素が既に存在します")
        except Exception as e:
            self._show_error(f"保存に失敗しました: {str(e)}")
            logger.error(f"Failed to save factor: {e}")

    def _show_error(self, message: str):
        """エラーメッセージを表示"""
        error_dialog = ctk.CTkInputDialog(
            text=f"❌ {message}",
            title="エラー"
        )
        error_dialog.get_input()
