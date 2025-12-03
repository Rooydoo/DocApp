"""
ログ管理
Loguruを使用した統一的なログ管理
"""
import sys
from pathlib import Path
from loguru import logger
from config.settings import settings


def setup_logger():
    """
    ロガーのセットアップ
    
    - コンソール出力（開発用）
    - ファイル出力（ローテーション付き）
    """
    # デフォルトのハンドラーを削除
    logger.remove()
    
    # コンソール出力の設定
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.log_level,
        colorize=True
    )
    
    # ファイル出力の設定
    log_file_path = settings.project_root / settings.log_file_path
    
    logger.add(
        log_file_path,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=settings.log_level,
        rotation="10 MB",  # 10MBでローテーション
        retention="30 days",  # 30日間保持
        compression="zip",  # 圧縮
        encoding="utf-8"
    )
    
    logger.info("Logger initialized successfully")
    logger.debug(f"Log file: {log_file_path}")
    logger.debug(f"Log level: {settings.log_level}")


def get_logger(name: str = None):
    """
    ロガーインスタンスを取得
    
    Args:
        name: ロガー名（通常は__name__を渡す）
    
    Returns:
        logger: Loguruロガーインスタンス
    """
    if name:
        return logger.bind(name=name)
    return logger


# アプリケーション起動時に自動セットアップ
setup_logger()


# モジュールレベルでエクスポート
__all__ = ["logger", "get_logger", "setup_logger"]


# 開発用: ログテスト
if __name__ == "__main__":
    test_logger = get_logger(__name__)
    
    test_logger.debug("This is a DEBUG message")
    test_logger.info("This is an INFO message")
    test_logger.warning("This is a WARNING message")
    test_logger.error("This is an ERROR message")
    test_logger.critical("This is a CRITICAL message")
    
    # 例外のログ
    try:
        result = 1 / 0
    except Exception as e:
        test_logger.exception("An error occurred during division")
    
    print(f"\nLog file created at: {settings.project_root / settings.log_file_path}")
