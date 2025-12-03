"""
希望調査管理画面

スプレッドシート生成・インポート機能
"""
import customtkinter as ctk
from typing import Optional, Callable
from datetime import datetime
import webbrowser
import threading

from config.constants import Colors, Fonts, Spacing
from database.connection import get_db_session
from services.preference_survey_service import PreferenceSurveyService, PreferenceSurveyException
from repositories.staff_repository import StaffRepository
from repositories.hospital_repository import HospitalRepository
from repositories.evaluation_factor_repository import EvaluationFactorRepository
from repositories.hospital_choice_repository import HospitalChoiceRepository
from repositories.staff_factor_weight_repository import StaffFactorWeightRepository
from utils.logger import get_logger

logger = get_logger(__name__)


class SurveyView(ctk.CTkFrame):
    """
    希望調査管理画面

    機能:
    - スプレッドシート生成
    - データインポート
    - インポート状況確認
    """

    def __init__(self, parent):
        super().__init__(parent, fg_color=Colors.BG_MAIN)

        # 現在年度
        now = datetime.now()
        self.current_year = now.year if now.month >= 4 else now.year - 1

        # 生成されたスプレッドシート情報
        self.spreadsheet_id: Optional[str] = None
        self.spreadsheet_url: Optional[str] = None

        # UI構築
        self._create_header()
        self._create_content()

        # 状況更新
        self._update_status()

        logger.info("SurveyView initialized")

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
            text="📊 希望調査管理",
            font=(Fonts.FAMILY, Fonts.TITLE, Fonts.BOLD),
            text_color=Colors.TEXT_PRIMARY,
            anchor="w"
        )
        title_label.pack(side="left", pady=Spacing.PADDING_MEDIUM)

        # 年度選択
        year_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        year_frame.pack(side="right", pady=Spacing.PADDING_MEDIUM)

        year_label = ctk.CTkLabel(
            year_frame,
            text="対象年度:",
            font=(Fonts.FAMILY, Fonts.BODY),
            text_color=Colors.TEXT_PRIMARY
        )
        year_label.pack(side="left", padx=(0, Spacing.PADDING_SMALL))

        years = [str(y) for y in range(self.current_year - 2, self.current_year + 3)]
        self.year_combo = ctk.CTkComboBox(
            year_frame,
            values=years,
            font=(Fonts.FAMILY, Fonts.BODY),
            width=100,
            height=40,
            command=self._on_year_change
        )
        self.year_combo.set(str(self.current_year))
        self.year_combo.pack(side="left")

    def _create_content(self):
        """コンテンツエリアを作成"""
        content_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        content_frame.pack(fill="both", expand=True, padx=Spacing.PADDING_LARGE, pady=Spacing.PADDING_MEDIUM)

        # 左カラム: スプレッドシート操作
        left_col = ctk.CTkFrame(
            content_frame,
            fg_color=Colors.BG_CARD,
            corner_radius=Spacing.RADIUS_CARD
        )
        left_col.pack(side="left", fill="both", expand=True, padx=(0, Spacing.PADDING_SMALL))

        self._create_spreadsheet_section(left_col)

        # 右カラム: 状況表示
        right_col = ctk.CTkFrame(
            content_frame,
            fg_color=Colors.BG_CARD,
            corner_radius=Spacing.RADIUS_CARD
        )
        right_col.pack(side="right", fill="both", expand=True, padx=(Spacing.PADDING_SMALL, 0))

        self._create_status_section(right_col)

    def _create_spreadsheet_section(self, parent):
        """スプレッドシート操作セクション"""
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
            text="📝 スプレッドシート操作",
            font=(Fonts.FAMILY, Fonts.SUBTITLE, Fonts.BOLD),
            text_color=Colors.TEXT_WHITE
        )
        header_label.pack(side="left", padx=Spacing.PADDING_MEDIUM, pady=Spacing.PADDING_SMALL)

        # コンテンツ
        content = ctk.CTkFrame(parent, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=Spacing.PADDING_MEDIUM, pady=Spacing.PADDING_MEDIUM)

        # 説明
        desc_label = ctk.CTkLabel(
            content,
            text="希望調査用のGoogleスプレッドシートを作成し、\n専攻医に配布して希望を収集します。",
            font=(Fonts.FAMILY, Fonts.BODY),
            text_color=Colors.TEXT_SECONDARY,
            justify="left"
        )
        desc_label.pack(fill="x", pady=(0, Spacing.PADDING_LARGE))

        # スプレッドシート作成ボタン
        create_btn = ctk.CTkButton(
            content,
            text="📊 希望調査シートを作成",
            font=(Fonts.FAMILY, Fonts.BODY, Fonts.BOLD),
            fg_color=Colors.PRIMARY,
            hover_color=Colors.PRIMARY_HOVER,
            height=50,
            command=self._on_create_spreadsheet
        )
        create_btn.pack(fill="x", pady=Spacing.PADDING_SMALL)

        # スプレッドシートID入力
        id_frame = ctk.CTkFrame(content, fg_color="transparent")
        id_frame.pack(fill="x", pady=Spacing.PADDING_MEDIUM)

        id_label = ctk.CTkLabel(
            id_frame,
            text="スプレッドシートID:",
            font=(Fonts.FAMILY, Fonts.BODY),
            text_color=Colors.TEXT_PRIMARY
        )
        id_label.pack(anchor="w")

        self.spreadsheet_id_entry = ctk.CTkEntry(
            id_frame,
            placeholder_text="スプレッドシートIDを入力または自動設定",
            font=(Fonts.FAMILY, Fonts.BODY),
            height=40
        )
        self.spreadsheet_id_entry.pack(fill="x", pady=(Spacing.PADDING_XSMALL, 0))

        # URL表示・開くボタン
        url_frame = ctk.CTkFrame(content, fg_color="transparent")
        url_frame.pack(fill="x", pady=Spacing.PADDING_SMALL)

        self.url_label = ctk.CTkLabel(
            url_frame,
            text="",
            font=(Fonts.FAMILY, Fonts.SMALL),
            text_color=Colors.PRIMARY,
            cursor="hand2"
        )
        self.url_label.pack(side="left")
        self.url_label.bind("<Button-1>", lambda e: self._open_spreadsheet())

        open_btn = ctk.CTkButton(
            url_frame,
            text="🔗 開く",
            font=(Fonts.FAMILY, Fonts.SMALL),
            fg_color=Colors.MEDIUM_GRAY,
            hover_color=Colors.DARK_GRAY,
            width=80,
            height=30,
            command=self._open_spreadsheet
        )
        open_btn.pack(side="right")

        # 区切り線
        separator = ctk.CTkFrame(content, fg_color=Colors.LIGHT_GRAY, height=2)
        separator.pack(fill="x", pady=Spacing.PADDING_LARGE)

        # インポートボタン
        import_btn = ctk.CTkButton(
            content,
            text="📥 スプレッドシートからインポート",
            font=(Fonts.FAMILY, Fonts.BODY, Fonts.BOLD),
            fg_color=Colors.SUCCESS,
            hover_color="#219a52",
            height=50,
            command=self._on_import_data
        )
        import_btn.pack(fill="x", pady=Spacing.PADDING_SMALL)

        # 進捗表示
        self.progress_label = ctk.CTkLabel(
            content,
            text="",
            font=(Fonts.FAMILY, Fonts.BODY),
            text_color=Colors.TEXT_SECONDARY
        )
        self.progress_label.pack(fill="x", pady=Spacing.PADDING_SMALL)

        self.progress_bar = ctk.CTkProgressBar(
            content,
            fg_color=Colors.MEDIUM_GRAY,
            progress_color=Colors.PRIMARY,
            height=10
        )
        self.progress_bar.set(0)

        # 結果表示
        self.result_frame = ctk.CTkFrame(content, fg_color="transparent")
        self.result_frame.pack(fill="both", expand=True, pady=Spacing.PADDING_MEDIUM)

    def _create_status_section(self, parent):
        """状況表示セクション"""
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
            text="📈 データ収集状況",
            font=(Fonts.FAMILY, Fonts.SUBTITLE, Fonts.BOLD),
            text_color=Colors.TEXT_WHITE
        )
        header_label.pack(side="left", padx=Spacing.PADDING_MEDIUM, pady=Spacing.PADDING_SMALL)

        refresh_btn = ctk.CTkButton(
            header,
            text="🔄",
            font=(Fonts.FAMILY, Fonts.BODY),
            fg_color="transparent",
            hover_color=Colors.MEDIUM_GRAY,
            width=40,
            height=40,
            command=self._update_status
        )
        refresh_btn.pack(side="right", padx=Spacing.PADDING_SMALL)

        # コンテンツ
        self.status_content = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        self.status_content.pack(fill="both", expand=True, padx=Spacing.PADDING_MEDIUM, pady=Spacing.PADDING_MEDIUM)

    def _update_status(self):
        """状況を更新"""
        # クリア
        for widget in self.status_content.winfo_children():
            widget.destroy()

        try:
            fiscal_year = int(self.year_combo.get())

            with get_db_session() as db:
                staff_repo = StaffRepository(db)
                hospital_repo = HospitalRepository(db)
                factor_repo = EvaluationFactorRepository(db)
                choice_repo = HospitalChoiceRepository(db)
                weight_repo = StaffFactorWeightRepository(db)

                # 基本情報
                residents = staff_repo.get_resident_doctors()
                hospitals = hospital_repo.get_all()
                factors = factor_repo.get_staff_preference_factors()

                total_residents = len(residents)

                # 希望入力済み人数
                choices_count = 0
                weights_count = 0

                for staff in residents:
                    choices = choice_repo.get_by_staff_and_year(staff.id, fiscal_year)
                    if len(choices) > 0:
                        choices_count += 1

                    weights = weight_repo.get_by_staff_and_year(staff.id, fiscal_year)
                    if len(weights) > 0:
                        weights_count += 1

                # 統計表示
                self._add_status_card(
                    "👥 対象専攻医",
                    f"{total_residents} 名",
                    Colors.PRIMARY
                )

                self._add_status_card(
                    "🏥 選択可能病院",
                    f"{len(hospitals)} 施設",
                    Colors.PRIMARY
                )

                self._add_status_card(
                    "📊 評価要素",
                    f"{len(factors)} 項目",
                    Colors.PRIMARY
                )

                # 区切り
                separator = ctk.CTkFrame(self.status_content, fg_color=Colors.LIGHT_GRAY, height=2)
                separator.pack(fill="x", pady=Spacing.PADDING_MEDIUM)

                # 入力状況
                choice_pct = (choices_count / total_residents * 100) if total_residents > 0 else 0
                self._add_status_card(
                    "🏥 病院希望入力",
                    f"{choices_count} / {total_residents} 名 ({choice_pct:.0f}%)",
                    Colors.SUCCESS if choice_pct >= 100 else Colors.WARNING if choice_pct > 0 else Colors.ERROR
                )

                weight_pct = (weights_count / total_residents * 100) if total_residents > 0 else 0
                self._add_status_card(
                    "⚖️ 要素重み入力",
                    f"{weights_count} / {total_residents} 名 ({weight_pct:.0f}%)",
                    Colors.SUCCESS if weight_pct >= 100 else Colors.WARNING if weight_pct > 0 else Colors.ERROR
                )

                # 未入力者リスト
                if choices_count < total_residents or weights_count < total_residents:
                    separator2 = ctk.CTkFrame(self.status_content, fg_color=Colors.LIGHT_GRAY, height=2)
                    separator2.pack(fill="x", pady=Spacing.PADDING_MEDIUM)

                    pending_label = ctk.CTkLabel(
                        self.status_content,
                        text="⚠️ 未入力者",
                        font=(Fonts.FAMILY, Fonts.BODY, Fonts.BOLD),
                        text_color=Colors.WARNING,
                        anchor="w"
                    )
                    pending_label.pack(fill="x", pady=(0, Spacing.PADDING_SMALL))

                    for staff in residents:
                        choices = choice_repo.get_by_staff_and_year(staff.id, fiscal_year)
                        weights = weight_repo.get_by_staff_and_year(staff.id, fiscal_year)

                        missing = []
                        if len(choices) == 0:
                            missing.append("希望")
                        if len(weights) == 0:
                            missing.append("重み")

                        if missing:
                            missing_text = "、".join(missing)
                            staff_label = ctk.CTkLabel(
                                self.status_content,
                                text=f"  • {staff.name}: {missing_text}未入力",
                                font=(Fonts.FAMILY, Fonts.SMALL),
                                text_color=Colors.TEXT_SECONDARY,
                                anchor="w"
                            )
                            staff_label.pack(fill="x")

        except Exception as e:
            logger.error(f"Failed to update status: {e}")
            error_label = ctk.CTkLabel(
                self.status_content,
                text=f"状況の取得に失敗しました:\n{e}",
                font=(Fonts.FAMILY, Fonts.BODY),
                text_color=Colors.ERROR
            )
            error_label.pack(fill="x")

    def _add_status_card(self, title: str, value: str, color: str):
        """状況カードを追加"""
        card = ctk.CTkFrame(
            self.status_content,
            fg_color=Colors.MEDIUM_GRAY,
            corner_radius=Spacing.RADIUS_BUTTON
        )
        card.pack(fill="x", pady=Spacing.PADDING_XSMALL)

        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=(Fonts.FAMILY, Fonts.BODY),
            text_color=Colors.TEXT_SECONDARY,
            anchor="w"
        )
        title_label.pack(fill="x", padx=Spacing.PADDING_MEDIUM, pady=(Spacing.PADDING_SMALL, 0))

        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=(Fonts.FAMILY, Fonts.SUBTITLE, Fonts.BOLD),
            text_color=color,
            anchor="w"
        )
        value_label.pack(fill="x", padx=Spacing.PADDING_MEDIUM, pady=(0, Spacing.PADDING_SMALL))

    def _on_year_change(self, value):
        """年度変更時"""
        self._update_status()

    def _on_create_spreadsheet(self):
        """スプレッドシート作成"""
        fiscal_year = int(self.year_combo.get())

        self.progress_label.configure(text="スプレッドシートを作成中...")
        self.progress_bar.pack(fill="x", pady=Spacing.PADDING_SMALL)
        self.progress_bar.set(0)
        self.progress_bar.start()

        def create_task():
            try:
                with get_db_session() as db:
                    service = PreferenceSurveyService(db)
                    spreadsheet_id, url = service.create_survey_spreadsheet(
                        fiscal_year=fiscal_year
                    )

                # UIスレッドで更新
                self.after(0, lambda: self._on_create_success(spreadsheet_id, url))

            except PreferenceSurveyException as e:
                self.after(0, lambda: self._on_create_error(str(e)))
            except Exception as e:
                logger.error(f"Failed to create spreadsheet: {e}")
                self.after(0, lambda: self._on_create_error(str(e)))

        thread = threading.Thread(target=create_task, daemon=True)
        thread.start()

    def _on_create_success(self, spreadsheet_id: str, url: str):
        """作成成功"""
        self.progress_bar.stop()
        self.progress_bar.pack_forget()

        self.spreadsheet_id = spreadsheet_id
        self.spreadsheet_url = url

        self.spreadsheet_id_entry.delete(0, "end")
        self.spreadsheet_id_entry.insert(0, spreadsheet_id)
        self.url_label.configure(text=url)

        self.progress_label.configure(
            text="✅ スプレッドシートを作成しました",
            text_color=Colors.SUCCESS
        )

        logger.info(f"Spreadsheet created: {spreadsheet_id}")

    def _on_create_error(self, error: str):
        """作成エラー"""
        self.progress_bar.stop()
        self.progress_bar.pack_forget()

        self.progress_label.configure(
            text=f"❌ エラー: {error}",
            text_color=Colors.ERROR
        )

    def _open_spreadsheet(self):
        """スプレッドシートを開く"""
        spreadsheet_id = self.spreadsheet_id_entry.get().strip()
        if spreadsheet_id:
            url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"
            webbrowser.open(url)

    def _on_import_data(self):
        """データインポート"""
        spreadsheet_id = self.spreadsheet_id_entry.get().strip()

        if not spreadsheet_id:
            self.progress_label.configure(
                text="❌ スプレッドシートIDを入力してください",
                text_color=Colors.ERROR
            )
            return

        fiscal_year = int(self.year_combo.get())

        self.progress_label.configure(text="データをインポート中...")
        self.progress_bar.pack(fill="x", pady=Spacing.PADDING_SMALL)
        self.progress_bar.set(0)
        self.progress_bar.start()

        # 結果エリアをクリア
        for widget in self.result_frame.winfo_children():
            widget.destroy()

        def import_task():
            try:
                with get_db_session() as db:
                    service = PreferenceSurveyService(db)
                    result = service.import_from_spreadsheet(
                        spreadsheet_id,
                        fiscal_year=fiscal_year
                    )

                self.after(0, lambda: self._on_import_success(result))

            except PreferenceSurveyException as e:
                self.after(0, lambda: self._on_import_error(str(e)))
            except Exception as e:
                logger.error(f"Failed to import data: {e}")
                self.after(0, lambda: self._on_import_error(str(e)))

        thread = threading.Thread(target=import_task, daemon=True)
        thread.start()

    def _on_import_success(self, result: dict):
        """インポート成功"""
        self.progress_bar.stop()
        self.progress_bar.pack_forget()

        choices = result.get("hospital_choices", {})
        weights = result.get("factor_weights", {})

        # 結果表示
        result_text = ctk.CTkLabel(
            self.result_frame,
            text="📊 インポート結果",
            font=(Fonts.FAMILY, Fonts.BODY, Fonts.BOLD),
            text_color=Colors.TEXT_PRIMARY,
            anchor="w"
        )
        result_text.pack(fill="x", pady=(0, Spacing.PADDING_SMALL))

        # 病院希望
        choices_label = ctk.CTkLabel(
            self.result_frame,
            text=f"🏥 病院希望: {choices.get('imported', 0)} 件インポート",
            font=(Fonts.FAMILY, Fonts.BODY),
            text_color=Colors.SUCCESS,
            anchor="w"
        )
        choices_label.pack(fill="x")

        if choices.get("errors"):
            for error in choices["errors"][:5]:
                error_label = ctk.CTkLabel(
                    self.result_frame,
                    text=f"  ⚠️ {error}",
                    font=(Fonts.FAMILY, Fonts.SMALL),
                    text_color=Colors.WARNING,
                    anchor="w"
                )
                error_label.pack(fill="x")

        # 要素重み
        weights_label = ctk.CTkLabel(
            self.result_frame,
            text=f"⚖️ 要素重み: {weights.get('imported', 0)} 件インポート",
            font=(Fonts.FAMILY, Fonts.BODY),
            text_color=Colors.SUCCESS,
            anchor="w"
        )
        weights_label.pack(fill="x", pady=(Spacing.PADDING_SMALL, 0))

        if weights.get("errors"):
            for error in weights["errors"][:5]:
                error_label = ctk.CTkLabel(
                    self.result_frame,
                    text=f"  ⚠️ {error}",
                    font=(Fonts.FAMILY, Fonts.SMALL),
                    text_color=Colors.WARNING,
                    anchor="w"
                )
                error_label.pack(fill="x")

        self.progress_label.configure(
            text="✅ インポートが完了しました",
            text_color=Colors.SUCCESS
        )

        # 状況更新
        self._update_status()

        logger.info(f"Import completed: choices={choices.get('imported', 0)}, weights={weights.get('imported', 0)}")

    def _on_import_error(self, error: str):
        """インポートエラー"""
        self.progress_bar.stop()
        self.progress_bar.pack_forget()

        self.progress_label.configure(
            text=f"❌ エラー: {error}",
            text_color=Colors.ERROR
        )
