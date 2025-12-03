"""
メール管理画面
"""
import customtkinter as ctk
from typing import Optional, List
from config.constants import Colors, Fonts, Spacing
from database.base import SessionLocal
from database.models.mail_template import MailTemplate
from repositories.mail_template_repository import MailTemplateRepository
from utils.logger import get_logger
from utils.exceptions import DuplicateRecordException

logger = get_logger(__name__)


class MailView(ctk.CTkFrame):
    """
    メール管理画面

    サブタブ:
    - テンプレート管理
    - メール作成
    """

    def __init__(self, parent):
        super().__init__(parent, fg_color=Colors.BG_MAIN)

        self.current_tab = "templates"
        self.selected_template: Optional[MailTemplate] = None

        # UI構築
        self._create_header()
        self._create_tab_bar()
        self._create_content_area()

        # 初期タブ表示
        self._load_tab_content(self.current_tab)

        logger.info("MailView initialized")

    def _create_header(self):
        """ヘッダーを作成"""
        header_frame = ctk.CTkFrame(
            self,
            fg_color="transparent",
            height=80
        )
        header_frame.pack(fill="x", padx=Spacing.PADDING_LARGE, pady=(Spacing.PADDING_LARGE, 0))
        header_frame.pack_propagate(False)

        title_label = ctk.CTkLabel(
            header_frame,
            text="✉️ メール管理",
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
            ("templates", "📋 テンプレート管理"),
            ("compose", "✍️ メール作成"),
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

        if tab_id == "templates":
            self._load_templates_tab()
        elif tab_id == "compose":
            self._load_compose_tab()

    # ===== テンプレート管理タブ =====

    def _load_templates_tab(self):
        """テンプレート管理タブを読み込み"""
        # ツールバー
        toolbar = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        toolbar.pack(fill="x", padx=Spacing.PADDING_MEDIUM, pady=Spacing.PADDING_MEDIUM)

        add_btn = ctk.CTkButton(
            toolbar,
            text="➕ 新規テンプレート",
            font=(Fonts.FAMILY, Fonts.BODY, Fonts.BOLD),
            fg_color=Colors.SUCCESS,
            hover_color="#219a52",
            width=180,
            height=40,
            command=self._on_add_template
        )
        add_btn.pack(side="left")

        # 検索
        self.search_entry = ctk.CTkEntry(
            toolbar,
            placeholder_text="テンプレートを検索...",
            font=(Fonts.FAMILY, Fonts.BODY),
            width=300,
            height=40
        )
        self.search_entry.pack(side="right", padx=Spacing.PADDING_SMALL)
        self.search_entry.bind("<KeyRelease>", lambda e: self._load_template_list())

        # テンプレートリスト
        self.template_list_frame = ctk.CTkScrollableFrame(
            self.content_frame,
            fg_color="transparent"
        )
        self.template_list_frame.pack(fill="both", expand=True, padx=Spacing.PADDING_MEDIUM)

        self._load_template_list()

    def _load_template_list(self):
        """テンプレートリストを読み込み"""
        for widget in self.template_list_frame.winfo_children():
            widget.destroy()

        keyword = self.search_entry.get().strip() if hasattr(self, 'search_entry') else ""

        with SessionLocal() as db:
            repo = MailTemplateRepository(db)
            if keyword:
                templates = repo.search_by_keyword(keyword)
            else:
                templates = repo.get_all()

        if not templates:
            no_data = ctk.CTkLabel(
                self.template_list_frame,
                text="テンプレートがありません",
                font=(Fonts.FAMILY, Fonts.BODY),
                text_color=Colors.TEXT_SECONDARY
            )
            no_data.pack(pady=Spacing.PADDING_LARGE)
            return

        for template in templates:
            self._create_template_row(template)

    def _create_template_row(self, template: MailTemplate):
        """テンプレート行を作成"""
        row = ctk.CTkFrame(
            self.template_list_frame,
            fg_color=Colors.BG_MAIN,
            corner_radius=Spacing.RADIUS_CARD
        )
        row.pack(fill="x", pady=4)

        # 左側: テンプレート情報
        info_frame = ctk.CTkFrame(row, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=Spacing.PADDING_MEDIUM, pady=Spacing.PADDING_SMALL)

        name_label = ctk.CTkLabel(
            info_frame,
            text=template.name,
            font=(Fonts.FAMILY, Fonts.BODY, Fonts.BOLD),
            text_color=Colors.TEXT_PRIMARY,
            anchor="w"
        )
        name_label.pack(fill="x")

        subject_label = ctk.CTkLabel(
            info_frame,
            text=f"件名: {template.subject}",
            font=(Fonts.FAMILY, Fonts.SMALL),
            text_color=Colors.TEXT_SECONDARY,
            anchor="w"
        )
        subject_label.pack(fill="x")

        if template.category:
            category_label = ctk.CTkLabel(
                info_frame,
                text=f"カテゴリ: {template.category}",
                font=(Fonts.FAMILY, Fonts.SMALL),
                text_color=Colors.INFO,
                anchor="w"
            )
            category_label.pack(fill="x")

        # 右側: アクションボタン
        btn_frame = ctk.CTkFrame(row, fg_color="transparent")
        btn_frame.pack(side="right", padx=Spacing.PADDING_MEDIUM, pady=Spacing.PADDING_SMALL)

        edit_btn = ctk.CTkButton(
            btn_frame,
            text="✏️",
            font=(Fonts.FAMILY, Fonts.BODY),
            fg_color=Colors.INFO,
            hover_color=Colors.PRIMARY_HOVER,
            width=40,
            height=32,
            command=lambda t=template: self._on_edit_template(t)
        )
        edit_btn.pack(side="left", padx=2)

        use_btn = ctk.CTkButton(
            btn_frame,
            text="📝",
            font=(Fonts.FAMILY, Fonts.BODY),
            fg_color=Colors.SUCCESS,
            hover_color="#219a52",
            width=40,
            height=32,
            command=lambda t=template: self._on_use_template(t)
        )
        use_btn.pack(side="left", padx=2)

        delete_btn = ctk.CTkButton(
            btn_frame,
            text="🗑️",
            font=(Fonts.FAMILY, Fonts.BODY),
            fg_color=Colors.ERROR,
            hover_color="#c0392b",
            width=40,
            height=32,
            command=lambda t=template: self._on_delete_template(t)
        )
        delete_btn.pack(side="left", padx=2)

    def _on_add_template(self):
        """新規テンプレート追加"""
        dialog = TemplateEditDialog(self, on_save=self._load_template_list)
        dialog.grab_set()

    def _on_edit_template(self, template: MailTemplate):
        """テンプレート編集"""
        dialog = TemplateEditDialog(self, template_id=template.id, on_save=self._load_template_list)
        dialog.grab_set()

    def _on_use_template(self, template: MailTemplate):
        """テンプレートを使用してメール作成"""
        self.selected_template = template
        self._switch_tab("compose")

    def _on_delete_template(self, template: MailTemplate):
        """テンプレート削除"""
        confirm = ctk.CTkInputDialog(
            text=f"「{template.name}」を削除しますか？\n\n削除する場合は「削除」と入力してください。",
            title="削除確認"
        )
        if confirm.get_input() == "削除":
            try:
                with SessionLocal() as db:
                    repo = MailTemplateRepository(db)
                    repo.delete(template.id)
                self._load_template_list()
                logger.info(f"Deleted template: {template.name}")
            except Exception as e:
                self._show_error(f"削除に失敗しました: {str(e)}")

    # ===== メール作成タブ =====

    def _load_compose_tab(self):
        """メール作成タブを読み込み"""
        # テンプレート選択
        select_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        select_frame.pack(fill="x", padx=Spacing.PADDING_MEDIUM, pady=Spacing.PADDING_MEDIUM)

        select_label = ctk.CTkLabel(
            select_frame,
            text="テンプレート:",
            font=(Fonts.FAMILY, Fonts.BODY, Fonts.BOLD),
            text_color=Colors.TEXT_PRIMARY
        )
        select_label.pack(side="left")

        # テンプレート選択肢を取得
        with SessionLocal() as db:
            repo = MailTemplateRepository(db)
            templates = repo.get_all()

        template_names = ["(テンプレートを選択)"] + [t.name for t in templates]
        self.template_map = {t.name: t.id for t in templates}

        self.template_combo = ctk.CTkComboBox(
            select_frame,
            values=template_names,
            font=(Fonts.FAMILY, Fonts.BODY),
            width=300,
            height=40,
            command=self._on_template_selected
        )
        self.template_combo.pack(side="left", padx=Spacing.PADDING_SMALL)

        # 選択済みテンプレートがあれば設定
        if self.selected_template:
            self.template_combo.set(self.selected_template.name)

        # メール編集エリア
        edit_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        edit_frame.pack(fill="both", expand=True, padx=Spacing.PADDING_MEDIUM, pady=Spacing.PADDING_MEDIUM)

        # 宛先
        to_label = ctk.CTkLabel(
            edit_frame,
            text="宛先:",
            font=(Fonts.FAMILY, Fonts.BODY, Fonts.BOLD),
            text_color=Colors.TEXT_PRIMARY
        )
        to_label.pack(anchor="w")

        self.to_entry = ctk.CTkEntry(
            edit_frame,
            placeholder_text="example@example.com",
            font=(Fonts.FAMILY, Fonts.BODY),
            height=40
        )
        self.to_entry.pack(fill="x", pady=(4, Spacing.PADDING_MEDIUM))

        # 件名
        subject_label = ctk.CTkLabel(
            edit_frame,
            text="件名:",
            font=(Fonts.FAMILY, Fonts.BODY, Fonts.BOLD),
            text_color=Colors.TEXT_PRIMARY
        )
        subject_label.pack(anchor="w")

        self.subject_entry = ctk.CTkEntry(
            edit_frame,
            placeholder_text="メールの件名",
            font=(Fonts.FAMILY, Fonts.BODY),
            height=40
        )
        self.subject_entry.pack(fill="x", pady=(4, Spacing.PADDING_MEDIUM))

        # 本文
        body_label = ctk.CTkLabel(
            edit_frame,
            text="本文:",
            font=(Fonts.FAMILY, Fonts.BODY, Fonts.BOLD),
            text_color=Colors.TEXT_PRIMARY
        )
        body_label.pack(anchor="w")

        self.body_text = ctk.CTkTextbox(
            edit_frame,
            font=(Fonts.FAMILY, Fonts.BODY),
            height=250
        )
        self.body_text.pack(fill="both", expand=True, pady=(4, Spacing.PADDING_MEDIUM))

        # 選択済みテンプレートの内容を読み込み
        if self.selected_template:
            self._load_template_content(self.selected_template.id)

        # ボタン
        btn_frame = ctk.CTkFrame(edit_frame, fg_color="transparent")
        btn_frame.pack(fill="x")

        clear_btn = ctk.CTkButton(
            btn_frame,
            text="クリア",
            font=(Fonts.FAMILY, Fonts.BODY),
            fg_color=Colors.MEDIUM_GRAY,
            hover_color=Colors.DARK_GRAY,
            width=120,
            height=40,
            command=self._clear_compose
        )
        clear_btn.pack(side="left")

        send_btn = ctk.CTkButton(
            btn_frame,
            text="📤 送信",
            font=(Fonts.FAMILY, Fonts.BODY, Fonts.BOLD),
            fg_color=Colors.PRIMARY,
            hover_color=Colors.PRIMARY_HOVER,
            width=140,
            height=40,
            command=self._on_send_mail
        )
        send_btn.pack(side="right")

    def _on_template_selected(self, template_name: str):
        """テンプレート選択時"""
        if template_name == "(テンプレートを選択)":
            return

        template_id = self.template_map.get(template_name)
        if template_id:
            self._load_template_content(template_id)

    def _load_template_content(self, template_id: int):
        """テンプレート内容を読み込み"""
        with SessionLocal() as db:
            repo = MailTemplateRepository(db)
            template = repo.get(template_id)

        if template:
            self.subject_entry.delete(0, "end")
            self.subject_entry.insert(0, template.subject)

            self.body_text.delete("1.0", "end")
            self.body_text.insert("1.0", template.body)

    def _clear_compose(self):
        """作成エリアをクリア"""
        self.to_entry.delete(0, "end")
        self.subject_entry.delete(0, "end")
        self.body_text.delete("1.0", "end")
        self.template_combo.set("(テンプレートを選択)")
        self.selected_template = None

    def _on_send_mail(self):
        """メール送信"""
        to = self.to_entry.get().strip()
        subject = self.subject_entry.get().strip()
        body = self.body_text.get("1.0", "end-1c").strip()

        if not to:
            self._show_error("宛先を入力してください")
            return

        if not subject:
            self._show_error("件名を入力してください")
            return

        if not body:
            self._show_error("本文を入力してください")
            return

        # メール送信（実際の送信はGmail APIを使用 - 将来的に実装）
        logger.info(f"Mail to be sent: to={to}, subject={subject}")

        # 成功メッセージ
        success_dialog = ctk.CTkInputDialog(
            text=f"✅ メールを送信しました（実際には送信されていません）\n\n宛先: {to}\n件名: {subject}",
            title="送信完了"
        )
        success_dialog.get_input()

    def _show_error(self, message: str):
        """エラーメッセージを表示"""
        dialog = ctk.CTkInputDialog(
            text=f"❌ {message}",
            title="エラー"
        )
        dialog.get_input()


class TemplateEditDialog(ctk.CTkToplevel):
    """テンプレート編集ダイアログ"""

    def __init__(self, parent, template_id: Optional[int] = None, on_save: callable = None):
        super().__init__(parent)

        self.template_id = template_id
        self.on_save = on_save
        self.template: Optional[MailTemplate] = None

        self.title("テンプレート編集" if template_id else "新規テンプレート")
        self.geometry("600x500")
        self.resizable(False, False)

        if template_id:
            with SessionLocal() as db:
                repo = MailTemplateRepository(db)
                self.template = repo.get(template_id)

        self._create_form()

    def _create_form(self):
        """フォームを作成"""
        main_frame = ctk.CTkFrame(self, fg_color=Colors.BG_MAIN)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # テンプレート名
        name_label = ctk.CTkLabel(
            main_frame,
            text="テンプレート名 *",
            font=(Fonts.FAMILY, Fonts.BODY, Fonts.BOLD),
            text_color=Colors.TEXT_PRIMARY
        )
        name_label.pack(anchor="w")

        self.name_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="配属通知、会議案内など",
            font=(Fonts.FAMILY, Fonts.BODY),
            height=40
        )
        self.name_entry.pack(fill="x", pady=(4, Spacing.PADDING_MEDIUM))
        if self.template:
            self.name_entry.insert(0, self.template.name)

        # カテゴリ
        category_label = ctk.CTkLabel(
            main_frame,
            text="カテゴリ",
            font=(Fonts.FAMILY, Fonts.BODY, Fonts.BOLD),
            text_color=Colors.TEXT_PRIMARY
        )
        category_label.pack(anchor="w")

        self.category_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="通知、案内など",
            font=(Fonts.FAMILY, Fonts.BODY),
            height=40
        )
        self.category_entry.pack(fill="x", pady=(4, Spacing.PADDING_MEDIUM))
        if self.template and self.template.category:
            self.category_entry.insert(0, self.template.category)

        # 件名
        subject_label = ctk.CTkLabel(
            main_frame,
            text="件名 *",
            font=(Fonts.FAMILY, Fonts.BODY, Fonts.BOLD),
            text_color=Colors.TEXT_PRIMARY
        )
        subject_label.pack(anchor="w")

        self.subject_entry = ctk.CTkEntry(
            main_frame,
            placeholder_text="{name}様への配属のお知らせ",
            font=(Fonts.FAMILY, Fonts.BODY),
            height=40
        )
        self.subject_entry.pack(fill="x", pady=(4, Spacing.PADDING_MEDIUM))
        if self.template:
            self.subject_entry.insert(0, self.template.subject)

        # 本文
        body_label = ctk.CTkLabel(
            main_frame,
            text="本文 *（{name}などの変数が使用可能）",
            font=(Fonts.FAMILY, Fonts.BODY, Fonts.BOLD),
            text_color=Colors.TEXT_PRIMARY
        )
        body_label.pack(anchor="w")

        self.body_text = ctk.CTkTextbox(
            main_frame,
            font=(Fonts.FAMILY, Fonts.BODY),
            height=150
        )
        self.body_text.pack(fill="x", pady=(4, Spacing.PADDING_MEDIUM))
        if self.template:
            self.body_text.insert("1.0", self.template.body)

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
        name = self.name_entry.get().strip()
        if not name:
            self._show_error("テンプレート名を入力してください")
            return

        subject = self.subject_entry.get().strip()
        if not subject:
            self._show_error("件名を入力してください")
            return

        body = self.body_text.get("1.0", "end-1c").strip()
        if not body:
            self._show_error("本文を入力してください")
            return

        category = self.category_entry.get().strip() or None

        try:
            with SessionLocal() as db:
                repo = MailTemplateRepository(db)

                data = {
                    "name": name,
                    "subject": subject,
                    "body": body,
                    "category": category
                }

                if self.template_id:
                    repo.update(self.template_id, data)
                else:
                    repo.create(data)

            logger.info(f"Saved template: {name}")
            if self.on_save:
                self.on_save()
            self.destroy()

        except DuplicateRecordException:
            self._show_error("同じ名前のテンプレートが既に存在します")
        except Exception as e:
            self._show_error(f"保存に失敗しました: {str(e)}")
            logger.error(f"Failed to save template: {e}")

    def _show_error(self, message: str):
        """エラーメッセージを表示"""
        dialog = ctk.CTkInputDialog(
            text=f"❌ {message}",
            title="エラー"
        )
        dialog.get_input()
