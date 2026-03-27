"""
メインウィンドウ
アプリケーションのメインUI
"""
import customtkinter as ctk
from config.constants import Colors, Fonts, WindowSize
from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class MainWindow(ctk.CTk):
    """メインウィンドウクラス"""
    
    def __init__(self):
        super().__init__()
        
        # ウィンドウ設定
        self.title("🏥 医局業務管理システム")
        self.geometry(f"{WindowSize.DEFAULT_WIDTH}x{WindowSize.DEFAULT_HEIGHT}")
        self.minsize(WindowSize.MIN_WIDTH, WindowSize.MIN_HEIGHT)
        
        # テーマ設定
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # 現在のタブ
        self.current_tab = "dashboard"
        
        # UI構築
        self._create_title_bar()
        self._create_tab_bar()
        self._create_content_area()
        self._create_footer_bar()
        
        logger.info("Main window initialized")
    
    def _create_title_bar(self):
        """タイトルバーを作成"""
        self.title_frame = ctk.CTkFrame(
            self,
            height=WindowSize.TITLEBAR_HEIGHT,
            fg_color=Colors.GRADIENT_START,
            corner_radius=0
        )
        self.title_frame.pack(fill="x", side="top")
        self.title_frame.pack_propagate(False)
        
        # タイトル
        title_label = ctk.CTkLabel(
            self.title_frame,
            text="🏥 医局業務管理システム",
            font=(Fonts.FAMILY, Fonts.SUBTITLE, Fonts.BOLD),
            text_color=Colors.TEXT_WHITE
        )
        title_label.pack(side="left", padx=20)
        
        # ユーザー情報
        user_info = ctk.CTkLabel(
            self.title_frame,
            text=f"医局長 | {settings.fiscal_year}年度",
            font=(Fonts.FAMILY, Fonts.BODY),
            text_color=Colors.TEXT_WHITE
        )
        user_info.pack(side="right", padx=20)
    
    def _create_tab_bar(self):
        """タブバーを作成"""
        self.tab_frame = ctk.CTkFrame(
            self,
            height=WindowSize.TABBAR_HEIGHT,
            fg_color=Colors.DARK_GRAY,
            corner_radius=0
        )
        self.tab_frame.pack(fill="x", side="top")
        self.tab_frame.pack_propagate(False)
        
        # タブ定義
        self.tabs = [
            ("dashboard", "📊 ダッシュボード"),
            ("personnel", "👥 人事管理"),
            ("outpatient", "🏥 外勤管理"),
            ("mail", "✉️ メール"),
            ("document", "📄 書類"),
            ("settings", "⚙️ 設定"),
        ]
        
        # タブボタンを作成
        self.tab_buttons = {}
        for tab_id, tab_label in self.tabs:
            btn = ctk.CTkButton(
                self.tab_frame,
                text=tab_label,
                font=(Fonts.FAMILY, Fonts.CAPTION),
                fg_color=Colors.DARK_GRAY,
                hover_color=Colors.MEDIUM_GRAY,
                corner_radius=0,
                command=lambda t=tab_id: self._switch_tab(t)
            )
            btn.pack(side="left", fill="both", expand=True)
            self.tab_buttons[tab_id] = btn
        
        # 初期タブをアクティブ化
        self._update_tab_appearance()
    
    def _create_content_area(self):
        """コンテンツエリアを作成"""
        self.content_frame = ctk.CTkFrame(
            self,
            fg_color=Colors.BG_MAIN,
            corner_radius=0
        )
        self.content_frame.pack(fill="both", expand=True, side="top")
        
        # 初期表示（ダッシュボード）
        self._load_tab_content(self.current_tab)
    
    def _create_footer_bar(self):
        """フッターバーを作成"""
        self.footer_frame = ctk.CTkFrame(
            self,
            height=WindowSize.FOOTER_HEIGHT,
            fg_color=Colors.LIGHT_GRAY,
            corner_radius=0
        )
        self.footer_frame.pack(fill="x", side="bottom")
        self.footer_frame.pack_propagate(False)
        
        # ステータスインジケーター
        status_frame = ctk.CTkFrame(
            self.footer_frame,
            fg_color="transparent"
        )
        status_frame.pack(side="left", padx=20)
        
        status_label = ctk.CTkLabel(
            status_frame,
            text="🟢 システム正常動作中",
            font=(Fonts.FAMILY, Fonts.SMALL),
            text_color=Colors.TEXT_SECONDARY
        )
        status_label.pack(side="left")
        
        # 右側情報
        info_frame = ctk.CTkFrame(
            self.footer_frame,
            fg_color="transparent"
        )
        info_frame.pack(side="right", padx=20)
        
        db_label = ctk.CTkLabel(
            info_frame,
            text="DB: 接続済み",
            font=(Fonts.FAMILY, Fonts.SMALL),
            text_color=Colors.TEXT_SECONDARY
        )
        db_label.pack(side="left", padx=10)
        
        llm_label = ctk.CTkLabel(
            info_frame,
            text=f"LLM: {settings.ollama_model}",
            font=(Fonts.FAMILY, Fonts.SMALL),
            text_color=Colors.TEXT_SECONDARY
        )
        llm_label.pack(side="left", padx=10)
    
    def _switch_tab(self, tab_id: str):
        """
        タブを切り替え
        
        Args:
            tab_id: タブID
        """
        logger.info(f"Switching to tab: {tab_id}")
        self.current_tab = tab_id
        self._update_tab_appearance()
        self._load_tab_content(tab_id)
    
    def _update_tab_appearance(self):
        """タブの見た目を更新"""
        for tab_id, btn in self.tab_buttons.items():
            if tab_id == self.current_tab:
                # アクティブタブ
                btn.configure(
                    fg_color=Colors.PRIMARY,
                    text_color=Colors.TEXT_WHITE
                )
            else:
                # 非アクティブタブ
                btn.configure(
                    fg_color=Colors.DARK_GRAY,
                    text_color=Colors.LIGHT_GRAY
                )
    
    def _load_tab_content(self, tab_id: str):
        """
        タブのコンテンツを読み込み
        
        Args:
            tab_id: タブID
        """
        # 現在のコンテンツをクリア
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # タブ別のコンテンツを読み込み
        if tab_id == "dashboard":
            self._load_dashboard()
        elif tab_id == "personnel":
            self._load_personnel()
        elif tab_id == "outpatient":
            self._load_placeholder("🏥 外勤管理")
        elif tab_id == "mail":
            self._load_mail()
        elif tab_id == "document":
            self._load_document()
        elif tab_id == "settings":
            self._load_settings()
        else:
            self._load_placeholder(tab_id)
    
    def _load_dashboard(self):
        """ダッシュボードを読み込み"""
        from ui.dashboard.dashboard_view import DashboardView
        
        view = DashboardView(self.content_frame)
        view.pack(fill="both", expand=True)
        
        logger.info("Dashboard view loaded")
    
    def _load_personnel(self):
        """人事管理画面を読み込み"""
        from ui.personnel.personnel_view import PersonnelView
        
        view = PersonnelView(self.content_frame)
        view.pack(fill="both", expand=True)
        
        logger.info("Personnel management view loaded")
    
    def _load_mail(self):
        """メール管理画面を読み込み"""
        from ui.mail.mail_view import MailView

        view = MailView(self.content_frame)
        view.pack(fill="both", expand=True)

        logger.info("Mail view loaded")

    def _load_document(self):
        """書類管理画面を読み込み"""
        from ui.document.document_view import DocumentView

        view = DocumentView(self.content_frame)
        view.pack(fill="both", expand=True)

        logger.info("Document view loaded")

    def _load_settings(self):
        """設定画面を読み込み"""
        from ui.settings.settings_view import SettingsView

        view = SettingsView(self.content_frame)
        view.pack(fill="both", expand=True)

        logger.info("Settings view loaded")
    
    def _load_placeholder(self, title: str):
        """
        プレースホルダーを表示
        
        Args:
            title: タイトル
        """
        placeholder = ctk.CTkLabel(
            self.content_frame,
            text=f"{title}画面\n\n実装予定",
            font=(Fonts.FAMILY, Fonts.TITLE),
            text_color=Colors.TEXT_SECONDARY
        )
        placeholder.pack(expand=True)
    
    def run(self):
        """アプリケーションを実行"""
        logger.info("Starting main window")
        self.mainloop()


# 開発用: 単体テスト
if __name__ == "__main__":
    app = MainWindow()
    app.run()