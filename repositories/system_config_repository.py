"""
システム設定リポジトリ
"""
from typing import Optional, Dict
from sqlalchemy.orm import Session
from database.models.system_config import SystemConfig
from repositories.base_repository import BaseRepository
from utils.logger import get_logger

logger = get_logger(__name__)


class SystemConfigRepository(BaseRepository[SystemConfig]):
    """システム設定リポジトリ"""
    
    def __init__(self, db: Session):
        super().__init__(SystemConfig, db)
    
    def get_by_key(self, config_key: str) -> Optional[SystemConfig]:
        """
        設定キーで検索
        
        Args:
            config_key: 設定キー
        
        Returns:
            SystemConfig: 設定インスタンス、存在しない場合None
        """
        return self.db.query(SystemConfig).filter(
            SystemConfig.config_key == config_key
        ).first()
    
    def get_value(self, config_key: str, default: str = None) -> Optional[str]:
        """
        設定値を取得
        
        Args:
            config_key: 設定キー
            default: デフォルト値
        
        Returns:
            str: 設定値、存在しない場合はdefault
        """
        config = self.get_by_key(config_key)
        return config.config_value if config else default
    
    def set_value(self, config_key: str, config_value: str, description: str = None) -> SystemConfig:
        """
        設定値を設定（作成または更新）
        
        Args:
            config_key: 設定キー
            config_value: 設定値
            description: 説明
        
        Returns:
            SystemConfig: 設定インスタンス
        """
        existing = self.get_by_key(config_key)
        
        if existing:
            # 更新
            update_data = {"config_value": config_value}
            if description:
                update_data["description"] = description
            return self.update(existing.id, update_data)
        else:
            # 新規作成
            create_data = {
                "config_key": config_key,
                "config_value": config_value
            }
            if description:
                create_data["description"] = description
            return self.create(create_data)
    
    def get_all_as_dict(self) -> Dict[str, str]:
        """
        全設定を辞書形式で取得
        
        Returns:
            Dict[str, str]: {config_key: config_value}
        """
        configs = self.get_all()
        return {config.config_key: config.config_value for config in configs}
    
    def delete_by_key(self, config_key: str) -> bool:
        """
        設定を削除
        
        Args:
            config_key: 設定キー
        
        Returns:
            bool: 削除成功時True
        """
        config = self.get_by_key(config_key)
        if config:
            return self.delete(config.id)
        return False
