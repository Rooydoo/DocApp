"""
病院管理画面 - 一覧表示
"""
import customtkinter as ctk
from typing import Optional
from config.constants import Colors, Fonts, Spacing
from ui.components import ScrollableTable, TableColumn, FormDialog, FormField, FieldType
from database.connection import get_db_session
from repositories.hospital_repository import HospitalRepository
from database.models.hospital import Hospital
from utils.logger import get_logger
from utils.exceptions import RecordNotFoundException

logger = get_logger(__name__)


class HospitalListView(ctk.CTkFrame):
    """
    病院管理画面
    
    機能:
    - 病院一覧表示
    - 検索・フィルター
    - 新規登録
    - 編集
    - 削除
    """
    
    def __init__(self, parent):
        super().__init__(parent, fg_color=Colors.BG_MAIN)
        
        self.selected_hospital: Optional[Hospital] = None
        
        # UI構築
        self._create_header()
        self._create_content()
        
        # 初期データ読み込み
        self.load_data()
        
        logger.info("HospitalListView initialized")
    
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
            text="🏥 病院管理",
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
            command=self._on_add_hospital
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
            placeholder_text="病院名、住所、院長名で検索",
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
        
        # メインコンテンツ（左:一覧、右:詳細）
        main_frame = ctk.CTkFrame(
            content_frame,
            fg_color="transparent"
        )
        main_frame.pack(fill="both", expand=True)
        
        # 左側: テーブル表示（40%）
        table_container = ctk.CTkFrame(
            main_frame,
            fg_color=Colors.BG_CARD,
            corner_radius=Spacing.RADIUS_CARD
        )
        table_container.pack(side="left", fill="both", expand=True, padx=(0, Spacing.PADDING_SMALL))
        
        # テーブル定義
        columns = [
            TableColumn("id", "ID", width=50, min_width=40, sortable=True),
            TableColumn("name", "病院名", width=160, min_width=100, sortable=True),
            TableColumn("director_name", "院長名", width=100, min_width=80, sortable=True),
            TableColumn("address", "住所", width=200, min_width=100, sortable=True),
            TableColumn("resident_capacity", "専攻医", width=60, min_width=50, sortable=True),
            TableColumn("specialist_capacity", "専門医", width=60, min_width=50, sortable=True),
            TableColumn("instructor_capacity", "指導医", width=60, min_width=50, sortable=True),
            TableColumn(
                "outpatient_flag",
                "外勤",
                width=50,
                min_width=40,
                sortable=True,
                formatter=lambda x: "✓" if x else ""
            ),
        ]
        
        self.table = ScrollableTable(table_container, columns=columns)
        self.table.pack(fill="both", expand=True, padx=Spacing.PADDING_SMALL, pady=Spacing.PADDING_SMALL)
        self.table.on_row_select(self._on_row_select)
        
        # 右側: 詳細表示（60%）
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
            text="👈 左側のリストから\n病院を選択してください",
            font=(Fonts.FAMILY, Fonts.BODY),
            text_color=Colors.TEXT_SECONDARY
        )
        placeholder.pack(expand=True)
    
    def _show_detail(self, hospital: Hospital):
        """
        詳細情報を表示
        
        Args:
            hospital: 病院インスタンス
        """
        for widget in self.detail_frame.winfo_children():
            widget.destroy()
        
        # 基本情報
        self._add_detail_section("基本情報")
        self._add_detail_field("病院名", hospital.name)
        self._add_detail_field("院長名", hospital.director_name or "未設定")
        self._add_detail_field("住所", hospital.address)
        
        # 受入情報
        self._add_detail_section("受入情報")
        self._add_detail_field("専攻医受入人数", f"{hospital.resident_capacity}名")
        self._add_detail_field("専門医受入人数", f"{hospital.specialist_capacity}名")
        self._add_detail_field("指導医受入人数", f"{hospital.instructor_capacity}名")
        self._add_detail_field("合計受入人数", f"{hospital.total_capacity}名")
        self._add_detail_field("ローテーション期間", f"{hospital.rotation_months or '未設定'}ヶ月")
        self._add_detail_field("年収", f"¥{hospital.annual_salary:,.0f}" if hospital.annual_salary else "未設定")
        
        # フラグ
        self._add_detail_section("設定")
        self._add_detail_field("外勤対象", "✓ はい" if hospital.outpatient_flag else "✗ いいえ")
        
        # 備考
        if hospital.notes:
            self._add_detail_section("備考")
            notes_label = ctk.CTkLabel(
                self.detail_frame,
                text=hospital.notes,
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
            command=lambda: self._on_edit_hospital(hospital)
        )
        edit_btn.pack(side="left", padx=(0, Spacing.PADDING_SMALL))
        
        delete_btn = ctk.CTkButton(
            button_frame,
            text="🗑️ 削除",
            font=(Fonts.FAMILY, Fonts.BODY),
            fg_color=Colors.ERROR,
            hover_color="#c0392b",
            width=120,
            height=40,
            command=lambda: self._on_delete_hospital(hospital)
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
    
    def load_data(self, keyword: Optional[str] = None):
        """
        データを読み込み
        
        Args:
            keyword: 検索キーワード（省略時は全件取得）
        """
        try:
            with get_db_session() as db:
                repo = HospitalRepository(db)
                
                if keyword:
                    hospitals = repo.search_by_keyword(keyword)
                    logger.info(f"Searched hospitals: {len(hospitals)} results for '{keyword}'")
                else:
                    hospitals = repo.get_all()
                    logger.info(f"Loaded hospitals: {len(hospitals)} records")
                
                self.table.set_data(hospitals)
        
        except Exception as e:
            logger.error(f"Failed to load hospitals: {e}")
            self._show_error("データの読み込みに失敗しました")
    
    def _on_search(self):
        """検索実行"""
        keyword = self.search_entry.get().strip()
        if keyword:
            self.load_data(keyword=keyword)
        else:
            self.load_data()
    
    def _on_clear_search(self):
        """検索クリア"""
        self.search_entry.delete(0, "end")
        self.load_data()
        self._show_detail_placeholder()
    
    def _on_row_select(self, hospital: Hospital):
        """
        行選択時の処理
        
        Args:
            hospital: 選択された病院
        """
        self.selected_hospital = hospital
        self._show_detail(hospital)
        logger.debug(f"Hospital selected: {hospital.name}")
    
    def _on_add_hospital(self):
        """新規登録ボタンクリック"""
        from ui.personnel.hospital.hospital_form_dialog import HospitalFormDialog
        
        dialog = HospitalFormDialog(self, mode="create")
        dialog.on_submit(self._on_form_submit)
    
    def _on_edit_hospital(self, hospital: Hospital):
        """
        編集ボタンクリック
        
        Args:
            hospital: 編集する病院
        """
        from ui.personnel.hospital.hospital_form_dialog import HospitalFormDialog
        
        dialog = HospitalFormDialog(self, mode="edit", hospital=hospital)
        dialog.on_submit(self._on_form_submit)
    
    def _on_delete_hospital(self, hospital: Hospital):
        """
        削除ボタンクリック
        
        Args:
            hospital: 削除する病院
        """
        # 確認ダイアログ
        dialog = ctk.CTkInputDialog(
            text=f"本当に「{hospital.name}」を削除しますか？\n\n確認のため「削除」と入力してください:",
            title="削除確認"
        )
        
        confirmation = dialog.get_input()
        
        if confirmation == "削除":
            try:
                with get_db_session() as db:
                    repo = HospitalRepository(db)
                    repo.delete(hospital.id)
                
                logger.info(f"Hospital deleted: {hospital.name}")
                self._show_success(f"「{hospital.name}」を削除しました")
                
                # データ再読み込み
                self.load_data()
                self._show_detail_placeholder()
            
            except Exception as e:
                logger.error(f"Failed to delete hospital: {e}")
                self._show_error("削除に失敗しました")
        else:
            logger.debug("Hospital deletion cancelled")
    
    def _on_form_submit(self, values: dict):
        """
        フォーム送信時の処理
        
        Args:
            values: フォーム入力値
        """
        # データ再読み込み
        self.load_data()
        
        # 成功メッセージは不要（ダイアログ側で表示）
        logger.info("Hospital form submitted successfully")
    
    def _show_success(self, message: str):
        """成功メッセージを表示"""
        # TODO: トーストメッセージ実装
        logger.info(f"Success: {message}")
    
    def _show_error(self, message: str):
        """エラーメッセージを表示"""
        # TODO: エラーダイアログ実装
        logger.error(f"Error: {message}")