"""
ダッシュボードビュー
"""
import customtkinter as ctk
from typing import Dict, List
from config.constants import Colors, Fonts, Spacing
from services.dashboard_service import dashboard_service
from utils.logger import get_logger

logger = get_logger(__name__)


class DashboardView(ctk.CTkFrame):
    """ダッシュボードビュー"""
    
    def __init__(self, parent):
        super().__init__(parent, fg_color=Colors.BG_MAIN)
        
        # スクロール可能なフレームを作成
        self.scrollable_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=Colors.BG_MAIN
        )
        self.scrollable_frame.pack(fill="both", expand=True, padx=Spacing.PADDING_LARGE, pady=Spacing.PADDING_LARGE)
        
        # コンテンツを構築
        self._create_header()
        self._create_metrics_section()
        self._create_alerts_section()
        self._create_capacity_section()
        self._create_activities_section()
        
        # データを読み込み
        self._load_data()
        
        logger.info("Dashboard view initialized")
    
    def _create_header(self):
        """ヘッダーを作成"""
        header_frame = ctk.CTkFrame(
            self.scrollable_frame,
            fg_color="transparent"
        )
        header_frame.pack(fill="x", pady=(0, Spacing.MARGIN_SECTION))
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="📊 ダッシュボード",
            font=(Fonts.FAMILY, Fonts.TITLE, Fonts.BOLD),
            text_color=Colors.TEXT_PRIMARY
        )
        title_label.pack(side="left")
        
        # 更新ボタン
        refresh_button = ctk.CTkButton(
            header_frame,
            text="🔄 更新",
            font=(Fonts.FAMILY, Fonts.BODY),
            fg_color=Colors.PRIMARY,
            hover_color=Colors.PRIMARY_HOVER,
            corner_radius=Spacing.RADIUS_BUTTON,
            width=100,
            command=self._load_data
        )
        refresh_button.pack(side="right")
    
    def _create_metrics_section(self):
        """メトリクスセクションを作成"""
        section_frame = ctk.CTkFrame(
            self.scrollable_frame,
            fg_color="transparent"
        )
        section_frame.pack(fill="x", pady=(0, Spacing.MARGIN_SECTION))
        
        # メトリクスカードを配置するグリッド
        self.metrics_frame = ctk.CTkFrame(
            section_frame,
            fg_color="transparent"
        )
        self.metrics_frame.pack(fill="x")
        
        # 4列のグリッドレイアウト
        for i in range(4):
            self.metrics_frame.grid_columnconfigure(i, weight=1, uniform="metrics")
    
    def _create_alerts_section(self):
        """アラートセクションを作成"""
        section_label = ctk.CTkLabel(
            self.scrollable_frame,
            text="⚠️ アラート",
            font=(Fonts.FAMILY, Fonts.SUBTITLE, Fonts.BOLD),
            text_color=Colors.TEXT_PRIMARY,
            anchor="w"
        )
        section_label.pack(fill="x", pady=(0, Spacing.PADDING_SMALL))
        
        self.alerts_frame = ctk.CTkFrame(
            self.scrollable_frame,
            fg_color=Colors.BG_CARD,
            corner_radius=Spacing.RADIUS_CARD
        )
        self.alerts_frame.pack(fill="x", pady=(0, Spacing.MARGIN_SECTION))
    
    def _create_capacity_section(self):
        """受入状況セクションを作成"""
        section_label = ctk.CTkLabel(
            self.scrollable_frame,
            text="📊 受入状況",
            font=(Fonts.FAMILY, Fonts.SUBTITLE, Fonts.BOLD),
            text_color=Colors.TEXT_PRIMARY,
            anchor="w"
        )
        section_label.pack(fill="x", pady=(0, Spacing.PADDING_SMALL))
        
        self.capacity_frame = ctk.CTkFrame(
            self.scrollable_frame,
            fg_color=Colors.BG_CARD,
            corner_radius=Spacing.RADIUS_CARD
        )
        self.capacity_frame.pack(fill="x", pady=(0, Spacing.MARGIN_SECTION))
    
    def _create_activities_section(self):
        """アクティビティセクションを作成"""
        section_label = ctk.CTkLabel(
            self.scrollable_frame,
            text="📋 最近のアクティビティ",
            font=(Fonts.FAMILY, Fonts.SUBTITLE, Fonts.BOLD),
            text_color=Colors.TEXT_PRIMARY,
            anchor="w"
        )
        section_label.pack(fill="x", pady=(0, Spacing.PADDING_SMALL))
        
        self.activities_frame = ctk.CTkFrame(
            self.scrollable_frame,
            fg_color=Colors.BG_CARD,
            corner_radius=Spacing.RADIUS_CARD
        )
        self.activities_frame.pack(fill="both", expand=True)
    
    def _load_data(self):
        """データを読み込み"""
        logger.info("Loading dashboard data")
        
        try:
            # メトリクス
            metrics = dashboard_service.get_metrics()
            self._update_metrics(metrics)
            
            # アラート
            alerts = dashboard_service.get_alerts()
            self._update_alerts(alerts)
            
            # 受入状況
            capacity = dashboard_service.get_capacity_status()
            self._update_capacity(capacity)
            
            # アクティビティ
            activities = dashboard_service.get_recent_activities(limit=10)
            self._update_activities(activities)
            
            logger.info("Dashboard data loaded successfully")
        
        except Exception as e:
            logger.error(f"Failed to load dashboard data: {e}")
    
    def _update_metrics(self, metrics: Dict):
        """メトリクスカードを更新"""
        # 既存のカードをクリア
        for widget in self.metrics_frame.winfo_children():
            widget.destroy()
        
        # カード定義
        cards = [
            {
                "icon": "🏥",
                "label": "病院数",
                "value": str(metrics["hospital_count"]),
                "color": Colors.PRIMARY
            },
            {
                "icon": "👥",
                "label": "職員数",
                "value": str(metrics["staff_count"]),
                "color": Colors.INFO
            },
            {
                "icon": "🎓",
                "label": "選考医",
                "value": str(metrics["resident_count"]),
                "color": Colors.WARNING
            },
            {
                "icon": "📍",
                "label": "配置済み",
                "value": f"{metrics['assigned_count']}/{metrics['resident_count']}",
                "color": Colors.SUCCESS
            },
        ]
        
        # カードを作成
        for i, card_data in enumerate(cards):
            card = self._create_metric_card(
                icon=card_data["icon"],
                label=card_data["label"],
                value=card_data["value"],
                color=card_data["color"]
            )
            card.grid(row=0, column=i, padx=Spacing.PADDING_SMALL, pady=Spacing.PADDING_SMALL, sticky="ew")
    
    def _create_metric_card(self, icon: str, label: str, value: str, color: str) -> ctk.CTkFrame:
        """メトリクスカードを作成"""
        card = ctk.CTkFrame(
            self.metrics_frame,
            fg_color=Colors.BG_CARD,
            corner_radius=Spacing.RADIUS_CARD
        )
        
        # アイコン
        icon_label = ctk.CTkLabel(
            card,
            text=icon,
            font=(Fonts.FAMILY, 32),
            text_color=color
        )
        icon_label.pack(pady=(Spacing.PADDING_MEDIUM, Spacing.PADDING_XSMALL))
        
        # 値
        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=(Fonts.FAMILY, 24, Fonts.BOLD),
            text_color=Colors.TEXT_PRIMARY
        )
        value_label.pack()
        
        # ラベル
        label_label = ctk.CTkLabel(
            card,
            text=label,
            font=(Fonts.FAMILY, Fonts.CAPTION),
            text_color=Colors.TEXT_SECONDARY
        )
        label_label.pack(pady=(Spacing.PADDING_XSMALL, Spacing.PADDING_MEDIUM))
        
        return card
    
    def _update_alerts(self, alerts: List[Dict]):
        """アラートを更新"""
        # 既存のアラートをクリア
        for widget in self.alerts_frame.winfo_children():
            widget.destroy()
        
        if not alerts:
            no_alert = ctk.CTkLabel(
                self.alerts_frame,
                text="アラートはありません",
                font=(Fonts.FAMILY, Fonts.BODY),
                text_color=Colors.TEXT_SECONDARY
            )
            no_alert.pack(pady=Spacing.PADDING_MEDIUM)
            return
        
        # アラートを表示
        for alert in alerts:
            alert_frame = ctk.CTkFrame(
                self.alerts_frame,
                fg_color="transparent"
            )
            alert_frame.pack(fill="x", padx=Spacing.PADDING_MEDIUM, pady=Spacing.PADDING_SMALL)
            
            # アイコン + メッセージ
            alert_label = ctk.CTkLabel(
                alert_frame,
                text=f"{alert['icon']} {alert['message']}",
                font=(Fonts.FAMILY, Fonts.BODY),
                text_color=Colors.TEXT_PRIMARY,
                anchor="w"
            )
            alert_label.pack(side="left", fill="x", expand=True)
    
    def _update_capacity(self, capacity: Dict):
        """受入状況を更新"""
        # 既存のコンテンツをクリア
        for widget in self.capacity_frame.winfo_children():
            widget.destroy()
        
        content_frame = ctk.CTkFrame(
            self.capacity_frame,
            fg_color="transparent"
        )
        content_frame.pack(fill="x", padx=Spacing.PADDING_MEDIUM, pady=Spacing.PADDING_MEDIUM)
        
        # 統計情報
        stats_text = (
            f"総受入人数: {capacity['total_capacity']}人 | "
            f"配置済み: {capacity['used_capacity']}人 | "
            f"空き: {capacity['available_capacity']}人 | "
            f"使用率: {capacity['utilization_rate']}%"
        )
        
        stats_label = ctk.CTkLabel(
            content_frame,
            text=stats_text,
            font=(Fonts.FAMILY, Fonts.BODY),
            text_color=Colors.TEXT_PRIMARY
        )
        stats_label.pack()
        
        # プログレスバー
        if capacity['total_capacity'] > 0:
            progress_value = capacity['used_capacity'] / capacity['total_capacity']
            
            progress = ctk.CTkProgressBar(
                content_frame,
                width=400,
                height=20,
                progress_color=Colors.PRIMARY
            )
            progress.pack(pady=(Spacing.PADDING_SMALL, 0))
            progress.set(progress_value)
    
    def _update_activities(self, activities: List[Dict]):
        """アクティビティを更新"""
        # 既存のアクティビティをクリア
        for widget in self.activities_frame.winfo_children():
            widget.destroy()
        
        if not activities:
            no_activity = ctk.CTkLabel(
                self.activities_frame,
                text="アクティビティはありません",
                font=(Fonts.FAMILY, Fonts.BODY),
                text_color=Colors.TEXT_SECONDARY
            )
            no_activity.pack(pady=Spacing.PADDING_MEDIUM)
            return
        
        # アクティビティを表示
        for activity in activities:
            activity_frame = ctk.CTkFrame(
                self.activities_frame,
                fg_color="transparent"
            )
            activity_frame.pack(fill="x", padx=Spacing.PADDING_MEDIUM, pady=Spacing.PADDING_SMALL)
            
            # タイムスタンプ
            timestamp_str = activity["timestamp"].strftime("%Y-%m-%d %H:%M")
            
            timestamp_label = ctk.CTkLabel(
                activity_frame,
                text=timestamp_str,
                font=(Fonts.FAMILY, Fonts.SMALL),
                text_color=Colors.TEXT_SECONDARY,
                width=140,
                anchor="w"
            )
            timestamp_label.pack(side="left")
            
            # アイコン + メッセージ
            message_label = ctk.CTkLabel(
                activity_frame,
                text=f"{activity['icon']} {activity['message']}",
                font=(Fonts.FAMILY, Fonts.BODY),
                text_color=Colors.TEXT_PRIMARY,
                anchor="w"
            )
            message_label.pack(side="left", fill="x", expand=True)
