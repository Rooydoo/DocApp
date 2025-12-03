"""
システム設定テーブルモデル
"""
from sqlalchemy import Column, Integer, String, Text
from database.base import Base, TimestampMixin
from config.constants import TableName


class SystemConfig(Base, TimestampMixin):
    """
    システム設定
    
    アプリケーション設定をDB内で管理
    Key-Value形式
    """
    __tablename__ = TableName.SYSTEM_CONFIG
    
    # 主キー
    id = Column(Integer, primary_key=True, autoincrement=True, comment="設定ID")
    
    # 設定情報
    config_key = Column(String(100), nullable=False, unique=True, comment="設定キー")
    config_value = Column(Text, comment="設定値")
    
    # 説明
    description = Column(Text, comment="説明")
    
    def __repr__(self):
        return f"<SystemConfig(key='{self.config_key}', value='{self.config_value}')>"
    
    def __str__(self):
        return f"{self.config_key}: {self.config_value}"
