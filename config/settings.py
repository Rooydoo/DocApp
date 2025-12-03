"""
アプリケーション設定管理
Pydantic Settingsを使用して環境変数から設定を読み込む
"""
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """アプリケーション設定"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # ===== Database =====
    database_url: str = Field(
        default="sqlite:///data/medical_dept.db",
        description="データベース接続URL"
    )
    
    # ===== Google APIs =====
    google_maps_api_key: str = Field(
        default="",
        description="Google Maps API Key"
    )
    gmail_credentials_path: str = Field(
        default="config/credentials/gmail_credentials.json",
        description="Gmail API認証情報パス"
    )
    google_forms_credentials_path: str = Field(
        default="config/credentials/forms_credentials.json",
        description="Google Forms API認証情報パス"
    )
    
    # ===== LLM (Ollama) =====
    ollama_base_url: str = Field(
        default="http://localhost:11434",
        description="Ollama APIベースURL"
    )
    ollama_model: str = Field(
        default="llama3-elyza",
        description="使用するOllamaモデル"
    )
    
    # ===== Application Settings =====
    log_level: str = Field(
        default="INFO",
        description="ログレベル (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )
    log_file_path: str = Field(
        default="logs/app.log",
        description="ログファイルパス"
    )
    backup_dir: str = Field(
        default="backups/",
        description="バックアップディレクトリ"
    )
    
    # ===== GA Settings =====
    ga_population_size: int = Field(
        default=100,
        description="GA個体数",
        ge=10,
        le=500
    )
    ga_generations: int = Field(
        default=200,
        description="GA世代数",
        ge=50,
        le=1000
    )
    ga_crossover_prob: float = Field(
        default=0.7,
        description="GA交叉確率",
        ge=0.0,
        le=1.0
    )
    ga_mutation_prob: float = Field(
        default=0.2,
        description="GA突然変異確率",
        ge=0.0,
        le=1.0
    )
    ga_mismatch_bonus: float = Field(
        default=1.5,
        description="アンマッチボーナス係数",
        ge=1.0,
        le=5.0
    )
    
    # ===== System =====
    fiscal_year: int = Field(
        default=2025,
        description="現在の会計年度"
    )
    
    # ===== プロジェクトルート =====
    @property
    def project_root(self) -> Path:
        """プロジェクトルートディレクトリを取得"""
        return Path(__file__).parent.parent
    
    @property
    def data_dir(self) -> Path:
        """データディレクトリパスを取得"""
        path = self.project_root / "data"
        path.mkdir(exist_ok=True)
        return path
    
    @property
    def logs_dir(self) -> Path:
        """ログディレクトリパスを取得"""
        path = self.project_root / "logs"
        path.mkdir(exist_ok=True)
        return path
    
    @property
    def backups_dir(self) -> Path:
        """バックアップディレクトリパスを取得"""
        path = self.project_root / self.backup_dir
        path.mkdir(exist_ok=True)
        return path
    
    @property
    def credentials_dir(self) -> Path:
        """認証情報ディレクトリパスを取得"""
        path = self.project_root / "config" / "credentials"
        path.mkdir(exist_ok=True)
        return path


# グローバル設定インスタンス
settings = Settings()


# 開発用: 設定の表示
if __name__ == "__main__":
    print("=== Application Settings ===")
    print(f"Database URL: {settings.database_url}")
    print(f"Ollama Model: {settings.ollama_model}")
    print(f"Log Level: {settings.log_level}")
    print(f"Fiscal Year: {settings.fiscal_year}")
    print(f"Project Root: {settings.project_root}")
    print(f"GA Population Size: {settings.ga_population_size}")
    print(f"GA Generations: {settings.ga_generations}")
