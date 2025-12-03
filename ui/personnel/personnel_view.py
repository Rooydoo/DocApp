"""
人事管理メイン画面
病院管理と職員管理のタブ切り替え
"""
import customtkinter as ctk
from config.constants import Colors, Fonts, Spacing
from ui.personnel.hospital import HospitalListView
from ui.personnel.staff import StaffListView
from ui.personnel.survey import SurveyView
from utils.logger import get_logger

logger = get_logger(__name__)


class PersonnelView(ctk.CTkFrame):
    """
    人事管理メイン画面

    サブタブ:
    - 病院管理
    - 職員管理
    - 希望調査
    """
    
    def __init__(self, parent):
        super().__init__(parent, fg_color=Colors.BG_MAIN)
        
        self.current_tab = "hospital"
        
        # UI構築
        self._create_tab_bar()
        self._create_content_area()
        
        # 初期タブ表示
        self._load_tab_content(self.current_tab)
        
        logger.info("PersonnelView initialized")
    
    def _create_tab_bar(self):
        """サブタブバーを作成"""
        tab_frame = ctk.CTkFrame(
            self,
            fg_color=Colors.MEDIUM_GRAY,
            height=50
        )
        tab_frame.pack(fill="x", padx=0, pady=0)
        tab_frame.pack_propagate(False)
        
        # タブ定義
        self.tabs = [
            ("hospital", "🏥 病院管理"),
            ("staff", "👥 職員管理"),
            ("survey", "📊 希望調査"),
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
        self.content_frame = ctk.CTkFrame(
            self,
            fg_color=Colors.BG_MAIN
        )
        self.content_frame.pack(fill="both", expand=True, padx=0, pady=0)
    
    def _switch_tab(self, tab_id: str):
        """
        タブを切り替え
        
        Args:
            tab_id: タブID
        """
        logger.info(f"Switching to personnel sub-tab: {tab_id}")
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
                    fg_color=Colors.MEDIUM_GRAY,
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
        if tab_id == "hospital":
            view = HospitalListView(self.content_frame)
            view.pack(fill="both", expand=True)
            logger.info("Hospital management view loaded")

        elif tab_id == "staff":
            view = StaffListView(self.content_frame)
            view.pack(fill="both", expand=True)
            logger.info("Staff management view loaded")

        elif tab_id == "survey":
            view = SurveyView(self.content_frame)
            view.pack(fill="both", expand=True)
            logger.info("Survey management view loaded")
