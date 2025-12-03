"""
バックアップ履歴テーブルモデル
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from database.base import Base, TimestampMixin
from config.constants import TableName


class BackupHistory(Base, TimestampMixin):
    """
    バックアップ履歴
    
    データベースバックアップの実行履歴を管理
    """
    __tablename__ = TableName.BACKUP_HISTORY
    
    # 主キー
    id = Column(Integer, primary_key=True, autoincrement=True, comment="バックアップID")
    
    # バックアップ情報
    file_path = Column(String(500), nullable=False, comment="バックアップファイルパス")
    file_size_bytes = Column(Integer, comment="ファイルサイズ（バイト）")
    
    # 実行情報
    backup_datetime = Column(DateTime, nullable=False, comment="バックアップ実行日時")
    is_auto = Column(Boolean, default=False, comment="自動バックアップフラグ")
    
    # ステータス
    success = Column(Boolean, default=True, comment="成功フラグ")
    error_message = Column(String(500), comment="エラーメッセージ")
    
    def __repr__(self):
        status = "成功" if self.success else "失敗"
        return f"<BackupHistory(id={self.id}, datetime={self.backup_datetime}, status={status})>"
    
    def __str__(self):
        return f"{self.backup_datetime.strftime('%Y-%m-%d %H:%M:%S')}"
    
    @property
    def file_size_mb(self) -> float:
        """
        ファイルサイズをMB単位で取得
        
        Returns:
            float: ファイルサイズ（MB）
        """
        if not self.file_size_bytes:
            return 0.0
        return round(self.file_size_bytes / (1024 * 1024), 2)
