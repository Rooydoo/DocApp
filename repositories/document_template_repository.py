"""
書類テンプレートリポジトリ
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from database.models.document_template import DocumentTemplate
from repositories.base_repository import BaseRepository
from utils.logger import get_logger

logger = get_logger(__name__)


class DocumentTemplateRepository(BaseRepository[DocumentTemplate]):
    """書類テンプレートリポジトリ"""
    
    def __init__(self, db: Session):
        super().__init__(DocumentTemplate, db)
    
    def get_by_name(self, name: str) -> Optional[DocumentTemplate]:
        """
        テンプレート名で検索
        
        Args:
            name: テンプレート名
        
        Returns:
            DocumentTemplate: テンプレートインスタンス、存在しない場合None
        """
        return self.db.query(DocumentTemplate).filter(
            DocumentTemplate.name == name
        ).first()
    
    def get_by_category(self, category: str) -> List[DocumentTemplate]:
        """
        カテゴリで検索
        
        Args:
            category: カテゴリ
        
        Returns:
            List[DocumentTemplate]: テンプレートのリスト
        """
        return self.db.query(DocumentTemplate).filter(
            DocumentTemplate.category == category
        ).all()
    
    def search_by_keyword(self, keyword: str) -> List[DocumentTemplate]:
        """
        キーワードで検索（名前、説明）
        
        Args:
            keyword: 検索キーワード
        
        Returns:
            List[DocumentTemplate]: テンプレートのリスト
        """
        search_pattern = f"%{keyword}%"
        return self.db.query(DocumentTemplate).filter(
            (DocumentTemplate.name.like(search_pattern)) |
            (DocumentTemplate.description.like(search_pattern))
        ).all()
