"""
職員管理画面 - 一覧表示
"""
import customtkinter as ctk
from typing import Optional
from config.constants import Colors, Fonts, Spacing, StaffType
from ui.components import ScrollableTable, TableColumn, FormDialog, FormField, FieldType
from database.connection import get_db_session
from repositories.staff_repository import StaffRepository
from database.models.staff import Staff
from utils.logger import get_logger
from utils.exceptions import RecordNotFoundException

logger = get_logger(__name__)


class StaffListView(ctk.CTkFrame):
    """
    職員管理画面
    
    機能:
    - 職員一覧表示
    - 検索・フィルター
    - 新規登録
    - 編集
    - 削除
    """
    
    def __init__(self, parent):
        super().__init__(parent, fg_color=Colors.BG_MAIN)
        
        self.selected_staff: Optional[Staff] = None
        
        # UI構築
        self._create_header()
        self._create_content()
        
        # 初期データ読み込み
        self.load_data()
        
        logger.info("StaffListView initialized")
    
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
            text="👥 職員管理",
            font=(Fonts.FAMILY, Fonts.TITLE, Fonts.BOLD),
            text_color=Colors.TEXT_PRIMARY,
            anchor="w"
        )
        title_label.pack(side="left", pady=Spacing.PADDING_MEDIUM)
        
        # 追加ボタン
        add_btn = ctk.CTkButton(
            header_frame,
            text="➕ 新規登録",
            font=(Fonts.FAMILY, Fonts.BODY, Fonts.BOLD),
            fg_color=Colors.PRIMARY,
            hover_color=Colors.PRIMARY_HOVER,
            width=140,
            height=40,
            command=self._on_add_staff
        )
        add_btn.pack(side="right", pady=Spacing.PADDING_MEDIUM)
    
    def _create_content(self):
        """コンテンツエリアを作成"""
        content_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        content_frame.pack(fill="both", expand=True, padx=Spacing.PADDING_LARGE, pady=Spacing.PADDING_MEDIUM)
        
        # 検索バー
        search_frame = ctk.CTkFrame(
            content_frame,
            fg_color="transparent",
            height=60
        )
        search_frame.pack(fill="x", pady=(0, Spacing.PADDING_MEDIUM))
        search_frame.pack_propagate(False)
        
        search_label = ctk.CTkLabel(
            search_frame,
            text="🔍 検索:",
            font=(Fonts.FAMILY, Fonts.BODY),
            text_color=Colors.TEXT_PRIMARY
        )
        search_label.pack(side="left", padx=(0, Spacing.PADDING_SMALL))
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="氏名、メールアドレスで検索",
            font=(Fonts.FAMILY, Fonts.BODY),
            width=300,
            height=40
        )
        self.search_entry.pack(side="left", padx=Spacing.PADDING_SMALL)
        self.search_entry.bind("<KeyRelease>", lambda e: self._on_search())
        
        search_btn = ctk.CTkButton(
            search_frame,
            text="検索",
            font=(Fonts.FAMILY, Fonts.BODY),
            fg_color=Colors.PRIMARY,
            hover_color=Colors.PRIMARY_HOVER,
            width=100,
            height=40,
            command=self._on_search
        )
        search_btn.pack(side="left", padx=Spacing.PADDING_SMALL)
        
        clear_btn = ctk.CTkButton(
            search_frame,
            text="クリア",
            font=(Fonts.FAMILY, Fonts.BODY),
            fg_color=Colors.MEDIUM_GRAY,
            hover_color=Colors.DARK_GRAY,
            width=100,
            height=40,
            command=self._on_clear_search
        )
        clear_btn.pack(side="left", padx=Spacing.PADDING_SMALL)
        
        # フィルター（職員種別）
        filter_label = ctk.CTkLabel(
            search_frame,
            text="種別:",
            font=(Fonts.FAMILY, Fonts.BODY),
            text_color=Colors.TEXT_PRIMARY
        )
        filter_label.pack(side="left", padx=(Spacing.PADDING_LARGE, Spacing.PADDING_SMALL))
        
        self.staff_type_filter = ctk.CTkComboBox(
            search_frame,
            values=["全て"] + StaffType.all(),
            font=(Fonts.FAMILY, Fonts.BODY),
            width=150,
            height=40,
            command=self._on_filter_change
        )
        self.staff_type_filter.set("全て")
        self.staff_type_filter.pack(side="left", padx=Spacing.PADDING_SMALL)
        
        # メインコンテンツ（左:一覧、右:詳細）
        main_frame = ctk.CTkFrame(
            content_frame,
            fg_color="transparent"
        )
        main_frame.pack(fill="both", expand=True)
        
        # 左側: テーブル表示
        table_container = ctk.CTkFrame(
            main_frame,
            fg_color=Colors.BG_CARD,
            corner_radius=Spacing.RADIUS_CARD
        )
        table_container.pack(side="left", fill="both", expand=True, padx=(0, Spacing.PADDING_SMALL))
        
        # テーブル定義
        columns = [
            TableColumn("id", "ID", width=50, min_width=40, sortable=True),
            TableColumn("name", "氏名", width=120, min_width=80, sortable=True),
            TableColumn("staff_type", "職員種別", width=100, min_width=80, sortable=True),
            TableColumn("email", "メールアドレス", width=200, min_width=120, sortable=True),
            TableColumn("phone", "電話番号", width=120, min_width=80, sortable=True),
            TableColumn("address", "住所", width=200, min_width=100, sortable=True),
        ]
        
        self.table = ScrollableTable(table_container, columns=columns)
        self.table.pack(fill="both", expand=True, padx=Spacing.PADDING_SMALL, pady=Spacing.PADDING_SMALL)
        self.table.on_row_select(self._on_row_select)
        
        # 右側: 詳細表示
        detail_container = ctk.CTkFrame(
            main_frame,
            fg_color=Colors.BG_CARD,
            corner_radius=Spacing.RADIUS_CARD
        )
        detail_container.pack(side="right", fill="both", expand=True, padx=(Spacing.PADDING_SMALL, 0))
        
        # 詳細ヘッダー
        detail_header = ctk.CTkFrame(
            detail_container,
            fg_color=Colors.DARK_GRAY,
            corner_radius=0,
            height=50
        )
        detail_header.pack(fill="x", padx=0, pady=0)
        detail_header.pack_propagate(False)
        
        detail_title = ctk.CTkLabel(
            detail_header,
            text="📋 詳細情報",
            font=(Fonts.FAMILY, Fonts.SUBTITLE, Fonts.BOLD),
            text_color=Colors.TEXT_WHITE
        )
        detail_title.pack(side="left", padx=Spacing.PADDING_MEDIUM, pady=Spacing.PADDING_SMALL)
        
        # 詳細コンテンツ
        self.detail_frame = ctk.CTkScrollableFrame(
            detail_container,
            fg_color="transparent"
        )
        self.detail_frame.pack(fill="both", expand=True, padx=Spacing.PADDING_MEDIUM, pady=Spacing.PADDING_MEDIUM)
        
        # 初期メッセージ
        self._show_detail_placeholder()
    
    def _show_detail_placeholder(self):
        """詳細エリアにプレースホルダーを表示"""
        for widget in self.detail_frame.winfo_children():
            widget.destroy()
        
        placeholder = ctk.CTkLabel(
            self.detail_frame,
            text="👈 左側のリストから\n職員を選択してください",
            font=(Fonts.FAMILY, Fonts.BODY),
            text_color=Colors.TEXT_SECONDARY
        )
        placeholder.pack(expand=True)
    
    def _show_detail(self, staff: Staff):
        """
        詳細情報を表示
        
        Args:
            staff: 職員インスタンス
        """
        for widget in self.detail_frame.winfo_children():
            widget.destroy()
        
        # 基本情報
        self._add_detail_section("基本情報")
        self._add_detail_field("氏名", staff.name)
        self._add_detail_field("職員種別", staff.staff_type)
        self._add_detail_field("メールアドレス", staff.email)
        self._add_detail_field("電話番号", staff.phone or "未設定")
        self._add_detail_field("住所", staff.address or "未設定")
        
        # 選考医専用情報
        if staff.is_resident_doctor:
            self._add_detail_section("選考医情報")
            self._add_detail_field("希望ローテーション期間", f"{staff.rotation_months or '未設定'}ヶ月")
        
        # 備考
        if staff.notes:
            self._add_detail_section("備考")
            notes_label = ctk.CTkLabel(
                self.detail_frame,
                text=staff.notes,
                font=(Fonts.FAMILY, Fonts.BODY),
                text_color=Colors.TEXT_PRIMARY,
                anchor="w",
                justify="left",
                wraplength=400
            )
            notes_label.pack(fill="x", pady=(0, Spacing.PADDING_MEDIUM))
        
        # アクションボタン
        button_frame = ctk.CTkFrame(
            self.detail_frame,
            fg_color="transparent"
        )
        button_frame.pack(fill="x", pady=(Spacing.PADDING_LARGE, 0))

        edit_btn = ctk.CTkButton(
            button_frame,
            text="✏️ 編集",
            font=(Fonts.FAMILY, Fonts.BODY, Fonts.BOLD),
            fg_color=Colors.PRIMARY,
            hover_color=Colors.PRIMARY_HOVER,
            width=120,
            height=40,
            command=lambda: self._on_edit_staff(staff)
        )
        edit_btn.pack(side="left", padx=(0, Spacing.PADDING_SMALL))

        # 専攻医の場合は希望・評価設定ボタンを表示
        if staff.is_resident_doctor:
            pref_btn = ctk.CTkButton(
                button_frame,
                text="📊 希望・評価",
                font=(Fonts.FAMILY, Fonts.BODY, Fonts.BOLD),
                fg_color=Colors.SUCCESS,
                hover_color="#219a52",
                width=140,
                height=40,
                command=lambda: self._on_preference_settings(staff)
            )
            pref_btn.pack(side="left", padx=(0, Spacing.PADDING_SMALL))

        delete_btn = ctk.CTkButton(
            button_frame,
            text="🗑️ 削除",
            font=(Fonts.FAMILY, Fonts.BODY),
            fg_color=Colors.ERROR,
            hover_color="#c0392b",
            width=120,
            height=40,
            command=lambda: self._on_delete_staff(staff)
        )
        delete_btn.pack(side="left")
    
    def _add_detail_section(self, title: str):
        """詳細セクションタイトルを追加"""
        section_label = ctk.CTkLabel(
            self.detail_frame,
            text=title,
            font=(Fonts.FAMILY, Fonts.SUBTITLE, Fonts.BOLD),
            text_color=Colors.TEXT_PRIMARY,
            anchor="w"
        )
        section_label.pack(fill="x", pady=(Spacing.PADDING_LARGE, Spacing.PADDING_SMALL))
        
        separator = ctk.CTkFrame(
            self.detail_frame,
            fg_color=Colors.LIGHT_GRAY,
            height=2
        )
        separator.pack(fill="x", pady=(0, Spacing.PADDING_SMALL))
    
    def _add_detail_field(self, label: str, value: str):
        """詳細フィールドを追加"""
        field_frame = ctk.CTkFrame(
            self.detail_frame,
            fg_color="transparent"
        )
        field_frame.pack(fill="x", pady=Spacing.PADDING_XSMALL)
        
        label_widget = ctk.CTkLabel(
            field_frame,
            text=f"{label}:",
            font=(Fonts.FAMILY, Fonts.BODY, Fonts.BOLD),
            text_color=Colors.TEXT_SECONDARY,
            anchor="w",
            width=150
        )
        label_widget.pack(side="left")
        
        value_widget = ctk.CTkLabel(
            field_frame,
            text=value,
            font=(Fonts.FAMILY, Fonts.BODY),
            text_color=Colors.TEXT_PRIMARY,
            anchor="w"
        )
        value_widget.pack(side="left", fill="x", expand=True)
    
    def load_data(self, keyword: Optional[str] = None, staff_type: Optional[str] = None):
        """
        データを読み込み
        
        Args:
            keyword: 検索キーワード（省略時は全件取得）
            staff_type: 職員種別フィルター
        """
        try:
            with get_db_session() as db:
                repo = StaffRepository(db)
                
                if keyword:
                    staff_list = repo.search_by_keyword(keyword)
                elif staff_type and staff_type != "全て":
                    staff_list = repo.get_by_staff_type(staff_type)
                else:
                    staff_list = repo.get_all()
                
                logger.info(f"Loaded staff: {len(staff_list)} records")
                self.table.set_data(staff_list)
        
        except Exception as e:
            logger.error(f"Failed to load staff: {e}")
            self._show_error("データの読み込みに失敗しました")
    
    def _on_search(self):
        """検索実行"""
        keyword = self.search_entry.get().strip()
        if keyword:
            self.load_data(keyword=keyword)
        else:
            staff_type = self.staff_type_filter.get()
            self.load_data(staff_type=staff_type)
    
    def _on_clear_search(self):
        """検索クリア"""
        self.search_entry.delete(0, "end")
        self.staff_type_filter.set("全て")
        self.load_data()
        self._show_detail_placeholder()
    
    def _on_filter_change(self, value):
        """フィルター変更時"""
        self.load_data(staff_type=value)
    
    def _on_row_select(self, staff: Staff):
        """
        行選択時の処理
        
        Args:
            staff: 選択された職員
        """
        self.selected_staff = staff
        self._show_detail(staff)
        logger.debug(f"Staff selected: {staff.name}")
    
    def _on_add_staff(self):
        """新規登録ボタンクリック"""
        from ui.personnel.staff.staff_form_dialog import StaffFormDialog
        
        dialog = StaffFormDialog(self, mode="create")
        dialog.on_submit(self._on_form_submit)
    
    def _on_edit_staff(self, staff: Staff):
        """
        編集ボタンクリック
        
        Args:
            staff: 編集する職員
        """
        from ui.personnel.staff.staff_form_dialog import StaffFormDialog
        
        dialog = StaffFormDialog(self, mode="edit", staff=staff)
        dialog.on_submit(self._on_form_submit)
    
    def _on_delete_staff(self, staff: Staff):
        """
        削除ボタンクリック
        
        Args:
            staff: 削除する職員
        """
        # 確認ダイアログ
        dialog = ctk.CTkInputDialog(
            text=f"本当に「{staff.name}」を削除しますか？\n\n確認のため「削除」と入力してください:",
            title="削除確認"
        )
        
        confirmation = dialog.get_input()
        
        if confirmation == "削除":
            try:
                with get_db_session() as db:
                    repo = StaffRepository(db)
                    repo.delete(staff.id)
                
                logger.info(f"Staff deleted: {staff.name}")
                self._show_success(f"「{staff.name}」を削除しました")
                
                # データ再読み込み
                self.load_data()
                self._show_detail_placeholder()
            
            except Exception as e:
                logger.error(f"Failed to delete staff: {e}")
                self._show_error("削除に失敗しました")
        else:
            logger.debug("Staff deletion cancelled")
    
    def _on_form_submit(self, values: dict):
        """
        フォーム送信時の処理
        
        Args:
            values: フォーム入力値
        """
        # データ再読み込み
        self.load_data()
        
        logger.info("Staff form submitted successfully")
    
    def _show_success(self, message: str):
        """成功メッセージを表示"""
        # TODO: トーストメッセージ実装
        logger.info(f"Success: {message}")
    
    def _show_error(self, message: str):
        """エラーメッセージを表示"""
        # TODO: エラーダイアログ実装
        logger.error(f"Error: {message}")

    def _on_preference_settings(self, staff: Staff):
        """
        希望・評価設定ボタンクリック

        Args:
            staff: 対象の職員
        """
        from ui.personnel.staff.staff_preference_dialog import StaffPreferenceDialog

        dialog = StaffPreferenceDialog(
            self,
            staff=staff,
            on_save=lambda: self._show_detail(staff)
        )
