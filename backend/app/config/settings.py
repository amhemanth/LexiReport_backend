from typing import List, Union
from pydantic_settings import BaseSettings
from pydantic import field_validator, AnyHttpUrl, ConfigDict

class Settings(BaseSettings):
    """Application settings."""
    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str
    VERSION: str
    DESCRIPTION: str
    
    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # PostgreSQL
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: str
    DB_ECHO: bool = False
    
    # Redis Settings
    REDIS_HOST: str
    REDIS_PORT: str
    REDIS_DB: str
    REDIS_PASSWORD: str
    REDIS_SSL: bool
    REDIS_TIMEOUT: int
    REDIS_RETRY_ON_TIMEOUT: bool
    
    # Database Pool Settings
    DB_POOL_SIZE: int
    DB_MAX_OVERFLOW: int
    DB_POOL_TIMEOUT: int
    DB_POOL_RECYCLE: int
    
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """Get database URI."""
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    model_config = ConfigDict(
        case_sensitive=True,
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix=""
    )

def get_settings() -> Settings:
    """Get application settings."""
    return Settings() 