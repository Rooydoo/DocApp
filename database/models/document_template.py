"""
書類テンプレートテーブルモデル
"""
import json
from typing import List, Dict, Any, Optional
from sqlalchemy import Column, Integer, String, Text
from database.base import Base, TimestampMixin
from config.constants import TableName


class DocumentTemplate(Base, TimestampMixin):
    """
    書類テンプレート

    Word/Excelテンプレートファイルと差し込みフィールドを管理
    """
    __tablename__ = TableName.DOCUMENT_TEMPLATE

    # 主キー
    id = Column(Integer, primary_key=True, autoincrement=True, comment="テンプレートID")

    # テンプレート情報
    name = Column(String(100), nullable=False, unique=True, comment="テンプレート名")
    description = Column(Text, comment="説明")

    # ファイル情報
    file_path = Column(String(500), comment="テンプレートファイルパス")
    file_type = Column(String(10), comment="ファイル種別（docx/xlsx）")

    # テンプレート内容（テキストベースの場合）
    template_content = Column(Text, comment="テンプレート内容")

    # 差し込みフィールド定義（JSON形式）
    # 例: [{"key": "staff_name", "label": "職員名", "source": "staff.name"}, ...]
    placeholders = Column(Text, comment="差し込みフィールド定義（JSON）")

    # Few-shot学習用サンプル（JSON形式で保存）
    fewshot_examples = Column(Text, comment="Few-shot例（JSON）")

    # カテゴリ
    category = Column(String(50), comment="カテゴリ")

    # 備考
    notes = Column(Text, comment="備考")

    def __repr__(self):
        return f"<DocumentTemplate(id={self.id}, name='{self.name}')>"

    def __str__(self):
        return self.name

    @property
    def placeholder_list(self) -> List[Dict[str, Any]]:
        """差し込みフィールド定義をリストで取得"""
        if not self.placeholders:
            return []
        try:
            return json.loads(self.placeholders)
        except json.JSONDecodeError:
            return []

    @placeholder_list.setter
    def placeholder_list(self, value: List[Dict[str, Any]]):
        """差し込みフィールド定義を設定"""
        self.placeholders = json.dumps(value, ensure_ascii=False)

    @property
    def is_file_template(self) -> bool:
        """ファイルベースのテンプレートかどうか"""
        return bool(self.file_path)

    @property
    def is_word(self) -> bool:
        """Wordテンプレートかどうか"""
        return self.file_type == "docx"

    @property
    def is_excel(self) -> bool:
        """Excelテンプレートかどうか"""
        return self.file_type == "xlsx"
