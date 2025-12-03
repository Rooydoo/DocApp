"""
データベーステストスクリプト
"""
from database.base import init_db, engine
from database.models import (
    Hospital, Staff, Assignment, CommuteCache,
    StaffWeight, OutpatientSlot, OutpatientAssignment,
    MailTemplate, DocumentTemplate, SystemConfig, BackupHistory
)
from utils.logger import get_logger

logger = get_logger(__name__)

def main():
    print("=" * 60)
    print("Database Initialization Test")
    print("=" * 60)
    print()
    
    try:
        # データベース初期化
        logger.info("Initializing database...")
        init_db()
        
        # テーブル一覧を表示
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        print(f"✓ Database initialized successfully")
        print(f"✓ Created {len(tables)} tables:")
        for table in tables:
            print(f"  - {table}")
        
        print()
        print("=" * 60)
        print("All tests passed!")
        print("=" * 60)
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        print(f"\n✗ Error: {e}")
        raise

if __name__ == "__main__":
    main()
