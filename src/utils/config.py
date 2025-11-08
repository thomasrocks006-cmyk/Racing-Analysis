"""
Configuration management for Racing Analysis system.
Loads settings from .env and provides typed access.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # ============================================================================
    # API CREDENTIALS
    # ============================================================================
    
    betfair_app_key: Optional[str] = Field(default=None, alias="BETFAIR_APP_KEY")
    betfair_username: Optional[str] = Field(default=None, alias="BETFAIR_USERNAME")
    betfair_password: Optional[str] = Field(default=None, alias="BETFAIR_PASSWORD")
    betfair_cert_path: Optional[Path] = Field(default=None, alias="BETFAIR_CERT_PATH")
    betfair_key_path: Optional[Path] = Field(default=None, alias="BETFAIR_KEY_PATH")
    
    weather_api_key: Optional[str] = Field(default=None, alias="WEATHER_API_KEY")
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    
    # ============================================================================
    # DATABASE
    # ============================================================================
    
    db_path: Path = Field(default=Path("./data/racing.duckdb"), alias="DB_PATH")
    feature_store_path: Path = Field(default=Path("./data/features"), alias="FEATURE_STORE_PATH")
    model_path: Path = Field(default=Path("./data/models"), alias="MODEL_PATH")
    
    # ============================================================================
    # SCRAPING
    # ============================================================================
    
    user_agent: str = Field(
        default="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        alias="USER_AGENT"
    )
    scrape_rate_limit: int = Field(default=2, alias="SCRAPE_RATE_LIMIT")
    scrape_max_retries: int = Field(default=3, alias="SCRAPE_MAX_RETRIES")
    scrape_timeout: int = Field(default=30, alias="SCRAPE_TIMEOUT")
    
    # ============================================================================
    # MODEL
    # ============================================================================
    
    model_type: str = Field(default="catboost", alias="MODEL_TYPE")
    model_version: str = Field(default="v1", alias="MODEL_VERSION")
    calibration_method: str = Field(default="isotonic", alias="CALIBRATION_METHOD")
    conformal_coverage: float = Field(default=0.90, alias="CONFORMAL_COVERAGE")
    
    # ============================================================================
    # EXECUTION
    # ============================================================================
    
    kelly_fraction: float = Field(default=0.25, alias="KELLY_FRACTION")
    max_stake_per_race: float = Field(default=100.0, alias="MAX_STAKE_PER_RACE")
    max_daily_loss: float = Field(default=500.0, alias="MAX_DAILY_LOSS")
    min_edge: float = Field(default=0.10, alias="MIN_EDGE")
    commission_rate: float = Field(default=0.05, alias="COMMISSION_RATE")
    
    # ============================================================================
    # MONITORING
    # ============================================================================
    
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_file: Path = Field(default=Path("./logs/racing-analysis.log"), alias="LOG_FILE")
    enable_monitoring: bool = Field(default=True, alias="ENABLE_MONITORING")
    drift_threshold: float = Field(default=0.15, alias="DRIFT_THRESHOLD")
    
    # ============================================================================
    # DEVELOPMENT
    # ============================================================================
    
    environment: str = Field(default="dev", alias="ENVIRONMENT")
    debug: bool = Field(default=True, alias="DEBUG")
    test_mode: bool = Field(default=False, alias="TEST_MODE")
    cache_dir: Path = Field(default=Path("./data/cache"), alias="CACHE_DIR")
    cache_ttl: int = Field(default=3600, alias="CACHE_TTL")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
    def ensure_directories(self):
        """Create required directories if they don't exist"""
        directories = [
            self.db_path.parent,
            self.feature_store_path,
            self.model_path,
            self.log_file.parent,
            self.cache_dir,
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
settings.ensure_directories()
