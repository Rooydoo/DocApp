"""
汎用テーブル表示コンポーネント
一覧表示、ソート、行選択機能を提供
"""
import customtkinter as ctk
from typing import Callable, Optional, Any, List, Dict
from config.constants import Colors, Fonts, Spacing
from utils.logger import get_logger

logger = get_logger(__name__)


class TableColumn:
    """テーブル列定義"""
    
    def __init__(
        self,
        key: str,
        label: str,
        width: int = 100,
        sortable: bool = True,
        formatter: Optional[Callable[[Any], str]] = None
    ):
        """
        Args:
            key: データのキー名（モデルの属性名）
            label: 列ヘッダーに表示するラベル
            width: 列の幅（ピクセル）
            sortable: ソート可能かどうか
            formatter: 値を文字列に変換する関数
        """
        self.key = key
        self.label = label
        self.width = width
        self.sortable = sortable
        self.formatter = formatter or str


class TableView(ctk.CTkScrollableFrame):
    """
    汎用テーブル表示コンポーネント
    
    使用例:
        columns = [
            TableColumn("id", "ID", width=60),
            TableColumn("name", "病院名", width=200),
            TableColumn("capacity", "受入人数", width=100),
        ]
        table = TableView(parent, columns=columns)
        table.set_data(hospitals)
        table.on_row_select(callback)
    """
    
    def __init__(
        self,
        parent,
        columns: List[TableColumn],
        **kwargs
    ):
        """
        Args:
            parent: 親ウィジェット
            columns: 列定義のリスト
            **kwargs: CTkScrollableFrameに渡す追加引数
        """
        super().__init__(
            parent,
            fg_color=Colors.BG_CARD,
            corner_radius=Spacing.RADIUS_CARD,
            **kwargs
        )
        
        self.columns = columns
        self.data: List[Any] = []
        self.selected_index: Optional[int] = None
        self.selected_row_frame: Optional[ctk.CTkFrame] = None
        self.row_frames: List[ctk.CTkFrame] = []
        
        # コールバック
        self._on_select_callback: Optional[Callable[[Any], None]] = None
        
        # ソート状態
        self.sort_key: Optional[str] = None
        self.sort_reverse: bool = False
        
        # ヘッダーを作成
        self._create_header()
        
        logger.debug(f"TableView initialized with {len(columns)} columns")
    
    def _create_header(self):
        """ヘッダー行を作成"""
        # ヘッダーコンテナ（横スクロール可能）
        header_container = ctk.CTkFrame(
            self,
            fg_color=Colors.DARK_GRAY,
            corner_radius=0,
            height=44
        )
        header_container.pack(fill="x", padx=0, pady=(0, 2))
        header_container.pack_propagate(False)
        
        # 総幅を計算
        total_width = sum(col.width for col in self.columns) + len(self.columns) * 4
        
        header_frame = ctk.CTkFrame(
            header_container,
            fg_color="transparent",
            width=total_width
        )
        header_frame.pack(side="left", fill="y")
        header_frame.pack_propagate(False)
        
        for col in self.columns:
            col_frame = ctk.CTkFrame(
                header_frame,
                fg_color="transparent",
                width=col.width
            )
            col_frame.pack(side="left", padx=2, fill="y")
            col_frame.pack_propagate(False)
            
            if col.sortable:
                # ソート可能な列はボタン化
                btn = ctk.CTkButton(
                    col_frame,
                    text=col.label,
                    font=(Fonts.FAMILY, Fonts.CAPTION, Fonts.BOLD),
                    fg_color="transparent",
                    hover_color=Colors.MEDIUM_GRAY,
                    text_color=Colors.TEXT_WHITE,
                    anchor="w",
                    command=lambda k=col.key: self._sort_by_column(k)
                )
                btn.pack(fill="both", expand=True, padx=Spacing.PADDING_SMALL)
            else:
                # ソート不可の列はラベル
                label = ctk.CTkLabel(
                    col_frame,
                    text=col.label,
                    font=(Fonts.FAMILY, Fonts.CAPTION, Fonts.BOLD),
                    text_color=Colors.TEXT_WHITE,
                    anchor="w"
                )
                label.pack(fill="both", expand=True, padx=Spacing.PADDING_SMALL)
    
    def set_data(self, data: List[Any]):
        """
        データを設定して表示
        
        Args:
            data: 表示するデータのリスト（モデルインスタンスやDict）
        """
        self.data = data
        self.selected_index = None
        self.selected_row_frame = None
        self._render_rows()
        logger.debug(f"TableView data set: {len(data)} rows")
    
    def _render_rows(self):
        """データ行を描画"""
        # 既存の行を削除（ヘッダーは残す）
        for frame in self.row_frames:
            frame.destroy()
        self.row_frames.clear()
        
        # データがない場合
        if not self.data:
            empty_frame = ctk.CTkFrame(self, fg_color="transparent")
            empty_frame.pack(fill="both", expand=True, pady=40)
            
            empty_label = ctk.CTkLabel(
                empty_frame,
                text="📭 データがありません",
                font=(Fonts.FAMILY, Fonts.BODY),
                text_color=Colors.TEXT_SECONDARY
            )
            empty_label.pack()
            self.row_frames.append(empty_frame)
            return
        
        # 各行を描画
        for idx, item in enumerate(self.data):
            row_frame = self._create_row(item, idx)
            row_frame.pack(fill="x", padx=0, pady=1)
            self.row_frames.append(row_frame)
    
    def _create_row(self, item: Any, index: int) -> ctk.CTkFrame:
        """
        データ行を作成
        
        Args:
            item: データアイテム（モデルインスタンスやDict）
            index: 行インデックス
            
        Returns:
            CTkFrame: 行フレーム
        """
        # 行の背景色（偶数/奇数で交互）
        bg_color = Colors.BG_CARD if index % 2 == 0 else Colors.LIGHT_GRAY
        
        row_frame = ctk.CTkFrame(
            self,
            fg_color=bg_color,
            corner_radius=0,
            height=40
        )
        row_frame.pack_propagate(False)
        
        # クリックイベント
        row_frame.bind("<Button-1>", lambda e, i=index: self._on_row_click(i))
        
        # 各列のデータを表示
        for col in self.columns:
            col_frame = ctk.CTkFrame(
                row_frame,
                fg_color="transparent",
                width=col.width
            )
            col_frame.pack(side="left", padx=2, fill="y")
            col_frame.pack_propagate(False)
            
            # データ取得
            if isinstance(item, dict):
                value = item.get(col.key, "")
            else:
                value = getattr(item, col.key, "")
            
            # フォーマット適用
            display_text = col.formatter(value)
            
            label = ctk.CTkLabel(
                col_frame,
                text=display_text,
                font=(Fonts.FAMILY, Fonts.BODY),
                text_color=Colors.TEXT_PRIMARY,
                anchor="w"
            )
            label.pack(fill="both", expand=True, padx=Spacing.PADDING_SMALL)
            
            # ラベルにもクリックイベント
            label.bind("<Button-1>", lambda e, i=index: self._on_row_click(i))
        
        return row_frame
    
    def _on_row_click(self, index: int):
        """
        行がクリックされたときの処理
        
        Args:
            index: クリックされた行のインデックス
        """
        # 前回選択行のハイライトを解除
        if self.selected_row_frame:
            bg_color = Colors.BG_CARD if self.selected_index % 2 == 0 else Colors.LIGHT_GRAY
            self.selected_row_frame.configure(fg_color=bg_color)
        
        # 新しい選択行をハイライト
        self.selected_index = index
        self.selected_row_frame = self.row_frames[index]
        self.selected_row_frame.configure(fg_color=Colors.PRIMARY_HOVER)
        
        # すべてのラベルの色を白に変更
        for widget in self.selected_row_frame.winfo_children():
            if isinstance(widget, ctk.CTkFrame):
                for child in widget.winfo_children():
                    if isinstance(child, ctk.CTkLabel):
                        child.configure(text_color=Colors.TEXT_WHITE)
        
        # コールバック実行
        if self._on_select_callback and 0 <= index < len(self.data):
            selected_item = self.data[index]
            self._on_select_callback(selected_item)
            logger.debug(f"Row selected: index={index}")
    
    def _sort_by_column(self, key: str):
        """
        列でソート
        
        Args:
            key: ソートするキー
        """
        # 同じ列を再度クリックした場合は昇順/降順を切り替え
        if self.sort_key == key:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_key = key
            self.sort_reverse = False
        
        # データをソート
        try:
            self.data.sort(
                key=lambda x: getattr(x, key, "") if not isinstance(x, dict) else x.get(key, ""),
                reverse=self.sort_reverse
            )
            self._render_rows()
            logger.debug(f"Sorted by {key}, reverse={self.sort_reverse}")
        except Exception as e:
            logger.error(f"Sort failed: {e}")
    
    def on_row_select(self, callback: Callable[[Any], None]):
        """
        行選択時のコールバックを設定
        
        Args:
            callback: コールバック関数（選択されたアイテムを引数に受け取る）
        """
        self._on_select_callback = callback
    
    def get_selected(self) -> Optional[Any]:
        """
        選択中のアイテムを取得
        
        Returns:
            選択中のアイテム、未選択の場合はNone
        """
        if self.selected_index is not None and 0 <= self.selected_index < len(self.data):
            return self.data[self.selected_index]
        return None
    
    def refresh(self):
        """テーブルを再描画（データは保持）"""
        self._render_rows()
    
    def clear_selection(self):
        """選択を解除"""
        if self.selected_row_frame:
            bg_color = Colors.BG_CARD if self.selected_index % 2 == 0 else Colors.LIGHT_GRAY
            self.selected_row_frame.configure(fg_color=bg_color)
            
            # ラベルの色を元に戻す
            for widget in self.selected_row_frame.winfo_children():
                if isinstance(widget, ctk.CTkFrame):
                    for child in widget.winfo_children():
                        if isinstance(child, ctk.CTkLabel):
                            child.configure(text_color=Colors.TEXT_PRIMARY)
        
        self.selected_index = None
        self.selected_row_frame = None