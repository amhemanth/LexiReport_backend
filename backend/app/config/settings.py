from typing import Any, Dict, List, Optional, Union
from pydantic import AnyHttpUrl, EmailStr, PostgresDsn, validator, Field, ConfigDict
from pydantic_settings import BaseSettings
import os
import secrets
from pathlib import Path

class Settings(BaseSettings):
    """Application settings."""
    
    # Environment Settings
    ENVIRONMENT: str = Field(
        default="development",
        description="Application environment (development, staging, production)"
    )
    
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "AI Report Analyzer"
    VERSION: str = Field(default="1.0.0", description="API version")
    DESCRIPTION: str = Field(default="LexiReport Backend API", description="API description")
    SERVER_NAME: str = Field(default="localhost", description="Server name")
    SERVER_HOST: str = Field(default="0.0.0.0", description="Server host")
    
    # Parse ALLOWED_HOSTS from environment variable
    ALLOWED_HOSTS: str = Field(
        default="localhost,127.0.0.1",
        description="Comma-separated list of allowed host names"
    )

    @property
    def ALLOWED_HOSTS(self) -> List[str]:
        """Get the list of allowed hosts."""
        if not self.ALLOWED_HOSTS_STR:
            return ["localhost", "127.0.0.1"]
        return [host.strip() for host in self.ALLOWED_HOSTS.split(",") if host.strip()]

    # CORS Configuration
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Security Settings
    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    JWT_ALGORITHM: str = "HS256"
    SESSION_EXPIRE_MINUTES: int = Field(
        default=60 * 24,  # 24 hours
        description="Session expiration time in minutes"
    )

    # Database Settings
    POSTGRES_SERVER: str = Field(
        default="localhost",
        description="PostgreSQL server host"
    )
    POSTGRES_PORT: int = Field(
        default=5432,
        description="PostgreSQL port"
    )
    POSTGRES_USER: str = Field(
        default="postgres",
        description="PostgreSQL user"
    )
    POSTGRES_PASSWORD: str = Field(
        default="postgres",
        description="PostgreSQL password"
    )
    POSTGRES_DB: str = Field(
        default="lexireport",
        description="PostgreSQL database name"
    )
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None
    SQL_ECHO: bool = Field(
        default=False,
        description="Enable SQL query logging"
    )

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return str(PostgresDsn.build(
            scheme="postgresql",
            username=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            port=values.get("POSTGRES_PORT"),
            path=values.get("POSTGRES_DB") or "",
        ))

    # Database Pool Settings
    DB_POOL_SIZE: int = Field(
        default=5,
        description="Database connection pool size"
    )
    DB_MAX_OVERFLOW: int = Field(
        default=10,
        description="Database connection pool max overflow"
    )
    DB_POOL_TIMEOUT: int = Field(
        default=30,
        description="Database connection pool timeout in seconds"
    )
    DB_POOL_RECYCLE: int = Field(
        default=1800,
        description="Database connection pool recycle time in seconds"
    )

    # Redis Settings
    REDIS_HOST: str = Field(
        default="localhost",
        description="Redis server host"
    )
    REDIS_PORT: int = Field(
        default=6379,
        description="Redis server port"
    )
    REDIS_PASSWORD: Optional[str] = Field(
        default=None,
        description="Redis password"
    )
    REDIS_DB: int = Field(
        default=0,
        description="Redis database number"
    )
    REDIS_SSL: bool = False
    REDIS_URL: Optional[str] = None
    REDIS_MAX_CONNECTIONS: int = Field(
        default=10,
        description="Maximum number of Redis connections"
    )
    REDIS_SOCKET_TIMEOUT: int = Field(
        default=5,
        description="Redis socket timeout in seconds"
    )
    REDIS_RETRY_ON_TIMEOUT: bool = True

    @validator("REDIS_URL", pre=True)
    def assemble_redis_url(cls, v: Optional[str], values: Dict[str, Any]) -> str:
        if isinstance(v, str):
            return v
        password = values.get("REDIS_PASSWORD")
        auth = f":{password}@" if password else ""
        return f"redis://{auth}{values.get('REDIS_HOST')}:{values.get('REDIS_PORT')}/{values.get('REDIS_DB')}"

    # Email Settings
    SMTP_TLS: bool = Field(
        default=True,
        description="Enable TLS for SMTP"
    )
    SMTP_PORT: Optional[int] = Field(
        default=None,
        description="SMTP port"
    )
    SMTP_HOST: Optional[str] = Field(
        default=None,
        description="SMTP host"
    )
    SMTP_USER: Optional[str] = Field(
        default=None,
        description="SMTP user"
    )
    SMTP_PASSWORD: Optional[str] = Field(
        default=None,
        description="SMTP password"
    )
    EMAILS_FROM_EMAIL: Optional[EmailStr] = None
    EMAILS_FROM_NAME: Optional[str] = None
    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48
    EMAIL_TEMPLATES_DIR: str = "/app/app/email-templates/build"
    EMAILS_ENABLED: bool = False

    @validator("EMAILS_ENABLED", pre=True)
    def get_emails_enabled(cls, v: bool, values: Dict[str, Any]) -> bool:
        return bool(
            values.get("SMTP_HOST")
            and values.get("SMTP_PORT")
            and values.get("EMAILS_FROM_EMAIL")
        )

    # User Settings
    FIRST_SUPERUSER_EMAIL: Optional[EmailStr] = None
    FIRST_SUPERUSER_NAME: Optional[str] = None
    FIRST_SUPERUSER_PASSWORD: Optional[str] = None
    FIRST_SUPERUSER_FULL_NAME: Optional[str] = None

    # AI Settings
    MODEL_PATH: str = Field(
        default="models",
        description="Path to AI models"
    )
    CACHE_DIR: str = Field(
        default="cache",
        description="Directory for cache files"
    )
    MAX_WORKERS: int = Field(
        default=4,
        description="Maximum number of worker processes"
    )
    BATCH_SIZE: int = Field(
        default=16,
        description="Batch size for processing"
    )
    AI_MODEL_NAME: str
    AI_QA_MODEL: str
    AI_KEYWORDS_MODEL: str
    MAX_TOKENS: int = Field(
        default=2048,
        description="Maximum number of tokens for AI processing"
    )
    TEMPERATURE: float = Field(
        default=0.7,
        description="Temperature for AI processing"
    )
    TOP_P: float = Field(
        default=1.0,
        description="Top P for AI processing"
    )
    FREQUENCY_PENALTY: float = Field(
        default=0.0,
        description="Frequency penalty for AI processing"
    )
    PRESENCE_PENALTY: float = Field(
        default=0.0,
        description="Presence penalty for AI processing"
    )

    # File Storage Settings
    UPLOAD_DIR: str = Field(
        default="uploads",
        description="Directory for storing uploaded files"
    )
    MAX_UPLOAD_SIZE: int = Field(
        default=50 * 1024 * 1024,  # 50MB
        description="Maximum file upload size in bytes"
    )
    ALLOWED_EXTENSIONS: str = "pdf,docx,xlsx,csv,txt"

    # Voice Settings
    DEFAULT_VOICE: str = Field(
        default="en-US-Neural2-F",
        description="Default voice for text-to-speech"
    )
    SUPPORTED_LANGUAGES: str = "en,es,fr,de,it"

    # Cache Settings
    CACHE_TTL: int = Field(
        default=3600,  # 1 hour
        description="Cache time-to-live in seconds"
    )

    # Rate Limiting Settings
    MAX_LOGIN_ATTEMPTS: int = Field(
        default=5,
        description="Maximum number of login attempts"
    )
    LOGIN_ATTEMPT_WINDOW: int = Field(
        default=15,  # minutes
        description="Login attempt window in minutes"
    )
    RATE_LIMIT_PER_MINUTE: int = Field(
        default=60,
        description="Rate limit per minute"
    )
    RATE_LIMIT_PER_HOUR: int = Field(
        default=1000,
        description="Rate limit per hour"
    )
    RATE_LIMIT_PER_DAY: int = Field(
        default=10000,
        description="Rate limit per day"
    )

    @validator("MODEL_PATH", "CACHE_DIR", "UPLOAD_DIR", pre=True)
    def validate_paths(cls, v: str) -> str:
        """Validate and create paths if they don't exist."""
        if not os.path.exists(v):
            os.makedirs(v, exist_ok=True)
        return v

    @validator("MAX_WORKERS", "BATCH_SIZE", "MAX_UPLOAD_SIZE", "CACHE_TTL", pre=True)
    def validate_positive_int(cls, v: int) -> int:
        """Validate that the value is positive."""
        if int(v) <= 0:
            raise ValueError("Value must be positive")
        return v

    model_config = ConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=True,
        extra='allow'
    )

def get_settings() -> Settings:
    """Get application settings."""
    return Settings()

settings = get_settings() 