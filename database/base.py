"""
SQLAlchemy基底設定
全てのモデルが継承する基底クラスとセッション管理
"""
from datetime import datetime
from sqlalchemy import create_engine, DateTime, MetaData, Column
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.sql import func
from typing import Generator
from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)

# メタデータ設定（命名規則の統一）
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

# 基底クラス
Base = declarative_base(metadata=metadata)


class TimestampMixin:
    """
    タイムスタンプMixin
    作成日時・更新日時を自動管理
    """
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


# データベースエンジンの作成
engine = create_engine(
    settings.database_url,
    echo=False,  # SQLログ出力（開発時はTrue推奨）
    pool_pre_ping=True,  # 接続チェック
    pool_recycle=3600,  # 1時間で接続をリサイクル
)

# セッションファクトリー
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db() -> Generator[Session, None, None]:
    """
    データベースセッションを取得
    
    Yields:
        Session: SQLAlchemyセッション
    
    Example:
        ```python
        with get_db() as db:
            result = db.query(Hospital).all()
        ```
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    データベースを初期化
    全てのテーブルを作成
    """
    logger.info("Initializing database...")

    # 全てのモデルをインポート（テーブル作成のため）
    from database.models import (
        hospital,
        staff,
        assignment,
        commute_cache,
        staff_weight,
        outpatient_slot,
        outpatient_assignment,
        mail_template,
        document_template,
        system_config,
        backup_history,
        # GA用評価要素テーブル
        evaluation_factor,
        staff_factor_weight,
        admin_evaluation,
        hospital_choice,
    )

    # テーブル作成
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized successfully")


def drop_db():
    """
    データベースを削除
    全てのテーブルを削除（開発・テスト用）
    
    Warning:
        本番環境では使用しないこと！
    """
    logger.warning("Dropping all database tables...")
    Base.metadata.drop_all(bind=engine)
    logger.warning("All tables dropped")


# 開発用: データベース接続テスト
if __name__ == "__main__":
    logger.info(f"Database URL: {settings.database_url}")
    logger.info("Testing database connection...")
    
    try:
        # 接続テスト
        with engine.connect() as conn:
            logger.info("✓ Database connection successful")
        
        # セッションテスト
        with SessionLocal() as session:
            logger.info("✓ Session creation successful")
        
        print("\n✓ All database tests passed!")
        
    except Exception as e:
        logger.error(f"✗ Database test failed: {e}")
        raise