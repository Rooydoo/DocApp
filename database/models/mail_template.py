"""
メールテンプレートテーブルモデル
"""
from sqlalchemy import Column, Integer, String, Text
from database.base import Base, TimestampMixin
from config.constants import TableName


class MailTemplate(Base, TimestampMixin):
    """
    メールテンプレート
    
    定型メールのテンプレートを管理
    """
    __tablename__ = TableName.MAIL_TEMPLATE
    
    # 主キー
    id = Column(Integer, primary_key=True, autoincrement=True, comment="テンプレートID")
    
    # テンプレート情報
    name = Column(String(100), nullable=False, unique=True, comment="テンプレート名")
    subject = Column(String(200), nullable=False, comment="件名")
    body = Column(Text, nullable=False, comment="本文")
    
    # カテゴリ
    category = Column(String(50), comment="カテゴリ")
    
    # 備考
    notes = Column(Text, comment="備考")
    
    def __repr__(self):
        return f"<MailTemplate(id={self.id}, name='{self.name}')>"
    
    def __str__(self):
        return self.name
    
    def render(self, **kwargs) -> dict:
        """
        テンプレートを変数で置換してレンダリング
        
        Args:
            **kwargs: 置換する変数
        
        Returns:
            dict: {"subject": "...", "body": "..."}
        """
        subject = self.subject
        body = self.body
        
        # 簡易的なテンプレート変数置換
        for key, value in kwargs.items():
            placeholder = f"{{{key}}}"
            subject = subject.replace(placeholder, str(value))
            body = body.replace(placeholder, str(value))
        
        return {
            "subject": subject,
            "body": body
        }
