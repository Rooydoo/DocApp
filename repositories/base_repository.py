"""
基底リポジトリ
全てのリポジトリが継承する基底クラス
"""
from typing import TypeVar, Generic, List, Optional, Type, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database.base import Base
from utils.logger import get_logger
from utils.exceptions import (
    RecordNotFoundException,
    DuplicateRecordException,
    IntegrityConstraintException,
    DatabaseException
)

logger = get_logger(__name__)

# ジェネリック型変数（モデルクラス）
ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    基底リポジトリクラス
    
    CRUD操作の共通実装を提供
    """
    
    def __init__(self, model: Type[ModelType], db: Session):
        """
        Args:
            model: SQLAlchemyモデルクラス
            db: データベースセッション
        """
        self.model = model
        self.db = db
    
    def create(self, obj_in: Dict[str, Any]) -> ModelType:
        """
        レコードを作成
        
        Args:
            obj_in: 作成するデータ（辞書形式）
        
        Returns:
            ModelType: 作成されたモデルインスタンス
        
        Raises:
            DuplicateRecordException: 一意制約違反
            IntegrityConstraintException: その他の整合性制約違反
        """
        try:
            db_obj = self.model(**obj_in)
            self.db.add(db_obj)
            self.db.commit()
            self.db.refresh(db_obj)
            logger.info(f"Created {self.model.__name__} with id={db_obj.id}")
            return db_obj
        except IntegrityError as e:
            self.db.rollback()
            error_msg = str(e.orig)
            
            if "UNIQUE constraint failed" in error_msg or "duplicate" in error_msg.lower():
                raise DuplicateRecordException(
                    self.model.__name__,
                    details={"error": error_msg}
                )
            else:
                raise IntegrityConstraintException(
                    f"Failed to create {self.model.__name__}",
                    details={"error": error_msg}
                )
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create {self.model.__name__}: {e}")
            raise DatabaseException(f"Failed to create {self.model.__name__}: {str(e)}")
    
    def get(self, id: int) -> Optional[ModelType]:
        """
        IDでレコードを取得
        
        Args:
            id: レコードID
        
        Returns:
            ModelType: モデルインスタンス、存在しない場合None
        """
        return self.db.query(self.model).filter(self.model.id == id).first()
    
    def get_or_raise(self, id: int) -> ModelType:
        """
        IDでレコードを取得（存在しない場合は例外）
        
        Args:
            id: レコードID
        
        Returns:
            ModelType: モデルインスタンス
        
        Raises:
            RecordNotFoundException: レコードが存在しない
        """
        obj = self.get(id)
        if obj is None:
            raise RecordNotFoundException(self.model.__name__, id)
        return obj
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """
        全レコードを取得
        
        Args:
            skip: スキップ件数
            limit: 取得上限
        
        Returns:
            List[ModelType]: モデルインスタンスのリスト
        """
        return self.db.query(self.model).offset(skip).limit(limit).all()
    
    def get_by_filter(self, **filters) -> List[ModelType]:
        """
        フィルター条件でレコードを取得
        
        Args:
            **filters: フィルター条件（カラム名=値）
        
        Returns:
            List[ModelType]: モデルインスタンスのリスト
        
        Example:
            repository.get_by_filter(name="田中", staff_type="選考医")
        """
        query = self.db.query(self.model)
        for key, value in filters.items():
            if hasattr(self.model, key):
                query = query.filter(getattr(self.model, key) == value)
        return query.all()
    
    def update(self, id: int, obj_in: Dict[str, Any]) -> ModelType:
        """
        レコードを更新
        
        Args:
            id: レコードID
            obj_in: 更新するデータ（辞書形式）
        
        Returns:
            ModelType: 更新されたモデルインスタンス
        
        Raises:
            RecordNotFoundException: レコードが存在しない
            IntegrityConstraintException: 整合性制約違反
        """
        try:
            db_obj = self.get_or_raise(id)
            
            for key, value in obj_in.items():
                if hasattr(db_obj, key):
                    setattr(db_obj, key, value)
            
            self.db.commit()
            self.db.refresh(db_obj)
            logger.info(f"Updated {self.model.__name__} with id={id}")
            return db_obj
        except RecordNotFoundException:
            raise
        except IntegrityError as e:
            self.db.rollback()
            error_msg = str(e.orig)
            
            if "UNIQUE constraint failed" in error_msg or "duplicate" in error_msg.lower():
                raise DuplicateRecordException(
                    self.model.__name__,
                    details={"error": error_msg}
                )
            else:
                raise IntegrityConstraintException(
                    f"Failed to update {self.model.__name__}",
                    details={"error": error_msg}
                )
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update {self.model.__name__}: {e}")
            raise DatabaseException(f"Failed to update {self.model.__name__}: {str(e)}")
    
    def delete(self, id: int) -> bool:
        """
        レコードを削除
        
        Args:
            id: レコードID
        
        Returns:
            bool: 削除成功時True
        
        Raises:
            RecordNotFoundException: レコードが存在しない
        """
        try:
            db_obj = self.get_or_raise(id)
            self.db.delete(db_obj)
            self.db.commit()
            logger.info(f"Deleted {self.model.__name__} with id={id}")
            return True
        except RecordNotFoundException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to delete {self.model.__name__}: {e}")
            raise DatabaseException(f"Failed to delete {self.model.__name__}: {str(e)}")
    
    def count(self, **filters) -> int:
        """
        レコード数をカウント
        
        Args:
            **filters: フィルター条件（カラム名=値）
        
        Returns:
            int: レコード数
        """
        query = self.db.query(self.model)
        for key, value in filters.items():
            if hasattr(self.model, key):
                query = query.filter(getattr(self.model, key) == value)
        return query.count()
    
    def exists(self, id: int) -> bool:
        """
        レコードが存在するか確認
        
        Args:
            id: レコードID
        
        Returns:
            bool: 存在する場合True
        """
        return self.db.query(self.model).filter(self.model.id == id).count() > 0
