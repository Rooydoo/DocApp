"""
質問項目集計・スプレッドシートエクスポート画面
病院希望、要素重み、医局側評価の集計データを閲覧・エクスポート
"""
import threading
import webbrowser
import customtkinter as ctk
from typing import Dict, Any, Optional, List
from config.constants import Colors, Fonts, Spacing
from services.config_service import config_service
from services.survey_export_service import survey_export_service
from utils.logger import get_logger

logger = get_logger(__name__)


class SurveySummaryView(ctk.CTkFrame):
    """
    質問項目集計画面

    サブタブ:
    - 病院希望一覧
    - 要素重み一覧
    - 医局側評価一覧
    - 病院人気度
    """

    def __init__(self, parent):
        super().__init__(parent, fg_color=Colors.BG_MAIN)

        self.fiscal_year = config_service.get_fiscal_year()
        self.summaries: Optional[Dict[str, Dict[str, Any]]] = None
        self.current_tab = "hospital_choices"

        # UI構築
        self._create_header()
        self._create_tab_bar()
        self._create_content_area()

        # データ読み込み
        self._load_data()

        logger.info("SurveySummaryView initialized")

    def _create_header(self):
        """ヘッダーを作成"""
        header_frame = ctk.CTkFrame(self, fg_color="transparent", height=80)
        header_frame.pack(fill="x", padx=Spacing.PADDING_LARGE, pady=(Spacing.PADDING_LARGE, 0))
        header_frame.pack_propagate(False)

        # タイトル
        title_label = ctk.CTkLabel(
            header_frame,
            text="質問項目集計",
            font=(Fonts.FAMILY, Fonts.TITLE, Fonts.BOLD),
            text_color=Colors.TEXT_PRIMARY,
            anchor="w"
        )
        title_label.pack(side="left", pady=Spacing.PADDING_MEDIUM)

        # 右側: 年度表示 + アクションボタン
        action_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        action_frame.pack(side="right", pady=Spacing.PADDING_MEDIUM)

        year_label = ctk.CTkLabel(
            action_frame,
            text=f"{self.fiscal_year}年度",
            font=(Fonts.FAMILY, Fonts.BODY),
            text_color=Colors.TEXT_SECONDARY
        )
        year_label.pack(side="left", padx=(0, Spacing.PADDING_MEDIUM))

        # 更新ボタン
        refresh_btn = ctk.CTkButton(
            action_frame,
            text="更新",
            font=(Fonts.FAMILY, Fonts.BODY),
            fg_color=Colors.INFO,
            hover_color=Colors.PRIMARY_HOVER,
            width=100,
            height=36,
            command=self._load_data
        )
        refresh_btn.pack(side="left", padx=4)

        # スプレッドシートエクスポートボタン
        self.export_btn = ctk.CTkButton(
            action_frame,
            text="Sheets出力",
            font=(Fonts.FAMILY, Fonts.BODY, Fonts.BOLD),
            fg_color=Colors.SUCCESS,
            hover_color="#219a52",
            width=140,
            height=36,
            command=self._on_export
        )
        self.export_btn.pack(side="left", padx=4)

    def _create_tab_bar(self):
        """サブタブバーを作成"""
        tab_frame = ctk.CTkFrame(
            self,
            fg_color=Colors.MEDIUM_GRAY,
            height=46
        )
        tab_frame.pack(fill="x", padx=Spacing.PADDING_LARGE, pady=(Spacing.PADDING_MEDIUM, 0))
        tab_frame.pack_propagate(False)

        self.tabs = [
            ("hospital_choices", "病院希望"),
            ("factor_weights", "要素重み"),
            ("admin_evaluations", "医局側評価"),
            ("popularity", "病院人気度"),
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
                height=46,
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
            fill="both", expand=True,
            padx=Spacing.PADDING_LARGE,
            pady=Spacing.PADDING_MEDIUM
        )

    def _switch_tab(self, tab_id: str):
        """タブを切り替え"""
        self.current_tab = tab_id
        self._update_tab_appearance()
        self._render_current_tab()

    def _update_tab_appearance(self):
        """タブの見た目を更新"""
        for tab_id, btn in self.tab_buttons.items():
            if tab_id == self.current_tab:
                btn.configure(fg_color=Colors.PRIMARY, text_color=Colors.TEXT_WHITE)
            else:
                btn.configure(fg_color=Colors.MEDIUM_GRAY, text_color=Colors.LIGHT_GRAY)

    def _load_data(self):
        """集計データを読み込み"""
        self._clear_content()
        loading_label = ctk.CTkLabel(
            self.content_frame,
            text="データを読み込み中...",
            font=(Fonts.FAMILY, Fonts.BODY),
            text_color=Colors.TEXT_SECONDARY
        )
        loading_label.pack(expand=True)

        try:
            self.summaries = survey_export_service.get_all_summaries(self.fiscal_year)
            self._render_current_tab()
        except Exception as e:
            self._clear_content()
            error_label = ctk.CTkLabel(
                self.content_frame,
                text=f"データ読み込みエラー: {str(e)}",
                font=(Fonts.FAMILY, Fonts.BODY),
                text_color=Colors.ERROR
            )
            error_label.pack(expand=True)
            logger.error(f"Failed to load survey data: {e}")

    def _clear_content(self):
        """コンテンツをクリア"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def _render_current_tab(self):
        """現在のタブの内容を描画"""
        self._clear_content()

        if not self.summaries:
            return

        data = self.summaries.get(self.current_tab)
        if not data:
            return

        # 統計情報セクション
        stats = data.get("stats")
        if stats:
            self._render_stats(stats)

        # テーブルセクション
        headers = data.get("headers", [])
        rows = data.get("rows", [])
        self._render_table(headers, rows)

    def _render_stats(self, stats: Dict[str, Any]):
        """統計情報を描画"""
        stats_frame = ctk.CTkFrame(
            self.content_frame,
            fg_color=Colors.BG_MAIN,
            corner_radius=Spacing.RADIUS_CARD
        )
        stats_frame.pack(fill="x", padx=Spacing.PADDING_MEDIUM, pady=Spacing.PADDING_MEDIUM)

        # タブ別の統計表示
        if self.current_tab == "hospital_choices":
            self._render_choice_stats(stats_frame, stats)
        elif self.current_tab == "factor_weights":
            self._render_weight_stats(stats_frame, stats)
        elif self.current_tab == "admin_evaluations":
            self._render_eval_stats(stats_frame, stats)

    def _render_choice_stats(self, parent, stats: Dict[str, Any]):
        """病院希望の統計"""
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=Spacing.PADDING_MEDIUM, pady=Spacing.PADDING_SMALL)

        total = stats.get("total_staff", 0)
        with_choices = stats.get("staff_with_choices", 0)

        self._add_stat_badge(row, "対象選考医", str(total))
        self._add_stat_badge(row, "希望入力済", str(with_choices))
        self._add_stat_badge(row, "未入力", str(total - with_choices))

        # 人気病院
        popularity = stats.get("popularity", {})
        if popularity:
            pop_frame = ctk.CTkFrame(parent, fg_color="transparent")
            pop_frame.pack(fill="x", padx=Spacing.PADDING_MEDIUM, pady=(0, Spacing.PADDING_SMALL))

            pop_label = ctk.CTkLabel(
                pop_frame,
                text="人気病院: " + ", ".join(
                    f"{name}({count})" for name, count in list(popularity.items())[:5]
                ),
                font=(Fonts.FAMILY, Fonts.SMALL),
                text_color=Colors.TEXT_SECONDARY,
                anchor="w"
            )
            pop_label.pack(fill="x")

    def _render_weight_stats(self, parent, stats: Dict[str, Any]):
        """要素重みの統計"""
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=Spacing.PADDING_MEDIUM, pady=Spacing.PADDING_SMALL)

        count = stats.get("count_with_weights", 0)
        self._add_stat_badge(row, "入力済み", str(count))

        # 要素平均
        averages = stats.get("factor_averages", {})
        if averages:
            avg_frame = ctk.CTkFrame(parent, fg_color="transparent")
            avg_frame.pack(fill="x", padx=Spacing.PADDING_MEDIUM, pady=(0, Spacing.PADDING_SMALL))

            avg_text = "平均重み: " + ", ".join(
                f"{name}: {val}" for name, val in averages.items()
            )
            avg_label = ctk.CTkLabel(
                avg_frame,
                text=avg_text,
                font=(Fonts.FAMILY, Fonts.SMALL),
                text_color=Colors.TEXT_SECONDARY,
                anchor="w",
                wraplength=800
            )
            avg_label.pack(fill="x")

    def _render_eval_stats(self, parent, stats: Dict[str, Any]):
        """医局側評価の統計"""
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=Spacing.PADDING_MEDIUM, pady=Spacing.PADDING_SMALL)

        count = stats.get("count_with_evals", 0)
        self._add_stat_badge(row, "評価入力済み", str(count))

        averages = stats.get("factor_averages", {})
        if averages:
            avg_frame = ctk.CTkFrame(parent, fg_color="transparent")
            avg_frame.pack(fill="x", padx=Spacing.PADDING_MEDIUM, pady=(0, Spacing.PADDING_SMALL))

            avg_text = "平均評価: " + ", ".join(
                f"{name}: {val}" for name, val in averages.items()
            )
            avg_label = ctk.CTkLabel(
                avg_frame,
                text=avg_text,
                font=(Fonts.FAMILY, Fonts.SMALL),
                text_color=Colors.TEXT_SECONDARY,
                anchor="w",
                wraplength=800
            )
            avg_label.pack(fill="x")

    def _add_stat_badge(self, parent, label: str, value: str):
        """統計バッジを追加"""
        badge = ctk.CTkFrame(parent, fg_color=Colors.BG_CARD, corner_radius=6)
        badge.pack(side="left", padx=4, pady=4)

        lbl = ctk.CTkLabel(
            badge,
            text=f"{label}: {value}",
            font=(Fonts.FAMILY, Fonts.BODY, Fonts.BOLD),
            text_color=Colors.TEXT_PRIMARY
        )
        lbl.pack(padx=Spacing.PADDING_MEDIUM, pady=Spacing.PADDING_XSMALL)

    def _render_table(self, headers: List[str], rows: List[List[str]]):
        """テーブルを描画"""
        if not headers:
            return

        # スクロール可能フレーム
        table_frame = ctk.CTkScrollableFrame(
            self.content_frame,
            fg_color="transparent"
        )
        table_frame.pack(fill="both", expand=True, padx=Spacing.PADDING_MEDIUM, pady=(0, Spacing.PADDING_MEDIUM))

        num_cols = len(headers)

        # 列幅を設定
        for col_idx in range(num_cols):
            table_frame.grid_columnconfigure(col_idx, weight=1, minsize=100)

        # ヘッダー行
        for col_idx, header in enumerate(headers):
            cell = ctk.CTkLabel(
                table_frame,
                text=header,
                font=(Fonts.FAMILY, Fonts.SMALL, Fonts.BOLD),
                text_color=Colors.TEXT_WHITE,
                fg_color=Colors.PRIMARY,
                corner_radius=0,
                anchor="center",
                height=32
            )
            cell.grid(row=0, column=col_idx, sticky="nsew", padx=1, pady=1)

        # データ行
        if not rows:
            no_data = ctk.CTkLabel(
                table_frame,
                text="データがありません",
                font=(Fonts.FAMILY, Fonts.BODY),
                text_color=Colors.TEXT_SECONDARY
            )
            no_data.grid(row=1, column=0, columnspan=num_cols, pady=Spacing.PADDING_LARGE)
            return

        for row_idx, row in enumerate(rows):
            bg_color = Colors.BG_CARD if row_idx % 2 == 0 else Colors.BG_MAIN
            for col_idx in range(num_cols):
                value = row[col_idx] if col_idx < len(row) else ""
                cell = ctk.CTkLabel(
                    table_frame,
                    text=value,
                    font=(Fonts.FAMILY, Fonts.SMALL),
                    text_color=Colors.TEXT_PRIMARY,
                    fg_color=bg_color,
                    corner_radius=0,
                    anchor="center",
                    height=28
                )
                cell.grid(row=row_idx + 1, column=col_idx, sticky="nsew", padx=1, pady=0)

    def _on_export(self):
        """スプレッドシートにエクスポート"""
        self.export_btn.configure(text="出力中...", state="disabled")

        def do_export():
            try:
                url = survey_export_service.export_to_spreadsheet(self.fiscal_year)
                self.after(0, lambda: self._on_export_complete(url))
            except Exception as e:
                self.after(0, lambda: self._on_export_error(str(e)))

        thread = threading.Thread(target=do_export, daemon=True)
        thread.start()

    def _on_export_complete(self, url: Optional[str]):
        """エクスポート完了"""
        self.export_btn.configure(text="Sheets出力", state="normal")

        if url:
            # URLを開くか確認
            dialog = ctk.CTkInputDialog(
                text=f"スプレッドシートを作成しました。\n\nブラウザで開く場合は「開く」と入力してください。\n\nURL: {url}",
                title="エクスポート完了"
            )
            result = dialog.get_input()
            if result and result.strip() == "開く":
                webbrowser.open(url)
        else:
            self._show_error("スプレッドシートの作成に失敗しました。\nAPI設定を確認してください。")

    def _on_export_error(self, error_msg: str):
        """エクスポートエラー"""
        self.export_btn.configure(text="Sheets出力", state="normal")
        self._show_error(f"エクスポートに失敗しました:\n{error_msg}")

    def _show_error(self, message: str):
        """エラーメッセージを表示"""
        dialog = ctk.CTkInputDialog(
            text=f"{message}",
            title="エラー"
        )
        dialog.get_input()
