"""
書類管理画面

テンプレート管理と書類生成
"""
import customtkinter as ctk
from typing import Optional, List, Dict, Any
from tkinter import filedialog
import os
import subprocess
import platform
from datetime import datetime

from config.constants import Colors, Fonts, Spacing
from database.connection import get_db_session
from repositories.document_template_repository import DocumentTemplateRepository
from repositories.staff_repository import StaffRepository
from repositories.hospital_repository import HospitalRepository
from database.models.document_template import DocumentTemplate
from services.document_service import DocumentService, DocumentServiceException
from utils.logger import get_logger

logger = get_logger(__name__)


class DocumentView(ctk.CTkFrame):
    """
    書類管理画面

    機能:
    - テンプレート管理（アップロード・削除）
    - 書類生成（データ差し込み）
    - 生成履歴
    """

    def __init__(self, parent):
        super().__init__(parent, fg_color=Colors.BG_MAIN)

        self.selected_template: Optional[DocumentTemplate] = None
        self.document_service = DocumentService()

        # UI構築
        self._create_header()
        self._create_content()

        # データ読み込み
        self._load_templates()

        logger.info("DocumentView initialized")

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
            text="📄 書類管理",
            font=(Fonts.FAMILY, Fonts.TITLE, Fonts.BOLD),
            text_color=Colors.TEXT_PRIMARY,
            anchor="w"
        )
        title_label.pack(side="left", pady=Spacing.PADDING_MEDIUM)

        # テンプレート追加ボタン
        add_btn = ctk.CTkButton(
            header_frame,
            text="📁 テンプレート追加",
            font=(Fonts.FAMILY, Fonts.BODY, Fonts.BOLD),
            fg_color=Colors.PRIMARY,
            hover_color=Colors.PRIMARY_HOVER,
            width=180,
            height=40,
            command=self._on_add_template
        )
        add_btn.pack(side="right", pady=Spacing.PADDING_MEDIUM)

    def _create_content(self):
        """コンテンツエリアを作成"""
        content_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        content_frame.pack(fill="both", expand=True, padx=Spacing.PADDING_LARGE, pady=Spacing.PADDING_MEDIUM)

        # 左カラム: テンプレート一覧
        left_col = ctk.CTkFrame(
            content_frame,
            fg_color=Colors.BG_CARD,
            corner_radius=Spacing.RADIUS_CARD,
            width=350
        )
        left_col.pack(side="left", fill="y", padx=(0, Spacing.PADDING_SMALL))
        left_col.pack_propagate(False)

        self._create_template_list(left_col)

        # 右カラム: 書類生成
        right_col = ctk.CTkFrame(
            content_frame,
            fg_color=Colors.BG_CARD,
            corner_radius=Spacing.RADIUS_CARD
        )
        right_col.pack(side="right", fill="both", expand=True, padx=(Spacing.PADDING_SMALL, 0))

        self._create_generation_panel(right_col)

    def _create_template_list(self, parent):
        """テンプレート一覧を作成"""
        # ヘッダー
        header = ctk.CTkFrame(
            parent,
            fg_color=Colors.DARK_GRAY,
            corner_radius=0,
            height=50
        )
        header.pack(fill="x")
        header.pack_propagate(False)

        header_label = ctk.CTkLabel(
            header,
            text="📋 テンプレート一覧",
            font=(Fonts.FAMILY, Fonts.SUBTITLE, Fonts.BOLD),
            text_color=Colors.TEXT_WHITE
        )
        header_label.pack(side="left", padx=Spacing.PADDING_MEDIUM, pady=Spacing.PADDING_SMALL)

        # リストエリア
        self.template_list_frame = ctk.CTkScrollableFrame(
            parent,
            fg_color="transparent"
        )
        self.template_list_frame.pack(fill="both", expand=True, padx=Spacing.PADDING_SMALL, pady=Spacing.PADDING_SMALL)

    def _create_generation_panel(self, parent):
        """書類生成パネルを作成"""
        # ヘッダー
        header = ctk.CTkFrame(
            parent,
            fg_color=Colors.DARK_GRAY,
            corner_radius=0,
            height=50
        )
        header.pack(fill="x")
        header.pack_propagate(False)

        header_label = ctk.CTkLabel(
            header,
            text="📝 書類生成",
            font=(Fonts.FAMILY, Fonts.SUBTITLE, Fonts.BOLD),
            text_color=Colors.TEXT_WHITE
        )
        header_label.pack(side="left", padx=Spacing.PADDING_MEDIUM, pady=Spacing.PADDING_SMALL)

        # コンテンツ
        self.generation_content = ctk.CTkFrame(parent, fg_color="transparent")
        self.generation_content.pack(fill="both", expand=True, padx=Spacing.PADDING_MEDIUM, pady=Spacing.PADDING_MEDIUM)

        # 初期表示
        self._show_generation_placeholder()

    def _show_generation_placeholder(self):
        """生成パネルのプレースホルダーを表示"""
        for widget in self.generation_content.winfo_children():
            widget.destroy()

        placeholder = ctk.CTkLabel(
            self.generation_content,
            text="👈 左側のリストから\nテンプレートを選択してください",
            font=(Fonts.FAMILY, Fonts.BODY),
            text_color=Colors.TEXT_SECONDARY
        )
        placeholder.pack(expand=True)

    def _show_generation_form(self, template: DocumentTemplate):
        """書類生成フォームを表示"""
        for widget in self.generation_content.winfo_children():
            widget.destroy()

        # テンプレート情報
        info_frame = ctk.CTkFrame(self.generation_content, fg_color=Colors.MEDIUM_GRAY, corner_radius=Spacing.RADIUS_BUTTON)
        info_frame.pack(fill="x", pady=(0, Spacing.PADDING_MEDIUM))

        info_label = ctk.CTkLabel(
            info_frame,
            text=f"選択中: {template.name}",
            font=(Fonts.FAMILY, Fonts.BODY, Fonts.BOLD),
            text_color=Colors.TEXT_PRIMARY
        )
        info_label.pack(padx=Spacing.PADDING_MEDIUM, pady=Spacing.PADDING_SMALL)

        if template.description:
            desc_label = ctk.CTkLabel(
                info_frame,
                text=template.description,
                font=(Fonts.FAMILY, Fonts.SMALL),
                text_color=Colors.TEXT_SECONDARY
            )
            desc_label.pack(padx=Spacing.PADDING_MEDIUM, pady=(0, Spacing.PADDING_SMALL))

        # スクロール可能なフォームエリア
        form_scroll = ctk.CTkScrollableFrame(self.generation_content, fg_color="transparent")
        form_scroll.pack(fill="both", expand=True, pady=Spacing.PADDING_SMALL)

        # プレースホルダーから入力フィールドを生成
        self.field_entries: Dict[str, Any] = {}

        # 差し込みフィールド取得
        if template.file_path:
            placeholders = self.document_service.extract_placeholders(template.file_path)
        else:
            placeholders = []

        if placeholders:
            fields_label = ctk.CTkLabel(
                form_scroll,
                text="■ 差し込みフィールド",
                font=(Fonts.FAMILY, Fonts.BODY, Fonts.BOLD),
                text_color=Colors.TEXT_PRIMARY,
                anchor="w"
            )
            fields_label.pack(fill="x", pady=(0, Spacing.PADDING_SMALL))

            available_fields = self.document_service.get_available_fields()

            for key in placeholders:
                field_frame = ctk.CTkFrame(form_scroll, fg_color="transparent")
                field_frame.pack(fill="x", pady=Spacing.PADDING_XSMALL)

                # ラベルを探す
                label = key
                for category, fields in available_fields.items():
                    for f in fields:
                        if f["key"] == key:
                            label = f["label"]
                            break

                field_label = ctk.CTkLabel(
                    field_frame,
                    text=f"{label}:",
                    font=(Fonts.FAMILY, Fonts.BODY),
                    text_color=Colors.TEXT_PRIMARY,
                    width=150,
                    anchor="w"
                )
                field_label.pack(side="left")

                field_entry = ctk.CTkEntry(
                    field_frame,
                    placeholder_text=f"{{{{{key}}}}}",
                    font=(Fonts.FAMILY, Fonts.BODY),
                    height=35
                )
                field_entry.pack(side="left", fill="x", expand=True)

                self.field_entries[key] = field_entry
        else:
            no_fields_label = ctk.CTkLabel(
                form_scroll,
                text="テンプレートにプレースホルダーがありません\n（{{key}}形式で記述）",
                font=(Fonts.FAMILY, Fonts.BODY),
                text_color=Colors.TEXT_SECONDARY
            )
            no_fields_label.pack(pady=Spacing.PADDING_LARGE)

        # データソース選択
        source_frame = ctk.CTkFrame(form_scroll, fg_color="transparent")
        source_frame.pack(fill="x", pady=Spacing.PADDING_MEDIUM)

        source_label = ctk.CTkLabel(
            source_frame,
            text="■ データソース（オプション）",
            font=(Fonts.FAMILY, Fonts.BODY, Fonts.BOLD),
            text_color=Colors.TEXT_PRIMARY,
            anchor="w"
        )
        source_label.pack(fill="x", pady=(0, Spacing.PADDING_SMALL))

        # 職員選択
        staff_frame = ctk.CTkFrame(source_frame, fg_color="transparent")
        staff_frame.pack(fill="x", pady=Spacing.PADDING_XSMALL)

        staff_label = ctk.CTkLabel(
            staff_frame,
            text="職員:",
            font=(Fonts.FAMILY, Fonts.BODY),
            text_color=Colors.TEXT_PRIMARY,
            width=150,
            anchor="w"
        )
        staff_label.pack(side="left")

        self.staff_combo = ctk.CTkComboBox(
            staff_frame,
            values=["（選択なし）"],
            font=(Fonts.FAMILY, Fonts.BODY),
            height=35,
            command=self._on_staff_selected
        )
        self.staff_combo.pack(side="left", fill="x", expand=True)
        self._load_staff_options()

        # 病院選択
        hospital_frame = ctk.CTkFrame(source_frame, fg_color="transparent")
        hospital_frame.pack(fill="x", pady=Spacing.PADDING_XSMALL)

        hospital_label = ctk.CTkLabel(
            hospital_frame,
            text="病院:",
            font=(Fonts.FAMILY, Fonts.BODY),
            text_color=Colors.TEXT_PRIMARY,
            width=150,
            anchor="w"
        )
        hospital_label.pack(side="left")

        self.hospital_combo = ctk.CTkComboBox(
            hospital_frame,
            values=["（選択なし）"],
            font=(Fonts.FAMILY, Fonts.BODY),
            height=35,
            command=self._on_hospital_selected
        )
        self.hospital_combo.pack(side="left", fill="x", expand=True)
        self._load_hospital_options()

        # 生成ボタン
        button_frame = ctk.CTkFrame(self.generation_content, fg_color="transparent")
        button_frame.pack(fill="x", pady=Spacing.PADDING_MEDIUM)

        generate_btn = ctk.CTkButton(
            button_frame,
            text="📄 書類を生成",
            font=(Fonts.FAMILY, Fonts.BODY, Fonts.BOLD),
            fg_color=Colors.SUCCESS,
            hover_color="#219a52",
            height=50,
            command=lambda: self._on_generate(template)
        )
        generate_btn.pack(fill="x")

        # 結果表示エリア
        self.result_label = ctk.CTkLabel(
            self.generation_content,
            text="",
            font=(Fonts.FAMILY, Fonts.BODY),
            text_color=Colors.TEXT_SECONDARY
        )
        self.result_label.pack(fill="x", pady=Spacing.PADDING_SMALL)

    def _load_templates(self):
        """テンプレート一覧を読み込み"""
        # クリア
        for widget in self.template_list_frame.winfo_children():
            widget.destroy()

        try:
            with get_db_session() as db:
                repo = DocumentTemplateRepository(db)
                templates = repo.get_all()

                if not templates:
                    no_data_label = ctk.CTkLabel(
                        self.template_list_frame,
                        text="テンプレートがありません\n\n「テンプレート追加」から\nWord/Excelファイルを\nアップロードしてください",
                        font=(Fonts.FAMILY, Fonts.BODY),
                        text_color=Colors.TEXT_SECONDARY
                    )
                    no_data_label.pack(expand=True, pady=Spacing.PADDING_LARGE)
                    return

                for template in templates:
                    self._add_template_item(template)

        except Exception as e:
            logger.error(f"Failed to load templates: {e}")

    def _add_template_item(self, template: DocumentTemplate):
        """テンプレートアイテムを追加"""
        item_frame = ctk.CTkFrame(
            self.template_list_frame,
            fg_color=Colors.MEDIUM_GRAY,
            corner_radius=Spacing.RADIUS_BUTTON
        )
        item_frame.pack(fill="x", pady=Spacing.PADDING_XSMALL)

        # クリック可能にする
        item_frame.bind("<Button-1>", lambda e, t=template: self._on_template_select(t))

        # アイコン
        icon = "📘" if template.is_word else "📗" if template.is_excel else "📄"

        info_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        info_frame.pack(fill="x", padx=Spacing.PADDING_SMALL, pady=Spacing.PADDING_SMALL)
        info_frame.bind("<Button-1>", lambda e, t=template: self._on_template_select(t))

        name_label = ctk.CTkLabel(
            info_frame,
            text=f"{icon} {template.name}",
            font=(Fonts.FAMILY, Fonts.BODY, Fonts.BOLD),
            text_color=Colors.TEXT_PRIMARY,
            anchor="w"
        )
        name_label.pack(fill="x")
        name_label.bind("<Button-1>", lambda e, t=template: self._on_template_select(t))

        if template.category:
            cat_label = ctk.CTkLabel(
                info_frame,
                text=f"カテゴリ: {template.category}",
                font=(Fonts.FAMILY, Fonts.SMALL),
                text_color=Colors.TEXT_SECONDARY,
                anchor="w"
            )
            cat_label.pack(fill="x")
            cat_label.bind("<Button-1>", lambda e, t=template: self._on_template_select(t))

        # 削除ボタン
        delete_btn = ctk.CTkButton(
            item_frame,
            text="🗑️",
            font=(Fonts.FAMILY, Fonts.SMALL),
            fg_color="transparent",
            hover_color=Colors.ERROR,
            width=30,
            height=30,
            command=lambda t=template: self._on_delete_template(t)
        )
        delete_btn.pack(side="right", padx=Spacing.PADDING_XSMALL, pady=Spacing.PADDING_XSMALL)

    def _on_template_select(self, template: DocumentTemplate):
        """テンプレート選択時"""
        self.selected_template = template
        self._show_generation_form(template)
        logger.debug(f"Template selected: {template.name}")

    def _on_add_template(self):
        """テンプレート追加"""
        file_path = filedialog.askopenfilename(
            title="テンプレートファイルを選択",
            filetypes=[
                ("Word/Excelファイル", "*.docx *.xlsx"),
                ("Wordファイル", "*.docx"),
                ("Excelファイル", "*.xlsx"),
            ]
        )

        if not file_path:
            return

        # 名前入力ダイアログ
        dialog = ctk.CTkInputDialog(
            text="テンプレート名を入力してください:",
            title="テンプレート追加"
        )
        name = dialog.get_input()

        if not name:
            return

        try:
            # ファイルを保存
            saved_path, file_type = self.document_service.save_template(file_path, name)

            # DBに登録
            with get_db_session() as db:
                repo = DocumentTemplateRepository(db)

                # 重複チェック
                existing = repo.get_by_name(name)
                if existing:
                    self._show_error("同じ名前のテンプレートが既に存在します")
                    return

                repo.create({
                    "name": name,
                    "file_path": saved_path,
                    "file_type": file_type,
                    "description": os.path.basename(file_path),
                })

            self._load_templates()
            logger.info(f"Template added: {name}")

        except Exception as e:
            logger.error(f"Failed to add template: {e}")
            self._show_error(f"テンプレートの追加に失敗しました: {e}")

    def _on_delete_template(self, template: DocumentTemplate):
        """テンプレート削除"""
        dialog = ctk.CTkInputDialog(
            text=f"「{template.name}」を削除しますか？\n\n確認のため「削除」と入力してください:",
            title="削除確認"
        )

        if dialog.get_input() != "削除":
            return

        try:
            # ファイル削除
            if template.file_path:
                self.document_service.delete_template(template.file_path)

            # DB削除
            with get_db_session() as db:
                repo = DocumentTemplateRepository(db)
                repo.delete(template.id)

            self._load_templates()
            self._show_generation_placeholder()
            logger.info(f"Template deleted: {template.name}")

        except Exception as e:
            logger.error(f"Failed to delete template: {e}")
            self._show_error(f"テンプレートの削除に失敗しました: {e}")

    def _load_staff_options(self):
        """職員オプションを読み込み"""
        try:
            with get_db_session() as db:
                repo = StaffRepository(db)
                staff_list = repo.get_all()

                self.staff_map: Dict[str, Any] = {}
                options = ["（選択なし）"]

                for staff in staff_list:
                    display = f"{staff.name} ({staff.staff_type})"
                    options.append(display)
                    self.staff_map[display] = staff

                self.staff_combo.configure(values=options)

        except Exception as e:
            logger.error(f"Failed to load staff options: {e}")

    def _load_hospital_options(self):
        """病院オプションを読み込み"""
        try:
            with get_db_session() as db:
                repo = HospitalRepository(db)
                hospital_list = repo.get_all()

                self.hospital_map: Dict[str, Any] = {}
                options = ["（選択なし）"]

                for hospital in hospital_list:
                    options.append(hospital.name)
                    self.hospital_map[hospital.name] = hospital

                self.hospital_combo.configure(values=options)

        except Exception as e:
            logger.error(f"Failed to load hospital options: {e}")

    def _on_staff_selected(self, selection: str):
        """職員選択時にフィールドを自動入力"""
        if selection == "（選択なし）":
            return

        staff = self.staff_map.get(selection)
        if not staff:
            return

        # 対応するフィールドを自動入力
        field_mapping = {
            "staff_name": staff.name,
            "staff_email": staff.email or "",
            "staff_phone": staff.phone or "",
            "staff_address": staff.address or "",
            "staff_type": staff.staff_type or "",
        }

        for key, value in field_mapping.items():
            if key in self.field_entries:
                entry = self.field_entries[key]
                entry.delete(0, "end")
                entry.insert(0, value)

    def _on_hospital_selected(self, selection: str):
        """病院選択時にフィールドを自動入力"""
        if selection == "（選択なし）":
            return

        hospital = self.hospital_map.get(selection)
        if not hospital:
            return

        # 対応するフィールドを自動入力
        field_mapping = {
            "hospital_name": hospital.name,
            "hospital_address": hospital.address or "",
            "hospital_phone": hospital.phone or "",
            "hospital_director": hospital.director_name or "",
        }

        for key, value in field_mapping.items():
            if key in self.field_entries:
                entry = self.field_entries[key]
                entry.delete(0, "end")
                entry.insert(0, value)

    def _on_generate(self, template: DocumentTemplate):
        """書類生成"""
        if not template.file_path:
            self._show_error("テンプレートファイルが設定されていません")
            return

        # フィールド値を収集
        data = {}
        for key, entry in self.field_entries.items():
            value = entry.get().strip()
            if value:
                data[key] = value

        # 日付フィールドを自動追加
        now = datetime.now()
        data.setdefault("today", now.strftime("%Y年%m月%d日"))
        data.setdefault("today_jp", self._to_japanese_era(now))
        fiscal_year = now.year if now.month >= 4 else now.year - 1
        data.setdefault("fiscal_year", str(fiscal_year))

        try:
            output_path = self.document_service.generate_document(
                template.file_path,
                data
            )

            self.result_label.configure(
                text=f"✅ 生成完了: {os.path.basename(output_path)}",
                text_color=Colors.SUCCESS
            )

            # ファイルを開くか確認
            self._ask_open_file(output_path)

            logger.info(f"Document generated: {output_path}")

        except DocumentServiceException as e:
            self._show_error(str(e))
        except Exception as e:
            logger.error(f"Failed to generate document: {e}")
            self._show_error(f"書類の生成に失敗しました: {e}")

    def _to_japanese_era(self, dt: datetime) -> str:
        """和暦に変換"""
        year = dt.year
        if year >= 2019:
            era_year = year - 2018
            era = "令和"
        elif year >= 1989:
            era_year = year - 1988
            era = "平成"
        else:
            era_year = year - 1925
            era = "昭和"

        return f"{era}{era_year}年{dt.month}月{dt.day}日"

    def _ask_open_file(self, file_path: str):
        """ファイルを開くか確認"""
        dialog = ctk.CTkInputDialog(
            text="生成したファイルを開きますか？\n\n「開く」と入力してください:",
            title="ファイルを開く"
        )

        if dialog.get_input() == "開く":
            self._open_file(file_path)

    def _open_file(self, file_path: str):
        """ファイルを開く"""
        try:
            if platform.system() == "Windows":
                os.startfile(file_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", file_path])
            else:  # Linux
                subprocess.run(["xdg-open", file_path])
        except Exception as e:
            logger.error(f"Failed to open file: {e}")

    def _show_error(self, message: str):
        """エラーを表示"""
        self.result_label.configure(
            text=f"❌ エラー: {message}",
            text_color=Colors.ERROR
        )
