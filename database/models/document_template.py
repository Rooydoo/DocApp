"""
書類テンプレートテーブルモデル
"""
from sqlalchemy import Column, Integer, String, Text
from database.base import Base, TimestampMixin
from config.constants import TableName


class DocumentTemplate(Base, TimestampMixin):
    """
    書類テンプレート
    
    書類作成用のテンプレートとFew-shot例を管理
    """
    __tablename__ = TableName.DOCUMENT_TEMPLATE
    
    # 主キー
    id = Column(Integer, primary_key=True, autoincrement=True, comment="テンプレートID")
    
    # テンプレート情報
    name = Column(String(100), nullable=False, unique=True, comment="テンプレート名")
    description = Column(Text, comment="説明")
    
    # テンプレート内容
    template_content = Column(Text, nullable=False, comment="テンプレート内容")
    
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
