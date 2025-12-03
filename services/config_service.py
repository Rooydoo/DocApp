"""
設定管理サービス
環境変数とデータベース設定を統合管理
"""
from typing import Optional, Dict, Any
from decimal import Decimal
from database.connection import get_db_session
from repositories.system_config_repository import SystemConfigRepository
from config.settings import settings
from utils.logger import get_logger
from utils.exceptions import ValidationException

logger = get_logger(__name__)


class ConfigService:
    """設定管理サービス"""
    
    # 設定キーの定義
    class Keys:
        # Google APIs
        GOOGLE_MAPS_API_KEY = "google_maps_api_key"
        GMAIL_CREDENTIALS_PATH = "gmail_credentials_path"
        GOOGLE_FORMS_CREDENTIALS_PATH = "google_forms_credentials_path"
        
        # LLM
        OLLAMA_BASE_URL = "ollama_base_url"
        OLLAMA_MODEL = "ollama_model"
        
        # GA Settings
        GA_POPULATION_SIZE = "ga_population_size"
        GA_GENERATIONS = "ga_generations"
        GA_CROSSOVER_PROB = "ga_crossover_prob"
        GA_MUTATION_PROB = "ga_mutation_prob"
        GA_MISMATCH_BONUS = "ga_mismatch_bonus"
        
        # System
        FISCAL_YEAR = "fiscal_year"
        LOG_LEVEL = "log_level"
    
    def __init__(self):
        """初期化"""
        self._ensure_defaults_in_db()
    
    def _ensure_defaults_in_db(self):
        """デフォルト設定をDBに保存（存在しない場合のみ）"""
        try:
            with get_db_session() as db:
                repo = SystemConfigRepository(db)
                
                defaults = self._get_default_configs()
                
                for key, (value, description) in defaults.items():
                    existing = repo.get_by_key(key)
                    if not existing:
                        repo.set_value(key, str(value), description)
                        logger.debug(f"Initialized config: {key} = {value}")
        
        except Exception as e:
            logger.warning(f"Failed to initialize default configs: {e}")
    
    def _get_default_configs(self) -> Dict[str, tuple]:
        """
        デフォルト設定を取得
        
        Returns:
            Dict[str, tuple]: {key: (value, description)}
        """
        return {
            # Google APIs
            self.Keys.GOOGLE_MAPS_API_KEY: (
                settings.google_maps_api_key,
                "Google Maps API Key"
            ),
            self.Keys.GMAIL_CREDENTIALS_PATH: (
                settings.gmail_credentials_path,
                "Gmail API認証情報パス"
            ),
            self.Keys.GOOGLE_FORMS_CREDENTIALS_PATH: (
                settings.google_forms_credentials_path,
                "Google Forms API認証情報パス"
            ),
            
            # LLM
            self.Keys.OLLAMA_BASE_URL: (
                settings.ollama_base_url,
                "Ollama APIベースURL"
            ),
            self.Keys.OLLAMA_MODEL: (
                settings.ollama_model,
                "使用するOllamaモデル名"
            ),
            
            # GA Settings
            self.Keys.GA_POPULATION_SIZE: (
                settings.ga_population_size,
                "GA個体数（10-500）"
            ),
            self.Keys.GA_GENERATIONS: (
                settings.ga_generations,
                "GA世代数（50-1000）"
            ),
            self.Keys.GA_CROSSOVER_PROB: (
                settings.ga_crossover_prob,
                "GA交叉確率（0.0-1.0）"
            ),
            self.Keys.GA_MUTATION_PROB: (
                settings.ga_mutation_prob,
                "GA突然変異確率（0.0-1.0）"
            ),
            self.Keys.GA_MISMATCH_BONUS: (
                settings.ga_mismatch_bonus,
                "アンマッチボーナス係数（1.0-5.0）"
            ),
            
            # System
            self.Keys.FISCAL_YEAR: (
                settings.fiscal_year,
                "現在の会計年度"
            ),
            self.Keys.LOG_LEVEL: (
                settings.log_level,
                "ログレベル（DEBUG/INFO/WARNING/ERROR/CRITICAL）"
            ),
        }
    
    def get(self, key: str, default: Any = None) -> Optional[str]:
        """
        設定値を取得
        
        Args:
            key: 設定キー
            default: デフォルト値
        
        Returns:
            設定値（文字列）
        """
        try:
            with get_db_session() as db:
                repo = SystemConfigRepository(db)
                return repo.get_value(key, default)
        except Exception as e:
            logger.error(f"Failed to get config {key}: {e}")
            return default
    
    def get_int(self, key: str, default: int = 0) -> int:
        """設定値を整数で取得"""
        value = self.get(key)
        if value is None:
            return default
        try:
            return int(value)
        except (ValueError, TypeError):
            logger.warning(f"Invalid int value for {key}: {value}, using default {default}")
            return default
    
    def get_float(self, key: str, default: float = 0.0) -> float:
        """設定値を浮動小数点数で取得"""
        value = self.get(key)
        if value is None:
            return default
        try:
            return float(value)
        except (ValueError, TypeError):
            logger.warning(f"Invalid float value for {key}: {value}, using default {default}")
            return default
    
    def get_bool(self, key: str, default: bool = False) -> bool:
        """設定値を真偽値で取得"""
        value = self.get(key)
        if value is None:
            return default
        return value.lower() in ("true", "1", "yes", "on")
    
    def set(self, key: str, value: Any, description: str = None) -> bool:
        """
        設定値を保存
        
        Args:
            key: 設定キー
            value: 設定値
            description: 説明
        
        Returns:
            bool: 成功時True
        """
        try:
            with get_db_session() as db:
                repo = SystemConfigRepository(db)
                repo.set_value(key, str(value), description)
                logger.info(f"Updated config: {key} = {value}")
                return True
        except Exception as e:
            logger.error(f"Failed to set config {key}: {e}")
            return False
    
    def get_all(self) -> Dict[str, str]:
        """
        全設定を取得
        
        Returns:
            Dict[str, str]: {key: value}
        """
        try:
            with get_db_session() as db:
                repo = SystemConfigRepository(db)
                return repo.get_all_as_dict()
        except Exception as e:
            logger.error(f"Failed to get all configs: {e}")
            return {}
    
    def validate_and_set(self, key: str, value: Any) -> bool:
        """
        バリデーション付きで設定値を保存
        
        Args:
            key: 設定キー
            value: 設定値
        
        Returns:
            bool: 成功時True
        
        Raises:
            ValidationException: バリデーションエラー
        """
        # バリデーション
        if key == self.Keys.GA_POPULATION_SIZE:
            value = int(value)
            if not (10 <= value <= 500):
                raise ValidationException(f"GA個体数は10-500の範囲で指定してください")
        
        elif key == self.Keys.GA_GENERATIONS:
            value = int(value)
            if not (50 <= value <= 1000):
                raise ValidationException(f"GA世代数は50-1000の範囲で指定してください")
        
        elif key == self.Keys.GA_CROSSOVER_PROB:
            value = float(value)
            if not (0.0 <= value <= 1.0):
                raise ValidationException(f"GA交叉確率は0.0-1.0の範囲で指定してください")
        
        elif key == self.Keys.GA_MUTATION_PROB:
            value = float(value)
            if not (0.0 <= value <= 1.0):
                raise ValidationException(f"GA突然変異確率は0.0-1.0の範囲で指定してください")
        
        elif key == self.Keys.GA_MISMATCH_BONUS:
            value = float(value)
            if not (1.0 <= value <= 5.0):
                raise ValidationException(f"アンマッチボーナス係数は1.0-5.0の範囲で指定してください")
        
        elif key == self.Keys.FISCAL_YEAR:
            value = int(value)
            if not (2000 <= value <= 2100):
                raise ValidationException(f"年度は2000-2100の範囲で指定してください")
        
        elif key == self.Keys.LOG_LEVEL:
            valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
            if value.upper() not in valid_levels:
                raise ValidationException(f"ログレベルは{', '.join(valid_levels)}のいずれかを指定してください")
            value = value.upper()
        
        # 保存
        return self.set(key, value)
    
    # 便利メソッド：よく使う設定の取得
    
    def get_google_maps_api_key(self) -> str:
        """Google Maps API Keyを取得"""
        return self.get(self.Keys.GOOGLE_MAPS_API_KEY, "")
    
    def get_ollama_model(self) -> str:
        """Ollamaモデル名を取得"""
        return self.get(self.Keys.OLLAMA_MODEL, "llama3-elyza")
    
    def get_fiscal_year(self) -> int:
        """現在の年度を取得"""
        return self.get_int(self.Keys.FISCAL_YEAR, 2025)
    
    def get_ga_config(self) -> Dict[str, Any]:
        """
        GA設定を一括取得
        
        Returns:
            Dict: GA設定
        """
        return {
            "population_size": self.get_int(self.Keys.GA_POPULATION_SIZE, 100),
            "generations": self.get_int(self.Keys.GA_GENERATIONS, 200),
            "crossover_prob": self.get_float(self.Keys.GA_CROSSOVER_PROB, 0.7),
            "mutation_prob": self.get_float(self.Keys.GA_MUTATION_PROB, 0.2),
            "mismatch_bonus": self.get_float(self.Keys.GA_MISMATCH_BONUS, 1.5),
        }


# グローバルインスタンス
config_service = ConfigService()


# 開発用: テスト
if __name__ == "__main__":
    print("=== Config Service Test ===\n")
    
    service = ConfigService()
    
    # 全設定を表示
    print("Current configs:")
    configs = service.get_all()
    for key, value in configs.items():
        print(f"  {key}: {value}")
    
    print("\n=== GA Config ===")
    ga_config = service.get_ga_config()
    for key, value in ga_config.items():
        print(f"  {key}: {value}")
    
    print("\n=== Update Test ===")
    # テスト更新
    service.set("test_key", "test_value", "テスト設定")
    print(f"test_key: {service.get('test_key')}")
    
    # バリデーションテスト
    print("\n=== Validation Test ===")
    try:
        service.validate_and_set(service.Keys.GA_POPULATION_SIZE, 150)
        print("✓ Valid GA population size: 150")
    except Exception as e:
        print(f"✗ Validation failed: {e}")
    
    try:
        service.validate_and_set(service.Keys.GA_POPULATION_SIZE, 999)
        print("✓ Valid GA population size: 999")
    except Exception as e:
        print(f"✓ Caught invalid value: {e}")
