"""
書類管理画面
スプレッドシート集計閲覧・書類作成・テンプレート管理を統合
"""
import customtkinter as ctk
from config.constants import Colors, Fonts, Spacing
from utils.logger import get_logger

logger = get_logger(__name__)


class DocumentView(ctk.CTkFrame):
    """
    書類管理画面

    サブタブ:
    - 質問項目集計（スプレッドシート）
    - 書類作成（将来実装）
    - テンプレート（将来実装）
    """

    def __init__(self, parent):
        super().__init__(parent, fg_color=Colors.BG_MAIN)

        self.current_tab = "survey"

        # UI構築
        self._create_header()
        self._create_tab_bar()
        self._create_content_area()

        # 初期タブ表示
        self._load_tab_content(self.current_tab)

        logger.info("DocumentView initialized")

    def _create_header(self):
        """ヘッダーを作成"""
        header_frame = ctk.CTkFrame(self, fg_color="transparent", height=60)
        header_frame.pack(fill="x", padx=Spacing.PADDING_LARGE, pady=(Spacing.PADDING_LARGE, 0))
        header_frame.pack_propagate(False)

        title_label = ctk.CTkLabel(
            header_frame,
            text="書類管理",
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

        self.tabs = [
            ("survey", "質問項目集計"),
            ("create", "書類作成"),
            ("template", "テンプレート"),
        ]

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

        self._update_tab_appearance()

    def _create_content_area(self):
        """コンテンツエリアを作成"""
        self.content_frame = ctk.CTkFrame(
            self,
            fg_color="transparent",
            corner_radius=0
        )
        self.content_frame.pack(fill="both", expand=True)

    def _switch_tab(self, tab_id: str):
        """タブを切り替え"""
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
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        if tab_id == "survey":
            self._load_survey_view()
        elif tab_id == "create":
            self._load_placeholder("書類作成")
        elif tab_id == "template":
            self._load_placeholder("テンプレート管理")

    def _load_survey_view(self):
        """質問項目集計画面を読み込み"""
        from ui.document.spreadsheet.survey_summary_view import SurveySummaryView

        view = SurveySummaryView(self.content_frame)
        view.pack(fill="both", expand=True)

    def _load_placeholder(self, title: str):
        """プレースホルダーを表示"""
        placeholder = ctk.CTkLabel(
            self.content_frame,
            text=f"{title}\n\n実装予定",
            font=(Fonts.FAMILY, Fonts.TITLE),
            text_color=Colors.TEXT_SECONDARY
        )
        placeholder.pack(expand=True)
