"""
病院テーブルのcapacityカラムを3つに分割するマイグレーションスクリプト

実行方法:
    python migrate_hospital_capacity.py
"""
import sqlite3
from pathlib import Path
from utils.logger import get_logger

logger = get_logger(__name__)

def migrate_database():
    """データベースをマイグレーション"""
    
    # データベースファイルパス
    db_path = Path("data/medical_dept.db")
    
    if not db_path.exists():
        logger.error(f"Database file not found: {db_path}")
        print("❌ データベースファイルが見つかりません")
        return False
    
    try:
        # データベース接続
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 既に新しいカラムが存在するかチェック
        cursor.execute("PRAGMA table_info(hospital)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'resident_capacity' in columns:
            logger.info("Migration already applied")
            print("✅ マイグレーションは既に適用されています")
            conn.close()
            return True
        
        logger.info("Starting migration...")
        print("🔄 マイグレーションを開始します...")
        
        # トランザクション開始
        cursor.execute("BEGIN TRANSACTION")
        
        # 1. 新しいカラムを追加
        cursor.execute("""
            ALTER TABLE hospital 
            ADD COLUMN resident_capacity INTEGER NOT NULL DEFAULT 0
        """)
        logger.info("Added resident_capacity column")
        
        cursor.execute("""
            ALTER TABLE hospital 
            ADD COLUMN specialist_capacity INTEGER NOT NULL DEFAULT 0
        """)
        logger.info("Added specialist_capacity column")
        
        cursor.execute("""
            ALTER TABLE hospital 
            ADD COLUMN instructor_capacity INTEGER NOT NULL DEFAULT 0
        """)
        logger.info("Added instructor_capacity column")
        
        # 2. 既存のcapacityの値をresident_capacityにコピー
        cursor.execute("""
            UPDATE hospital 
            SET resident_capacity = capacity
        """)
        logger.info("Copied capacity values to resident_capacity")
        
        # 3. 古いcapacityカラムを削除するため、テーブルを再作成
        # SQLiteではALTER TABLE DROP COLUMNが使えないため、テーブル再作成が必要
        
        # 一時テーブルを作成
        cursor.execute("""
            CREATE TABLE hospital_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL UNIQUE,
                director_name VARCHAR(100),
                address VARCHAR(200) NOT NULL,
                resident_capacity INTEGER NOT NULL DEFAULT 0,
                specialist_capacity INTEGER NOT NULL DEFAULT 0,
                instructor_capacity INTEGER NOT NULL DEFAULT 0,
                rotation_months INTEGER,
                annual_salary DECIMAL(10, 2),
                outpatient_flag BOOLEAN DEFAULT 0,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        logger.info("Created new hospital table")
        
        # データをコピー
        cursor.execute("""
            INSERT INTO hospital_new (
                id, name, director_name, address,
                resident_capacity, specialist_capacity, instructor_capacity,
                rotation_months, annual_salary, outpatient_flag, notes,
                created_at, updated_at
            )
            SELECT 
                id, name, director_name, address,
                resident_capacity, specialist_capacity, instructor_capacity,
                rotation_months, annual_salary, outpatient_flag, notes,
                created_at, updated_at
            FROM hospital
        """)
        logger.info("Copied data to new table")
        
        # 古いテーブルを削除
        cursor.execute("DROP TABLE hospital")
        logger.info("Dropped old hospital table")
        
        # 新しいテーブルをリネーム
        cursor.execute("ALTER TABLE hospital_new RENAME TO hospital")
        logger.info("Renamed new table to hospital")
        
        # コミット
        conn.commit()
        logger.info("Migration completed successfully")
        print("✅ マイグレーションが完了しました")
        
        # 確認
        cursor.execute("SELECT COUNT(*) FROM hospital")
        count = cursor.fetchone()[0]
        print(f"📊 病院データ: {count}件")
        
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        print(f"❌ マイグレーション失敗: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False


if __name__ == "__main__":
    print("=" * 50)
    print("病院テーブル マイグレーション")
    print("capacity → resident/specialist/instructor_capacity")
    print("=" * 50)
    print()
    
    success = migrate_database()
    
    if success:
        print()
        print("✨ マイグレーションが正常に完了しました")
        print("これで hospital.py を更新版に置き換えてください")
    else:
        print()
        print("⚠️ マイグレーションに失敗しました")
        print("ログを確認してください")