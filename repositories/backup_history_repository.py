"""
バックアップ履歴リポジトリ
"""
from typing import List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database.models.backup_history import BackupHistory
from repositories.base_repository import BaseRepository
from utils.logger import get_logger

logger = get_logger(__name__)


class BackupHistoryRepository(BaseRepository[BackupHistory]):
    """バックアップ履歴リポジトリ"""
    
    def __init__(self, db: Session):
        super().__init__(BackupHistory, db)
    
    def get_successful_backups(self) -> List[BackupHistory]:
        """
        成功したバックアップを取得
        
        Returns:
            List[BackupHistory]: バックアップ履歴のリスト（日時降順）
        """
        return self.db.query(BackupHistory).filter(
            BackupHistory.success == True
        ).order_by(BackupHistory.backup_datetime.desc()).all()
    
    def get_failed_backups(self) -> List[BackupHistory]:
        """
        失敗したバックアップを取得
        
        Returns:
            List[BackupHistory]: バックアップ履歴のリスト（日時降順）
        """
        return self.db.query(BackupHistory).filter(
            BackupHistory.success == False
        ).order_by(BackupHistory.backup_datetime.desc()).all()
    
    def get_auto_backups(self) -> List[BackupHistory]:
        """
        自動バックアップを取得
        
        Returns:
            List[BackupHistory]: バックアップ履歴のリスト（日時降順）
        """
        return self.db.query(BackupHistory).filter(
            BackupHistory.is_auto == True
        ).order_by(BackupHistory.backup_datetime.desc()).all()
    
    def get_manual_backups(self) -> List[BackupHistory]:
        """
        手動バックアップを取得
        
        Returns:
            List[BackupHistory]: バックアップ履歴のリスト（日時降順）
        """
        return self.db.query(BackupHistory).filter(
            BackupHistory.is_auto == False
        ).order_by(BackupHistory.backup_datetime.desc()).all()
    
    def get_recent_backups(self, days: int = 30) -> List[BackupHistory]:
        """
        最近のバックアップを取得
        
        Args:
            days: 日数
        
        Returns:
            List[BackupHistory]: バックアップ履歴のリスト（日時降順）
        """
        since_date = datetime.now() - timedelta(days=days)
        return self.db.query(BackupHistory).filter(
            BackupHistory.backup_datetime >= since_date
        ).order_by(BackupHistory.backup_datetime.desc()).all()
    
    def get_latest_backup(self) -> BackupHistory:
        """
        最新のバックアップを取得
        
        Returns:
            BackupHistory: 最新のバックアップ履歴、存在しない場合None
        """
        return self.db.query(BackupHistory).order_by(
            BackupHistory.backup_datetime.desc()
        ).first()
    
    def delete_old_backups(self, keep_count: int = 10) -> int:
        """
        古いバックアップ履歴を削除（指定件数を残す）
        
        Args:
            keep_count: 保持する件数
        
        Returns:
            int: 削除件数
        """
        # 保持するバックアップのIDを取得
        keep_ids = [
            b.id for b in self.db.query(BackupHistory)
            .order_by(BackupHistory.backup_datetime.desc())
            .limit(keep_count)
            .all()
        ]
        
        # それ以外を削除
        count = self.db.query(BackupHistory).filter(
            BackupHistory.id.notin_(keep_ids)
        ).delete(synchronize_session=False)
        
        self.db.commit()
        logger.info(f"Deleted {count} old backup histories (kept {keep_count})")
        return count
    
    def get_total_backup_size(self) -> int:
        """
        全バックアップの合計サイズを取得
        
        Returns:
            int: 合計サイズ（バイト）
        """
        from sqlalchemy import func
        result = self.db.query(
            func.sum(BackupHistory.file_size_bytes)
        ).filter(
            BackupHistory.success == True
        ).scalar()
        
        return result or 0
