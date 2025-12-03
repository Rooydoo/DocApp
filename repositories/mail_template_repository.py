"""
メールテンプレートリポジトリ
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from database.models.mail_template import MailTemplate
from repositories.base_repository import BaseRepository
from utils.logger import get_logger

logger = get_logger(__name__)


class MailTemplateRepository(BaseRepository[MailTemplate]):
    """メールテンプレートリポジトリ"""
    
    def __init__(self, db: Session):
        super().__init__(MailTemplate, db)
    
    def get_by_name(self, name: str) -> Optional[MailTemplate]:
        """
        テンプレート名で検索
        
        Args:
            name: テンプレート名
        
        Returns:
            MailTemplate: テンプレートインスタンス、存在しない場合None
        """
        return self.db.query(MailTemplate).filter(
            MailTemplate.name == name
        ).first()
    
    def get_by_category(self, category: str) -> List[MailTemplate]:
        """
        カテゴリで検索
        
        Args:
            category: カテゴリ
        
        Returns:
            List[MailTemplate]: テンプレートのリスト
        """
        return self.db.query(MailTemplate).filter(
            MailTemplate.category == category
        ).all()
    
    def search_by_keyword(self, keyword: str) -> List[MailTemplate]:
        """
        キーワードで検索（名前、件名、本文）
        
        Args:
            keyword: 検索キーワード
        
        Returns:
            List[MailTemplate]: テンプレートのリスト
        """
        search_pattern = f"%{keyword}%"
        return self.db.query(MailTemplate).filter(
            (MailTemplate.name.like(search_pattern)) |
            (MailTemplate.subject.like(search_pattern)) |
            (MailTemplate.body.like(search_pattern))
        ).all()
