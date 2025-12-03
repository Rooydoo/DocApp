"""
横・縦スクロール対応の汎用テーブルコンポーネント
Canvas + Scrollbar実装
"""
import customtkinter as ctk
import tkinter as tk
from typing import Callable, Optional, Any, List
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
        min_width: int = 50,
        sortable: bool = True,
        formatter: Optional[Callable[[Any], str]] = None
    ):
        """
        Args:
            key: データのキー名（モデルの属性名）
            label: 列ヘッダーに表示するラベル
            width: 列の初期幅（ピクセル）
            min_width: 列の最小幅
            sortable: ソート可能かどうか
            formatter: 値を文字列に変換する関数
        """
        self.key = key
        self.label = label
        self.width = width
        self.min_width = min_width
        self.sortable = sortable
        self.formatter = formatter or str


class ScrollableTable(ctk.CTkFrame):
    """
    横・縦スクロール対応テーブル
    
    特徴:
    - 横・縦の両方向にスクロール可能
    - 列幅をドラッグでリサイズ可能
    - 行選択、ソート機能
    
    使用例:
        columns = [
            TableColumn("id", "ID", width=60),
            TableColumn("name", "病院名", width=200),
        ]
        table = ScrollableTable(parent, columns=columns)
        table.set_data(hospitals)
        table.on_row_select(callback)
    """
    
    ROW_HEIGHT = 40
    HEADER_HEIGHT = 44
    
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
        
        # コールバック
        self._on_select_callback: Optional[Callable[[Any], None]] = None
        
        # ソート状態
        self.sort_key: Optional[str] = None
        self.sort_reverse: bool = False
        
        # リサイズ状態
        self.resizing_column: Optional[int] = None
        self.resize_start_x: Optional[int] = None
        self.resize_start_width: Optional[int] = None
        
        # UI構築
        self._create_widgets()
        
        logger.debug(f"ScrollableTable initialized with {len(columns)} columns")
    
    def _create_widgets(self):
        """ウィジェットを作成"""
        # ヘッダーフレーム
        self.header_frame = ctk.CTkFrame(
            self,
            fg_color=Colors.DARK_GRAY,
            height=self.HEADER_HEIGHT
        )
        self.header_frame.pack(fill="x", padx=0, pady=0)
        self.header_frame.pack_propagate(False)
        
        # ヘッダーキャンバス
        self.header_canvas = tk.Canvas(
            self.header_frame,
            bg=Colors.DARK_GRAY,
            highlightthickness=0,
            height=self.HEADER_HEIGHT
        )
        self.header_canvas.pack(side="left", fill="both", expand=True)
        
        # データフレーム（スクロール領域）
        data_container = ctk.CTkFrame(self, fg_color="transparent")
        data_container.pack(fill="both", expand=True, padx=0, pady=0)
        
        # データキャンバス
        self.data_canvas = tk.Canvas(
            data_container,
            bg=Colors.BG_CARD,
            highlightthickness=0
        )
        
        # スクロールバー
        self.v_scrollbar = ctk.CTkScrollbar(
            data_container,
            orientation="vertical",
            command=self.data_canvas.yview
        )
        self.h_scrollbar = ctk.CTkScrollbar(
            data_container,
            orientation="horizontal",
            command=self._on_h_scroll
        )
        
        self.data_canvas.configure(
            yscrollcommand=self.v_scrollbar.set,
            xscrollcommand=self.h_scrollbar.set
        )
        
        # レイアウト
        self.data_canvas.grid(row=0, column=0, sticky="nsew")
        self.v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        data_container.grid_rowconfigure(0, weight=1)
        data_container.grid_columnconfigure(0, weight=1)
        
        # データ用内部フレーム
        self.data_inner_frame = ctk.CTkFrame(
            self.data_canvas,
            fg_color="transparent"
        )
        self.data_canvas_window = self.data_canvas.create_window(
            (0, 0),
            window=self.data_inner_frame,
            anchor="nw"
        )
        
        # イベントバインディング
        self.data_inner_frame.bind("<Configure>", self._on_frame_configure)
        self.data_canvas.bind("<Configure>", self._on_canvas_configure)
        self.header_canvas.bind("<ButtonPress-1>", self._on_header_click)
        self.header_canvas.bind("<B1-Motion>", self._on_header_drag)
        self.header_canvas.bind("<ButtonRelease-1>", self._on_header_release)
        self.header_canvas.bind("<Motion>", self._on_header_motion)
        
        # 初期ヘッダー描画
        self._draw_header()
    
    def _draw_header(self):
        """ヘッダーを描画"""
        self.header_canvas.delete("all")
        
        x = 0
        for i, col in enumerate(self.columns):
            # ヘッダー背景
            self.header_canvas.create_rectangle(
                x, 0, x + col.width, self.HEADER_HEIGHT,
                fill=Colors.DARK_GRAY,
                outline=Colors.MEDIUM_GRAY,
                tags=f"header_{i}"
            )
            
            # ヘッダーテキスト
            text = col.label
            if self.sort_key == col.key:
                text += " ▼" if self.sort_reverse else " ▲"
            
            self.header_canvas.create_text(
                x + 10, self.HEADER_HEIGHT // 2,
                text=text,
                anchor="w",
                fill="white",
                font=(Fonts.FAMILY, Fonts.CAPTION, Fonts.BOLD),
                tags=f"header_text_{i}"
            )
            
            # リサイズハンドル
            self.header_canvas.create_rectangle(
                x + col.width - 3, 0,
                x + col.width + 3, self.HEADER_HEIGHT,
                fill="",
                outline="",
                tags=f"resize_{i}"
            )
            
            x += col.width
        
        # 総幅を設定
        total_width = sum(col.width for col in self.columns)
        self.header_canvas.configure(scrollregion=(0, 0, total_width, self.HEADER_HEIGHT))
    
    def _draw_rows(self):
        """データ行を描画"""
        # 既存の行を削除
        for widget in self.data_inner_frame.winfo_children():
            widget.destroy()
        
        # データがない場合
        if not self.data:
            empty_label = ctk.CTkLabel(
                self.data_inner_frame,
                text="📭 データがありません",
                font=(Fonts.FAMILY, Fonts.BODY),
                text_color=Colors.TEXT_SECONDARY
            )
            empty_label.pack(pady=40)
            return
        
        # 各行を描画
        for idx, item in enumerate(self.data):
            self._create_row(item, idx)
    
    def _create_row(self, item: Any, index: int):
        """データ行を作成"""
        bg_color = Colors.BG_CARD if index % 2 == 0 else Colors.LIGHT_GRAY
        
        # 総幅を計算
        total_width = sum(col.width for col in self.columns)
        
        row_frame = ctk.CTkFrame(
            self.data_inner_frame,
            fg_color=bg_color,
            height=self.ROW_HEIGHT,
            width=total_width
        )
        row_frame.pack(fill="x", pady=1)
        row_frame.pack_propagate(False)
        
        # クリックイベント
        row_frame.bind("<Button-1>", lambda e, i=index: self._on_row_click(i))
        
        # 各列のデータ
        for col in self.columns:
            col_frame = ctk.CTkFrame(
                row_frame,
                fg_color="transparent",
                width=col.width
            )
            col_frame.pack(side="left", fill="y")
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
            label.bind("<Button-1>", lambda e, i=index: self._on_row_click(i))
    
    def _on_frame_configure(self, event=None):
        """フレームサイズ変更時"""
        self.data_canvas.configure(scrollregion=self.data_canvas.bbox("all"))
    
    def _on_canvas_configure(self, event=None):
        """キャンバスサイズ変更時"""
        canvas_width = event.width if event else self.data_canvas.winfo_width()
        total_width = sum(col.width for col in self.columns)
        
        # 内部フレームの幅を調整
        self.data_canvas.itemconfig(
            self.data_canvas_window,
            width=max(canvas_width, total_width)
        )
    
    def _on_h_scroll(self, *args):
        """横スクロール時、ヘッダーも同期"""
        self.data_canvas.xview(*args)
        self.header_canvas.xview(*args)
    
    def _on_header_click(self, event):
        """ヘッダークリック時"""
        x = self.header_canvas.canvasx(event.x)
        
        # リサイズハンドルをクリックしたか確認
        col_x = 0
        for i, col in enumerate(self.columns):
            if abs(x - (col_x + col.width)) < 5:
                # リサイズ開始
                self.resizing_column = i
                self.resize_start_x = x
                self.resize_start_width = col.width
                return
            col_x += col.width
        
        # ソート実行
        col_x = 0
        for col in self.columns:
            if col_x <= x < col_x + col.width:
                if col.sortable:
                    self._sort_by_column(col.key)
                break
            col_x += col.width
    
    def _on_header_drag(self, event):
        """ヘッダードラッグ時（リサイズ）"""
        if self.resizing_column is not None:
            x = self.header_canvas.canvasx(event.x)
            delta = x - self.resize_start_x
            new_width = max(
                self.columns[self.resizing_column].min_width,
                self.resize_start_width + delta
            )
            self.columns[self.resizing_column].width = int(new_width)
            
            # 再描画
            self._draw_header()
            self._draw_rows()
    
    def _on_header_release(self, event):
        """ヘッダーリリース時"""
        self.resizing_column = None
        self.resize_start_x = None
        self.resize_start_width = None
    
    def _on_header_motion(self, event):
        """ヘッダー上でマウス移動時（カーソル変更）"""
        x = self.header_canvas.canvasx(event.x)
        
        # リサイズハンドル付近か確認
        col_x = 0
        for col in self.columns:
            if abs(x - (col_x + col.width)) < 5:
                self.header_canvas.configure(cursor="sb_h_double_arrow")
                return
            col_x += col.width
        
        self.header_canvas.configure(cursor="")
    
    def _on_row_click(self, index: int):
        """行クリック時"""
        self.selected_index = index
        
        # 全行の背景色をリセット
        for i, widget in enumerate(self.data_inner_frame.winfo_children()):
            if isinstance(widget, ctk.CTkFrame):
                bg_color = Colors.BG_CARD if i % 2 == 0 else Colors.LIGHT_GRAY
                if i == index:
                    bg_color = Colors.PRIMARY_HOVER
                widget.configure(fg_color=bg_color)
                
                # ラベルの色も変更
                for child in widget.winfo_children():
                    if isinstance(child, ctk.CTkFrame):
                        for label in child.winfo_children():
                            if isinstance(label, ctk.CTkLabel):
                                text_color = Colors.TEXT_WHITE if i == index else Colors.TEXT_PRIMARY
                                label.configure(text_color=text_color)
        
        # コールバック実行
        if self._on_select_callback and 0 <= index < len(self.data):
            self._on_select_callback(self.data[index])
            logger.debug(f"Row selected: index={index}")
    
    def _sort_by_column(self, key: str):
        """列でソート"""
        if self.sort_key == key:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_key = key
            self.sort_reverse = False
        
        try:
            self.data.sort(
                key=lambda x: getattr(x, key, "") if not isinstance(x, dict) else x.get(key, ""),
                reverse=self.sort_reverse
            )
            self._draw_header()
            self._draw_rows()
            logger.debug(f"Sorted by {key}, reverse={self.sort_reverse}")
        except Exception as e:
            logger.error(f"Sort failed: {e}")
    
    def set_data(self, data: List[Any]):
        """データを設定"""
        self.data = data
        self.selected_index = None
        self._draw_rows()
        logger.debug(f"ScrollableTable data set: {len(data)} rows")
    
    def on_row_select(self, callback: Callable[[Any], None]):
        """行選択時のコールバックを設定"""
        self._on_select_callback = callback
    
    def get_selected(self) -> Optional[Any]:
        """選択中のアイテムを取得"""
        if self.selected_index is not None and 0 <= self.selected_index < len(self.data):
            return self.data[self.selected_index]
        return None
    
    def refresh(self):
        """テーブルを再描画"""
        self._draw_rows()
