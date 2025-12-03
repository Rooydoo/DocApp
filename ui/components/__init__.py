"""
UI共通コンポーネント
"""
from ui.components.table_view import TableView, TableColumn as TableColumnOld
from ui.components.scrollable_table import ScrollableTable, TableColumn
from ui.components.form_dialog import FormDialog, FormField, FieldType

__all__ = [
    "TableView",  # 旧版（後方互換性のため残す）
    "TableColumnOld",  # 旧版の列定義
    "ScrollableTable",  # 新版（推奨）
    "TableColumn",  # 新版の列定義
    "FormDialog",
    "FormField",
    "FieldType",
]