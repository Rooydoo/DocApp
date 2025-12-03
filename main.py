"""
医局業務管理システム
メインエントリーポイント
"""
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from ui.main_window import MainWindow
from database.base import init_db
from utils.logger import get_logger
from services.config_service import config_service

logger = get_logger(__name__)


def initialize_application():
    """アプリケーションの初期化"""
    try:
        logger.info("Initializing application...")
        
        # データベース初期化
        logger.info("Initializing database...")
        init_db()
        logger.info("Database initialized")
        
        # 設定の初期化（デフォルト値をDBに保存）
        logger.info("Initializing configuration...")
        config_service._ensure_defaults_in_db()
        logger.info("Configuration initialized")
        
        logger.info("Application initialization completed")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        return False


def main():
    """メイン関数"""
    logger.info("=" * 60)
    logger.info("Starting 医局業務管理システム")
    logger.info("=" * 60)
    
    # アプリケーション初期化
    if not initialize_application():
        logger.error("Application initialization failed. Exiting...")
        sys.exit(1)
    
    # メインウィンドウを起動
    try:
        app = MainWindow()
        app.run()
    except Exception as e:
        logger.error(f"Application error: {e}")
        sys.exit(1)
    
    logger.info("Application closed")


if __name__ == "__main__":
    main()
