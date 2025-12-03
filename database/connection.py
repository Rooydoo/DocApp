"""
データベース接続管理
コンテキストマネージャーを使用した安全な接続管理
"""
from contextlib import contextmanager
from typing import Generator
from sqlalchemy.orm import Session
from database.base import SessionLocal, engine
from utils.logger import get_logger
from utils.exceptions import DatabaseConnectionException

logger = get_logger(__name__)


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    データベースセッションのコンテキストマネージャー
    
    Yields:
        Session: SQLAlchemyセッション
    
    Raises:
        DatabaseConnectionException: 接続エラー
    
    Example:
        ```python
        from database.connection import get_db_session
        
        with get_db_session() as db:
            hospitals = db.query(Hospital).all()
        ```
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database session error: {e}")
        raise DatabaseConnectionException(f"Session error: {str(e)}")
    finally:
        session.close()


def test_connection() -> bool:
    """
    データベース接続テスト
    
    Returns:
        bool: 接続成功時True
    """
    try:
        with engine.connect() as conn:
            logger.info("Database connection test successful")
            return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False


def execute_raw_sql(sql: str) -> None:
    """
    生SQLを実行（管理用）
    
    Args:
        sql: 実行するSQL文
    
    Warning:
        通常のアプリケーションロジックでは使用しない
        管理タスクやマイグレーション用
    """
    try:
        with engine.connect() as conn:
            conn.execute(sql)
            conn.commit()
            logger.info(f"Executed SQL: {sql[:100]}...")
    except Exception as e:
        logger.error(f"Failed to execute SQL: {e}")
        raise DatabaseConnectionException(f"SQL execution error: {str(e)}")


# 開発用: 接続テスト
if __name__ == "__main__":
    print("Testing database connection...")
    
    if test_connection():
        print("✓ Connection test passed")
        
        # セッションテスト
        try:
            with get_db_session() as db:
                print("✓ Session context manager works")
        except Exception as e:
            print(f"✗ Session test failed: {e}")
    else:
        print("✗ Connection test failed")
