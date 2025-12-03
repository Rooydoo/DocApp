"""
専攻医の希望・評価設定ダイアログ
"""
import customtkinter as ctk
from typing import Optional, Dict, List, Callable
from decimal import Decimal
from config.constants import Colors, Fonts, Spacing, FactorType
from database.base import SessionLocal
from database.models.staff import Staff
from database.models.hospital import Hospital
from database.models.evaluation_factor import EvaluationFactor
from repositories.evaluation_factor_repository import EvaluationFactorRepository
from repositories.hospital_repository import HospitalRepository
from repositories.staff_factor_weight_repository import StaffFactorWeightRepository
from repositories.admin_evaluation_repository import AdminEvaluationRepository
from repositories.hospital_choice_repository import HospitalChoiceRepository
from services.config_service import config_service
from utils.logger import get_logger
from utils.exceptions import ValidationException

logger = get_logger(__name__)


class StaffPreferenceDialog(ctk.CTkToplevel):
    """
    専攻医の希望・評価設定ダイアログ

    タブ:
    - 病院希望（第1〜第3希望）
    - 要素重み（合計100）
    - 医局側評価
    """

    def __init__(self, parent, staff: Staff, on_save: Optional[Callable] = None):
        super().__init__(parent)

        self.staff = staff
        self.on_save_callback = on_save
        self.fiscal_year = int(config_service.get(config_service.Keys.FISCAL_YEAR, "2025"))

        # ダイアログ設定
        self.title(f"希望・評価設定 - {staff.name}")
        self.geometry("700x600")
        self.minsize(600, 500)

        # データを読み込み
        self._load_data()

        # UI構築
        self._create_ui()

        # モーダル化
        self.transient(parent)
        self.grab_set()

        logger.info(f"StaffPreferenceDialog opened for {staff.name}")

    def _load_data(self):
        """データを読み込み"""
        with SessionLocal() as db:
            # 病院リスト
            hospital_repo = HospitalRepository(db)
            self.hospitals = hospital_repo.get_all()

            # 評価要素
            factor_repo = EvaluationFactorRepository(db)
            self.staff_factors = factor_repo.get_staff_preference_factors()
            self.admin_factors = factor_repo.get_admin_evaluation_factors()

            # 現在の設定を読み込み
            choice_repo = HospitalChoiceRepository(db)
            self.current_choices = choice_repo.get_choices_as_dict(
                self.staff.id, self.fiscal_year
            )

            weight_repo = StaffFactorWeightRepository(db)
            self.current_weights = weight_repo.get_weights_as_dict(
                self.staff.id, self.fiscal_year
            )

            eval_repo = AdminEvaluationRepository(db)
            self.current_evaluations = eval_repo.get_evaluations_as_dict(
                self.staff.id, self.fiscal_year
            )

    def _create_ui(self):
        """UIを構築"""
        # メインフレーム
        main_frame = ctk.CTkFrame(self, fg_color=Colors.BG_MAIN)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # ヘッダー
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, Spacing.PADDING_MEDIUM))

        title_label = ctk.CTkLabel(
            header_frame,
            text=f"👤 {self.staff.name} の希望・評価設定",
            font=(Fonts.FAMILY, Fonts.TITLE, Fonts.BOLD),
            text_color=Colors.TEXT_PRIMARY
        )
        title_label.pack(side="left")

        year_label = ctk.CTkLabel(
            header_frame,
            text=f"年度: {self.fiscal_year}",
            font=(Fonts.FAMILY, Fonts.BODY),
            text_color=Colors.TEXT_SECONDARY
        )
        year_label.pack(side="right")

        # タブビュー
        self.tabview = ctk.CTkTabview(main_frame, height=400)
        self.tabview.pack(fill="both", expand=True)

        # タブ作成
        self.tabview.add("🏥 病院希望")
        self.tabview.add("⚖️ 要素重み")
        self.tabview.add("📝 医局側評価")

        # 各タブのコンテンツ
        self._create_hospital_choice_tab()
        self._create_weight_tab()
        self._create_evaluation_tab()

        # ボタンフレーム
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(Spacing.PADDING_MEDIUM, 0))

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

    def _create_hospital_choice_tab(self):
        """病院希望タブを作成"""
        tab = self.tabview.tab("🏥 病院希望")

        # 説明
        desc_label = ctk.CTkLabel(
            tab,
            text="第1希望から第3希望まで病院を選択してください。",
            font=(Fonts.FAMILY, Fonts.BODY),
            text_color=Colors.TEXT_SECONDARY
        )
        desc_label.pack(anchor="w", pady=(0, Spacing.PADDING_MEDIUM))

        # 病院選択肢
        hospital_options = ["未選択"] + [h.name for h in self.hospitals]
        hospital_id_map = {h.name: h.id for h in self.hospitals}
        self.hospital_id_map = hospital_id_map

        self.choice_combos: Dict[int, ctk.CTkComboBox] = {}

        for rank in [1, 2, 3]:
            frame = ctk.CTkFrame(tab, fg_color="transparent")
            frame.pack(fill="x", pady=Spacing.PADDING_SMALL)

            label = ctk.CTkLabel(
                frame,
                text=f"第{rank}希望:",
                font=(Fonts.FAMILY, Fonts.BODY, Fonts.BOLD),
                text_color=Colors.TEXT_PRIMARY,
                width=100
            )
            label.pack(side="left")

            combo = ctk.CTkComboBox(
                frame,
                values=hospital_options,
                font=(Fonts.FAMILY, Fonts.BODY),
                width=400,
                height=40
            )
            combo.pack(side="left", padx=Spacing.PADDING_SMALL)

            # 現在の値を設定
            current_hospital_id = self.current_choices.get(rank)
            if current_hospital_id:
                for h in self.hospitals:
                    if h.id == current_hospital_id:
                        combo.set(h.name)
                        break
            else:
                combo.set("未選択")

            self.choice_combos[rank] = combo

    def _create_weight_tab(self):
        """要素重みタブを作成"""
        tab = self.tabview.tab("⚖️ 要素重み")

        # 説明
        desc_frame = ctk.CTkFrame(tab, fg_color="transparent")
        desc_frame.pack(fill="x", pady=(0, Spacing.PADDING_MEDIUM))

        desc_label = ctk.CTkLabel(
            desc_frame,
            text="各要素の重要度を入力してください（合計100になるようにしてください）",
            font=(Fonts.FAMILY, Fonts.BODY),
            text_color=Colors.TEXT_SECONDARY
        )
        desc_label.pack(side="left")

        # 合計表示
        self.total_label = ctk.CTkLabel(
            desc_frame,
            text="合計: 0",
            font=(Fonts.FAMILY, Fonts.BODY, Fonts.BOLD),
            text_color=Colors.TEXT_PRIMARY
        )
        self.total_label.pack(side="right")

        # スクロール可能フレーム
        scroll_frame = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True)

        self.weight_entries: Dict[int, ctk.CTkEntry] = {}

        if not self.staff_factors:
            no_data = ctk.CTkLabel(
                scroll_frame,
                text="評価要素が登録されていません。\n設定画面から評価要素を追加してください。",
                font=(Fonts.FAMILY, Fonts.BODY),
                text_color=Colors.TEXT_SECONDARY
            )
            no_data.pack(pady=Spacing.PADDING_LARGE)
            return

        for factor in self.staff_factors:
            frame = ctk.CTkFrame(scroll_frame, fg_color=Colors.BG_CARD, corner_radius=6)
            frame.pack(fill="x", pady=4)

            # 要素名
            name_label = ctk.CTkLabel(
                frame,
                text=factor.name,
                font=(Fonts.FAMILY, Fonts.BODY, Fonts.BOLD),
                text_color=Colors.TEXT_PRIMARY,
                width=200,
                anchor="w"
            )
            name_label.pack(side="left", padx=Spacing.PADDING_MEDIUM, pady=Spacing.PADDING_SMALL)

            # 説明（あれば）
            if factor.description:
                desc = ctk.CTkLabel(
                    frame,
                    text=factor.description,
                    font=(Fonts.FAMILY, Fonts.SMALL),
                    text_color=Colors.TEXT_SECONDARY,
                    anchor="w"
                )
                desc.pack(side="left", fill="x", expand=True)

            # 入力フィールド
            entry = ctk.CTkEntry(
                frame,
                font=(Fonts.FAMILY, Fonts.BODY),
                width=80,
                height=36,
                placeholder_text="0"
            )
            entry.pack(side="right", padx=Spacing.PADDING_MEDIUM, pady=Spacing.PADDING_SMALL)

            # 現在の値を設定
            current_weight = self.current_weights.get(factor.id, 0)
            if current_weight > 0:
                entry.insert(0, str(int(current_weight)))

            # 入力時に合計を更新
            entry.bind("<KeyRelease>", lambda e: self._update_total())

            self.weight_entries[factor.id] = entry

        # 初期合計を計算
        self._update_total()

    def _update_total(self):
        """重みの合計を更新"""
        total = 0
        for entry in self.weight_entries.values():
            try:
                val = int(entry.get() or "0")
                total += val
            except ValueError:
                pass

        color = Colors.SUCCESS if total == 100 else (Colors.WARNING if total < 100 else Colors.ERROR)
        self.total_label.configure(text=f"合計: {total}", text_color=color)

    def _create_evaluation_tab(self):
        """医局側評価タブを作成"""
        tab = self.tabview.tab("📝 医局側評価")

        # 説明
        desc_label = ctk.CTkLabel(
            tab,
            text="各要素に対して0.0〜1.0の評価値を入力してください。",
            font=(Fonts.FAMILY, Fonts.BODY),
            text_color=Colors.TEXT_SECONDARY
        )
        desc_label.pack(anchor="w", pady=(0, Spacing.PADDING_MEDIUM))

        # スクロール可能フレーム
        scroll_frame = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True)

        self.eval_entries: Dict[int, ctk.CTkEntry] = {}

        if not self.admin_factors:
            no_data = ctk.CTkLabel(
                scroll_frame,
                text="評価要素が登録されていません。\n設定画面から評価要素を追加してください。",
                font=(Fonts.FAMILY, Fonts.BODY),
                text_color=Colors.TEXT_SECONDARY
            )
            no_data.pack(pady=Spacing.PADDING_LARGE)
            return

        for factor in self.admin_factors:
            frame = ctk.CTkFrame(scroll_frame, fg_color=Colors.BG_CARD, corner_radius=6)
            frame.pack(fill="x", pady=4)

            # 要素名
            name_label = ctk.CTkLabel(
                frame,
                text=factor.name,
                font=(Fonts.FAMILY, Fonts.BODY, Fonts.BOLD),
                text_color=Colors.TEXT_PRIMARY,
                width=200,
                anchor="w"
            )
            name_label.pack(side="left", padx=Spacing.PADDING_MEDIUM, pady=Spacing.PADDING_SMALL)

            # 説明（あれば）
            if factor.description:
                desc = ctk.CTkLabel(
                    frame,
                    text=factor.description,
                    font=(Fonts.FAMILY, Fonts.SMALL),
                    text_color=Colors.TEXT_SECONDARY,
                    anchor="w"
                )
                desc.pack(side="left", fill="x", expand=True)

            # 入力フィールド
            entry = ctk.CTkEntry(
                frame,
                font=(Fonts.FAMILY, Fonts.BODY),
                width=80,
                height=36,
                placeholder_text="0.5"
            )
            entry.pack(side="right", padx=Spacing.PADDING_MEDIUM, pady=Spacing.PADDING_SMALL)

            # 現在の値を設定
            current_eval = self.current_evaluations.get(factor.id, 0.5)
            entry.insert(0, str(current_eval))

            self.eval_entries[factor.id] = entry

    def _on_save(self):
        """保存処理"""
        try:
            with SessionLocal() as db:
                # 病院希望を保存
                self._save_hospital_choices(db)

                # 要素重みを保存（登録されている場合のみ）
                if self.staff_factors:
                    self._save_weights(db)

                # 医局側評価を保存（登録されている場合のみ）
                if self.admin_factors:
                    self._save_evaluations(db)

            logger.info(f"Preferences saved for {self.staff.name}")

            if self.on_save_callback:
                self.on_save_callback()

            self.destroy()

        except ValidationException as e:
            self._show_error(str(e))
        except Exception as e:
            self._show_error(f"保存に失敗しました: {str(e)}")
            logger.error(f"Failed to save preferences: {e}")

    def _save_hospital_choices(self, db):
        """病院希望を保存"""
        choices: Dict[int, int] = {}

        for rank, combo in self.choice_combos.items():
            hospital_name = combo.get()
            if hospital_name != "未選択":
                hospital_id = self.hospital_id_map.get(hospital_name)
                if hospital_id:
                    choices[rank] = hospital_id

        if choices:
            repo = HospitalChoiceRepository(db)
            repo.bulk_upsert(self.staff.id, self.fiscal_year, choices)

    def _save_weights(self, db):
        """要素重みを保存"""
        weights: Dict[int, float] = {}

        for factor_id, entry in self.weight_entries.items():
            try:
                val = float(entry.get() or "0")
                weights[factor_id] = val
            except ValueError:
                weights[factor_id] = 0

        # 合計チェック
        total = sum(weights.values())
        if abs(total - 100) > 0.01 and total > 0:
            raise ValidationException(f"要素重みの合計は100である必要があります（現在: {total}）")

        if weights and total > 0:
            repo = StaffFactorWeightRepository(db)
            repo.bulk_upsert(self.staff.id, self.fiscal_year, weights)

    def _save_evaluations(self, db):
        """医局側評価を保存"""
        evaluations: Dict[int, float] = {}

        for factor_id, entry in self.eval_entries.items():
            try:
                val = float(entry.get() or "0.5")
                val = max(0.0, min(1.0, val))  # 0.0-1.0に制限
                evaluations[factor_id] = val
            except ValueError:
                evaluations[factor_id] = 0.5

        if evaluations:
            repo = AdminEvaluationRepository(db)
            repo.bulk_upsert(self.staff.id, self.fiscal_year, evaluations)

    def _show_error(self, message: str):
        """エラーメッセージを表示"""
        dialog = ctk.CTkInputDialog(
            text=f"❌ {message}",
            title="エラー"
        )
        dialog.get_input()
